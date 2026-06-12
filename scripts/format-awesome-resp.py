"""Awesome-Resp-Module formatter: format readme.md and then lint it.

Pipeline (always sequential):
    1. ``format``: read ``libraries.yml``, clone each repo, detect license +
       last commit time, render the Libraries table into ``readme.md.tpl`` and
       write the result to ``readme.md`` (or stdout with ``--stdout``).
       ``--dry-run`` clones only the first entry as a smoke test.
    2. ``lint``: run ``npx awesome-lint`` against the freshly written
       ``readme.md`` because awesome-resp-module itself is an awesome list.
       Skip with ``--no-lint`` (e.g. when running in ``--stdout`` mode).

Usage:
    python3 scripts/format-awesome-resp.py [--stdout] [--dry-run] [--no-lint]
"""

import argparse
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import yaml


# ---------------------------------------------------------------------------
# Shared constants & paths
# ---------------------------------------------------------------------------

# Repository root = parent directory of this script. It anchors the default
# input/output paths so the script works regardless of the cwd it is run from.
REPO_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_LIBRARIES_FILE = REPO_ROOT / "libraries.yml"
DEFAULT_TEMPLATE_FILE = REPO_ROOT / "readme.md.tpl"
DEFAULT_OUTPUT_FILE = REPO_ROOT / "readme.md"
DEFAULT_TMP_DIR = REPO_ROOT / "tmp"

PLACEHOLDER = "{{LIBRARIES_TABLE}}"
TABLE_HEADERS = ("Repo", "License", "Last Commit Time")

# Ordered (specific -> generic) so that "Redis Source Available License 2.0"
# is matched before the generic "Redis Source Available License".
LICENSE_PATTERNS = [
    ("Redis Source Available License 2.0", "Redis Source Available License 2.0"),
    ("Redis Source Available License",     "Redis Source Available License"),
    ("MIT License",                        "MIT License"),
    ("Apache License",                     "Apache License"),
    ("BSD 3-Clause License",               "BSD 3-Clause License"),
    ("GNU General Public License",         "GNU GPL"),
]

LICENSE_FILE_PREFIXES = ("LICENSE", "LICENCE", "COPYING")


# ---------------------------------------------------------------------------
# YAML loading
# ---------------------------------------------------------------------------

def load_libraries(file_path):
    """Read ``libraries.yml`` from disk and return ``[(url, branch_or_none), ...]``.

    @param file_path  Path to the YAML file.
    @return           List of (url, branch) tuples preserving file order.
    @exit             1 if the file is missing or has no entries.
    """
    path = Path(file_path)
    if not path.is_file():
        print(f"file {file_path} not exist")
        sys.exit(1)

    data = yaml.safe_load(path.read_text())
    if not isinstance(data, dict) or not isinstance(data.get("libraries"), list) or not data["libraries"]:
        print("Invalid libraries.yml: top-level 'libraries' must be a non-empty list")
        sys.exit(1)

    out = []
    for idx, item in enumerate(data["libraries"]):
        if not isinstance(item, dict) or not item.get("url"):
            print(f"Skip entry #{idx}: missing 'url'")
            continue
        out.append((item["url"], item.get("branch")))
    return out


# ---------------------------------------------------------------------------
# Per-repository helpers
# ---------------------------------------------------------------------------

def clone_repo(url, branch, dest_root):
    """Clone ``url`` into ``dest_root/<repo_name>`` with ``--depth 1``.

    @param url        Git clone URL (typically ending with ``.git``).
    @param branch     Optional branch name; ``None`` for the remote default.
    @param dest_root  Directory in which the clone is created.
    @return           Path to the cloned repository on success, else ``None``.
    """
    repo_name = os.path.basename(url)
    if repo_name.endswith(".git"):
        repo_name = repo_name[:-len(".git")]
    target = Path(dest_root) / repo_name

    cmd = ["git", "clone", "--quiet", "--depth", "1"]
    if branch:
        cmd += ["-b", branch, "--single-branch"]
    cmd += [url, str(target)]

    # Skip the Git LFS smudge filter. Some repos (e.g. RedisAI) enable LFS,
    # but when the remote disables LFS, ``git clone`` fails with
    # "smudge filter lfs failed". We only need the LICENSE files and the last
    # commit time, never the actual LFS payloads, so setting
    # GIT_LFS_SKIP_SMUDGE=1 lets the lfs filter pass through pointers as-is.
    env = os.environ.copy()
    env["GIT_LFS_SKIP_SMUDGE"] = "1"

    try:
        rc = subprocess.call(cmd, env=env)
    except subprocess.CalledProcessError:
        rc = 1
    if rc != 0 or not target.is_dir():
        print(f"Failed to clone {url}")
        return None
    return target


def detect_license(repo_dir):
    """Detect the license type by scanning license-like files in ``repo_dir``."""
    license_files = []
    for root, _dirs, files in os.walk(repo_dir):
        for name in files:
            if name.startswith(LICENSE_FILE_PREFIXES):
                license_files.append(os.path.join(root, name))

    if not license_files:
        return "Unknown license"

    for license_file in license_files:
        try:
            with open(license_file, "r", errors="ignore") as f:
                content = f.read()
        except OSError:
            continue
        for needle, name in LICENSE_PATTERNS:
            if needle in content:
                return name
    return "Unknown license"


def get_last_commit_time(repo_dir):
    """Return the last commit time of ``repo_dir`` as ``YYYY-MM-DD HH:MM:SS``."""
    try:
        out = subprocess.check_output(
            ["git", "log", "-1", "--format=%cd", "--date=format:%Y-%m-%d %H:%M:%S"],
            cwd=repo_dir,
        )
        return out.decode().strip()
    except subprocess.CalledProcessError:
        print(f"Failed to get the last commit time for {repo_dir}")
        return ""


def format_repo_link(url):
    """Build the Markdown link cell ``[owner/repo](https://...)`` from a clone URL."""
    display_url = url[:-len(".git")] if url.endswith(".git") else url
    owner_repo = "/".join(display_url.split("/")[-2:])
    return f"[{owner_repo}]({display_url})"


def collect_repo_row(url, branch, tmp_root):
    """Clone a repo and assemble a single Markdown table row.

    @return  ``[link, license, last_commit_time]`` or ``None`` on failure.
    """
    repo_dir = clone_repo(url, branch, tmp_root)
    if repo_dir is None:
        return None
    last_commit = get_last_commit_time(repo_dir)
    if not last_commit:
        return None
    return [format_repo_link(url), detect_license(repo_dir), last_commit]


# ---------------------------------------------------------------------------
# Rendering helpers
# ---------------------------------------------------------------------------

def _sort_by_commit_desc(row):
    return datetime.strptime(row[2], "%Y-%m-%d %H:%M:%S")


def render_table(rows):
    """Render the Markdown table from ``rows`` (list of 3-cell lists).

    Cells are padded so that pipes are vertically aligned, satisfying the
    ``remark-lint:table-pipe-alignment`` and ``remark-lint:table-cell-padding``
    rules used by ``awesome-lint``.
    """
    rows_sorted = sorted(rows, key=_sort_by_commit_desc, reverse=True)
    str_rows = [[str(c) for c in row] for row in rows_sorted]
    headers = list(TABLE_HEADERS)
    widths = [len(h) for h in headers]
    for row in str_rows:
        for i, cell in enumerate(row):
            if len(cell) > widths[i]:
                widths[i] = len(cell)

    def fmt_row(cells):
        return "| " + " | ".join(cell.ljust(widths[i]) for i, cell in enumerate(cells)) + " |"

    header_line = fmt_row(headers)
    separator_line = "| " + " | ".join("-" * widths[i] for i in range(len(headers))) + " |"
    body = [fmt_row(row) for row in str_rows]
    return "\n".join([header_line, separator_line, *body])


def render_readme(template_text, table_md):
    """Replace the ``{{LIBRARIES_TABLE}}`` placeholder in the template."""
    if PLACEHOLDER not in template_text:
        print(f"Template is missing the {PLACEHOLDER} placeholder")
        sys.exit(1)
    return template_text.replace(PLACEHOLDER, table_md)


def _prepare_tmp_dir(tmp_dir):
    shutil.rmtree(tmp_dir, ignore_errors=True)
    os.makedirs(tmp_dir, exist_ok=True)


# ---------------------------------------------------------------------------
# Pipeline stages
# ---------------------------------------------------------------------------

def step_format(args):
    """Stage 1: format ``readme.md`` from ``libraries.yml`` + template.

    @return  Number of rendered library rows.
    """
    template_path = Path(args.template)
    if not template_path.is_file():
        print(f"template {args.template} not exist")
        sys.exit(1)
    template_text = template_path.read_text()

    entries = load_libraries(args.file)
    if args.dry_run:
        first = entries[0]
        print(f"[dry-run] cloning only the first entry: {first[0]} (branch={first[1] or 'default'})")
        entries = entries[:1]

    tmp_dir = str(DEFAULT_TMP_DIR)
    _prepare_tmp_dir(tmp_dir)

    total = len(entries)
    rows = []
    succeeded = 0
    failed = 0
    print(f"==> Cloning and inspecting {total} repositor{'y' if total == 1 else 'ies'}...")
    for idx, (url, branch) in enumerate(entries, start=1):
        prefix = f"[{idx}/{total}]"
        branch_hint = f" (branch={branch})" if branch else ""
        print(f"{prefix} {url}{branch_hint}", flush=True)
        row = collect_repo_row(url, branch, tmp_dir)
        if row is not None:
            rows.append(row)
            succeeded += 1
            print(f"{prefix}   -> ok | {row[1]} | {row[2]}", flush=True)
        else:
            failed += 1
            print(f"{prefix}   -> FAILED", flush=True)
    print(f"==> Done: {succeeded} ok, {failed} failed, {total} total")

    table_md = render_table(rows)
    readme_text = render_readme(template_text, table_md)

    if args.stdout:
        print(readme_text)
    else:
        Path(args.output).write_text(readme_text)
        print(f"Wrote {args.output} ({len(rows)} libraries)")
    return len(rows)


def step_lint():
    """Stage 2: run ``npx awesome-lint`` against this repository's readme.md.

    @return  ``0`` on success, non-zero on failure.
    """
    if not (REPO_ROOT / "readme.md").is_file():
        print(f"readme.md not found under {REPO_ROOT}")
        return 1
    rc = subprocess.call(["npx", "awesome-lint"], cwd=REPO_ROOT)
    if rc != 0:
        print("awesome-lint failed")
        return 1
    print("awesome-lint passed")
    return 0


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def _build_parser():
    parser = argparse.ArgumentParser(
        description="Format readme.md from libraries.yml + template, then run awesome-lint",
    )
    parser.add_argument("--file", default=str(DEFAULT_LIBRARIES_FILE),
                        help=f"Path to libraries YAML (default: {DEFAULT_LIBRARIES_FILE})")
    parser.add_argument("--template", default=str(DEFAULT_TEMPLATE_FILE),
                        help=f"Path to readme template (default: {DEFAULT_TEMPLATE_FILE})")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_FILE),
                        help=f"Path to write the rendered readme (default: {DEFAULT_OUTPUT_FILE})")
    parser.add_argument("--stdout", action="store_true",
                        help="Print the rendered readme instead of writing --output (implies --no-lint)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Only clone the first entry during the format step")
    parser.add_argument("--no-lint", action="store_true",
                        help="Skip the awesome-lint step")
    return parser


def main():
    args = _build_parser().parse_args()
    step_format(args)
    if args.stdout or args.no_lint:
        return 0
    return step_lint()


if __name__ == "__main__":
    sys.exit(main())

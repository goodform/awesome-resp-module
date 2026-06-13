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

PLACEHOLDER_TABLE = "{{LIBRARIES_TABLE}}"
PLACEHOLDER_TOC   = "{{LIBRARIES_TOC}}"
TABLE_HEADERS = ("Repo", "Description", "Tags", "Status")

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

def load_categories(file_path):
    """Read the ``categories`` section from ``libraries.yml``.

    @param file_path  Path to the YAML file.
    @return           ``(valid_names, descriptions)`` tuple where
                      ``valid_names`` is a ``set`` of allowed category names
                      and ``descriptions`` is a ``dict`` mapping name -> text.
    @exit             1 if the ``categories`` section is missing or empty.
    """
    path = Path(file_path)
    data = yaml.safe_load(path.read_text())
    cats = data.get("categories")
    if not isinstance(cats, list) or not cats:
        print("Invalid libraries.yml: top-level 'categories' must be a non-empty list")
        sys.exit(1)

    valid_names = set()
    descriptions = {}
    for idx, item in enumerate(cats):
        name = item.get("name")
        if not name:
            print(f"Skip categories entry #{idx}: missing 'name'")
            continue
        valid_names.add(name)
        descriptions[name] = item.get("description", "")
    if not valid_names:
        print("No valid category names found in libraries.yml")
        sys.exit(1)
    return valid_names, descriptions


def load_libraries(file_path, valid_categories):
    """Read ``libraries.yml`` from disk and return ``[(url, branch, description, tags, category), ...]``.

    @param file_path         Path to the YAML file.
    @param valid_categories  Set of allowed category names (from ``load_categories``).
    @return                  List of (url, branch, description, tags, category) tuples preserving file order.
    @exit                    1 if the file is missing or has no entries.
    """
    path = Path(file_path)
    if not path.is_file():
        print(f"file {file_path} not exist")
        sys.exit(1)

    data = yaml.safe_load(path.read_text())
    libs = data.get("libraries")
    if not isinstance(libs, list) or not libs:
        print("Invalid libraries.yml: top-level 'libraries' must be a non-empty list")
        sys.exit(1)

    out = []
    for idx, item in enumerate(libs):
        if not isinstance(item, dict) or not item.get("url"):
            print(f"Skip entry #{idx}: missing 'url'")
            continue
        category = item.get("category", "")
        if category not in valid_categories:
            print(f"ERROR: entry #{idx} ({item['url']}) has invalid category "
                  f"'{category}'. Valid categories: {sorted(valid_categories)}")
            sys.exit(1)
        out.append((
            item["url"],
            item.get("branch"),
            item.get("description", ""),
            item.get("tags", []),
            category,
        ))
    return out


# ---------------------------------------------------------------------------
# Per-repository helpers
# ---------------------------------------------------------------------------

def _repo_name_from_url(url):
    """Extract the bare repo name from a clone URL."""
    name = os.path.basename(url)
    if name.endswith(".git"):
        name = name[:-len(".git")]
    return name


def _git_env():
    """Return an environment dict with ``GIT_LFS_SKIP_SMUDGE=1`` set.

    Some repos (e.g. RedisAI) enable LFS, but when the remote disables LFS,
    ``git clone`` / ``git fetch`` fails with "smudge filter lfs failed".  We
    only need the LICENSE files and the last commit time, never the actual LFS
    payloads, so skipping the smudge filter is safe.
    """
    env = os.environ.copy()
    env["GIT_LFS_SKIP_SMUDGE"] = "1"
    return env


def _do_clone(url, branch, target):
    """Perform a fresh ``git clone --depth 1`` into ``target``.

    @return  ``target`` on success, ``None`` on failure.
    """
    cmd = ["git", "clone", "--quiet", "--depth", "1"]
    if branch:
        cmd += ["-b", branch, "--single-branch"]
    cmd += [url, str(target)]

    try:
        rc = subprocess.call(cmd, env=_git_env())
    except subprocess.CalledProcessError:
        rc = 1
    if rc != 0 or not target.is_dir():
        return None
    return target


def ensure_repo(url, branch, dest_root):
    """Ensure ``url`` is available at ``dest_root/<repo_name>``.

    If the repo already exists locally, fetch the latest commit via
    ``git fetch --depth 1`` + ``git checkout FETCH_HEAD`` instead of
    re-cloning.  Falls back to a fresh ``git clone --depth 1`` when the
    directory is missing, corrupted, or the remote URL has changed.

    @param url        Git clone URL (typically ending with ``.git``).
    @param branch     Optional branch name; ``None`` for the remote default.
    @param dest_root  Directory in which the repo resides.
    @return           Path to the repository on success, else ``None``.
    """
    repo_name = _repo_name_from_url(url)
    target = Path(dest_root) / repo_name
    env = _git_env()

    # --- Fast path: repo already exists, try incremental fetch ----------
    if target.is_dir() and (target / ".git").exists():
        # Verify the remote URL still matches the YAML entry.
        try:
            current_url = subprocess.check_output(
                ["git", "remote", "get-url", "origin"],
                cwd=target, env=env,
            ).decode().strip()
        except subprocess.CalledProcessError:
            current_url = ""
        if current_url.rstrip("/") != url.rstrip("/"):
            print(f"  Remote URL changed for {repo_name}, re-cloning ...")
            shutil.rmtree(target, ignore_errors=True)
            return _do_clone(url, branch, target)

        # Fetch the latest commit (shallow).
        fetch_cmd = ["git", "fetch", "--depth", "1", "origin"]
        if branch:
            fetch_cmd.append(branch)
        try:
            rc = subprocess.call(fetch_cmd, cwd=target, env=env)
        except subprocess.CalledProcessError:
            rc = 1
        if rc != 0:
            print(f"  Fetch failed for {repo_name}, re-cloning ...")
            shutil.rmtree(target, ignore_errors=True)
            return _do_clone(url, branch, target)

        # Move HEAD to the just-fetched commit.
        try:
            subprocess.check_call(
                ["git", "checkout", "-q", "-f", "FETCH_HEAD"],
                cwd=target, env=env,
            )
        except subprocess.CalledProcessError:
            shutil.rmtree(target, ignore_errors=True)
            return _do_clone(url, branch, target)

        return target

    # --- Slow path: directory missing or not a git repo -----------------
    if target.exists():
        shutil.rmtree(target, ignore_errors=True)
    result = _do_clone(url, branch, target)
    if result is None:
        print(f"Failed to clone {url}")
    return result


def detect_license(repo_dir):
    """Detect the license type by scanning license-like files in ``repo_dir``."""
    license_files = []
    for root, _, files in os.walk(repo_dir):
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


def collect_repo_row(url, branch, description, tags, category, tmp_root):
    """Ensure a repo is available and assemble a single Markdown table row.

    @return  ``[link, description, tags, license, last_commit_time, category]`` or ``None`` on failure.
    """
    repo_dir = ensure_repo(url, branch, tmp_root)
    if repo_dir is None:
        return None
    last_commit = get_last_commit_time(repo_dir)
    if not last_commit:
        return None
    return [format_repo_link(url), description, tags, detect_license(repo_dir), last_commit, category]


# ---------------------------------------------------------------------------
# Rendering helpers
# ---------------------------------------------------------------------------

def _sort_by_commit_desc(row):
    return datetime.strptime(row[4], "%Y-%m-%d %H:%M:%S")


def _format_tags(tags):
    """Convert a list of tag strings to inline-code Markdown.

    @param tags  List of tag strings (e.g. ``["search", "vector"]``).
    @return      Space-separated `` `tag` `` items, or ``-`` if empty.
    """
    if not tags:
        return "-"
    return " ".join(f"`{t}`" for t in tags)


def _format_license_time(license_str, commit_time_str):
    """Merge license and last-commit-time into one cell.

    If the last commit is more than 2 years ago, the time portion is rendered
    in *italics*.

    @param license_str       License name string.
    @param commit_time_str   ``YYYY-MM-DD HH:MM:SS`` string.
    @return                  ``"license | time"`` or ``"license | *time*"``.
    """
    try:
        dt = datetime.strptime(commit_time_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return f"{commit_time_str} · {license_str}"
    # Display only the date portion (YYYY-MM-DD).
    date_str = dt.strftime("%Y-%m-%d")
    if (datetime.now() - dt).days > 730:
        return f"*{date_str}* · {license_str}"
    return f"{date_str} · {license_str}"


def _render_single_table(rows, headers):
    """Render a Markdown table from ``rows`` (list of cell lists).

    Cells are padded so that pipes are vertically aligned, satisfying the
    ``remark-lint:table-pipe-alignment`` and ``remark-lint:table-cell-padding``
    rules used by ``awesome-lint``.
    """
    str_rows = [[str(c) for c in row] for row in rows]
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


def _anchor_from_category(cat):
    """Convert a category name to a GitHub-compatible anchor slug."""
    return cat.lower().replace(" & ", "--").replace(" ", "-")


def render_toc(categories):
    """Render the Libraries sub-section of the Contents from a list of category names.

    @param categories  Ordered list of category names (as they appear in the YAML).
    @return            Markdown lines for the Contents section under ``- [Libraries]``.
    """
    lines = ["- [Libraries](#libraries)"]
    for cat in categories:
        anchor = _anchor_from_category(cat)
        lines.append(f"  - [{cat}](#{anchor})")
    return "\n".join(lines)


def render_categorized_tables(rows, category_descriptions):
    """Render category-grouped Markdown tables from ``rows``.

    Each row is ``[link, description, tags, license, last_commit_time, category]``.
    Rows are grouped by ``category``, sorted within each group by last commit
    time descending, and rendered as ``### Category Name`` + a Markdown table.

    @param category_descriptions  ``dict`` mapping category name -> description text.
    @return                       ``(markdown_string, ordered_category_names)`` tuple.
    """
    # Group rows by category.
    groups = {}
    for row in rows:
        cat = row[5]
        groups.setdefault(cat, []).append(row)

    # Preserve the order categories first appear in the YAML.
    seen = []
    for row in rows:
        cat = row[5]
        if cat not in seen:
            seen.append(cat)

    display_headers = list(TABLE_HEADERS)

    sections = []
    for cat in seen:
        cat_rows = groups[cat]
        cat_rows.sort(key=_sort_by_commit_desc, reverse=True)
        # Build display rows: [link, description, formatted_tags, license|time]
        display_rows = []
        for row in cat_rows:
            display_rows.append([
                row[0],  # link
                row[1],  # description
                _format_tags(row[2]),  # tags
                _format_license_time(row[3], row[4]),  # license & last commit
            ])
        desc = category_descriptions.get(cat, "")
        section = f"### {cat}\n\n{desc}\n\n{_render_single_table(display_rows, display_headers)}"
        sections.append(section)

    return "\n\n".join(sections), seen


def render_readme(template_text, categorized_md, toc_md):
    """Replace ``{{LIBRARIES_TABLE}}`` and ``{{LIBRARIES_TOC}}`` placeholders."""
    if PLACEHOLDER_TABLE not in template_text:
        print(f"Template is missing the {PLACEHOLDER_TABLE} placeholder")
        sys.exit(1)
    if PLACEHOLDER_TOC not in template_text:
        print(f"Template is missing the {PLACEHOLDER_TOC} placeholder")
        sys.exit(1)
    text = template_text.replace(PLACEHOLDER_TABLE, categorized_md)
    return text.replace(PLACEHOLDER_TOC, toc_md)


def _prepare_tmp_dir(tmp_dir):
    """Ensure the tmp directory exists (no longer clears it on every run)."""
    os.makedirs(tmp_dir, exist_ok=True)


def _cleanup_stale_repos(tmp_dir, expected_names):
    """Remove repo directories in ``tmp_dir`` that are no longer listed in ``libraries.yml``.

    @param tmp_dir         Path to the tmp directory.
    @param expected_names  Set of repo directory names that should be kept.
    """
    if not os.path.isdir(tmp_dir):
        return
    for entry in os.listdir(tmp_dir):
        entry_path = os.path.join(tmp_dir, entry)
        if os.path.isdir(entry_path) and entry not in expected_names:
            print(f"  Cleaning up stale repo: {entry}")
            shutil.rmtree(entry_path, ignore_errors=True)


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

    valid_categories, category_descriptions = load_categories(args.file)
    entries = load_libraries(args.file, valid_categories)

    # Build the set of expected repo names for stale cleanup *before* dry-run
    # truncation so that we never accidentally delete repos that are still
    # listed in libraries.yml.
    expected_names = {_repo_name_from_url(url) for url, _, _, _, _ in entries}

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
    print(f"==> Ensuring {total} repositor{'y' if total == 1 else 'ies'} (incremental fetch + fallback clone)...")
    for idx, (url, branch, description, tags, category) in enumerate(entries, start=1):
        prefix = f"[{idx}/{total}]"
        branch_hint = f" (branch={branch})" if branch else ""
        print(f"{prefix} {url}{branch_hint}", flush=True)
        row = collect_repo_row(url, branch, description, tags, category, tmp_dir)
        if row is not None:
            rows.append(row)
            succeeded += 1
            print(f"{prefix}   -> ok | {row[3]} | {row[4]}", flush=True)
        else:
            failed += 1
            print(f"{prefix}   -> FAILED", flush=True)
    print(f"==> Done: {succeeded} ok, {failed} failed, {total} total")

    # Remove repos that are no longer in libraries.yml.
    _cleanup_stale_repos(tmp_dir, expected_names)

    categorized_md, categories = render_categorized_tables(rows, category_descriptions)
    toc_md = render_toc(categories)
    readme_text = render_readme(template_text, categorized_md, toc_md)

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

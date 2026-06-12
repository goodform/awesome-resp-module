# Contribution Guidelines

Please ensure your pull request adheres to the following guidelines:

- The repository you suggest must be related to a Valkey or Redis module.
- Add a single entry to [`libraries.yml`](libraries.yml) per pull request.
- Each entry must use the `https://...` clone URL ending with `.git`.
- Optionally specify a `branch` field if the module's default branch is not the one to track.
- Run `python3 scripts/format-awesome-resp.py` locally before opening the pull request, and commit the regenerated `readme.md`.
- Make sure the entry's repository itself follows the [Awesome list guidelines](https://github.com/sindresorhus/awesome/blob/main/awesome.md).

Thank you for your suggestions!

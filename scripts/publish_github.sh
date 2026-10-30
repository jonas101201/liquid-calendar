#!/usr/bin/env bash
# Creates a public repository and publishes this prerelease through an authenticated GitHub CLI.
set -euo pipefail
release_root="$(cd -- "$(dirname -- "$0")/.." && pwd)"
cd -- "$release_root"
command -v gh >/dev/null || { echo 'Install the GitHub CLI from https://cli.github.com/ and run gh auth login first.' >&2; exit 1; }
gh auth status >/dev/null
release_owner="${1:-$(gh api user --jq .login)}"
release_repo="$release_owner/liquid-calendar"
release_version="$(tr -d '\r\n' < VERSION)"
release_tag="v$release_version"
[[ -z "$(git status --porcelain)" ]] || { echo 'Commit or review all source changes before publishing.' >&2; exit 1; }
git rev-parse --verify "$release_tag" >/dev/null
[[ "$(git branch --show-current)" == main ]] || { echo 'Switch to the main branch before publishing.' >&2; exit 1; }
[[ "$(git rev-parse HEAD)" == "$(git rev-parse "$release_tag^{commit}")" ]] || { echo 'The beta tag must identify this exact source commit. Refusing mismatched assets.' >&2; exit 1; }
python3 scripts/build_release.py
if git remote get-url origin >/dev/null 2>&1; then
    release_origin="$(git remote get-url origin)"
    [[ "$release_origin" == "https://github.com/$release_repo.git" || "$release_origin" == "git@github.com:$release_repo.git" || "$release_origin" == "https://github.com/$release_repo" ]] || { echo 'Existing origin does not match the requested repository.' >&2; exit 1; }
else
    if gh repo view "$release_repo" >/dev/null 2>&1; then
        echo "Repository $release_repo already exists. Review and attach its origin explicitly before rerunning." >&2
        exit 1
    fi
    gh repo create "$release_repo" --public --source . --remote origin --description 'Local calendar and task planner for Fedora/KDE Plasma. Public beta.' --push
fi
git push origin main
git push origin "$release_tag"
if gh release view "$release_tag" --repo "$release_repo" >/dev/null 2>&1; then
    echo 'This release already exists; refusing to replace published assets.' >&2
    exit 1
fi
mapfile -t release_assets < <(python3 -c 'import json; print("\n".join("dist/"+name for name in json.load(open("dist/release.json"))["assets"]))')
gh release create "$release_tag" --repo "$release_repo" --verify-tag --prerelease --title "Liquid Calendar ${release_version/-beta./ Beta }" --notes-file RELEASE_NOTES.md "${release_assets[@]}"
gh release view "$release_tag" --repo "$release_repo" --json url --jq .url

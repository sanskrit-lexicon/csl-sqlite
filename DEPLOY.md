# Deployment — csl-sqlite

## Overview

csl-sqlite is a **distribution-only** repository. There are no scripts to run here.
Deployment means uploading newly built SQLite files as a GitHub Release asset.

The SQLite files are generated upstream by `csl-pywork` from source text in `csl-orig`.

## Prerequisites

| Tool | Version | Install |
|---|---|---|
| GitHub CLI (`gh`) | ≥ 2.x | https://cli.github.com/ |
| `csl-pywork` pipeline | current | see that repo's DEPLOY.md |

## Environment variables

| Variable | Required | Description |
|---|---|---|
| `GITHUB_TOKEN` | yes (for `gh`) | Token with `repo` scope for creating releases |

## Routine deployment (after csl-orig update)

```bash
# Step 1 — run the build pipeline in csl-pywork to generate SQLite files
# (see csl-pywork's DEPLOY.md for the exact build command)
<run csl-pywork build>

# Step 2 — validate output
# [to be filled by reviewer — describe any validation checks]
<validation step>

# Step 3 — create a new GitHub Release and upload SQLite files
gh release create <tag> --repo sanskrit-lexicon/csl-sqlite \
  --title "Release <tag>" \
  --notes "Updated SQLite files from csl-orig <commit>." \
  *.sqlite
```

## Rollback

To revert to a previous release, point downstream consumers at the previous release tag URL:

```bash
# Download a specific prior release
gh release download <previous-tag> --repo sanskrit-lexicon/csl-sqlite --pattern "*.sqlite"
```

GitHub Releases are immutable once published; the previous release remains available.

## Health check

After publishing a release, verify:
1. The new release appears at https://github.com/sanskrit-lexicon/csl-sqlite/releases/latest
2. Asset file sizes are non-zero and consistent with the previous release.
3. [to be filled by reviewer: any automated smoke-test against the SQLite schema]

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `gh release create` fails with auth error | GITHUB_TOKEN missing or insufficient | Re-authenticate: `gh auth login` |
| Release assets are 0 bytes | Build pipeline error upstream | Re-run csl-pywork build; check its logs |
| `csl-app` not picking up new data | csl-app has its own update schedule | Trigger csl-app's deployment separately |

## Deployment frequency

Triggered manually after `csl-orig` merges a correction batch.
Typical cadence: weekly during active correction periods, monthly otherwise.

## CI / automation

No GitHub Actions workflows are currently configured in this repository.
Deployment is performed manually by a project maintainer.

## Downstream

Once published, SQLite files are consumed by:
- **csl-app** — downloads them to serve the web API
- **Researchers** — download directly from the GitHub Releases page

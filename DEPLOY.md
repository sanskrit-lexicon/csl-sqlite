# Deployment — csl-sqlite

## What "deploy" means here

This repo holds **no build scripts**. "Deploying" csl-sqlite means creating a new
GitHub Release and uploading freshly built per-dictionary SQLite zip files as
release assets. The build itself runs in
[csl-pywork](https://github.com/sanskrit-lexicon/csl-pywork) — see its
`v02/makotemplates/pywork/sqlite/sqlite.py`.

In 2026, releases happen roughly weekly (see the
[Releases page](https://github.com/sanskrit-lexicon/csl-sqlite/releases) for the
real cadence). Each release replaces the previous; older releases stay available
and immutable.

## Prerequisites

| Tool | Notes |
|---|---|
| `gh` CLI ≥ 2.x | https://cli.github.com/ — used to create the release and upload assets |
| Built `.sqlite` files | Produced by csl-pywork on the build host |
| GitHub auth | `gh auth login` once; or `GITHUB_TOKEN` env var with `repo` scope |

## Release-tag convention

Existing tags use a UTC timestamp: `YYYY-MM-DD-HH-MM-SS`. Example:
`2026-05-17-07-42-11`. Stick to this pattern so the Releases list sorts cleanly.

## Routine procedure

```bash
# 1. Build SQLite files in csl-pywork (per its own runbook). Produces:
#       <short>.sqlite           -- one per dictionary (~42 dicts)
#       <short>_lslinks.sqlite   -- for dicts with literary-source links
#       hwnorm1c.sqlite, keydoc_glob1.sqlite  -- auxiliary global DBs
#    Then zip each .sqlite into <name>.zip.

# 2. Pick a tag:
TAG=$(date -u +"%Y-%m-%d-%H-%M-%S")

# 3. Create the release (in the directory holding the .zip files):
gh release create "$TAG" \
   --repo sanskrit-lexicon/csl-sqlite \
   --title "Release $TAG" \
   --notes "Updated SQLite files." \
   *.zip
```

`gh release create` uploads each `.zip` in the current directory as a release asset
in one call. For a typical release this is ~50 assets totalling ~250 MB.

## Verifying a release

After the upload completes:

```bash
# Confirm asset count and sizes match expectations
gh release view "$TAG" --repo sanskrit-lexicon/csl-sqlite \
  --json assets --jq '.assets | length, ([.[].size] | add)'

# Spot-check a SQLite file
gh release download "$TAG" --repo sanskrit-lexicon/csl-sqlite --pattern "mw.zip"
unzip -p mw.zip mw.sqlite | sqlite3 :memory: "SELECT COUNT(*) FROM mw;"
```

The MW entry count should be in the same ballpark as the previous release
(currently ~286,561 — see [MWS DATA_DICTIONARY.md](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/DATA_DICTIONARY.md)).

## Rollback

GitHub Releases are immutable once published, so "rollback" means asking
downstream consumers to pin to the previous tag:

```bash
gh release download <previous-tag> --repo sanskrit-lexicon/csl-sqlite --pattern "*.zip"
```

To remove a bad release entirely:

```bash
gh release delete "$TAG" --repo sanskrit-lexicon/csl-sqlite --cleanup-tag
```

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `gh release create` fails with HTTP 401 | Missing or insufficient auth | `gh auth login` (needs `repo` scope) |
| Asset uploads stall or 0-byte | Slow upstream / network drop | Retry: `gh release upload $TAG <file>.zip --clobber` |
| `csl-app` still serving old data | csl-app has its own update job | Trigger csl-app's deployment separately |
| Local clone bloats unexpectedly | Someone ran `git pull` | The repo tree itself stays small; Releases are not in the tree |

## CI / automation

No GitHub Actions workflows are committed in this repository as of 2026-05-22. The
weekly release cadence visible in the Releases page is driven by an external
scheduled job (lives outside this repo). Adding a workflow here that ties release
creation to csl-pywork builds would close that gap.

## Downstream consumers

| Consumer | How they pick up new data |
|---|---|
| [csl-app](https://github.com/sanskrit-lexicon/csl-app) | Pulls the latest SQLite files from the most recent Release |
| Researchers | Download specific zips from the Releases UI |
| Local dev | `gh release download --pattern "<short>.zip"` |

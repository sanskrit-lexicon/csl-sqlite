# csl-sqlite
Storage space for sqlites of Cologne Digital Sanskrit Dictionaries

Purpose of this repository is to release the latest data to the users / downstream scripts. 
 
Do not do `git pull` on this repository. It will unnecessarily fetch too much data from 'Releases'.

If you are interested in the latest data, you can visit https://github.com/sanskrit-lexicon/csl-sqlite/releases/latest and download the latest data.

Each release publishes ~50 zip files: one per dictionary (`mw.zip`, `pwg.zip`, etc.),
plus literary-source link files (`<short>_lslinks.sqlite.zip`) and global auxiliary
databases (`hwnorm1c.sqlite.zip`, `keydoc_glob1.sqlite.zip`).

```bash
# Quick download (e.g. Monier-Williams)
gh release download --repo sanskrit-lexicon/csl-sqlite --pattern "mw.zip"
unzip mw.zip                                          # -> mw.sqlite
sqlite3 mw.sqlite "SELECT COUNT(*) FROM mw;"          # -> ~286,561
```

## Architecture overview

csl-sqlite is a **distribution channel** in the CDSL pipeline:

```
csl-orig (source text) → csl-pywork (build) → csl-sqlite (releases) → csl-app / users
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for the full component diagram and data-flow description.

## Related repositories

| Repository | Role |
|---|---|
| [csl-orig](https://github.com/sanskrit-lexicon/csl-orig) | Digitized source text for all dictionaries |
| [csl-pywork](https://github.com/sanskrit-lexicon/csl-pywork) | Build pipeline that generates SQLite files |
| [csl-app](https://github.com/sanskrit-lexicon/csl-app) | Web API server that consumes these SQLite files |
| [csl-homepage](https://github.com/sanskrit-lexicon/csl-homepage) | Project website and documentation hub |

## Citation

If you use these dictionaries in research, please cite the repository using the metadata
in [CITATION.cff](CITATION.cff).

#!/usr/bin/env python3
"""make_manifest.py -- build dictionaries.json for csl-sqlite.

Publishes alongside the <dict>.zip files so clients (csl-app) can discover
dictionaries without a hardcoded list.

Inputs
  --indexdirs  csl-homepage/indexdirs.xml  (title, authors, text date, pages)
  --overlay    scripts/dictionary_overlay.json (group, flags, status, profile)
  --zips       directory holding the <dict>.zip files to be published
               (only dictionaries whose zip exists are listed)
Output
  --out        dictionaries.json

A dictionary present as a zip but absent from indexdirs.xml is still listed
(with its code as name) and a warning is printed, so a new release never
drops a dictionary just because metadata lags behind.

Usage
  python3 -I scripts/make_manifest.py \
      --indexdirs ../csl-homepage/indexdirs.xml \
      --zips /path/to/zips --out dictionaries.json
"""
import argparse
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from datetime import date

SCHEMA_VERSION = 1
# <code>.zip only: excludes <code>_lslinks.sqlite.zip, hwnorm1c.sqlite.zip, ...
ZIP_RE = re.compile(r'^([a-z0-9]+)\.zip$')
DEFAULTS = {
    'group': None,
    'hasAccent': False,
    'hasDeva': False,
    'englishHeadwords': False,
    'status': 'active',
    'renderProfile': 'default',
}


def read_indexdirs(path):
    meta = {}
    for e in ET.parse(path).getroot().findall('entry'):
        code = (e.findtext('pfx') or '').strip().lower()
        if not code:
            continue
        meta[code] = {
            'name': (e.findtext('title') or '').strip(),
            'authors': (e.findtext('authors') or '').strip(),
            'textDate': (e.findtext('textdate') or '').strip(),
            'pages': (e.findtext('textpages') or '').strip(),
        }
    return meta


def year_of(text_date):
    m = re.search(r'\b(1[0-9]{3}|20[0-9]{2})\b', text_date or '')
    return int(m.group(1)) if m else None


def build(indexdirs, overlay, zips_dir):
    meta = read_indexdirs(indexdirs)
    zips = {}
    for fn in sorted(os.listdir(zips_dir)):
        m = ZIP_RE.match(fn)
        if m:
            zips[m.group(1)] = os.path.getsize(os.path.join(zips_dir, fn))

    entries, warnings = [], []
    for code, size in sorted(zips.items()):
        info = meta.get(code)
        ov = overlay.get(code, {})
        if info is None:
            warnings.append(f'{code}: zip present but not in indexdirs.xml')
            info = {'name': code.upper(), 'authors': '', 'textDate': '', 'pages': ''}
        if code not in overlay:
            warnings.append(f'{code}: no overlay entry (using defaults)')
        e = {'code': code, 'name': info['name'], 'authors': info['authors'],
             'textDate': info['textDate'], 'year': year_of(info['textDate']),
             'pages': info['pages'], 'zip': f'{code}.zip', 'bytes': size}
        for k, dv in DEFAULTS.items():
            e[k] = ov.get(k, dv)
        entries.append(e)

    for code in sorted(set(meta) - set(zips)):
        warnings.append(f'{code}: in indexdirs.xml but no zip (omitted)')
    return {'schemaVersion': SCHEMA_VERSION,
            'generated': date.today().isoformat(),
            'dictionaries': entries}, warnings


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    here = os.path.dirname(os.path.abspath(__file__))
    ap.add_argument('--indexdirs', required=True)
    ap.add_argument('--overlay', default=os.path.join(here, 'dictionary_overlay.json'))
    ap.add_argument('--zips', required=True)
    ap.add_argument('--out', default='dictionaries.json')
    a = ap.parse_args()
    with open(a.overlay, encoding='utf-8') as f:
        overlay = json.load(f)['dictionaries']
    manifest, warnings = build(a.indexdirs, overlay, a.zips)
    for w in warnings:
        print('WARNING:', w, file=sys.stderr)
    with open(a.out, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
        f.write('\n')
    print(f'wrote {a.out}: {len(manifest["dictionaries"])} dictionaries')


if __name__ == '__main__':
    main()

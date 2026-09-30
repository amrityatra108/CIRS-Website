#!/usr/bin/env python3
"""Build Alumni hit areas from world-atlas@2.0.2 countries-50m.json.

Natural Earth 1:50m admin-0 geometry (public domain), distributed by
world-atlas (ISC). Run with a local topology path; normal builds are offline.
Uses the existing Robinson projection, crop and antimeridian handling.
No country area threshold: small territories must remain selectable in text.
Boundaries are illustrative, not a statement of political recognition.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

SOURCE_SHA256 = '04342cdc1e3016bcd7db1630de95684d67b79fe3c8c460321e87aef469502394'
ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('worldmap', ROOT / 'make-worldmap.py')
worldmap = importlib.util.module_from_spec(spec)
spec.loader.exec_module(worldmap)


def generate(source):
    raw = Path(source).read_bytes()
    if hashlib.sha256(raw).hexdigest() != SOURCE_SHA256:
        raise ValueError('Expected the unmodified world-atlas@2.0.2 countries-50m.json')
    topo = json.loads(raw)
    arcs = worldmap.arcs_of(topo)
    countries = []
    for geom in topo['objects']['countries']['geometries']:
        paths = []
        polys = geom['arcs'] if geom['type'] == 'MultiPolygon' else [geom['arcs']]
        for poly in polys:
            for indices in poly:
                ring = []
                for i in indices:
                    arc = arcs[~i][::-1] if i < 0 else arcs[i]
                    ring.extend(arc[1:] if ring else arc)
                if not ring or max(lat for lon, lat in ring) < worldmap.robinson.LAT_MIN:
                    continue
                pts = [worldmap.robinson.project(lat, lon)
                       for lon, lat in worldmap.unwrapped(ring)]
                simplified = worldmap.simplify(pts, .035)
                if len(simplified) >= 4:
                    pts = simplified
                paths.append('M' + 'L'.join('%.3f %.3f' % p for p in pts) + 'Z')
        if paths:
            countries.append({'id': geom.get('id', geom['properties']['name'].lower().replace(' ', '-')), 'name': geom['properties']['name'],
                              'path': ''.join(paths)})
    countries.sort(key=lambda c: c['name'])
    output = {'source': 'world-atlas@2.0.2/countries-50m.json',
              'source_sha256': SOURCE_SHA256,
              'license': 'Natural Earth public domain; world-atlas ISC',
              'projection': 'tools/robinson.py', 'countries': countries}
    (ROOT / 'alumni-countries.json').write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n')
    print('Generated %d country/territory shapes' % len(countries))


if __name__ == '__main__':
    generate(sys.argv[1])

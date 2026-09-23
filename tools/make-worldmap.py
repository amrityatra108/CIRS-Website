#!/usr/bin/env python3
"""Mirror the world's coastline into tools/worldland.py, once.

The alumni field is a map, and a map needs a coastline. This fetches one,
projects it with tools/robinson.py, simplifies it hard enough to be worth
inlining in a page, and writes the result out as a Python module of SVG
path data. Like tools/make-fonts.py, it is run by hand and what it writes
is committed: the build has no network and must not need one.

    python3 tools/make-worldmap.py

SOURCE. Natural Earth's 110m land layer, in the public domain, taken from
the world-atlas package on npm (ISC, Mike Bostock) because Natural Earth's
own downloads are shapefiles. The npm registry is reachable where a CDN is
not, which is why this shells out to `npm pack` rather than curl.

WHAT IT DOES TO IT. 110m is already coarse; it is still far more coastline
than a field 1,200 pixels wide can show. So every ring is projected, then
thinned by Douglas-Peucker at TOL viewBox units — about one part in two
thousand of the width — and any island whose projected area falls below
AREA is dropped entirely. What survives is the shape of the continents at
the size they are actually drawn, and about a fifth of the bytes.
"""

import json
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import robinson  # noqa: E402

PKG = "world-atlas@2.0.2"
SRC = "land-110m.json"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "worldland.py")

TOL = 0.10    # Douglas-Peucker tolerance, in viewBox units (width is 200)
AREA = 0.55   # smallest island kept, in square viewBox units


# ------------------------------------------------------------------
# TopoJSON
# ------------------------------------------------------------------
def arcs_of(topo):
    """Every arc, dequantized into [(lon, lat), ...]."""
    sx, sy = topo["transform"]["scale"]
    tx, ty = topo["transform"]["translate"]
    out = []
    for arc in topo["arcs"]:
        x = y = 0
        pts = []
        for dx, dy in arc:
            x += dx
            y += dy
            pts.append((x * sx + tx, y * sy + ty))
        out.append(pts)
    return out


def rings_of(topo):
    """Every ring of the land object, as lists of (lon, lat)."""
    arcs = arcs_of(topo)

    def ring(idx):
        pts = []
        for i in idx:
            a = arcs[~i][::-1] if i < 0 else arcs[i]
            pts.extend(a[1:] if pts else a)
        return pts

    out = []
    for geom in topo["objects"]["land"]["geometries"]:
        polys = geom["arcs"] if geom["type"] == "MultiPolygon" else [geom["arcs"]]
        for poly in polys:
            for idx in poly:
                out.append(ring(idx))
    return out


# ------------------------------------------------------------------
# Geometry
# ------------------------------------------------------------------
def simplify(pts, tol):
    """Douglas-Peucker, iteratively so a long coastline cannot blow the stack."""
    if len(pts) < 3:
        return pts
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        i, j = stack.pop()
        if j <= i + 1:
            continue
        ax, ay = pts[i]
        bx, by = pts[j]
        dx, dy = bx - ax, by - ay
        den = dx * dx + dy * dy
        far, best = -1, 0.0
        for k in range(i + 1, j):
            px, py = pts[k]
            if den == 0:
                d = (px - ax) ** 2 + (py - ay) ** 2
            else:
                t = ((px - ax) * dx + (py - ay) * dy) / den
                t = 0.0 if t < 0 else (1.0 if t > 1 else t)
                d = (px - ax - t * dx) ** 2 + (py - ay - t * dy) ** 2
            if d > best:
                best, far = d, k
        if best > tol * tol:
            keep[far] = True
            stack.append((i, far))
            stack.append((far, j))
    return [p for p, k in zip(pts, keep) if k]


def area(pts):
    a = 0.0
    for i in range(len(pts)):
        x0, y0 = pts[i - 1]
        x1, y1 = pts[i]
        a += x0 * y1 - x1 * y0
    return abs(a) * 0.5


def unwrapped(ring):
    """A ring with its antimeridian crossings taken out.

    Eurasia's ring runs off the east edge of the frame at Chukotka and
    comes back on at the west one, and Natural Earth writes that as a
    step from 179 to -180 in the middle of a list of points. Projected
    literally it draws a line straight across the Pacific — which is
    what put a rule through the middle of the first map this generated.

    So the longitudes are unwound first, each one taken to within half a
    turn of the one before it, and only then held inside the frame. The
    far tip of Chukotka ends up flat against the right-hand edge, which
    is a fair price and about four pixels wide.
    """
    lons, prev = [], None
    for lon, _lat in ring:
        if prev is not None:
            while lon - prev > 180:
                lon -= 360
            while prev - lon > 180:
                lon += 360
        prev = lon
        lons.append(lon)

    # Unwinding is only relative: a ring that happens to START on the
    # dateline comes out a whole turn away from the frame, and clamping
    # it there draws the west edge of the map instead of Siberia. So the
    # whole ring is brought back by whole turns until it straddles zero.
    shift = 360.0 * round(sum(lons) / len(lons) / 360.0)
    return [(max(-180.0, min(180.0, lon - shift)),
             max(robinson.LAT_MIN, min(robinson.LAT_MAX, lat)))
            for lon, (_o, lat) in zip(lons, ring)]


# ------------------------------------------------------------------
def fetch():
    """The topology, straight out of the npm tarball."""
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["npm", "pack", PKG], cwd=tmp, check=True,
                       stdout=subprocess.DEVNULL)
        tgz = [f for f in os.listdir(tmp) if f.endswith(".tgz")][0]
        subprocess.run(["tar", "xzf", tgz, "package/" + SRC], cwd=tmp, check=True)
        with open(os.path.join(tmp, "package", SRC)) as fh:
            return json.load(fh)


def main():
    topo = fetch()
    paths = []
    dropped = 0
    for ring in rings_of(topo):
        # Antarctica is off the frame entirely, not clipped onto its
        # bottom edge: clamped, its coast becomes a rule under the map.
        if max(la for _lo, la in ring) < robinson.LAT_MIN:
            dropped += 1
            continue
        pts = [robinson.project(la, lo) for lo, la in unwrapped(ring)]
        pts = simplify(pts, TOL)
        if len(pts) < 4 or area(pts) < AREA:
            dropped += 1
            continue
        d = "M" + " L".join("%.2f %.2f" % p for p in pts) + "Z"
        paths.append((area(pts), d))

    # Biggest first: the continents land before the islands, which is the
    # order they should paint in and a kinder one to read in a diff.
    paths.sort(key=lambda p: -p[0])
    body = "".join(d for _a, d in paths)

    with open(OUT, "w") as fh:
        fh.write('''"""The world's coastline, projected — generated, do not edit.

Written by tools/make-worldmap.py from Natural Earth's 110m land layer
(public domain), by way of the world-atlas package on npm (ISC, Mike
Bostock). Already in the frame tools/robinson.py defines, so alumni.py
drops it into the field's viewBox as it stands.

%d rings, simplified at %.2f viewBox units; %d below %.2f square units
were left out.
"""

LAND = (
%s)
''' % (len(paths), TOL, dropped, AREA,
       "\n".join('    "%s"' % body[i:i + 88] for i in range(0, len(body), 88))))

    print("tools/worldland.py: %d rings, %d dropped, %.1f KB"
          % (len(paths), dropped, len(body) / 1024.0))


if __name__ == "__main__":
    main()

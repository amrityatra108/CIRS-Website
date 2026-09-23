#!/usr/bin/env python3
"""The Robinson projection, and the frame the alumni map is drawn in.

Shared by tools/make-worldmap.py, which projects the coastline once and
writes tools/worldland.py, and by tools/alumni.py, which projects the
nineteen destinations and CIRS every build. Both must agree to the last
decimal or the points would float off the coast, so the projection is
written down once, here.

WHY ROBINSON. A web map is a Mercator, and a Mercator on a dark page with
a graticule reads as Google Maps with the lights off — which is the one
thing this field must not look like. Robinson is a compromise projection
drawn for atlases: the continents keep their shapes, the poles are a line
rather than a tearing, and the outline is a leaf rather than a rectangle.
It is a picture of the world, not an interface for one.

The table is Robinson's own, at five-degree steps: X is the length of a
parallel against the equator's, Y its distance from the equator. Between
the steps it is interpolated with a Catmull-Rom spline rather than a
straight line, which is what keeps a coastline from developing a crease
every five degrees.
"""

# lat 0, 5, 10 ... 90
_X = [1.0000, 0.9986, 0.9954, 0.9900, 0.9822, 0.9730, 0.9600, 0.9427,
      0.9216, 0.8962, 0.8679, 0.8350, 0.7986, 0.7597, 0.7186, 0.6732,
      0.6213, 0.5722, 0.5322]
_Y = [0.0000, 0.0620, 0.1240, 0.1860, 0.2480, 0.3100, 0.3720, 0.4340,
      0.4958, 0.5571, 0.6176, 0.6769, 0.7346, 0.7903, 0.8435, 0.8936,
      0.9394, 0.9761, 1.0000]

# Antarctica is left off. It carries no destination, it is a third of the
# height of an uncropped Robinson, and what it would buy is a white smear
# under a field whose whole subject is nineteen points in the north.
LAT_MIN, LAT_MAX = -56.0, 83.5

# The frame. VB_W is chosen, VB_H falls out of the projection, and both are
# written into the viewBox and into .ajc__field's aspect-ratio so that a
# position in percent of the box is a position in the projection.
#
# PAD is sky: bare viewBox units added above and below the projection, so a
# label sitting over Durham has somewhere to go and the coastline does not
# run into the top of the frame. It is inside the frame rather than outside
# it, which is what keeps a percentage of the field a place on the map.
VB_W = 200.0
PAD  = 7.0
_KX, _KY = 0.8487, 1.3523


def _spline(tbl, lat):
    """tbl interpolated at |lat| degrees, Catmull-Rom between the 5° steps."""
    a = min(abs(lat), 90.0) / 5.0
    i = min(int(a), 17)
    t = a - i
    p1, p2 = tbl[i], tbl[i + 1]
    p0 = tbl[i - 1] if i > 0 else p1 - (p2 - p1)
    p3 = tbl[i + 2] if i + 2 < len(tbl) else p2 + (p2 - p1)
    return (((-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3
             + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t ** 2
             + (-p0 + p2) * t) * 0.5 + p1)


def raw(lat, lon):
    """(x, y) in projection units, equator at y=0, y growing downward."""
    x = _KX * _spline(_X, lat) * (lon * 3.141592653589793 / 180.0)
    y = _KY * _spline(_Y, lat)
    return (x, -y if lat >= 0 else y)


# The box the frame is cut to: the full 180° of longitude at the equator,
# and the cropped band of latitude.
_X0 = raw(0.0, -180.0)[0]
_Y0 = raw(LAT_MAX, 0.0)[1]
_Y1 = raw(LAT_MIN, 0.0)[1]
_SCALE = VB_W / (2 * -_X0)
VB_H = round((_Y1 - _Y0) * _SCALE + 2 * PAD, 4)


def project(lat, lon):
    """(x, y) in viewBox units: 0..VB_W across, 0..VB_H down."""
    x, y = raw(lat, lon)
    return ((x - _X0) * _SCALE, (y - _Y0) * _SCALE + PAD)


def pct(lat, lon):
    """(x, y) as percentages of the field box, which is the same frame."""
    x, y = project(lat, lon)
    return (x / VB_W * 100.0, y / VB_H * 100.0)

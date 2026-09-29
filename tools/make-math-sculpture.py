#!/usr/bin/env python3
"""Draw the Math Challenge sculpture's still states as SVG.

The page's sculpture is 216 bevelled blocks rendered by
assets/js/math-sculpture.js. Before its first frame, and wherever WebGL,
scripting or motion is unavailable, the page shows these drawings instead.
They are projected with the same geometry, view and camera the script uses
for its opening state, so the rendered cube lands on the drawn one:

  assets/img/math-challenge/sculpture-cube.svg
      state A, the 6x6x6 cube, the page's opening
  assets/img/math-challenge/sculpture-torus.svg
      state C, the same blocks sampled around a torus, shown beside the
      statement when nothing moves (from assets/css/matharena.css)

Keep the constants here and in math-sculpture.js in step.

    python tools/make-math-sculpture.py
"""
import math
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "img", "math-challenge")

N = 6                   # the cube is N x N x N
COLS, ROWS = 18, 12     # the field and the torus are COLS x ROWS
BLOCK = 0.34            # block edge
PITCH = 0.40            # cube pitch: BLOCK plus a narrow gap
TORUS_R, TORUS_r = 2.0, 0.78
TORUS_U0 = -0.75 * math.pi
GOLD_COL = 9

# The opening view (Euler XYZ, as three.js composes it) and camera.
VIEW_A = (0.50, -0.70, 0.0)
VIEW_C = (1.02, 0.35, 0.0)
DIST = 12.0
RADIUS_A = 2.2          # world radius that fills half the drawing
RADIUS_C = 3.05
SIZE = 720

IVORY = (0.945, 0.922, 0.867)
STONE = (0.886, 0.851, 0.769)
GOLD = (0.80, 0.63, 0.26)
KEY = (-0.62, 0.66, 0.58)
FILL = (0.72, -0.08, 0.42)
CORE = (0.42, 0.39, 0.35)


def norm(v):
    length = math.sqrt(sum(c * c for c in v)) or 1.0
    return tuple(c / length for c in v)


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def mat_vec(m, v):
    return tuple(dot(row, v) for row in m)


def mat_mul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def euler_xyz(x, y, z):
    cx, sx, cy, sy, cz, sz = math.cos(x), math.sin(x), math.cos(y), math.sin(y), math.cos(z), math.sin(z)
    rx = [[1, 0, 0], [0, cx, -sx], [0, sx, cx]]
    ry = [[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]]
    rz = [[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]]
    return mat_mul(mat_mul(rx, ry), rz)


def hash01(i):
    s = math.sin(i * 12.9898 + 4.1414) * 43758.5453
    return s - math.floor(s)


KEY_N, FILL_N = norm(KEY), norm(FILL)


def blocks():
    """Every block: id, cube cell, field cell, torus basis."""
    out = []
    for y in range(N):
        for z in range(N):
            for x in range(N):
                i = x + N * z + N * N * y
                col = x + N * (y % 3)
                row = z + N * (y // 3)
                out.append({"id": i, "x": x, "y": y, "z": z, "col": col, "row": row,
                            "gold": col == GOLD_COL})
    return out


def cube_pose(b):
    c = tuple((k - (N - 1) / 2) * PITCH for k in (b["x"], b["y"], b["z"]))
    return c, [[1, 0, 0], [0, 1, 0], [0, 0, 1]], (1.0, 1.0, 1.0)


def torus_pose(b):
    u = b["col"] / COLS * 2 * math.pi + TORUS_U0
    v = b["row"] / ROWS * 2 * math.pi
    ring = TORUS_R + TORUS_r * math.cos(v)
    c = (ring * math.cos(u), TORUS_r * math.sin(v), ring * math.sin(u))
    ax = (-math.sin(u), 0.0, math.cos(u))
    ay = (math.cos(v) * math.cos(u), math.sin(v), math.cos(v) * math.sin(u))
    az = cross(ax, ay)
    basis = [[ax[0], ay[0], az[0]], [ax[1], ay[1], az[1]], [ax[2], ay[2], az[2]]]
    return c, basis, torus_scale(ring)


def torus_scale(ring):
    """Tiles widen with the circle they sit on, so the torus reads as one
    surface: (along the ring, along the normal, around the tube)."""
    return (min(1.9, ring * 2 * math.pi / COLS * 0.8 / BLOCK), 0.78, 0.94)


def depth_shade(b):
    """Blocks deeper in the cube sit in the shadow of the ones around them."""
    k = min(b["x"], N - 1 - b["x"], b["y"], N - 1 - b["y"], b["z"], N - 1 - b["z"])
    return (1.0, 0.72, 0.55)[min(k, 2)]


FACES = [((1, 0, 0), (0, 1, 0), (0, 0, 1)), ((-1, 0, 0), (0, 1, 0), (0, 0, -1)),
         ((0, 1, 0), (0, 0, 1), (1, 0, 0)), ((0, -1, 0), (0, 0, -1), (1, 0, 0)),
         ((0, 0, 1), (1, 0, 0), (0, 1, 0)), ((0, 0, -1), (-1, 0, 0), (0, 1, 0))]


def colour(b, shade):
    if b["gold"]:
        base = GOLD
    else:
        t = hash01(b["id"]) * 0.6
        base = tuple(a + (s - a) * t for a, s in zip(IVORY, STONE))
    return tuple(min(1.0, c * shade) for c in base)


def hexc(c):
    return "#" + "".join(f"{round(max(0, min(1, v)) * 255):02x}" for v in c)


def project(f, c):
    return (SIZE / 2 + f * c[0] / (DIST - c[2]), SIZE / 2 - f * c[1] / (DIST - c[2]))


def core(view, f):
    """The cube's own silhouette in shadow, seen through the gaps."""
    h = (N * PITCH - (PITCH - BLOCK)) / 2 - 0.02
    out = []
    for n, u, v in FACES:
        nw = mat_vec(view, n)
        if nw[2] <= 0:
            continue
        pts = [project(f, mat_vec(view, tuple(n[k] * h + (u[k] * su + v[k] * sv) * h for k in range(3))))
               for su, sv in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        out.append((-99, CORE, pts))
    return out


def draw(pose, view, radius, name, cull=None, deep=False):
    f = (SIZE / 2) * DIST / radius
    polys = []
    for b in blocks():
        if cull and not cull(b):
            continue
        centre, basis, scale = pose(b)
        h = tuple(BLOCK * s / 2 for s in scale)
        bevel = BLOCK * 0.5 * 0.2
        for n, u, v in FACES:
            nw = mat_vec(view, mat_vec(basis, n))
            corners = []
            for su, sv in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
                # A bevelled face: its flat part is inset by the chamfer.
                local = tuple(n[k] * h[k] + (u[k] * su + v[k] * sv) * (h[k] - bevel) for k in range(3))
                world = mat_vec(view, tuple(centre[k] + mat_vec(basis, local)[k] for k in range(3)))
                corners.append(world)
            mid = tuple(sum(c[k] for c in corners) / 4 for k in range(3))
            to_eye = norm((-mid[0], -mid[1], DIST - mid[2]))
            if dot(nw, to_eye) <= 0.02:
                continue
            light = 0.58 + 0.46 * max(0.0, dot(nw, KEY_N)) + 0.10 * max(0.0, dot(nw, FILL_N))
            light *= 0.94 + 0.06 * max(0.0, nw[1])
            if deep:
                light *= depth_shade(b)
            pts = [project(f, c) for c in corners]
            polys.append((mid[2], colour(b, light), pts))
    polys.sort(key=lambda p: p[0])
    if deep:
        polys = core(view, f) + polys
    body = []
    for _, c, pts in polys:
        d = "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + "Z"
        body.append(f'<path fill="{hexc(c)}" d="{d}"/>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SIZE} {SIZE}" '
           f'width="{SIZE}" height="{SIZE}">'
           # A chamfer reads as a lighter edge: stroke each face in its own
           # colour, lifted, so neighbouring faces meet on a highlight.
           f'<g stroke="#fffdf6" stroke-opacity=".32" stroke-width=".9" stroke-linejoin="round">'
           + "".join(body) + "</g></svg>\n")
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, name), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(svg)
    print(f"{name}: {len(polys)} faces, {len(svg) // 1024} KB")


def shell(b):
    return min(b["x"], N - 1 - b["x"], b["y"], N - 1 - b["y"], b["z"], N - 1 - b["z"]) < 2


if __name__ == "__main__":
    draw(cube_pose, euler_xyz(*VIEW_A), RADIUS_A, "sculpture-cube.svg", cull=shell, deep=True)
    draw(torus_pose, euler_xyz(*VIEW_C), RADIUS_C, "sculpture-torus.svg")

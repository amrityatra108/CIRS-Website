/* ============================================================
   Arts, Music & Theatre — the wall
   ------------------------------------------------------------
   An endless, explorable field of the school's photographs of
   its arts, music and theatre. Drag, swipe, scroll or use the
   arrow keys to move through it; open a photograph to see it
   whole.

   Written for the archive the designer delivered as a standalone
   folder, and kept as it was. What changed for the site: the
   photographs are read from the page's own <template> rather than
   fetched as a second JSON copy that had to be kept in step, the
   palette numbers in the canvas are the site's gold, and the fold
   publishes its presence as --fold so the eyebrow can follow the
   title.

   It runs alone. GSAP, Lenis and ScrollTrigger drive the pages
   that scroll; this one does not scroll.
   ============================================================ */

(() => {
    'use strict';

    // ------------------------------------------------------------ CONFIGURATION
// The photographs come from the page itself: tools/build-site.py writes them
// into a <template> from the list in tools/artswall.py, as a link to the
// photograph wrapped around an image of its tile copy. One list, kept in the
// HTML, which is also what lets tools/check-links.py see every file the wall
// uses. A <template> is inert, so naming them there costs no requests.
const plates = [...document.getElementById('wall-plates').content.querySelectorAll('a')]
    .map(a => ({
        src: a.getAttribute('href'),
        thumb: a.firstElementChild.getAttribute('src'),
        cat: a.firstElementChild.dataset.cat || 'Arts',
        title: a.firstElementChild.getAttribute('alt') || ''
    }));

    const $ = id => document.getElementById(id);
    const wrap = $('p1-wrap'), stage = $('p1-stage'), ring = $('cursor-ring'), dot = $('cursor-dot');
    const titleSharp = $('p1-title'), titleSoft = $('p1-title-soft'), hintEl = $('p1-hint');
    const hero = document.querySelector('.p1-hero');
    const modal = $('master-modal'), mediaCont = $('m-media-cont'), mTitle = $('m-title'), mMeta = $('m-meta'), closeBtn = $('m-close');

    const PERSP = 1120;                       // must match #p1-viewport perspective
    const REDUCED = matchMedia('(prefers-reduced-motion: reduce)').matches;
    const clamp = (lo, hi, v) => v < lo ? lo : v > hi ? hi : v;
    // Frame-rate independent easing: the same feel at 60, 90 or 120 Hz.
    const easeK = (rate, dt) => 1 - Math.pow(1 - rate, dt / 16.667);

    let W = innerWidth, H = innerHeight;
    let modalActive = false, modalOpenedAt = 0, lastFocus = null;
    let touchMode = matchMedia('(hover: none), (pointer: coarse)').matches;
    const mouse = { x: W / 2, y: H / 2 };
    const lerpCursor = { x: W / 2, y: H / 2 };

    function setTouchMode(on) {
        touchMode = on;
        document.body.classList.toggle('is-touch', on);
        hintEl.textContent = on ? 'Swipe around the cylinder // Tap to open' : 'Drag around the cylinder // Scroll // Click to open';
        closeBtn.textContent = on ? '[ CLOSE ]' : '[ ESC // CLOSE ]';
    }
    setTouchMode(touchMode);
    // No custom cursor, tilt or focus until the mouse actually moves in. Before that the
    // page doesn't know where the pointer is, and assuming a corner tilts the whole field.
    if (!touchMode) document.body.classList.add('is-away');

    window.addEventListener('pointermove', e => {
        if (e.pointerType !== 'mouse') return;
        if (touchMode) setTouchMode(false);
        document.body.classList.remove('is-away');
        mouse.x = e.clientX; mouse.y = e.clientY;
        dot.style.transform = `translate3d(${e.clientX}px,${e.clientY}px,0)`;
    }, { passive: true });
    // Hide the custom cursor when the mouse leaves the window instead of freezing it at the edge.
    document.documentElement.addEventListener('mouseleave', () => document.body.classList.add('is-away'));

    // ------------------------------------------------------------------ PLEXUS
    // Particle count scales with screen area, distance tests skip the square root,
    // and lines are grouped into four strength bands so the canvas strokes four
    // paths a frame instead of hundreds. The canvas is sized for the display's
    // pixel density so the lines stay crisp on phones and high-DPI screens.
    const plexus = {
        ctx: null, pts: [], bands: [[], [], [], []], dpr: 1,
        init() { this.ctx = $('global-canvas').getContext('2d'); this.resize(); },
        resize() {
            const c = $('global-canvas');
            this.dpr = Math.min(2, window.devicePixelRatio || 1);
            c.width = Math.round(W * this.dpr); c.height = Math.round(H * this.dpr);
            this.ctx.setTransform(this.dpr, 0, 0, this.dpr, 0, 0);
            const n = Math.round(clamp(36, 120, (W * H) / 11000));
            while (this.pts.length > n) this.pts.pop();
            for (const p of this.pts) { p.x = clamp(0, W, p.x); p.y = clamp(0, H, p.y); }
            while (this.pts.length < n) this.pts.push({ x: Math.random() * W, y: Math.random() * H, vx: (Math.random() - .5) * .5, vy: (Math.random() - .5) * .5, s: Math.random() * 1.5 + .5 });
        },
        draw(dt) {
            const ctx = this.ctx, pts = this.pts, n = pts.length, f = dt / 16.667, bands = this.bands;
            ctx.clearRect(0, 0, W, H);
            const repel = !touchMode && !document.body.classList.contains('is-away');
            for (const p of pts) {
                p.x += p.vx * f; p.y += p.vy * f;
                if (repel) {
                    const dx = mouse.x - p.x, dy = mouse.y - p.y, d2 = dx * dx + dy * dy;
                    if (d2 < 22500 && d2 > 0.01) { const d = Math.sqrt(d2), force = (150 - d) / 150; p.x -= dx / d * force * 5 * f; p.y -= dy / d * force * 5 * f; }
                }
                if (p.x < 0 || p.x > W) { p.vx *= -1; p.x = clamp(0, W, p.x); }
                if (p.y < 0 || p.y > H) { p.vy *= -1; p.y = clamp(0, H, p.y); }
            }
            for (const b of bands) b.length = 0;
            for (let i = 0; i < n; i++) {
                const a = pts[i];
                for (let j = i + 1; j < n; j++) {
                    const b = pts[j], dx = a.x - b.x, dy = a.y - b.y, d2 = dx * dx + dy * dy;
                    if (d2 < 14400) { const t = 1 - Math.sqrt(d2) / 120; bands[Math.min(3, (t * 4) | 0)].push(a.x, a.y, b.x, b.y); }
                }
            }
            ctx.lineWidth = 0.5;
            for (let k = 0; k < 4; k++) {
                const s = bands[k]; if (!s.length) continue;
                ctx.strokeStyle = `rgba(255,195,8,${(0.22 * (k + 0.5) / 4).toFixed(3)})`;
                ctx.beginPath();
                for (let q = 0; q < s.length; q += 4) { ctx.moveTo(s[q], s[q + 1]); ctx.lineTo(s[q + 2], s[q + 3]); }
                ctx.stroke();
            }
            ctx.fillStyle = 'rgba(255,215,92,0.6)';
            ctx.beginPath();
            for (const p of pts) { ctx.moveTo(p.x + p.s, p.y); ctx.arc(p.x, p.y, p.s, 0, Math.PI * 2); }
            ctx.fill();
        }
    };

    // --------------------------------------------------------- THE INFINITE ARCHIVE
    //
    // An endless staggered grid of tiles. A fixed pool covers the screen plus a
    // margin for the tilt. Each slot owns one residue class of grid cells
    // (column mod cols, row mod rows), so when the view crosses a cell boundary
    // only the single row or column that scrolled off is re-pointed -- never the
    // whole pool at once.
    //
    // Nothing is read back from the DOM while animating. Tile screen positions,
    // including the 3D tilt and perspective, are projected here in JS, so a frame
    // is pure math followed by transform writes: no forced layout.
    const p1 = {
        slots: [], cols: 0, rows: 0, CELL: 200, MARGIN: 3, scale: 1,
        panX: 0, panY: 0, vx: 0, vy: 0, wheelX: 0, wheelY: 0, lastWheelAt: 0,
        prevPanX: 0, prevPanY: 0, svx: 0, svy: 0,
        rot: { x: 0, y: 0 }, wrx: NaN, wry: NaN,
        titleFade: 1, tSharp: -1, tSoft: -1, tFold: -1,
        ringS: { x: W / 2, y: H / 2, s: 40 }, ringW: NaN, snapped: false,

        hash(q, r) {
            let h = (q * 374761393) + (r * 668265263);
            h = (h ^ (h >> 13)) * 1274126177;
            return (h ^ (h >> 16)) >>> 0;
        },
        unit(q, r, salt) { return (this.hash(q + salt * 131, r - salt * 71) % 10000) / 9999; },

        // (gx + 2gy) mod 5 differs across all eight neighbours, so no photograph
        // ever sits beside itself.
        plateFor(gx, gy) {
            const N = plates.length;
            if (N < 6) return this.hash(gx, gy) % N;
            const cls = (((gx + 2 * gy) % 5) + 5) % 5;
            const count = Math.floor((N - 1 - cls) / 5) + 1;
            return cls + (this.hash(gx + 7919, gy + 104729) % count) * 5;
        },

        // Sizes keep the original rings' range (180/140/100/80) and small bias;
        // everything scales down together on small screens.
        cellFor(gx, gy) {
            const C = this.CELL, s = this.scale;
            // Keep only a light amount of per-tile depth variation. The cylinder
            // supplies the dominant Z-shape, so its centre always reads closer
            // than either shoulder instead of being contradicted by random tiles.
            const depth = this.hash(gx - 313, gy + 197) % 3;
            const depths = [-60, 0, 60];
            return {
                plate: this.plateFor(gx, gy),
                size: Math.round((78 + 104 * Math.pow(this.unit(gx, gy, 1), 1.8)) * s),
                wx: gx * C + ((gy & 1) ? C / 2 : 0) + (this.unit(gx, gy, 2) - 0.5) * C * 0.36,
                wy: gy * C * 0.9 + (this.unit(gx, gy, 3) - 0.5) * C * 0.30,
                z: depths[depth] * Math.max(0.72, s),
                depth,
                tilt: (this.unit(gx, gy, 5) - 0.5) * 5
            };
        },

        // Rows are sized with 160px of headroom so a phone's address bar sliding in
        // and out never changes the grid and forces a rebuild (which would flash
        // every image).
        metrics() {
            // A page can start at zero size (a hidden or lazily loaded iframe); size the
            // grid for a sensible minimum and let the size watcher rebuild once it's real.
            const w = Math.max(W, 320), h = Math.max(H, 320);
            // Stepped in 5% increments so dragging a window edge doesn't change the tile size every pixel.
            const s = Math.round(clamp(0.62, 1, Math.min(w, h) / 760) * 20) / 20;
            const C = Math.round(200 * s);
            const M = Math.min(w, h) < 700 ? 2 : 3;
            return { s, C, M, cols: Math.ceil(w / C) + M * 2, rows: Math.ceil((h + 160) / (C * 0.9)) + M * 2 };
        },

        build() {
            const m = this.metrics();
            Object.assign(this, { scale: m.s, CELL: m.C, MARGIN: m.M, cols: m.cols, rows: m.rows });
            stage.textContent = ''; this.slots = [];
            const frag = document.createDocumentFragment();
            for (let j = 0; j < this.rows; j++) {
                for (let i = 0; i < this.cols; i++) {
                    const el = document.createElement('button'); el.type = 'button'; el.className = 'p1-tile';
                    const img = document.createElement('img'); img.alt = ''; img.decoding = 'async'; img.draggable = false;
                    el.appendChild(img); frag.appendChild(el);
                    const slot = { el, img, i, j, gx: NaN, gy: NaN, plate: -1, size: 0, wx: 0, wy: 0, baseZ: 0, depth: -1, tilt: 0, lift: 0, hovered: false, hidden: false, tx: NaN, ty: NaN, tz: NaN };
                    // If a thumbnail is missing, fall back to the full photograph once.
                    img.onerror = () => {
                        const p = plates[slot.plate];
                        if (p && p.thumb && img.getAttribute('src') !== p.src) img.src = p.src;
                    };
                    el.__slot = slot;
                    el.addEventListener('click', e => {
                        // Pointer taps are handled by endDrag, so dragging never opens a tile.
                        if (e.detail === 0) openModal(slot.plate, el);
                    });
                    el.addEventListener('focus', () => {
                        if (!el.matches(':focus-visible') || modalActive) return;
                        this.vx = this.vy = this.wheelX = this.wheelY = 0;
                        this.panX = W / 2 - slot.wx; this.panY = H / 2 - slot.wy;
                        this.frame(16.7, performance.now());
                    });
                    this.slots.push(slot);
                }
            }
            stage.appendChild(frag);
        },

        // Grow-only: rebuild when the tile size changes or the pool is too small. A
        // slightly larger pool just leaves a few tiles off screen, so a phone's address
        // bar sliding in and out never tears down and reloads the grid.
        needsRebuild() {
            const m = this.metrics();
            if (m.C !== this.CELL || m.M !== this.MARGIN) return true;
            if (m.cols > this.cols || m.rows > this.rows) return true;
            return m.cols * m.rows < 0.6 * this.cols * this.rows;
        },

        recycle() {
            const C = this.CELL, rowH = C * 0.9, M = this.MARGIN, cols = this.cols, rows = this.rows;
            const sgx = Math.floor(-this.panX / C) - M, sgy = Math.floor(-this.panY / rowH) - M;
            for (const s of this.slots) {
                // Never change the photograph represented by the focused control.
                if (s.el === document.activeElement) continue;
                const gx = sgx + (((s.i - sgx) % cols) + cols) % cols;
                const gy = sgy + (((s.j - sgy) % rows) + rows) % rows;
                if (gx === s.gx && gy === s.gy) continue;
                const c = this.cellFor(gx, gy);
                s.gx = gx; s.gy = gy; s.wx = c.wx; s.wy = c.wy; s.baseZ = c.z; s.tilt = c.tilt; s.lift = 0;
                if (c.depth !== s.depth) {
                    s.depth = c.depth;
                    s.el.classList.remove('depth-back', 'depth-main', 'depth-front');
                    s.el.classList.add(['depth-back', 'depth-main', 'depth-front'][c.depth]);
                }
                if (c.size !== s.size) { s.size = c.size; s.el.style.width = s.el.style.height = c.size + 'px'; }
                if (c.plate !== s.plate) { s.plate = c.plate; const p = plates[c.plate]; s.img.src = p.thumb || p.src; s.el.setAttribute('aria-label', p.title + ' — ' + p.cat); }
            }
        },

        frame(dt, now) {
            const f = dt / 16.667;

            // Wheel / trackpad / arrow keys: eased toward the target so each step glides.
            if (this.wheelX || this.wheelY) {
                const k = easeK(0.28, dt), dx = this.wheelX * k, dy = this.wheelY * k;
                this.panX += dx; this.panY += dy; this.wheelX -= dx; this.wheelY -= dy;
                if (Math.abs(this.wheelX) < 0.3) { this.panX += this.wheelX; this.wheelX = 0; }
                if (Math.abs(this.wheelY) < 0.3) { this.panY += this.wheelY; this.wheelY = 0; }
            }
            // Fling.
            if (!drag.active && (this.vx || this.vy)) {
                this.panX += this.vx * f; this.panY += this.vy * f;
                const fr = Math.pow(0.95, f); this.vx *= fr; this.vy *= fr;
                if (Math.hypot(this.vx, this.vy) < 0.05) this.vx = this.vy = 0;
            }

            // Smoothed on-screen speed, used for the touch lean and the title fade.
            const mvx = (this.panX - this.prevPanX) / f, mvy = (this.panY - this.prevPanY) / f;
            this.prevPanX = this.panX; this.prevPanY = this.panY;
            const sk = easeK(0.25, dt); this.svx += (mvx - this.svx) * sk; this.svy += (mvy - this.svy) * sk;

            this.recycle();

            // A restrained whole-camera lean complements the cylindrical surface.
            // The cylinder supplies the dominant depth cue; the camera never spins.
            const away = document.body.classList.contains('is-away');
            let tRY, tRX;
            if (REDUCED || (!touchMode && away)) { tRY = tRX = 0; }
            else if (touchMode) { tRY = clamp(-6, 6, this.svx * 0.42); tRX = clamp(-6, 6, -this.svy * 0.42); }
            else { tRY = clamp(-8, 8, (mouse.x - W / 2) / (W / 2) * 8); tRX = clamp(-6, 6, -(mouse.y - H / 2) / (H / 2) * 6); }
            const rk = easeK(0.08, dt);
            this.rot.x += (tRY - this.rot.x) * rk; this.rot.y += (tRX - this.rot.y) * rk;
            if (!(Math.abs(this.rot.x - this.wrx) <= 0.005 && Math.abs(this.rot.y - this.wry) <= 0.005)) {
                this.wrx = this.rot.x; this.wry = this.rot.y;
                stage.style.transform = `rotateY(${this.wrx.toFixed(3)}deg) rotateX(${this.wry.toFixed(3)}deg)`;
            }
            const aY = this.wrx * Math.PI / 180, aX = this.wry * Math.PI / 180;
            const cY = Math.cos(aY), sY = Math.sin(aY), cX = Math.cos(aX), sX = Math.sin(aX);

            const cx = W / 2, cy = H / 2;
            const focusX = touchMode || away ? cx : mouse.x, focusY = touchMode || away ? cy : mouse.y;
            const R = touchMode ? 260 * this.scale + 40 : 400;
            const snapR = (drag.active && !touchMode) || away ? 0 : (touchMode ? 150 : 120);
            const lk = easeK(0.12, dt), liftMax = touchMode ? 72 : 105;
            let closest = null, minD = snapR, cK = 1, cSX = 0, cSY = 0;

            const cylinderRadius = Math.max(380, W * 0.72);
            const cylinderLimit = cylinderRadius * 1.16;
            for (const s of this.slots) {
                const flatX = s.wx + this.panX, y = s.wy + this.panY;
                const offsetX = flatX - cx;
                const curve = clamp(-1.16, 1.16, offsetX / cylinderRadius);
                const x = cx + Math.sin(curve) * cylinderRadius;
                // Positive CSS Z moves toward the reader. Put the crown well in
                // front of the screen plane and both shoulders behind it so the
                // field unmistakably reads as the outside of a convex cylinder.
                const cylinderZ = (Math.cos(curve) - 0.70) * cylinderRadius;
                let z = s.baseZ + s.lift + cylinderZ;
                // CSS: rotateY(ry) rotateX(rx) => p' = RY(RX(p)), then perspective about the centre.
                const px = x - cx, py = y - cy;
                const y1 = py * cX - z * sX, z1 = py * sX + z * cX;
                const x2 = px * cY + z1 * sY, z2 = -px * sY + z1 * cY;
                const k = PERSP / Math.max(1, PERSP - z2), sx = cx + x2 * k, sy = cy + y1 * k, half = s.size * 0.5 * k;

                const off = Math.abs(offsetX) > cylinderLimit || sx + half < -60 || sx - half > W + 60 || sy + half < -60 || sy - half > H + 60;
                if (off !== s.hidden) { s.hidden = off; s.el.style.visibility = off ? 'hidden' : ''; }
                if (off) { if (s.hovered) { s.hovered = false; s.el.classList.remove('is-hovered'); } s.lift = 0; continue; }

                const d = Math.hypot(focusX - sx, focusY - sy);
                const near = d < R;
                s.lift += ((near ? (R - d) / R * liftMax : 0) - s.lift) * lk;
                if (near !== s.hovered) { s.hovered = near; s.el.classList.toggle('is-hovered', near); }
                if (d < minD) { minD = d; closest = s; cK = k; cSX = sx; cSY = sy; }

                z = s.baseZ + s.lift + cylinderZ;
                const tx = x - s.size / 2, ty = y - s.size / 2;
                // Written as "not within tolerance" so an unset (NaN) position always writes.
                if (!(Math.abs(tx - s.tx) <= 0.05 && Math.abs(ty - s.ty) <= 0.05 && Math.abs(z - s.tz) <= 0.05)) {
                    s.tx = tx; s.ty = ty; s.tz = z;
                    s.el.style.transform = `translate3d(${tx.toFixed(2)}px,${ty.toFixed(2)}px,${z.toFixed(2)}px) rotateY(${(curve * 180 / Math.PI).toFixed(2)}deg) rotateZ(${s.tilt.toFixed(2)}deg)`;
                }
            }

            // Cursor ring (mouse only): snaps around the nearest tile, else trails the cursor.
            if (!touchMode) {
                const target = closest ? { x: cSX, y: cSY, s: closest.size * cK + 15 } : { x: lerpCursor.x, y: lerpCursor.y, s: drag.active ? 30 : 40 };
                const k = easeK(0.25, dt), r = this.ringS;
                r.x += (target.x - r.x) * k; r.y += (target.y - r.y) * k; r.s += (target.s - r.s) * k;
                ring.style.transform = `translate3d(${(r.x - r.s / 2).toFixed(1)}px,${(r.y - r.s / 2).toFixed(1)}px,0)`;
                if (!(Math.abs(r.s - this.ringW) <= 0.3)) {
                    this.ringW = r.s;
                    ring.style.width = ring.style.height = r.s.toFixed(1) + 'px';
                    ring.style.borderRadius = closest ? '15px' : (r.s / 2).toFixed(1) + 'px';
                }
                if (!!closest !== this.snapped) { this.snapped = !!closest; ring.classList.toggle('is-snapped', this.snapped); if (!closest) ring.style.borderRadius = (r.s / 2).toFixed(1) + 'px'; }
            }

            // Title: revealed near the centre (as before), and faded out while the
            // field is moving so it never sits over the tiles you're trying to see.
            const busy = drag.active || Math.abs(this.svx) + Math.abs(this.svy) > 0.6 || now - this.lastWheelAt < 350;
            this.titleFade += ((busy ? 0 : 1) - this.titleFade) * easeK(busy ? 0.14 : 0.05, dt);
            const reveal = Math.max(0, 1 - Math.hypot(focusX - cx, focusY - cy) / 500);
            const total = (0.05 + reveal * 0.95) * this.titleFade;
            const oSharp = total * reveal, oSoft = total * (1 - reveal);
            if (Math.abs(oSharp - this.tSharp) > 0.004) { this.tSharp = oSharp; titleSharp.style.opacity = oSharp.toFixed(3); }
            if (Math.abs(oSoft - this.tSoft) > 0.004) { this.tSoft = oSoft; titleSoft.style.opacity = oSoft.toFixed(3); }
            // The eyebrow and the cue read at full strength or not at all, so they
            // follow the fold's overall presence rather than the focus-pull.
            if (Math.abs(total - this.tFold) > 0.004) { this.tFold = total; hero.style.setProperty('--fold', total.toFixed(3)); }
        }
    };

    // ------------------------------------------------------------------- DRAG
    // One pointer model for mouse, pen and touch. The pan follows the finger 1:1;
    // on release the fling speed comes from the last ~90 ms of movement (not the
    // last single event, which is noisy), and a finger that stopped before
    // lifting doesn't fling at all. Taps are detected here too, so a drag never
    // opens a tile and a tap always does.
    const drag = { active: false, id: null, startX: 0, startY: 0, startT: 0, lastX: 0, lastY: 0, moved: 0, samples: [] };

    wrap.addEventListener('pointerdown', e => {
        if (modalActive || drag.active) return;
        if (e.pointerType === 'mouse' && e.button !== 0) return;
        setTouchMode(e.pointerType !== 'mouse');
        Object.assign(drag, { active: true, id: e.pointerId, startX: e.clientX, startY: e.clientY, lastX: e.clientX, lastY: e.clientY, startT: e.timeStamp, moved: 0 });
        drag.samples.length = 0; drag.samples.push(e.clientX, e.clientY, e.timeStamp);
        p1.vx = p1.vy = 0; p1.wheelX = p1.wheelY = 0;
        try { wrap.setPointerCapture(e.pointerId); } catch (_) {}
    });

    wrap.addEventListener('pointermove', e => {
        if (!drag.active || e.pointerId !== drag.id) return;
        const x = e.clientX, y = e.clientY;
        p1.panX += x - drag.lastX; p1.panY += y - drag.lastY;
        drag.lastX = x; drag.lastY = y;
        drag.moved = Math.max(drag.moved, Math.hypot(x - drag.startX, y - drag.startY));
        const s = drag.samples; s.push(x, y, e.timeStamp);
        while (s.length > 9 && e.timeStamp - s[5] > 120) s.splice(0, 3);
    });

    function endDrag(e, cancelled) {
        if (!drag.active || e.pointerId !== drag.id) return;
        drag.active = false;
        try { wrap.releasePointerCapture(e.pointerId); } catch (_) {}

        const slop = e.pointerType === 'mouse' ? 6 : 10;
        if (!cancelled && drag.moved < slop && e.timeStamp - drag.startT < 450) {
            const hit = document.elementFromPoint(e.clientX, e.clientY);
            const tile = hit && hit.closest ? hit.closest('.p1-tile') : null;
            if (tile && tile.__slot && tile.__slot.plate >= 0) openModal(tile.__slot.plate, tile);
            return;
        }

        const s = drag.samples, n = s.length;
        let vx = 0, vy = 0;
        if (!cancelled && !REDUCED && n >= 6 && e.timeStamp - s[n - 1] < 60) {
            const tEnd = s[n - 1];
            let i = n - 3;
            while (i > 0 && tEnd - s[i - 1] <= 90) i -= 3;
            const span = tEnd - s[i + 2];
            if (span > 8) { vx = (s[n - 3] - s[i]) / span * 16.667; vy = (s[n - 2] - s[i + 1]) / span * 16.667; }
        }
        p1.vx = clamp(-60, 60, vx); p1.vy = clamp(-60, 60, vy);
    }
    wrap.addEventListener('pointerup', e => endDrag(e, false));
    wrap.addEventListener('pointercancel', e => endDrag(e, true));
    wrap.addEventListener('lostpointercapture', e => { if (drag.active && e.pointerId === drag.id) endDrag(e, true); });

    wrap.addEventListener('wheel', e => {
        if (modalActive) return;
        e.preventDefault();
        const k = e.deltaMode === 1 ? 32 : e.deltaMode === 2 ? H : 1;
        // Keep a wild trackpad burst from queueing up a long runaway glide.
        p1.wheelX = clamp(-1600, 1600, p1.wheelX - e.deltaX * k);
        p1.wheelY = clamp(-1600, 1600, p1.wheelY - e.deltaY * k);
        p1.lastWheelAt = performance.now(); p1.vx = p1.vy = 0;
    }, { passive: false });

    // iOS Safari ignores touch-action for pinch; stop the page zooming under the gallery.
    document.addEventListener('gesturestart', e => e.preventDefault());

    // ------------------------------------------------------------------ MODAL
    let modalToken = 0;
    function openModal(i, from) {
        const d = plates[i]; if (!d) return;
        modalActive = true; modalOpenedAt = performance.now();
        lastFocus = from || document.activeElement;
        drag.active = false; p1.vx = p1.vy = 0; p1.wheelX = p1.wheelY = 0;
        mTitle.textContent = d.title;
        mMeta.textContent = `${d.cat} \u00b7 Arts, Music & Theatre`;
        const full = d.src, thumb = d.thumb || d.src, token = ++modalToken;
        mediaCont.textContent = '';
        // Show the tile copy at once, swap in the photograph when it has loaded.
        const img = document.createElement('img'); img.alt = d.title; img.src = thumb; mediaCont.appendChild(img);
        img.onerror = () => { if (img.getAttribute('src') !== full) img.src = full; };
        if (full !== thumb) { const hi = new Image(); hi.decoding = 'async'; hi.onload = () => { if (token === modalToken) img.src = full; }; hi.src = full; }
        modal.style.display = 'flex'; modal.setAttribute('aria-hidden', 'false');
        modal.removeAttribute('inert');
        void modal.offsetWidth; modal.classList.add('is-open');
        try { closeBtn.focus({ preventScroll: true }); } catch (_) { closeBtn.focus(); }
        if (!touchMode) { ring.classList.remove('is-snapped'); p1.snapped = false; }
    }

    function closeModal() {
        if (!modalActive) return;
        modal.classList.remove('is-open');
        const token = ++modalToken;
        setTimeout(() => {
            if (token !== modalToken) return;
            modal.style.display = 'none'; modal.setAttribute('aria-hidden', 'true');
            modal.setAttribute('inert', '');
            mediaCont.textContent = ''; modalActive = false; last = performance.now();
            const back = lastFocus && lastFocus !== document.body && document.contains(lastFocus) ? lastFocus : wrap;
            try { back.focus({ preventScroll: true }); } catch (_) {}
        }, REDUCED ? 0 : 460);
    }

    closeBtn.addEventListener('click', closeModal);
    // Tap outside the photo to close -- ignoring the click that the opening tap itself produces.
    modal.addEventListener('click', e => {
        if (performance.now() - modalOpenedAt < 400) return;
        if (e.target === modal || e.target === mediaCont) closeModal();
    });

    window.addEventListener('keydown', e => {
        if (modalActive) {
            if (e.key === 'Escape') { e.preventDefault(); closeModal(); }
            // The close button is the dialog's only control: keep focus inside the dialog.
            else if (e.key === 'Tab') { e.preventDefault(); closeBtn.focus(); }
            return;
        }
        if (document.body.classList.contains('menu-open')) return;
        // Keyboard fallback for exploring: arrows glide, Home returns to the start.
        const step = e.shiftKey ? 520 : 260;
        const keys = { ArrowLeft: [step, 0], ArrowRight: [-step, 0], ArrowUp: [0, step], ArrowDown: [0, -step] };
        if (keys[e.key]) {
            e.preventDefault();
            p1.vx = p1.vy = 0;
            p1.wheelX = clamp(-1600, 1600, p1.wheelX + keys[e.key][0]);
            p1.wheelY = clamp(-1600, 1600, p1.wheelY + keys[e.key][1]);
            p1.lastWheelAt = performance.now();
        } else if (e.key === 'Home') {
            e.preventDefault();
            p1.vx = p1.vy = 0; p1.wheelX = W / 2 - p1.panX; p1.wheelY = H / 2 - p1.panY; p1.lastWheelAt = performance.now();
        }
    });

    // ------------------------------------------------------------------- LOOP
    let last = performance.now(), lastFrameAt = 0;
    function tick(now) {
        const dt = clamp(1, 50, now - last); last = now;
        lastFrameAt = performance.now();
        // Catch size changes that arrive without a resize event (late iframe sizing, some mobile browsers).
        if (!resizeTimer && (innerWidth !== W || innerHeight !== H)) onResize();
        const ck = easeK(0.15, dt);
        lerpCursor.x += (mouse.x - lerpCursor.x) * ck; lerpCursor.y += (mouse.y - lerpCursor.y) * ck;
        if (!modalActive) {
            p1.frame(dt, now);
            plexus.draw(dt);
        } else if (!touchMode) {
            ring.style.transform = `translate3d(${(lerpCursor.x - 20).toFixed(1)}px,${(lerpCursor.y - 20).toFixed(1)}px,0)`;
            if (p1.ringW !== 40) { p1.ringW = 40; p1.ringS.s = 40; ring.style.width = ring.style.height = '40px'; ring.style.borderRadius = '20px'; }
        }
        requestAnimationFrame(tick);
    }
    // Coming back to a background tab should resume, not jump.
    document.addEventListener('visibilitychange', () => { if (!document.hidden) last = performance.now(); });

    // ----------------------------------------------------------------- RESIZE
    // Phones fire resize whenever the address bar slides; only rebuild the pool
    // when the grid actually needs different dimensions.
    let resizeTimer = 0;
    function onResize() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => {
            resizeTimer = 0;
            const cxOld = W / 2, cyOld = H / 2;
            W = innerWidth; H = innerHeight;
            if (touchMode || document.body.classList.contains('is-away')) {
                mouse.x = lerpCursor.x = p1.ringS.x = W / 2; mouse.y = lerpCursor.y = p1.ringS.y = H / 2;
            }
            // Keep the same spot of the archive centred through rotation or resizing.
            p1.panX += W / 2 - cxOld; p1.panY += H / 2 - cyOld; p1.prevPanX = p1.panX; p1.prevPanY = p1.panY;
            plexus.resize();
            if (p1.needsRebuild()) p1.build();
            for (const s of p1.slots) s.tx = NaN;
            p1.recycle();
            // Place the tiles now rather than waiting for the next animation frame, which
            // a frame that was hidden or zero-sized may not deliver straight away.
            if (!modalActive) { p1.frame(16.7, performance.now()); plexus.draw(16.7); }
        }, 150);
    }
    window.addEventListener('resize', onResize);
    window.addEventListener('orientationchange', onResize);
    // Also poll: a hidden or not-yet-rendered frame gets neither resize events nor animation frames.
    setInterval(() => {
        if (!resizeTimer && (innerWidth !== W || innerHeight !== H)) onResize();
        // Watchdog: if animation frames have stalled (some embedded contexts pause them), still
        // draw a frame so the gallery is never left unpainted. It never starts a second loop.
        const t = performance.now();
        if (!modalActive && !document.hidden && t - lastFrameAt > 900) { p1.frame(16.7, t); plexus.draw(16.7); }
    }, 500);

    // ------------------------------------------------------------------- BOOT
    // Decode every tile image up front, and keep hold of them so the browser keeps
    // them decoded -- recycling a tile then never stalls on a decode.
    const warm = [];
    function preload(list) {
        warm.length = 0;
        for (const p of list) {
            const im = new Image(); im.decoding = 'async'; im.src = p.thumb || p.src;
            if (im.decode) im.decode().catch(() => {});
            warm.push(im);
        }
    }

    plexus.init();
    p1.build();
    p1.panX = p1.prevPanX = W / 2; p1.panY = p1.prevPanY = H / 2;
    preload(plates);
    p1.recycle();
    requestAnimationFrame(t => { last = t; tick(t); });

    // Exposed only for testing in the console.
    window.__wall = { p1, plexus, drag, openModal, closeModal, get plates() { return plates; }, get modalActive() { return modalActive; } };
})();

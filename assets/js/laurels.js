/* ============================================================
   Our Laurels — motion and interaction.
   The page is complete without this file (see laurels.css). This
   adds, in order: the opening field of points that gathers into a
   wreath; the held category sequence; the counted figures; the
   sideways reel; the featured laurels' parallax; the archive's
   filters and reading dialog; the year timeline; the roll of names;
   and the closing laurel.

   One animation frame reads the scroll position for every scroll-
   linked piece, so nothing listens to scroll more than once. Lenis,
   when cirs.js runs it, moves the window, so window.scrollY is the
   truth either way.
   ============================================================ */
(function () {
  "use strict";

  var page = document.querySelector(".lr");
  if (!page) return;

  var body = document.body;
  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var wideMQ = window.matchMedia("(min-width: 900px) and (min-height: 560px)");
  var finePointer = window.matchMedia("(hover: hover) and (pointer: fine)").matches;
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var clamp = function (v, a, b) { return v < a ? a : v > b ? b : v; };
  var ease = function (t) { return t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; };
  var easeOut = function (t) { return 1 - Math.pow(1 - t, 3); };
  var lerp = function (a, b, t) { return a + (b - a) * t; };

  body.classList.add("lr-live");
  if (!reduced) body.classList.add("lr-scroll");

  var vw = window.innerWidth, vh = window.innerHeight;

  /* Section progress: 0 when its top meets the window's top, 1 when its
     bottom meets the window's bottom. */
  function held(el) {
    var r = el.getBoundingClientRect();
    var run = r.height - vh;
    return run > 0 ? clamp(-r.top / run, 0, 1) : (r.top < 0 ? 1 : 0);
  }

  /* Smooth scroll through the site's own engine when it is running. */
  function scrollToY(y, instant) {
    var ev = new CustomEvent("cirs-section-scroll", { cancelable: true,
      detail: { top: y, duration: instant ? 0.01 : 1.1 } });
    if (window.dispatchEvent(ev)) window.scrollTo({ top: y, behavior: instant || reduced ? "auto" : "smooth" });
  }

  /* Once-only entrance: adds .is-seen when an element first shows. */
  var seenIO = "IntersectionObserver" in window ? new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (!e.isIntersecting) return;
      e.target.classList.add("is-seen");
      seenIO.unobserve(e.target);
      if (e.target.__onSeen) e.target.__onSeen();
    });
  }, { threshold: 0.18, rootMargin: "0px 0px -6% 0px" }) : null;
  function onSeen(el, fn) {
    if (fn) el.__onSeen = fn;
    if (seenIO && !reduced) seenIO.observe(el);
    else { el.classList.add("is-seen"); if (fn) fn(); }
  }

  /* ==========================================================
     The field: points that gather into a laurel wreath
     ========================================================== */
  function rng(seed) {
    return function () {
      seed |= 0; seed = seed + 0x6D2B79F5 | 0;
      var t = Math.imul(seed ^ seed >>> 15, 1 | seed);
      t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
      return ((t ^ t >>> 14) >>> 0) / 4294967296;
    };
  }

  /* Two branches rising from the foot of a circle and stopping short of
     its crown; paired leaves along each, shrinking towards the tip. Returns
     candidate points, the leaf tips, and (optionally) one leaf left out. */
  function wreath(cx, cy, R, leavesPerSide, perLeaf, omitLast) {
    var pts = [], tips = [], missing = null, leaves = [], stems = [];
    [1, -1].forEach(function (side) {
      var stem = [];
      for (var q = 0; q <= 36; q++) {
        var sa = Math.PI / 2 + side * (0.24 + (q / 36) * 2.4);
        stem.push([cx + R * Math.cos(sa), cy + R * Math.sin(sa)]);
      }
      stems.push(stem);
      for (var k = 0; k < leavesPerSide; k++) {
        var t = (k + 0.5) / leavesPerSide;
        var a = Math.PI / 2 + side * (0.24 + t * 2.4);
        var sx = cx + R * Math.cos(a), sy = cy + R * Math.sin(a);
        var tx = -Math.sin(a) * side, ty = Math.cos(a) * side;       // along the growth
        var nx = Math.cos(a), ny = Math.sin(a);                         // outward
        var len = R * 0.27 * (1 - 0.42 * t), wid = len * 0.34;
        // stem
        for (var s = 0; s < 3; s++) {
          var aa = a + side * (s / 3) * (2.4 / leavesPerSide);
          pts.push([cx + R * Math.cos(aa), cy + R * Math.sin(aa), 0]);
        }
        [1, -1].forEach(function (inout) {
          var ang = 0.72;
          var dx = tx * Math.cos(ang) + nx * inout * Math.sin(ang);
          var dy = ty * Math.cos(ang) + ny * inout * Math.sin(ang);
          var px = -dy, py = dx;
          var bx = sx + nx * inout * 2, by = sy + ny * inout * 2;
          var outline = [];
          for (var i = 0; i <= perLeaf; i++) {
            var u = i / perLeaf;
            var hw = wid * Math.pow(Math.sin(Math.PI * u), 0.85) * (1 - u * 0.25);
            outline.push([bx + dx * u * len + px * hw, by + dy * u * len + py * hw]);
            outline.push([bx + dx * u * len - px * hw, by + dy * u * len - py * hw]);
          }
          var tip = [bx + dx * len, by + dy * len];
          var poly = outline.filter(function (_, n) { return n % 2 === 0; })
            .concat(outline.filter(function (_, n) { return n % 2 === 1; }).reverse());
          if (omitLast && side === -1 && inout === 1 && k === leavesPerSide - 1) {
            missing = { outline: outline, tip: tip, base: [bx, by] };
            return;
          }
          leaves.push(poly);
          outline.forEach(function (p) { pts.push([p[0], p[1], 1]); });
          for (var m = 1; m < 4; m++) pts.push([bx + dx * len * m / 4, by + dy * len * m / 4, 1]);
          tips.push(tip);
        });
      }
    });
    return { pts: pts, tips: tips, missing: missing, leaves: leaves, stems: stems };
  }

  function Field(canvas, mode) {
    this.c = canvas;
    this.x = canvas.getContext("2d");
    this.mode = mode;
    this.p = 0;
    this.px = -9999; this.py = -9999; this.pointerOn = false;
    this.data = [];
    if (mode === "hero") {
      try { this.data = JSON.parse(($("#lr-points") || {}).textContent || "[]"); } catch (e) { this.data = []; }
    }
    this.build();
  }
  Field.prototype.build = function () {
    var c = this.c, w = c.clientWidth || vw, h = c.clientHeight || vh;
    var dpr = Math.min(2, window.devicePixelRatio || 1);
    this.w = w; this.h = h; this.dpr = dpr;
    c.width = Math.round(w * dpr); c.height = Math.round(h * dpr);
    this.x.setTransform(dpr, 0, 0, dpr, 0, 0);
    var small = w < 700;
    var hero = this.mode === "hero";
    var n = hero ? (small ? 260 : 620) : (small ? 190 : 380);
    var cx = w / 2, cy = hero ? h / 2 : h * (small ? 0.3 : 0.27);
    var R = hero ? Math.min(w, h) * (small ? 0.36 : 0.33) : Math.min(w, h) * (small ? 0.17 : 0.125);
    var W = wreath(cx, cy, R, small ? 10 : 13, small ? 5 : 8, !hero);
    this.cx = cx; this.cy = cy; this.R = R; this.missing = W.missing;
    this.leaves = W.leaves; this.stems = W.stems;
    var r = rng(hero ? 1996 : 2026);

    // Targets: every candidate point, thinned or repeated to n.
    var cand = W.pts, targets = [];
    for (var i = 0; i < n; i++) {
      var q = cand[Math.floor(i * cand.length / n) % cand.length];
      targets.push([q[0] + (r() - .5) * 1.2, q[1] + (r() - .5) * 1.2]);
    }
    // Homes: a loose field, denser away from the centre of the lettering.
    var homes = [];
    for (i = 0; i < n; i++) {
      var hx = r() * w, hy = r() * h;
      if (!hero) { hx = cx + (r() - .5) * w * 1.1; hy = h * (0.55 + r() * 0.6); }
      homes.push([hx, hy]);
    }
    // Pair homes to targets by angle round the centre, so the gathering
    // sweeps rather than criss-crosses.
    var byAng = function (arr) {
      return arr.map(function (p, j) { return { j: j, a: Math.atan2(p[1] - cy, p[0] - cx) }; })
                .sort(function (a, b) { return a.a - b.a; }).map(function (o) { return o.j; });
    };
    var hs = byAng(homes), ts = byAng(targets);
    var P = this.P = [];
    for (i = 0; i < n; i++) {
      var hm = homes[hs[i]], tg = targets[ts[i]];
      P.push({ hx: hm[0], hy: hm[1], tx: tg[0], ty: tg[1],
        d: r(), s: 0.6 + r() * 1.1, k: r() < 0.16 ? 2 : 0, tw: r() * 6.28,
        fx: (r() - .5) * w * 0.3, fy: h * (0.22 + r() * 0.4), ox: 0, oy: 0 });
    }
    // The laurels themselves: one brighter point each, gathering to a leaf tip.
    var tips = W.tips;
    for (i = 0; i < this.data.length; i++) {
      var tip = tips[Math.floor(i * tips.length / this.data.length)];
      var hx2 = w * (0.08 + r() * 0.84), hy2 = h * (0.1 + r() * 0.8);
      // keep the brighter points out of the lettering's own band
      if (Math.abs(hy2 - h / 2) < h * 0.16) hy2 += (hy2 < h / 2 ? -1 : 1) * h * 0.18;
      P.push({ hx: hx2, hy: hy2, tx: tip[0], ty: tip[1], d: r() * .6, s: 2.3, k: 1, tw: r() * 6.28,
        fx: (r() - .5) * w * 0.24, fy: h * (0.3 + r() * 0.35), ox: 0, oy: 0, data: this.data[i] });
    }
  };
  Field.prototype.nearest = function (x, y) {
    var best = null, bd = 26 * 26;
    for (var i = 0; i < this.P.length; i++) {
      var q = this.P[i];
      if (q.k !== 1) continue;
      var dx = q.cx - x, dy = q.cy - y, dd = dx * dx + dy * dy;
      if (dd < bd) { bd = dd; best = q; }
    }
    return best;
  };
  Field.prototype.draw = function (time) {
    var x = this.x, w = this.w, h = this.h, p = this.p, hero = this.mode === "hero";
    var gather = hero ? p : p;
    var fall = hero ? clamp((p - 0.8) / 0.2, 0, 1) : 0;
    var toIvory = hero ? clamp((p - 0.94) / 0.06, 0, 1) : 0;

    // Ground: ink, a plum glow, and at the very end the ivory of what follows.
    x.globalAlpha = 1;
    x.fillStyle = "#1E1626"; x.fillRect(0, 0, w, h);
    var g = x.createRadialGradient(w / 2, h * (hero ? .42 : .45), 0, w / 2, h * .45, Math.max(w, h) * .7);
    g.addColorStop(0, "rgba(43,32,55,1)"); g.addColorStop(1, "rgba(43,32,55,0)");
    x.fillStyle = g; x.fillRect(0, 0, w, h);
    if (toIvory > 0) { x.globalAlpha = ease(toIvory); x.fillStyle = "#FAF9F3"; x.fillRect(0, 0, w, h); }

    var rot = hero ? (gather - 0.45) * 0.14 : 0;
    var cs = Math.cos(rot), sn = Math.sin(rot), cx = this.cx, cy = this.cy;
    var pointer = this.pointerOn && gather < 0.5;
    var t = time * 0.001;
    var dust = toIvory > 0.5 ? [57, 42, 72] : [250, 249, 243];
    var gold = toIvory > 0.5 ? [143, 110, 47] : [255, 215, 92];

    for (var i = 0; i < this.P.length; i++) {
      var q = this.P[i];
      var c = ease(clamp((gather - 0.04 - q.d * 0.16) / 0.36, 0, 1));
      var f = fall > 0 ? ease(clamp((fall - q.d * 0.3) / 0.7, 0, 1)) : 0;
      var dx = q.tx - cx, dy = q.ty - cy;
      var tx = cx + dx * cs - dy * sn, ty = cy + dx * sn + dy * cs;
      var drift = reduced ? 0 : (1 - c) * 2.2;
      var hx = q.hx + Math.sin(t * 0.35 + q.tw) * drift, hy = q.hy + Math.cos(t * 0.3 + q.tw) * drift;
      var px = lerp(hx, tx, c) + q.fx * f, py = lerp(hy, ty, c) + q.fy * f;

      // A light hand near the pointer: points lean away, then settle.
      var ox = 0, oy = 0;
      if (pointer) {
        var ex = px - this.px, ey = py - this.py, dd = ex * ex + ey * ey;
        if (dd < 16900) { var dist = Math.sqrt(dd) || 1, push = Math.pow(1 - dist / 130, 2) * 22 * (1 - c); ox = ex / dist * push; oy = ey / dist * push; }
      }
      q.ox += (ox - q.ox) * 0.09; q.oy += (oy - q.oy) * 0.09;
      px += q.ox; py += q.oy;
      q.cx = px; q.cy = py;

      var a;
      if (q.k === 1) a = 0.95 - f * 0.6;
      else a = (0.3 + q.s * 0.28) * (0.75 + 0.25 * Math.sin(t * 1.1 + q.tw) * (1 - c)) + c * 0.2;
      a *= 1 - f * 0.4;
      if (a <= 0.01) continue;
      var col = q.k === 0 ? dust : gold;
      x.globalAlpha = Math.min(1, a);
      x.fillStyle = "rgb(" + col[0] + "," + col[1] + "," + col[2] + ")";
      if (q.k === 1) {
        x.beginPath(); x.arc(px, py, q.s * (1 + c * 0.2), 0, 6.283); x.fill();
        x.globalAlpha = Math.min(1, a) * 0.16;
        x.beginPath(); x.arc(px, py, q.s * 3.6, 0, 6.283); x.fill();
      } else {
        var s = q.s * (1 + c * 0.25);
        x.fillRect(px - s / 2, py - s / 2, s, s);
      }
    }

    // As the points settle, fine lines ink the leaves and stems between them,
    // so the wreath resolves from dust into a drawn laurel.
    var ink = ease(clamp((gather - 0.5) / 0.16, 0, 1)) * (1 - clamp(fall * 1.8, 0, 1));
    if (ink > 0.01 && this.leaves) {
      x.save();
      x.translate(cx, cy); x.rotate(rot); x.translate(-cx, -cy);
      x.lineJoin = "round"; x.lineCap = "round";
      x.strokeStyle = "rgb(255,215,92)"; x.fillStyle = "rgb(255,215,92)";
      x.globalAlpha = ink * 0.34; x.lineWidth = 1.1;
      this.stems.forEach(function (st) {
        x.beginPath(); x.moveTo(st[0][0], st[0][1]);
        for (var m = 1; m < st.length; m++) x.lineTo(st[m][0], st[m][1]);
        x.stroke();
      });
      x.lineWidth = 0.8;
      this.leaves.forEach(function (lf) {
        x.beginPath(); x.moveTo(lf[0][0], lf[0][1]);
        for (var m = 1; m < lf.length; m++) x.lineTo(lf[m][0], lf[m][1]);
        x.closePath();
        x.globalAlpha = ink * 0.07; x.fill();
        x.globalAlpha = ink * 0.42; x.stroke();
      });
      x.restore();
    }

    // The closing laurel keeps one leaf unplaced: an outline, breathing.
    if (!hero && this.missing && p > 0.75) {
      var m = this.missing, show = clamp((p - 0.75) / 0.25, 0, 1);
      x.globalAlpha = show * (0.45 + (reduced ? 0.2 : 0.25 * Math.sin(t * 1.6)));
      x.strokeStyle = "#FFC308"; x.lineWidth = 1;
      x.setLineDash([2, 4]);
      x.beginPath();
      var o = m.outline, j;
      x.moveTo(o[0][0], o[0][1]);
      for (j = 2; j < o.length; j += 2) x.lineTo(o[j][0], o[j][1]);
      for (j = o.length - 1; j > 0; j -= 2) x.lineTo(o[j][0], o[j][1]);
      x.closePath(); x.stroke(); x.setLineDash([]);
    }
    x.globalAlpha = 1;
  };

  /* ==========================================================
     1. Opening
     ========================================================== */
  var hero = $("[data-lr-hero]");
  var heroField = null, heroVisible = true;
  var heroEls = hero ? {
    our: $(".lr-hero__word--our", hero), laurels: $(".lr-hero__word--laurels", hero),
    line: $(".lr-hero__line", hero), cue: $(".lr-hero__cue", hero),
    note: $(".lr-hero__wreath-note", hero), peek: $("[data-lr-peek]", hero)
  } : null;
  if (hero && $("canvas", hero).getContext) {
    heroField = new Field($("canvas", hero), "hero");
    if (finePointer && !reduced) {
      var stage = $(".lr-hero__stage", hero);
      stage.addEventListener("pointermove", function (e) {
        var r = stage.getBoundingClientRect();
        heroField.px = e.clientX - r.left; heroField.py = e.clientY - r.top; heroField.pointerOn = true;
        var near = heroField.p < 0.08 ? heroField.nearest(heroField.px, heroField.py) : null;
        var pk = heroEls.peek;
        if (near && near.data) {
          if (pk.__for !== near) {
            pk.__for = near;
            pk.innerHTML = "<span></span><b></b><span></span>";
            pk.children[0].textContent = near.data.y ? String(near.data.y) : "Year to be confirmed";
            pk.children[1].textContent = near.data.t;
            pk.children[2].textContent = near.data.c;
          }
          var left = clamp(near.cx + 14, 12, r.width - 272), top = clamp(near.cy - 20, 80, r.height - 120);
          pk.style.left = left + "px"; pk.style.top = top + "px";
          pk.classList.add("is-on");
        } else pk.classList.remove("is-on");
      });
      stage.addEventListener("pointerleave", function () { heroField.pointerOn = false; heroEls.peek.classList.remove("is-on"); });
    }
  }
  function heroFrame(time) {
    if (!hero) return;
    var p = reduced ? 0 : held(hero);
    if (heroField) { heroField.p = p; if (heroVisible) heroField.draw(time); }
    if (reduced) return;
    var e = heroEls;
    var a = ease(clamp(p / 0.34, 0, 1));
    e.our.style.opacity = 1 - clamp(p / 0.2, 0, 1);
    e.our.style.transform = "translate3d(0," + (-p * 140) + "px,0)";
    e.laurels.style.transform = "translate3d(0," + (-a * 8) + "vh,0) scale(" + (1 - a * 0.62) + ")";
    e.laurels.style.opacity = 1 - clamp((p - 0.22) / 0.14, 0, 1);
    e.line.style.opacity = e.cue.style.opacity = 1 - clamp(p / 0.08, 0, 1);
    e.note.style.opacity = clamp((p - 0.4) / 0.1, 0, 1) * (1 - clamp((p - 0.77) / 0.06, 0, 1));
    if (p > 0.08) e.peek.classList.remove("is-on");
  }
  if (hero && "IntersectionObserver" in window) {
    new IntersectionObserver(function (en) { heroVisible = en[0].isIntersecting; }).observe($(".lr-hero__stage", hero));
  }

  /* ==========================================================
     2. Excellence has many forms
     ========================================================== */
  var forms = $("[data-lr-forms]");
  var formItems = forms ? $$(".lr-form", forms) : [];
  var formCount = forms ? $("[data-lr-form-n]", forms) : null;
  var formIndex = -1;
  formItems.forEach(function (li) { onSeen(li); });
  function formsFrame() {
    if (!forms || !body.classList.contains("lr-cine")) return;
    var p = held(forms), n = formItems.length;
    var idx = Math.min(n - 1, Math.floor(p * n * 0.999));
    var local = p * n - idx;
    if (idx !== formIndex) {
      formIndex = idx;
      formItems.forEach(function (li, i) {
        li.classList.toggle("is-active", i === idx);
        li.classList.toggle("is-past", i < idx);
      });
      if (formCount) formCount.textContent = (idx < 9 ? "0" : "") + (idx + 1);
    }
    formItems[idx].style.setProperty("--lp", local.toFixed(3));
  }

  /* ==========================================================
     3. In figures: counted up once, from zero
     ========================================================== */
  $$(".lr-number__figure").forEach(function (fig) {
    var big = $(".lr-number__big", fig), target = parseFloat(fig.getAttribute("data-count"));
    var suffix = $(".lr-number__suffix", fig);
    fig.setAttribute("aria-label", fig.getAttribute("data-count") + (suffix ? suffix.textContent : ""));
    $$("span", fig).forEach(function (s) { s.setAttribute("aria-hidden", "true"); });
    if (reduced || isNaN(target)) return;
    big.textContent = "0";
    onSeen(fig.parentNode, function () {
      var t0 = null;
      (function tick(ts) {
        if (t0 === null) t0 = ts;
        var k = clamp((ts - t0) / 1400, 0, 1);
        big.textContent = String(Math.round(target * easeOut(k)));
        if (k < 1) requestAnimationFrame(tick);
      })(performance.now());
    });
  });

  /* ==========================================================
     4. The reel
     ========================================================== */
  var reel = $("[data-lr-reel]");
  var track = reel ? $("[data-lr-track]", reel) : null;
  var reelBar = reel ? $("[data-lr-reel-bar]", reel) : null;
  var reelHead = reel ? $(".lr-reel__head", reel) : null;
  var spreads = track ? $$(".lr-spread", track) : [];
  var reelDist = 0;
  function measureReel() {
    if (!reel) return;
    if (!body.classList.contains("lr-cine")) { reel.style.height = ""; track.style.transform = ""; if (reelHead) reelHead.style.removeProperty("--hp"); return; }
    reelDist = Math.max(0, track.scrollWidth - vw);
    reel.style.height = (reelDist + vh) + "px";
  }
  function reelFrame() {
    if (!reel || !body.classList.contains("lr-cine")) return;
    var p = held(reel), x = -p * reelDist;
    track.style.transform = "translate3d(" + x.toFixed(1) + "px,0,0)";
    if (reelBar) reelBar.parentNode.style.setProperty("--rp", p.toFixed(3));
    // The heading gives way before the first spread reaches it.
    if (reelHead) reelHead.style.setProperty("--hp", clamp(p / 0.07, 0, 1).toFixed(3));
    for (var i = 0; i < spreads.length; i++) {
      var s = spreads[i], sx = s.offsetLeft + x + s.offsetWidth / 2;
      if (sx < -vw || sx > vw * 2) continue;
      s.style.setProperty("--yp", ((sx - vw / 2) * -0.09).toFixed(1));
    }
  }
  if (track) {
    // A keyboard user tabbing into a spread that is off to the side is
    // carried to it: the reel's position is its vertical scroll.
    track.addEventListener("focusin", function (e) {
      if (!body.classList.contains("lr-cine") || !reelDist) return;
      var s = e.target.closest(".lr-spread");
      if (!s) return;
      var want = clamp((s.offsetLeft - vw * 0.42) / reelDist, 0, 1);
      var top = reel.getBoundingClientRect().top + window.scrollY;
      scrollToY(top + want * reelDist, true);
    });
  }

  /* ==========================================================
     5. Featured laurels
     ========================================================== */
  var features = $$(".lr-feature");
  features.forEach(function (f) { onSeen(f); });
  function featuresFrame() {
    if (reduced) return;
    for (var i = 0; i < features.length; i++) {
      var r = features[i].getBoundingClientRect();
      if (r.bottom < -50 || r.top > vh + 50) continue;
      var k = ((r.top + r.height / 2) - vh / 2) / (vh + r.height);
      features[i].style.setProperty("--py", clamp(k * -12, -6, 6).toFixed(2));
    }
  }

  /* ==========================================================
     6–7. The archive: filters and the reading dialog
     ========================================================== */
  var archive = $("[data-lr-archive]");
  var filters = archive ? $("[data-lr-filters]", archive) : null;
  var items = archive ? $$(".lr-item", archive) : [];
  var status = archive ? $("[data-lr-status]", archive) : null;
  var empty = archive ? $("[data-lr-empty]", archive) : null;
  var state = { cat: "all", level: "all", year: "all" };
  var catNames = {};
  if (filters) {
    filters.hidden = false;
    $$(".lr-cat", filters).forEach(function (b) { catNames[b.getAttribute("data-cat")] = $(".lr-cat__name", b).textContent; });
  }
  function matches(it, s) {
    return (s.cat === "all" || (" " + it.getAttribute("data-cats") + " ").indexOf(" " + s.cat + " ") > -1) &&
           (s.level === "all" || it.getAttribute("data-level") === s.level) &&
           (s.year === "all" || it.getAttribute("data-year") === s.year);
  }
  function applyFilters(animate) {
    if (!archive) return;
    var shown = 0, k = 0;
    items.forEach(function (it) {
      var ok = matches(it, state);
      var was = !it.hidden;
      it.hidden = !ok;
      it.classList.remove("is-entering");
      if (ok) {
        shown++;
        if (animate && !reduced && (!was || true)) {
          void it.offsetWidth;
          it.style.setProperty("--k", Math.min(k++, 10));
          it.classList.add("is-entering");
        }
      }
    });
    // Category counts under the other two choices; a category with none is set aside.
    $$(".lr-cat", filters).forEach(function (b) {
      var cat = b.getAttribute("data-cat");
      var s = { cat: cat, level: state.level, year: state.year };
      var n = items.filter(function (it) { return matches(it, s); }).length;
      $(".lr-cat__count", b).textContent = n;
      b.disabled = n === 0 && cat !== state.cat;
      b.setAttribute("aria-pressed", String(cat === state.cat));
    });
    $$(".lr-opt", filters).forEach(function (b) {
      var lv = b.getAttribute("data-level"), yr = b.getAttribute("data-year");
      b.setAttribute("aria-pressed", String(lv ? lv === state.level : yr === state.year));
    });
    var parts = [];
    if (state.cat !== "all") parts.push(catNames[state.cat]);
    if (state.level !== "all") parts.push($('.lr-opt[data-level="' + state.level + '"]', filters).textContent);
    if (state.year !== "all") parts.push(state.year === "undated" ? "undated" : state.year);
    status.textContent = "Showing " + shown + " of " + items.length + " laurels" + (parts.length ? ": " + parts.join(" · ") : "") + ".";
    empty.hidden = shown !== 0;
    if (grid) queuePack();
  }
  if (filters) {
    filters.addEventListener("click", function (e) {
      var b = e.target.closest("button");
      if (!b || b.disabled) return;
      if (b.hasAttribute("data-cat")) state.cat = b.getAttribute("data-cat");
      else if (b.hasAttribute("data-level")) state.level = b.getAttribute("data-level");
      else if (b.hasAttribute("data-year")) state.year = b.getAttribute("data-year");
      applyFilters(true);
    });
    var reset = $("[data-lr-reset]", archive);
    if (reset) reset.addEventListener("click", function () { state = { cat: "all", level: "all", year: "all" }; applyFilters(true); });
    applyFilters(false);
  }

  /* Masonry: each visible laurel spans as many 8px rows as it is tall. */
  var grid = archive ? $("[data-lr-grid]", archive) : null;
  var packQueued = false;
  function packGrid() {
    packQueued = false;
    if (!grid) return;
    items.forEach(function (it) {
      if (it.hidden) return;
      it.style.setProperty("--rs", Math.ceil(it.getBoundingClientRect().height / 8) + 1);
    });
  }
  function queuePack() {
    if (packQueued) return;
    packQueued = true;
    requestAnimationFrame(packGrid);
  }
  if (grid) {
    if ("ResizeObserver" in window) {
      var packRO = new ResizeObserver(queuePack);
      items.forEach(function (it) { packRO.observe($(".lr-card", it)); });
    }
    queuePack();
    window.addEventListener("load", queuePack);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(queuePack);
  }

  var dialog = $("#lr-dialog");
  var lastTrigger = null;
  function lockScroll(locked) {
    window.dispatchEvent(new CustomEvent("cirs-portal-scroll-lock", { detail: { locked: locked } }));
  }
  function openLaurel(btn) {
    if (!dialog || typeof dialog.showModal !== "function") return;
    var card = btn.closest(".lr-card");
    var media = $(".lr-card__media", card), more = $(".lr-card__more", card);
    var mediaSlot = $("[data-lr-dialog-media]", dialog);
    mediaSlot.innerHTML = "";
    if (media) {
      var m = media.cloneNode(true);
      var im = $("img", m); if (im) { im.removeAttribute("loading"); im.sizes = "(max-width: 679px) 92vw, 460px"; }
      mediaSlot.appendChild(m);
    }
    $(".lr-dialog__panel", dialog).classList.toggle("is-textonly", !media);
    $("[data-lr-dialog-meta]", dialog).innerHTML = $(".lr-card__meta", card).innerHTML;
    $("[data-lr-dialog-title]", dialog).textContent = btn.textContent;
    $("[data-lr-dialog-result]", dialog).innerHTML = $(".lr-card__result", card).innerHTML;
    var slot = $("[data-lr-dialog-more]", dialog);
    slot.innerHTML = "";
    if (more) slot.appendChild(more.cloneNode(true));
    lastTrigger = btn;
    dialog.showModal();
    dialog.scrollTop = 0;
    lockScroll(true);
    $("[data-lr-close-dialog]", dialog).focus();
  }
  if (dialog) {
    dialog.addEventListener("close", function () {
      lockScroll(false);
      if (lastTrigger) lastTrigger.focus({ preventScroll: true });
    });
    dialog.addEventListener("click", function (e) {
      if (e.target === dialog || e.target.closest("[data-lr-close-dialog]")) dialog.close();
    });
  }
  if (archive) {
    archive.addEventListener("click", function (e) {
      var b = e.target.closest(".lr-card__open");
      if (b) { openLaurel(b); return; }
      var card = e.target.closest(".lr-card");
      if (card && !e.target.closest("a")) openLaurel($(".lr-card__open", card));
    });
  }

  /* Links into the archive (from the timeline) clear any filter that
     would hide the laurel, then carry the reader to it. */
  function goToLaurel(id) {
    var it = document.getElementById("laurel-" + id);
    if (!it) return;
    if (it.hidden) { state = { cat: "all", level: "all", year: "all" }; applyFilters(false); }
    var top = it.getBoundingClientRect().top + window.scrollY - vh * 0.2;
    scrollToY(top);
    it.classList.remove("is-entering"); void it.offsetWidth; it.classList.add("is-entering");
    setTimeout(function () { var b = $(".lr-card__open", it); if (b) b.focus({ preventScroll: true }); }, reduced ? 0 : 900);
  }

  /* ==========================================================
     8. Year by year
     ========================================================== */
  var tl = $("[data-lr-timeline]");
  if (tl) {
    var yearBtns = $$(".lr-tl__year", tl);
    var panels = $$(".lr-tl__panel", tl);
    var trackEl = $(".lr-tl__track", tl);
    var committed = yearBtns.length ? yearBtns[yearBtns.length - 1].getAttribute("data-year") : null;
    var showYear = function (y, commit) {
      yearBtns.forEach(function (b) {
        var on = b.getAttribute("data-year") === y;
        b.setAttribute("aria-pressed", String(on && (commit || b.getAttribute("data-year") === committed)));
        if (on) {
          var x = parseFloat(b.parentNode.style.getPropertyValue("--x"));
          if (!isNaN(x)) trackEl.style.setProperty("--hx", x);
        }
      });
      panels.forEach(function (pn) { pn.classList.toggle("is-on", pn.getAttribute("data-year") === y); });
      if (commit) {
        committed = y;
        yearBtns.forEach(function (b) { b.setAttribute("aria-pressed", String(b.getAttribute("data-year") === y)); });
      }
    };
    if (committed) showYear(committed, true);
    tl.addEventListener("click", function (e) {
      var yb = e.target.closest(".lr-tl__year");
      if (yb) { showYear(yb.getAttribute("data-year"), true); return; }
      var show = e.target.closest("[data-show-year]");
      if (show) {
        state = { cat: "all", level: "all", year: show.getAttribute("data-show-year") };
        applyFilters(true);
        scrollToY(archive.getBoundingClientRect().top + window.scrollY + ($(".lr-archive__head", archive).offsetHeight || 0));
        return;
      }
      var link = e.target.closest("[data-laurel-link]");
      if (link) { e.preventDefault(); goToLaurel(link.getAttribute("data-laurel-link")); }
    });
    tl.addEventListener("keydown", function (e) {
      var yb = e.target.closest(".lr-tl__year");
      if (!yb || (e.key !== "ArrowRight" && e.key !== "ArrowLeft")) return;
      var i = yearBtns.indexOf(yb) + (e.key === "ArrowRight" ? 1 : -1);
      if (i < 0 || i >= yearBtns.length) return;
      e.preventDefault();
      yearBtns[i].focus();
      showYear(yearBtns[i].getAttribute("data-year"), true);
    });
    // On a wide window the rail can be dragged or hovered; the nearest
    // year with a laurel is shown, and a release or click keeps it.
    if (finePointer) {
      var nearestYear = function (clientX) {
        var best = null, bd = Infinity;
        yearBtns.forEach(function (b) {
          var r = b.parentNode.getBoundingClientRect(), d = Math.abs(r.left - clientX);
          if (d < bd) { bd = d; best = b; }
        });
        return best;
      };
      var dragging = false;
      trackEl.addEventListener("pointerdown", function (e) {
        if (!wideMQ.matches || e.target.closest(".lr-tl__year")) return;
        dragging = true; trackEl.classList.add("is-dragging");
        try { trackEl.setPointerCapture(e.pointerId); } catch (err) { /* older browsers */ }
        var b = nearestYear(e.clientX); if (b) showYear(b.getAttribute("data-year"), false);
      });
      trackEl.addEventListener("pointermove", function (e) {
        if (!wideMQ.matches) return;
        var b = nearestYear(e.clientX);
        if (b) showYear(b.getAttribute("data-year"), false);
      });
      var endDrag = function (e) {
        if (!dragging) return;
        dragging = false; trackEl.classList.remove("is-dragging");
        var b = nearestYear(e.clientX); if (b) showYear(b.getAttribute("data-year"), true);
      };
      trackEl.addEventListener("pointerup", endDrag);
      trackEl.addEventListener("pointercancel", endDrag);
      trackEl.addEventListener("pointerleave", function () { if (!dragging && committed) showYear(committed, true); });
    }
  }

  /* ==========================================================
     9. The roll of names
     ========================================================== */
  var namesSec = $("[data-lr-names]");
  if (namesSec) {
    var field = $("[data-lr-namefield]", namesSec);
    var reading = $("[data-lr-reading]", namesSec);
    var pinned = null;
    var light = function (li) {
      $$(".lr-name.is-on", field).forEach(function (x) { if (x !== li) x.classList.remove("is-on"); });
      if (!li) { field.classList.remove("is-dim"); reading.classList.remove("is-on"); return; }
      li.classList.add("is-on");
      field.classList.add("is-dim");
      reading.innerHTML = "<span><b></b></span>";
      $("b", reading).textContent = $(".lr-name__btn", li).textContent;
      $("span", reading).appendChild(document.createTextNode($(".lr-name__detail", li).textContent));
      reading.classList.add("is-on");
    };
    field.addEventListener("pointerover", function (e) {
      if (e.pointerType !== "mouse") return;
      var li = e.target.closest(".lr-name"); if (li && !pinned) light(li);
    });
    field.addEventListener("pointerleave", function () { if (!pinned) light(null); });
    field.addEventListener("focusin", function (e) { var li = e.target.closest(".lr-name"); if (li) light(li); });
    field.addEventListener("focusout", function (e) {
      if (!field.contains(e.relatedTarget)) { pinned = null; light(null); }
    });
    field.addEventListener("click", function (e) {
      var li = e.target.closest(".lr-name"); if (!li) return;
      if (pinned === li) { pinned = null; light(null); li.classList.remove("is-on"); }
      else { pinned = li; light(li); }
    });
    namesSec.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && field.classList.contains("is-dim")) { pinned = null; light(null); }
    });
  }
  function namesFrame() {
    if (!namesSec || reduced) return;
    var r = namesSec.getBoundingClientRect();
    if (r.bottom < 0 || r.top > vh) return;
    var k = clamp((vh - r.top) / (vh + r.height), 0, 1);
    namesSec.style.setProperty("--np", ((k - 0.5) * 2).toFixed(3));
  }

  /* The season in photographs: each event reveals once, as it arrives. */
  $$(".lr-event").forEach(function (ev) { onSeen(ev); });

  /* ==========================================================
     10. Closing
     ========================================================== */
  var closeSec = $("[data-lr-close]");
  var closeField = null, closeVisible = false;
  if (closeSec) {
    onSeen(closeSec);
    var cc = $("canvas", closeSec);
    if (cc.getContext) {
      closeField = new Field(cc, "close");
      if ("IntersectionObserver" in window) {
        new IntersectionObserver(function (en) { closeVisible = en[0].isIntersecting; }).observe(closeSec);
      } else closeVisible = true;
    }
  }
  function closeFrame(time) {
    if (!closeField || (!closeVisible && !reduced)) return;
    var r = closeSec.getBoundingClientRect();
    closeField.p = reduced ? 1 : clamp((vh - r.top) / (vh * 0.95), 0, 1);
    closeField.draw(time);
  }

  /* ==========================================================
     Layout, and the one frame loop
     ========================================================== */
  function setCine() {
    body.classList.toggle("lr-cine", !reduced && wideMQ.matches);
    formIndex = -1;
    if (!body.classList.contains("lr-cine")) formItems.forEach(function (li) { li.classList.remove("is-active", "is-past"); li.style.removeProperty("--lp"); });
    measureReel();
  }
  var resizeTimer = null, lastW = vw;
  window.addEventListener("resize", function () {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function () {
      vw = window.innerWidth; vh = window.innerHeight;
      // A phone's toolbar changes the height alone: keep the fields.
      if (Math.abs(vw - lastW) > 2 || !finePointer) {
        lastW = vw;
        if (heroField) heroField.build();
        if (closeField) closeField.build();
      }
      setCine();
      if (typeof queuePack === "function") queuePack();
      if (reduced) drawStill();
    }, 160);
  });
  if (wideMQ.addEventListener) wideMQ.addEventListener("change", setCine);
  setCine();
  // Fonts change the reel's width; measure again once they are in.
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(measureReel);
  window.addEventListener("load", measureReel);

  function drawStill() {
    var now = performance.now();
    if (heroField) { heroField.p = 0; heroField.draw(now); }
    if (closeField) { closeField.p = 1; closeField.draw(now); }
  }

  if (reduced) {
    drawStill();
    return;
  }

  function frame(time) {
    heroFrame(time);
    formsFrame();
    reelFrame();
    featuresFrame();
    namesFrame();
    closeFrame(time);
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
})();

/**
 * The CIRS Math Challenge — Interactive Arena
 * Includes:
 * 1. Hero Geometric Canvas: "The moment a pattern appears"
 * 2. Heron's Shortest Path Demonstration Puzzle
 * 3. Challenge Zones selection & archive anchor linking
 * 4. "How a Mind Solves" 5-stage interactive proof of invariants
 * 5. Complete verified monthly archive filtering and search
 */
(function () {
  "use strict";

  // Check reduced motion preference
  var prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ==========================================================================
     1. HERO CANVAS: "The moment a pattern appears"
     ========================================================================== */
  (function initHeroCanvas() {
    var canvas = document.getElementById("heroCanvas");
    if (!canvas) return;

    var ctx = canvas.getContext("2d");
    if (!ctx) return;

    var width = 0, height = 0, dpr = 1;
    var pointer = { x: 0, y: 0, px: 0, py: 0, active: false, movedDistance: 0 };
    var discoveryProgress = prefersReducedMotion ? 100 : 0;
    var discoveryStatus = document.getElementById("heroDiscoveryStatus");
    var discoveryText = document.getElementById("heroDiscoveryText");
    var skipBtn = document.getElementById("heroSkipBtn");

    var trails = [];
    var maxTrails = 120;
    var animFrameId = null;

    function resize() {
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      width = canvas.parentElement.offsetWidth || window.innerWidth;
      height = canvas.parentElement.offsetHeight || window.innerHeight;
      canvas.width = Math.floor(width * dpr);
      canvas.height = Math.floor(height * dpr);
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.scale(dpr, dpr);

      if (!pointer.active) {
        pointer.x = width / 2;
        pointer.y = height / 2;
        pointer.px = pointer.x;
        pointer.py = pointer.y;
      }
    }
    window.addEventListener("resize", resize);
    resize();

    // Mouse & Touch Tracking
    function onPointerMove(e) {
      var rect = canvas.getBoundingClientRect();
      var clientX = e.touches ? e.touches[0].clientX : e.clientX;
      var clientY = e.touches ? e.touches[0].clientY : e.clientY;
      var newX = clientX - rect.left;
      var newY = clientY - rect.top;

      var dx = newX - pointer.x;
      var dy = newY - pointer.y;
      var dist = Math.sqrt(dx * dx + dy * dy);

      pointer.px = pointer.x;
      pointer.py = pointer.y;
      pointer.x = newX;
      pointer.y = newY;
      pointer.active = true;
      pointer.movedDistance += dist;

      if (discoveryProgress < 100) {
        discoveryProgress = Math.min(100, discoveryProgress + dist * 0.08);
        updateDiscoveryUI();
      }

      // Add harmonic trail points
      trails.push({
        x: pointer.x,
        y: pointer.y,
        vx: dx,
        vy: dy,
        age: 0,
        maxAge: 70 + Math.random() * 40,
        color: Math.random() > 0.4 ? "#D4AF5A" : "#38BDF8"
      });
      if (trails.length > maxTrails) trails.shift();
    }

    function updateDiscoveryUI() {
      if (!discoveryText) return;
      if (discoveryProgress < 30) {
        discoveryText.textContent = "Tracing harmonic tangents (" + Math.round(discoveryProgress) + "%)";
      } else if (discoveryProgress < 70) {
        discoveryText.textContent = "Constructing geometric envelope (" + Math.round(discoveryProgress) + "%)";
      } else if (discoveryProgress < 100) {
        discoveryText.textContent = "Resolving symmetry axis (" + Math.round(discoveryProgress) + "%)";
      } else {
        discoveryText.textContent = "Geometric relationship resolved: Harmonic Envelope";
        if (discoveryStatus) discoveryStatus.classList.add("is-complete");
      }
    }

    if (skipBtn) {
      skipBtn.addEventListener("click", function () {
        discoveryProgress = 100;
        updateDiscoveryUI();
      });
    }

    window.addEventListener("mousemove", onPointerMove, { passive: true });
    window.addEventListener("touchmove", onPointerMove, { passive: true });

    // Drawing the background grid & geometric construction
    function drawGrid(cx, cy, offsetX, offsetY) {
      var gridSize = 45;
      var subGrid = 15;

      ctx.save();
      // Millimeter sub-grid
      ctx.strokeStyle = "rgba(212, 175, 90, 0.035)";
      ctx.lineWidth = 0.5;
      ctx.beginPath();
      for (var x = (offsetX % subGrid); x < width; x += subGrid) {
        ctx.moveTo(x, 0); ctx.lineTo(x, height);
      }
      for (var y = (offsetY % subGrid); y < height; y += subGrid) {
        ctx.moveTo(0, y); ctx.lineTo(width, y);
      }
      ctx.stroke();

      // Major coordinate grid
      ctx.strokeStyle = "rgba(56, 189, 248, 0.07)";
      ctx.lineWidth = 0.8;
      ctx.beginPath();
      for (var mx = (offsetX % gridSize); mx < width; mx += gridSize) {
        ctx.moveTo(mx, 0); ctx.lineTo(mx, height);
      }
      for (var my = (offsetY % gridSize); my < height; my += gridSize) {
        ctx.moveTo(0, my); ctx.lineTo(width, my);
      }
      ctx.stroke();

      // Coordinate axes
      ctx.strokeStyle = "rgba(212, 175, 90, 0.18)";
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(cx, 0); ctx.lineTo(cx, height);
      ctx.moveTo(0, cy); ctx.lineTo(width, cy);
      ctx.stroke();

      // Ticks along axes
      ctx.strokeStyle = "rgba(212, 175, 90, 0.3)";
      ctx.beginPath();
      for (var tx = cx % gridSize; tx < width; tx += gridSize) {
        ctx.moveTo(tx, cy - 3); ctx.lineTo(tx, cy + 3);
      }
      for (var ty = cy % gridSize; ty < height; ty += gridSize) {
        ctx.moveTo(cx - 3, ty); ctx.lineTo(cx + 3, ty);
      }
      ctx.stroke();
      ctx.restore();
    }

    var time = 0;
    function render() {
      time += 0.015;
      ctx.clearRect(0, 0, width, height);

      var cx = width / 2;
      var cy = height / 2;
      var parallaxX = (pointer.x - cx) * 0.05;
      var parallaxY = (pointer.y - cy) * 0.05;

      drawGrid(cx + parallaxX, cy + parallaxY, parallaxX, parallaxY);

      var progressRatio = discoveryProgress / 100;

      // Draw mathematical harmonic curves
      ctx.save();
      ctx.translate(cx + parallaxX, cy + parallaxY);

      // Rotating epicycloid / cardioid envelope
      var numPoints = prefersReducedMotion ? 64 : Math.floor(16 + progressRatio * 48);
      var radius = Math.min(width, height) * (0.22 + progressRatio * 0.08);

      ctx.lineWidth = 0.9;
      for (var i = 0; i < numPoints; i++) {
        var theta1 = (i / numPoints) * Math.PI * 2 + (prefersReducedMotion ? 0 : time * 0.2);
        var mult = 2 + progressRatio;
        var theta2 = theta1 * mult;

        var x1 = Math.cos(theta1) * radius;
        var y1 = Math.sin(theta1) * radius;
        var x2 = Math.cos(theta2) * radius;
        var y2 = Math.sin(theta2) * radius;

        ctx.strokeStyle = (i % 2 === 0)
          ? "rgba(212, 175, 90, " + (0.06 + progressRatio * 0.16) + ")"
          : "rgba(56, 189, 248, " + (0.05 + progressRatio * 0.14) + ")";

        ctx.beginPath();
        ctx.moveTo(x1, y1);
        ctx.lineTo(x2, y2);
        ctx.stroke();
      }

      // Golden ratio spiral arcs
      if (progressRatio > 0.25 || prefersReducedMotion) {
        ctx.beginPath();
        ctx.strokeStyle = "rgba(212, 175, 90, " + (0.1 + progressRatio * 0.25) + ")";
        ctx.lineWidth = 1.2;
        var spiralTurns = 3.5;
        var a = 3;
        var b = 0.2;
        for (var t = 0; t < spiralTurns * Math.PI * 2; t += 0.05) {
          var r = a * Math.exp(b * t);
          var sx = r * Math.cos(t + (prefersReducedMotion ? 0 : time * 0.1));
          var sy = r * Math.sin(t + (prefersReducedMotion ? 0 : time * 0.1));
          if (t === 0) ctx.moveTo(sx, sy);
          else ctx.lineTo(sx, sy);
        }
        ctx.stroke();
      }
      ctx.restore();

      // Render interactive user trails
      if (!prefersReducedMotion && trails.length > 1) {
        for (var j = 0; j < trails.length; j++) {
          var tr = trails[j];
          tr.age++;
          var life = 1 - tr.age / tr.maxAge;
          if (life <= 0) continue;

          ctx.save();
          ctx.strokeStyle = tr.color;
          ctx.globalAlpha = life * 0.55;
          ctx.lineWidth = life * 2;
          ctx.beginPath();
          ctx.arc(tr.x, tr.y, (1 - life) * 12 + 1, 0, Math.PI * 2);
          ctx.stroke();
          ctx.restore();
        }
        trails = trails.filter(function (t) { return t.age < t.maxAge; });
      }

      // The Seed / Cursor Point
      var px = pointer.x;
      var py = pointer.y;

      var pulse = 1 + 0.15 * Math.sin(time * 3);
      var grad = ctx.createRadialGradient(px, py, 2, px, py, 24 * pulse);
      grad.addColorStop(0, "rgba(56, 189, 248, 0.9)");
      grad.addColorStop(0.3, "rgba(212, 175, 90, 0.45)");
      grad.addColorStop(1, "rgba(212, 175, 90, 0)");

      ctx.fillStyle = grad;
      ctx.beginPath();
      ctx.arc(px, py, 24 * pulse, 0, Math.PI * 2);
      ctx.fill();

      ctx.fillStyle = "#FFFFFF";
      ctx.beginPath();
      ctx.arc(px, py, 3, 0, Math.PI * 2);
      ctx.fill();

      if (!prefersReducedMotion) {
        animFrameId = requestAnimationFrame(render);
      }
    }

    if (prefersReducedMotion) {
      render();
    } else {
      render();
    }
  })();

  /* ==========================================================================
     2. EDITORIAL DEMONSTRATION PUZZLE: Heron's Shortest Path
     ========================================================================== */
  (function initPuzzle() {
    var canvas = document.getElementById("puzzleCanvas");
    if (!canvas) return;

    var ctx = canvas.getContext("2d");
    if (!ctx) return;

    var slider = document.getElementById("puzzleSlider");
    var nudgeLeft = document.getElementById("puzzleNudgeLeft");
    var nudgeRight = document.getElementById("puzzleNudgeRight");
    var posPercent = document.getElementById("puzzlePosPercent");
    var checkBtn = document.getElementById("puzzleCheckBtn");
    var hintBtn = document.getElementById("puzzleHintBtn");
    var hintBox = document.getElementById("puzzleHintBox");
    var proofBtn = document.getElementById("puzzleProofBtn");
    var revealBox = document.getElementById("puzzleRevealBox");
    var resetBtn = document.getElementById("puzzleResetBtn");
    var srStatus = document.getElementById("puzzleSrStatus");

    var readoutAP = document.getElementById("readoutAP");
    var readoutPB = document.getElementById("readoutPB");
    var readoutTotal = document.getElementById("readoutTotal");
    var readoutAlpha = document.getElementById("readoutAlpha");
    var readoutBeta = document.getElementById("readoutBeta");

    // Coordinates setup on a 800 x 420 virtual space
    var V_WIDTH = 800;
    var V_HEIGHT = 420;
    var BASELINE_Y = 270;
    var LINE_X_MIN = 80;
    var LINE_X_MAX = 720;

    var ptA = { x: 170, y: 80, label: "A" };
    var ptB = { x: 640, y: 135, label: "B" };
    var ptB_reflected = { x: ptB.x, y: BASELINE_Y + (BASELINE_Y - ptB.y), label: "B'" };

    // Exact mathematical minimum:
    // Slope of line connecting A and B' is m = (B'_y - A_y) / (B'_x - A_x)
    // x_optimal satisfies: (BASELINE_Y - A_y) / (x_optimal - A_x) = m
    var slopeABprime = (ptB_reflected.y - ptA.y) / (ptB_reflected.x - ptA.x);
    var optimalX = ptA.x + (BASELINE_Y - ptA.y) / slopeABprime;
    var optimalPercent = ((optimalX - LINE_X_MIN) / (LINE_X_MAX - LINE_X_MIN)) * 100;

    var currentPercent = 25.0; // initial slider position
    var isDragging = false;
    var showProof = false;
    var isSolved = false;

    function getPointP() {
      var x = LINE_X_MIN + (currentPercent / 100) * (LINE_X_MAX - LINE_X_MIN);
      return { x: x, y: BASELINE_Y };
    }

    function calculateMetrics() {
      var p = getPointP();
      var dxA = ptA.x - p.x;
      var dyA = ptA.y - p.y;
      var lenAP = Math.sqrt(dxA * dxA + dyA * dyA);

      var dxB = ptB.x - p.x;
      var dyB = ptB.y - p.y;
      var lenPB = Math.sqrt(dxB * dxB + dyB * dyB);

      var total = lenAP + lenPB;

      // Scale to human-friendly units (e.g. 1 unit = 20px)
      var scale = 20;
      var uAP = (lenAP / scale).toFixed(2);
      var uPB = (lenPB / scale).toFixed(2);
      var uTotal = (total / scale).toFixed(2);

      // Incident angle alpha: angle with normal at P
      // normal is vertical up: (0, -1)
      var alpha = (Math.atan2(Math.abs(p.x - ptA.x), Math.abs(BASELINE_Y - ptA.y)) * (180 / Math.PI)).toFixed(1);
      var beta = (Math.atan2(Math.abs(ptB.x - p.x), Math.abs(BASELINE_Y - ptB.y)) * (180 / Math.PI)).toFixed(1);

      return {
        ap: uAP,
        pb: uPB,
        total: uTotal,
        alpha: alpha,
        beta: beta,
        diff: Math.abs(parseFloat(alpha) - parseFloat(beta)),
        isOptimal: Math.abs(currentPercent - optimalPercent) < 1.4
      };
    }

    function updateUI() {
      var m = calculateMetrics();
      if (readoutAP) readoutAP.textContent = m.ap;
      if (readoutPB) readoutPB.textContent = m.pb;
      if (readoutTotal) readoutTotal.textContent = m.total;
      if (readoutAlpha) readoutAlpha.textContent = m.alpha + "°";
      if (readoutBeta) readoutBeta.textContent = m.beta + "°";
      if (posPercent) posPercent.textContent = Math.round(currentPercent) + "%";
      if (slider) slider.value = currentPercent;

      if (m.isOptimal) {
        isSolved = true;
        if (checkBtn) {
          checkBtn.textContent = "Solution Verified!";
          checkBtn.classList.add("is-solved");
        }
      } else {
        isSolved = false;
        if (checkBtn) {
          checkBtn.textContent = "Check Solution";
          checkBtn.classList.remove("is-solved");
        }
      }

      draw();
    }

    function draw() {
      ctx.clearRect(0, 0, V_WIDTH, V_HEIGHT);
      var p = getPointP();
      var m = calculateMetrics();

      // 1. Grid background inside canvas
      ctx.strokeStyle = "rgba(248, 246, 240, 0.04)";
      ctx.lineWidth = 1;
      for (var x = 0; x < V_WIDTH; x += 40) {
        ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, V_HEIGHT); ctx.stroke();
      }
      for (var y = 0; y < V_HEIGHT; y += 40) {
        ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(V_WIDTH, y); ctx.stroke();
      }

      // 2. Baseline L (Reflective riverbank)
      ctx.strokeStyle = "rgba(212, 175, 90, 0.4)";
      ctx.lineWidth = 2.5;
      ctx.beginPath();
      ctx.moveTo(LINE_X_MIN - 30, BASELINE_Y);
      ctx.lineTo(LINE_X_MAX + 30, BASELINE_Y);
      ctx.stroke();

      // Baseline hatch marks below line
      ctx.strokeStyle = "rgba(212, 175, 90, 0.18)";
      ctx.lineWidth = 1;
      for (var hx = LINE_X_MIN - 20; hx <= LINE_X_MAX + 20; hx += 16) {
        ctx.beginPath();
        ctx.moveTo(hx, BASELINE_Y);
        ctx.lineTo(hx - 8, BASELINE_Y + 12);
        ctx.stroke();
      }

      // Line L label
      ctx.font = "bold 13px Newsreader, Georgia, serif";
      ctx.fillStyle = "rgba(212, 175, 90, 0.8)";
      ctx.fillText("Line L (Reflective Axis)", LINE_X_MIN - 20, BASELINE_Y - 10);

      // 3. Normal at P (perpendicular dashed line)
      ctx.save();
      ctx.setLineDash([4, 4]);
      ctx.strokeStyle = "rgba(148, 163, 184, 0.4)";
      ctx.lineWidth = 1.2;
      ctx.beginPath();
      ctx.moveTo(p.x, BASELINE_Y - 90);
      ctx.lineTo(p.x, BASELINE_Y);
      ctx.stroke();
      ctx.restore();

      // Normal label
      ctx.font = "11px sans-serif";
      ctx.fillStyle = "rgba(148, 163, 184, 0.6)";
      ctx.fillText("Normal", p.x + 5, BASELINE_Y - 75);

      // 4. Angle arcs at P
      ctx.strokeStyle = m.isOptimal ? "rgba(212, 175, 90, 0.9)" : "rgba(56, 189, 248, 0.7)";
      ctx.lineWidth = 1.5;

      // Arc for alpha (left)
      var angA = Math.atan2(ptA.y - p.y, ptA.x - p.x);
      ctx.beginPath();
      ctx.arc(p.x, p.y, 34, -Math.PI / 2, angA, true);
      ctx.stroke();

      // Arc for beta (right)
      var angB = Math.atan2(ptB.y - p.y, ptB.x - p.x);
      ctx.beginPath();
      ctx.arc(p.x, p.y, 34, -Math.PI / 2, angB, false);
      ctx.stroke();

      ctx.font = "12px sans-serif";
      ctx.fillStyle = m.isOptimal ? "#F5D37E" : "#7DD3FC";
      ctx.fillText("α=" + m.alpha + "°", p.x - 55, BASELINE_Y - 38);
      ctx.fillText("β=" + m.beta + "°", p.x + 18, BASELINE_Y - 38);

      // 5. If Proof is active, draw reflected point B' and straight line A -> B'
      if (showProof) {
        ctx.save();
        // Virtual line from B to B'
        ctx.setLineDash([3, 5]);
        ctx.strokeStyle = "rgba(56, 189, 248, 0.35)";
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.moveTo(ptB.x, ptB.y);
        ctx.lineTo(ptB_reflected.x, ptB_reflected.y);
        ctx.stroke();

        // Line from P to B'
        ctx.strokeStyle = "rgba(212, 175, 90, 0.4)";
        ctx.beginPath();
        ctx.moveTo(p.x, p.y);
        ctx.lineTo(ptB_reflected.x, ptB_reflected.y);
        ctx.stroke();

        // Collinear straight line A -> B'
        ctx.setLineDash([6, 4]);
        ctx.strokeStyle = "rgba(245, 211, 126, 0.85)";
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(ptA.x, ptA.y);
        ctx.lineTo(ptB_reflected.x, ptB_reflected.y);
        ctx.stroke();
        ctx.restore();

        // Reflected Point B'
        ctx.fillStyle = "rgba(56, 189, 248, 0.2)";
        ctx.beginPath();
        ctx.arc(ptB_reflected.x, ptB_reflected.y, 14, 0, Math.PI * 2);
        ctx.fill();

        ctx.fillStyle = "#38BDF8";
        ctx.beginPath();
        ctx.arc(ptB_reflected.x, ptB_reflected.y, 6, 0, Math.PI * 2);
        ctx.fill();

        ctx.font = "bold 14px sans-serif";
        ctx.fillStyle = "#7DD3FC";
        ctx.fillText("B' (Mirror of B)", ptB_reflected.x + 12, ptB_reflected.y + 5);
      }

      // 6. Draw Path Segments AP and PB
      ctx.lineWidth = m.isOptimal ? 3 : 2;
      ctx.strokeStyle = m.isOptimal ? "#F5D37E" : "#38BDF8";
      ctx.beginPath();
      ctx.moveTo(ptA.x, ptA.y);
      ctx.lineTo(p.x, p.y);
      ctx.stroke();

      ctx.strokeStyle = m.isOptimal ? "#F5D37E" : "#D4AF5A";
      ctx.beginPath();
      ctx.moveTo(p.x, p.y);
      ctx.lineTo(ptB.x, ptB.y);
      ctx.stroke();

      // 7. Draw Point A
      drawAnchorPoint(ptA.x, ptA.y, "A (Start)", "#38BDF8");

      // 8. Draw Point B
      drawAnchorPoint(ptB.x, ptB.y, "B (Destination)", "#D4AF5A");

      // 9. Draw Point P (Movable handle)
      drawPointP(p.x, p.y, m.isOptimal);
    }

    function drawAnchorPoint(x, y, label, color) {
      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.arc(x, y, 7, 0, Math.PI * 2);
      ctx.fill();

      ctx.strokeStyle = "#FFFFFF";
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(x, y, 7, 0, Math.PI * 2);
      ctx.stroke();

      ctx.font = "bold 14px Newsreader, Georgia, serif";
      ctx.fillStyle = "#FFFFFF";
      ctx.fillText(label, x - 20, y - 14);
    }

    function drawPointP(x, y, optimal) {
      var pulse = optimal ? 1.25 : 1;
      var auraColor = optimal ? "rgba(212, 175, 90, 0.4)" : "rgba(56, 189, 248, 0.3)";

      ctx.fillStyle = auraColor;
      ctx.beginPath();
      ctx.arc(x, y, 18 * pulse, 0, Math.PI * 2);
      ctx.fill();

      ctx.fillStyle = optimal ? "#F5D37E" : "#FFFFFF";
      ctx.beginPath();
      ctx.arc(x, y, 8, 0, Math.PI * 2);
      ctx.fill();

      ctx.strokeStyle = optimal ? "#D4AF5A" : "#060609";
      ctx.lineWidth = 2.5;
      ctx.beginPath();
      ctx.arc(x, y, 8, 0, Math.PI * 2);
      ctx.stroke();

      ctx.font = "bold 14px sans-serif";
      ctx.fillStyle = optimal ? "#F5D37E" : "#FFFFFF";
      ctx.fillText("Point P", x - 22, y + 26);
    }

    // Canvas coordinate conversion helper
    function getCanvasCoordinates(e) {
      var rect = canvas.getBoundingClientRect();
      var clientX = e.touches ? e.touches[0].clientX : e.clientX;
      var clientY = e.touches ? e.touches[0].clientY : e.clientY;
      var scaleX = V_WIDTH / rect.width;
      var scaleY = V_HEIGHT / rect.height;
      return {
        x: (clientX - rect.left) * scaleX,
        y: (clientY - rect.top) * scaleY
      };
    }

    function updateFromCanvasX(canvasX) {
      var clamped = Math.max(LINE_X_MIN, Math.min(LINE_X_MAX, canvasX));
      currentPercent = ((clamped - LINE_X_MIN) / (LINE_X_MAX - LINE_X_MIN)) * 100;
      updateUI();
    }

    canvas.addEventListener("mousedown", function (e) {
      var pos = getCanvasCoordinates(e);
      var p = getPointP();
      var dist = Math.hypot(pos.x - p.x, pos.y - p.y);
      if (dist < 40 || Math.abs(pos.y - BASELINE_Y) < 35) {
        isDragging = true;
        updateFromCanvasX(pos.x);
      }
    });

    window.addEventListener("mousemove", function (e) {
      if (!isDragging) return;
      var pos = getCanvasCoordinates(e);
      updateFromCanvasX(pos.x);
    });

    window.addEventListener("mouseup", function () {
      isDragging = false;
    });

    canvas.addEventListener("touchstart", function (e) {
      var pos = getCanvasCoordinates(e);
      var p = getPointP();
      var dist = Math.hypot(pos.x - p.x, pos.y - p.y);
      if (dist < 45 || Math.abs(pos.y - BASELINE_Y) < 40) {
        isDragging = true;
        updateFromCanvasX(pos.x);
        e.preventDefault();
      }
    }, { passive: false });

    window.addEventListener("touchmove", function (e) {
      if (!isDragging) return;
      var pos = getCanvasCoordinates(e);
      updateFromCanvasX(pos.x);
      e.preventDefault();
    }, { passive: false });

    window.addEventListener("touchend", function () {
      isDragging = false;
    });

    // Slider input
    if (slider) {
      slider.addEventListener("input", function () {
        currentPercent = parseFloat(slider.value);
        updateUI();
      });
    }

    // Keyboard & Nudge Controls
    if (nudgeLeft) {
      nudgeLeft.addEventListener("click", function () {
        currentPercent = Math.max(0, currentPercent - 1.5);
        updateUI();
      });
    }
    if (nudgeRight) {
      nudgeRight.addEventListener("click", function () {
        currentPercent = Math.min(100, currentPercent + 1.5);
        updateUI();
      });
    }

    window.addEventListener("keydown", function (e) {
      if (document.activeElement === slider || document.activeElement === canvas) {
        if (e.key === "ArrowLeft") {
          currentPercent = Math.max(0, currentPercent - 1);
          updateUI();
          e.preventDefault();
        } else if (e.key === "ArrowRight") {
          currentPercent = Math.min(100, currentPercent + 1);
          updateUI();
          e.preventDefault();
        }
      }
    });

    // Action Buttons
    if (checkBtn) {
      checkBtn.addEventListener("click", function () {
        var m = calculateMetrics();
        if (m.isOptimal) {
          if (revealBox) revealBox.hidden = false;
          if (srStatus) srStatus.textContent = "Correct! Point P is at the geometric minimum path length.";
          showProof = true;
          draw();
        } else {
          var advice = (currentPercent < optimalPercent) ? "Try moving Point P further right." : "Try moving Point P further left.";
          if (srStatus) srStatus.textContent = "Not quite at minimum. " + advice + " Total length is " + m.total + ".";
          alert("Total length is currently " + m.total + " units.\n" + advice + "\nNotice that angle α (" + m.alpha + "°) does not yet equal angle β (" + m.beta + "°).");
        }
      });
    }

    if (hintBtn) {
      hintBtn.addEventListener("click", function () {
        var isHidden = hintBox.hidden;
        hintBox.hidden = !isHidden;
        hintBtn.setAttribute("aria-expanded", isHidden ? "true" : "false");
        hintBtn.textContent = isHidden ? "Hide Hint" : "Hint";
      });
    }

    if (proofBtn) {
      proofBtn.addEventListener("click", function () {
        showProof = !showProof;
        proofBtn.textContent = showProof ? "Hide Proof" : "Show Proof";
        if (revealBox) revealBox.hidden = !showProof;
        draw();
      });
    }

    if (resetBtn) {
      resetBtn.addEventListener("click", function () {
        currentPercent = 25.0;
        showProof = false;
        if (proofBtn) proofBtn.textContent = "Show Proof";
        if (hintBox) hintBox.hidden = true;
        if (hintBtn) {
          hintBtn.setAttribute("aria-expanded", "false");
          hintBtn.textContent = "Hint";
        }
        if (revealBox) revealBox.hidden = true;
        updateUI();
      });
    }

    updateUI();
  })();

  /* ==========================================================================
     3. FOUR CHALLENGE ZONES: Direct Filtering & Navigation
     ========================================================================== */
  (function initZones() {
    var zoneCards = document.querySelectorAll(".ma-zone");
    var archiveSection = document.getElementById("archive");

    zoneCards.forEach(function (card) {
      var grade = card.dataset.grade;
      var btn = card.querySelector(".ma-zone__btn");

      function activateZone() {
        var targetFilter = document.querySelector('.ma-filter[data-grade="' + grade + '"]');
        if (targetFilter) {
          targetFilter.click();
        }
        if (archiveSection) {
          archiveSection.scrollIntoView({ behavior: "smooth" });
        }
      }

      if (btn) {
        btn.addEventListener("click", function (e) {
          e.stopPropagation();
          activateZone();
        });
      }

      card.addEventListener("click", activateZone);
      card.addEventListener("keydown", function (e) {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          activateZone();
        }
      });
    });
  })();

  /* ==========================================================================
     4. HOW A MIND SOLVES: Five Stages, One Problem (The Mutilated Chessboard)
     ========================================================================== */
  (function initJourney() {
    var canvas = document.getElementById("journeyCanvas");
    if (!canvas) return;

    var ctx = canvas.getContext("2d");
    if (!ctx) return;

    var tabs = Array.prototype.slice.call(document.querySelectorAll(".ma-journey-tab"));
    var steps = Array.prototype.slice.call(document.querySelectorAll(".ma-step"));
    var stageBadge = document.getElementById("journeyStageBadge");
    var currentStage = "01";

    var stageTitles = {
      "01": "Stage 1: Question — Excising Corners",
      "02": "Stage 2: Think — Invariant Tile Rule",
      "03": "Stage 3: Explore — Minimal 2×2 Case",
      "04": "Stage 4: Solve — Parity Proof (30 ≠ 32)",
      "05": "Stage 5: Discover — The Invariant Principle"
    };

    function setStage(stageId) {
      currentStage = stageId;

      tabs.forEach(function (tab) {
        var on = tab.dataset.step === stageId;
        tab.classList.toggle("is-active", on);
        tab.setAttribute("aria-selected", on ? "true" : "false");
      });

      steps.forEach(function (step) {
        var on = step.dataset.step === stageId;
        step.classList.toggle("is-active", on);
      });

      if (stageBadge && stageTitles[stageId]) {
        stageBadge.textContent = stageTitles[stageId];
      }

      drawStage();
    }

    tabs.forEach(function (tab) {
      tab.addEventListener("click", function () {
        setStage(tab.dataset.step);
      });
    });

    steps.forEach(function (step) {
      step.addEventListener("click", function () {
        setStage(step.dataset.step);
      });
    });

    function drawStage() {
      var w = canvas.width;
      var h = canvas.height;
      ctx.clearRect(0, 0, w, h);

      if (currentStage === "03") {
        drawMiniCase(w, h);
      } else {
        drawChessboard(w, h);
      }
    }

    function drawChessboard(w, h) {
      var size = 8;
      var tileSize = 44;
      var startX = (w - size * tileSize) / 2;
      var startY = (h - size * tileSize) / 2;

      for (var r = 0; r < size; r++) {
        for (var c = 0; c < size; c++) {
          var isCutCorner = (r === 0 && c === 0) || (r === 7 && c === 7);
          var x = startX + c * tileSize;
          var y = startY + r * tileSize;

          if (isCutCorner) {
            // Excised corner
            ctx.fillStyle = "rgba(239, 68, 68, 0.12)";
            ctx.fillRect(x, y, tileSize, tileSize);

            ctx.strokeStyle = "rgba(239, 68, 68, 0.5)";
            ctx.lineWidth = 1.5;
            ctx.strokeRect(x + 2, y + 2, tileSize - 4, tileSize - 4);

            // Draw red X
            ctx.strokeStyle = "rgba(239, 68, 68, 0.8)";
            ctx.beginPath();
            ctx.moveTo(x + 10, y + 10); ctx.lineTo(x + tileSize - 10, y + tileSize - 10);
            ctx.moveTo(x + tileSize - 10, y + 10); ctx.lineTo(x + 10, y + tileSize - 10);
            ctx.stroke();
          } else {
            // Chessboard coloring
            var isDark = (r + c) % 2 === 0;

            if (currentStage === "04" || currentStage === "05") {
              // Highlighting parity in Stage 4 & 5
              ctx.fillStyle = isDark ? "#1A1822" : "rgba(212, 175, 90, 0.28)";
            } else {
              ctx.fillStyle = isDark ? "#14151E" : "#242738";
            }
            ctx.fillRect(x, y, tileSize, tileSize);

            ctx.strokeStyle = "rgba(248, 246, 240, 0.08)";
            ctx.lineWidth = 1;
            ctx.strokeRect(x, y, tileSize, tileSize);
          }
        }
      }

      // Draw Domino Demonstration
      if (currentStage === "01") {
        // Draw sample 2x1 domino beside grid
        ctx.fillStyle = "rgba(56, 189, 248, 0.4)";
        ctx.strokeStyle = "#38BDF8";
        ctx.lineWidth = 2;
        var dx = startX + 2 * tileSize;
        var dy = startY + 3 * tileSize;
        ctx.fillRect(dx, dy, tileSize * 2, tileSize);
        ctx.strokeRect(dx, dy, tileSize * 2, tileSize);

        ctx.font = "bold 12px sans-serif";
        ctx.fillStyle = "#FFFFFF";
        ctx.fillText("2×1 Domino", dx + 8, dy + 26);
      } else if (currentStage === "02") {
        // Highlight edge sharing
        ctx.strokeStyle = "#F5D37E";
        ctx.lineWidth = 3;
        ctx.strokeRect(startX + 3 * tileSize, startY + 3 * tileSize, tileSize * 2, tileSize);

        ctx.fillStyle = "#F5D37E";
        ctx.font = "12px sans-serif";
        ctx.fillText("Always 1 Dark + 1 Light", startX + 3 * tileSize - 10, startY + 3 * tileSize - 10);
      } else if (currentStage === "04") {
        // Stage 4 Solve: Tally banner
        ctx.fillStyle = "rgba(13, 14, 20, 0.9)";
        ctx.fillRect(20, h - 60, w - 40, 44);
        ctx.strokeStyle = "var(--ma-gold, #D4AF5A)";
        ctx.strokeRect(20, h - 60, w - 40, 44);

        ctx.font = "bold 13px sans-serif";
        ctx.fillStyle = "#F5D37E";
        ctx.fillText("Board: 30 Dark + 32 Light ≠ 31 Dominoes (Impossible!)", 36, h - 33);
      } else if (currentStage === "05") {
        // Stage 5 Discover
        ctx.fillStyle = "rgba(13, 14, 20, 0.92)";
        ctx.fillRect(20, h - 60, w - 40, 44);
        ctx.strokeStyle = "#38BDF8";
        ctx.strokeRect(20, h - 60, w - 40, 44);

        ctx.font = "bold 13px sans-serif";
        ctx.fillStyle = "#7DD3FC";
        ctx.fillText("Parity Invariant eliminates 2×10¹⁵ brute-force checks.", 40, h - 33);
      }
    }

    function drawMiniCase(w, h) {
      // 2x2 grid with opposite corners missing
      var tileSize = 100;
      var startX = (w - 2 * tileSize) / 2;
      var startY = (h - 2 * tileSize) / 2;

      ctx.fillStyle = "#F8F6F0";
      ctx.font = "bold 16px sans-serif";
      ctx.fillText("Minimal Case: 2×2 Board", startX + 10, startY - 24);

      // (0,0) - excised
      ctx.fillStyle = "rgba(239, 68, 68, 0.15)";
      ctx.fillRect(startX, startY, tileSize, tileSize);
      ctx.strokeStyle = "#EF4444";
      ctx.strokeRect(startX, startY, tileSize, tileSize);
      ctx.font = "14px sans-serif";
      ctx.fillStyle = "#EF4444";
      ctx.fillText("Excised", startX + 25, startY + 55);

      // (0,1) - remaining
      ctx.fillStyle = "#1E2235";
      ctx.fillRect(startX + tileSize, startY, tileSize, tileSize);
      ctx.strokeStyle = "#D4AF5A";
      ctx.strokeRect(startX + tileSize, startY, tileSize, tileSize);
      ctx.fillStyle = "#F5D37E";
      ctx.fillText("Square A", startX + tileSize + 20, startY + 55);

      // (1,0) - remaining
      ctx.fillStyle = "#1E2235";
      ctx.fillRect(startX, startY + tileSize, tileSize, tileSize);
      ctx.strokeStyle = "#D4AF5A";
      ctx.strokeRect(startX, startY + tileSize, tileSize, tileSize);
      ctx.fillStyle = "#F5D37E";
      ctx.fillText("Square B", startX + 20, startY + tileSize + 55);

      // (1,1) - excised
      ctx.fillStyle = "rgba(239, 68, 68, 0.15)";
      ctx.fillRect(startX + tileSize, startY + tileSize, tileSize, tileSize);
      ctx.strokeStyle = "#EF4444";
      ctx.strokeRect(startX + tileSize, startY + tileSize, tileSize, tileSize);
      ctx.fillStyle = "#EF4444";
      ctx.fillText("Excised", startX + tileSize + 25, startY + tileSize + 55);

      // Note below
      ctx.font = "italic 13px sans-serif";
      ctx.fillStyle = "#DFD9CE";
      ctx.fillText("Squares A & B only touch at a diagonal vertex — sharing NO edge.", startX - 40, startY + 2 * tileSize + 35);
      ctx.fillText("A single 2×1 domino CANNOT cover both!", startX + 10, startY + 2 * tileSize + 55);
    }

    setStage("01");
  })();

  /* ==========================================================================
     5. CHALLENGE ARCHIVE: Filter and Search
     ========================================================================== */
  (function initArchive() {
    var grid = document.getElementById("maGrid");
    if (!grid) return;

    var cards = Array.prototype.slice.call(grid.querySelectorAll(".ma-card"));
    var months = Array.prototype.slice.call(grid.querySelectorAll(".ma-month"));
    var buttons = Array.prototype.slice.call(document.querySelectorAll(".ma-filter"));
    var search = document.getElementById("maSearch");
    var none = document.getElementById("maNone");
    var currentGrade = "all";
    var currentTerm = "";

    function applyFilter() {
      var shownCount = 0;

      cards.forEach(function (card) {
        var cardGrade = card.dataset.grade;
        var cardFind = (card.dataset.find || "").toLowerCase();

        var matchesGrade = (currentGrade === "all" || cardGrade === currentGrade);
        var matchesTerm = (!currentTerm || cardFind.indexOf(currentTerm) !== -1);

        var isVisible = matchesGrade && matchesTerm;
        card.hidden = !isVisible;

        if (isVisible) shownCount++;
      });

      // Hide months that have zero visible cards
      months.forEach(function (m) {
        var hasVisible = !!m.querySelector(".ma-card:not([hidden])");
        m.hidden = !hasVisible;
      });

      if (none) {
        none.hidden = shownCount !== 0;
      }
    }

    buttons.forEach(function (btn) {
      btn.addEventListener("click", function () {
        currentGrade = btn.dataset.grade;
        buttons.forEach(function (b) {
          var on = b === btn;
          b.classList.toggle("is-on", on);
          b.setAttribute("aria-pressed", on ? "true" : "false");
        });
        applyFilter();
      });
    });

    if (search) {
      search.addEventListener("input", function () {
        currentTerm = search.value.trim().toLowerCase();
        applyFilter();
      });
    }
  })();
})();

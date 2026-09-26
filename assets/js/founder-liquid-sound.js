/* Founder portrait: the opt-in liquid sound. Ported from the designer's
   Gurudev handoff (src/liquid-sound.js); settings and behaviour unchanged.
   No sound, network request, or AudioContext before the Sound button.

   The recording is the designer's Mountain_Stillness.m4a, byte for byte,
   at assets/audio/gurudev-liquid-source.m4a; the page names it on the
   portrait's data-sound. The handoff's file:// fallback (the same bytes
   as a script) is left out: this site is only ever served over HTTP(S). */
(() => {
  'use strict';
  const root = document.querySelector('[data-gurudev-opening]');
  const hero = root?.querySelector('.gp-hero');
  const button = hero?.querySelector('.gp-sound');
  const status = hero?.querySelector('.gp-sound-status');
  if (!hero || !button) return;

  // EDIT THESE VALUES to tune the sound. Gain is linear amplitude, not a percentage of perceived loudness.
  const SETTINGS = {
    source: hero.dataset.sound,
    // This source is fuller than the former ASMR clip; keep its output restrained.
    maxGain: 0.16,
    attackMs: 100,
    releaseMs: 350,
    speedSmoothingMs: 75,
    idleMs: 75,
    speedFloor: 12,
    speedAtFull: 1000,
    // Greater than 1 keeps slow movement whisper-quiet and gives faster movement more presence.
    speedExponent: 1.25,
    loopStart: 36.80,
    loopEnd: 45.60372,
    crossfadeSeconds: 0.65,
  };

  let context = null, gain = null, decoded = null, loop = null, voice = null, loading = null;
  let enabled = false, ready = false, active = false, visible = true, focused = true, disposed = false;
  let previous = null, smoothedSpeed = 0, lastMovement = 0, intent = 0;
  let raf = 0, stopTimer = 0, lastTick = 0, resumePending = null;
  let envelope = { from: 0, target: 0, start: 0, tau: 0.1 };
  let loadCount = 0, decodeCount = 0, starts = 0, peakVoices = 0;
  const clamp = (n, lo, hi) => Math.max(lo, Math.min(hi, n));
  const allowed = () => enabled && ready && active && visible && focused && !document.hidden && !disposed;

  function label(message = '') {
    button.textContent = enabled ? 'Sound on' : 'Sound off';
    button.setAttribute('aria-pressed', String(enabled));
    button.setAttribute('aria-label', enabled ? 'Sound on. Turn liquid sound off' : 'Sound off. Turn liquid sound on');
    button.setAttribute('aria-busy', String(enabled && !ready));
    if (status && message) status.textContent = message;
  }

  function gainAt(time = context?.currentTime || 0) {
    return envelope.target + (envelope.from - envelope.target) * Math.exp(-Math.max(0, time - envelope.start) / envelope.tau);
  }

  function targetGain(value) {
    if (!gain || !context) return;
    const now = context.currentTime;
    const from = gainAt(now), target = clamp(value, 0, SETTINGS.maxGain);
    if (Math.abs(envelope.target - target) < 0.00005) return;
    const tau = Math.max(0.005, (target > from ? SETTINGS.attackMs : SETTINGS.releaseMs) / 3000);
    // Hold the computed current value when replacing automation; never jump to a previous target.
    gain.gain.cancelScheduledValues(now);
    gain.gain.setValueAtTime(from, now);
    gain.gain.setTargetAtTime(target, now, tau);
    if (target === 0) gain.gain.setValueAtTime(0, now + SETTINGS.releaseMs / 1000 * 2);
    envelope = { from, target, start: now, tau };
  }

  function resetMotion() {
    previous = null; smoothedSpeed = 0; lastMovement = 0;
  }

  function stopVoice() {
    clearTimeout(stopTimer); stopTimer = 0;
    if (!voice) return;
    const old = voice; voice = null;
    try { old.stop(); } catch {}
    old.disconnect();
  }

  function silence(reason = 'stopped') {
    resetMotion(); cancelAnimationFrame(raf); raf = 0;
    targetGain(0);
    clearTimeout(stopTimer);
    // AudioParam fades on the audio thread even if page timers are throttled in a hidden tab.
    stopTimer = setTimeout(() => { stopTimer = 0; stopVoice(); }, SETTINGS.releaseMs * 2 + 60);
    hero.dataset.soundActivity = reason;
  }

  function ensureVoice() {
    clearTimeout(stopTimer); stopTimer = 0;
    if (voice || !loop || context?.state !== 'running') return;
    voice = context.createBufferSource();
    voice.buffer = loop;
    voice.loop = true;
    voice.loopStart = 0;
    voice.loopEnd = loop.duration;
    voice.playbackRate.value = 1; // Preserve the source's natural pitch at every cursor speed.
    voice.connect(gain);
    voice.start();
    starts++; peakVoices = Math.max(peakVoices, 1);
  }

  function makeLoop(buffer) {
    const sr = buffer.sampleRate;
    const start = Math.round(SETTINGS.loopStart * sr);
    const end = Math.min(buffer.length, Math.round(SETTINGS.loopEnd * sr));
    const span = end - start;
    if (span < sr * 0.5) throw Error('The selected audio region is too short.');
    const overlap = Math.min(Math.round(SETTINGS.crossfadeSeconds * sr), Math.floor(span / 3));
    const length = span - overlap;
    const result = context.createBuffer(buffer.numberOfChannels, length, sr);
    for (let channel = 0; channel < buffer.numberOfChannels; channel++) {
      const source = buffer.getChannelData(channel), output = result.getChannelData(channel);
      output.set(source.subarray(start, start + length));
      // The loop joins raw adjacent samples at its wrap. The audible transition is spread
      // over the configured overlap with an equal-power tail-to-head crossfade.
      for (let i = 0; i < overlap; i++) {
        const theta = i / Math.max(1, overlap - 1) * Math.PI / 2;
        output[i] = source[start + length + i] * Math.cos(theta) + source[start + i] * Math.sin(theta);
      }
    }
    return result;
  }

  async function load() {
    if (decoded) return;
    if (loading) return loading;
    loading = (async () => {
      loadCount++;
      const response = await fetch(SETTINGS.source, { credentials: 'same-origin' });
      if (!response.ok) throw Error(`Audio request failed (${response.status}).`);
      const bytes = await response.arrayBuffer();
      if (disposed) return;
      decoded = await context.decodeAudioData(bytes);
      decodeCount++;
      if (disposed) return;
      loop = makeLoop(decoded);
    })();
    try { await loading; } finally { loading = null; }
  }

  function resume() {
    if (!context || context.state === 'running') return Promise.resolve();
    if (!resumePending) resumePending = context.resume().finally(() => { resumePending = null; });
    return resumePending;
  }

  async function toggleSound() {
    const token = ++intent;
    if (enabled) {
      enabled = false; silence('muted'); label('Liquid sound is off.'); return;
    }
    enabled = true; resetMotion(); label('Loading liquid sound.');
    try {
      if (!context) {
        const AudioContextClass = window.AudioContext || window.webkitAudioContext;
        if (!AudioContextClass) throw Error('This browser does not support Web Audio.');
        // Creation and resume happen synchronously in the explicit button gesture.
        context = new AudioContextClass({ latencyHint: 'interactive' });
        gain = context.createGain(); gain.gain.value = 0; gain.connect(context.destination);
        context.addEventListener('statechange', contextStateChanged);
      }
      const unlocked = resume();
      await Promise.all([unlocked, load()]);
      if (disposed || token !== intent || !enabled) return;
      ready = true; silence('ready'); label('Liquid sound is on. Move across the portrait to hear it.');
    } catch (error) {
      if (disposed || token !== intent) return;
      enabled = false; ready = false; silence('unavailable');
      label('Sound could not start. Select Sound off to try again.');
      hero.dataset.soundError = error.message;
    }
  }

  function contextStateChanged() {
    if (context?.state !== 'running') silence('suspended');
  }

  function animate(now) {
    raf = 0;
    if (!allowed()) { silence('inactive'); return; }
    const dt = clamp((now - lastTick) / 1000, 0.001, 0.05); lastTick = now;
    if (now - lastMovement > SETTINGS.idleMs) {
      silence('stationary'); return;
    }
    const ratio = clamp((smoothedSpeed - SETTINGS.speedFloor) / (SETTINGS.speedAtFull - SETTINGS.speedFloor), 0, 1);
    const desired = SETTINGS.maxGain * Math.pow(ratio, SETTINGS.speedExponent);
    if (desired > 0 && context.state === 'running') {
      ensureVoice(); targetGain(desired); hero.dataset.soundActivity = 'moving';
    } else targetGain(0);
    if (allowed()) raf = requestAnimationFrame(animate);
  }

  function motion(x, y, timestamp = performance.now()) {
    if (!allowed() || !Number.isFinite(x + y + timestamp)) return;
    if (context.state !== 'running') { resetMotion(); resume().catch(() => silence('suspended')); return; }
    const current = { x, y, t: timestamp };
    if (!previous) { previous = current; return; }
    const elapsedMs = timestamp - previous.t;
    const distance = Math.hypot(x - previous.x, y - previous.y);
    if (elapsedMs < 1) return;
    previous = current;
    if (elapsedMs > 200 || distance > Math.max(hero.clientWidth, hero.clientHeight) * 0.65) {
      smoothedSpeed = 0; return; // Re-entry/teleport must not produce a loud burst.
    }
    const rawSpeed = clamp(distance / (elapsedMs / 1000), 0, SETTINGS.speedAtFull * 3);
    const smoothing = 1 - Math.exp(-elapsedMs / SETTINGS.speedSmoothingMs);
    smoothedSpeed += (rawSpeed - smoothedSpeed) * smoothing;
    if (distance < 0.4) return;
    lastMovement = performance.now();
    clearTimeout(stopTimer); stopTimer = 0;
    if (!raf) { lastTick = performance.now(); raf = requestAnimationFrame(animate); }
  }

  function setActive(value) { active = Boolean(value); silence(active ? 'ready' : 'section-exit'); }
  function setVisible(value) { visible = Boolean(value); silence(visible ? 'ready' : 'out-of-view'); }
  function onVisibility() { silence(document.hidden ? 'tab-hidden' : 'ready'); }
  function onBlur() { focused = false; silence('window-blur'); }
  function onFocus() { focused = true; silence('ready'); }
  function dispose() {
    if (disposed) return;
    disposed = true; enabled = false; intent++; silence('disposed'); clearTimeout(stopTimer); stopVoice();
    button.removeEventListener('click', toggleSound);
    document.removeEventListener('visibilitychange', onVisibility);
    window.removeEventListener('blur', onBlur); window.removeEventListener('focus', onFocus);
    context?.removeEventListener('statechange', contextStateChanged);
    gain?.disconnect(); context?.close().catch(() => {});
    decoded = loop = null;
  }

  button.addEventListener('click', toggleSound);
  document.addEventListener('visibilitychange', onVisibility);
  window.addEventListener('blur', onBlur); window.addEventListener('focus', onFocus);
  label();
  root.__gurudevLiquidSound = {
    motion, silence, setActive, setVisible, dispose,
    inspect() { return { enabled, ready, active, visible, focused, contextState: context?.state || 'not-created',
      contextCreated: Boolean(context), loadCount, decodeCount, activeVoices: voice ? 1 : 0, peakVoices, starts,
      smoothedSpeed, targetGain: envelope.target, currentGain: gainAt(), pitch: 1,
      loopDuration: loop?.duration || 0, sourceDuration: decoded?.duration || 0, settings: { ...SETTINGS } }; },
    // Enables an OfflineAudioContext verification without changing normal playback.
    copyLoop() { return loop ? { sampleRate: loop.sampleRate, channels: Array.from({ length: loop.numberOfChannels }, (_, i) => Array.from(loop.getChannelData(i))) } : null; },
  };
})();

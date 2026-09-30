// The supplied humming sound follows cursor speed only while it contacts the logo.
export const LOGO_AUDIO_SETTINGS = Object.freeze({
  maxVolume: 0.30,
  quietVolume: 0.020,
  attackSeconds: 0.075,
  releaseSeconds: 0.22,
  speedSmoothingSeconds: 0.08,
  movementGraceMs: 95,
  loopStartSeconds: 0.4,
  loopEndSeconds: 24.7,
  crossfadeSeconds: 0.6
});

export function gainForSpeed(speed, settings = LOGO_AUDIO_SETTINGS) {
  if (!Number.isFinite(speed) || speed <= 0) return 0;
  const amount = Math.min(speed / 2.4, 1);
  return settings.quietVolume + (settings.maxVolume - settings.quietVolume) * Math.pow(amount, 0.72);
}

// Blend the tail into the head once, then let a single AudioBufferSource loop.
// The middle of the supplied recording remains unchanged, including its texture.
export function makeSeamlessLoop(context, decoded, settings = LOGO_AUDIO_SETTINGS) {
  const rate = decoded.sampleRate;
  const start = Math.max(0, Math.min(Math.round(settings.loopStartSeconds * rate), decoded.length - 2));
  const end = Math.min(decoded.length, Math.round(settings.loopEndSeconds * rate));
  const length = end - start;
  const overlap = Math.max(2, Math.min(Math.round(settings.crossfadeSeconds * rate), Math.floor(length / 4)));
  const output = context.createBuffer(decoded.numberOfChannels, length - overlap, rate);
  for (let channel = 0; channel < decoded.numberOfChannels; channel++) {
    const original = decoded.getChannelData(channel);
    const data = output.getChannelData(channel);
    data.set(original.subarray(start, end - overlap));
    for (let i = 0; i < overlap; i++) {
      const angle = (i / (overlap - 1)) * Math.PI * 0.5;
      data[i] = original[end - overlap + i] * Math.cos(angle) + original[start + i] * Math.sin(angle);
    }
  }
  return output;
}

export function createLogoAudio({ button, url }) {
  let context = null, master = null, source = null, buffer = null, loadPromise = null;
  let enabled = false, loading = false, disposed = false, error = null;
  let timer = 0, fadeStopTimer = 0, starts = 0, fetched = false;
  let rawSpeed = 0, smoothSpeed = 0, targetGain = 0, lastMovement = -Infinity;
  let previousTick = performance.now(), generation = 0;
  const settings = LOGO_AUDIO_SETTINGS;
  const ownerDocument = button?.ownerDocument || (typeof document !== 'undefined' ? document : null);

  function paint() {
    if (!button) return;
    button.type = 'button';
    button.textContent = loading && enabled ? 'Sound loading…' : enabled ? 'Sound on' : 'Sound off';
    button.setAttribute('aria-pressed', String(enabled));
    button.setAttribute('aria-label', enabled ? 'Sound on. Disable logo sound' : 'Sound off. Enable logo sound');
    button.setAttribute('aria-busy', String(loading && enabled));
    button.dataset.audioState = error ? 'error' : loading && enabled ? 'loading' : enabled ? 'on' : 'off';
    button.title = error ? 'Sound could not load. Select to try again.' : 'Sound responds when you move over the logo';
  }

  function automate(value, duration) {
    targetGain = value;
    if (!master || !context || context.state === 'closed') return;
    // setTargetAtTime approaches 95% of the requested change within duration.
    master.gain.setTargetAtTime(value, context.currentTime, duration / 3);
  }

  function silence() {
    rawSpeed = 0; smoothSpeed = 0; lastMovement = -Infinity;
    if (targetGain !== 0) automate(0, settings.releaseSeconds);
    clearInterval(timer); timer = 0;
  }

  function tick() {
    const now = performance.now();
    const dt = Math.max(0.001, Math.min((now - previousTick) / 1000, 0.1));
    previousTick = now;
    const moving = enabled && !ownerDocument?.hidden && now - lastMovement < settings.movementGraceMs;
    smoothSpeed += ((moving ? rawSpeed : 0) - smoothSpeed) * (1 - Math.exp(-dt / settings.speedSmoothingSeconds));
    const target = moving ? gainForSpeed(smoothSpeed) : 0;
    if (Math.abs(target - targetGain) > 0.0004 || target === 0 && targetGain !== 0) {
      automate(target, target > targetGain ? settings.attackSeconds : settings.releaseSeconds);
    }
    if (!moving && target === 0 && smoothSpeed < 0.005) {
      clearInterval(timer); timer = 0;
    }
  }

  async function prepare() {
    if (buffer) return buffer;
    if (!loadPromise) {
      loadPromise = (async () => {
        fetched = true;
        const response = await fetch(url);
        if (!response.ok) throw new Error(`Logo audio returned ${response.status}`);
        const decoded = await context.decodeAudioData(await response.arrayBuffer());
        if (decoded.duration < settings.loopEndSeconds) throw new Error('Logo audio clip is shorter than its loop region');
        buffer = makeSeamlessLoop(context, decoded);
        return buffer;
      })().catch(reason => { loadPromise = null; throw reason; });
    }
    return loadPromise;
  }

  function startSource() {
    if (source || !buffer || disposed || !enabled) return;
    source = context.createBufferSource();
    source.buffer = buffer;
    source.loop = true;
    source.playbackRate.value = 1;
    source.connect(master);
    source.start();
    starts++;
  }

  function stopSource() {
    if (!source) return;
    source.stop(); source.disconnect(); source = null;
  }

  async function setEnabled(value) {
    if (disposed) return false;
    const requested = Boolean(value);
    if (requested === enabled && (source || loading || !requested)) return enabled;
    generation++;
    const request = generation;
    enabled = requested; error = null;
    clearTimeout(fadeStopTimer); fadeStopTimer = 0;
    silence();
    if (!enabled) {
      loading = false;
      clearInterval(timer); timer = 0;
      fadeStopTimer = setTimeout(() => {
        if (enabled || disposed) return;
        stopSource();
        if (context?.state === 'running') context.suspend().catch(() => {});
      }, settings.releaseSeconds * 1000 + 70);
      paint();
      return false;
    }
    loading = !buffer; paint();
    try {
      // Context creation and resume happen inside the visitor's button gesture.
      if (!context) {
        const AudioContextClass = globalThis.AudioContext || globalThis.webkitAudioContext;
        if (!AudioContextClass) throw new Error('Web Audio is unavailable');
        context = new AudioContextClass();
        master = context.createGain(); master.gain.value = 0; master.connect(context.destination);
      }
      await context.resume();
      await prepare();
      if (disposed || !enabled || request !== generation) return false;
      loading = false;
      startSource();
      previousTick = performance.now();
      paint();
      return true;
    } catch (reason) {
      if (disposed || request !== generation) return false;
      error = String(reason?.message || reason); enabled = false; loading = false;
      silence(); stopSource(); paint();
      return false;
    }
  }

  function movement(speed) {
    if (!enabled || loading || disposed || ownerDocument?.hidden || !Number.isFinite(speed) || speed <= 0) return;
    rawSpeed = Math.max(0, Math.min(speed, 3));
    lastMovement = performance.now();
    if (!timer) { previousTick = lastMovement; timer = setInterval(tick, 25); }
  }

  const onClick = () => { void setEnabled(!enabled); };
  const onVisibility = () => { if (ownerDocument?.hidden) silence(); };
  button?.addEventListener('click', onClick);
  ownerDocument?.addEventListener('visibilitychange', onVisibility);
  paint();

  return {
    movement, silence, setEnabled,
    inspect: () => ({ enabled, loading, loaded: Boolean(buffer), fetched, error, starts,
      activeSources: source ? 1 : 0, targetGain, smoothSpeed, rawSpeed,
      playbackRate: source?.playbackRate.value ?? 1, contextState: context?.state ?? 'uncreated',
      loopDuration: buffer?.duration ?? 0, settings: { ...settings } }),
    dispose() {
      if (disposed) return;
      disposed = true; enabled = false; generation++;
      clearInterval(timer); clearTimeout(fadeStopTimer);
      button?.removeEventListener('click', onClick);
      ownerDocument?.removeEventListener('visibilitychange', onVisibility);
      stopSource(); master?.disconnect();
      if (context && context.state !== 'closed') context.close().catch(() => {});
      paint();
    }
  };
}

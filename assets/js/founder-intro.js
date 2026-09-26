(() => {
  const section = document.querySelector('.founder-film-intro');
  if (!section) return;

  const video = section.querySelector('video');
  const toggle = section.querySelector('[data-founder-film-toggle]');
  const status = section.querySelector('[data-founder-film-status]');
  const progress = section.querySelector('[data-founder-film-progress]');
  if (!video || !toggle || !status || !progress) return;

  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  let attempted = false;

  toggle.hidden = false;

  const setStatus = (message, { visible = false } = {}) => {
    status.textContent = message;
    status.hidden = !message;
    if (visible && message) status.dataset.visible = 'true';
    else delete status.dataset.visible;
  };

  const updateProgress = () => {
    const duration = video.duration;
    const fraction = Number.isFinite(duration) && duration > 0
      ? Math.min(1, Math.max(0, video.currentTime / duration))
      : 0;
    progress.style.transform = `scaleX(${fraction})`;
  };

  const play = () => {
    if (video.ended) video.currentTime = 0;
    const result = video.play();
    if (result && typeof result.catch === 'function') {
      result.catch(() => {
        toggle.textContent = 'Play intro';
        setStatus('Autoplay is unavailable. Choose Play intro to start, or skip to the portrait below.', { visible: true });
      });
    }
  };

  toggle.addEventListener('click', () => {
    if (video.paused || video.ended) {
      play();
    } else {
      video.pause();
    }
  });

  video.addEventListener('playing', () => {
    toggle.textContent = 'Pause intro';
    setStatus('');
  });

  video.addEventListener('pause', () => {
    if (!video.ended) toggle.textContent = 'Resume intro';
  });

  video.addEventListener('timeupdate', updateProgress);
  video.addEventListener('ended', () => {
    toggle.textContent = 'Replay intro';
    updateProgress();
    setStatus('The intro has ended. The interactive portrait follows below.');
  });

  video.addEventListener('error', () => {
    toggle.hidden = true;
    setStatus('The opening film is unavailable. Skip to the portrait below.', { visible: true });
  });

  document.addEventListener('visibilitychange', () => {
    if (document.hidden && !video.paused) video.pause();
  });

  if (reducedMotion) {
    toggle.textContent = 'Play intro';
    setStatus('The opening film is paused because reduced motion is enabled. Play it here or continue below.', { visible: true });
    return;
  }

  const attemptPlayback = () => {
    if (attempted || !section.isConnected) return;
    attempted = true;
    play();
  };

  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      const entry = entries[0];
      if (!entry) return;
      if (entry.isIntersecting && entry.intersectionRatio >= 0.2) {
        attemptPlayback();
      } else if (attempted && !video.paused) {
        video.pause();
      }
    }, { threshold: [0, 0.2] });
    observer.observe(section);
  } else {
    attemptPlayback();
  }
})();

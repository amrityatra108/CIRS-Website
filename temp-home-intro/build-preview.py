from pathlib import Path
import re
root=Path.cwd(); out=root/'temp-home-intro'
html=(root/'index.html').read_text(encoding='utf-8')
html=html.replace('<head>','<head>\n<base href="../">\n<meta name="robots" content="noindex,nofollow">')
html=re.sub(r'<div class="curtain" id="curtain".*?</div>', '', html, count=1, flags=re.S)
html=re.sub(r'<video class="hero__video".*?</video>', '<img class="hero__still" src="temp-home-intro/media/final-frame.png" alt="" width="1672" height="940" fetchpriority="high">', html, count=1, flags=re.S)
html=html.replace('</head>', '''<link rel="stylesheet" href="temp-home-intro/intro.css">
<script>
try {
  var nav = performance.getEntriesByType('navigation')[0];
  if (!matchMedia('(prefers-reduced-motion: reduce)').matches && !(nav && nav.type === 'back_forward') && !sessionStorage.getItem('cirsHomeIntroSeen')) document.documentElement.classList.add('intro-active');
} catch (_) {}
window.setTimeout(function () {
 if (window.cirsTempFinish) window.cirsTempFinish('watchdog');
 else document.documentElement.classList.remove('intro-active');
}, 10000);
</script>
</head>''')
html=html.replace('<body>', '''<body>
<div class="home-intro" data-home-intro
     data-webm="temp-home-intro/media/cirs-campus-intro.webm"
     data-mp4="temp-home-intro/media/cirs-campus-intro.mp4"
     data-mobile-webm="temp-home-intro/media/cirs-campus-intro-mobile.webm"
     data-mobile-mp4="temp-home-intro/media/cirs-campus-intro-mobile.mp4">
  <img class="home-intro__poster" src="temp-home-intro/media/intro-poster.jpg" alt="" aria-hidden="true">
  <video class="home-intro__video" muted playsinline preload="auto" aria-hidden="true" hidden></video>
  <div class="home-intro__wash" aria-hidden="true"></div>
  <button class="home-intro__skip" type="button">Skip intro</button>
</div>
<button class="preview-replay" type="button" onclick="try{sessionStorage.removeItem('cirsHomeIntroSeen')}catch(_){} location.reload()">Replay preview</button>''')
html=html.replace('assets/js/cirs.js?b=46','temp-home-intro/cirs-preview.js').replace('<script src="assets/vendor/gsap', '<script src="temp-home-intro/intro.js" defer></script>\n<script src="assets/vendor/gsap',1)
(out/'index.html').write_text(html,encoding='utf-8')
js=(root/'assets/js/cirs.js').read_text(encoding='utf-8')
a=js.index('    var curtain =',js.index('  function playIntro(done)'))
b=js.index('\n  /* =====',a)
js=js[:a]+'''    window.cirsTempIntro(done, lenis);
  }
''' +js[b:]
js=js.replace('if (!$("#curtain")) { heroParallax(); return; }','if (!document.documentElement.classList.contains("intro-active")) { heroParallax(); return; }')
js=js.replace('  function heroParallax() {','  function heroParallax() {\n    return; // Temporary still hero: keep identical framing through handoff.')
(out/'cirs-preview.js').write_text(js,encoding='utf-8')
print('Generated isolated preview HTML and interaction-script snapshot.')

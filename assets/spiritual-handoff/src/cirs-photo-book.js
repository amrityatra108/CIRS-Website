/* The spiral's small, progressively loaded record of the seventeen practices. */
(() => {
  'use strict';

  const chapters = window.CIRS_CHAPTERS;
  const stage = document.querySelector('.stage');
  if (!stage || !Array.isArray(chapters) || chapters.length !== 17) return;

  const book = document.createElement('figure');
  book.className = 'practice-book';
  book.setAttribute('aria-label', 'Photographs of the seventeen practices');
  book.innerHTML = '<div class="practice-book-heading"><span>THE LIVING PRACTICE</span><span class="practice-book-number">01 / 17</span></div><div class="practice-book-image"></div><figcaption class="practice-book-caption">Spiritual Classes</figcaption>';
  stage.append(book);

  const imageHolder = book.querySelector('.practice-book-image');
  const caption = book.querySelector('.practice-book-caption');
  const number = book.querySelector('.practice-book-number');
  const prepared = new Map();
  let current = -1;
  let request = 0;

  function imageFor(index) {
    if (index < 0 || index >= chapters.length) return null;
    if (prepared.has(index)) return prepared.get(index);
    const image = new Image();
    image.decoding = 'async';
    image.alt = `Practice photograph for ${chapters[index].title}`;
    // Uploads 13 and 17 repeat uploads 6 and 14; share the same download.
    const photoNumber = { 12: 6, 16: 14 }[index] || index + 1;
    image.src = `assets/practice-photos/practice-${String(photoNumber).padStart(2, '0')}.webp`;
    const ready = image.decode().then(() => image).catch(() => null);
    const entry = { image, ready };
    prepared.set(index, entry);
    return entry;
  }

  async function show(index) {
    index = Math.max(0, Math.min(chapters.length - 1, Math.trunc(index)));
    if (index === current) return;
    const token = ++request;
    const entry = imageFor(index);
    const image = await entry.ready;
    if (token !== request || !image) return;

    imageHolder.replaceChildren(image);
    current = index;
    caption.textContent = chapters[index].title;
    number.textContent = `${String(index + 1).padStart(2, '0')} / 17`;

    // Only the visible image and its immediate neighbours are decoded in advance.
    const keep = new Set([index - 1, index, index + 1]);
    for (const cached of prepared.keys()) if (!keep.has(cached)) prepared.delete(cached);
    imageFor(index - 1);
    imageFor(index + 1);
  }

  window.addEventListener('cirs:activechapter', event => {
    const index = event.detail?.index;
    if (Number.isInteger(index)) show(index);
  });
  show(0);
})();

const test = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const source = fs.readFileSync(require('node:path').join(__dirname, '../assets/js/media-lifecycle.js'), 'utf8');
function setup() {
  const doc = new EventTarget(); doc.hidden = false; doc.querySelectorAll = () => [];
  const win = new EventTarget();
  const motion = new EventTarget(); motion.matches = false;
  let observer;
  class IO { constructor(cb) { observer = cb; } observe() {} }
  vm.runInNewContext(source, { document: doc, window: win, matchMedia: () => motion, IntersectionObserver: IO, isFinite });
  const video = new EventTarget();
  Object.assign(video, { readyState: 1, duration: 10, seeking: false, paused: true, ended: false, writes: [], plays: 0, removeAttribute() {} });
  let time = 0;
  Object.defineProperty(video, 'currentTime', { get: () => time, set: t => { video.writes.push(t); time = t; video.seeking = true; } });
  video.finishSeek = () => { video.seeking = false; video.dispatchEvent(new Event('seeked')); };
  video.play = () => { video.plays++; video.paused = false; video.dispatchEvent(new Event('play')); return Promise.resolve(); };
  video.pause = () => { if (!video.paused) { video.paused = true; video.dispatchEvent(new Event('pause')); } };
  return { video, doc, win, motion, api: win.CIRSMedia, visible: value => observer([{isIntersecting:value}]) };
}
test('seeking coalesces bursts and finishes at the newest target, including reverse', () => {
  const {api,video}=setup(), s=api.createSeeker(video);
  s.seek(8);s.seek(2);s.seek(4);assert.deepEqual(video.writes,[8]);
  video.finishSeek();assert.deepEqual(video.writes,[8,4]);video.finishSeek();assert.equal(video.seeking,false);
});
test('metadata arriving late preserves requested frame and avoids exact duration', () => {
  const {api,video}=setup();video.readyState=0;const s=api.createSeeker(video);s.seek(20);assert.equal(video.writes.length,0);
  video.readyState=1;video.dispatchEvent(new Event('loadedmetadata'));assert.equal(video.writes[0],9.97);
});
test('a disabled seeker does not reclaim native playback on later media events', () => {
  const {api,video}=setup(), s=api.createSeeker(video);s.seek(3);s.seek(8);s.enable(false);video.finishSeek();s.enable(true);assert.deepEqual(video.writes,[3]);
});
test('background seeking waits until the document becomes visible', () => {
  const {api,video,doc}=setup(), s=api.createSeeker(video);doc.hidden=true;s.seek(5);assert.equal(video.writes.length,0);
  doc.hidden=false;doc.dispatchEvent(new Event('visibilitychange'));assert.deepEqual(video.writes,[5]);
});
test('offscreen playback pauses and resumes only if it was playing', () => {
  const {api,video,visible}=setup();api.manage(video);video.play();visible(false);assert.equal(video.paused,true);visible(true);assert.equal(video.paused,false);
  video.pause();const plays=video.plays;visible(false);visible(true);assert.equal(video.plays,plays);
});
test('hidden tabs pause and rejected late play cannot run in the background', () => {
  const {api,video,doc}=setup();api.manage(video);video.play();doc.hidden=true;doc.dispatchEvent(new Event('visibilitychange'));assert.equal(video.paused,true);
  video.play();assert.equal(video.paused,true);doc.hidden=false;doc.dispatchEvent(new Event('visibilitychange'));assert.equal(video.paused,false);
});
test('reduced motion and explicit ownership changes cancel automatic resume', () => {
  const {api,video,visible,motion}=setup();const m=api.manage(video);video.play();visible(false);m.forget();visible(true);assert.equal(video.paused,true);
  video.play();motion.matches=true;motion.dispatchEvent(new Event('change'));visible(false);visible(true);assert.equal(video.paused,true);
});
test('page lifecycle pauses media and a single manager owns each video', () => {
  const {api,video,win}=setup();assert.equal(api.manage(video),api.manage(video));video.play();win.dispatchEvent(new Event('pagehide'));assert.equal(video.paused,true);win.dispatchEvent(new Event('pageshow'));assert.equal(video.paused,false);
});

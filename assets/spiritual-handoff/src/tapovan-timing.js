// Pure, seekable journey evaluation. The film is sampled at its actual PTS;
// this controller never synthesises motion between those photographic frames.
export const TIMES = Object.freeze([.04, 2.20, 4.40, 6.50, 8.80, 11.25, 14.50]);
export const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
export const mix = (a, b, t) => a + (b - a) * t;
export const ease = t => (t = clamp(t), t * t * (3 - 2 * t));
const LAST = TIMES.length - 1;
const PAN = [[0,.60],[2.3,.62],[3.45,.95],[4.5,.63],[5.55,.55],[6.6,.33],[8.6,.31],[10.5,.62],[11.7,.53],[12.6,.35],[13.5,.34],[14.5,.51],[15.140125,.48]];
export function timeForProgress(progress) {
  const position = clamp(progress) * LAST, low = Math.min(LAST - 1, Math.floor(position));
  return mix(TIMES[low], TIMES[low + 1], position - low);
}
export function progressForTime(time) {
  for (let i = 0; i < LAST; i++) if (time <= TIMES[i + 1])
    return (i + clamp((time - TIMES[i]) / (TIMES[i + 1] - TIMES[i]))) / LAST;
  return 1;
}
export function frameIndexForTime(time, pts) {
  let low = 0, high = pts.length - 1;
  while (low < high) { const middle = Math.ceil((low + high) / 2); if (pts[middle] <= time + 1e-6) low = middle; else high = middle - 1; }
  return low;
}
export function targetFrame(time, stream) {
  const index = frameIndexForTime(time, stream.pts), start = stream.pts[index];
  const end = stream.pts[index + 1] ?? stream.duration;
  // Seek just inside the selected presentation interval, avoiding floating
  // point boundary rounding in browser media engines. Not frame interpolation.
  return { index, pts: start, time: start + Math.min(.006, (end - start) * .15) };
}
export function captionPose(time, index) {
  const arrival = TIMES[index + 1];
  const enter = ease((time - (arrival - .42)) / .40);
  const exit = index === LAST - 1 ? 0 : ease((time - (TIMES[index + 2] - .64)) / .34);
  return { opacity: enter * (1 - exit), y: 14 * (1 - enter) - 8 * exit };
}
export function mobilePan(time) {
  for (let i = 0; i < PAN.length - 1; i++) {
    const [start, from] = PAN[i], [end, to] = PAN[i + 1];
    if (time <= end) return mix(from, to, ease((time - start) / (end - start)));
  }
  return PAN.at(-1)[1];
}

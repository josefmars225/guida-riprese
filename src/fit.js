// Full screen, no scrolling: the board takes the phone's proportions (at least 390 wide, the guide's design width) and
// is scaled to fill it; when a screen's content is taller than the space, the scale shrinks just enough for it to fit.
function natural() {
  const scr = document.querySelector('#board .scr');
  if (!scr) return 0;
  const h = scr.style.height; scr.style.height = 'auto';
  const n = scr.scrollHeight; scr.style.height = h;
  return n;
}
function fit() {
  const de = document.documentElement, cs = getComputedStyle(de);
  const vw = de.clientWidth, vh = window.innerHeight - parseFloat(cs.paddingTop) - parseFloat(cs.paddingBottom);
  const board = $('#board'), stage = $('#stage');
  let s = Math.min(vw / 390, 1.3);
  for (let k = 0; k < 2; k++) {
    const w = Math.min(vw / s, 480), h = vh / s;
    board.style.width = w + 'px'; board.style.height = h + 'px';
    board.style.setProperty('--bw', w + 'px'); board.style.setProperty('--bh', h + 'px');
    const need = Math.max(600, natural() + 24);
    if (h >= need) break;
    s = vh / need;
  }
  const w = Math.min(vw / s, 480), h = vh / s;
  board.style.width = w + 'px'; board.style.height = h + 'px';
  board.style.setProperty('--bw', w + 'px'); board.style.setProperty('--bh', h + 'px');
  board.style.transform = `scale(${s})`;
  stage.style.width = w * s + 'px'; stage.style.height = vh + 'px';
}
let fitQueued = false;
const refit = () => { if (!fitQueued) { fitQueued = true; requestAnimationFrame(() => { fitQueued = false; fit(); }); } };
window.addEventListener('resize', refit);

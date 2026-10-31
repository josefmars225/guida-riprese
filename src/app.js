// ---- The guide for clients: each step is filmed with the Camera app; the guide sends every video by itself
// to the owner's Google Drive (through the Apps Script in apps-script/), while the client goes on with the next step. ----
const PROPS = __PROPS__;
const CFG = window.GUIDA_CONFIG || {};
const $ = (s) => document.querySelector(s);
const esc = (t) => String(t == null ? '' : t).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const AREA = (k) => ROOMS.includes(k) ? 'Ambiente' : STAIRS.includes(k) ? 'Scalinata' : 'Corridoio';
const fmtMB = (b) => (b / 1048576).toLocaleString('it-IT', { maximumFractionDigits: 0 }) + ' MB';
let comp = null;

__FIT__

// ---------- the property: from the link (?casa=Via Roma 12), otherwise asked once ----------
const fromLink = new URLSearchParams(location.search).get('casa');
function casa() {
  if (fromLink && fromLink.trim()) return fromLink.trim();
  try { return localStorage.getItem('guida-casa') || ''; } catch (_) { return ''; }
}
function setCasa(v) { try { localStorage.setItem('guida-casa', v.trim()); } catch (_) {} }

// ---------- sending: one video after the other, in 8 MB pieces, picking up again after a dropped connection ----------
const PIECE = 8 * 1024 * 1024;   // a multiple of 256 KiB, as Drive asks
const Q = [];
let busy = false, lock = null;
const pending = () => Q.filter((x) => x.state !== 'ok');
async function call(action, body) {
  const r = await fetch(CFG.scriptUrl, { method: 'POST', body: JSON.stringify(Object.assign({ action }, body)) });
  const j = await r.json();
  if (!j.ok) throw new Error(j.error || 'risposta non valida');
  return j;
}
const wait = (ms) => new Promise((r) => setTimeout(r, ms));
// The phone may close the page while the client is in the Camera app: videos not yet in Drive are kept in the
// browser's own storage (the file once, the progress after every piece) and carry on when the page comes back.
const STORE = (() => {
  let dbp = null;
  const open = () => dbp || (dbp = new Promise((res, rej) => {
    const r = indexedDB.open('guida-invii', 1);
    r.onupgradeneeded = () => { r.result.createObjectStore('meta', { keyPath: 'id' }); r.result.createObjectStore('file'); };
    r.onsuccess = () => res(r.result); r.onerror = () => rej(r.error);
  }));
  const meta = (it) => ({ id: it.id, name: it.name, casa: it.casa, type: it.type, size: it.size, sent: it.sent, location: it.location || null });
  const write = (stores, fn) => open().then((db) => new Promise((res, rej) => {
    const t = db.transaction(stores, 'readwrite'); fn(t); t.oncomplete = () => res(); t.onerror = t.onabort = () => rej(t.error);
  }));
  return {
    add: (it) => write(['meta', 'file'], (t) => { t.objectStore('file').put(it.file, it.id); t.objectStore('meta').put(meta(it)); }),
    save: (it) => write(['meta'], (t) => t.objectStore('meta').put(meta(it))),
    drop: (id) => write(['meta', 'file'], (t) => { t.objectStore('meta').delete(id); t.objectStore('file').delete(id); }),
    all: () => open().then((db) => new Promise((res, rej) => {
      const t = db.transaction(['meta', 'file'], 'readonly'), out = [], m = t.objectStore('meta').getAll();
      m.onsuccess = () => m.result.forEach((x) => { const g = t.objectStore('file').get(x.id); g.onsuccess = () => { if (g.result) out.push(Object.assign(x, { file: g.result })); }; });
      t.oncomplete = () => res(out); t.onerror = () => rej(t.error);
    }))
  };
})();
async function sendOne(it) {
  if (it.resumed && it.location) {
    // back after the page was closed: ask Drive how much of this video it already has
    it.resumed = false;
    try {
      const q = await fetch(it.location, { method: 'PUT', headers: { 'Content-Range': `bytes */${it.size}` } });
      if (q.ok) { it.sent = it.size; return; }
      if (q.status === 308) { const rg = q.headers.get('Range'); it.sent = rg ? Number(rg.split('-')[1]) + 1 : 0; }
      else { it.location = null; it.sent = 0; }
    } catch (_) {}
  }
  if (!it.location) { it.location = (await call('start', { casa: it.casa, name: it.name, type: it.type, size: it.size, origin: location.origin })).location; it.sent = 0; STORE.save(it).catch(() => {}); }
  const size = it.size;
  while (it.sent < size) {
    const end = Math.min(it.sent + PIECE, size);
    let res = null;
    for (let tryN = 0; tryN < 6 && !res; tryN++) {
      try {
        const r = await fetch(it.location, { method: 'PUT', headers: { 'Content-Range': `bytes ${it.sent}-${end - 1}/${size}` }, body: it.file.slice(it.sent, end) });
        if (r.ok || r.status === 308) res = r;
        else if (r.status === 404 || r.status === 410) { it.location = null; it.sent = 0; throw new Error('sessione scaduta'); }
        else await wait(1500 * (tryN + 1));
      } catch (e) {
        if (!it.location) throw e;
        await wait(1500 * (tryN + 1));
        // where did Drive get to? if it says, carry on from there
        try {
          const q = await fetch(it.location, { method: 'PUT', headers: { 'Content-Range': `bytes */${size}` } });
          if (q.ok) { it.sent = size; res = q; break; }
          const rg = q.headers.get('Range');
          if (rg) { it.sent = Number(rg.split('-')[1]) + 1; status(); break; }
        } catch (_) {}
      }
    }
    if (it.sent >= size) break;
    if (!res) throw new Error('connessione');
    const rg = res.headers.get('Range');
    it.sent = res.ok ? size : rg ? Number(rg.split('-')[1]) + 1 : end;
    STORE.save(it).catch(() => {});
    status();
  }
}
async function pump() {
  if (busy || !CFG.scriptUrl) return;
  busy = true; awake(true);
  let it;
  while ((it = Q.find((x) => x.state === 'wait'))) {
    it.state = 'send'; status();
    try { await sendOne(it); it.state = 'ok'; STORE.drop(it.id).catch(() => {}); }
    catch (_) { it.state = 'wait'; it.errors = (it.errors || 0) + 1; status(true); await wait(Math.min(30000, 4000 * it.errors)); if (!navigator.onLine) break; }
    status();
  }
  busy = false; awake(false); status();
}
window.addEventListener('online', pump);
window.addEventListener('beforeunload', (e) => { if (pending().length) { e.preventDefault(); e.returnValue = ''; } });
async function awake(on) {
  try { if (on && !lock && navigator.wakeLock) lock = await navigator.wakeLock.request('screen'); else if (!on && lock) { await lock.release(); lock = null; } } catch (_) {}
}
let hideT = null;
function status(trouble) {
  const el = $('#send'), p = pending();
  clearTimeout(hideT);
  if (!Q.length) { el.hidden = true; document.body.classList.remove('sending'); return; }
  el.hidden = false; document.body.classList.add('sending'); el.classList.toggle('ok', !p.length); el.classList.toggle('err', !!trouble && !navigator.onLine);
  if (!p.length) { $('#send-t').textContent = Q.length === 1 ? 'Video arrivato' : `Tutti i ${Q.length} video sono arrivati`; hideT = setTimeout(() => { el.hidden = true; document.body.classList.remove('sending'); }, 6000); return; }
  const tot = p.reduce((a, x) => a + x.size, 0), done = p.reduce((a, x) => a + x.sent, 0);
  const pct = tot ? Math.floor(done / tot * 100) : 0;
  $('#send-t').textContent = !navigator.onLine ? 'Invio in pausa: manca la connessione' : `Invio ${p.length === 1 ? 'del video' : `di ${p.length} video`} · ${pct}%`;
}
function enqueue(file, sc) {
  const steps = stepsOf(sc.key), st = steps[sc.i], ext = (file.name.match(/\.\w+$/) || ['.mp4'])[0].toLowerCase();
  const where = AREA(sc.key) + (sc.key === 'corridoio' ? '' : ' ' + SHAPES[sc.key].name);
  const name = `${where} · passo ${String(sc.i + 1).padStart(2, '0')} di ${steps.length} · ${st.title}${ext}`;
  const it = { id: Date.now().toString(36) + Math.random().toString(36).slice(2, 6), file, name, casa: casa() || 'Senza nome', type: file.type || 'video/mp4', size: file.size, sent: 0, state: 'wait' };
  Q.push(it);
  STORE.add(it).catch(() => {});
  status(); pump();
}

// ---------- the sheet ----------
const OV = { screen: null };
function sheet(html) { $('#sheet').className = 'sheet'; $('#sheet').innerHTML = html; $('#ov').hidden = false; }
function closeSheet() { $('#ov').hidden = true; $('#sheet').innerHTML = ''; OV.screen = null; saveState(); }
const KEEP = 'guida-stato:' + (fromLink || '');
function saveState() {
  try { const c = (comp && comp.state) || {}; sessionStorage.setItem(KEEP, JSON.stringify({ scr: c.scr || null, hist: c.hist || [], rec: OV.screen })); } catch (_) {}
}
function loadState() { try { return JSON.parse(sessionStorage.getItem(KEEP) || 'null'); } catch (_) { return null; } }
const X = '<button type="button" class="o-x" data-a="close" aria-label="Chiudi"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"></path></svg></button>';
const li = (n, t) => `<li style="display: grid; grid-template-columns: 30px 1fr; gap: 6px; padding: 10px 0; border-top: 1px solid var(--line); font-size: 15px; line-height: 1.45"><span style="font-family: var(--display); font-style: italic; font-size: 17px; color: var(--champ)">${n}</span><span>${t}</span></li>`;

// Registra: film the step with the Camera app, then one tap to pick it; the guide sends it and moves on.
function drawRec(err) {
  saveState();
  const sc = OV.screen, steps = stepsOf(sc.key), st = steps[sc.i], ask = !casa();
  sheet(`<div class="o-top"><div style="display: flex; flex-direction: column; gap: 8px"><span class="o-lab">${AREA(sc.key)} · passo ${sc.i + 1} di ${steps.length}</span><h2 class="o-h" id="ov-title">Registra con la <em>Fotocamera</em></h2></div>${X}</div>
    <ol style="list-style: none; margin: 0; padding: 0">
      ${li('i.', 'Apri l’app <strong>Fotocamera</strong>, modalità <strong>Video</strong>, <strong>4K</strong> e lente <strong>0,5×</strong>.')}
      ${li('ii.', esc(st.text))}
      ${li('iii.', 'Ferma la registrazione, torna qui, tocca <strong>Scegli il video</strong> e seleziona il video appena registrato.')}
      ${li('iv.', 'Nel menu tocca <strong>Libreria foto</strong> (o <strong>Raccolta fotografica</strong>), non la voce per fare un nuovo video.')}
    </ol>
    ${ask ? `<div style="display: flex; flex-direction: column; gap: 8px"><label class="o-lab" for="ov-casa" style="color: var(--soft)">Indirizzo dell’immobile</label><input class="o-in" id="ov-casa" autocomplete="street-address" placeholder="Es. Via Roma 12, Bologna"></div>` : ''}
    ${err ? `<p class="o-err">${esc(err)}</p>` : ''}
    ${CFG.scriptUrl ? '' : '<p class="o-err">L’invio dei video non è ancora collegato: per ora la guida va solo avanti.</p>'}
    <div class="o-row"><button type="button" class="o-btn p" data-a="pick">Scegli il video</button></div>`);
}
// The end: no uploading to do, only to wait for the videos still travelling.
function drawEnd() {
  const p = pending();
  sheet(`<div class="o-top"><div style="display: flex; flex-direction: column; gap: 8px"><span class="o-lab">Alla fine</span><h2 class="o-h" id="ov-title">${p.length ? 'Quasi <em>fatto</em>' : 'Grazie, <em>è tutto</em>'}</h2></div>${X}</div>
    <p class="o-p" style="color: var(--ink)">${p.length
      ? `Stiamo ancora mandando ${p.length === 1 ? 'un video' : p.length + ' video'} (${fmtMB(p.reduce((a, x) => a + x.size - x.sent, 0))}). Tieni aperta questa pagina, con il Wi-Fi se puoi, finché in alto compare «Tutti i video sono arrivati».`
      : Q.length ? `Abbiamo ricevuto tutti i ${Q.length} video. Puoi chiudere la pagina.` : 'Hai finito le riprese.'}</p>
    <div class="o-row"><button type="button" class="o-btn p" data-a="close">${p.length ? 'Va bene' : 'Chiudi'}</button></div>
    <button type="button" class="o-link" data-a="restart">Ricomincia la guida</button>`);
}
$('#gal').addEventListener('change', (e) => {
  const f = e.target.files && e.target.files[0], sc = OV.screen;
  if (!f || !sc) return;
  if (!/^video\//.test(f.type || 'video/')) { drawRec('Questo file non è un video: scegli il video del passo.'); return; }
  if (CFG.scriptUrl) enqueue(f, sc);
  closeSheet();
  if (comp) comp.nextStep({ type: 'step', key: sc.key, i: sc.i });
});
$('#sheet').addEventListener('click', (e) => {
  const b = e.target.closest('[data-a]'); if (!b) return;
  const a = b.dataset.a;
  if (a === 'close') closeSheet();
  if (a === 'restart') { closeSheet(); if (comp) comp.enter({ type: 'setup', i: 0 }, []); }
  if (a === 'pick') {
    const c = $('#ov-casa');
    if (c) { if (!c.value.trim()) { drawRec('Scrivi l’indirizzo dell’immobile: serve per sapere di che casa sono i video.'); return; } setCasa(c.value); }
    $('#gal').value = ''; $('#gal').click();
  }
});
$('#ov').addEventListener('click', (e) => { if (e.target === $('#ov')) closeSheet(); });
document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && !$('#ov').hidden) closeSheet(); });

// ---------- hooks into the guide ----------
const _enter = Component.prototype.enter;
Component.prototype.enter = function (screen, h) { _enter.call(this, screen, h); saveState(); };
const _go = Component.prototype.go;
Component.prototype.go = function (screen, push) {
  if (screen && screen.type === 'rec') { comp = this; OV.screen = screen; drawRec(); return; }
  if (screen && screen.type === 'perm') return _go.call(this, { type: 'space' }, push);   // the Camera app asks for its own permissions
  if (screen && screen.type === 'end') { comp = this; drawEnd(); return; }
  return _go.call(this, screen, push);
};
const _fb = Component.prototype.feedbackVals;
Component.prototype.feedbackVals = function () {
  const v = _fb.call(this), fb = (this.state && this.state.fb) || {}, send = v.send;
  v.send = () => {
    if (fb.rating && !fb.sent && CFG.scriptUrl) call('feedback', { rating: fb.rating, text: String(fb.text || '').slice(0, 1000), casa: casa() }).catch((e) => console.warn('feedback non inviato:', e));
    send();
  };
  return v;
};

// ---------- the music is background music: on iPhone it then follows the silent switch, and never stops other apps' audio ----------
try { if (navigator.audioSession) navigator.audioSession.type = 'ambient'; } catch (_) {}

// ---------- leaving the browser: the music stops (the client is going to the Camera app) and comes back after ----------
document.addEventListener('visibilitychange', () => {
  const a = window.__guidaMusica, v = document.querySelector('#board .prato-video');
  if (document.hidden) { if (a && !a.paused) { a.pause(); window.__guidaPausa = true; } if (v) v.pause(); return; }
  if (v && v.style.visibility !== 'hidden') v.play().catch(() => {});
  if (window.__guidaPausa && comp && comp.musicOn()) comp.startMusic(comp.shared().time);
  window.__guidaPausa = false;
});

// ---------- the meadow: with Low Power Mode the phone refuses to start videos by themselves, and shows its own
// play button; then the still photo of the meadow stays, and the wind comes back at the first touch ----------
function meadow() {
  const v = document.querySelector('#board .prato-video');
  if (!v) return;
  v.muted = true; v.playsInline = true;
  const p = v.play();
  if (p && p.catch) p.catch(() => {
    v.style.visibility = 'hidden';
    const wake = () => v.play().then(() => { v.style.visibility = ''; }).catch(() => {});
    document.addEventListener('pointerdown', wake, { once: true, capture: true });
  });
}

// ---------- start ----------
comp = DC.mount($('#board'), $('#dc-tpl'), Component, PROPS);
meadow();
const was = loadState();
if (was && was.scr) {
  comp.enter(was.scr, was.hist || []);
  if (was.rec) { OV.screen = was.rec; drawRec(); }
}
STORE.all().then((items) => {
  if (!items.length) return;
  items.forEach((x) => Q.push(Object.assign(x, { state: 'wait', resumed: true })));
  status(); pump();
}).catch(() => {});
fit();
new MutationObserver(refit).observe($('#board'), { childList: true, subtree: true });
if (document.fonts && document.fonts.ready) document.fonts.ready.then(refit);

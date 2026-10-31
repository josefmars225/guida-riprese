# Second batch: "Entra registrando" and the stumbling moments (permission, denied, phone check, upload paused, resume).
# Reuses the builder of the first batch so every screen shares the same system. Run from the canvas project folder.
import importlib.util

spec = importlib.util.spec_from_file_location("b", "../../scripts/build_screens.py")
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)

ICON = {
    "camera": '<path d="M4 8h3l2-2.5h6L17 8h3v11H4z"></path><circle cx="12" cy="13.5" r="3.5"></circle>',
    "mic": '<rect x="9" y="3.5" width="6" height="11" rx="3"></rect><path d="M5.5 11.5a6.5 6.5 0 0 0 13 0M12 18v3"></path>',
    "memory": '<rect x="5" y="3.5" width="14" height="17" rx="2"></rect><path d="M9 7.5h6M9 11h6"></path>',
    "battery": '<rect x="3" y="8" width="16" height="9" rx="2"></rect><path d="M21 11v3"></path><path d="M6 11v3" stroke-width="2.4"></path>',
    "wifi": '<path d="M3 9a14 14 0 0 1 18 0M6.5 12.5a9 9 0 0 1 11 0M10 16a4 4 0 0 1 4 0M4 4l16 16"></path>',
    "apple": '<rect x="7" y="2.5" width="10" height="19" rx="2.5"></rect><path d="M11 18.5h2"></path>',
    "android": '<rect x="6" y="2.5" width="12" height="19" rx="2"></rect><path d="M10 5h4"></path>',
    "list": '<path d="M5 7h14M5 12h14M5 17h9"></path>',
}
def icon(name):
    return f'<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICON[name]}</svg>'

EXTRA_CSS = """/* Rows inside a glass card: icon, title, one line of help. */
.irow{display:grid;grid-template-columns:34px 1fr;gap:10px;padding:13px 0}
.irow+.irow{border-top:1px solid rgba(243,235,221,.14)}
.irow-i{color:#E6D3B0;padding-top:1px}
.irow-t{font-size:15px;font-weight:600}
.irow-p{font-size:13px;line-height:1.5;color:rgba(243,235,221,.92)}
.bar-fill{transform-origin:left center}
.anim .bar-fill{animation:seg 1.1s cubic-bezier(.22,1,.36,1) var(--d,0ms) backwards}"""

def irow(ic, title, text, extra=""):
    return f'''          <div class="irow">
            <span class="irow-i">{icon(ic)}</span>
            <span style="display: flex; flex-direction: column; gap: 4px"><span class="irow-t">{title}</span><span class="irow-p">{text}</span>{extra}</span>
          </div>'''

def meter(pct, color, d=1000):
    return (f'<span aria-hidden="true" style="margin-top: 6px; height: 3px; border-radius: 2px; background: rgba(243,235,221,.25); overflow: hidden">'
            f'<span class="bar-fill" style="--d: {d}ms; display: block; width: {pct}%; height: 100%; background: {color}"></span></span>')

def card(key, d, inner, suono, mt=20, pad="6px 20px"):
    return f'''    <div class="posa l" style="--d: {d}ms; margin-top: {mt}px">
      <section ref="{{{{ {key}.ref }}}}" data-suono="{suono}" class="lg" style="border-radius: 22px; padding: {pad}; --h: {{{{{key}.h}}}}">
        {b.glass_layers(key)}
        <div class="lg-c">
{inner}
        </div>
      </section>
    </div>'''

def para(text, d, suono=None, mt=14, size=15):
    s = f' data-suono="{suono}"' if suono else ""
    return f'''    <div class="posa" style="--d: {d}ms; margin-top: {mt}px">
      <p{s} style="margin: 0; font-size: {size}px; line-height: 1.55; color: #F3EBDD; max-width: 34ch">{text}</p>
    </div>'''

def nav(back_href, back_label, back_d, primary_href, primary_label, prim_d, rec=False, suono=4):
    dot = b.REC_DOT if rec else ""
    s = f' data-suono="{suono}"' if suono else ""
    return f'''    <nav style="margin-top: auto; display: flex; gap: 10px">
{b.back_btn(back_href, back_d, back_label)}
      <div class="posa" style="--d: {prim_d}ms; flex: 2; display: flex">
        <a href="{primary_href}"{s} class="btn btn-p" style="flex: 1">{dot}{primary_label}</a>
      </div>
    </nav>'''

OPEN = '  <div style="position: relative; height: 100%; box-sizing: border-box; padding: 54px 20px 34px; display: flex; flex-direction: column">'
CLOSE = "  </div>"
STD = {"snd": "round", "inb": "pill", "card": "card", "back": "pill"}

# ---------------------------------------------------------------- Entra registrando (Ogni spazio 1/4)
ENTRA_SVG = b.svg("Pianta: parti dal corridoio due passi prima della porta, avvii la registrazione, attraversi la porta camminando piano e continui dentro la stanza.",
    f'<rect x="10" y="10" width="300" height="104" rx="6" {b.WALL}></rect><rect x="10" y="130" width="300" height="50" rx="6" fill="rgba(42,47,28,.55)" stroke="rgba(243,235,221,.7)" stroke-width="1.2"></rect>'
    f'<rect x="138" y="110" width="44" height="24" {b.DOOR}></rect>'
    + b.lbl(60, 30, "LA STANZA") + b.lbl(258, 168, "FUORI")
    + b.route("routeEntra", [(160, 166), (160, 52)])
    + '<path d="M155 92l5-6 5 6" fill="none" stroke="#D9C29A" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"></path>'
    + b.lbl(212, 158, "AVVIA QUI") + b.lbl(220, 56, "CONTINUA DENTRO")
    + b.pt(1, 160, 162) + b.pt(2, 160, 52, False))
entra = OPEN + f'''
{b.header()}
{b.meta("Ogni spazio · Spazio 2", 1, 4, 1)}
{b.kicker("Uno spazio: ogni parte separata da una porta")}
{b.title_lines("Da fuori,", "entra registrando", 200, 310)}
{b.FIG_OPEN.replace("@D@", "450").replace("@MT@", "20")}
{ENTRA_SVG}
          <p style="margin: 10px 0 0; font-size: 13px; line-height: 1.45">Avvia due passi prima della porta, attraversala piano e continua dentro.</p>
{b.FIG_CLOSE}
{b.actions(["Telefono davanti a te, all’altezza degli occhi.", "Da qui non fermare più fino all’uscita."], 500)}
    <nav style="margin-top: auto; display: flex; gap: 10px">
{b.back_btn("Permesso.dc.html", 560)}
      <div class="posa" style="--d: 590ms; flex: 2; display: flex">
        <a href="Stanza.dc.html" data-suono="4" class="btn btn-p" style="flex: 1">Avanti</a>
      </div>
    </nav>
''' + CLOSE

# ---------------------------------------------------------------- Permesso (camera and microphone)
permesso = OPEN + f'''
{b.header()}
{b.kicker("Un’ultima cosa", 100, 34)}
{b.title_lines("La fotocamera,", "qui dentro", 200, 310)}
{para("La guida registra al suo interno: niente app da aprire, niente andirivieni.", 450, 3)}
{card("card", 590, irow("camera", "Fotocamera", "Per riprendere gli spazi con la lente 0,5×.") + chr(10) + irow("mic", "Microfono", "Il telefono lo chiede insieme al video. Mentre registri la musica tace."), 4)}
{para("Il telefono mostrerà la sua richiesta: tocca «Consenti».", 650, None, 16, 13)}
{nav("Main.dc.html", "Indietro", 710, "Entra.dc.html", "Consenti", 760, suono=None)}
''' + CLOSE

# ---------------------------------------------------------------- Negato (permission denied)
negato = OPEN + f'''
{b.header()}
{b.kicker("Permesso non concesso", 100, 34)}
{b.title_lines("Senza fotocamera", "non si parte", 200, 310, size=42)}
{para("Si sistema in un minuto, poi riprendi da qui.", 380, None)}
{card("card", 450, irow("apple", "iPhone", "Tocca «aA» accanto all’indirizzo, poi «Impostazioni sito web»: Fotocamera e Microfono su «Consenti».") + chr(10) + irow("android", "Android", "Tocca l’icona accanto all’indirizzo, poi «Autorizzazioni»: attiva Fotocamera e Microfono."), 3)}
{nav("Main.dc.html", "Indietro", 560, "Permesso.dc.html", "Riprova", 590)}
''' + CLOSE

# ---------------------------------------------------------------- Telefono (memory and battery)
telefono = OPEN + f'''
{b.header()}
{b.kicker("Un controllo veloce", 100, 34)}
{b.title_lines("Il telefono", "ha bisogno di te", 200, 310)}
{card("card", 450, irow("memory", "Memoria quasi piena", "Liberi 1,2 GB: circa 4 minuti di video. Ne servono almeno 5 GB.", meter(24, "#E0583F")) + chr(10) + irow("battery", "Batteria al 18%", "Collega il caricatore o tienilo a portata di mano.", meter(18, "#D9C29A", 1100)), 3)}
{para("Puoi continuare lo stesso: se il telefono si spegne a metà, rifai solo lo spazio interrotto.", 520, None, 16, 13)}
{nav("Entra.dc.html", "Continua così", 560, "Entra.dc.html", "Ho sistemato", 590)}
''' + CLOSE

# ---------------------------------------------------------------- Interrotto (uploads paused)
ROW_CSS = """.row{display:grid;grid-template-columns:34px 1fr auto;gap:10px;align-items:center;padding:14px 0}
li.posa+li.posa{border-top:1px solid rgba(243,235,221,.16)}"""
def vrow(n, d, name, sub, status, dim=False, suono=None, extra=""):
    col = "rgba(243,235,221,.75)" if dim else "#E6D3B0"
    s = f' data-suono="{suono}"' if suono else ""
    return f'''          <li class="posa" style="--d: {d}ms; --tilt: -1.2deg">
            <span class="row"{s}>
              <span class="dsp" style="font-size: 18px; font-style: italic; color: {col}">{n}</span>
              <span style="display: flex; flex-direction: column; gap: 4px"><span style="font-size: 15px; font-weight: 600">{name}</span><span style="font-size: 12px; color: rgba(243,235,221,.86)">{sub}</span>{extra}</span>
              <span class="lab" style="font-size: 9px; color: {col}">{status}</span>
            </span>
          </li>'''
interrotto = OPEN + f'''
    <header style="display: flex; justify-content: space-between; align-items: center; height: 44px">
      <div class="posa" style="--d: 0ms">
        <a ref="{{{{ back.ref }}}}" href="Video.dc.html" class="lg lab" style="height: 44px; padding: 0 18px; border-radius: 999px; display: inline-flex; align-items: center; text-decoration: none; --h: {{{{back.h}}}}">
          {b.glass_layers("back")}
          <span class="lg-c" style="display: inline-flex; gap: 8px"><span aria-hidden="true">←</span>Guida</span>
        </a>
      </div>
      <div style="display: flex; gap: 14px; align-items: center">
        <div class="posa" style="--d: 50ms"><span class="dsp" style="display: block; font-size: 22px; letter-spacing: .14em; line-height: 1">RIPRESE</span></div>
        {b.SND_BTN}
      </div>
    </header>
    <div class="posa" style="--d: 110ms; margin-top: 34px">
      <p class="lab" style="margin: 0; color: #D9C29A; display: flex; align-items: center; gap: 8px">{icon("wifi")}Caricamento in pausa</p>
    </div>
{b.title_lines("Connessione", "persa", 200, 310)}
{para("I video sono al sicuro nel telefono. Il caricamento riprende da solo appena torna la rete.", 450, 3, 12)}
    <div class="posa l" style="--d: 590ms; margin-top: 20px">
      <section ref="{{{{ card.ref }}}}" data-suono="4" class="lg" style="padding: 4px 18px; border-radius: 22px; --h: {{{{card.h}}}}">
        {b.glass_layers("card")}
        <ul class="lg-c" style="list-style: none; margin: 0; padding: 0">
{vrow("01", 700, "Spazio 1", "2:58 · 0,9 GB", "Caricato")}
{vrow("02", 750, "Spazio 2", "In pausa a 64%", "In pausa", extra=meter(64, "rgba(217,194,154,.55)", 1300))}
{vrow("03", 800, "Spazio 3", "1:55 · 0,6 GB", "In attesa", dim=True)}
{vrow("04", 850, "Spazio 4", "4:10 · 1,3 GB", "In attesa", dim=True)}
        </ul>
      </section>
    </div>
    <div style="margin-top: auto; display: flex; flex-direction: column; gap: 12px">
      <div class="posa" style="--d: 900ms">
        <a href="Video.dc.html" class="btn btn-p" style="display: flex">Riprendi i caricamenti</a>
      </div>
      <div class="posa" style="--d: 950ms">
        <p style="margin: 0; text-align: center; font-size: 12px; line-height: 1.5; color: rgba(243,235,221,.85)">Meglio con il Wi-Fi. Lascia la guida aperta fino alla fine.</p>
      </div>
    </div>
''' + CLOSE

# ---------------------------------------------------------------- Riprendi (back after closing the guide)
riprendi = OPEN + f'''
{b.header()}
{b.kicker("La guida si è ricordata dove eri", 100, 34)}
{b.title_lines("Riprendiamo", "dallo spazio 3", 200, 310)}
{card("card", 450, irow("list", "2 spazi registrati", "Spazio 1 · 2:58 &#160;·&#160; Spazio 2 · 3:42") + chr(10) + irow("memory", "Tutti caricati", "Nessun video da rifare.", meter(100, "#D9C29A")), 3)}
{para("La casa deve essere com’era: stessa luce, niente spostato. Se qualcosa è cambiato, rifai gli spazi che lo mostrano.", 520, None, 16, 13)}
{nav("Main.dc.html", "Nuovo immobile", 560, "Entra.dc.html", "Riprendi", 590)}
''' + CLOSE

pages = {
    "Entra.dc.html": b.page("Ogni spazio — entra registrando", {"snd": "round", "inb": "pill", "fig": "card", "back": "pill"}, entra, extra_vals="\n      d0: '1450ms',"),
    "Permesso.dc.html": b.page("Prima di iniziare — fotocamera e microfono", STD, permesso, extra_css=EXTRA_CSS),
    "Negato.dc.html": b.page("Permesso non concesso", STD, negato, extra_css=EXTRA_CSS),
    "Telefono.dc.html": b.page("Un controllo veloce — memoria e batteria", STD, telefono, extra_css=EXTRA_CSS),
    "Interrotto.dc.html": b.page("Caricamento in pausa", {"snd": "round", "back": "pill", "card": "card"}, interrotto, extra_css=EXTRA_CSS + "\n" + ROW_CSS),
    "Riprendi.dc.html": b.page("Riprendiamo dallo spazio 3", STD, riprendi, extra_css=EXTRA_CSS),
}
if __name__ == "__main__":
    for name, html in pages.items():
        open(name, "w", encoding="utf-8").write(html)
        print(name, len(html))

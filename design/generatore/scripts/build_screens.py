# Builds the new guide screens from the shared parts of Stanza.dc.html (CSS, glass, motion, sound logic),
# so every screen carries the exact same system. Run from the canvas project folder.
import re

SRC = open("Stanza.dc.html", encoding="utf-8").read()
L = SRC.split("\n")

def lines(a, b):  # 1-based inclusive, as numbered in the file
    return "\n".join(L[a - 1:b])

HEAD_CSS = lines(15, 36)        # base, glass
SND_CSS = lines(38, 39)
PILL_CSS = lines(40, 45)
MOTION_CSS = lines(46, 73)      # posa, seg, rim, sheen, route, points, reduced motion
SCRIPT = SRC[SRC.index("class Component extends DCLogic {"):SRC.index("  renderVals() {")]
# Stanza carries its own shape-pill logic; the shared script must not.
SCRIPT = re.sub(r"  // Shape pills:.*?\n  }\n(?=  // Each glass piece)", "", SCRIPT, flags=re.S)

MAPS = {"card": ("/_blob/116c5dac2ab57a55619f3f6ee89ec668", 38), "pill": ("/_blob/a9ba74de8a60ba585f969e9af2a342a4", 26),
        "round": ("/_blob/7f937f9d5015902de39fec83b78470f3", 20), "sheet": ("/_blob/0143f76e6f83cd0590c0529f58c79692", 44)}

def filters(glass):
    out = []
    for key, kind in glass.items():
        href, scale = MAPS[kind]
        fid = "lg" + key[0].upper() + key[1:]
        out.append(f'''    <filter id="{fid}" filterUnits="userSpaceOnUse" x="0" y="0" width="{{{{{key}.w}}}}" height="{{{{{key}.h}}}}" color-interpolation-filters="sRGB">
      <feImage href="{href}" x="0" y="0" width="{{{{{key}.w}}}}" height="{{{{{key}.h}}}}" preserveAspectRatio="none" result="map"></feImage>
      <feDisplacementMap in="SourceGraphic" in2="map" scale="{scale}" xChannelSelector="R" yChannelSelector="G"></feDisplacementMap>
    </filter>''')
    return "\n".join(out)

def glass_layers(key):
    return (f'<span class="lg-refr f-{key}" aria-hidden="true"><span class="lg-img" style="left: {{{{{key}.l}}}}; top: {{{{{key}.t}}}}; '
            f'transform-origin: {{{{{key}.ox}}}} {{{{{key}.oy}}}}"></span></span>\n'
            f'          <span class="lg-tint" aria-hidden="true"></span>')

SND_BTN = '''<div class="posa" style="--d: 30ms">
          <button ref="{{ snd.ref }}" type="button" class="lg snd" aria-label="{{musicLabel}}" aria-pressed="{{musicPressed}}" onClick="{{ toggleMusic }}" style="--h: {{snd.h}}">
            ''' + glass_layers("snd") + '''
            <span class="lg-c" style="display: grid; place-items: center">
              <sc-if value="{{ music }}" hint-placeholder-val="{{ false }}"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 9.5h3.5L12 5.5v13l-4.5-4H4z"></path><path d="M15.5 9a4 4 0 0 1 0 6M18 6.5a7.5 7.5 0 0 1 0 11"></path></svg></sc-if>
              <sc-if value="{{ musicOff }}" hint-placeholder-val="{{ true }}"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 9.5h3.5L12 5.5v13l-4.5-4H4z"></path><path d="M16 9.5l5 5M21 9.5l-5 5"></path></svg></sc-if>
            </span>
          </button>
        </div>'''

LOGO = '''<div class="posa" style="--d: 0ms">
        <div style="display: flex; flex-direction: column; gap: 3px">
          <span class="lab" style="font-size: 8px; letter-spacing: .34em; color: rgba(243,235,221,.7)">Guida alle</span>
          <span class="dsp" style="font-size: 22px; letter-spacing: .14em; line-height: 1">RIPRESE</span>
        </div>
      </div>'''

INB_LINK = '''<div class="posa" style="--d: 50ms">
          <a ref="{{ inb.ref }}" href="InBreve.dc.html" class="lg" style="height: 44px; padding: 0 18px; border-radius: 999px; display: inline-flex; align-items: center; text-decoration: none; --h: {{inb.h}}">
            ''' + glass_layers("inb") + '''
            <span class="lg-c lab">In breve</span>
          </a>
        </div>'''

def header(right=None):
    right = right if right is not None else SND_BTN + "\n        " + INB_LINK
    return f'''    <header style="display: flex; justify-content: space-between; align-items: center">
      {LOGO}
      <div style="display: flex; gap: 8px">
        {right}
      </div>
    </header>'''

def meta(module, step, total, new_index, d=100):
    segs = []
    for i in range(1, total + 1):
        if i == new_index:
            segs.append('<span class="seg-new" style="--d: 520ms; height: 2px; background: #D9C29A"></span>')
        elif i < new_index:
            segs.append('<span style="height: 2px; background: #D9C29A"></span>')
        else:
            segs.append('<span style="height: 2px; background: rgba(243,235,221,.3)"></span>')
    segs = "\n          ".join(segs)
    return f'''    <div class="posa" style="--d: {d}ms; margin-top: 30px">
      <div style="display: flex; flex-direction: column; gap: 12px">
        <div style="display: flex; justify-content: space-between; align-items: baseline">
          <span class="lab" style="color: rgba(243,235,221,.78)">{module}</span>
          <span class="dsp" style="font-size: 15px; font-style: italic; color: #D9C29A">{step} / {total}</span>
        </div>
        <div aria-hidden="true" style="display: grid; grid-template-columns: repeat({total}, minmax(0, 1fr)); gap: 6px">
          {segs}
        </div>
      </div>
    </div>'''

def back_btn(href, d, label="Indietro"):
    return f'''      <div class="posa" style="--d: {d}ms; flex: 1; display: flex">
        <a ref="{{{{ back.ref }}}}" href="{href}" class="btn lg" style="flex: 1; --h: {{{{back.h}}}}">
          {glass_layers("back")}
          <span class="lg-c">{label}</span>
        </a>
      </div>'''

REC_DOT = '<span aria-hidden="true" style="width: 9px; height: 9px; border-radius: 50%; background: #C8452F; box-shadow: 0 0 0 3px rgba(200,69,47,.22)"></span>'

def page(title, glass, body, extra_css="", extra_vals="", extra_logic="", wide_pills=False):
    filter_classes = "".join(f".f-{k}{{filter:url(#lg{k[0].upper() + k[1:]})}}" for k in glass)
    css = "\n".join([HEAD_CSS, filter_classes, SND_CSS, PILL_CSS, extra_css, MOTION_CSS])
    glass_vals = ", ".join(f"{k}: this.glass('{k}')" for k in glass if k != "snd")
    script = SCRIPT.replace("  // Each glass piece shows the meadow", extra_logic + "  // Each glass piece shows the meadow") if extra_logic else SCRIPT
    return f'''<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<title>{title}</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="anonymous">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,300..700&amp;family=Bodoni+Moda:ital,opsz,wght@0,6..96,400..700;1,6..96,400..700&amp;family=GFS+Didot&amp;display=swap">
<style>
{css}
</style>
</helmet>
<div ref="{{{{ rootRef }}}}" class="prato {{{{animClass}}}}" style="position: relative; width: 390px; height: 844px; overflow: hidden; color: #F3EBDD; font-family: Archivo, system-ui, sans-serif; --display: {{{{displayFont}}}}">
  <svg aria-hidden="true" width="0" height="0" style="position: absolute">
{filters(glass)}
  </svg>
  <video class="prato-video" src="/_blob/a78189329319cf3af17d4e9383c05b28" autoplay="autoplay" muted="muted" loop="loop" playsinline="playsinline" preload="auto" aria-hidden="true"></video>
  <div aria-hidden="true" style="position: absolute; inset: 0; background: {{{{veilBg}}}}"></div>
{body}
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"display":{{"editor":"enum","options":["Bodoni Moda","GFS Didot"],"default":"Bodoni Moda","section":"Tipografia"}},"veil":{{"editor":"range","min":0.2,"max":0.8,"step":0.05,"default":0.45,"section":"Leggibilità"}},"animazioni":{{"editor":"boolean","default":true,"section":"Movimento"}},"$preview":{{"width":390,"height":844}}}}'>
{script}  renderVals() {{
    const display = this.props.display ?? 'Bodoni Moda';
    const v = this.props.veil ?? 0.45;
    const a = (x) => Math.max(0, Math.min(0.96, x)).toFixed(2);
    return {{
      rootRef: (el) => {{ this._root = el; }},
      animClass: (this.props.animazioni ?? true) ? 'anim' : '',
      snd: this.glass('snd'),
      music: this.musicOn(), musicOff: !this.musicOn(),
      musicPressed: String(this.musicOn()),
      musicLabel: this.musicOn() ? 'Spegni la musica' : 'Accendi la musica',
      toggleMusic: () => this.toggleMusic(),
      {glass_vals},{extra_vals}
      displayFont: '"' + display + '", "Bodoni Moda", Didot, serif',
      veilBg: 'linear-gradient(180deg, rgba(18,15,9,' + a(v) + ') 0%, rgba(18,15,9,0) 28%, rgba(18,15,9,0) 68%, rgba(18,15,9,' + a(v + 0.1) + ') 100%)'
    }};
  }}
}}
</script>
</body>
</html>
'''

def title_lines(a, b, d1, d2, size=44, s1=1, s2=2, mt=12):
    return f'''    <h1 class="dsp" style="margin: {mt}px 0 0; font-size: {size}px; line-height: 1.02; letter-spacing: -.012em">
      <span class="posa" style="--d: {d1}ms"><span data-suono="{s1}" style="display: block">{a}</span></span>
      <span class="posa" style="--d: {d2}ms"><span data-suono="{s2}" style="display: block"><em>{b}</em></span></span>
    </h1>'''

def kicker(text, d=150, mt=24):
    return f'''    <div class="posa" style="--d: {d}ms; margin-top: {mt}px">
      <p class="lab" style="margin: 0; color: #D9C29A">{text}</p>
    </div>'''

def actions(items, d0, step=45):
    rn = ["i.", "ii.", "iii.", "iv."]
    lis = "\n".join(f'''      <li class="posa" style="--d: {d0 + i * step}ms"><span style="display: grid; grid-template-columns: 30px 1fr; gap: 6px; padding: 6px 0; font-size: 15px; line-height: 1.45"><span class="dsp" style="font-style: italic; font-size: 17px; color: #D9C29A">{rn[i]}</span>{t}</span></li>'''
                    for i, t in enumerate(items))
    return f'''    <ol style="list-style: none; margin: 16px 0 0; padding: 0 2px; text-shadow: 0 1px 12px rgba(12,10,6,.5)">
{lis}
    </ol>'''

def pills(options, state_key):
    btns = "\n".join(f'            <button type="button" class="pill" aria-pressed="{{{{{state_key}.{k}.pressed}}}}" onClick="{{{{ {state_key}.{k}.pick }}}}">{label}</button>' for k, label in options)
    return btns

FIG_OPEN = '''    <div class="posa l" style="--d: @D@ms; --d0: {{d0}}; margin-top: @MT@px">
      <figure ref="{{ fig.ref }}" data-suono="3" class="lg" style="margin: 0; border-radius: 22px; padding: 14px; --h: {{fig.h}}">
        ''' + glass_layers("fig") + '''
        <div class="lg-c">'''
FIG_CLOSE = '''        </div>
      </figure>
    </div>'''

# Shared SVG bits for the plans
WALL = 'fill="rgba(18,15,9,.22)" stroke="rgba(243,235,221,.7)" stroke-width="1.2"'
DOOR = 'fill="#3c4526"'
FURN = 'fill="none" stroke="rgba(243,235,221,.4)"'
def lbl(x, y, t, size=8):
    return f'<text x="{x}" y="{y}" fill="rgba(243,235,221,.75)" font-size="{size}" text-anchor="middle" font-family="Archivo, sans-serif" letter-spacing="1.5">{t}</text>'
def route(mid, pts, draw=True):
    p = " ".join(f"{x},{y}" for x, y in pts)
    if not draw:
        return f'<polyline points="{p}" fill="none" stroke="#D9C29A" stroke-width="1.2" stroke-dasharray="3 4" opacity=".85"></polyline>'
    return (f'<defs><mask id="{mid}" maskUnits="userSpaceOnUse" x="0" y="0" width="320" height="200"><polyline class="route-draw" points="{p}" fill="none" stroke="#fff" stroke-width="6" pathLength="1" stroke-dasharray="1"></polyline></mask></defs>'
            f'<polyline mask="url(#{mid})" points="{p}" fill="none" stroke="#D9C29A" stroke-width="1.2" stroke-dasharray="3 4" opacity=".85"></polyline>')
def pt(i, x, y, filled=True, label=None):
    label = label if label is not None else str(i)
    if filled:
        return f'<g class="pt" style="--i: {i}"><circle cx="{x}" cy="{y}" r="9" fill="#D9C29A"></circle><text x="{x}" y="{y + 3.5}" fill="#17130C" font-size="9" text-anchor="middle" font-family="Archivo, sans-serif" font-weight="700">{label}</text></g>'
    return f'<g class="pt" style="--i: {i}"><circle cx="{x}" cy="{y}" r="9" fill="#2a2f1c" stroke="rgba(243,235,221,.7)"></circle><text x="{x}" y="{y + 3.5}" fill="#F3EBDD" font-size="9" text-anchor="middle" font-family="Archivo, sans-serif">{label}</text></g>'
def skipped(x, y):
    return f'<g aria-hidden="true"><circle cx="{x}" cy="{y}" r="8" fill="none" stroke="rgba(243,235,221,.45)" stroke-dasharray="2 2"></circle><path d="M{x - 4} {y - 4}l8 8M{x + 4} {y - 4}l-8 8" stroke="rgba(243,235,221,.55)" stroke-width="1.2"></path></g>'
def sweep(x, y, r, a0, a1):
    import math
    p0 = (x + r * math.cos(math.radians(a0)), y + r * math.sin(math.radians(a0)))
    p1 = (x + r * math.cos(math.radians(a1)), y + r * math.sin(math.radians(a1)))
    large = 1 if (a1 - a0) % 360 > 180 else 0
    return f'<path d="M{x} {y} L{p0[0]:.1f} {p0[1]:.1f} A{r} {r} 0 {large} 1 {p1[0]:.1f} {p1[1]:.1f} Z" fill="rgba(217,194,154,.22)"></path>'
def svg(label, inner):
    return f'''          <svg viewBox="0 0 320 190" width="100%" role="img" aria-label="{label}" style="display: block">
            {inner}
          </svg>'''

# Variant switching logic, shared by the screens with shape pills.
def variant_logic(key, options, first):
    keys = ", ".join(f"'{k}'" for k, _ in options)
    return f'''  // Shape pills: choosing one swaps the plan; its route and points play again right away.
  {key}Vals() {{
    const cur = (this.state && this.state.{key}) || '{first}';
    const v = {{ d0: this._{key}Picked ? '150ms' : (this._d0 || '1450ms') }};
    [{keys}].forEach((k) => {{
      v[k] = {{ on: cur === k, pressed: String(cur === k), pick: () => {{ this._{key}Picked = true; this.setState({{ {key}: k }}); }} }};
    }});
    return v;
  }}
'''

# ---------------------------------------------------------------- Stretta (Ogni spazio 3/4)
CORR = svg("Corridoio visto dall'alto: entri dal basso, cammini fino in fondo, sosti girando da parete a parete, poi torni camminando in avanti.",
    f'<rect x="128" y="10" width="64" height="160" rx="4" {WALL}></rect><rect x="124" y="52" width="8" height="30" {DOOR}></rect><rect x="188" y="110" width="8" height="30" {DOOR}></rect><rect x="143" y="166" width="34" height="8" {DOOR}></rect>'
    + sweep(160, 34, 24, 180, 360) + route("routeCorr", [(152, 188), (152, 40), (168, 40), (168, 188)])
    + '<path d="M148 112l4-6 4 6M164 118l4 6 4-6" fill="none" stroke="#D9C29A" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"></path>'
    + lbl(244, 40, "SOSTA IN FONDO") + lbl(240, 120, "RITORNO") + lbl(240, 131, "IN AVANTI") + lbl(86, 120, "ANDATA")
    + pt(1, 160, 34) + pt(2, 168, 178, False))
BAGNO = svg("Bagno piccolo visto dall'alto: entri, vai fino in fondo, sosti girando da parete a parete, poi esci.",
    f'<rect x="100" y="40" width="120" height="130" rx="4" {WALL}></rect><rect x="108" y="48" width="44" height="50" rx="3" {FURN}></rect><rect x="176" y="48" width="36" height="28" rx="3" {FURN}></rect><rect x="176" y="120" width="36" height="40" rx="3" {FURN}></rect><rect x="143" y="166" width="34" height="8" {DOOR}></rect>'
    + lbl(130, 76, "DOCCIA", 7) + lbl(194, 65, "WC", 7) + lbl(194, 143, "LAVABO", 7)
    + sweep(160, 92, 22, 180, 360) + route("routeBagno", [(156, 188), (156, 96), (168, 96), (168, 188)])
    + lbl(266, 96, "SOSTA IN FONDO") + pt(1, 160, 92) + pt(2, 168, 180, False))
SCALA = svg("Scala vista di lato: sosta in basso, sul pianerottolo e in cima, con una mano sul corrimano.",
    '<path d="M16 172H48V156H72V140H96V124H120V108H170V92H194V76H218V60H242V44H304" fill="none" stroke="rgba(243,235,221,.7)" stroke-width="1.6"></path>'
    '<path d="M20 140L120 80H170L246 16" fill="none" stroke="rgba(243,235,221,.4)" stroke-width="1.2"></path>'
    + route("routeScala", [(32, 158), (145, 94), (272, 30)])
    + lbl(40, 186, "IN BASSO") + lbl(145, 126, "PIANEROTTOLO") + lbl(282, 60, "IN CIMA") + lbl(64, 104, "CORRIMANO", 7)
    + pt(1, 32, 158) + pt(2, 145, 94) + pt(3, 272, 30))
STRETTA_OPTS = [("corridoio", "Corridoio"), ("bagno", "Bagno piccolo"), ("scala", "Scala")]
stretta_body = f'''  <div style="position: relative; height: 100%; box-sizing: border-box; padding: 54px 20px 34px; display: flex; flex-direction: column">
{header()}
{meta("Ogni spazio · Spazio 2", 3, 4, 3)}
{kicker("Parte stretta · meno di 2 passi di larghezza")}
{title_lines("Fino in fondo,", "e ritorno", 200, 310)}
{FIG_OPEN.replace('@D@', '450').replace('@MT@', '20')}
          <sc-if value="{{{{ forma.corridoio.on }}}}" hint-placeholder-val="{{{{ true }}}}">
{CORR}
            <p style="margin: 10px 0 0; font-size: 13px; line-height: 1.45">Niente soste in mezzo: andata, sosta in fondo, ritorno in avanti.</p>
          </sc-if>
          <sc-if value="{{{{ forma.bagno.on }}}}" hint-placeholder-val="{{{{ false }}}}">
{BAGNO}
            <p style="margin: 10px 0 0; font-size: 13px; line-height: 1.45">Bagno piccolo: è una parte stretta. Fino in fondo, sosta, e fuori.</p>
          </sc-if>
          <sc-if value="{{{{ forma.scala.on }}}}" hint-placeholder-val="{{{{ false }}}}">
{SCALA}
            <p style="margin: 10px 0 0; font-size: 13px; line-height: 1.45">Vista di lato. Se salire registrando non è sicuro, ferma e riprendi su ogni pianerottolo.</p>
          </sc-if>
          <div style="margin-top: 12px; display: flex; flex-wrap: wrap; gap: 6px" aria-label="Tipi di parte stretta">
{pills(STRETTA_OPTS, "forma")}
          </div>
{FIG_CLOSE}
{actions(["Cammina piano, telefono davanti agli occhi.", "Girati da fermo e torna in avanti, mai all’indietro."], 500)}
    <nav style="margin-top: auto; display: flex; gap: 10px">
{back_btn("Stanza.dc.html", 560)}
      <div class="posa" style="--d: 590ms; flex: 2; display: flex">
        <a href="Porte.dc.html" data-suono="4" class="btn btn-p" style="flex: 1">Avanti</a>
      </div>
    </nav>
  </div>'''

# ---------------------------------------------------------------- Porte (Ogni spazio 4/4)
PORTE_SVG = svg("Pianta: dallo spazio che stai riprendendo passi la porta verso un altro spazio, fai due passi oltre, ti giri e torni; poi esci dalla porta in basso e fermi la registrazione due passi dopo.",
    f'<rect x="10" y="10" width="220" height="160" rx="6" {WALL}></rect><rect x="238" y="10" width="72" height="160" rx="6" fill="rgba(42,47,28,.55)" stroke="rgba(243,235,221,.7)" stroke-width="1.2"></rect>'
    f'<rect x="226" y="70" width="16" height="40" {DOOR}></rect><rect x="110" y="166" width="34" height="8" {DOOR}></rect>'
    + lbl(120, 30, "QUESTO SPAZIO") + lbl(274, 30, "ALTRO") + lbl(274, 41, "SPAZIO")
    + route("routePorte", [(110, 120), (205, 84), (276, 84), (276, 98), (205, 98), (127, 150), (127, 188)])
    + pt(1, 276, 91) + pt(2, 127, 182, False))
porte_body = f'''  <div style="position: relative; height: 100%; box-sizing: border-box; padding: 54px 20px 34px; display: flex; flex-direction: column">
{header()}
{meta("Ogni spazio · Spazio 2", 4, 4, 4)}
{kicker("Fine dello spazio")}
{title_lines("Ogni porta,", "attraversata", 200, 310)}
{FIG_OPEN.replace('@D@', '450').replace('@MT@', '20')}
{PORTE_SVG}
          <p style="margin: 10px 0 0; font-size: 13px; line-height: 1.45"><span class="dsp" style="font-style: italic; color: #E6D3B0">1</span>&#160; Due passi oltre ogni porta verso uno spazio che riprendi, poi torna. <span class="dsp" style="font-style: italic; color: #E6D3B0">2</span>&#160; Esci e ferma due passi dopo.</p>
{FIG_CLOSE}
{actions(["Porte chiuse a chiave e armadi: ignorali.", "La porta-finestra del balcone è una porta come le altre."], 500)}
    <nav style="margin-top: auto; display: flex; gap: 10px">
{back_btn("Stretta.dc.html", 560)}
      <div class="posa" style="--d: 590ms; flex: 2; display: flex">
        <a href="Registra.dc.html" data-suono="4" class="btn btn-p" style="flex: 1">{REC_DOT}Avvia la registrazione</a>
      </div>
    </nav>
  </div>'''

# ---------------------------------------------------------------- Controllo (Alla fine 1/2)
CHK_CSS = """/* Final checklist: real checkboxes, drawn as champagne rings that fill when ticked. */
.chk{position:relative;display:grid;grid-template-columns:30px 1fr;gap:12px;align-items:start;padding:12px 0;cursor:pointer;font-size:15px;line-height:1.45}
.chk+.chk{border-top:1px solid rgba(243,235,221,.14)}
.chk input{position:absolute;opacity:0;width:30px;height:30px;margin:0;cursor:pointer}
.chk-box{width:26px;height:26px;border-radius:50%;border:1.5px solid #D9C29A;display:grid;place-items:center;transition:background .3s cubic-bezier(.22,1,.36,1)}
.chk input:checked+.chk-box{background:#D9C29A;color:#17130C}
.chk input:focus-visible+.chk-box{outline:2px solid #F3EBDD;outline-offset:3px}"""
def chk(key, text):
    return f'''            <label class="chk">
              <input type="checkbox" checked="{{{{ chk.{key}.on }}}}" onChange="{{{{ chk.{key}.toggle }}}}">
              <span class="chk-box" aria-hidden="true"><sc-if value="{{{{ chk.{key}.on }}}}" hint-placeholder-val="{{{{ false }}}}"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l4.5 4.5L19 7.5"></path></svg></sc-if></span>
              <span>{text}</span>
            </label>'''
controllo_body = f'''  <div style="position: relative; height: 100%; box-sizing: border-box; padding: 54px 20px 34px; display: flex; flex-direction: column">
{header()}
{meta("Alla fine", 1, 2, 1)}
{kicker("Prima di lasciare l’immobile")}
{title_lines("Prima di", "andare via", 200, 310)}
    <div class="posa l" style="--d: 450ms; margin-top: 20px">
      <section ref="{{{{ card.ref }}}}" data-suono="3" class="lg" style="border-radius: 22px; padding: 6px 20px; --h: {{{{card.h}}}}">
        {glass_layers("card")}
        <div class="lg-c">
{chk("spazi", "Una registrazione per ogni spazio, anche corridoi e scale che li collegano.")}
{chk("porte", "Ogni porta tra due spazi ripresi, attraversata registrando.")}
{chk("video", "Due o tre video aperti a caso: nitidi, luminosi, senza dita davanti.")}
        </div>
      </section>
    </div>
    <div class="posa" style="--d: 500ms; margin: 16px 2px 0">
      <p style="margin: 0; font-size: 15px; line-height: 1.55">Manca qualcosa? Registralo adesso: la casa è ancora com’era. Uno spazio si rifà da solo.</p>
    </div>
    <nav style="margin-top: auto; display: flex; gap: 10px">
{back_btn("Fatto.dc.html", 560, "Uno spazio")}
      <div class="posa" style="--d: 590ms; flex: 2; display: flex">
        <a href="Video.dc.html" data-suono="4" class="btn btn-p" style="flex: 1">Tutto fatto</a>
      </div>
    </nav>
  </div>'''
CHK_LOGIC = '''  // Final checklist state: three ticks, each toggled by its own row.
  chkVals() {
    const s = (this.state && this.state.chk) || {};
    const v = {};
    ['spazi', 'porte', 'video'].forEach((k) => {
      v[k] = { on: !!s[k], toggle: () => this.setState({ chk: Object.assign({}, s, { [k]: !s[k] }) }) };
    });
    return v;
  }
'''

# ---------------------------------------------------------------- In breve (sheet)
RULES = [
    "Telefono verticale, sempre. La guida usa la lente 0,5×.",
    "Una bella giornata e più luce possibile: tapparelle su, tende spostate.",
    "Porte aperte e niente spostato fino alla fine.",
    "Una registrazione per spazio: parti da fuori, entra, non fermarti fino all’uscita.",
    "Parte ampia: ogni angolo e il centro di ogni parete, con un giro piano.",
    "Un punto bloccato da un mobile? Saltalo.",
    "Parte stretta: fino in fondo, sosta, ritorno camminando in avanti.",
    "Ogni porta tra spazi ripresi, attraversata registrando.",
]
RN = ["i.", "ii.", "iii.", "iv.", "v.", "vi.", "vii.", "viii."]
rules_html = "\n".join(
    f'''          <li class="posa" style="--d: {560 + i * 45}ms"{' data-x=""' if False else ''}><span{' data-suono="4"' if i == 0 else ''} style="display: grid; grid-template-columns: 34px 1fr; gap: 4px; padding: 9px 0; font-size: 14px; line-height: 1.45; border-top: 1px solid rgba(243,235,221,.12)"><span class="dsp" style="font-style: italic; font-size: 16px; color: #E6D3B0">{RN[i]}</span>{t}</span></li>'''
    for i, t in enumerate(RULES))
inbreve_body = f'''  <div aria-hidden="true" style="position: absolute; inset: 0; background: rgba(12,10,6,.28)"></div>
  <div style="position: relative; height: 100%; box-sizing: border-box; padding: 54px 12px 24px; display: flex; flex-direction: column">
    <header style="display: flex; justify-content: space-between; align-items: center; padding: 0 8px">
      {LOGO}
      <div style="display: flex; gap: 8px">
        {SND_BTN}
      </div>
    </header>
    <div class="posa l" style="--d: 120ms; margin-top: 18px; flex: 1; display: flex; --tilt: -.6deg">
      <section ref="{{{{ sheet.ref }}}}" data-suono="1" class="lg" style="flex: 1; border-radius: 30px; padding: 20px 22px 14px; --h: {{{{sheet.h}}}}" aria-labelledby="inbreve-title">
        {glass_layers("sheet")}
        <div class="lg-c">
          <div style="display: flex; justify-content: space-between; align-items: center">
            <p class="lab" style="margin: 0; color: #D9C29A">In breve</p>
            <a ref="{{{{ close.ref }}}}" href="Main.dc.html" class="lg lab" style="height: 44px; padding: 0 18px; border-radius: 999px; display: inline-flex; align-items: center; text-decoration: none; --h: {{{{close.h}}}}">
              {glass_layers("close")}
              <span class="lg-c">Chiudi</span>
            </a>
          </div>
          <h1 id="inbreve-title" class="dsp" style="margin: 10px 0 8px; font-size: 38px; line-height: 1.04; letter-spacing: -.012em">
            <span class="posa" style="--d: 340ms"><span data-suono="2" style="display: block">Tutta la guida</span></span>
            <span class="posa" style="--d: 450ms"><span data-suono="3" style="display: block"><em>in otto righe</em></span></span>
          </h1>
          <ol style="list-style: none; margin: 0; padding: 0">
{rules_html}
          </ol>
        </div>
      </section>
    </div>
  </div>'''
# In the sheet the 4th knock falls on the first rule; give it the rhythm slot.
inbreve_body = inbreve_body.replace('<li class="posa" style="--d: 560ms">', '<li class="posa" style="--d: 590ms">')

files = {
    "Stretta.dc.html": page("Ogni spazio — parte stretta", {"snd": "round", "inb": "pill", "fig": "card", "back": "pill"}, stretta_body,
                            extra_vals="\n      forma: this.formaVals(), d0: this.formaVals().d0,",
                            extra_logic=variant_logic("forma", STRETTA_OPTS, "corridoio")),
    "Porte.dc.html": page("Ogni spazio — porte e uscita", {"snd": "round", "inb": "pill", "fig": "card", "back": "pill"}, porte_body,
                          extra_vals="\n      d0: '1450ms',"),
    "Controllo.dc.html": page("Alla fine — controllo prima di andare via", {"snd": "round", "inb": "pill", "card": "card", "back": "pill"}, controllo_body,
                              extra_css=CHK_CSS, extra_vals="\n      chk: this.chkVals(),", extra_logic=CHK_LOGIC),
    "InBreve.dc.html": page("In breve — tutta la guida in otto righe", {"snd": "round", "sheet": "sheet", "close": "pill"}, inbreve_body),
}
if __name__ == "__main__":
    for name, html in files.items():
        open(name, "w", encoding="utf-8").write(html)
        print(name, len(html))

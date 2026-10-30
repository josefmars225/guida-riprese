"""Build index.html: the guide designed in the canvas (design/Main.dc.html), run by the small runtime in
src/shell.html, with src/app.js sending the videos to Google Drive. Run: python3 tools/build.py"""
import json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
src = (ROOT / "design/Main.dc.html").read_text(encoding="utf-8")
# the canvas's media, published beside the page
MEDIA = {"8ec3f1fa633ba7a58c1af553710c756c": "media/prato.webp", "c08311aba401b5634c4ceb2b469a4baa": "media/prato-vento.mp4",
         "d6dd3f830358c6b6cb9ee9cf8c8607c8": "media/gymnopedie.mp4", "5e6684a3ce03d7a74af4cff8c6b43de9": "media/lg-card.png",
         "af4adb5233848d8abd4191eadd20fbdf": "media/lg-pill.png", "6f7dd104080ac8959b6432595e3e268a": "media/lg-round.png"}
for blob, path in MEDIA.items():
    src = src.replace("/_blob/" + blob, path)
assert "/_blob/" not in src, "the design uses a file not listed in MEDIA"

xdc = src[src.index("<x-dc>") + 6:src.index("</x-dc>")]
helmet = xdc[xdc.index("<helmet>") + 8:xdc.index("</helmet>")]
body = xdc[xdc.index("</helmet>") + 9:]
m = re.search(r"<script type=\"text/x-dc\" data-dc-script data-props='([^']*)'>(.*?)</script>", src, re.S)
props = {k: v["default"] for k, v in json.loads(m.group(1).replace("&amp;", "&").replace("&#39;", "'")).items()
         if not k.startswith("$") and "default" in v}
component = m.group(2)

app = (ROOT / "src/app.js").read_text(encoding="utf-8")
app = app.replace("__FIT__", (ROOT / "src/fit.js").read_text(encoding="utf-8")).replace("__PROPS__", json.dumps(props, ensure_ascii=False))
names = lambda js: set(re.findall(r"^(?:const|let|var|function|class)\s+([A-Za-z_$][\w$]*)", js, re.M))
clash = names(component) & names(app)
assert not clash, f"names used by both the design and app.js: {clash}"

shell = (ROOT / "src/shell.html").read_text(encoding="utf-8")
html = (shell.replace("__HELMET_LINKS__", "\n".join(re.findall(r"<link[^>]*>", helmet)))
             .replace("__HELMET_STYLE__", "\n".join(re.findall(r"<style>(.*?)</style>", helmet, re.S))
                      + "\n/* sending is shown by the page itself */\n")
             .replace("__XDC__", body).replace("__COMPONENT__", component)
             .replace("__APP__", "<script>\n" + app + "</script>"))
assert not re.search(r"__[A-Z]+__", html), "a placeholder was left"
# config.js changes on its own (the script address): its name carries its content's hash, so a phone never keeps an old one
import hashlib
ver = hashlib.sha1((ROOT / "config.js").read_bytes()).hexdigest()[:8]
html = html.replace('<script src="config.js"></script>', f'<script src="config.js?v={ver}"></script>', 1)
(ROOT / "index.html").write_text(html, encoding="utf-8")
print("index.html", len(html), "bytes")

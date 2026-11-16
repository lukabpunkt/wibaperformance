"""Teil 1 der Aufbereitung für wibaperformance.de (Wix).
Aufruf: python3 -I _raw/scripts/extract.py <projektordner>
- lädt alle Wix-Medien in Originalgröße (static.wixstatic.com/media/<uri> ohne /v1/fill/...) nach _raw/assets/media/
- lädt Videos (höchste verfügbare Auflösung) nach _raw/assets/video/
- extrahiert pro Seite den Hauptinhalt (ohne Header/Footer) als Blöcke inkl. Bild-Reihenfolge
- schreibt _raw/extract.json
"""
import os, re, sys, json, time, html, hashlib
from urllib.parse import urlparse, unquote
import requests
from bs4 import BeautifulSoup, Comment

ROOT = sys.argv[1]
RAW = os.path.join(ROOT, "_raw")
crawl = json.load(open(os.path.join(RAW, "crawl-render.json"), encoding="utf-8"))
S = requests.Session(); S.headers["User-Agent"] = "Mozilla/5.0 (Macintosh) site-archiver"
MEDIA_RE = re.compile(r"(?:[0-9a-f]{6}_)?[0-9a-f]{32}(?:~mv2(?:_d_\d+_\d+_s_\d+)?)?\.(?:jpg|jpeg|png|webp|gif|svg)", re.I)
VIDEO_RE = re.compile(r"video\.wixstatic\.com/video/([0-9a-f]{6}_[0-9a-f]{32})")


def media_uri_from_url(u):
    m = re.search(r"static\.wixstatic\.com/media/([^/?#]+)", u)
    return unquote(m.group(1)) if m else None


def block_md(el):
    """Rich-Text-Element -> Markdown (Überschriften, Absätze, Listen)."""
    out = []
    for n in el.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "li"]):
        if n.find_parent(["li"]) and n.name == "p":
            continue
        t = n.get_text(" ", strip=True).replace("\xa0", " ")
        t = re.sub(r"\s+", " ", t)
        if not t or t == "​":
            continue
        if n.name.startswith("h"):
            out.append("#" * int(n.name[1]) + " " + t)
        elif n.name == "li":
            out.append("- " + t)
        else:
            bold = n.find(["strong", "b"]) or (n.find("span", style=re.compile("font-weight:\\s*(bold|[6-9]00)")))
            whole_bold = bold and bold.get_text(" ", strip=True) == n.get_text(" ", strip=True)
            out.append(("**" + t + "**") if whole_bold else t)
    return "\n\n".join(out)


pages = []
media = {}  # uri -> info
videos = {}
done_names = set()
for p in crawl["pages"]:
    name = p["name"]
    if name in done_names: continue
    done_names.add(name)
    rendered = open(os.path.join(RAW, "html-rendered", name + ".html"), encoding="utf-8").read()
    rawhtml_path = os.path.join(RAW, "html", name + ".html")
    rawhtml = open(rawhtml_path, encoding="utf-8").read() if os.path.exists(rawhtml_path) else ""
    s = BeautifulSoup(rendered, "html.parser")
    comments = [c.strip() for c in s.find_all(string=lambda t: isinstance(t, Comment)) if len(c.strip()) > 20]
    main = s.select_one("#PAGES_CONTAINER") or s.select_one("main") or s.body
    blocks = []
    last_heading = None
    for el in main.find_all(True):
        if el.get("data-testid") == "richTextElement":
            t = block_md(el)
            if t:
                blocks.append({"typ": "text", "md": t})
                first = t.split("\n")[0].lstrip("#* ").rstrip("*")
                last_heading = first[:80]
        elif el.name == "img":
            uri = media_uri_from_url(el.get("src") or "")
            if uri:
                blocks.append({"typ": "bild", "uri": uri, "alt": el.get("alt", "")})
                mi = media.setdefault(uri, {"uri": uri, "seiten": [], "alts": [], "kontext": []})
                if name not in mi["seiten"]: mi["seiten"].append(name)
                if el.get("alt") and el["alt"] not in mi["alts"]: mi["alts"].append(el["alt"])
                if last_heading and last_heading not in mi["kontext"]: mi["kontext"].append(last_heading)
        elif el.name == "video" or (el.name == "wix-video"):
            pass
        elif el.get("data-testid") in ("linkElement",) and el.name == "a" and el.get_text(strip=True):
            blocks.append({"typ": "button", "text": el.get_text(" ", strip=True), "href": el.get("href")})
    # alle weiteren Medien-URIs aus SSR-JSON (Galerien, Slider, nicht geladene Bilder)
    for uri in set(MEDIA_RE.findall(html.unescape(rawhtml + rendered))):
        mi = media.setdefault(uri, {"uri": uri, "seiten": [], "alts": [], "kontext": []})
        if name not in mi["seiten"]: mi["seiten"].append(name)
    for vid in set(VIDEO_RE.findall(rendered + rawhtml)):
        videos.setdefault(vid, {"id": vid, "seiten": []})
        if name not in videos[vid]["seiten"]: videos[vid]["seiten"].append(name)
        blocks.insert(0, {"typ": "video", "id": vid})
    # Seiten-Bloecke ohne Header/Footer-Duplikate
    pages.append({"name": name, "url": p["final"], "titel": p["title"], "meta": p["meta"], "headings": p["headings"],
                  "bloecke": blocks, "kommentare": comments, "mobil": p["mobile"], "fehlende_alt": p["missingAlt"]})

# Wix-Namen der Bilder aus JSON ("uri":"..","name":"..") holen
names = {}
for p in crawl["pages"]:
    h = html.unescape(open(os.path.join(RAW, "html", p["name"] + ".html"), encoding="utf-8").read()) if os.path.exists(os.path.join(RAW, "html", p["name"] + ".html")) else ""
    for m in re.finditer(r'"uri":"([^"]+)","name":"([^"]*)"', h):
        names.setdefault(m.group(1), m.group(2))
    for m in re.finditer(r'"name":"([^"]*)"[^{}]{0,200}?"uri":"([^"]+)"', h):
        names.setdefault(m.group(2), m.group(1))

# Download Originale
os.makedirs(os.path.join(RAW, "assets", "media"), exist_ok=True)
from PIL import Image
seen_md5 = {}
for uri, mi in sorted(media.items()):
    dest = os.path.join(RAW, "assets", "media", uri)
    if not os.path.exists(dest):
        r = S.get("https://static.wixstatic.com/media/" + uri, timeout=60)
        time.sleep(0.3)
        if r.status_code != 200:
            mi["fehler"] = r.status_code; continue
        open(dest, "wb").write(r.content)
    data = open(dest, "rb").read()
    mi["datei"] = os.path.relpath(dest, ROOT)
    mi["bytes"] = len(data)
    mi["md5"] = hashlib.md5(data).hexdigest()
    mi["wix_name"] = names.get(uri, "")
    try:
        mi["breite"], mi["hoehe"] = Image.open(dest).size
    except Exception:
        mi["breite"] = mi["hoehe"] = None
    if mi["md5"] in seen_md5:
        mi["duplikat_von"] = seen_md5[mi["md5"]]
    else:
        seen_md5[mi["md5"]] = uri

os.makedirs(os.path.join(RAW, "assets", "video"), exist_ok=True)
for vid, vi in videos.items():
    for q in ("1080p", "720p", "480p", "360p"):
        u = f"https://video.wixstatic.com/video/{vid}/{q}/mp4/file.mp4"
        dest = os.path.join(RAW, "assets", "video", f"{vid}-{q}.mp4")
        if os.path.exists(dest):
            vi.update(datei=os.path.relpath(dest, ROOT), qualitaet=q); break
        r = S.get(u, timeout=120); time.sleep(0.3)
        if r.status_code == 200 and r.headers.get("content-type", "").startswith("video"):
            open(dest, "wb").write(r.content)
            vi.update(datei=os.path.relpath(dest, ROOT), qualitaet=q, bytes=len(r.content), url=u); break

json.dump({"seiten": pages, "medien": list(media.values()), "videos": list(videos.values())},
          open(os.path.join(RAW, "extract.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(len(pages), "Seiten", len(media), "Medien", len(seen_md5), "eindeutig", len(videos), "Videos")

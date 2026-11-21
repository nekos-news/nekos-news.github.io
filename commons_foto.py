#!/usr/bin/env python3
"""Freie Fotos von Wikimedia Commons für die News-Videos (Wunsch Nicolas 2026-11-21, über ANALYSE/FILMCRAFT).
Nur freie Lizenzen (CC0, Public Domain, CC BY, CC BY-SA). Keine Agenturfotos aus den Artikeln.

  python3 commons_foto.py suche "Olaf Scholz 2025"       → Kandidaten mit Lizenz, Urheber, Größe, Datum
  python3 commons_foto.py hole "File:Name.jpg" ZIEL.jpg   → lädt (max. 1920 px breit), gibt den Bildnachweis aus
  python3 commons_foto.py hole "File:Name.jpg" ZIEL.jpg --ausschnitte 3
        → ZIEL1.jpg (ganz), ZIEL2.jpg (80 %), ZIEL3.jpg (65 %), auf den Kopf zentriert – für 3 Starts mit demselben Foto
Das ausgewählte Bild vor der Nutzung ansehen (richtige Person? aktuell? kein Logo/Wasserzeichen?).
"""
import json, os, re, subprocess, sys, urllib.parse, urllib.request

API = "https://commons.wikimedia.org/w/api.php"
GESICHT = os.path.expanduser("~/NekoTools/gesicht/gesicht")  # Apple Vision, größtes Gesicht als x y b h
UA = "MorgenzeitungFotoHelfer/1.0 (lokales Skript; freie Lizenzen)"
FREI = re.compile(r"^(CC0|Public domain|PD|CC BY(-SA)? \d|CC BY(-SA)?$|Attribution)", re.I)


def api(**p):
    p.update(format="json", formatversion="2")
    r = urllib.request.Request(API + "?" + urllib.parse.urlencode(p), headers={"User-Agent": UA})
    return json.load(urllib.request.urlopen(r, timeout=30))


def klar(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html or "")).strip()


def info(seiten):
    out = []
    for s in seiten:
        ii = (s.get("imageinfo") or [{}])[0]; m = ii.get("extmetadata", {})
        lz = klar(m.get("LicenseShortName", {}).get("value"))
        out.append(dict(titel=s["title"], lizenz=lz, frei=bool(FREI.match(lz)),
                        urheber=klar(m.get("Artist", {}).get("value")) or "unbekannt",
                        datum=klar(m.get("DateTimeOriginal", {}).get("value"))[:10],
                        breite=ii.get("width"), hoehe=ii.get("height"), mime=ii.get("mime"),
                        url=ii.get("thumburl") or ii.get("url"), seite=ii.get("descriptionurl"),
                        beschreibung=klar(m.get("ImageDescription", {}).get("value"))[:140]))
    return out


def suche(begriff, n=12):
    d = api(action="query", generator="search", gsrnamespace=6, gsrsearch=begriff + " filetype:bitmap", gsrlimit=n,
            prop="imageinfo", iiprop="url|size|mime|extmetadata", iiurlwidth=1920)
    return [x for x in info(d.get("query", {}).get("pages", [])) if x["mime"] in ("image/jpeg", "image/png")]


def nachweis(x):
    return "Foto: %s / Wikimedia Commons, %s" % (x["urheber"], x["lizenz"])


def hole(titel, ziel, ausschnitte=1):
    d = api(action="query", titles=titel, prop="imageinfo", iiprop="url|size|mime|extmetadata", iiurlwidth=1920)
    x = info(d["query"]["pages"])[0]
    if not x["frei"]: sys.exit("Keine freie Lizenz: %s (%s)" % (x["lizenz"], titel))
    os.makedirs(os.path.dirname(os.path.abspath(ziel)), exist_ok=True)
    roh = ziel + ".roh"
    with urllib.request.urlopen(urllib.request.Request(x["url"], headers={"User-Agent": UA}), timeout=60) as r, open(roh, "wb") as f: f.write(r.read())
    basis, _ = os.path.splitext(ziel); dateien = []
    if ausschnitte <= 1:
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", roh, "-q:v", "2", basis + ".jpg"], check=True); dateien.append(basis + ".jpg")
    else:
        # 1 = ganz, 2 = 80 %, 3 = 65 %, auf den Kopf zentriert (Wunsch FILMCRAFT 2026-11-21: ganzes Gesicht samt Kinn, oben etwas Luft;
        # die Titelseite schneidet danach mittig auf ~0,96 B/H zu, deshalb Kopf ungefähr in die Bildmitte)
        W, H = [int(v) for v in subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=width,height", "-of", "csv=p=0", roh],
                                               capture_output=True, text=True).stdout.split(",")[:2]]
        g = subprocess.run([GESICHT, roh], capture_output=True, text=True).stdout.split() if os.path.exists(GESICHT) else []
        if len(g) == 4:
            fx, fy, fb, fh = map(int, g)
            kx, ky = fx + fb / 2, fy + fh / 2 - 0.15 * fh            # Mitte Kopf (etwas nach oben wegen Haaren)
            oben, unten = fy - 0.6 * fh, fy + fh * 1.15                # Haare bzw. Kinn mit Rand
        else:
            kx, ky = W / 2, H * 0.45; oben = unten = ky                 # kein Gesicht erkannt: mittig, etwas nach oben
            print("Hinweis: kein Gesicht erkannt, Ausschnitte mittig – Bild ansehen", file=sys.stderr)
        for i, f in enumerate([1.0, 0.8, 0.65][:ausschnitte], 1):
            b, h = W * f, H * f
            h = max(h, unten - oben); b = min(W, max(b, h * W / H)); h = min(H, b * H / W)   # Kopf passt immer ganz rein
            cx = min(max(0, kx - b / 2), W - b); cy = min(max(0, ky - h / 2), H - h)
            p = "%s%d.jpg" % (basis, i)
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", roh, "-vf", "crop=%d:%d:%d:%d" % (b, h, cx, cy), "-q:v", "2", p], check=True)
            dateien.append(p)
    os.remove(roh)
    return dict(dateien=dateien, nachweis=nachweis(x), seite=x["seite"], lizenz=x["lizenz"], urheber=x["urheber"])


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["suche"]:
        for x in suche(" ".join(a[1:])):
            print(("FREI " if x["frei"] else "NEIN ") + "%s | %s | %s | %sx%s | %s | %s" % (x["titel"], x["lizenz"], x["urheber"][:40], x["breite"], x["hoehe"], x["datum"], x["beschreibung"][:80]))
    elif a[:1] == ["hole"]:
        n = int(a[a.index("--ausschnitte") + 1]) if "--ausschnitte" in a else 1
        print(json.dumps(hole(a[1], a[2], n), ensure_ascii=False, indent=1))
    else:
        print(__doc__)

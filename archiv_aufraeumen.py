#!/usr/bin/env python3
"""Archiv: nur die letzten 7 Tage vollständig, davor nur Highlights (Wunsch Nicolas 2026-11-25, spart Speicherplatz).

Für Ausgaben, die älter als 7 Tage sind:
  - Die Seite archiv/<datum>.html zeigt nur noch die Highlights (krass ≥ 7 oder gerade in Woche/Monat/Jahr, mindestens eins je Tag). Der Text
    bleibt in der Datei, weil Videos und geteilte Links auf einzelne Meldungen zeigen: …/archiv/<datum>#m5 zeigt m5 immer.
  - liste.json enthält nur noch die Highlights; alle anderen MP3s (auch „kurz“) wandern in den Papierkorb
    (~/.Trash/Morgenzeitung_alt/<datum>/), beim nächsten audio_hochladen.sh verschwinden sie auch online.
  - Zwischenspeicher der Stimme (~/NekoTools/qwen_tts/cache): WAVs älter als 7 Tage in den Papierkorb (neu erzeugbar).
Täglich nach seiten_bauen.py und VOR audio_hochladen.sh. Mehrfach laufen lassen ist harmlos.
  archiv_aufraeumen.py            nur anzeigen
  archiv_aufraeumen.py --los      ausführen"""
import datetime, glob, json, os, re, shutil, sys, time

HIER = os.path.dirname(os.path.abspath(__file__))
TAGE = 7
CACHE = os.path.expanduser("~/NekoTools/qwen_tts/cache")
TRASH = os.path.expanduser("~/.Trash/Morgenzeitung_alt")
MARKE = re.compile(r'\n?<script data-alt>.*?</script>\n?', re.S)
SKRIPT = '''<script data-alt>
/* Ältere Ausgabe: nur noch die Highlights, dazu die Meldung aus dem Link (archiv_aufraeumen.py, 2026-11-25) */
(function () { var bleibt = %s, ziel = location.hash.slice(1), w = document.querySelector('.wrap[data-datum]'); if (!w) return;
  w.querySelectorAll('article[id]').forEach(function (a) { if (bleibt.indexOf(a.id) < 0 && a.id !== ziel) a.remove(); });
  var k = document.getElementById('kurz'); if (k) k.remove();
  w.querySelectorAll('section.gruppe').forEach(function (s) { if (!s.querySelector('article')) s.remove(); });
  var s = w.querySelector('section.gruppe'); if (!s) return;
  w.querySelectorAll('section.gruppe h2.zettel').forEach(function (h) { h.remove(); });
  var h = document.createElement('h2'); h.className = 'zettel'; h.textContent = 'Highlights vom %s'; s.insertBefore(h, s.firstChild);
})();
</script>'''


def mb(x): return "%.1f MB" % (x / 1e6)


def papierkorb(pfad, unter):
    z = os.path.join(TRASH, unter); os.makedirs(z, exist_ok=True)
    ziel = os.path.join(z, os.path.basename(pfad))
    if os.path.exists(ziel): ziel = "%s_%d%s" % (*os.path.splitext(ziel)[:1], time.time_ns(), os.path.splitext(ziel)[1])
    shutil.move(pfad, ziel)


def main():
    los = "--los" in sys.argv
    alle = json.load(open(os.path.join(HIER, "daten", "artikel.json"), encoding="utf-8"))
    heute = max(datetime.date.fromisoformat(a["datum"]) for a in alle)
    highlights = set()
    for f in ("woche.html", "monat.html", "jahr.html"):
        highlights |= set(re.findall(r'href="archiv/(\d{4}-\d\d-\d\d)\.html#(m\d+)"', open(os.path.join(HIER, f), encoding="utf-8").read()))
    weg = 0
    for seite in sorted(glob.glob(os.path.join(HIER, "archiv", "20*.html"))):
        d = os.path.basename(seite)[:10]
        if (heute - datetime.date.fromisoformat(d)).days < TAGE: continue
        tag = [a for a in alle if a["datum"] == d]
        s = open(seite, encoding="utf-8").read()
        ids = re.findall(r'<article[^>]*id="(m\d+)"', s)
        bleibt = [i for i in ids if (d, i) in highlights or any(a["id"] == i and a.get("krass", 0) >= 7 for a in tag)]
        if not bleibt and tag: bleibt = [x for x in [max(tag, key=lambda a: a.get("krass", 0))["id"]] if x in ids]
        if not bleibt: print(d, "kein Highlight gefunden, übersprungen"); continue   # im Zweifel nichts anfassen
        dd = datetime.date.fromisoformat(d)
        neu = MARKE.sub("\n", s).replace("<!-- AUSGABE-ENDE -->", SKRIPT % (json.dumps(bleibt), dd.strftime("%d.%m.%Y")) + "\n<!-- AUSGABE-ENDE -->", 1)
        o = os.path.join(HIER, "audio", d)
        fort = [f for f in glob.glob(os.path.join(o, "*.mp3")) if os.path.basename(f).split(".")[0] not in bleibt]
        n = sum(os.path.getsize(f) for f in fort); weg += n
        print(d, "bleibt:", ",".join(bleibt), "| Audio weg:", len(fort), mb(n))
        if los:
            if neu != s: open(seite, "w", encoding="utf-8").write(neu)
            p = os.path.join(o, "liste.json")
            if os.path.exists(p):
                alt = json.load(open(p)); l = [i for i in alt if i in bleibt]
                if l != alt: json.dump(l, open(p, "w"))
            for f in fort: papierkorb(f, d)
    c = [f for f in glob.glob(os.path.join(CACHE, "*")) if os.path.isfile(f) and time.time() - os.path.getmtime(f) > TAGE * 86400]
    n = sum(os.path.getsize(f) for f in c); weg += n
    print("Zwischenspeicher der Stimme:", len(c), "Dateien", mb(n))
    if los:
        for f in c: papierkorb(f, "cache")
    print("zusammen", mb(weg), "in den Papierkorb gelegt" if los else "(nur angezeigt)")


if __name__ == "__main__": main()

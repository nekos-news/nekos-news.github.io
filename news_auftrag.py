#!/usr/bin/env python3
"""Auftragsdatei für die eigenständigen News-Videos (FILMCRAFT/ANALYSE), Wunsch Nicolas 2026-11-21 („Ja, ab morgen“).

Eingabe (schreibt der Morgenlauf): daten/news/<datum>/entwurf.json
  {"meldungen": [{"id": "m3", "starts": ["krasse Aussage wie eine Überschrift"], "herkunft": "Das berichtet heute die Tagesschau.", "frage": "…?",
                  "belegstellen": ["wörtlich aus dem Originalartikel", …1–2], "fotos": [{"datei": "daten/news/<datum>/m3_foto1.jpg", "nachweis": "Foto: … / Wikimedia Commons, CC BY-SA 4.0"}, …]}]}
  (3–5 Favoriten; Fotos mit commons_foto.py holen, nur freie Lizenzen)

Ausgabe: daten/news_auftrag_<datum>.json (Format von FILMCRAFT, 2026-11-21) und in daten/news/<datum>/:
  <id>_haupt.mp3 + <id>_haupt.woerter.json  = Herkunftssatz + Kernteil der Meldung (vor „Mehr anzeigen“) OHNE die Überschrift
  Seit 2026-11-21 (Nicolas): pro Meldung NUR EIN Video mit EINEM Start, nur Kurzfassung 30–45 s; haupt = Herkunft + Kern + Schlusssatz
  („… Den ganzen Überblick findest du auf unserer Seite, Nekos News.“); keine Frage mehr. seite_url = Archivseite mit #id.
  <id>_start1.mp3 + .woerter.json            = der eine Start
  Gleiche Stimme wie die Zeitung (Qwen, STIL probe2, gleiche Aussprache-Liste), ohne Musik.
daten/news/ und news_auftrag_*.json sind in .gitignore: nichts davon geht online.

Nutzung: ~/NekoTools/qwen_tts/venv/bin/python news_auftrag.py <datum> [--nur m9]
  --nur <id>: nur diese Meldung neu sprechen (nach Änderung in entwurf.json), die übrigen Einträge der Auftragsdatei bleiben.
Wartet von selbst, solange ein anderer Qwen-Lauf, FilmCraft-Render oder der Handy-Emulator läuft (Mac-Abstürze 2026-11-17/21).
"""
import json, os, re, subprocess, sys, time, hashlib, tempfile

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.expanduser("~/NekoTools/qwen_tts"))
import zeitung_audio_qwen as Z          # bloecke, aussprache, Cache, Stimme, ffmpeg-Einstellungen
import soundfile as sf
sys.path.insert(0, HIER)
from wortzeiten import woerter
from zeitung_audio import klartext


SCHLUSS = "Wer sich ausführlicher informieren will: Den ganzen Überblick findest du auf unserer Seite, Nekos News."
SEITE = "https://nekos-news.pages.dev/archiv/%s#%s"   # Archivseite bleibt fest, #mX öffnet die Meldung


def warte_bis_frei():
    muster = "zeitung_audio_qwen|vertonen.py|dazn_probe|filmcraft-cli|qemu-system"
    while True:
        r = subprocess.run(["pgrep", "-f", muster], capture_output=True, text=True).stdout.split()
        r = [p for p in r if int(p) != os.getpid()]
        if not r: return
        print("warte, es läuft noch:", r, flush=True); time.sleep(30)


def seite_fuer(datum):
    s = open(os.path.join(HIER, "index.html"), encoding="utf-8").read()
    if 'data-datum="%s"' % datum not in s: s = open(os.path.join(HIER, "archiv", datum + ".html"), encoding="utf-8").read()
    return s


def quellen(seite, mid):
    m = re.search(r'<article[^>]*id="%s"[^>]*>(.*?)</article>' % mid, seite, re.S)
    q = re.findall(r'<[^>]*class="quelle"[^>]*>(.*?)</(?:p|div)>', m.group(1), re.S) if m else []
    return re.findall(r'href="(https?://[^"]+)"', " ".join(q) or (m.group(1) if m else ""))


def sprich(s, stil, text, ziel):
    """Text wie die Zeitung vertonen (Cache wie zeitung_audio_qwen), als MP3 mit Lautheit -16 LUFS."""
    t = Z.aussprache(text.strip())
    c = os.path.join(Z.CACHE, hashlib.sha1((stil + "|" + os.path.basename(s.stil["ref"]) + "|%d|%s|" % (s.stil["lang"], s.stil.get("v", "")) + t).encode()).hexdigest() + ".wav")
    if not os.path.exists(c):
        w, sr, werte = s.sprich(t); os.makedirs(Z.CACHE, exist_ok=True); sf.write(c, w, sr)
        print("  Treffer min %.2f  %s" % (min(werte), t[:60]), flush=True)
    Z.ff("-i", c, "-af", Z.LN, *Z.ENDE, ziel)
    json.dump(woerter(ziel), open(ziel[:-4] + ".woerter.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))


def main():
    datum = sys.argv[1]
    ordner = os.path.join(HIER, "daten", "news", datum)
    entwurf = json.load(open(os.path.join(ordner, "entwurf.json"), encoding="utf-8"))
    seite = seite_fuer(datum); bl = dict(Z.bloecke(seite))
    warte_bis_frei()
    stil = os.environ.get("STIL", "probe2"); s = Z.Stimme(stil=stil)
    nur = sys.argv[sys.argv.index("--nur") + 1] if "--nur" in sys.argv else None
    aus = []
    for m in entwurf["meldungen"]:
        if nur and m["id"] != nur: continue
        mid = m["id"]; print(mid, flush=True)
        kern = bl[mid].split(Z.TRENNER)[0].strip()
        ueberschrift = re.search(r'<article[^>]*id="%s"[^>]*>.*?<h3>(.*?)</h3>' % mid, seite, re.S)
        erster = klartext(ueberschrift.group(1)) + "."
        haupt = kern[len(erster):].strip() if kern.startswith(erster) else kern
        # Satz 2 im Video = Herkunft („Das berichtet heute die Tagesschau.“), dann der Inhalt (Wunsch Nicolas 2026-11-21 über ANALYSE)
        if m.get("kurztext"): haupt = m["kurztext"].strip()   # eigene Kurzfassung, wenn der Kern zu lang ist (Ziel 30–45 s gesamt)
        if m.get("herkunft"): haupt = m["herkunft"].strip() + " " + haupt
        # Nur noch die Kurzfassung (30–45 s); am Ende statt Frage der Hinweis auf unsere Seite (Entscheidung Nicolas 2026-11-21 über ANALYSE)
        haupt = haupt + " " + m.get("schluss", SCHLUSS)
        p = lambda n: os.path.join(ordner, "%s_%s.mp3" % (mid, n))
        sprich(s, stil, haupt, p("haupt"))
        starts = []
        for i, (t, f) in enumerate(zip(m["starts"], m["fotos"]), 1):
            sprich(s, stil, t, p("start%d" % i))
            starts.append(dict(text=t, audio=p("start%d" % i), woerter=p("start%d" % i)[:-4] + ".woerter.json",
                               foto=os.path.join(HIER, f["datei"]) if not os.path.isabs(f["datei"]) else f["datei"], nachweis=f["nachweis"]))
        q = quellen(seite, mid)
        aus.append(dict(id=mid, datum=datum, favorit=True, ueberschrift=erster.rstrip("."), haupt=p("haupt"),
                        woerter=p("haupt")[:-4] + ".woerter.json", haupt_text=haupt, haupt_sekunden=round(float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',p('haupt')],capture_output=True,text=True).stdout or 0),1), starts=starts, frage=m.get("frage", ""), seite_url=SEITE % (datum, mid), belegstellen=m.get("belegstellen", []),
                        artikel_url=q[0] if q else "", quellen=q))
    ziel = os.path.join(HIER, "daten", "news_auftrag_%s.json" % datum)
    if nur:   # nur eine Meldung ersetzt, Reihenfolge bleibt
        alt = json.load(open(ziel, encoding="utf-8")); neu = {x["id"]: x for x in aus}
        aus = [neu.pop(x["id"], x) for x in alt] + list(neu.values())
    json.dump(aus, open(ziel, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(aus), "Meldungen ->", ziel)


if __name__ == "__main__": main()

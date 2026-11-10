#!/usr/bin/env python3
"""Wort-Zeiten für das Mitlesen beim Vorlesen (Wunsch Nicolas 2026-11-08).

Für jede Meldungs-Aufnahme audio/<datum>/<id>.mp3 entsteht audio/<datum>/<id>.woerter.json:
[[start_in_sekunden, "Wort"], ...]. Die Seite macht damit das gerade gesprochene Wort dicker.
Läuft lokal mit whisper-cli (wie die Untertitel), kostet nichts.

Nutzung: python3 wortzeiten.py 2026-11-07            (fehlende Dateien erzeugen)
         python3 wortzeiten.py 2026-11-07 --neu      (alle neu)
         python3 wortzeiten.py --alle                (alle Ausgaben, nur fehlende)
"""
import json, os, subprocess, sys, tempfile

HIER = os.path.dirname(os.path.abspath(__file__))
MODELL = os.path.expanduser("~/NekoTools/models/ggml-large-v3-turbo.bin")
WHISPER = "/opt/homebrew/bin/whisper-cli"


def woerter(mp3):
    with tempfile.TemporaryDirectory() as tmp:
        wav = os.path.join(tmp, "a.wav")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp3, "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", wav], check=True)
        # whisper.cpp bricht mit --dtw manchmal ab (filter_width-Assert bei sehr kurzen Abschnitten, 2026-11-10):
        # dann mit 1,5 s Stille am Ende nochmal, zuletzt ohne DTW (Zeiten aus den Token-Offsets, etwas ungenauer)
        def lauf(datei, dtw=True):
            r = subprocess.run([WHISPER, "-m", MODELL, "-l", "de", "-nfa", *(["--dtw", "large.v3.turbo"] if dtw else []), "-ojf", "-of", os.path.join(tmp, "w"), "-f", datei],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return r.returncode == 0
        if not lauf(wav):
            lang = os.path.join(tmp, "b.wav")
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-af", "apad=pad_dur=1.5", lang], check=True)
            if not lauf(lang) and not lauf(wav, dtw=False):
                raise RuntimeError("Whisper ging nicht: " + mp3)
        d = json.load(open(os.path.join(tmp, "w.json"), encoding="utf-8"))
        for s in d.get("transcription", []):   # ohne DTW: Startzeit aus dem Token-Offset
            for t in s.get("tokens", []):
                if t.get("t_dtw", -1) < 0 and "offsets" in t: t["t_dtw"] = t["offsets"]["from"] / 10 + 8
    out = []
    for s in d.get("transcription", []):
        for t in s.get("tokens", []):
            tx = t.get("text", "")
            if tx.startswith("[_") or tx.startswith("<|") or t.get("t_dtw", -1) < 0:
                continue
            if tx.startswith(" ") or not out:
                out.append([round(max(0, t["t_dtw"] / 100 - 0.08), 2), tx.strip()])
            else:
                out[-1][1] += tx
    return [w for w in out if w[1]]


def ausgabe(datum, neu=False):
    ordner = os.path.join(HIER, "audio", datum)
    if not os.path.isdir(ordner):
        return 0
    n = 0
    for f in sorted(os.listdir(ordner)):
        if not f.endswith(".mp3") or f.endswith(".lofi.mp3"):
            continue
        ziel = os.path.join(ordner, f[:-4] + ".woerter.json")
        if os.path.exists(ziel) and not neu:
            continue
        w = woerter(os.path.join(ordner, f))
        json.dump(w, open(ziel, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
        print(f"{datum}/{f[:-4]}: {len(w)} Wörter")
        n += 1
    if n:   # Stand-Stempel: Seite lädt Audio UND Wortzeiten mit diesem Stempel, sonst passen nach Neusprechen alte Wortzeiten (24 h im Handy-Speicher) nicht mehr (2026-11-10)
        open(os.path.join(ordner, "stand.txt"), "w").write(str(int(__import__("time").time())))
    return n


if __name__ == "__main__":
    a = sys.argv[1:]
    neu = "--neu" in a
    if "--alle" in a:
        for d in sorted(os.listdir(os.path.join(HIER, "audio"))):
            ausgabe(d, neu)
    else:
        for d in [x for x in a if not x.startswith("--")]:
            ausgabe(d, neu)

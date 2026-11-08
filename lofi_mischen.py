#!/usr/bin/env python3
"""Lo-Fi-Fassung jeder Aufnahme (Wunsch Nicolas 2026-11-08): audio/<datum>/<id>.lofi.mp3 = Stimme + selbst erzeugtes Lo-Fi (audio/lofi.m4a).
Grund: Das iPhone spielt auf einer Webseite nicht zuverlässig zwei Audios gleichzeitig; die Musik stoppte dann immer wieder.
Die Musik läuft über die Meldungen der Ausgabe weiter (jede Meldung nimmt das nächste Stück der Schleife).

Nutzung: python3 lofi_mischen.py 2026-11-08        (fehlende erzeugen)
         python3 lofi_mischen.py 2026-11-08 --neu  (alle neu)
"""
import json, os, subprocess, sys

HIER = os.path.dirname(os.path.abspath(__file__))
LOFI = os.path.join(HIER, "audio", "lofi.m4a")


def dauer(f):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f], capture_output=True, text=True).stdout.strip())


def ausgabe(datum, neu=False):
    ordner = os.path.join(HIER, "audio", datum)
    if not os.path.isdir(ordner):
        return
    stimmen = sorted(f[:-4] for f in os.listdir(ordner) if f.endswith(".mp3") and not f.endswith(".lofi.mp3"))
    try:
        reihe = [i for i in json.load(open(os.path.join(ordner, "liste.json"))) if i in stimmen]
    except Exception:
        reihe = []
    reihe += [i for i in stimmen if i not in reihe]
    gesamt, ab = dauer(LOFI), 37.0
    for i in reihe:
        quelle, ziel = os.path.join(ordner, i + ".mp3"), os.path.join(ordner, i + ".lofi.mp3")
        d = dauer(quelle)
        if neu or not os.path.exists(ziel):
            subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", quelle, "-stream_loop", "-1", "-ss", f"{ab % gesamt:.2f}", "-i", LOFI,
                            "-filter_complex", f"[1]atrim=0:{d + 0.6:.2f},afade=t=in:d=0.8,afade=t=out:st={d - 0.6:.2f}:d=1.2[m];[0][m]amix=inputs=2:duration=longest:normalize=0",
                            "-ac", "1", "-ar", "48000", "-b:a", "64k", ziel], check=True)
            print(f"{datum}/{i}.lofi.mp3")
        ab += d + 1.0


if __name__ == "__main__":
    a = sys.argv[1:]
    for d in [x for x in a if not x.startswith("--")]:
        ausgabe(d, "--neu" in a)

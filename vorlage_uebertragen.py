#!/usr/bin/env python3
"""Überträgt alles außerhalb von <!-- AUSGABE-START --> … <!-- AUSGABE-ENDE --> aus vorlage.html in index.html und archiv/JJJJ-MM-TT.html
(Inhalt der Ausgabe bleibt). Danach seiten_bauen.py für Woche/Monat/Jahr/Shop/Neko/Rechtliches. (2026-11-10)"""
import os, glob, re, subprocess
HIER = os.path.dirname(os.path.abspath(__file__)); A, E = "<!-- AUSGABE-START -->", "<!-- AUSGABE-ENDE -->"
v = open(os.path.join(HIER, "vorlage.html"), encoding="utf-8").read(); kopf, fuss = v[:v.index(A)], v[v.index(E):]
for p in [os.path.join(HIER, "index.html")] + sorted(glob.glob(os.path.join(HIER, "archiv", "20*.html"))):
    s = open(p, encoding="utf-8").read()
    if A not in s or E not in s: print("übersprungen (keine Marker):", p); continue
    neu = kopf + s[s.index(A):s.index(E)] + fuss
    if neu != s: open(p, "w", encoding="utf-8").write(neu); print("übertragen:", os.path.relpath(p, HIER))
subprocess.run(["python3", os.path.join(HIER, "seiten_bauen.py")], check=True, stdout=subprocess.DEVNULL)

#!/usr/bin/env python3
"""Baut archiv/index.html aus allen archiv/JJJJ-MM-TT.html (neueste oben)."""
import os, re, datetime
ORDNER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "archiv")
TAGE = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
dateien = sorted((f for f in os.listdir(ORDNER) if re.fullmatch(r"\d{4}-\d{2}-\d{2}\.html", f)), reverse=True)
zeilen = []
for f in dateien:
    d = datetime.date.fromisoformat(f[:10])
    zeilen.append(f'    <a class="papier" href="{f}"><span class="tag">{TAGE[d.weekday()]}</span><span class="datum">{d:%d.%m.%Y}</span></a>')
html = """<!doctype html>
<html lang="de"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Archiv · Nekos Morgenzeitung</title><meta name="robots" content="noindex"><meta name="theme-color" content="#13306B">
<link rel="icon" type="image/png" href="../icon-192.png">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Libre+Caslon+Text:wght@700&family=Libre+Franklin:wght@700;800&display=swap">
<style>
body { margin: 0; min-height: 100vh; background-color: #13306B; color: #2E2B2A; font-family: "Libre Franklin", Arial, sans-serif;
  background-image: repeating-linear-gradient(0deg, rgba(232,220,198,0.07) 0 1px, transparent 1px 28px),
    repeating-linear-gradient(90deg, rgba(232,220,198,0.07) 0 1px, transparent 1px 28px); }
.wrap { max-width: 40rem; margin: 0 auto; padding: calc(2rem + env(safe-area-inset-top, 0px)) 16px 3rem; display: grid; gap: 1rem; }
h1 { justify-self: start; margin: 0 0 0.6rem; font-family: "Libre Caslon Text", Georgia, serif; font-size: 2rem; background: #E8DCC6; padding: 0.5rem 1rem; transform: rotate(-1deg);
  filter: drop-shadow(0 4px 0 rgba(0,0,0,0.28)) drop-shadow(6px 16px 18px rgba(2,6,20,0.62)); }
.papier { display: flex; justify-content: space-between; gap: 1rem; text-decoration: none; color: inherit; background: #EDE4D2; padding: 0.8rem 1rem;
  filter: drop-shadow(0 3px 0 rgba(0,0,0,0.25)) drop-shadow(4px 10px 12px rgba(2,6,20,0.55)); }
.papier:nth-of-type(odd) { transform: rotate(0.6deg); background: #E2D6BE; }
.papier:nth-of-type(even) { transform: rotate(-0.5deg); }
.tag { font-weight: 800; letter-spacing: 0.12em; text-transform: uppercase; color: #C8603A; font-size: 0.8rem; align-self: center; }
.datum { font-family: "Libre Caslon Text", Georgia, serif; font-weight: 700; font-size: 1.2rem; }
.zurueck { justify-self: start; margin-top: 1rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.08em; font-size: 0.85rem; text-decoration: none;
  background: #C8603A; color: #E8DCC6; padding: 0.5rem 0.9rem; transform: rotate(-1.5deg); }
</style></head><body><div class="wrap">
  <h1>Archiv</h1>
""" + "\n".join(zeilen) + """
  <a class="zurueck" href="../">← Heutige Ausgabe</a>
</div></body></html>
"""
open(os.path.join(ORDNER, "index.html"), "w", encoding="utf-8").write(html)
print(f"Archiv: {len(dateien)} Ausgaben")

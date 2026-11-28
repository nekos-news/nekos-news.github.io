#!/usr/bin/env python3
"""Baut archiv/index.html: nur die letzten 7 Tage (Wunsch Nicolas 2026-11-25), Älteres steht als Highlights in Monat und Jahr."""
import os, re, datetime
ORDNER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "archiv")
TAGE = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
dateien = sorted((f for f in os.listdir(ORDNER) if re.fullmatch(r"\d{4}-\d{2}-\d{2}\.html", f)), reverse=True)
neueste = datetime.date.fromisoformat(dateien[0][:10])
dateien = [f for f in dateien if (neueste - datetime.date.fromisoformat(f[:10])).days < 7]
zeilen = []
for f in dateien:
    d = datetime.date.fromisoformat(f[:10])
    zeilen.append(f'    <a class="papier riss archiv-tag" href="/archiv/{f[:-5]}"><span class="tag">{TAGE[d.weekday()]}</span><span class="datum">{d:%d.%m.%Y}</span></a>')
# Seit 2026-11-28 aus der gemeinsamen Vorlage (Menü, Logo, Raster, Halbton wie alle Seiten; vorher eigene schlichte Seite ohne Menü)
v = open(os.path.join(os.path.dirname(ORDNER), "vorlage.html"), encoding="utf-8").read()
a = v.index("<!-- AUSGABE-START -->") + len("<!-- AUSGABE-START -->"); b = v.index("<!-- AUSGABE-ENDE -->")
inhalt = """<div class="wrap">
  <section class="gruppe" id="archiv">
    <h2 class="zettel zettel-gross">Archiv</h2>
    <p class="archiv-info">Die letzten 7 Tage. Ältere Highlights findest du unter <a href="/monat.html">Dieser Monat</a> und <a href="/jahr.html">Dieses Jahr</a>.</p>
""" + "\n".join(zeilen) + """
  </section>
</div>"""
html = v[:a] + "\n" + inhalt + "\n" + v[b:]
html = html.replace("<title>Nekos News Shop</title>", "<title>Archiv · Nekos News Shop</title>", 1).replace('<head>', '<head><meta name="robots" content="noindex">', 1)
open(os.path.join(ORDNER, "index.html"), "w", encoding="utf-8").write(html)
print(f"Archiv: {len(dateien)} Ausgaben")

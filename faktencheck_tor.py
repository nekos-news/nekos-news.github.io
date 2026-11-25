#!/usr/bin/env python3
"""Tor vor dem Vertonen (Wunsch Nicolas 2026-11-25: „dass direkt nur die richtigen Texte gemacht werden“).

Merkt sich je Meldung, dass genau DIESER Text unabhängig geprüft ist. Wird danach ein Wort geändert, gilt die Meldung wieder als ungeprüft.
  faktencheck_tor.py                        prüfen; Fehlercode 1, solange etwas ungeprüft ist
  faktencheck_tor.py kurz m3 m11            nur diese Teile prüfen (Nachmittagslauf, Korrekturen)
  faktencheck_tor.py ok m1 "Kurznotiz"      m1 (oder kurz) ist in der jetzigen Fassung geprüft
Geprüft wird alles Sichtbare: Überschrift, Zusammenfassung, einfache Sprache, „Mehr anzeigen“, Marken, Quellen-Links.
Ablage: daten/news/<datum>/faktencheck.json (nur lokal, nicht online)."""
import hashlib, html, json, os, re, sys, datetime

HIER = os.path.dirname(os.path.abspath(__file__))


def teile():
    s = open(os.path.join(HIER, "index.html"), encoding="utf-8").read()
    datum = re.search(r'data-datum="([^"]+)"', s).group(1)
    t = {"kurz": re.search(r'<aside[^>]*id="kurz"[^>]*>(.*?)</aside>', s, re.S).group(1)}
    for i, x in re.findall(r'<article[^>]*id="(m\d+)"[^>]*>(.*?)</article>', s, re.S): t[i] = x
    def h(x):
        k = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", x))) + " ".join(re.findall(r'href="(http[^"]+)"', x))
        return hashlib.sha1(k.encode()).hexdigest()
    return datum, {i: h(x) for i, x in t.items()}


def main():
    datum, jetzt = teile()
    p = os.path.join(HIER, "daten", "news", datum, "faktencheck.json")
    d = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
    if sys.argv[1:2] == ["ok"]:
        i, notiz = sys.argv[2], sys.argv[3]
        if i not in jetzt: sys.exit("Unbekannt: " + i)
        d[i] = dict(h=jetzt[i], notiz=notiz, zeit=datetime.datetime.now().strftime("%H:%M"))
        os.makedirs(os.path.dirname(p), exist_ok=True); json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        return
    if sys.argv[1:]: jetzt = {i: jetzt[i] for i in sys.argv[1:]}   # nur diese Teile (Nachmittagslauf)
    offen = [i for i in jetzt if i not in d]; geaendert = [i for i in jetzt if i in d and d[i]["h"] != jetzt[i]]
    if offen: print("UNGEPRÜFT:", ",".join(offen))
    if geaendert: print("NACH DER PRÜFUNG GEÄNDERT:", ",".join(geaendert))
    if offen or geaendert: sys.exit(1)
    print("Faktencheck vollständig:", len(jetzt), "Teile, Ausgabe", datum)


if __name__ == "__main__": main()

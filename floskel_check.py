#!/usr/bin/env python3
"""Abwechslung prüfen (Wunsch Nicolas 2026-11-28: „wenn man die Sachen alle in Folge hört, nervt das voll, dass die Formulierungen zu gleich sind“).
Messung 24.–28.11.: „Kurz zur Einordnung“ in 40 von 57 Meldungen, „Der Haken“ in 19, „Heißt für dich“ in 7.
Regeln je Ausgabe: jede feste Übergangsfloskel höchstens 1-mal (Nicolas: die Etiketten mit Doppelpunkt nerven beim Hören); Satzanfänge (erste 2 Wörter) öfter als 3-mal nur als Hinweis;
„Mehr anzeigen“ zweier Meldungen hintereinander beginnt nie gleich. Exit 1 bei Verstoß.
Nutzung: python3 floskel_check.py [datei.html]   (Standard index.html)"""
import re, sys, html, collections
FLOSKELN = ["Kurz zur Einordnung", "Der Haken", "Heißt für dich", "Gute Nachricht", "Unterm Strich", "Zum Vergleich", "Dazu kommt",
            "Das bedeutet", "Wichtig ist", "Spannend ist", "Und genau deswegen", "Was heißt das", "Für dich heißt das", "Zum Hintergrund", "Außerdem"]
datei = sys.argv[1] if len(sys.argv) > 1 else "index.html"
s = open(datei, encoding="utf-8").read()
def klar(x): return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", x))).strip()
arts = re.findall(r'<article[^>]*id="(m\d+)"[^>]*>(.*?)</article>', s, re.S)
fehler = []; hinweise = []; zahl = collections.Counter(); anf = collections.Counter(); mehr_anf = []
for mid, a in arts:
    t = klar(re.sub(r'<p class="(einfach|quelle)">.*?</p>|<span class="rubrik">.*?</span>|<b[^>]*>KI-Zusammenfassung</b>', "", a, flags=re.S))
    for f in FLOSKELN: zahl[f] += len(re.findall(r"\b" + re.escape(f) + r"\b", t))
    for satz in re.split(r"(?<=[.!?:])\s+", t):
        w = satz.split()
        if len(w) >= 3 and w[0] != "Mehr": anf[" ".join(w[:2])] += 1
    m = re.search(r'<summary>.*?</summary>\s*<p>(.*?)</p>', a, re.S)
    mehr_anf.append((mid, " ".join(klar(m.group(1)).split()[:3]) if m else ""))
for f, n in zahl.items():
    if n > 1: fehler.append("„%s“ %d-mal (höchstens 1, besser als normaler Satz erzählen)" % (f, n))
for a, n in anf.most_common():
    if n > 3: hinweise.append("Satzanfang „%s …“ %d-mal – wenn es keine Namen sind, umformulieren" % (a, n))
for (m1, a1), (m2, a2) in zip(mehr_anf, mehr_anf[1:]):
    if a1 and a1.split()[:2] == a2.split()[:2]: fehler.append("„Mehr anzeigen“ von %s und %s beginnt gleich: „%s“" % (m1, m2, a2))
print("Abwechslung: %d Meldungen geprüft" % len(arts))
for f in fehler: print("  ZU GLEICH:", f)
for f in hinweise: print("  Hinweis:", f)
sys.exit(1 if fehler else 0)

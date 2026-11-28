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
    # Einheiten in Aufzählungen nur einmal (Nicolas 2026-11-28: „nervt, wie oft da Euro gesagt wird“)
    for satz in re.split(r"(?<=[.!?])\s+", t):
        for e in ("Euro", "Prozent", "Millionen", "Milliarden", "Menschen", "Jahre", "Jahren"):
            if len(re.findall(r"\b" + e + r"\b", satz)) > 2: fehler.append("%s: „%s“ %d-mal in einem Satz – Einheit nur einmal am Ende („Frankfurt 620, Stuttgart 600 und Köln 595 Euro“): %s …" % (mid, e, len(re.findall(r"\b" + e + r"\b", satz)), satz[:60]))
    # Gesprochen statt geschrieben (Nicolas 2026-11-28): eingeschobene Nebensätze mitten im Satz, Quellen mitten im Satz, Konjunktiv der indirekten Rede
    REL = r"(?:der|die|das|den|dem|deren|dessen|denen|welche[rsnm]?|wo|weil|obwohl|nachdem|wenn|dass|ob)"
    for satz in re.split(r"(?<=[.!?])\s+", t):
        ein = re.search(r"\w, (?:(?:über|mit|von|in|an|auf|für|bei|aus|nach|zu|vor) )?" + REL + r"\b[^,.;:]{3,90}, [a-zäöü]+\b", satz)
        WEITER = {"und", "aber", "oder", "also", "weil", "denn", "doch", "sondern", "dass", "wenn", "um", "ob", "sagt", "sagte", "sagen", "heißt", "etwa", "zum", "wie", "was", "wo", "bis"}
        if ein and ein.group(0).rsplit(" ", 1)[-1] in WEITER: ein = None   # Nebensatz am Ende, danach geht es mit „und“ usw. weiter: gesprochen in Ordnung
        if ein and not re.match(r"[^,]*\b(?:sagt|sagte|sagen|erklärt|meint|betont|kritisiert|warnt|fordert|schreibt|berichtet)\b", satz):
            fehler.append("%s: eingeschobener Nebensatz – umstellen, wie man es erzählen würde: „…%s…“" % (mid, ein.group(0)[:70]))
        if re.search(r"\b(?:will|soll|hat|ist|sind|haben|wird|werden|kann|muss)\s+laut\s", satz): hinweise.append("%s: Quelle mitten im Satz („… laut …“) – nach vorn oder eigener Satz: %s …" % (mid, satz[:60]))
        if re.search(r"\b(?:sagte|sagt|erklärte|meinte|betonte)\b[^.]{0,80}\b(?:sei|seien|habe|hätten|wäre|werde)\b", satz): hinweise.append("%s: indirekte Rede im Konjunktiv – gesprochen Indikativ (außer Vorwürfe): %s …" % (mid, satz[:60]))
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

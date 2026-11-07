#!/usr/bin/env python3
"""Baut die festen Seiten aus vorlage.html (nur der Bereich zwischen den AUSGABE-Markern wird ersetzt):
- woche.html / monat.html / jahr.html: die „krassesten“ Meldungen aus daten/artikel.json (Feld krass 1–10)
- shop.html (Platzhalter), links.html (Über mich, Kanäle, Hinweis)
Nutzung: python3 seiten_bauen.py   (täglich nach der neuen Ausgabe)"""
import os, json, html, datetime

HIER = os.path.dirname(os.path.abspath(__file__))
TAGE = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
MONATE = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"]

def vorlage():
    return open(os.path.join(HIER, "vorlage.html"), encoding="utf-8").read()

def seite(inhalt, titel, datei):
    s = vorlage()
    a = s.index("<!-- AUSGABE-START -->") + len("<!-- AUSGABE-START -->")
    b = s.index("<!-- AUSGABE-ENDE -->")
    s = s[:a] + "\n" + inhalt + "\n" + s[b:]
    s = s.replace("<title>Nekos Morgenzeitung</title>", f"<title>{html.escape(titel)} · Nekos Morgenzeitung</title>", 1)
    open(os.path.join(HIER, datei), "w", encoding="utf-8").write(s)

def kopf(zeile, titel, unter, neko="neko_zeitung.png"):
    return f'''<div class="wrap">
  <header class="kopf papier riss">
    <div class="zeile"><span>{zeile}</span></div>
    <h1 class="titel">{titel}</h1>
    <span class="unter">{unter}</span>
    <img class="neko" src="bilder/{neko}" alt="" width="110" height="150">
  </header>'''

FUSS = '''  <footer class="papier riss">
    <span>Kein Journalismus: Eine KI (Claude) fasst hier nur Berichte echter Journalist:innen zusammen und verlinkt die Originale. „Perspektive“ ist eine Einordnung aus linker Sicht, keine Tatsache.</span>
  </footer>
</div>'''

def bestenliste():
    pfad = os.path.join(HIER, "daten", "artikel.json")
    alle = json.load(open(pfad, encoding="utf-8")) if os.path.exists(pfad) else []
    if not alle: return
    heute = max(datetime.date.fromisoformat(a["datum"]) for a in alle)
    for datei, tage, anzahl, titel, unter in (
        ("woche.html", 7, 7, "Diese Woche", "Die krassesten Meldungen der letzten 7 Tage"),
        ("monat.html", 31, 10, "Dieser Monat", "Die krassesten Meldungen der letzten 30 Tage"),
        ("jahr.html", 366, 20, "Dieses Jahr", "Die krassesten Meldungen der letzten 12 Monate"),
    ):
        auswahl = [a for a in alle if (heute - datetime.date.fromisoformat(a["datum"])).days < tage]
        auswahl.sort(key=lambda a: (-a.get("krass", 0), a["datum"]), reverse=False)
        auswahl = sorted(auswahl, key=lambda a: (-a.get("krass", 0), -datetime.date.fromisoformat(a["datum"]).toordinal()))[:anzahl]
        teile = [kopf(f"Stand {heute:%d.%m.%Y}", titel, unter)]
        teile.append('  <section class="gruppe" id="liste">\n    <h2 class="zettel">Bestenliste</h2>')
        if not auswahl:
            teile.append('    <article class="papier riss"><p>Noch keine Meldungen gesammelt.</p></article>')
        for i, a in enumerate(auswahl, 1):
            d = datetime.date.fromisoformat(a["datum"])
            teile.append(f'''    <article class="papier riss">
      <span class="rubrik"><span class="platz">{i}</span> {html.escape(a.get("rubrik", ""))} · {TAGE[d.weekday()]}, {d:%d.%m.}</span>
      <h3>{html.escape(a["titel"])}</h3>
      <p class="fakt"><b>Fakt</b>{html.escape(a.get("fakt", ""))}</p>
      <p class="quelle">{a.get("quellen_html", "")} · <a href="archiv/{a["datum"]}.html#{a["id"]}">Zur Ausgabe</a></p>
    </article>''')
        teile.append("  </section>")
        teile.append('  <p class="liste-info papier riss" style="padding:0.6rem 0.8rem">Wie „krass“ eine Meldung ist (1–10), schätzt die KI jeden Morgen ein: Tragweite, Betroffene, Ungerechtigkeit, Überraschung. Das ist eine Einschätzung, keine Messung.</p>')
        teile.append(FUSS)
        seite("\n".join(teile), titel, datei)

def shop():
    inhalt = kopf("Bald", "Shop", "Hoodies und antifaschistische Sticker", "neko_lupe.png") + '''
  <section class="gruppe" id="shop">
    <h2 class="zettel">Kommt bald</h2>
    <article class="papier riss">
      <span class="rubrik">In Arbeit</span>
      <h3>Nekos_News-Hoodie</h3>
      <p>Das Design steht schon. Sobald es bestellbar ist, findest du es hier.</p>
    </article>
    <article class="papier riss">
      <span class="rubrik">In Arbeit</span>
      <h3>Antifaschistische Sticker</h3>
      <p>Sticker im Papiercollage-Look. Infos folgen auf Instagram.</p>
      <p class="quelle"><a href="https://www.instagram.com/nekos_news/">@nekos_news auf Instagram</a></p>
    </article>
  </section>
''' + FUSS
    seite(inhalt, "Shop", "shop.html")

def links():
    s = vorlage()
    import re
    kanaele = re.search(r'<div class="kanaele">(.*?)</div>', s, re.S).group(1).strip()
    inhalt = kopf("Über mich", "Neko &amp; Nekos_News", "Links, Kanäle und worum es hier geht", "neko_zeitung.png") + f'''
  <section class="gruppe" id="links">
    <h2 class="zettel">Über mich</h2>
    <article class="papier riss">
      <p>Ich bin Neko und mache Nekos_news: politische Kurzvideos für Leute zwischen 20 und 35, links, antifaschistisch und mit Fakten, damit man mich auch dann nicht schlechtreden kann, wenn man anderer Meinung ist.</p>
    </article>
    <h2 class="zettel">Meine Kanäle</h2>
    <article class="papier riss">
      <div class="kanaele" style="justify-content:flex-start">{kanaele}</div>
    </article>
    <h2 class="zettel">Wichtig</h2>
    <article class="papier riss">
      <span class="rubrik">⚠ Kein Journalismus</span>
      <p>Ich bin kein Journalist und mache auf dieser Seite keinen eigenen Journalismus. Die Morgenzeitung fasst nur die Arbeit echter Journalistinnen und Journalisten zusammen und verlinkt die Originalartikel. Zusammengestellt wird sie jeden Morgen automatisch von einer KI (Claude); ich prüfe die Meldungen nicht selbst. Die Abschnitte „Perspektive“ sind eine Einordnung aus linker Sicht, keine Tatsachen.</p>
    </article>
  </section>
''' + FUSS
    seite(inhalt, "Über mich & Links", "links.html")

if __name__ == "__main__":
    bestenliste(); shop(); links()
    print("Seiten gebaut: woche, monat, jahr, shop, links")

#!/usr/bin/env python3
"""Baut die festen Seiten aus vorlage.html (nur der Bereich zwischen den AUSGABE-Markern wird ersetzt):
- woche.html / monat.html / jahr.html: die „krassesten“ Meldungen aus daten/artikel.json (Feld krass 1–10)
- shop.html (Platzhalter), links.html (Über mich, Kanäle, Hinweis)
Nutzung: python3 seiten_bauen.py   (täglich nach der neuen Ausgabe)"""
import os, re, json, html, datetime

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
    s = s.replace("<title>Nekos News Shop</title>", f"<title>{html.escape(titel)} · Nekos News Shop</title>", 1)
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
    <span>Kein Journalismus: Eine KI (Claude) fasst hier nur Berichte echter Journalist:innen zusammen und verlinkt die Originale.</span>
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
    inhalt = kopf("Vorschau", "Shop", "Bald bestellbar: Hoodie, Kappe und Sticker", "neko_lupe.png") + '''
  <section class="gruppe" id="shop">
    <h2 class="zettel">Kommt bald</h2>
    <article class="papier riss produkt" id="hoodie">
      <span class="rubrik">Hoodie · Vorschau</span>
      <h3>STOP – F*cking Fascists</h3>
      <div class="produktbilder"><img src="bilder/shop/hoodie_hinten.jpg" alt="Hoodie Rückseite mit Stoppschild „STOP – F*cking Fascists“ und #NIEWIEDERISTJETZT" loading="lazy"><img src="bilder/shop/hoodie_vorne.jpg" alt="Hoodie Vorderseite, dazu Kappe „MENSCH.“" loading="lazy"></div>
      <p>Schwarzer Hoodie mit großem Stoppschild auf dem Rücken, weißen Streifen an Kapuze und Ärmeln und #NIEWIEDERISTJETZT.</p>
      <span class="marke">Noch nicht bestellbar</span>
    </article>
    <article class="papier riss produkt" id="kappe">
      <span class="rubrik">Kappe · Vorschau</span>
      <h3>MENSCH.</h3>
      <div class="produktbilder eins"><img src="bilder/shop/kappe.jpg" alt="Schwarze Kappe mit Aufschrift „MENSCH.“" loading="lazy"></div>
      <p>Schwarze Kappe mit weißer Aufschrift „MENSCH.“.</p>
      <span class="marke">Noch nicht bestellbar</span>
    </article>
    <article class="papier riss produkt" id="sticker">
      <span class="rubrik">Sticker · Vorschau</span>
      <h3>You are the product</h3>
      <div class="produktbilder eins sticker"><img src="bilder/shop/sticker_product.jpg" alt="Sticker: „You are the product“ mit Strichcode" loading="lazy"></div>
      <p>Schwarz-weißer Sticker mit Strichcode: „You are the product“.</p>
      <span class="marke">Noch nicht bestellbar</span>
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
      <p>Ich bin kein Journalist und mache auf dieser Seite keinen eigenen Journalismus. Die Morgenzeitung fasst nur die Arbeit echter Journalistinnen und Journalisten zusammen und verlinkt die Originalartikel. Zusammengestellt wird sie jeden Morgen automatisch von einer KI (Claude); ich prüfe die Meldungen nicht selbst.</p>
    </article>
  </section>
''' + FUSS
    seite(inhalt, "Über mich & Links", "links.html")

def neko():
    inhalt = '''<div class="wrap">
  <section class="gruppe" id="neko">
    <h2 class="zettel zettel-gross">Neko</h2>
    <article class="papier riss vita">
      <span class="profil"><img src="bilder/profilbild.jpg" alt="Nekos Instagram-Profilbild" width="220" height="220"></span>
      <h3>Hi, ich bin Neko.</h3>
      <p>Ich mache <mark class="strich">Nekos_news</mark>: politische Kurzvideos auf Instagram, TikTok und YouTube. Links, antifaschistisch und mit Fakten, so dass man mich auch dann nicht schlechtreden kann, wenn man anders denkt.</p>
      <p>Mich interessiert, was <mark class="kreis">nicht zusammenpasst</mark>: Ungerechtigkeit, Doppelmoral und Politik, die am Ende ganz normale Leute trifft. Ich erzähle das so, wie ich es einem Freund erzählen würde, nicht wie eine Nachrichtensendung.</p>
      <div class="kanaele vita-kanaele">KANAELE<a class="anfrage" href="mailto:neko.anfragen@gmail.com?subject=Anfrage%20an%20Neko"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 5 H21 A1 1 0 0 1 22 6 V18 A1 1 0 0 1 21 19 H3 A1 1 0 0 1 2 18 V6 A1 1 0 0 1 3 5 Z M4 7.2 V17 H20 V7.2 L12 12.6 Z M5.6 7 L12 11.2 L18.4 7 Z"/></svg>Anfragen</a></div>
    </article>
  </section>
  <section class="gruppe" id="content">
    <h2 class="zettel zettel-gross">Content</h2>
    <div class="filter" id="filter" role="group" aria-label="Nach Thema filtern"></div>
    <div class="raster" id="raster"></div>
  </section>
''' + FUSS
    k = re.search(r'<div class="kanaele">(.*?)</div>', vorlage(), re.S).group(1).strip()
    seite(inhalt.replace("KANAELE", k), "Neko", "neko.html")
    # Auf der Profilseite kein „Kein Journalismus“-Hinweis (Wunsch Nicolas)
    pfad = os.path.join(HIER, "neko.html"); t = open(pfad, encoding="utf-8").read()
    t = re.sub(r'\s*<p class="hinweis">.*?</p>', '', t, count=1, flags=re.S)
    t = re.sub(r'\s*<footer class="papier riss">\s*<span>Kein Journalismus.*?</footer>', '', t, count=1, flags=re.S)
    open(pfad, "w", encoding="utf-8").write(t)

if __name__ == "__main__":
    bestenliste(); shop(); neko()
    print("Seiten gebaut: woche, monat, jahr, shop, neko")

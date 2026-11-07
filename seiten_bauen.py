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
      <h3>STOP – F*cking Fascists</h3>
      <div class="produktbilder"><img src="bilder/shop/hoodie_hinten.jpg" alt="Hoodie Rückseite mit Stoppschild „STOP – F*cking Fascists“ und #NIEWIEDERISTJETZT" loading="lazy"><img src="bilder/shop/hoodie_vorne.jpg" alt="Hoodie Vorderseite, dazu Kappe „MENSCH.“" loading="lazy"></div>
      <p data-einfach="Ein schwarzer Pulli mit Kapuze. Hinten ist ein großes Stopp-Schild gegen Nazis.">Schwarzer Hoodie mit großem Stoppschild auf dem Rücken, weißen Streifen an Kapuze und Ärmeln und #NIEWIEDERISTJETZT.</p>
      <span class="marke" data-einfach="Kann man noch nicht kaufen">Noch nicht bestellbar</span>
    </article>
    <article class="papier riss produkt" id="kappe">
      <h3>MENSCH.</h3>
      <div class="produktbilder eins"><img src="bilder/shop/kappe.jpg" alt="Schwarze Kappe mit Aufschrift „MENSCH.“" loading="lazy"></div>
      <p data-einfach="Eine schwarze Mütze mit Schirm. Darauf steht: MENSCH.">Schwarze Kappe mit weißer Aufschrift „MENSCH.“.</p>
      <span class="marke" data-einfach="Kann man noch nicht kaufen">Noch nicht bestellbar</span>
    </article>
    <article class="papier riss produkt" id="sticker">
      <h3>You are the product</h3>
      <div class="produktbilder eins sticker"><img src="bilder/shop/sticker_product.jpg" alt="Sticker: „You are the product“ mit Strichcode" loading="lazy"></div>
      <p data-einfach="Ein Aufkleber. Darauf steht: Du bist das Produkt.">Schwarz-weißer Sticker mit Strichcode: „You are the product“.</p>
      <span class="marke" data-einfach="Kann man noch nicht kaufen">Noch nicht bestellbar</span>
    </article>
  </section>
  <button type="button" class="wagen" aria-label="Einkaufswagen"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M2 3 H5 L7.4 14.2 A1.5 1.5 0 0 0 8.9 15.4 H18.6 A1.5 1.5 0 0 0 20 14.3 L21.8 7 H6.3 M9 20.5 A1.6 1.6 0 1 0 9 17.3 A1.6 1.6 0 1 0 9 20.5 Z M18 20.5 A1.6 1.6 0 1 0 18 17.3 A1.6 1.6 0 1 0 18 20.5 Z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/></svg><span class="anzahl">0</span><span class="wagen-info" hidden>Bald bestellbar</span></button>
''' + FUSS
    seite(inhalt, "Shop", "shop.html")
    ohne_ki("shop.html")  # Shop ist keine KI-Zusammenfassung (Wunsch Nicolas 2026-11-08)

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

def ohne_ki(datei):
    """Entfernt den „Kein Journalismus“-Hinweis oben und die KI-Fußzeile (Neko- und Shop-Seite)."""
    pfad = os.path.join(HIER, datei); t = open(pfad, encoding="utf-8").read()
    t = re.sub(r'\s*<p class="hinweis">.*?</p>', '', t, count=1, flags=re.S)
    t = re.sub(r'\s*<footer class="papier riss">\s*<span>Kein Journalismus.*?</footer>', '', t, count=1, flags=re.S)
    open(pfad, "w", encoding="utf-8").write(t)

PATREON = ""  # Link zu Nekos Patreon, sobald bekannt (leer = Knopf ausgeblendet)

def neko():
    patreon = (f'<a class="patreon" href="{PATREON}" rel="noopener"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="15" cy="9.5" r="6.5"/><rect x="2.5" y="3" width="3.6" height="18"/></svg>Patreon</a>' if PATREON else "")
    inhalt = '''<div class="wrap">
  <section class="gruppe" id="neko">
    <article class="papier riss vita">
      <div class="vita-kopf">
        <span class="profil"><img src="bilder/profilbild.jpg" alt="Nekos Instagram-Profilbild" width="220" height="220"></span>
        <div class="vita-gruss">
          <h3>Hi, ich bin [Neko]</h3>
          <span class="beruf" data-einfach="Ich habe Design studiert">Studierter Kommunikationsdesigner</span>
        </div>
      </div>
      <p data-einfach="Ich mache kurze Videos über Politik. Auf Instagram, TikTok und YouTube. Ich erkläre, was gerade passiert. So, wie ich es einem Freund erzählen würde.">Ich mache <mark class="strich">Nekos_news</mark>: kurze Videos über Politik auf Instagram, TikTok und YouTube. Ich erzähl dir, was gerade passiert, so wie ich es einem Freund erzählen würde: ehrlich, mit Fakten und ohne Nachrichtensprecher-Ton.</p>
      <p data-einfach="Mich interessiert, wenn etwas nicht fair ist. Ich bin gegen Nazis. Ich möchte auch Menschen erreichen, die anders denken. Schön, dass du hier bist.">Mich interessiert, was <mark class="kreis">nicht zusammenpasst</mark>: wenn Politik das eine verspricht und das andere macht, oder wenn am Ende wieder die ganz normalen Leute zahlen. Ich bin links und klar gegen Rechtsextremismus, will aber auch die erreichen, die das anders sehen. Schön, dass du hier bist.</p>
      <div class="kanaele vita-kanaele">KANAELEPATREON<a class="anfrage" href="mailto:neko.anfragen@gmail.com?subject=Anfrage%20an%20Neko"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 5 H21 A1 1 0 0 1 22 6 V18 A1 1 0 0 1 21 19 H3 A1 1 0 0 1 2 18 V6 A1 1 0 0 1 3 5 Z M4 7.2 V17 H20 V7.2 L12 12.6 Z M5.6 7 L12 11.2 L18.4 7 Z"/></svg>Anfragen</a></div>
    </article>
  </section>
  <section class="gruppe" id="content">
    <h2 class="zettel zettel-gross">Content</h2>
    <div class="filter" id="filter" role="group" aria-label="Nach Thema filtern"></div>
    <div class="raster" id="raster"></div>
  </section>
''' + FUSS
    k = re.search(r'<div class="kanaele">(.*?)</div>', vorlage(), re.S).group(1).strip()
    seite(inhalt.replace("KANAELE", k).replace("PATREON", patreon), "Neko", "neko.html")
    # Auf der Profilseite kein „Kein Journalismus“-Hinweis (Wunsch Nicolas)
    ohne_ki("neko.html")

def datenschutz():
    """Datenschutzerklärung (Entwurf 2026-11-08, ohne Gewähr; vor dem Shop von Rechtstext-Anbieter prüfen lassen)."""
    abschnitte = [
        ("Kurz gesagt", "Diese Seite setzt keine Cookies, nutzt kein Tracking und keine Analyse-Werkzeuge. Schriften, Bilder und Audios liegen auf dieser Seite selbst. Daten an Dritte gehen nur, wenn du selbst etwas antippst, das ausdrücklich zu einem anderen Anbieter führt."),
        ("Verantwortlich", "Verantwortlich für diese Seite ist der Betreiber, siehe Impressum. Kontakt: <a href=\"mailto:neko.anfragen@gmail.com\">neko.anfragen@gmail.com</a>."),
        ("Hosting", "Die Seite liegt bei GitHub Pages (GitHub Inc., USA) und Cloudflare Pages (Cloudflare Inc., USA). Beim Aufruf verarbeiten diese Anbieter technisch nötige Daten wie IP-Adresse, Zeitpunkt und aufgerufene Datei, um die Seite auszuliefern und vor Angriffen zu schützen. Rechtsgrundlage ist Art. 6 Abs. 1 lit. f DSGVO (berechtigtes Interesse an einer sicheren, funktionierenden Seite). Für die Übermittlung in die USA stützen sich die Anbieter auf das EU-US Data Privacy Framework bzw. Standardvertragsklauseln."),
        ("Einstellungen im Browser", "Was du im Hilfe-Menü einstellst (z. B. Größer, Kontrast, Migräne-Modus) und ob du das Intro schon gesehen hast, wird nur in deinem eigenen Browser gespeichert (localStorage/sessionStorage) und nicht an uns übertragen. Das ist für die von dir gewünschte Funktion unbedingt nötig (§ 25 Abs. 2 Nr. 2 TDDDG). Du kannst es jederzeit in deinem Browser löschen."),
        ("YouTube-Video (Gen Z)", "Das Gameplay-Video im Hilfe-Menü lädt erst, wenn du nach einem Hinweis auf „Video laden“ tippst. Dann wird es über youtube-nocookie.com von Google Ireland Ltd. geladen; dabei gehen Daten wie deine IP-Adresse an Google, auch in die USA. Rechtsgrundlage ist deine Einwilligung (Art. 6 Abs. 1 lit. a DSGVO), die du durch das Antippen erteilst. Schließt du das Fenster, wird nichts weiter geladen."),
        ("Links zu anderen Seiten", "Links zu Instagram, TikTok, YouTube und zu den Originalartikeln der Medien führen auf deren Seiten. Erst dort gelten deren Datenschutzregeln."),
        ("Anfragen per E-Mail", "Schreibst du an neko.anfragen@gmail.com, werden deine Nachricht und deine Adresse genutzt, um dir zu antworten. Das Postfach liegt bei Google (Gmail). Rechtsgrundlage ist Art. 6 Abs. 1 lit. b bzw. f DSGVO. Die Mails werden gelöscht, wenn sie nicht mehr gebraucht werden."),
        ("Deine Rechte", "Du hast das Recht auf Auskunft, Berichtigung, Löschung, Einschränkung der Verarbeitung, Datenübertragbarkeit und Widerspruch sowie das Recht, eine erteilte Einwilligung zu widerrufen. Außerdem kannst du dich bei einer Datenschutz-Aufsichtsbehörde beschweren, z. B. bei der Landesbeauftragten für Datenschutz und Informationsfreiheit Nordrhein-Westfalen."),
    ]
    teile = ['<div class="wrap">\n  <section class="gruppe" id="datenschutz">\n    <h2 class="zettel zettel-gross">Datenschutz</h2>']
    for titel, text in abschnitte:
        teile.append(f'    <article class="papier riss"><h3>{titel}</h3><p>{text}</p></article>')
    teile.append('    <p class="liste-info papier riss" style="padding:0.6rem 0.8rem">Stand: November 2026</p>\n  </section>\n</div>')
    seite("\n".join(teile), "Datenschutz", "datenschutz.html")
    ohne_ki("datenschutz.html")

if __name__ == "__main__":
    bestenliste(); shop(); neko(); datenschutz()
    print("Seiten gebaut: woche, monat, jahr, shop, neko")

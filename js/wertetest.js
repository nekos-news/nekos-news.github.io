/* Werte-Test „Wie tickst du?“ (Wunsch Nicolas 2026-11-09): psychologische Alltagsszenen statt Wahl-O-Mat-Thesen.
   Antworten nur mit Regler (1–10) oder Ja/Nein, am Ende Gewichtung, Netzdiagramm und Nähe zu Parteien.
   Alles bleibt im Browser (localStorage), nichts wird gesendet.
   Partei-Werte sind eine EINSCHÄTZUNG von Claude anhand der Grundwerte in den Wahlprogrammen 2025, von Nicolas zu prüfen. */
(function () {
  var ACHSEN = {
    f: { name: 'Mitgefühl', hoch: 'Das Wohl anderer liegt dir spürbar am Herzen, auch wenn es dich etwas kostet.', tief: 'Du schaust zuerst auf dich und dein Umfeld und erwartest, dass andere das auch tun.' },
    g: { name: 'Sozial vs. Markt', hoch: 'Gerechte Verteilung ist dir wichtiger als freier Markt: Wer wenig hat, soll aufgefangen werden.', tief: 'Leistung und freier Markt sind dir wichtiger: Wer mehr schafft, darf auch mehr haben.' },
    o: { name: 'Offenheit', hoch: 'Du magst Neues und Veränderung und stellst Regeln gern infrage.', tief: 'Dir sind Stabilität, Bewährtes und klare Regeln wichtig.' },
    k: { name: 'Wir-Gefühl', hoch: 'Dein „Wir“ ist weit: Menschen anderswo zählen für dich fast so viel wie die nebenan.', tief: 'Dein „Wir“ ist eher eng: Familie, Region und Land kommen für dich zuerst.' },
    z: { name: 'Zukunft', hoch: 'Du denkst langfristig und verzichtest heute auch mal für morgen, etwa beim Klima.', tief: 'Dir ist das Hier und Jetzt wichtiger als das, was in 30 Jahren ist.' }
  };
  /* [Achse, Szene, linkes Ende, rechtes Ende, +1 = rechts zählt hoch / -1 = links zählt hoch] oder Ja/Nein: [Achse, Frage, 'jn', +1 = Ja zählt hoch] */
  var FRAGEN = [
    ['f', 'Im Bus sitzt jemand, der sichtbar weint. Was machst du?', 'Ich lasse die Person in Ruhe', 'Ich frage, ob alles okay ist', 1],
    ['g', 'Eine Kollegin verdient mehr, weil sie besser verhandelt hat, nicht weil sie mehr leistet.', 'Fair, wer verhandelt, gewinnt', 'Unfair, gleiche Arbeit, gleicher Lohn', 1],
    ['o', 'Dein Lieblingscafé wird von neuen Besitzern komplett umgestaltet.', 'Schade, es war gut so', 'Spannend, mal sehen', 1],
    ['k', 'Bei einer Katastrophe in einem weit entfernten Land sterben viele Menschen.', 'Berührt mich fast wie etwas in meiner Stadt', 'Berührt mich deutlich weniger', -1],
    ['z', 'Du bekommst unerwartet 1.000 Euro.', 'Ich gönne mir jetzt etwas Schönes', 'Ich lege das meiste für später weg', 1],
    ['f', 'Eine fremde Person hat glaubhaft ihr Portemonnaie verloren und fragt dich nach 20 Euro für die Heimfahrt. Gibst du ihr das Geld?', 'jn', 1],
    ['g', 'Jemand hat ein Millionenvermögen geerbt, ohne je dafür gearbeitet zu haben.', 'Sein gutes Recht', 'Davon sollte mehr an die Allgemeinheit gehen', 1],
    ['o', 'Ein Freund erzählt, dass er seinen sicheren Job kündigt, um etwas ganz Neues zu machen.', 'Mutig, mach das', 'Ganz schön leichtsinnig', -1],
    ['k', 'In deine Straße zieht eine Familie, die kaum Deutsch spricht.', 'Ich gehe auf sie zu', 'Ich warte erst mal ab', -1],
    ['z', 'Ein Flug in den Urlaub ist halb so teuer wie der Zug und viel schneller.', 'Klar, Flug', 'Ich nehme trotzdem den Zug', 1],
    ['f', 'Ein Kollege macht ständig Fehler, weil er privat eine schwere Zeit hat.', 'Ich fange ihn eine Weile auf', 'Arbeit ist Arbeit, er muss das trennen', -1],
    ['g', 'Wer Vollzeit arbeitet, soll davon gut leben können, auch wenn Produkte dadurch etwas teurer werden. Stimmst du zu?', 'jn', 1],
    ['o', 'Du bist auf einer Feier und kennst dort niemanden.', 'Ich lerne gern neue Leute kennen', 'Ich fühle mich eher unwohl', -1],
    ['k', 'Eine Firma kann 100 Jobs in Deutschland retten, wenn sie dafür 300 Jobs in einem ärmeren Land streicht.', 'Richtig so, erst mal wir', 'Unfair gegenüber den anderen', 1],
    ['z', 'Eine neue Regel würde deinen Alltag etwas teurer machen, das Klima in 30 Jahren aber deutlich verbessern.', 'Würde ich mittragen', 'Ist mir zu viel', -1],
    ['f', 'Vor dem Supermarkt bittet jemand um etwas Kleingeld.', 'Ich gebe meistens etwas', 'Ich gehe meistens vorbei', -1],
    ['g', 'Zwei Menschen fahren gleich schnell geblitzt, einer ist reich, einer arm. Wie sollte die Strafe sein?', 'Gleich hoch für beide', 'Nach Einkommen gestaffelt', 1],
    ['o', 'In der Schule wird darüber gesprochen, dass Jungs auch Kleider tragen und Mädchen Fußball spielen können.', 'Finde ich gut', 'Gehört eher nicht in die Schule', -1],
    ['k', 'Wäre es für dich okay, wenn ein Teil deiner Steuern in Hilfe für Menschen in ärmeren Ländern fließt?', 'jn', 1],
    ['z', 'Du kannst heute 100 Euro bekommen oder in 3 Jahren 180 Euro.', 'Heute 100', 'In 3 Jahren 180', 1],
    ['f', 'Deine Nachbarin ist alt und allein. Du hast selbst wenig Zeit.', 'Ich schaue trotzdem ab und zu vorbei', 'Dafür sind andere zuständig', -1],
    ['g', 'Ein Supermarkt erhöht die Preise, einfach weil er es kann. Sein Gewinn steigt stark.', 'So funktioniert Markt', 'Da sollte jemand eingreifen', 1],
    ['o', 'Jemand stellt eine Regel infrage, die schon immer so war.', 'Gut so, Regeln müssen sich erklären', 'Nervt, es hat doch funktioniert', -1],
    ['k', 'Ein Mensch aus einem anderen Land bekommt eine Hilfe, die deine Familie nicht bekommt.', 'Das ärgert mich', 'Wenn er sie mehr braucht, okay', 1],
    ['z', 'Würdest du weniger Fleisch essen, wenn du sicher wüsstest, dass es wirklich etwas bringt?', 'jn', 1],
    ['f', 'Jemand wird in der Bahn beleidigt.', 'Ich mische mich ein oder hole Hilfe', 'Ich halte mich raus', -1],
    ['g', 'Wer viel Geld hat, hat das meistens …', '… selbst verdient', '… auch viel Glück gehabt', 1],
    ['o', 'Deine Stadt will eine Hauptstraße für ein Jahr in eine Fußgängerzone verwandeln.', 'Lass es uns ausprobieren', 'Lieber alles so lassen', -1],
    ['k', 'Wem fühlst du dich mehr verbunden?', 'Menschen aus meiner Region', 'Menschen weltweit, die ähnlich denken wie ich', 1],
    ['z', 'An deinem Wohnort soll ein Windrad in Sichtweite gebaut werden.', 'Okay, irgendwo muss der Strom herkommen', 'Bitte nicht hier', -1],
    ['f', 'Hast du in den letzten 12 Monaten etwas gespendet, egal ob Geld, Zeit oder Sachen?', 'jn', 1],
    ['g', 'Ein Freund lebt von Grundsicherung und kommt kaum über die Runden.', 'Er sollte sich mehr anstrengen', 'Das System sollte ihn besser auffangen', 1],
    ['o', 'Wie fühlst du dich, wenn sich in der Gesellschaft viel und schnell verändert?', 'Unwohl, ich brauche Stabilität', 'Gut, Wandel ist normal', 1],
    ['k', 'Bei einem Länderspiel gewinnt die andere Mannschaft verdient.', 'Ich gönne es ihnen', 'Ärgert mich trotzdem richtig', -1],
    ['z', 'Eine Partei verspricht dir sofort mehr Geld, dafür steigen die Schulden für die nächste Generation.', 'Nehme ich', 'Lieber nicht', 1],
    ['f', 'Vor dir an der Kasse braucht eine ältere Person sehr lange.', 'Ich bleibe geduldig', 'Ich werde ungeduldig', -1]
  ];
  /* EINSCHÄTZUNG (keine Messung): Grundwerte der Parteien auf denselben Achsen, 0–100, anhand der Wahlprogramme 2025. Von Nicolas zu prüfen. */
  var PARTEIEN = [
    { n: 'Die Linke', f: 85, g: 92, o: 80, k: 85, z: 75 },
    { n: 'Grüne', f: 75, g: 70, o: 88, k: 85, z: 95 },
    { n: 'SPD', f: 70, g: 72, o: 62, k: 65, z: 60 },
    { n: 'Volt', f: 70, g: 58, o: 90, k: 92, z: 85 },
    { n: 'CDU/CSU', f: 45, g: 35, o: 30, k: 42, z: 42 },
    { n: 'FDP', f: 38, g: 18, o: 65, k: 55, z: 45 },
    { n: 'BSW', f: 62, g: 80, o: 25, k: 35, z: 35 },
    { n: 'AfD', f: 22, g: 38, o: 8, k: 8, z: 12 }
  ];
  var REIHE = ['f', 'g', 'o', 'k', 'z'], SPEICHER = 'mz-wertetest', PSTAND = '';
  /* Aktuelle Partei-Werte aus daten/parteien.json (wird montags anhand aktueller Forderungen geprüft); die Liste oben ist nur der Rückfall */
  fetch('/daten/parteien.json', { cache: 'no-cache' }).then(function (r) { return r.ok ? r.json() : null; }).then(function (d) { if (d && d.parteien && d.parteien.length) { PARTEIEN = d.parteien; PSTAND = d.stand || ''; } }).catch(function () {});

  function lade() { try { return JSON.parse(localStorage.getItem(SPEICHER) || '{}'); } catch (e) { return {}; } }
  function merke(st) { try { localStorage.setItem(SPEICHER, JSON.stringify(st)); } catch (e) {} }
  function esc(t) { return String(t).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }

  var css = document.createElement('style');
  css.textContent = [
    '.wt-grund{position:fixed;inset:0;z-index:60;overflow-y:auto;-webkit-overflow-scrolling:touch;background:rgba(4,8,20,0.9);padding:calc(env(safe-area-inset-top,0px) + 1.2rem) 1rem 3rem;display:grid;justify-items:center;align-content:start}',
    '.wt-grund[hidden]{display:none}',
    '.wt-karte{position:relative;width:min(30rem,100%);margin-top:2.6rem;padding:1.3rem 1.2rem 1.2rem;color:var(--anthrazit);background-color:var(--papier-3,#e8dcc6);background-image:var(--faser);filter:drop-shadow(0 3px 0 rgba(0,0,0,0.25)) drop-shadow(3px 10px 12px rgba(2,6,20,0.5));transform:rotate(-0.6deg)}',
    '.wt-zu{position:fixed;top:calc(env(safe-area-inset-top,0px) + 0.7rem);right:0.9rem;z-index:61;width:2.5rem;height:2.5rem;border:0;border-radius:50%;background:var(--rost,#C8603A);color:var(--creme,#f4ead8);font:800 1.3rem/1 var(--sans);cursor:pointer}',
    '.wt-stand{font:400 0.72rem var(--maschine);color:var(--mittelgrau,#7a7268);display:flex;justify-content:space-between;margin-bottom:0.4rem}',
    '.wt-balken{height:5px;background:rgba(46,43,42,0.12);margin-bottom:1rem}.wt-balken b{display:block;height:100%;background:var(--rost,#C8603A);transition:width .3s}',
    '.wt-szene{font:500 1.12rem/1.45 var(--lesen);margin:0 0 1.3rem}',
    '.wt-pole{display:flex;justify-content:space-between;gap:1rem;font:700 0.78rem/1.25 var(--sans);margin-bottom:0.5rem}.wt-pole span:last-child{text-align:right}',
    '.wt-regler{width:100%;accent-color:var(--rost,#C8603A);height:2rem;margin:0}',
    '.wt-zahl{text-align:center;font:400 0.8rem var(--maschine);color:var(--mittelgrau,#7a7268);margin:0.2rem 0 1rem}',
    '.wt-knoepfe{display:flex;gap:0.6rem;flex-wrap:wrap;justify-content:center}',
    '.wt-knopf{border:0;cursor:pointer;padding:0.7rem 1.1rem 0.62rem;font:800 0.82rem var(--sans);letter-spacing:.05em;text-transform:uppercase;color:var(--creme,#f4ead8);background:var(--rost,#C8603A);transform:rotate(-1deg)}',
    '.wt-knopf.leise{background:transparent;color:var(--anthrazit);box-shadow:inset 0 0 0 1.5px currentColor}',
    '.wt-knopf.gross{min-width:7.5rem;font-size:1rem}',
    '.wt-zurueck{display:block;margin:1rem auto 0;border:0;background:none;font:400 0.75rem var(--maschine);color:var(--mittelgrau,#7a7268);cursor:pointer;text-decoration:underline}',
    '.wt-h{font:800 1.35rem/1.2 var(--lesen);margin:0 0 0.6rem}',
    '.wt-p{font:400 0.98rem/1.5 var(--lesen);margin:0 0 0.9rem}',
    '.wt-klein{font:400 0.74rem/1.45 var(--sans);color:var(--mittelgrau,#7a7268);margin:0.8rem 0 0}',
    '.wt-gewicht{display:grid;grid-template-columns:7.2rem 1fr;align-items:center;gap:0.3rem 0.7rem;margin:0.8rem 0 1.1rem;font:700 0.8rem var(--sans)}',
    '.wt-netz{display:block;width:100%;max-width:21rem;margin:0.4rem auto 0.6rem}',
    '.wt-achse{margin:0 0 0.7rem;font:400 0.92rem/1.45 var(--lesen)}.wt-achse b{font:800 0.72rem var(--sans);letter-spacing:.05em;text-transform:uppercase;color:var(--rost,#C8603A);display:block}',
    '.wt-partei{display:grid;grid-template-columns:5.6rem 1fr 2.6rem;align-items:center;gap:0.5rem;font:700 0.82rem var(--sans);margin:0.32rem 0}',
    '.wt-partei i{display:block;height:0.6rem;background:rgba(46,43,42,0.13)}.wt-partei i b{display:block;height:100%;background:var(--ocker,#D99A4E)}',
    '.wt-partei.top i b{background:var(--rost,#C8603A)}.wt-partei span:last-child{text-align:right;font:400 0.78rem var(--maschine)}',
    '.wt-start{margin-top:0.8rem}'
  ].join('\n');
  document.head.appendChild(css);

  var grund, karte, st;
  function oeffnen() {
    st = lade(); if (!st.a) st.a = {}; if (st.i == null) st.i = 0;
    if (!grund) {
      grund = document.createElement('div'); grund.className = 'wt-grund'; grund.setAttribute('role', 'dialog'); grund.setAttribute('aria-label', 'Werte-Test');
      var zu = document.createElement('button'); zu.className = 'wt-zu'; zu.type = 'button'; zu.setAttribute('aria-label', 'Schließen'); zu.textContent = '✕';
      zu.addEventListener('click', schliessen);
      karte = document.createElement('div'); karte.className = 'wt-karte';
      grund.appendChild(zu); grund.appendChild(karte); document.body.appendChild(grund);
    }
    grund.hidden = false; document.documentElement.style.overflow = 'hidden';
    if (st.fertig) ergebnis(); else if (st.i >= FRAGEN.length) gewichten(); else if (st.i === 0 && !Object.keys(st.a).length) intro(); else frage();
  }
  function schliessen() { grund.hidden = true; document.documentElement.style.overflow = ''; }

  function intro() {
    karte.innerHTML = '<h3 class="wt-h">Wie tickst du?</h3>' +
      '<p class="wt-p">' + FRAGEN.length + ' kleine Alltagsszenen, keine Politik-Thesen. Du antwortest nur mit einem Regler oder mit Ja und Nein. Es gibt kein richtig oder falsch, nimm das, was du wirklich tun würdest.</p>' +
      '<p class="wt-p">Am Ende siehst du, was dir wichtig ist, und welche Parteien von ihren Grundwerten her am ehesten zu dir passen könnten. Dauert etwa 8 bis 10 Minuten.</p>' +
      '<div class="wt-knoepfe"><button type="button" class="wt-knopf gross" data-los>Los geht’s</button></div>' +
      '<p class="wt-klein">Deine Antworten bleiben nur auf deinem Gerät. Nichts wird gesendet oder gespeichert, außer in deinem Browser.</p>';
    karte.querySelector('[data-los]').addEventListener('click', function () { st.i = 0; merke(st); frage(); });
  }

  function kopf() {
    return '<div class="wt-stand"><span>Frage ' + (st.i + 1) + ' von ' + FRAGEN.length + '</span><span>' + ACHSEN[FRAGEN[st.i][0]].name + '</span></div>' +
      '<div class="wt-balken"><b style="width:' + Math.round(st.i / FRAGEN.length * 100) + '%"></b></div>';
  }
  function weiter(wert) { st.a[st.i] = wert; st.i++; merke(st); if (st.i >= FRAGEN.length) gewichten(); else frage(); karte.scrollIntoView({ block: 'start' }); }
  function frage() {
    var q = FRAGEN[st.i], alt = st.a[st.i];
    if (q[2] === 'jn') {
      karte.innerHTML = kopf() + '<p class="wt-szene">' + esc(q[1]) + '</p><div class="wt-knoepfe"><button type="button" class="wt-knopf gross" data-w="1">Ja</button><button type="button" class="wt-knopf gross" data-w="0">Nein</button></div>' +
        '<button type="button" class="wt-zurueck" data-skip>Kann ich nicht sagen</button>' + (st.i ? '<button type="button" class="wt-zurueck" data-back>Zurück</button>' : '');
      karte.querySelectorAll('[data-w]').forEach(function (b) { b.addEventListener('click', function () { weiter(+b.getAttribute('data-w')); }); });
    } else {
      var v = alt != null ? Math.round(1 + alt * 9) : 5.5;
      karte.innerHTML = kopf() + '<p class="wt-szene">' + esc(q[1]) + '</p><div class="wt-pole"><span>' + esc(q[2]) + '</span><span>' + esc(q[3]) + '</span></div>' +
        '<input class="wt-regler" type="range" min="1" max="10" step="1" value="' + v + '" aria-label="Zwischen ' + esc(q[2]) + ' und ' + esc(q[3]) + '">' +
        '<div class="wt-zahl">' + (alt != null ? Math.round(1 + alt * 9) : 'Regler bewegen') + '</div>' +
        '<div class="wt-knoepfe"><button type="button" class="wt-knopf gross" data-ok' + (alt == null ? ' disabled style="opacity:.45"' : '') + '>Weiter</button></div>' +
        '<button type="button" class="wt-zurueck" data-skip>Kann ich nicht sagen</button>' + (st.i ? '<button type="button" class="wt-zurueck" data-back>Zurück</button>' : '');
      var r = karte.querySelector('.wt-regler'), ok = karte.querySelector('[data-ok]'), z = karte.querySelector('.wt-zahl');
      r.addEventListener('input', function () { z.textContent = r.value; ok.disabled = false; ok.style.opacity = ''; });
      ok.addEventListener('click', function () { weiter((r.value - 1) / 9); });
    }
    karte.querySelector('[data-skip]').addEventListener('click', function () { weiter(null); });
    var bk = karte.querySelector('[data-back]'); if (bk) bk.addEventListener('click', function () { st.i--; merke(st); frage(); });
  }

  function werte() {
    var s = {}, n = {};
    REIHE.forEach(function (a) { s[a] = 0; n[a] = 0; });
    FRAGEN.forEach(function (q, i) { var v = st.a[i]; if (v == null) return; var p = q[2] === 'jn' ? q[3] : q[4]; s[q[0]] += p > 0 ? v : 1 - v; n[q[0]]++; });
    var out = {}; REIHE.forEach(function (a) { out[a] = n[a] ? Math.round(s[a] / n[a] * 100) : 50; }); return out;
  }

  function gewichten() {
    if (!st.g) { st.g = {}; REIHE.forEach(function (a) { st.g[a] = 3; }); }
    karte.innerHTML = '<h3 class="wt-h">Fast geschafft</h3><p class="wt-p">Wie wichtig ist dir jeder Bereich, wenn es um Politik geht? So kannst du ausgleichen, was dir mehr oder weniger zählt.</p>' +
      '<div class="wt-gewicht">' + REIHE.map(function (a) { return '<span>' + ACHSEN[a].name + '</span><input class="wt-regler" type="range" min="1" max="5" step="1" value="' + st.g[a] + '" data-a="' + a + '" aria-label="Gewicht ' + ACHSEN[a].name + '">'; }).join('') + '</div>' +
      '<div class="wt-knoepfe"><button type="button" class="wt-knopf gross" data-aus>Auswertung</button></div><button type="button" class="wt-zurueck" data-back>Zurück zur letzten Frage</button>';
    karte.querySelectorAll('[data-a]').forEach(function (r) { r.addEventListener('input', function () { st.g[r.getAttribute('data-a')] = +r.value; merke(st); }); });
    karte.querySelector('[data-aus]').addEventListener('click', function () { st.fertig = true; merke(st); ergebnis(); });
    karte.querySelector('[data-back]').addEventListener('click', function () { st.i = FRAGEN.length - 1; merke(st); frage(); });
  }

  function netz(w) {
    var c = 110, R = 82, pkt = function (i, v) { var a = -Math.PI / 2 + i * 2 * Math.PI / REIHE.length; return [c + Math.cos(a) * R * v, c + Math.sin(a) * R * v]; };
    var ringe = [0.25, 0.5, 0.75, 1].map(function (v) { return '<polygon points="' + REIHE.map(function (_, i) { return pkt(i, v).join(','); }).join(' ') + '" fill="none" stroke="rgba(46,43,42,0.18)" stroke-width="1"/>'; }).join('');
    var speichen = REIHE.map(function (_, i) { var p = pkt(i, 1); return '<line x1="' + c + '" y1="' + c + '" x2="' + p[0] + '" y2="' + p[1] + '" stroke="rgba(46,43,42,0.18)"/>'; }).join('');
    var flaeche = '<polygon points="' + REIHE.map(function (a, i) { return pkt(i, Math.max(0.04, w[a] / 100)).join(','); }).join(' ') + '" fill="rgba(200,96,58,0.32)" stroke="#C8603A" stroke-width="2.2" stroke-linejoin="round"/>';
    var namen = REIHE.map(function (a, i) { var p = pkt(i, 1.24); return '<text x="' + p[0] + '" y="' + (p[1] + 4) + '" text-anchor="middle" font-family="Libre Franklin, Arial, sans-serif" font-weight="800" font-size="10.5" fill="#2E2B2A">' + ACHSEN[a].name + '</text>'; }).join('');
    return '<svg class="wt-netz" viewBox="-30 -10 280 245" role="img" aria-label="Netzdiagramm deiner Werte">' + ringe + speichen + flaeche + namen + '</svg>';
  }

  function ergebnis() {
    var w = werte(), g = st.g || {};
    var nah = PARTEIEN.map(function (p) {
      var d = 0, gs = 0; REIHE.forEach(function (a) { var gw = g[a] || 3; d += gw * Math.pow((w[a] - p[a]) / 100, 2); gs += gw; });
      return { n: p.n, s: Math.max(0, Math.round((1 - 1.6 * Math.sqrt(d / gs)) * 100)) };
    }).sort(function (a, b) { return b.s - a.s; });
    var stark = REIHE.slice().sort(function (a, b) { return Math.abs(w[b] - 50) - Math.abs(w[a] - 50); });
    karte.innerHTML = '<h3 class="wt-h">So tickst du</h3>' + netz(w) +
      stark.map(function (a) { return '<p class="wt-achse"><b>' + ACHSEN[a].name + ' · ' + w[a] + ' von 100</b>' + (w[a] >= 50 ? ACHSEN[a].hoch : ACHSEN[a].tief) + '</p>'; }).join('') +
      '<h3 class="wt-h" style="margin-top:1.2rem">Diese Parteien könnten für dich interessant sein</h3>' +
      nah.map(function (p, i) { return '<div class="wt-partei' + (i < 2 ? ' top' : '') + '"><span>' + p.n + '</span><i><b style="width:' + Math.max(4, p.s) + '%"></b></i><span>' + p.s + ' %</span></div>'; }).join('') +
      '<p class="wt-klein">Keine Wahlwerbung und keine Wahlempfehlung, ausschließlich eine KI-Einschätzung. Die Partei-Werte sind eine grobe Einschätzung ihrer Grundwerte aus Wahlprogrammen und aktuellen Forderungen, keine Messung' + (PSTAND ? ' (Stand ' + PSTAND.split('-').reverse().join('.') + ')' : '') + '. Schau dir die Programme selbst an, zum Beispiel im Wahl-O-Mat der Bundeszentrale für politische Bildung.</p>' +
      '<div class="wt-knoepfe wt-start"><button type="button" class="wt-knopf leise" data-neu>Nochmal machen</button></div>';
    karte.querySelector('[data-neu]').addEventListener('click', function () { st = { a: {}, i: 0 }; merke(st); intro(); });
  }

  document.addEventListener('click', function (e) { var b = e.target.closest('[data-wertetest]'); if (b) { e.preventDefault(); oeffnen(); } });
})();

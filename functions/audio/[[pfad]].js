// Teil-Anfragen (Range) für Audio, gefunden beim Bugtest 2026-11-08: Cloudflare Pages schickte Audio immer komplett (200 statt 206).
// Safari auf dem iPhone braucht 206, um in Aufnahmen zu springen (10 Sek. zurück, Lo-Fi umschalten, Dauer). Bei jedem Fehler: normale Datei.
export async function onRequestGet({ request, next }) {
  const res = await next();
  try {
    const range = request.headers.get('Range');
    if (res.status !== 200) return res;
    if (!range) { const h = new Headers(res.headers); h.set('Accept-Ranges', 'bytes'); return new Response(res.body, { status: 200, headers: h }); }
    const m = /^bytes=(\d*)-(\d*)$/.exec(range.trim()); if (!m || (m[1] === '' && m[2] === '')) return res;
    const buf = await res.arrayBuffer(), size = buf.byteLength;
    let start, end;
    if (m[1] === '') { start = Math.max(0, size - Number(m[2])); end = size - 1; }
    else { start = Number(m[1]); end = m[2] === '' ? size - 1 : Math.min(Number(m[2]), size - 1); }
    if (start >= size || start > end) return new Response(null, { status: 416, headers: { 'Content-Range': 'bytes */' + size } });
    const h = new Headers(res.headers);
    h.set('Accept-Ranges', 'bytes'); h.set('Content-Range', 'bytes ' + start + '-' + end + '/' + size); h.set('Content-Length', String(end - start + 1));
    return new Response(buf.slice(start, end + 1), { status: 206, headers: h });
  } catch (e) { return res; }
}

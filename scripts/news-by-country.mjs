#!/usr/bin/env node
/* One story a country, every day, from open feeds.

   Runs in GitHub Actions on a timer (see .github/workflows/news-by-country.yml) and
   writes data/news-by-country.json, which the page reads. Nothing here needs a key.

   For each of the 195 countries in data/world-capitals.geojson, in this order:
     1. the country's own press, from scripts/news-feeds.json - national broadcasters and
        papers, and AllAfrica's per-country headlines for Africa - every one probed live
        before it went in the table;
     2. Google News's edition for that country (news.google.com/rss?gl=CC), which is a
        ranking of that country's own outlets and exists for nearly every code;
   and the newest item from the first source that has one from the last three days is
   the country's story. The source's name travels with it, so the reader sees who said it.

   Feeds are XML of two shapes (RSS <item>, Atom <entry>) and this reads both with a
   regular expression rather than a parser: the fields wanted are three, and a dependency
   for three fields is a dependency that can break on a Tuesday. */
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const OUT = join(ROOT, 'data', 'news-by-country.json');
const UA = 'DotWorld/1.0 (+https://fablab503-collab.github.io/openstreetmap-dot/; a personal experiment)';
const FRESH_MS = 3 * 86400e3;          // a story older than this is not today's
const PARALLEL = 8;
const only = process.argv[2] ? process.argv[2].split(',') : null;   // a few codes, for a quick run

const capitals = JSON.parse(readFileSync(join(ROOT, 'data', 'world-capitals.geojson'), 'utf8')).features
  .map(f => ({ cc: f.properties.cc, country: f.properties.country, capital: f.properties.name,
               lon: +f.geometry.coordinates[0].toFixed(3), lat: +f.geometry.coordinates[1].toFixed(3) }));
const feeds = JSON.parse(readFileSync(join(ROOT, 'scripts', 'news-feeds.json'), 'utf8'));

const unesc = s => s.replace(/<!\[CDATA\[([\s\S]*?)\]\]>/g, '$1').replace(/<[^>]+>/g, '')
  .replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"')
  .replace(/&#39;|&apos;/g, "'").replace(/&#(\d+);/g, (m, n) => String.fromCharCode(+n)).replace(/\s+/g, ' ').trim();

function parseItems(xml) {
  const out = [];
  const re = /<(item|entry)\b[\s\S]*?<\/\1>/g;
  let m;
  while ((m = re.exec(xml)) && out.length < 40) {
    const b = m[0];
    const tag = t => { const r = new RegExp('<' + t + '(?:\\s[^>]*)?>([\\s\\S]*?)<\\/' + t + '>', 'i').exec(b); return r ? unesc(r[1]) : ''; };
    let link = tag('link');
    if (!link) { const r = /<link[^>]*href="([^"]+)"/i.exec(b); link = r ? unesc(r[1]) : ''; }
    const when = Date.parse(tag('pubDate') || tag('published') || tag('updated') || tag('dc:date'));
    const source = tag('source');
    const title = tag('title');
    if (title && link) out.push({ title, link, t: isNaN(when) ? 0 : when, source });
  }
  return out;
}

async function fetchFeed(url) {
  const r = await fetch(url, { headers: { 'User-Agent': UA, 'Accept': 'application/rss+xml, application/atom+xml, application/xml, text/xml, */*' },
                               signal: AbortSignal.timeout(20000), redirect: 'follow' });
  if (!r.ok) throw new Error('HTTP ' + r.status);
  return parseItems(await r.text());
}

// The newest fresh item, or null. A feed with no dates at all is trusted for its first item.
function pick(items, fresh = FRESH_MS) {
  const dated = items.filter(i => i.t).sort((a, b) => b.t - a.t);
  if (dated.length) return dated[0].t > Date.now() - fresh ? dated[0] : null;
  return items[0] || null;
}

/* Two lists. EXTRA is more names to search by - the capital, the demonym, the long
   form - for countries the news rarely calls by their short name. STRICT is the subset
   whose name belongs to something louder: "Palau" is Barcelona's arena, "Georgia" a US
   state, "Jordan" a sneaker and a basketball player, "Chad" and "Niger" a first name and
   a river, "Guinea" three countries and a pig, "Congo" two. For those the story's title
   has to use the name as a country - the demonym or the capital, "Chad:" at the front,
   or "Chad's government". Nothing looser: searching "Chad" OR "Chadian" alone ranked an
   obituary for a man called Chad first, because the newest match wins; a title that
   merely started with the name let "Chad Tracy" and "Jordan Whittington" in; and
   "in/to/from" let "run(s) to Jordan Groshans" in. A country with no such story in a
   fortnight is listed as missing, which is better than a shortstop. */
const EXTRA = {
  PW: ['Koror', 'Palauan'], GE: ['Tbilisi', 'Georgian government'], JO: ['Amman', 'Jordanian'],
  TD: ["N'Djamena", 'Chadian'], NE: ['Niamey', 'Nigerien'], GN: ['Conakry', 'Guinean'],
  GW: ['Bissau'], GQ: ['Malabo', 'Equatorial Guinea'], CG: ['Brazzaville', 'Republic of Congo'],
  CD: ['Kinshasa', 'DR Congo', 'DRC'], DM: ['Roseau'], WS: ['Apia', 'Samoan'],
  SD: ['Khartoum', 'Sudanese'], FM: ['Federated States of Micronesia', 'Palikir', 'Pohnpei'],
  MH: ['Majuro', 'Marshallese'], KI: ['Tarawa', 'I-Kiribati'], NR: ['Nauruan'],
  TV: ['Funafuti', 'Tuvaluan'], MC: ['Monegasque'], VA: ['Vatican', 'Holy See'],
};
const STRICT = new Set(['PW', 'GE', 'JO', 'TD', 'NE', 'GN', 'GW', 'GQ', 'CG', 'CD', 'DM', 'SD']);
function searchTerms(c) {
  const names = [c.country, ...(EXTRA[c.cc] || [])];
  return names.map(n => '"' + n + '"').join(' OR ');
}
// case-sensitive throughout: these are proper nouns, and "koror" is also a Somali word
const esc = t => t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
function aboutThePlace(c, title) {
  if (!STRICT.has(c.cc)) return true;
  const alt = (EXTRA[c.cc] || []).map(esc).join('|');
  const n = esc(c.country);
  const re = new RegExp('\\b(' + alt + ')\\b'
    + '|^' + n + ':'                       // "Chad: …" is the country; "Chad Tracy" is a man
    + "|\\b" + n + "'s (government|president|king|army|police|minister|election|military|parliament|capital|border|refugees|economy|prime|junta|opposition|cabinet)");
  return re.test(title);
}

async function storyFor(c) {
  const tried = [];
  for (const [name, url] of feeds[c.cc] || []) {
    try {
      const it = pick(await fetchFeed(url));
      if (it) return { ...it, source: name, via: 'press' };
      tried.push(name + ': nothing fresh');
    } catch (e) { tried.push(name + ': ' + (e.message || e)); }
  }
  /* Google News, searched for the country by name in its own edition: stories that are
     about the place, from whatever outlet wrote them, with the outlet's name in <source>.
     Given a week rather than three days, because a small country is not in the news
     every day and an older story about it beats a fresh one about somewhere else.

     The edition's own front page was tried as a last resort and dropped: for a small
     country it is the world's news, not its own - Nauru's led with Riyadh - and a story
     that is not about the place is worse than no story. A country with nothing is
     listed as missing, and the page carries on without it. */
  try {
    const url = `https://news.google.com/rss/search?q=${encodeURIComponent(searchTerms(c))}&hl=en&gl=${c.cc}&ceid=${c.cc}:en`;
    const it = pick((await fetchFeed(url)).filter(i => aboutThePlace(c, i.title)), (STRICT.has(c.cc) ? 14 : 7) * 86400e3);
    if (it) {
      const m = /^(.*)\s-\s([^-]{2,60})$/.exec(it.title);
      return { ...it, title: m ? m[1] : it.title, source: it.source || (m ? m[2] : 'Google News'), via: 'google-news' };
    }
    tried.push('google news: nothing this week');
  } catch (e) { tried.push('google news: ' + (e.message || e)); }
  return { none: tried };
}

const list = only ? capitals.filter(c => only.includes(c.cc)) : capitals;
const rows = [], misses = [];
let i = 0;
await Promise.all(Array.from({ length: PARALLEL }, async () => {
  while (i < list.length) {
    const c = list[i++];
    const s = await storyFor(c);
    if (s.none) { misses.push({ cc: c.cc, country: c.country, tried: s.none }); continue; }
    rows.push({ cc: c.cc, country: c.country, capital: c.capital, lon: c.lon, lat: c.lat,
                t: s.t || Date.now(), title: s.title.slice(0, 200), url: s.link, source: s.source, via: s.via });
  }
}));
rows.sort((a, b) => a.country.localeCompare(b.country));
const out = { built: new Date().toISOString(), countries: rows.length, of: list.length,
              press: rows.filter(r => r.via === 'press').length, googleNews: rows.filter(r => r.via === 'google-news').length,
              missing: misses.map(m => m.cc), stories: rows };
if (!only) {
  const before = existsSync(OUT) ? JSON.parse(readFileSync(OUT, 'utf8')) : null;
  writeFileSync(OUT, JSON.stringify(out, null, 1) + '\n');
  console.log(`wrote ${OUT}: ${rows.length} of ${list.length} countries (${out.press} own press, ${out.googleNews} google news)` + (before ? `, was ${before.countries}` : ''));
} else {
  console.log(JSON.stringify(out, null, 1));
}
if (misses.length) console.log('no story for: ' + misses.map(m => m.cc).join(' '));

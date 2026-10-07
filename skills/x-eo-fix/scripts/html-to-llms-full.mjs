// Turn the visible text of an HTML file (or one region of it) into a Markdown-ish llms-full.txt.
// Generating it from the source page means it cannot go stale when the page changes (a hand-written copy did).
// Usage: node html-to-llms-full.mjs --in index.html --out llms-full.txt --title "Site name" --url https://example.com/
//          [--from '<div id="view-detail"'] [--to '<div id="view-print"']   (cut a region by literal markers)
//          [--note "extra line under the title"]
// Licensing: this file is public text. Do NOT feed it pages that quote third-party copyrighted material
// (e.g. Bible translations, lyrics) unless you may republish it; strip those regions with --from/--to.
import fs from 'node:fs'
const args = process.argv.slice(2)
const opt = (n, d) => { const i = args.indexOf(n); return i >= 0 ? args[i + 1] : d }
const inFile = opt('--in'), out = opt('--out', 'llms-full.txt'), title = opt('--title'), url = opt('--url')
if (!inFile || !title || !url) { console.error('usage: node html-to-llms-full.mjs --in F --title T --url U [--out F] [--from M] [--to M] [--note N]'); process.exit(2) }
let html = fs.readFileSync(inFile, 'utf8')
const from = opt('--from'), to = opt('--to')
if (from) {
  const a = html.indexOf(from); if (a < 0) { console.error('--from marker not found'); process.exit(1) }
  const b = to ? html.indexOf(to, a) : -1
  html = html.slice(a, b > a ? b : undefined)
} else {
  const m = html.match(/<body[^>]*>([\s\S]*)<\/body>/i); if (m) html = m[1]
}
const ENT = { '&amp;': '&', '&lt;': '<', '&gt;': '>', '&quot;': '"', '&#39;': "'", '&nbsp;': ' ', '&rarr;': '→', '&times;': '×', '&middot;': '·', '&mdash;': '—', '&ndash;': '–' }
const decode = (s) => s.replace(/&[a-z#0-9]+;/gi, (e) => ENT[e] ?? e)
const text = html
  .replace(/<(script|style|video|svg|noscript|template)\b[\s\S]*?<\/\1>/gi, '')
  .replace(/<!--[\s\S]*?-->/g, '')
  .replace(/<(img|source|br)\b[^>]*\/?>/gi, '\n')
  .replace(/<\/t[dh]>\s*<t[dh][^>]*>/gi, ' | ').replace(/<\/tr>/gi, '\n')
  .replace(/<h([1-6])[^>]*>/gi, (_, n) => '\n\n' + '#'.repeat(+n) + ' ').replace(/<\/h[1-6]>/gi, '\n')
  .replace(/<li[^>]*>/gi, '\n- ').replace(/<\/(p|div|ul|ol|table|section|article|header|footer)>/gi, '\n')
  .replace(/<hr\s*\/?>/gi, '\n').replace(/<[^>]+>/g, '')
  .split('\n').map((l) => decode(l).replace(/[ \t]+/g, ' ').trim()).join('\n')
  .replace(/\n{3,}/g, '\n\n').trim()
const note = opt('--note')
fs.writeFileSync(out, `# ${title} — full text\n\n> Generated from ${url} on ${new Date().toISOString().slice(0, 10)}. Plain-text copy for AI agents; the web page is canonical.${note ? '\n> ' + note : ''}\n\n${text}\n`)
console.log(`[llms-full] ${out}: ${text.length.toLocaleString()} chars`)

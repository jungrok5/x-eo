// Generate the "AI discovery" convention files from one JSON config:
//   .well-known/ai.txt   ai/summary.json   ai/faq.json   ai/service.json
// EVIDENCE TIER C: no major engine is shown to read these (Google's AI guide says it ignores AI text files).
// Generate them only if free, keep them truthful, and never report them as a result.
// Usage: node gen-ai-files.mjs --config site.json --out ./public
// site.json: { "name": "...", "alternateName": "...", "url": "https://example.com/", "description": "(>=20 chars)",
//              "sitemap": "https://example.com/sitemap.xml", "attribution": "Cite as ...",
//              "capabilities": ["what the site/service actually does", "..."],
//              "faqs": [{ "question": "...", "answer": "..." }], "extra": { "languages": 12 } }
// Shapes follow what common checkers validate: summary needs name(>=3)+description(>=20); service needs a non-empty "capabilities" list.
import fs from 'node:fs'
import path from 'node:path'
const args = process.argv.slice(2)
const opt = (n) => { const i = args.indexOf(n); return i >= 0 ? args[i + 1] : undefined }
const cfgPath = opt('--config'), out = opt('--out')
if (!cfgPath || !out) { console.error('usage: node gen-ai-files.mjs --config site.json --out DIR'); process.exit(2) }
const c = JSON.parse(fs.readFileSync(cfgPath, 'utf8'))
for (const k of ['name', 'url', 'description']) if (!c[k]) { console.error(`config.${k} is required`); process.exit(2) }
if (c.name.length < 3 || c.description.length < 20) { console.error('name >= 3 and description >= 20 chars'); process.exit(2) }
if (!Array.isArray(c.capabilities) || !c.capabilities.length) console.error('warning: no capabilities -> service.json will be skipped')
const root = c.url.replace(/\/$/, '')
const today = new Date().toISOString().slice(0, 10)
fs.mkdirSync(path.join(out, '.well-known'), { recursive: true }); fs.mkdirSync(path.join(out, 'ai'), { recursive: true })
fs.writeFileSync(path.join(out, '.well-known/ai.txt'),
`# AI crawler permissions for ${root}
# Public content may be crawled, indexed and cited by search and answer engines.
User-Agent: *
Allow: /
${c.attribution ? `\n# ${c.attribution}\n` : ''}${c.sitemap ? `Sitemap: ${c.sitemap}\n` : ''}Summary: ${root}/ai/summary.json
`)
const j = (f, o) => fs.writeFileSync(path.join(out, 'ai', f), JSON.stringify(o, null, 2) + '\n')
j('summary.json', { name: c.name, ...(c.alternateName && { alternateName: c.alternateName }), url: c.url, description: c.description, ...(c.sitemap && { sitemap: c.sitemap }), ...(c.extra || {}), lastModified: today })
if (c.faqs?.length) j('faq.json', { faqs: c.faqs, lastModified: today })
if (c.capabilities?.length) j('service.json', { name: c.name, url: c.url, description: c.description, capabilities: c.capabilities, lastModified: today })
console.log(`[ai-files] wrote to ${out}: .well-known/ai.txt, ai/summary.json${c.faqs?.length ? ', ai/faq.json' : ''}${c.capabilities?.length ? ', ai/service.json' : ''}  (Tier C)`)

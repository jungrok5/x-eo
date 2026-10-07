// Does an AI answer engine actually CITE your site? (sample check, not monitoring)
// Asks brand-free questions through retrieval-enabled APIs and counts URL citations on your host.
// Why this shape: a chat model without retrieval only shows training recall; a question that contains
// your brand/host makes any "mentioned" check trivially true; name mentions are often hallucinated.
// The metric here is a cited URL on your host — the thing that sends a reader to you.
//
// usage: node ai-recall.mjs --site https://example.com/ --q "question a user would really ask" [--q ...]
//          [--engine anthropic,openai] [--brand "Name"] [--dry-run] [--json]
// env:   ANTHROPIC_API_KEY (or an `ant auth login` profile)  ·  OPENAI_API_KEY  ·  OPENAI_MODEL (default gpt-5)
// deps:  npm i @anthropic-ai/sdk   (loaded only when the anthropic engine runs)
// cost:  each question = one web-search-enabled request per engine; you pay for it. Start with 3–5 questions.
// status: the OpenAI path follows the documented Responses API shape but was written without a live key — verify once.
const args = process.argv.slice(2)
const opt = (n, d) => { const i = args.indexOf(n); return i >= 0 ? args[i + 1] : d }
const all = (n) => args.flatMap((a, i) => (a === n ? [args[i + 1]] : []))
const flag = (n) => args.includes(n)
const site = opt('--site'); const qs = all('--q'); const brand = opt('--brand', '')
if (!site || !qs.length) { console.error('usage: node ai-recall.mjs --site URL --q "question" [--q ...] [--engine anthropic,openai] [--brand NAME] [--dry-run] [--json]'); process.exit(2) }
const host = new URL(site).host.replace(/^www\./, '')
const engines = opt('--engine', 'anthropic,openai').split(',').map((s) => s.trim()).filter(Boolean)
const onHost = (u) => { try { return new URL(u).host.replace(/^www\./, '') === host } catch { return false } }
const urlsIn = (t) => [...String(t).matchAll(/https?:\/\/[^\s)\]>"'`]+/g)].map((m) => m[0])

// Guard: a question that names the site leaks the answer.
for (const q of qs) {
  const leaks = q.toLowerCase().includes(host) || (brand && q.toLowerCase().includes(brand.toLowerCase()))
  if (leaks) console.error(`! question names the site ("${q.slice(0, 60)}…") — any mention it produces proves nothing. Rephrase as a user who has never heard of you.`)
}
if (flag('--dry-run')) { console.log(`host ${host} · engines ${engines.join(',')} · ${qs.length} question(s)`); qs.forEach((q) => console.log('  - ' + q)); process.exit(0) }

async function anthropic(q) {
  const { default: Anthropic } = await import('@anthropic-ai/sdk')
  const client = new Anthropic()
  let messages = [{ role: 'user', content: q }]
  let res, cited = new Set(), seen = new Set(), text = ''
  for (let i = 0; i < 4; i++) {   // server tool turns can pause; resume by echoing the assistant turn
    res = await client.beta.messages.create({
      model: 'claude-opus-5-5', max_tokens: 4096,
      betas: ['server-side-fallback-2026-07-01'], fallbacks: 'default',   // re-run on another model if a safety classifier declines
      tools: [{ type: 'web_search_20260209', name: 'web_search', max_uses: 5 }],
      messages,
    })
    for (const b of res.content) {
      if (b.type === 'web_search_tool_result' && Array.isArray(b.content)) for (const r of b.content) if (r.url) seen.add(r.url)
      if (b.type === 'text') { text += b.text; for (const c of b.citations || []) if (c.url) cited.add(c.url); urlsIn(b.text).forEach((u) => cited.add(u)) }
    }
    if (res.stop_reason !== 'pause_turn') break
    messages = [...messages, { role: 'assistant', content: res.content }]
  }
  if (res.stop_reason === 'refusal') return { engine: 'anthropic', model: res.model, refused: true, text: '', cited: [], seen: [] }
  return { engine: 'anthropic', model: res.model, text, cited: [...cited], seen: [...seen] }
}

async function openai(q) {
  const key = process.env.OPENAI_API_KEY; if (!key) throw new Error('OPENAI_API_KEY not set')
  const r = await fetch('https://api.openai.com/v1/responses', {
    method: 'POST', headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${key}` },
    body: JSON.stringify({ model: process.env.OPENAI_MODEL || 'gpt-5', tools: [{ type: 'web_search' }], input: q }),
  })
  if (!r.ok) throw new Error(`openai HTTP ${r.status}: ${(await r.text()).slice(0, 200)}`)
  const d = await r.json(); let text = ''; const cited = new Set()
  for (const item of d.output || []) if (item.type === 'message') for (const c of item.content || []) if (c.type === 'output_text') {
    text += c.text; for (const a of c.annotations || []) if (a.type === 'url_citation' && a.url) cited.add(a.url); urlsIn(c.text).forEach((u) => cited.add(u))
  }
  return { engine: 'openai', model: d.model, text, cited: [...cited], seen: [] }
}

const run = { anthropic, openai }
const out = []
for (const q of qs) for (const e of engines) {
  if (!run[e]) { console.error('unknown engine', e); continue }
  try {
    const r = await run[e](q)
    const hit = r.cited.filter(onHost); const inResults = r.seen.filter(onHost)
    out.push({ q, ...r, verdict: r.refused ? 'refused' : hit.length ? 'CITED' : inResults.length ? 'in search results, not cited' : 'absent', hit })
  } catch (err) { out.push({ q, engine: e, error: String(err.message || err), verdict: 'error' }) }
}
if (flag('--json')) { console.log(JSON.stringify(out, null, 1)); process.exit(0) }
for (const r of out) {
  console.log(`\n[${r.engine}${r.model ? ' ' + r.model : ''}] ${r.q}\n  -> ${r.verdict}${r.hit?.length ? ': ' + r.hit.join(', ') : ''}${r.error ? ': ' + r.error : ''}`)
  if (r.text) console.log('  ' + r.text.replace(/\s+/g, ' ').slice(0, 220) + (r.text.length > 220 ? '…' : ''))
}
const n = out.filter((r) => r.verdict !== 'error').length, c = out.filter((r) => r.verdict === 'CITED').length
console.log(`\ncited ${c}/${n} answers on ${host} (a sample, not a rate; results vary run to run)`)

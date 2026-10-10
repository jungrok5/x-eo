// Notify Bing / Naver / Yandex / Seznam that URLs changed (IndexNow). Google does NOT support IndexNow.
// Usage:
//   node indexnow.mjs --host example.com --key <32+ hex chars> [--key-location URL] [--dry-run] URL [URL ...]
//   node indexnow.mjs --host example.com --key KEY --sitemap https://example.com/sitemap.xml
// Setup (once): create a text file named <KEY>.txt at your host root whose content is exactly KEY, deploy it,
// then run this. Without the deployed key file the API answers 403/422.
const args = process.argv.slice(2)
const opt = (name) => { const i = args.indexOf(name); return i >= 0 ? args[i + 1] : undefined }
const flag = (name) => args.includes(name)
const host = opt('--host'), key = opt('--key')
if (!host || !key) { console.error('usage: node indexnow.mjs --host H --key K [--key-location URL] [--sitemap URL] [--dry-run] [URL...]'); process.exit(2) }
if (!/^[A-Za-z0-9-]{8,128}$/.test(key)) { console.error('key must be 8-128 chars of [A-Za-z0-9-] (IndexNow spec)'); process.exit(2) }
const keyLocation = opt('--key-location') || `https://${host}/${key}.txt`

const valued = new Set(['--host', '--key', '--key-location', '--sitemap'])
const urls = args.filter((a, i) => !a.startsWith('--') && !valued.has(args[i - 1]))
const sm = opt('--sitemap')
if (sm) {
  const r = await fetch(sm).catch((e) => ({ ok: false, status: e.message }))
  if (!r.ok) { console.error(`sitemap fetch failed: ${sm} (${r.status})`); process.exit(1) }
  const xml = await r.text()
  for (const m of xml.matchAll(/<loc>\s*([^<\s]+)\s*<\/loc>/g)) urls.push(m[1])
}
const onHost = (u) => { try { return new URL(u).host === host } catch { return false } }
const list = [...new Set(urls)].filter(onHost)   // IndexNow accepts only URLs on `host`
if (!list.length) { console.error('no URLs on host', host); process.exit(2) }

// Pre-flight: the key file must be live, or the submission is wasted.
const kf = await fetch(keyLocation).catch(() => null)
const kbody = kf && kf.ok ? (await kf.text()).trim() : null
if (kbody !== key) { console.error(`key file not live or content mismatch at ${keyLocation} (got ${kf ? kf.status : 'network error'})`); process.exit(1) }

console.log(`[indexnow] ${list.length} URL(s) on ${host}${flag('--dry-run') ? ' (dry run)' : ''}`)
if (flag('--dry-run')) { list.slice(0, 10).forEach((u) => console.log('  ' + u)); process.exit(0) }
// IndexNow limit: 10,000 URLs per request.
for (let i = 0; i < list.length; i += 10000) {
  const res = await fetch('https://api.indexnow.org/indexnow', {
    method: 'POST', headers: { 'Content-Type': 'application/json; charset=utf-8' },
    body: JSON.stringify({ host, key, keyLocation, urlList: list.slice(i, i + 10000) }),
  })
  console.log(`[indexnow] HTTP ${res.status} ${res.statusText}`)   // 200/202 = accepted
  if (!res.ok) { console.log((await res.text()).slice(0, 300)); process.exit(1) }
}

// Compare what a crawler sees without JavaScript to what a browser sees with it.
// Usage: node render-diff.mjs URL [--insecure] [--save FILE]
// Needs: npm i playwright-core, and a Chromium (set PLAYWRIGHT_CHROMIUM=/path/to/chrome, or it uses Playwright's own).
import { chromium } from 'playwright-core'
import fs from 'node:fs'
const argv = process.argv.slice(2)
const flags = argv.filter((a, i) => a.startsWith('--') || argv[i - 1] === '--save')
const url = argv.find((a, i) => !a.startsWith('--') && argv[i - 1] !== '--save')
if (!url) { console.error('usage: node render-diff.mjs URL [--insecure] [--save FILE]'); process.exit(2) }
const exe = process.env.PLAYWRIGHT_CHROMIUM || undefined
const browser = await chromium.launch({ executablePath: exe, args: ['--no-sandbox'] })
async function snap(js) {
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, javaScriptEnabled: js, reducedMotion: 'reduce', ignoreHTTPSErrors: flags.includes('--insecure') })
  const p = await ctx.newPage()
  await p.goto(url, { waitUntil: 'networkidle' }); await p.waitForTimeout(1500)
  const r = await p.evaluate(() => {
    const txt = document.body.innerText || ''
    const main = document.querySelector('main')
    return { chars: txt.length, headings: document.querySelectorAll('h1,h2,h3').length,
      mainChars: main ? main.innerText.length : null, mainEmpty: main ? main.children.length === 0 : null,
      jsonld: document.querySelectorAll('script[type="application/ld+json"]').length, dom: document.body.innerHTML }
  })
  await ctx.close(); return r
}
const off = await snap(false), on = await snap(true)
const ratio = on.chars ? off.chars / on.chars : 1
console.log(`JS off: ${off.chars} chars, ${off.headings} headings, main=${off.mainChars ?? 'n/a'}${off.mainEmpty ? ' (EMPTY)' : ''}`)
console.log(`JS on : ${on.chars} chars, ${on.headings} headings, main=${on.mainChars ?? 'n/a'}`)
console.log(`no-JS shows ${(ratio * 100).toFixed(0)}% of the rendered text ->`, ratio < 0.5 ? 'PROBLEM [A]: crawlers without JS miss most of the page' : 'OK')
if (flags.includes('--save')) fs.writeFileSync(flags[flags.indexOf('--save') + 1], JSON.stringify({ off, on }))
await browser.close(); process.exit(ratio < 0.5 ? 1 : 0)

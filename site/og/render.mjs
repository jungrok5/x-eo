// Render og/card.html to ../og.png (1200x630). Needs playwright-core and PLAYWRIGHT_CHROMIUM.
import { chromium } from 'playwright-core'
import { fileURLToPath } from 'node:url'
import path from 'node:path'
const here = path.dirname(fileURLToPath(import.meta.url))
const b = await chromium.launch({ executablePath: process.env.PLAYWRIGHT_CHROMIUM, args: ['--no-sandbox'] })
const p = await b.newPage({ viewport: { width: 1200, height: 630 }, colorScheme: 'light' })
await p.goto('file://' + path.join(here, 'card.html'))
await p.screenshot({ path: path.join(here, '..', 'og.png') })
await b.close()
console.log('wrote site/og.png')

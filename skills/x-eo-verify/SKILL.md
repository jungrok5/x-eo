---
name: x-eo-verify
description: Prove an SEO/AEO/GEO change broke nothing before shipping. Builds before/after trees and diffs them, parses every JSON-LD block, compares page content with JavaScript on vs off in a real browser (Playwright), and can audit your own local dev server. Use after x-eo-fix or any change made to raise a score.
---

# x-eo-verify — prove

Tiers/report: `../x-eo/SKILL.md`. Scripts relative to this directory. Run **all** of 1–3 before shipping.

1. **Build diff.** `bash scripts/diff-builds.sh "<build cmd>" <output dir> [base-ref]` — builds base (git worktree) and working tree, lists differing files. Only intended files may differ; unrelated pages must show 0 differences. For generators that write in place, also hash the output after builds #1, #2, #3 (idempotency).
2. **JSON-LD.** `python3 scripts/jsonld-lint.py <dir> [--require WebSite,Person] [--only "index.html"] [--strict]` — parse errors always fail; missing required types are reported separately. Then read the content: valid ≠ true.
3. **Render diff.** `node scripts/render-diff.mjs <url> [--insecure] [--save FILE]` (needs `npm i playwright-core` and `PLAYWRIGHT_CHROMIUM=/path/to/chrome`). Compares text/headings/main with JS off vs on. No-JS under 50% of JS-on = PROBLEM [A] (a judgement threshold). For a prerender fix: the JS-on final DOM must be unchanged; JS-off must improve.
4. **Local server.** `X_EO_ALLOW_LOCAL=1 python3 scripts/local-audit.py http://127.0.0.1:PORT/` — scores your own dev server; loopback only; patches the SSRF guard in-process, never in the package; depends on geo-optimizer internals (pinned version).
5. **Live re-measure** after deploy with `../x-eo-audit` using the same tool and version. Local scores are previews.

Report what was verified and what wasn't. A check you didn't run is "not verified", not "fine".

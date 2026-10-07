# Worked example: a 214-language static site, 62 → 90

Site: a single-page, mobile-first web app generated into 214 language pages by a Node build script
(`index.html` is both the template and the Korean root output). Tool: geo-optimizer-skill 4.18.3.
Scores are **live-URL** measurements, taken before and after deploy.

## Where the 28 points came from

| Category | Before | After | Δ | Tier | What changed |
|---|---|---|---|---|---|
| robots | 15 | 18 | +3 | A (neutral) | wildcard-only → explicit per-bot `Allow` (behaviour identical, `grep -c ^Disallow` = 0) |
| llms | 10 | 16 | +6 | **C** | plain `- ko: URL` lines → markdown links; added `llms-full.txt` (Scripture quotations excluded for licensing) |
| ai_discovery | 0 | 6 | +6 | **C** | `/.well-known/ai.txt`, `/ai/{summary,faq,service}.json` (generated; `service.json` needed a `capabilities` array) |
| schema | 7 | 16 | +9 | B | added Organization + Article, enriched WebSite/FAQPage with *true* attributes only |
| content | 11 | 12 | +1 | A | Korean root prerendered (below) |
| negative penalty | −3 | 0 | +3 | A/B | fewer "boilerplate/empty main" signals |
| **Total** | **62** | **90** | **+28** | | |

**Tier C points: +12 of 28.** Excluding Tier C (llms + ai_discovery) the score moved **52/76 (68%) → 68/76 (89%)**.
Google's own guide says it ignores the Tier C files. Treat those 12 points as optionality, not as a result.

## The one change with demonstrated value

The hand-written Korean root left `<main id="epochs">` and the core grid empty; the other 213 pages were
already prerendered. Without JavaScript the primary page showed **2,273 characters, 0 of 13 sections**.

`render-diff.mjs` before → after: no-JS content 11% → 53% of the rendered text; sections 0 → 13.
JS-on final DOM: **byte-identical** (`#epochs.innerHTML`, `#core.innerHTML` compared in headless Chromium),
because the runtime re-renders on load. Still 47% JS-only (UI strings, interactive parts) — fine, but noted.

## How it was kept safe

1. Build the old and new generator into separate trees; `diff -rq`. Only intended files differed:
   214 pages differed by exactly one JSON-LD line, `about/` and `maps/` by zero.
2. Parse all 443 JSON-LD blocks (`jsonld-lint.py`): 0 errors.
3. Before merging, sample pages (`/en`, `/ja`, `/ar`, `/sw`, `/about`, `/maps`) diffed against production: 0 lines.
4. Template pollution guard: prerendered Korean content wrapped in `<!--pre-->…<!--/pre-->`, stripped when the
   template is read. Build run three times → identical file hash; other languages' pages still carry their own text.
5. Merged only after review; re-measured on the live URL after deploy.

## What went wrong along the way (kept on purpose)

- First `llms.txt` links were plain text → tool counted **0 links**. The checker wants `[name](url)`.
- `service.json` used `features`; the checker requires `capabilities` → 0 points until fixed.
- Advised submitting a root `sitemap.xml` to a URL-prefix Search Console property → rejected ("invalid sitemap address").
  A prefix property accepts only sitemaps under the prefix; root sitemaps are advertised through `robots.txt`.
- A site on a sub-path (`user.github.io/resume/`) had `robots.txt`/`llms.txt` that crawlers never read; found only because
  the checker said "llms.txt not found". Now `host-root-check.sh` tests it first.
- A "broken link" finding came from string fragments inside `<script>` — a regex artifact, left alone.

---
name: x-eo
description: Audit and improve a website's visibility to search engines and AI answer engines (SEO + AEO + GEO) with evidence-graded recommendations. Use when asked to check or raise "AI search readiness", an AEO/GEO/SEO score, llms.txt, structured data (JSON-LD), AI-crawler access (robots.txt), or when a site scores low on tools such as geo-optimizer or tryoreum. Also use before/after any change made to raise such a score, to verify nothing user-facing broke.
---

# x-eo — SEO / AEO / GEO audit, graded by evidence

Reply in the user's language. This skill exists because **an audit score is a proxy, not the outcome.**
Tools reward files and markup; the thing you care about is whether crawlers can read the page and
whether answer engines cite it. Every recommendation below carries an **evidence tier** so you never
oversell a change.

## Evidence tiers (label every finding with one)

| Tier | Meaning | Examples | How to treat it |
|---|---|---|---|
| **A** | Vendor-documented or directly observable | page reachable (HTTP 200, no auth wall); content present in raw HTML without JavaScript; correct `canonical`/`hreflang`; sitemap; robots.txt not blocking the *search* crawlers; JSON-LD that parses and matches visible text | Fix first. Cheap to verify. |
| **B** | Plausible, supported only by third-party or correlational studies | question-shaped headings, self-contained answer passages, freshness, consistent entity name + `sameAs`, original statistics, off-site mentions | Do when it also helps human readers. Say "plausible", never "proven". |
| **C** | Convention with no demonstrated consumption | `llms.txt`, `llms-full.txt`, `/.well-known/ai.txt`, `/ai/*.json`, WebMCP attributes, `SearchAction` for agents, RSS-for-AI | Ship only if free and risk-free. **Never count toward success.** Google's AI-optimization guide (updated 2026-07-10) says it "ignores" such files and that no special markup is needed for generative features. |

Full source list and what was/was not verified: `references/evidence.md`.

## Workflow

0. **Scope & safety.** Read `references/pitfalls.md` once. Never `curl | bash` a tool; install into a throw-away venv with a pinned version (the scripts do this). Do not point audits at private/local addresses unless testing your own server (see `local-audit.py`).
1. **Baseline.** `bash scripts/audit.sh <url> [<url>…]` — prints the tool score *and* the score with Tier-C points removed, plus each recommendation tagged A/B/C. Save the numbers.
2. **Host-root check.** `bash scripts/host-root-check.sh <url>` — `robots.txt`, `llms.txt`, `/.well-known/*`, `/ai/*` are only read at the **host root**. Sites on a sub-path (GitHub Pages project sites, `/blog/`) silently fail this. Fix = a root site/repo or a root-level file, not a copy in the sub-path.
3. **Render check.** `node scripts/render-diff.mjs <url>` — compares content with JavaScript on vs off. If the no-JS view is mostly empty, that is a Tier-A problem the score may not show.
4. **Triage.** List failures by tier. Do A, then B where it also serves readers. Decide on C explicitly and record that it is optionality.
5. **Change the source, not the output.** Many sites generate pages (static-site builders). Edit the generator/template, then rebuild. If the template doubles as an output file, make the build **idempotent** (see pitfalls: template pollution).
6. **Verify before shipping.**
   - Build before/after into separate directories and `diff -rq` them: only intended files may differ.
   - `python3 scripts/jsonld-lint.py <dir>`: every JSON-LD block must parse; schemas must be truthful.
   - `node scripts/render-diff.mjs` on the *changed* page: JS-on final DOM must be unchanged; JS-off content should improve.
   - Spot-check unrelated pages against production: diff must be 0 lines.
7. **Deploy, then re-measure on the live URL** with the same tool and version. Local scores are a preview only.
8. **Submit.** Search Console: a URL-prefix property accepts only sitemaps *under that prefix*; a root sitemap is discovered via the `Sitemap:` line in root `robots.txt`. Bing Webmaster Tools can import from Search Console. IndexNow notifies Bing/Naver/Yandex (not Google).
9. **Report** with the template below.

## Honesty rules

- Do not invent facts to satisfy a check: no fake `dateModified`, no `sameAs` to profiles that are not the entity's, no made-up address/phone, no RSS feed with nothing to publish.
- Do not add personal data (e.g. an email) to structured data on many pages just for a point.
- Keyword-density or "boilerplate" warnings can be false positives on legitimate content; say so instead of rewriting text.
- A tool's recommendation list is a menu, not a to-do list.

## Report template

```
Scope: <urls>   Tool: <name+version>   Date: <date>
Score: A → B   (excluding Tier C: a% → b%)
Done:   [A] … [B] … [C] …           (each with evidence)
Skipped: … (why)
Verified: before/after diff, JSON-LD parse, JS on/off DOM, live re-measure
Not expected to move: … (be explicit that Tier C points are optionality)
```

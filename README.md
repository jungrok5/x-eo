# x-eo

**An agent skill for SEO / AEO / GEO audits that grades every recommendation by evidence.**
([한국어](README.ko.md))

Most "AI search readiness" tools hand you a 0–100 score and a to-do list. Some of that list is
documented engineering (can crawlers read your page?), some is plausible, and some is ritual
(`llms.txt`, `ai.txt`) that the biggest search engine says it ignores. `x-eo` makes an agent keep
those apart, so you can raise a score *without fooling yourself about what it means*.

> Google's AI optimization guide (updated 2026-07-10): *"You don't need to create new machine
> readable files, AI text files, markup, or Markdown to appear in Google Search … Google Search
> ignores them."*

## What you get — four skills, one loop

```
x-eo-audit  →  x-eo-fix  →  x-eo-verify  →  deploy  →  x-eo-audit (live)
        ↑                x-eo = router + shared rules + knowledge
```

| Skill | Contents |
|---|---|
| `x-eo` | Entry point: the three **evidence tiers** (A documented · B plausible · C convention), honesty rules, report template, topic map; `references/` = evidence ledger, 10 pitfalls, tool review, and **12 condensed topic guides vendored from [claude-seo](https://github.com/AgriciDaniel/claude-seo) (MIT)**: technical, on-page, content/E-E-A-T, schema, GEO, agentic, sitemap, images, hreflang, local, e-commerce, planning |
| `x-eo-audit` | `audit.sh` — [geo-optimizer-skill](https://github.com/Auriti-Labs/geo-optimizer-skill) (MIT) in a pinned throw-away venv; score **and score excluding Tier C**; A/B/C/SEC tags; `--threshold` for CI. `host-root-check.sh` — robots/llms/sitemap/`.well-known` are read at the **host root only** |
| `x-eo-fix` | `gen-robots.py` (per-bot policy, never blanket Disallow) · JSON-LD templates · sub-path→root scaffold · `html-to-llms-full.mjs` · `gen-ai-files.mjs` (Tier C) · `indexnow.mjs` |
| `x-eo-verify` | `diff-builds.sh` (before/after build tree) · `jsonld-lint.py` · `render-diff.mjs` (JS on vs off, Playwright) · `local-audit.py` (your own 127.0.0.1 server) |

## Install

```bash
git clone --depth 1 https://github.com/jungrok5/x-eo.git
mkdir -p ~/.claude/skills && cp -r x-eo/skills/* ~/.claude/skills/     # user-level
# or project-level:  mkdir -p .claude/skills && cp -r x-eo/skills/* .claude/skills/
```

Install **all four** (they reference each other). No installer, no hooks, no global agents — read the scripts first, they are short.
Requirements: `bash`, `python3` (3.10+), `git`; for `render-diff.mjs`: `npm i playwright-core` plus a Chromium (`PLAYWRIGHT_CHROMIUM=/path/to/chrome`).

Then ask your agent: *"use x-eo to audit https://example.com, fix what's Tier A, and verify."*

## Quick use without an agent

```bash
S=x-eo/skills
bash $S/x-eo-audit/scripts/audit.sh --threshold 80 https://example.com/
bash $S/x-eo-audit/scripts/host-root-check.sh https://example.com/blog/
node $S/x-eo-verify/scripts/render-diff.mjs https://example.com/
python3 $S/x-eo-verify/scripts/jsonld-lint.py ./dist --require WebSite --strict
python3 $S/x-eo-fix/scripts/gen-robots.py --sitemap https://example.com/sitemap.xml --out robots.txt
```

## Worked example

[`examples/one-scroll-bible.md`](examples/one-scroll-bible.md) — a 214-language static site taken
from 62 → 90 with before/after build diffs, a real-browser DOM comparison, and an honest account of
which points are Tier C.

## Limits of this skill (a self-review)

- **Tier labels are keyword heuristics** in `audit.sh`, not understanding. They can be wrong; read the finding.
- **One scorer.** Categories and weights belong to geo-optimizer-skill's author. Scores of different tools are not comparable; compare the *same* tool and version before/after.
- **No citation measurement.** Nothing here tells you whether ChatGPT/Claude/Perplexity actually cite you. That needs monitoring tools and API keys (see `references/tools.md`).
- `local-audit.py` reaches into geo-optimizer internals and may break on upgrade (hence the pinned version).
- The 50% no-JS threshold in `render-diff.mjs` is a judgement call, not a standard.
- Tested on Linux only. Korean/Naver-specific signals are not covered.
- Evidence ledger is dated; re-verify before relying on it.

## Prior art and credit

Reviewed while building this: claude-seo (AgriciDaniel), geo-optimizer-skill (Auriti-Labs),
usegeoaeo, geo-audit, ultimate-seo-geo, and the GEO paper (arXiv 2311.09735). claude-seo's topic guides are vendored (MIT, attribution in
`skills/x-eo/references/claude-seo/NOTICE.md`); the rest is original. `references/tools.md` records what each tool is good and bad at. The evidence-tier idea is influenced
by claude-seo giving `llms.txt` zero weight.

Validate the repo layout: `python3 tests/validate.py`.

MIT licensed.

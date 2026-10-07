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

## What you get

| | |
|---|---|
| `skills/x-eo/SKILL.md` | The workflow, the three **evidence tiers** (A documented · B plausible · C convention), honesty rules, report template |
| `scripts/audit.sh` | Runs [geo-optimizer-skill](https://github.com/Auriti-Labs/geo-optimizer-skill) (MIT) in a throw-away, version-pinned venv; prints the score **and the score with Tier-C points removed**; tags each recommendation A/B/C/SEC; `--threshold` for CI |
| `scripts/host-root-check.sh` | `robots.txt`, `llms.txt`, `/.well-known/*`, `/ai/*` are read at the **host root only** — catches sub-path sites (GitHub Pages project sites) where they silently don't count |
| `scripts/render-diff.mjs` | Content with JavaScript on vs off (Playwright). Flags pages whose real content only exists after JS |
| `scripts/jsonld-lint.py` | Parses every JSON-LD block in a build directory; separates parse errors from missing types |
| `scripts/local-audit.py` | Test-only: audit your own `127.0.0.1` server (opt-in env var; loopback only) |
| `references/` | `evidence.md` (what was verified vs merely reported), `pitfalls.md` (10 real traps), `tools.md` (reviewed alternatives) |

## Install

```bash
git clone --depth 1 https://github.com/jungrok5/x-eo.git
cp -r x-eo/skills/x-eo ~/.claude/skills/          # Claude Code (user-level)
# or: cp -r x-eo/skills/x-eo .claude/skills/       # project-level
```

No installer, no hooks, no global agents. Read the scripts first — they are short.
Requirements: `bash`, `python3` (3.10+), and for `render-diff.mjs`: `npm i playwright-core` plus a
Chromium (`PLAYWRIGHT_CHROMIUM=/path/to/chrome`).

Then ask your agent: *"audit https://example.com for AI search readiness with x-eo."*

## Quick use without an agent

```bash
bash skills/x-eo/scripts/audit.sh --threshold 80 https://example.com/
bash skills/x-eo/scripts/host-root-check.sh https://example.com/blog/
node skills/x-eo/scripts/render-diff.mjs https://example.com/
python3 skills/x-eo/scripts/jsonld-lint.py ./dist --require WebSite --only "index.html" --strict
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
usegeoaeo, geo-audit, ultimate-seo-geo, and the GEO paper (arXiv 2311.09735). No code was copied;
`references/tools.md` records what each is good and bad at. The evidence-tier idea is influenced
by claude-seo giving `llms.txt` zero weight.

MIT licensed.

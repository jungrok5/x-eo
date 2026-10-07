---
name: x-eo-audit
description: Measure a site's SEO/AEO/GEO readiness. Runs a version-pinned scored audit in a throw-away venv, reports the score with and without Tier-C (convention-only) points, tags every recommendation A/B/C/SEC, and checks that robots.txt/llms.txt/sitemap exist at the HOST ROOT (the sub-path trap). Use for a baseline, a CI gate, or a post-deploy re-measure.
---

# x-eo-audit — measure

Shared tiers, honesty rules and report template: `../x-eo/SKILL.md`. Traps: `../x-eo/references/pitfalls.md`.
Scripts below are relative to this skill's directory.

## Steps

1. **Scored audit.** `bash scripts/audit.sh [--threshold N] [--out DIR] <url> [<url>…]`
   - Installs `geo-optimizer-skill` (MIT, pinned; override with `GEO_OPTIMIZER_VERSION`) into a temp venv. No global install.
   - Prints `score X/100 (band)`, **`excluding Tier C: a/b = n%`**, category breakdown, and recommendations tagged A/B/C/SEC. Tags are keyword heuristics — read the finding.
   - Exit 1 below `--threshold` (CI use).
2. **Host-root check.** `bash scripts/host-root-check.sh <url>` — `robots.txt`, `sitemap.xml`, `llms.txt`, `/.well-known/ai.txt`, `/ai/*` are only read at the host root. Reports "exists under /sub/ but crawlers read the ROOT only", blanket `Disallow`, missing `Sitemap:` line, and absent explicit rules for OAI-SearchBot / Claude-SearchBot / PerplexityBot / Googlebot / Bingbot.
3. **Render check** (Tier A, scores often miss it): `node ../x-eo-verify/scripts/render-diff.mjs <url>`.
4. **Topic checklists.** For anything the scorer doesn't cover (content/E-E-A-T, hreflang, images, local, e-commerce, sitemap rules), open the matching file from the topic map in `../x-eo/SKILL.md`.
5. **Triage** by tier and write the report. Save the numbers: the same tool+version is needed to compare later.

## Rules
- Only audit sites the user owns or may test. Never point at private/loopback addresses (the tool refuses; keep it that way). For your own dev server use `../x-eo-verify/scripts/local-audit.py`.
- Scores of different tools are not comparable. Compare same tool, same version, before/after.
- The scorer's weights are its author's opinion, not search-engine behaviour.
- **SEC findings need a second look.** The UGC/injection check matches class names (`respond`, `comments`, …). Report it only after confirming a real write path (form, textarea, API) exists; otherwise label it a false positive (pitfall 11).

---
name: x-eo
description: One-stop SEO + AEO + GEO toolkit entry point. Use for any request about search visibility, AI-search / answer-engine readiness, "GEO score", llms.txt, structured data (JSON-LD), robots.txt and AI crawlers, sitemaps, hreflang/i18n SEO, E-E-A-T/content, local or e-commerce SEO, or when a site scores low on tools like geo-optimizer or tryoreum. Routes to x-eo-audit (measure), x-eo-fix (change), x-eo-verify (prove nothing broke). Every recommendation is graded by evidence tier.
---

# x-eo — router and shared rules

Reply in the user's language. **An audit score is a proxy, not the outcome.** Tools reward files and
markup; what matters is whether crawlers can read the page and whether engines cite it. So every
finding carries an evidence tier, and you never oversell.

## Four skills, one loop

| Skill | Job | Use when |
|---|---|---|
| `x-eo-audit` | Measure: scored audit (Tier C separated), host-root check, topic checklists | "how are we doing?", baseline, re-measure after deploy |
| `x-eo-fix` | Change: robots, JSON-LD, llms-full, AI files, sub-path root, IndexNow | a finding needs implementing |
| `x-eo-verify` | Prove: before/after build diff, JSON-LD parse, JS-on/off render diff | before shipping any change meant to raise a score |
| `x-eo` (this) | Shared tiers, honesty rules, topic map | start here, or for pure advice/planning |

Typical order: **audit → fix → verify → deploy → audit (live)**. Install all four together.

## Evidence tiers (label every finding)

| Tier | Meaning | Examples | Treatment |
|---|---|---|---|
| **A** | Vendor-documented or directly observable | reachable (200, no auth wall); content in raw HTML without JS; correct canonical/hreflang; sitemap; robots not blocking search crawlers; JSON-LD that parses and matches visible text | Fix first |
| **B** | Plausible; third-party/correlational support | question-shaped headings, self-contained answer passages, freshness, entity consistency + `sameAs`, original data, off-site mentions | Do when it also serves readers; say "plausible" |
| **C** | Convention, no demonstrated consumption | `llms.txt`, `llms-full.txt`, `ai.txt`, `/ai/*.json`, WebMCP, agent `SearchAction`, RSS-for-AI | Only if free and risk-free. **Never count as success.** Google's AI guide (2026-07-10) says it ignores them |
| **SEC** | Security finding | prompt-injection surface, exposed secrets | Report separately |

Sources and what was verified vs only reported: [references/evidence.md](references/evidence.md).
Thirteen recurring traps: [references/pitfalls.md](references/pitfalls.md). Tool landscape: [references/tools.md](references/tools.md).

## Topic map — where the knowledge is

Vendored, condensed from claude-seo (MIT, see [NOTICE](references/claude-seo/NOTICE.md)). Read only the file for the topic at hand.

| Topic | File |
|---|---|
| Crawl/index, CWV, security headers, JS rendering, mobile | [technical](references/claude-seo/technical.md) |
| Single-page on-page review (title, meta, headings, links) | [page-analysis](references/claude-seo/page-analysis.md) |
| Content quality, E-E-A-T, AI-content, readability | [content-eeat](references/claude-seo/content-eeat.md) |
| Structured data / JSON-LD types and rules | [schema](references/claude-seo/schema.md) |
| GEO: AI Overviews, ChatGPT/Perplexity citation tactics, passage structure, llms.txt stance | [geo](references/claude-seo/geo.md) |
| Agentic / MCP / machine-readable readiness | [agentic](references/claude-seo/agentic.md) |
| Sitemaps (size limits, lastmod, index files) | [sitemap](references/claude-seo/sitemap.md) |
| Images (alt, formats, lazy loading, OG) | [images](references/claude-seo/images.md) |
| Multilingual: hreflang, locale URLs | [hreflang](references/claude-seo/hreflang.md) |
| Local SEO / business profile | [local](references/claude-seo/local.md) |
| E-commerce / product schema | [ecommerce](references/claude-seo/ecommerce.md) |
| Strategy, roadmap, competitor framing | [planning](references/claude-seo/planning.md) |
| Korea: Naver Search Advisor, Yeti/Daumoa, KakaoTalk previews, IndexNow | [korea](references/korea.md) (original) |

Claude-seo's advice is vendored as knowledge, not authority: where it conflicts with this file's tiers, the tiers win.

## Honesty rules

- Don't invent facts to satisfy a check: no fake `dateModified`, no `sameAs` to profiles that aren't the entity's, no made-up address/phone/reviews.
- Don't put personal data (email, phone) in structured data on many pages for a point.
- Keyword-density / boilerplate warnings can be false positives on legitimate content — say so.
- A tool's recommendation list is a menu, not a to-do list.
- Report the score **and** the score excluding Tier C.
- Citation in ChatGPT/Claude/Perplexity is only **sampled** (`x-eo-audit/scripts/ai-recall.mjs`, needs API keys), never measured as a rate; don't promise it.

## Report template

```
Scope: <urls>   Tool: <name+version>   Date: <date>
Score: A → B   (excluding Tier C: a% → b%)
Done:   [A] … [B] … [C] …
Skipped: … (why)
Verified: build diff, JSON-LD parse, JS on/off DOM, live re-measure
Not expected to move: … (Tier C points are optionality)
```

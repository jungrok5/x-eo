---
name: x-eo-fix
description: Implement SEO/AEO/GEO fixes safely. Generates robots.txt with per-bot policy, JSON-LD from truthful templates, llms-full.txt from the real page, optional AI discovery files (Tier C), the root-site scaffold for sub-path hosting (GitHub Pages project sites), and IndexNow submissions. Use after x-eo-audit produced findings, and always pair with x-eo-verify before shipping.
---

# x-eo-fix — change

Tiers/honesty: `../x-eo/SKILL.md`. After any change run `x-eo-verify`. Scripts/templates relative to this directory.

## Principles
1. **Change the source, not the output.** If pages are generated, edit the generator/template and rebuild. If a template is also an output file, make the build idempotent (pitfall 3: wrap generated regions in `<!--pre-->…<!--/pre-->`, strip when reading, hash after builds #1–#3).
2. **Tier A before B before C.** Tier C only if it costs nothing and is true.
3. **Truth only.** Delete a placeholder property instead of inventing a value.
4. Smallest diff that fixes the finding. Don't restyle unrelated pages.

## Recipes

| Need | Do |
|---|---|
| robots.txt (explicit per-bot, by purpose) | `python3 scripts/gen-robots.py --sitemap https://H/sitemap.xml [--policy allow-all\|search-only\|block-ai] [--disallow /admin/] --out robots.txt` — never emits blanket `Disallow: /` |
| JSON-LD | copy from `templates/jsonld/` (website, organization, person, profilepage, article, faqpage); fill only true fields; markup must match visible text |
| No-JS content missing (Tier A) | prerender at build time (static HTML of the main content); see `../x-eo-verify` render-diff to prove it |
| Site lives at `host/project/` | use `templates/subpath-root/` in a root site/repo (`<user>.github.io`); canonical stays on the real page |
| `llms-full.txt` (Tier C) | `node scripts/html-to-llms-full.mjs --in index.html --out llms-full.txt --title … --url … [--from … --to …]` — regenerate on every build; strip third-party copyrighted regions (e.g. Scripture translations) |
| `ai.txt` / `/ai/*.json` (Tier C) | `node scripts/gen-ai-files.mjs --config site.json --out ./public` |
| Notify Bing/Naver/Yandex | `node scripts/indexnow.mjs --host H --key K --sitemap URL` (key file must be live; Google doesn't support IndexNow) |
| Search Console | URL-prefix property accepts only sitemaps under its prefix; root sitemap is advertised by `Sitemap:` in root robots.txt |
| Anything else (hreflang, images, schema types, content) | topic files listed in `../x-eo/SKILL.md` |

## Don'ts
- No fake `dateModified`, no unowned `sameAs`, no personal data in site-wide schema.
- No `Disallow` added while "fixing" robots; count them.
- Don't weaken a tool's SSRF guard to make an audit pass.

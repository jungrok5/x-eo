# JSON-LD templates

Copy one, replace every `__PLACEHOLDER__`, **delete any property you cannot truthfully fill**
(an absent property is always better than an invented one), then validate with
`x-eo-verify/scripts/jsonld-lint.py`.

- Markup must describe what is visible on the page (Tier A rule). Never mark up hidden content.
- `sameAs` only lists profiles that are really the same entity.
- `dateModified` only when content actually changed — not the build time.
- No personal email/phone/address unless the person published it on the page on purpose.
- Google documents which types are eligible for rich results; FAQPage rich results are limited to
  well-known government/health sites, so FAQ markup is Tier B for most sites.

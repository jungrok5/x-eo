# Sub-path site → host root files

Problem: the site lives at `https://host/project/` but crawlers read `robots.txt`, `llms.txt`,
`/.well-known/*`, `/ai/*` only at `https://host/`.

GitHub Pages: create the repo `<user>.github.io` and put these files at its root, replacing
`__HOST__` and `__PATH__` (e.g. `/resume/`). Keep `canonical` on the real page.

- `index.html` — redirect stub (meta refresh + JS), canonical points to the real page.
- `robots.txt` — generate with `x-eo-fix/scripts/gen-robots.py` (Sitemap line = root sitemap).
- `sitemap.xml` — sitemap index pointing to the project's own sitemap.

Search Console: a URL-prefix property for `https://host/project/` rejects the root sitemap.
Do not submit it there; root `robots.txt` advertises it.

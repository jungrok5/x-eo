#!/usr/bin/env python3
"""Parse every JSON-LD block in every .html under a directory.
Usage: jsonld-lint.py DIR [--require Type1,Type2] [--only GLOB]
  Parse errors always fail (exit 1). Missing --require types are reported separately and fail only
  with --strict, because sub-pages (about/, maps/ ...) legitimately carry different schema types.
  --only restricts which pages --require applies to, e.g. --only "index.html" or --only "*/index.html".
Required types are checked per page across all of its JSON-LD blocks (a page may split WebSite and
FAQPage into two scripts). Reports parse failures and the types seen."""
import json, re, sys, pathlib
args = sys.argv[1:]
if not args: sys.exit(__doc__)
root = pathlib.Path(args[0]); req = set()
if "--require" in args: req = set(args[args.index("--require") + 1].split(","))
SKIP = {".git", "node_modules", ".claude", ".github"}
bad = n = 0; missing = []; types_seen = {}
only = args[args.index("--only") + 1] if "--only" in args else None
strict = "--strict" in args
def _glob(p):  # '*' = one path segment, '**' = any depth
    return re.compile("^" + re.escape(p).replace(r"\*\*", ".*").replace(r"\*", "[^/]*") + "$")
only_re = _glob(only) if only else None
def _types(node, acc):
    if isinstance(node, list):
        for x in node: _types(x, acc)
    elif isinstance(node, dict):
        t = node.get("@type")
        acc.update([t] if isinstance(t, str) else [x for x in (t or []) if isinstance(x, str)])
        if "@graph" in node: _types(node["@graph"], acc)
for f in sorted(root.rglob("*.html")):
    if SKIP & set(f.parts): continue
    s = f.read_text(encoding="utf-8", errors="replace")
    blocks = re.findall(r'<script[^>]+application/ld\+json[^>]*>\s*(.*?)\s*</script>', s, re.S | re.I)
    page_types = set()
    for b in blocks:
        n += 1
        try:
            d = json.loads(b)
        except Exception as e:
            bad += 1; print(f"PARSE ERROR {f.relative_to(root)}: {e}"); continue
        types = set(); _types(d, types)
        for t in types: types_seen[t] = types_seen.get(t, 0) + 1
        page_types |= types
    applies = only_re is None or only_re.match(f.relative_to(root).as_posix())
    if req and applies and (req - page_types): missing.append((str(f.relative_to(root)), sorted(req - page_types)))
for p, m in missing[:20]: print(f"MISSING {p}: {m}")
if len(missing) > 20: print(f"... and {len(missing) - 20} more pages missing required types")
print(f"{n} JSON-LD blocks; {bad} parse errors; {len(missing)} pages missing required types; types: {dict(sorted(types_seen.items()))}")
sys.exit(1 if bad or (strict and missing) else 0)

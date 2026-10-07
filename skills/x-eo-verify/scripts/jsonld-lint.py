#!/usr/bin/env python3
"""Parse every JSON-LD block in every .html under a directory.
Usage: jsonld-lint.py DIR [--require Type1,Type2] [--only GLOB]
  Parse errors always fail (exit 1). Missing --require types are reported separately and fail only
  with --strict, because sub-pages (about/, maps/ ...) legitimately carry different schema types.
  --only restricts which pages --require applies to, e.g. --only "index.html" or --only "*/index.html".
Reports parse failures, the @graph types, and the average attribute count per node
(some checkers want >=5 for a 'rich' schema — but only add attributes that are TRUE)."""
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
for f in sorted(root.rglob("*.html")):
    if SKIP & set(f.parts): continue
    s = f.read_text(encoding="utf-8", errors="replace")
    blocks = re.findall(r'<script[^>]+application/ld\+json[^>]*>\s*(.*?)\s*</script>', s, re.S | re.I)
    for b in blocks:
        n += 1
        try:
            d = json.loads(b)
            nodes = d.get("@graph", [d]) if isinstance(d, dict) else d
            types = {t for x in nodes for t in ([x.get("@type")] if isinstance(x.get("@type"), str) else x.get("@type", []))}
            for t in types: types_seen[t] = types_seen.get(t, 0) + 1
            applies = only_re is None or only_re.match(f.relative_to(root).as_posix())
            if req and applies and (req - types): missing.append((str(f.relative_to(root)), sorted(req - types)))
        except Exception as e:
            bad += 1; print(f"PARSE ERROR {f.relative_to(root)}: {e}")
for p, m in missing[:20]: print(f"MISSING {p}: {m}")
if len(missing) > 20: print(f"... and {len(missing) - 20} more pages missing required types")
print(f"{n} JSON-LD blocks; {bad} parse errors; {len(missing)} pages missing required types; types: {dict(sorted(types_seen.items()))}")
sys.exit(1 if bad or (strict and missing) else 0)

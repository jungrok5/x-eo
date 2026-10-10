#!/usr/bin/env bash
# Measure AEO/GEO readiness with geo-optimizer-skill (MIT) in a throw-away venv, then re-read the score by evidence tier.
# Usage: audit.sh [--threshold N] [--out DIR] URL [URL ...]
# Env:   GEO_OPTIMIZER_VERSION (default pinned below) - pin it so before/after runs stay comparable.
set -euo pipefail
VER="${GEO_OPTIMIZER_VERSION:-4.18.3}"
THRESHOLD=""; OUT=""; URLS=()
while [ $# -gt 0 ]; do case "$1" in
  --threshold) THRESHOLD="$2"; shift 2;;
  --out) OUT="$2"; shift 2;;
  -h|--help) sed -n 2,5p "$0"; exit 0;;
  *) URLS+=("$1"); shift;; esac; done
[ ${#URLS[@]} -gt 0 ] || { echo "usage: audit.sh [--threshold N] [--out DIR] URL..." >&2; exit 2; }

T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
python3 -m venv "$T/v"
"$T/v/bin/pip" install -q "geo-optimizer-skill==${VER}" 2>&1 | grep -v "notice" || true
[ -n "$OUT" ] && mkdir -p "$OUT"

cat > "$T/summarize.py" <<'PYEOF'
import json, sys
url, ver, thr = sys.argv[1], sys.argv[2], sys.argv[3]
try:
    d = json.load(sys.stdin)
except Exception:
    print("\n== " + url + "\n   audit failed (blocked, unreachable, or tool error)")
    sys.exit(3)
bd = d.get("score_breakdown") or {}
MAX = {"robots": 18, "llms": 18, "schema": 16, "meta": 14, "content": 12,
       "signals": 6, "ai_discovery": 6, "brand_entity": 10}
score = d.get("score", 0)
# Tier C = llms.txt + AI-discovery files: conventions with no demonstrated consumption by major engines.
c_pts = bd.get("llms", 0) + bd.get("ai_discovery", 0)
c_max = MAX["llms"] + MAX["ai_discovery"]
rest, rest_max = score - c_pts, 100 - c_max
print("\n== %s   (geo-optimizer-skill %s)" % (url, ver))
print("   score %s/100 (%s)   excluding Tier C: %s/%s = %.0f%%"
      % (score, d.get("band", ""), rest, rest_max, 100.0 * rest / rest_max))
print("   " + ", ".join("%s=%s/%s" % (k, bd.get(k, 0), m) for k, m in MAX.items())
      + ", penalty=%s" % bd.get("negative_penalty", 0))

import re

def tier(r):
    l = r.lower()
    if "injection" in l or "prompt" in l:
        return "SEC"   # trust/security finding, not a ranking lever
    # Entity details are only worth adding if TRUE for this site - never invent them (Tier B at best).
    # Organization/FAQ markup: a site without an organization or a visible FAQ must not add one for points;
    # FAQ rich results are limited to a few site types, so it is not an engine-documented requirement.
    if any(k in l for k in ("sameas", "address", "telephone", "contactpoint", "knowledge graph",
                            "statistics", "numerical", "author", "brand", "organization", "faq")):
        return "B"
    if any(k in l for k in ("llms.txt", "ai.txt", "/ai/", "webmcp", "searchaction", "potentialaction",
                            "rss", "atom")) or re.search(r"\bforms?\b", l):
        return "C"
    if any(k in l for k in ("robots", "canonical", "hreflang", "title", "description", "javascript",
                            "sitemap", "json-ld", "schema", "h1", "heading", "<main>")):
        return "A"
    return "B"

for t, r in sorted((tier(r), r) for r in (d.get("recommendations") or [])):
    print("   [%s] %s" % (t, r[:150]))
sys.exit(0 if not thr or score >= int(thr) else 1)
PYEOF

FAIL=0
for u in "${URLS[@]}"; do
  RAW="$("$T/v/bin/geo" audit --url "$u" --format json 2>/dev/null || true)"
  if [ -n "$OUT" ]; then printf '%s' "$RAW" > "$OUT/$(echo "$u" | tr -c 'A-Za-z0-9' '_').json"; fi
  printf '%s' "$RAW" | python3 -I "$T/summarize.py" "$u" "$VER" "${THRESHOLD:-}" || FAIL=1
done
exit $FAIL

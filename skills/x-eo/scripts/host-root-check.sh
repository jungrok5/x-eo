#!/usr/bin/env bash
# Are the crawler-facing files where crawlers look? (host root, not the page's sub-path)
# Usage: host-root-check.sh URL
set -euo pipefail
URL="${1:?usage: host-root-check.sh URL}"
python3 -I - "$URL" <<'PY'
import sys, urllib.request, urllib.parse, re
u = urllib.parse.urlparse(sys.argv[1]); root = f"{u.scheme}://{u.netloc}"
sub = u.path.rstrip("/")
def get(url):
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "x-eo/1.0"}), timeout=20)
        return r.status, r.read(400000).decode("utf-8", "replace")
    except Exception as e:
        return getattr(e, "code", 0), ""
paths = ["/robots.txt", "/sitemap.xml", "/llms.txt", "/llms-full.txt", "/.well-known/ai.txt", "/ai/summary.json"]
print(f"host root: {root}   page path: {sub or '/'}")
bad = 0
for p in paths:
    s, body = get(root + p)
    ok = s == 200 and body.strip() != ""
    tier = "A" if p in ("/robots.txt", "/sitemap.xml") else "C"
    note = ""
    if not ok and sub:
        s2, b2 = get(root + sub + p)
        if s2 == 200 and b2.strip(): note = f"  <-- exists under {sub}{p} but crawlers read the ROOT only"
    print(f"  [{tier}] {p:<22} {'OK ' if ok else 'MISSING'} (HTTP {s}){note}")
    if tier == "A" and not ok: bad += 1
s, robots = get(root + "/robots.txt")
if s == 200:
    disallow_all = re.search(r"(?im)^user-agent:\s*\*\s*\n(?:(?!user-agent:).*\n)*?disallow:\s*/\s*$", robots)
    print("  robots: blanket 'Disallow: /' for *  ->", "YES (blocks everything!)" if disallow_all else "no")
    print("  robots: Sitemap line present        ->", "yes" if re.search(r"(?im)^sitemap:", robots) else "NO")
    for bot in ("OAI-SearchBot", "Claude-SearchBot", "PerplexityBot", "Googlebot", "Bingbot"):
        blk = re.search(rf"(?is)user-agent:\s*{bot}\s*\n(.*?)(?:\n\s*\n|\Z)", robots)
        print(f"  robots: {bot:<17} ->", ("explicit: " + ("BLOCKED" if blk and re.search(r"(?im)^disallow:\s*/\s*$", blk.group(1)) else "allowed")) if blk else "via wildcard")
sys.exit(1 if bad else 0)
PY

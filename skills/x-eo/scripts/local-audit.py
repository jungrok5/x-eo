#!/usr/bin/env python3
"""TEST-ONLY: run geo-optimizer against YOUR OWN local dev server (127.0.0.1 / localhost).
The tool refuses local targets on purpose (SSRF protection). This relaxes the guard inside this one
process, for loopback only, and only if X_EO_ALLOW_LOCAL=1. Never patch the installed package instead.
Usage: X_EO_ALLOW_LOCAL=1 python3 local-audit.py http://127.0.0.1:8000/ ...   (run with the venv python)"""
import os, sys, urllib.parse
if os.environ.get("X_EO_ALLOW_LOCAL") != "1": sys.exit(__doc__)
import geo_optimizer.utils.validators as v
def _loop(u): return urllib.parse.urlparse(u).hostname in ("127.0.0.1", "localhost", "::1")
_orig_pub, _orig_res = v.validate_public_url, v.resolve_and_validate_url
v.validate_public_url = lambda u: (True, "") if _loop(u) else _orig_pub(u)
v.resolve_and_validate_url = lambda u: (True, None, ["127.0.0.1"]) if _loop(u) else _orig_res(u)
from geo_optimizer import audit
from geo_optimizer.core.scoring import compute_score_breakdown
for url in sys.argv[1:]:
    if not _loop(url): print("refusing non-loopback target:", url); continue
    r = audit(url); print(url, r.score, getattr(r, "band", ""), compute_score_breakdown(r))

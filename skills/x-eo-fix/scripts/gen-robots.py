#!/usr/bin/env python3
"""Generate a robots.txt with explicit per-bot groups, grouped by purpose.

usage: gen-robots.py --sitemap URL [--policy allow-all|search-only|block-ai] [--disallow /private/ ...] [--out robots.txt]

Policies
  allow-all    (default) every listed bot is allowed. Behaviour-neutral vs. a bare `User-agent: * / Allow: /`,
               but some checkers only credit explicit groups.
  search-only  search/answer-retrieval + user-fetch bots allowed; model-TRAINING bots disallowed.
  block-ai     all AI bots disallowed; classic search bots (Googlebot, Bingbot, ...) stay allowed.

Never emits a blanket `Disallow: /` for `*`. Bot names/purposes change; re-check vendor docs before relying on them.
"""
import argparse, sys

# (token, vendor, purpose)  purpose: search | user | train
BOTS = [
    ("Googlebot", "Google", "classic"), ("Bingbot", "Microsoft", "classic"),
    ("OAI-SearchBot", "OpenAI", "search"), ("ChatGPT-User", "OpenAI", "user"), ("GPTBot", "OpenAI", "train"),
    ("Claude-SearchBot", "Anthropic", "search"), ("Claude-User", "Anthropic", "user"), ("ClaudeBot", "Anthropic", "train"),
    ("PerplexityBot", "Perplexity", "search"), ("Perplexity-User", "Perplexity", "user"),
    ("Google-Extended", "Google (Gemini/AI training opt-out token)", "train"),
    ("Applebot-Extended", "Apple (AI training opt-out token)", "train"),
    ("CCBot", "Common Crawl", "train"),
]
LABEL = {"classic": "Classic search crawlers", "search": "AI search / answer retrieval",
         "user": "AI fetch on behalf of a user request", "train": "Model-training crawlers / opt-out tokens"}

def allowed(purpose, policy):
    if policy == "allow-all": return True
    if policy == "search-only": return purpose != "train"
    if policy == "block-ai": return purpose == "classic"
    raise ValueError(policy)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sitemap", required=True)
    ap.add_argument("--policy", default="allow-all", choices=["allow-all", "search-only", "block-ai"])
    ap.add_argument("--disallow", nargs="*", default=[], help="path prefixes to keep out for everyone (e.g. /admin/)")
    ap.add_argument("--out", default="-")
    a = ap.parse_args()
    for d in a.disallow:
        if d.strip() in ("", "/"): sys.exit("refusing blanket Disallow: /")
    L = [f"# robots.txt — policy: {a.policy}", ""]
    for purpose in ("classic", "search", "user", "train"):
        grp = [b for b in BOTS if b[2] == purpose]
        L.append(f"# {LABEL[purpose]}")
        for tok, vendor, _ in grp:
            L.append(f"User-agent: {tok}")
            if allowed(purpose, a.policy):
                L.append("Allow: /")
                L += [f"Disallow: {d}" for d in a.disallow]
            else:
                L.append("Disallow: /")
            L.append("")
    L += ["# Everyone else", "User-agent: *", "Allow: /"] + [f"Disallow: {d}" for d in a.disallow] + ["", f"Sitemap: {a.sitemap}", ""]
    txt = "\n".join(L)
    if a.out == "-": sys.stdout.write(txt)
    else:
        open(a.out, "w").write(txt); print(f"[robots] wrote {a.out} ({a.policy})")
main()

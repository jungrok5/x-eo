#!/usr/bin/env python3
"""Site-level sample: what a crawler sees across several pages, not just one.

usage: site-sample.py URL [--max 8] [--thin 1500] [--json]

Reads robots.txt (Sitemap: lines) and the sitemap, samples the home page plus up to --max pages spread
across the sitemap, fetches each once, and reports per page: status, final URL, title, description,
canonical, robots meta, H1 count, OG, JSON-LD blocks, text length, internal links, images without alt.
Then flags cross-page issues: duplicate titles/descriptions, missing/multiple H1, noindex pages listed
in the sitemap, canonical pointing elsewhere, thin pages, a home page that is only a redirect stub.
Tiers: [A] documented crawl/index behaviour  [B] on-page convention  — see ../x-eo/SKILL.md.
Standard library only. Public URLs only; one fetch per page; identifies itself in the User-Agent.
"""
import argparse, html, json, re, sys, urllib.request, urllib.parse
from html.parser import HTMLParser
from collections import Counter

UA = "x-eo-site-sample/1.0 (+https://github.com/jungrok5/x-eo)"

def get(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,application/xml;q=0.9,*/*;q=0.5"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.geturl(), r.read(2_000_000).decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, url, ""
    except Exception as e:
        return 0, url, str(e)

def norm(u):
    p = urllib.parse.urlsplit(u)
    path = p.path or "/"
    return urllib.parse.urlunsplit((p.scheme.lower(), p.netloc.lower(), path.rstrip("/") or "/", "", ""))

class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ""; self.desc = ""; self.robots = ""; self.canonical = ""; self.lang = ""
        self.og = {}; self.h1 = 0; self.jsonld = 0; self.jsonld_bad = 0; self.refresh = ""
        self.links = []; self.img = 0; self.img_noalt = 0; self.text = []
        self._in = None; self._skip = 0; self._ld = False
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html": self.lang = a.get("lang", "")
        elif tag == "title": self._in = "title"
        elif tag == "meta":
            n = (a.get("name") or "").lower(); p = (a.get("property") or "").lower(); c = a.get("content", "") or ""
            if n == "description": self.desc = c.strip()
            elif n == "robots": self.robots = c
            elif p.startswith("og:"): self.og[p] = c
            elif (a.get("http-equiv") or "").lower() == "refresh": self.refresh = c
        elif tag == "link" and (a.get("rel") or "").lower() == "canonical": self.canonical = a.get("href", "")
        elif tag == "h1": self.h1 += 1
        elif tag == "script":
            self._skip += 1
            if (a.get("type") or "").lower() == "application/ld+json": self._ld = True; self._buf = []
        elif tag in ("style", "noscript", "template", "svg"): self._skip += 1
        elif tag == "a" and a.get("href"): self.links.append(a["href"])
        elif tag == "img":
            self.img += 1
            if not (a.get("alt") or "").strip() and a.get("alt") is None: self.img_noalt += 1
    def handle_endtag(self, tag):
        if tag == "title": self._in = None
        elif tag == "script":
            if self._ld:
                self.jsonld += 1
                try: json.loads("".join(self._buf))
                except Exception: self.jsonld_bad += 1
                self._ld = False
            self._skip = max(0, self._skip - 1)
        elif tag in ("style", "noscript", "template", "svg"): self._skip = max(0, self._skip - 1)
    def handle_data(self, d):
        if self._in == "title": self.title += d
        elif self._ld: self._buf.append(d)
        elif not self._skip: self.text.append(d)

def sitemap_urls(sm_url, host, depth=0, limit=5000):
    st, _, body = get(sm_url)
    if st != 200: return []
    locs = re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", body)
    if "<sitemapindex" in body and depth < 1:
        out = []
        for child in locs[:10]: out += sitemap_urls(child, host, depth + 1, limit)
        return out[:limit]
    return [html.unescape(u) for u in locs if urllib.parse.urlsplit(u).netloc.lower() == host][:limit]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url"); ap.add_argument("--max", type=int, default=8); ap.add_argument("--thin", type=int, default=1500)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    start = a.url if "://" in a.url else "https://" + a.url
    sp = urllib.parse.urlsplit(start); host = sp.netloc.lower(); root = f"{sp.scheme}://{sp.netloc}"
    issues = []
    # robots + sitemaps (host root only)
    st, _, robots = get(root + "/robots.txt")
    sitemaps = re.findall(r"(?im)^\s*sitemap:\s*(\S+)", robots) if st == 200 else []
    if st != 200: issues.append(("A", "no /robots.txt at host root (HTTP %s)" % st))
    if not sitemaps: sitemaps = [root + "/sitemap.xml"]; issues.append(("A", "robots.txt has no Sitemap: line; trying /sitemap.xml"))
    urls = []
    for sm in sitemaps[:3]: urls += sitemap_urls(sm, host)
    urls = list(dict.fromkeys(norm(u) for u in urls))
    if not urls: issues.append(("A", "no sitemap URLs found on this host (%s)" % ", ".join(sitemaps[:3])))
    # sample: root home, the requested page, then evenly spread
    sample = [norm(root + "/"), norm(start)]
    if urls:
        step = max(1, len(urls) // max(1, a.max - 2))
        sample += urls[::step]
    sample = list(dict.fromkeys(sample))[: max(2, a.max)]
    pages = []
    for u in sample:
        st, final, body = get(u)
        p = Page()
        if body and st == 200: p.feed(body)
        text = re.sub(r"\s+", " ", " ".join(p.text)).strip()
        internal = {norm(urllib.parse.urljoin(final, h)) for h in p.links if not h.startswith(("#", "mailto:", "tel:", "javascript:"))}
        internal = {x for x in internal if urllib.parse.urlsplit(x).netloc.lower() == host and x != norm(final)}
        pages.append(dict(url=u, status=st, final=norm(final), title=p.title.strip(), title_len=len(p.title.strip()),
            desc=p.desc, desc_len=len(p.desc), canonical=p.canonical, robots=p.robots, lang=p.lang, h1=p.h1,
            og=bool(p.og.get("og:title")) and bool(p.og.get("og:image")), jsonld=p.jsonld, jsonld_bad=p.jsonld_bad,
            text_len=len(text), internal_links=len(internal), img=p.img, img_noalt=p.img_noalt, refresh=bool(p.refresh)))
    # cross-page issues
    ok = [p for p in pages if p["status"] == 200]
    for p in pages:
        if p["status"] != 200: issues.append(("A", f"{p['url']} -> HTTP {p['status']}"))
    for p in ok:
        if not p["title"]: issues.append(("A", f"{p['url']}: no <title>"))
        if "noindex" in p["robots"].lower() and p["url"] in urls: issues.append(("A", f"{p['url']}: noindex but listed in sitemap"))
        if p["canonical"] and norm(p["canonical"]) != p["final"]: issues.append(("A", f"{p['url']}: canonical points to {p['canonical']} (this URL is not the canonical one)"))
        if p["jsonld_bad"]: issues.append(("A", f"{p['url']}: {p['jsonld_bad']} JSON-LD block(s) fail to parse"))
        if not p["desc"]: issues.append(("B", f"{p['url']}: no meta description"))
        if p["h1"] != 1: issues.append(("B", f"{p['url']}: {p['h1']} <h1> (convention is exactly one)"))
        if not p["og"]: issues.append(("B", f"{p['url']}: og:title/og:image missing (link previews in chat apps)"))
        if p["text_len"] < a.thin and not p["refresh"]: issues.append(("B", f"{p['url']}: thin — {p['text_len']} chars of text without JS (< {a.thin})"))
        if p["img_noalt"]: issues.append(("B", f"{p['url']}: {p['img_noalt']}/{p['img']} images without alt"))
    home = pages[0]
    if home["refresh"] or (home["status"] == 200 and home["text_len"] < 300 and home["canonical"] and norm(home["canonical"]) != home["final"]):
        issues.append(("A", f"host root {home['url']} is a redirect stub (meta refresh / canonical elsewhere): site-level checkers score it as your home page — give it a real title, description, OG and H1, or make it a real page"))
    for key, label in (("title", "title"), ("desc", "description")):
        for v, n in Counter(p[key] for p in ok if p[key]).items():
            if n > 1: issues.append(("B", f"{n} sampled pages share the same {label}: {v[:60]!r}"))
    if a.json:
        print(json.dumps(dict(host=host, sitemaps=sitemaps, sitemap_urls=len(urls), pages=pages, issues=issues), ensure_ascii=False, indent=1)); return
    print(f"host {host} · sitemaps {len(sitemaps)} · {len(urls)} URLs in sitemap · sampled {len(pages)}")
    print(f"{'status':6} {'h1':>2} {'ld':>2} {'og':>2} {'text':>6} {'links':>5} {'title':>5} {'desc':>4}  url")
    for p in pages:
        print(f"{p['status']:<6} {p['h1']:>2} {p['jsonld']:>2} {'y' if p['og'] else '-':>2} {p['text_len']:>6} {p['internal_links']:>5} {p['title_len']:>5} {p['desc_len']:>4}  {p['url']}")
    print("issues:" if issues else "issues: none")
    for t, m in sorted(issues, key=lambda x: x[0]): print(f"  [{t}] {m}")
main()

#!/usr/bin/env python3
"""Behaviour tests for the x-eo scripts. No network: every HTTP check runs against a local fixture server.

run: python3 -m unittest discover -s tests -v
Optional: X_EO_TEST_NODE_MODULES=/path/to/node_modules (with playwright-core) and PLAYWRIGHT_CHROMIUM
enable the render-diff test; without them it is skipped.
"""
import json, os, pathlib, re, shutil, subprocess, sys, tempfile, threading, unittest, urllib.robotparser
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

R = pathlib.Path(__file__).resolve().parent.parent
S = R / "skills"
AUDIT = S / "x-eo-audit/scripts"; FIX = S / "x-eo-fix/scripts"; VERIFY = S / "x-eo-verify/scripts"
PY = sys.executable


def run(*cmd, **kw):
    return subprocess.run([str(c) for c in cmd], capture_output=True, text=True, timeout=120, **kw)


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *a): pass


class Site:
    """Serve a dict {path: content} from a temp dir on 127.0.0.1."""
    def __init__(self, files):
        self.dir = pathlib.Path(tempfile.mkdtemp())
        for path, body in files.items():
            f = self.dir / path.lstrip("/"); f.parent.mkdir(parents=True, exist_ok=True); f.write_text(body)
        self.srv = ThreadingHTTPServer(("127.0.0.1", 0), partial(Quiet, directory=str(self.dir)))
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()
        self.url = f"http://127.0.0.1:{self.srv.server_port}"
    def close(self):
        self.srv.shutdown(); self.srv.server_close(); shutil.rmtree(self.dir, ignore_errors=True)


def page(title="Page", body="<h1>Page</h1><p>text</p>", head=""):
    return f"<!doctype html><html lang='en'><head><title>{title}</title>{head}</head><body>{body}</body></html>"


# ---------------------------------------------------------------------------------------------- fix
class GenRobots(unittest.TestCase):
    def robots(self, *args):
        r = run(PY, FIX / "gen-robots.py", "--sitemap", "https://e.com/sitemap.xml", *args)
        self.assertEqual(r.returncode, 0, r.stderr)
        rp = urllib.robotparser.RobotFileParser(); rp.parse(r.stdout.splitlines())
        return r.stdout, rp

    def test_allow_all_allows_every_bot_and_lists_sitemap(self):
        txt, rp = self.robots()
        for bot in ("Googlebot", "GPTBot", "OAI-SearchBot", "ClaudeBot", "Yeti", "Daumoa", "SomeNewBot"):
            self.assertTrue(rp.can_fetch(bot, "https://e.com/page"), bot)
        self.assertIn("Sitemap: https://e.com/sitemap.xml", txt)
        self.assertNotRegex(txt, r"(?m)^Disallow: /\s*$")

    def test_search_only_blocks_training_bots_only(self):
        _, rp = self.robots("--policy", "search-only")
        self.assertFalse(rp.can_fetch("GPTBot", "https://e.com/"))
        self.assertFalse(rp.can_fetch("ClaudeBot", "https://e.com/"))
        self.assertTrue(rp.can_fetch("OAI-SearchBot", "https://e.com/"))
        self.assertTrue(rp.can_fetch("Googlebot", "https://e.com/"))

    def test_block_ai_keeps_classic_search(self):
        _, rp = self.robots("--policy", "block-ai")
        self.assertTrue(rp.can_fetch("Googlebot", "https://e.com/"))
        self.assertTrue(rp.can_fetch("Yeti", "https://e.com/"))
        self.assertFalse(rp.can_fetch("OAI-SearchBot", "https://e.com/"))

    def test_disallow_path_applies_to_everyone(self):
        _, rp = self.robots("--disallow", "/admin/")
        for bot in ("Googlebot", "GPTBot", "SomeNewBot"):
            self.assertFalse(rp.can_fetch(bot, "https://e.com/admin/x"), bot)
            self.assertTrue(rp.can_fetch(bot, "https://e.com/blog/"), bot)

    def test_refuses_blanket_and_bad_input(self):
        for bad in (["--disallow", "/"], ["--disallow", "/*"], ["--disallow", "*"], ["--disallow", "admin/"]):
            r = run(PY, FIX / "gen-robots.py", "--sitemap", "https://e.com/s.xml", *bad)
            self.assertNotEqual(r.returncode, 0, bad)
        r = run(PY, FIX / "gen-robots.py", "--sitemap", "/sitemap.xml")
        self.assertNotEqual(r.returncode, 0)


class HtmlToLlmsFull(unittest.TestCase):
    def test_text_headings_entities_and_region(self):
        d = pathlib.Path(tempfile.mkdtemp()); src = d / "in.html"; out = d / "out.txt"
        src.write_text("<html><body><nav>skip me</nav><div id='a'><h2>Title &amp; more</h2>"
                       "<p>caf&#233; &#x2014; ok</p><script>var x=1</script><ul><li>one</li></ul></div>"
                       "<div id='b'>after</div></body></html>")
        r = run("node", FIX / "html-to-llms-full.mjs", "--in", src, "--out", out, "--title", "T", "--url", "https://e.com/",
                "--from", "<div id='a'>", "--to", "<div id='b'>")
        self.assertEqual(r.returncode, 0, r.stderr)
        t = out.read_text()
        self.assertIn("## Title & more", t)
        self.assertIn("café — ok", t)          # numeric entities decoded
        self.assertIn("- one", t)
        self.assertNotIn("var x", t); self.assertNotIn("skip me", t); self.assertNotIn("after", t)

    def test_missing_to_marker_warns(self):
        d = pathlib.Path(tempfile.mkdtemp()); src = d / "in.html"; src.write_text("<p>a</p><p>b</p>")
        r = run("node", FIX / "html-to-llms-full.mjs", "--in", src, "--out", d / "o", "--title", "T", "--url", "u",
                "--from", "<p>a", "--to", "<nope>")
        self.assertEqual(r.returncode, 0); self.assertIn("--to marker not found", r.stderr)


class GenAiFiles(unittest.TestCase):
    def test_writes_files_and_validates(self):
        d = pathlib.Path(tempfile.mkdtemp()); cfg = d / "c.json"
        cfg.write_text(json.dumps({"name": "Example", "url": "https://e.com/", "description": "A site that does one thing well.",
                                   "capabilities": ["one thing"], "faqs": [{"question": "q", "answer": "a"}]}))
        r = run("node", FIX / "gen-ai-files.mjs", "--config", cfg, "--out", d / "pub")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads((d / "pub/ai/service.json").read_text())["capabilities"], ["one thing"])
        self.assertTrue((d / "pub/.well-known/ai.txt").exists())
        cfg.write_text(json.dumps({"name": "Ex", "url": "https://e.com/", "description": "short"}))
        self.assertNotEqual(run("node", FIX / "gen-ai-files.mjs", "--config", cfg, "--out", d / "p2").returncode, 0)


class IndexNow(unittest.TestCase):
    def test_key_rules_and_dry_run_filtering(self):
        key = "abcXYZ-12345678"   # letters beyond hex are valid in the IndexNow spec
        site = Site({f"/{key}.txt": key, "/bad.txt": "other"})
        try:
            host = site.url.split("://")[1]
            r = run("node", FIX / "indexnow.mjs", "--host", host, "--key", key, "--key-location", f"{site.url}/{key}.txt",
                    "--dry-run", f"{site.url}/a", "https://elsewhere.example/b", "not a url")
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("1 URL(s)", r.stdout)
            r = run("node", FIX / "indexnow.mjs", "--host", host, "--key", key, "--key-location", f"{site.url}/bad.txt",
                    "--dry-run", f"{site.url}/a")
            self.assertEqual(r.returncode, 1)   # key file content mismatch
            r = run("node", FIX / "indexnow.mjs", "--host", host, "--key", "short", f"{site.url}/a")
            self.assertEqual(r.returncode, 2)
        finally:
            site.close()


# -------------------------------------------------------------------------------------------- verify
class JsonLdLint(unittest.TestCase):
    def tree(self, files):
        d = pathlib.Path(tempfile.mkdtemp())
        for p, body in files.items():
            (d / p).parent.mkdir(parents=True, exist_ok=True); (d / p).write_text(body)
        return d

    def lint(self, d, *a):
        return run(PY, VERIFY / "jsonld-lint.py", d, *a)

    def ld(self, obj):
        return f'<script type="application/ld+json">{json.dumps(obj)}</script>'

    def test_required_types_count_across_blocks_on_one_page(self):
        # regression: types used to be checked per block, so a page splitting WebSite and FAQPage failed
        d = self.tree({"index.html": page(head=self.ld({"@type": "WebSite"}) + self.ld({"@type": "FAQPage"}))})
        r = self.lint(d, "--require", "WebSite,FAQPage", "--strict")
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_graph_and_nested_graph_types(self):
        d = self.tree({"index.html": page(head=self.ld({"@context": "https://schema.org", "@graph": [
            {"@type": ["WebSite", "Thing"]}, {"@graph": [{"@type": "Person"}]}, "stray string"]}))})
        r = self.lint(d, "--require", "WebSite,Person", "--strict")
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_parse_error_fails_missing_only_with_strict(self):
        d = self.tree({"a/index.html": page(head='<script type="application/ld+json">{bad json</script>')})
        self.assertEqual(self.lint(d).returncode, 1)
        d = self.tree({"index.html": page(head=self.ld({"@type": "WebPage"}))})
        self.assertEqual(self.lint(d, "--require", "WebSite").returncode, 0)
        self.assertEqual(self.lint(d, "--require", "WebSite", "--strict").returncode, 1)

    def test_only_glob_limits_requirement(self):
        d = self.tree({"index.html": page(head=self.ld({"@type": "WebSite"})),
                       "about/index.html": page(head=self.ld({"@type": "AboutPage"}))})
        self.assertEqual(self.lint(d, "--require", "WebSite", "--only", "index.html", "--strict").returncode, 0)
        self.assertEqual(self.lint(d, "--require", "WebSite", "--only", "**index.html", "--strict").returncode, 1)


class DiffBuilds(unittest.TestCase):
    def test_lists_only_changed_outputs(self):
        d = pathlib.Path(tempfile.mkdtemp())
        g = lambda *a: run("git", "-C", d, *a)
        g("init", "-q"); g("config", "user.email", "t@e"); g("config", "user.name", "t")
        (d / "src").mkdir(); (d / "src/a.txt").write_text("a"); (d / "src/b.txt").write_text("b")
        (d / "build.sh").write_text("mkdir -p out && cp src/* out/\n")
        g("add", "-A"); g("commit", "-qm", "init")
        (d / "src/b.txt").write_text("B changed")
        r = run("bash", VERIFY / "diff-builds.sh", "bash build.sh", "out", "HEAD", cwd=d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("out/b.txt", r.stdout); self.assertNotIn("out/a.txt", r.stdout)
        self.assertEqual(run("git", "-C", d, "worktree", "list").stdout.count("\n"), 1)   # temp worktree removed


@unittest.skipUnless(os.environ.get("X_EO_TEST_NODE_MODULES") and os.environ.get("PLAYWRIGHT_CHROMIUM"),
                     "set X_EO_TEST_NODE_MODULES and PLAYWRIGHT_CHROMIUM to run the browser test")
class RenderDiff(unittest.TestCase):
    def test_js_only_page_is_a_problem_static_page_is_ok(self):
        site = Site({"/static.html": page(body="<main><h1>Hi</h1><p>" + "word " * 200 + "</p></main>"),
                     "/js.html": page(body="<main></main><script>document.querySelector('main').innerHTML='<h1>Hi</h1><p>'+'word '.repeat(200)+'</p>'</script>"),
                     "/blank.html": "<html><body></body></html>"})
        tmp = pathlib.Path(tempfile.mkdtemp()); shutil.copy(VERIFY / "render-diff.mjs", tmp)
        os.symlink(os.environ["X_EO_TEST_NODE_MODULES"], tmp / "node_modules")
        try:
            self.assertEqual(run("node", tmp / "render-diff.mjs", f"{site.url}/static.html").returncode, 0)
            self.assertEqual(run("node", tmp / "render-diff.mjs", f"{site.url}/js.html").returncode, 1)
            self.assertEqual(run("node", tmp / "render-diff.mjs", f"{site.url}/blank.html").returncode, 1)
        finally:
            site.close()


# --------------------------------------------------------------------------------------------- audit
def summarize_script():
    """The scoring/tier code is a heredoc inside audit.sh; extract it so it can be tested without pip."""
    src = (AUDIT / "audit.sh").read_text()
    body = re.search(r"<<'PYEOF'\n(.*?)\nPYEOF", src, re.S).group(1)
    f = pathlib.Path(tempfile.mkdtemp()) / "summarize.py"; f.write_text(body); return f


class AuditSummary(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.py = summarize_script()

    def summarize(self, data, thr=""):
        return subprocess.run([PY, "-I", str(self.py), "https://e.com/", "4.18.3", thr], input=data,
                              capture_output=True, text=True)

    def test_tiers(self):
        recs = {"Add Organization JSON-LD schema with name, url, and logo": "B",   # regression: was A via 'json-ld'
                "Add FAQPage schema with site FAQs": "B",
                "Add WebSite JSON-LD schema to homepage": "A",
                "Add a canonical tag": "A",
                "Create /llms.txt for AI indexing": "C",
                "Add RSS/Atom feed": "C",
                "Add descriptive labels to forms": "C",
                "Explain the anatomy of the page in one heading": "A",             # 'atom' inside a word is not RSS
                "Possible prompt injection in user content": "SEC",
                "Add sameAs links to Wikidata": "B"}
        out = self.summarize(json.dumps({"score": 70, "band": "good", "score_breakdown": {"llms": 10, "ai_discovery": 2},
                                         "recommendations": list(recs)})).stdout
        for rec, tier in recs.items():
            self.assertIn(f"[{tier}] {rec}", out)
        self.assertIn("excluding Tier C: 58/76", out)

    def test_threshold_and_failure_exit_codes(self):
        data = json.dumps({"score": 70, "score_breakdown": {}, "recommendations": []})
        self.assertEqual(self.summarize(data, "60").returncode, 0)
        self.assertEqual(self.summarize(data, "80").returncode, 1)
        self.assertEqual(self.summarize("not json").returncode, 3)
        self.assertEqual(self.summarize(json.dumps({"score": None})).returncode, 0)

    def test_argument_validation(self):
        self.assertEqual(run("bash", AUDIT / "audit.sh").returncode, 2)
        self.assertEqual(run("bash", AUDIT / "audit.sh", "--threshold", "high", "https://e.com/").returncode, 2)


class HostRootCheck(unittest.TestCase):
    def test_subpath_files_root_sitemap_name_and_bot_groups(self):
        site = Site({"/robots.txt": "User-agent: GPTBot\nDisallow: /\nUser-agent: Googlebot\nAllow: /\n\n"
                                    "User-agent: *\nAllow: /\nSitemap: http://127.0.0.1/custom-map.xml\n",
                     "/proj/llms.txt": "# x", "/proj/index.html": page()})
        try:
            robots = (site.dir / "robots.txt").read_text().replace("http://127.0.0.1", site.url)
            (site.dir / "robots.txt").write_text(robots); (site.dir / "custom-map.xml").write_text("<urlset/>")
            r = run("bash", AUDIT / "host-root-check.sh", f"{site.url}/proj/index.html")
            self.assertEqual(r.returncode, 0, r.stdout)
            self.assertIn("page path: /proj", r.stdout)
            self.assertIn("exists under /proj/llms.txt", r.stdout)
            self.assertIn("declared in robots.txt", r.stdout)
            self.assertRegex(r.stdout, r"Googlebot\s+-> explicit: allowed")
        finally:
            site.close()

    def test_blanket_disallow_and_missing_robots(self):
        site = Site({"/robots.txt": "User-agent: *\nDisallow: /\n", "/sitemap.xml": "<urlset/>"})
        try:
            self.assertIn("YES (blocks everything!)", run("bash", AUDIT / "host-root-check.sh", site.url + "/").stdout)
        finally:
            site.close()
        site = Site({"/index.html": page()})
        try:
            self.assertEqual(run("bash", AUDIT / "host-root-check.sh", site.url + "/").returncode, 1)
        finally:
            site.close()


class SiteSample(unittest.TestCase):
    def sample(self, files, *a):
        site = Site(files)
        try:
            for p in list(files):   # fixtures use HOST as a placeholder for the server address
                f = site.dir / p.lstrip("/"); f.write_text(f.read_text().replace("HOST", site.url))
            r = run(PY, AUDIT / "site-sample.py", site.url + "/", "--json", *a)
            return r, (json.loads(r.stdout) if r.stdout.strip().startswith("{") else None)
        finally:
            site.close()

    def base(self, **over):
        og = '<meta name="description" content="d"><meta property="og:title" content="t"><meta property="og:image" content="i">'
        files = {"/robots.txt": "User-agent: *\nAllow: /\nSitemap: HOST/sitemap.xml\n",
                 "/sitemap.xml": "<sitemapindex><sitemap><loc>HOST/pages.xml</loc></sitemap></sitemapindex>",
                 "/pages.xml": "<urlset><url><loc>HOST/a.html</loc></url><url><loc>HOST/b.html</loc></url></urlset>",
                 "/index.html": page("Home", "<h1>Home</h1>" + "x " * 900, og),
                 "/a.html": page("A", "<svg><title>icon</title></svg><h1>A</h1>" + "x " * 900, og + '<link rel="canonical" href="/a.html">'),
                 "/b.html": page("B", "<h1>B</h1>" + "x " * 900, og + '<meta name="robots" content="noindex">')}
        files.update(over); return files

    def test_svg_title_relative_canonical_noindex_and_sitemap_index(self):
        r, d = self.sample(self.base())
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(d["sitemap_urls"], 2)                                        # followed the sitemap index
        a = next(p for p in d["pages"] if p["url"].endswith("/a.html"))
        self.assertEqual(a["title"], "A")                                              # regression: <svg><title> leaked in
        msgs = " ".join(m for _, m in d["issues"])
        self.assertNotIn("canonical points to", msgs)                                  # regression: relative canonical
        self.assertIn("b.html: noindex but listed in sitemap", msgs)

    def test_redirect_stub_root(self):
        stub = '<html><head><title>S</title><link rel="canonical" href="HOST/a.html"><meta http-equiv="refresh" content="0; url=/a.html"></head><body></body></html>'
        _, d = self.sample(self.base(**{"/index.html": stub}))
        self.assertTrue(any("redirect stub missing description" in m for _, m in d["issues"]))
        full = ('<html><head><title>S</title><meta name="description" content="d"><meta property="og:title" content="t">'
                '<meta property="og:image" content="i"><link rel="canonical" href="HOST/a.html">'
                '<meta http-equiv="refresh" content="0; url=/a.html"></head><body><h1>S</h1></body></html>')
        _, d = self.sample(self.base(**{"/index.html": full}))
        self.assertFalse(any("stub" in m for _, m in d["issues"]))
        self.assertTrue(any("deliberate" in n for n in d["notes"]))

    def test_fail_on(self):
        r, _ = self.sample(self.base(), "--fail-on", "A")
        self.assertEqual(r.returncode, 1)   # the noindex page in the sitemap is a Tier A issue
        files = self.base(**{"/b.html": self.base()["/index.html"].replace("Home", "B")})
        r, _ = self.sample(files, "--fail-on", "A")
        self.assertEqual(r.returncode, 0, r.stdout)


class AiRecall(unittest.TestCase):
    def test_subpath_site_only_matches_its_own_path(self):
        m = lambda site, url: run("node", AUDIT / "ai-recall.mjs", "--site", site, "--match", url).stdout.strip()
        self.assertEqual(m("https://user.github.io/proj/", "https://user.github.io/proj/docs"), "match")
        self.assertEqual(m("https://user.github.io/proj/", "https://user.github.io/other/"), "no match")
        self.assertEqual(m("https://example.com/", "https://www.example.com/a"), "match")
        self.assertEqual(m("https://example.com/", "https://evil.com/?u=example.com"), "no match")

    def test_dry_run_warns_when_question_names_the_site(self):
        r = run("node", AUDIT / "ai-recall.mjs", "--site", "https://example.com/", "--q", "what is example.com", "--dry-run")
        self.assertEqual(r.returncode, 0); self.assertIn("names the site", r.stderr)
        self.assertEqual(run("node", AUDIT / "ai-recall.mjs", "--site", "https://example.com/").returncode, 2)


class SiteBuild(unittest.TestCase):
    def test_project_page_is_generated_from_build_py(self):
        before = {p: (R / p).read_text() for p in ("site/index.html", "site/ko/index.html", "site/sitemap.xml")}
        self.assertEqual(run(PY, R / "site/build.py").returncode, 0)
        for p, txt in before.items():
            self.assertEqual((R / p).read_text(), txt, f"{p} is stale: run python3 site/build.py")


if __name__ == "__main__":
    unittest.main()

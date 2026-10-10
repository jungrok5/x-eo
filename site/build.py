#!/usr/bin/env python3
"""Build the x-eo project page (GitHub Pages) in English and Korean from one template.

usage: python3 site/build.py      -> site/index.html, site/ko/index.html, site/sitemap.xml
Both pages share one structure so they cannot drift; only the strings in T differ.
"""
import html, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent
BASE = "https://jungrok5.github.io/x-eo/"
REPO = "https://github.com/jungrok5/x-eo"
E = html.escape

# Real output of `audit.sh` on a live site (2026-10-07), shortened to the lines discussed on the page.
TERM = """<span class="ds-c">$</span> bash audit.sh https://one-scroll-bible.com/
== https://one-scroll-bible.com/   (geo-optimizer-skill 4.18.3)
   score 90/100 (excellent)   <span class="hl">excluding Tier C: 68/76 = 89%</span>
   robots=18/18, llms=16/18, schema=16/16, meta=14/14, content=12/12,
   signals=3/6, ai_discovery=6/6, brand_entity=5/10, penalty=0
   [B] Add sameAs links in Organization schema to Wikipedia, Wikidata, ...
   [C] Add RSS/Atom feed and link it in &lt;head&gt; ...
   [C] Add potentialAction (SearchAction) to WebSite schema ...
   [SEC] This page exposes user-generated content ('respond' region) ..."""

INSTALL = "git clone --depth 1 https://github.com/jungrok5/x-eo.git\nmkdir -p ~/.claude/skills && cp -r x-eo/skills/* ~/.claude/skills/"
SCRIPTS = """S=x-eo/skills
bash    $S/x-eo-audit/scripts/audit.sh --threshold 80 https://example.com/
bash    $S/x-eo-audit/scripts/host-root-check.sh https://example.com/blog/
python3 $S/x-eo-audit/scripts/site-sample.py https://example.com/ --max 8
node    $S/x-eo-verify/scripts/render-diff.mjs https://example.com/
python3 $S/x-eo-verify/scripts/jsonld-lint.py ./dist --require WebSite --strict
python3 $S/x-eo-fix/scripts/gen-robots.py --sitemap https://example.com/sitemap.xml --out robots.txt"""

# Score movement from examples/one-scroll-bible.md (live URL, geo-optimizer-skill 4.18.3).
EXAMPLE = [("robots", 15, 18, "A"), ("llms", 10, 16, "C"), ("ai_discovery", 0, 6, "C"),
           ("schema", 7, 16, "B"), ("content", 11, 12, "A"), ("penalty", -3, 0, "A/B")]

T = {
 "en": dict(
  lang="en", path="", other="ko/", other_label="한국어", other_lang="ko",
  title="x-eo: SEO, AEO and GEO audits graded by evidence",
  desc="Claude Code skills that audit a site for search engines and AI answer engines, fix the findings and verify the fix, with an evidence tier on every recommendation.",
  theme=('data-dark="Dark mode" data-light="Light mode"', "Dark mode"),
  copy='data-copied="Copied" data-failed="Copy failed"', copy_label="Copy",
  nav_repo="GitHub", nav_install="Install",
  h1="Audit a site for search and AI answers, and know which points are real",
  lede="Four Claude Code skills measure a site, fix the source, and prove that nothing else changed. Every finding carries an evidence tier, and the score is reported with and without the points that no engine has been shown to use.",
  cta_primary="Install", cta_repo="Source on GitHub",
  term_cap="audit.sh on a live site, 2026-10-07 (lines shortened)",
  tiers_h="Evidence tiers",
  tiers_p=["AI search checkers mix three kinds of advice in one list: documented crawler behavior, plausible practice, and conventions such as <code>llms.txt</code> that no major engine has been shown to read. Google's AI optimization guide (updated 2026-07-10) says Google Search ignores AI text files and special markup.",
           "x-eo labels every finding with a tier. A score that rose only through Tier C points is reported as such."],
  tiers_head=("Tier", "Meaning", "Examples", "Treatment"),
  tiers=[("A", "Documented by the engine or directly observable", "HTTP 200, content in raw HTML, canonical, hreflang, sitemap, JSON-LD that parses and matches the page", "Fix first"),
         ("B", "Supported only by third-party or correlational studies", "Answer-shaped passages, freshness, consistent entity name and <code>sameAs</code>", "Do it when it also helps readers"),
         ("C", "Convention without demonstrated use", "<code>llms.txt</code>, <code>ai.txt</code>, <code>/ai/*.json</code>, WebMCP", "Only if free; never counted as a result"),
         ("SEC", "Security finding", "Prompt-injection surface, exposed secrets", "Confirm a real write path before reporting")],
  loop_h="Four skills, one loop",
  loop=[("x-eo-audit", "Measure the live site"), ("x-eo-fix", "Change the source, not the output"),
        ("x-eo-verify", "Build diff, JSON-LD, JavaScript on and off"), ("deploy", "Then audit the live URL again")],
  loop_back="After deploy, the loop starts again from x-eo-audit with the same tool and version.",
  shared="<code>x-eo</code> holds what the other three share: the tiers, honesty rules, report template, 13 pitfalls, a Korea guide (Naver, Daum, KakaoTalk), and 12 topic guides from claude-seo (MIT).",
  skills_head=("Skill", "Scripts"),
  skills=[("x-eo-audit", "<code>audit.sh</code> (score with and without Tier C, <code>--threshold</code> for CI), <code>host-root-check.sh</code>, <code>site-sample.py</code>, <code>ai-recall.mjs</code> (citations of your URLs by search-enabled AI APIs)"),
          ("x-eo-fix", "<code>gen-robots.py</code>, JSON-LD templates, root files for sub-path sites, <code>html-to-llms-full.mjs</code>, <code>gen-ai-files.mjs</code>, <code>indexnow.mjs</code>"),
          ("x-eo-verify", "<code>diff-builds.sh</code>, <code>jsonld-lint.py</code>, <code>render-diff.mjs</code> (Playwright), <code>local-audit.py</code>")],
  install_h="Install",
  install_p="Copy all four skills; they reference each other. There is no installer, hook or background agent.",
  steps=[("Clone and copy the skills", None, True),
         ("Ask Claude Code", "<code>Audit https://example.com with x-eo, fix the Tier A findings, and verify.</code>", False)],
  req="Requirements: <code>bash</code>, <code>git</code>, <code>python3</code> 3.10 or later. <code>render-diff.mjs</code> also needs <code>playwright-core</code> and a Chromium path in <code>PLAYWRIGHT_CHROMIUM</code>. <code>ai-recall.mjs</code> needs an Anthropic or OpenAI API key and costs one search-enabled request per question and engine.",
  direct_h="Run the scripts without an agent",
  example_h="Example: a 214-language static site, 62 to 90",
  example_p=["12 of the 28 points were Tier C. Without them the score moved from 52/76 to 68/76.",
             "The change with measurable value was prerendering the Korean root page: text visible without JavaScript rose from 11% to 53% of the rendered page, and the JavaScript-on DOM stayed byte-identical."],
  example_head=("Category", "Before", "After", "Tier"),
  example_link="Full write-up",
  limits_h="Limits",
  limits=["<code>audit.sh</code> assigns tiers with keyword rules. A label can be wrong; read the finding.",
          "Scores come from one tool and its author's weights. Compare the same tool and version before and after, not different tools.",
          "<code>ai-recall.mjs</code> takes a sample, not a rate. Answers vary between runs; Perplexity is not covered.",
          "<code>local-audit.py</code> patches geo-optimizer internals and can break on upgrade; the version is pinned.",
          "Tested on Linux. The evidence ledger and the Korea guide are dated; check them again before relying on them."],
  foot=["MIT license. Topic guides in <code>skills/x-eo/references/claude-seo/</code> come from claude-seo (MIT).",
        'Page built on the "Clear" design system from <a href="https://github.com/jungrok5/ai-design">ai-design</a>.'],
 ),
 "ko": dict(
  lang="ko", path="ko/", other="../", other_label="English", other_lang="en",
  title="x-eo: 증거 등급을 붙이는 SEO·AEO·GEO 점검",
  desc="검색엔진과 AI 답변 엔진 관점에서 사이트 점검, 수정, 수정 결과 검증을 맡는 Claude Code 스킬입니다. 모든 권고에 증거 등급을 붙입니다.",
  theme=("", "다크 모드"),
  copy="", copy_label="복사",
  nav_repo="GitHub", nav_install="설치",
  h1="검색과 AI 답변 기준의 사이트 점검, 어느 점수가 실제인지까지 구분합니다",
  lede="Claude Code 스킬 4개가 사이트 측정, 소스 수정, 다른 곳이 바뀌지 않았다는 확인을 차례로 맡습니다. 모든 항목에 증거 등급을 붙이고, 점수는 어느 엔진도 쓴다고 확인되지 않은 항목을 포함한 값과 뺀 값으로 함께 보고합니다.",
  cta_primary="설치 명령 보기", cta_repo="GitHub 소스",
  term_cap="실제 사이트에 실행한 audit.sh, 2026-10-07 (줄 일부 생략)",
  tiers_h="증거 등급",
  tiers_p=["AI 검색 점검 도구는 세 종류의 권고를 한 목록에 섞습니다. 문서로 확인되는 크롤러 동작, 그럴듯한 관행, 주요 엔진이 읽는다는 근거가 없는 <code>llms.txt</code> 같은 관례입니다. Google의 AI 최적화 안내(2026-07-10 갱신)는 Google 검색이 AI용 텍스트 파일과 특수 마크업을 무시한다고 밝힙니다.",
           "x-eo는 모든 항목에 등급을 붙입니다. Tier C 항목만으로 오른 점수는 그렇게 표시해 보고합니다."],
  tiers_head=("등급", "뜻", "예", "처리"),
  tiers=[("A", "검색엔진 문서로 확인되거나 직접 관찰 가능", "HTTP 200, 원본 HTML의 본문, canonical, hreflang, 사이트맵, 파싱되고 화면과 일치하는 JSON-LD", "먼저 수정"),
         ("B", "제3자 연구나 상관관계로만 뒷받침", "답변형 문단, 최신성, 일관된 개체 이름과 <code>sameAs</code>", "독자에게도 도움이 될 때 적용"),
         ("C", "사용 근거가 없는 관례", "<code>llms.txt</code>, <code>ai.txt</code>, <code>/ai/*.json</code>, WebMCP", "비용이 없을 때만 적용, 성과로 계산하지 않음"),
         ("SEC", "보안 항목", "프롬프트 주입 경로, 노출된 비밀값", "실제 쓰기 경로를 확인한 뒤 보고")],
  loop_h="스킬 4개와 작업 순서",
  loop=[("x-eo-audit", "실제 사이트 측정"), ("x-eo-fix", "결과물이 아닌 소스 수정"),
        ("x-eo-verify", "빌드 비교, JSON-LD, JavaScript 켬·끔 비교"), ("배포", "배포 후 실제 URL 재측정")],
  loop_back="배포 후에는 같은 도구와 버전으로 x-eo-audit부터 다시 실행합니다.",
  shared="<code>x-eo</code>에는 세 스킬이 함께 쓰는 내용이 있습니다. 증거 등급, 정직 원칙, 보고 양식, 함정 13개, 한국 가이드(네이버, 다음, 카카오톡), claude-seo(MIT)에서 가져온 주제별 가이드 12개입니다.",
  skills_head=("스킬", "스크립트"),
  skills=[("x-eo-audit", "<code>audit.sh</code>(Tier C 포함·제외 점수, CI용 <code>--threshold</code>), <code>host-root-check.sh</code>, <code>site-sample.py</code>, <code>ai-recall.mjs</code>(검색이 연결된 AI API의 내 URL 인용 집계)"),
          ("x-eo-fix", "<code>gen-robots.py</code>, JSON-LD 템플릿, 하위 경로 사이트용 루트 파일, <code>html-to-llms-full.mjs</code>, <code>gen-ai-files.mjs</code>, <code>indexnow.mjs</code>"),
          ("x-eo-verify", "<code>diff-builds.sh</code>, <code>jsonld-lint.py</code>, <code>render-diff.mjs</code>(Playwright), <code>local-audit.py</code>")],
  install_h="설치",
  install_p="네 스킬은 서로 참조하므로 모두 복사합니다. 설치 스크립트, 훅, 백그라운드 에이전트는 없습니다.",
  steps=[("레포를 받고 스킬 복사", None, True),
         ("Claude Code에 요청", "<code>x-eo로 https://example.com 을 점검하고 Tier A 항목을 고친 뒤 검증해 줘</code>", False)],
  req="<code>bash</code>, <code>git</code>, <code>python3</code> 3.10 이상이 필요합니다. <code>render-diff.mjs</code>는 <code>playwright-core</code>와 <code>PLAYWRIGHT_CHROMIUM</code>에 지정한 Chromium 경로가 추가로 필요합니다. <code>ai-recall.mjs</code>는 Anthropic 또는 OpenAI API 키가 필요하며 질문과 엔진마다 검색 요청 1회 비용이 발생합니다.",
  direct_h="에이전트 없이 스크립트 실행",
  example_h="사례: 214개 언어 정적 사이트, 62점에서 90점",
  example_p=["오른 28점 중 12점은 Tier C입니다. Tier C를 빼면 52/76에서 68/76으로 올랐습니다.",
             "효과를 측정할 수 있었던 변경은 한국어 루트 페이지의 사전 렌더링입니다. JavaScript 없이 보이는 본문이 렌더링된 화면의 11%에서 53%로 늘었고, JavaScript를 켠 화면의 DOM은 바이트 단위로 같았습니다."],
  example_head=("항목", "전", "후", "등급"),
  example_link="전체 기록",
  limits_h="한계",
  limits=["<code>audit.sh</code>는 키워드 규칙으로 등급을 매깁니다. 등급이 틀릴 수 있으므로 항목 내용을 직접 확인합니다.",
          "점수는 한 도구의 분류와 가중치를 따릅니다. 서로 다른 도구가 아니라 같은 도구, 같은 버전의 변경 전후를 비교합니다.",
          "<code>ai-recall.mjs</code>의 결과는 표본이며 비율이 아닙니다. 실행할 때마다 답이 달라지고 Perplexity는 지원하지 않습니다.",
          "<code>local-audit.py</code>는 geo-optimizer 내부를 수정하므로 업그레이드하면 동작하지 않을 수 있습니다. 그래서 버전을 고정합니다.",
          "리눅스에서만 시험했습니다. 증거 기록과 한국 가이드에는 작성 날짜가 있으므로 사용 전에 다시 확인합니다."],
  foot=["MIT 라이선스. <code>skills/x-eo/references/claude-seo/</code>의 주제별 가이드는 claude-seo(MIT)에서 가져왔습니다.",
        '이 페이지는 <a href="https://github.com/jungrok5/ai-design">ai-design</a>의 디자인 시스템 "Clear"로 만들었습니다.'],
 ),
}


def cmd(text, t):
    return f'<div class="ds-cmd"><pre><code>{E(text)}</code></pre><button type="button" {t["copy"]}>{t["copy_label"]}</button></div>'


def page(code):
    t = T[code]; url = BASE + t["path"]; pre = "../" if t["path"] else ""
    ld = {"@context": "https://schema.org", "@type": "SoftwareSourceCode", "name": "x-eo", "url": url,
          "codeRepository": REPO, "description": t["desc"], "inLanguage": t["lang"], "license": "https://opensource.org/licenses/MIT",
          "programmingLanguage": ["Python", "JavaScript", "Shell"], "runtimePlatform": "Claude Code"}
    rows = lambda head, body: ("<div class=\"ds-table-wrap\"><table class=\"ds-table\"><thead><tr>" +
        "".join(f"<th>{h}</th>" for h in head) + "</tr></thead><tbody>" + body + "</tbody></table></div>")
    tiers = "".join(f'<tr><td class="tier">{a}</td><td>{b}</td><td>{c}</td><td>{d}</td></tr>' for a, b, c, d in t["tiers"])
    skills = "".join(f"<tr><td><code>{a}</code></td><td>{b}</td></tr>" for a, b in t["skills"])
    ex = "".join(f'<tr><td><code>{n}</code></td><td class="num">{a}</td><td class="num">{b}</td><td class="tier">{tier}</td></tr>'
                 for n, a, b, tier in EXAMPLE)
    ex += f'<tr><td><strong>{"Total" if code == "en" else "합계"}</strong></td><td class="num">62</td><td class="num"><strong>90</strong></td><td></td></tr>'
    ex_head = (f"<th>{t['example_head'][0]}</th><th class=\"num\">{t['example_head'][1]}</th>"
               f"<th class=\"num\">{t['example_head'][2]}</th><th>{t['example_head'][3]}</th>")
    steps = ""
    for h, body, is_cmd in t["steps"]:
        steps += f"<li><div><h3>{h}</h3>" + (cmd(INSTALL, t) if is_cmd else f"<p>{body}</p>") + "</div></li>"
    loop = "".join(f"<li><code>{a}</code><span>{b}</span></li>" for a, b in t["loop"])
    return f"""<!doctype html>
<html lang="{t['lang']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(t['title'])}</title>
<meta name="description" content="{E(t['desc'])}">
<link rel="canonical" href="{url}">
<link rel="alternate" hreflang="en" href="{BASE}">
<link rel="alternate" hreflang="ko" href="{BASE}ko/">
<link rel="alternate" hreflang="x-default" href="{BASE}">
<meta property="og:type" content="website">
<meta property="og:title" content="{E(t['title'])}">
<meta property="og:description" content="{E(t['desc'])}">
<meta property="og:url" content="{url}">
<meta property="og:locale" content="{'en_US' if code == 'en' else 'ko_KR'}">
<meta property="og:image" content="{BASE}og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="x-eo: SEO, AEO and GEO audits graded by evidence, next to audit.sh output (score 90/100, excluding Tier C 68/76)">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{BASE}og.png">
<link rel="icon" href="data:,">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<link rel="stylesheet" href="{pre}assets/design/tokens.css">
<link rel="stylesheet" href="{pre}assets/design/components.css">
<link rel="stylesheet" href="{pre}assets/site.css">
<script src="{pre}assets/design/theme.js"></script>
</head>
<body>
<header class="ds-topbar top">
  <a class="brand" href="{pre or './'}">x-eo</a>
  <nav>
    <a href="#install">{t['nav_install']}</a>
    <a href="{REPO}">{t['nav_repo']}</a>
    <a href="{t['other']}" hreflang="{t['other_lang']}" lang="{t['other_lang']}">{t['other_label']}</a>
    <button type="button" class="theme-toggle" {t['theme'][0]}>{t['theme'][1]}</button>
  </nav>
</header>
<main class="ds-page">
<section class="hero">
  <div>
    <h1>{t['h1']}</h1>
    <p class="ds-lede">{t['lede']}</p>
    <div class="actions"><a class="ds-btn ds-btn--primary" href="#install">{t['cta_primary']}</a><a class="ds-btn" href="{REPO}">{t['cta_repo']}</a></div>
  </div>
  <figure class="term"><figcaption>{t['term_cap']}</figcaption><pre tabindex="0"><code>{TERM}</code></pre></figure>
</section>
<section id="tiers">
  <h2>{t['tiers_h']}</h2>
  {''.join(f'<p>{p}</p>' for p in t['tiers_p'])}
  {rows(t['tiers_head'], tiers)}
</section>
<section id="skills">
  <h2>{t['loop_h']}</h2>
  <figure class="ds-figure"><ol class="loop">{loop}</ol><p class="loop-back">{t['loop_back']}</p><p class="shared">{t['shared']}</p></figure>
  {rows(t['skills_head'], skills)}
</section>
<section id="install">
  <h2>{t['install_h']}</h2>
  <p>{t['install_p']}</p>
  <ol class="ds-steps">{steps}</ol>
  <p class="ds-muted">{t['req']}</p>
</section>
<section id="direct">
  <h2>{t['direct_h']}</h2>
  {cmd(SCRIPTS, t)}
</section>
<section id="example">
  <h2>{t['example_h']}</h2>
  {''.join(f'<p>{p}</p>' for p in t['example_p'])}
  <div class="ds-table-wrap"><table class="ds-table"><thead><tr>{ex_head}</tr></thead><tbody>{ex}</tbody></table></div>
  <p><a href="{REPO}/blob/main/examples/one-scroll-bible.md">{t['example_link']}</a></p>
</section>
<section id="limits">
  <h2>{t['limits_h']}</h2>
  <ul class="plain">{''.join(f'<li>{x}</li>' for x in t['limits'])}</ul>
</section>
<footer class="site">{''.join(f'<p>{x}</p>' for x in t['foot'])}</footer>
</main>
<script src="{pre}assets/design/copy.js" defer></script>
</body>
</html>
"""


def main():
    (ROOT / "index.html").write_text(page("en"))
    (ROOT / "ko").mkdir(exist_ok=True)
    (ROOT / "ko" / "index.html").write_text(page("ko"))
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"  <url><loc>{BASE}</loc></url>\n  <url><loc>{BASE}ko/</loc></url>\n</urlset>\n")
    print("wrote site/index.html, site/ko/index.html, site/sitemap.xml")


main()

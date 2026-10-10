#!/usr/bin/env python3
"""Build the x-eo project page (GitHub Pages) in English and Korean from one template.

usage: python3 site/build.py      -> site/index.html, site/ko/index.html, site/sitemap.xml
Both pages share one structure so they cannot drift; only the strings in T differ.
Order follows what a visitor needs: what it does for me, proof, how to start, why trust it, details.
"""
import html, json, pathlib, re
re_tags = re.compile(r"<[^>]+>")

ROOT = pathlib.Path(__file__).resolve().parent
BASE = "https://jungrok5.github.io/x-eo/"
REPO = "https://github.com/jungrok5/x-eo"
E = html.escape

PLUGIN = "claude plugin marketplace add jungrok5/x-eo\nclaude plugin install x-eo@x-eo"
MANUAL = "git clone --depth 1 https://github.com/jungrok5/x-eo.git\nmkdir -p ~/.claude/skills && cp -r x-eo/plugins/x-eo/skills/* ~/.claude/skills/"
SCRIPTS = """S=x-eo/plugins/x-eo/skills
bash    $S/x-eo-audit/scripts/audit.sh --threshold 80 https://example.com/
bash    $S/x-eo-audit/scripts/host-root-check.sh https://example.com/blog/
python3 $S/x-eo-audit/scripts/site-sample.py https://example.com/ --max 8 --fail-on A
node    $S/x-eo-verify/scripts/render-diff.mjs https://example.com/
python3 $S/x-eo-verify/scripts/jsonld-lint.py ./dist --require WebSite --strict
python3 $S/x-eo-fix/scripts/gen-robots.py --sitemap https://example.com/sitemap.xml --out robots.txt"""

# The report x-eo produced when it was run on this page (2026-10-10, geo-optimizer-skill 4.18.3).
# Every line is a fact from that run; see the commit "Self-audit with x-eo" in the repository.
REPORT = {
 "en": dict(ask="Audit https://jungrok5.github.io/x-eo/ with x-eo, fix it, and verify.",
            rows=[("Score", ["53 → 61 / 100", '<span class="hl">excluding Tier C: 70% → 80%</span>']),
                  ("Done", ["[A] WebSite and author JSON-LD", "[B] visible FAQ with matching FAQPage", "[B] author link (same-site links 1 → 2)"]),
                  ("Skipped", ["[B] Organization, address, phone: none exist, would be invented", "[C] llms.txt, ai.txt, /ai/*.json: no engine shown to read them"]),
                  ("Verified", ["build diff: 4 files, all intended", "JSON-LD parses · JS off shows 100% of text", "375 / 1440 px, light and dark · live re-measure"])]),
 "ko": dict(ask="x-eo로 https://jungrok5.github.io/x-eo/ 를 점검하고 고친 뒤 검증해 줘",
            rows=[("점수", ["53 → 61 / 100", '<span class="hl">Tier C 제외: 70% → 80%</span>']),
                  ("수정", ["[A] WebSite·저자 JSON-LD", "[B] 화면에 보이는 FAQ와 같은 내용의 FAQPage", "[B] 저자 링크 (같은 사이트 링크 1 → 2)"]),
                  ("제외", ["[B] Organization, 주소, 전화: 해당 조직이 없어 지어내야 함", "[C] llms.txt, ai.txt, /ai/*.json: 엔진이 읽는다는 근거 없음"]),
                  ("검증", ["빌드 비교: 바뀐 파일 4개, 모두 의도한 것", "JSON-LD 파싱 · JS 끔에서도 본문 100%", "375 / 1440 px, 라이트·다크 · 배포 후 재측정"])]),
}

T = {
 "en": """<span class="ds-c">&gt; Audit https://jungrok5.github.io/x-eo/ with x-eo, fix it, and verify.</span>

Score     53 → 61 / 100     <span class="hl">excluding Tier C: 70% → 80%</span>

Done      [A] WebSite and author JSON-LD
          [B] visible FAQ with matching FAQPage markup
          [B] author link (same-site links: 1 → 2)
Skipped   [B] Organization, address, phone: no such entity, would be invented
          [C] llms.txt, ai.txt, /ai/*.json: no engine shown to read them
Verified  build diff: 4 files, all intended
          JSON-LD parses · JS off shows 100% of the text
          375 / 1440 px, light and dark · live URL re-measured""",
 "ko": """<span class="ds-c">&gt; x-eo로 https://jungrok5.github.io/x-eo/ 를 점검하고 고친 뒤 검증해 줘</span>

점수      53 → 61 / 100     <span class="hl">Tier C 제외: 70% → 80%</span>

수정      [A] WebSite·저자 JSON-LD
          [B] 화면에 보이는 FAQ와 같은 내용의 FAQPage
          [B] 저자 링크 (같은 사이트 링크 1 → 2)
제외      [B] Organization, 주소, 전화: 해당 조직 없음, 지어내야 함
          [C] llms.txt, ai.txt, /ai/*.json: 엔진이 읽는다는 근거 없음
검증      빌드 비교: 바뀐 파일 4개, 모두 의도한 것
          JSON-LD 파싱 · JS 끔에서도 본문 100%
          375 / 1440 px, 라이트·다크 · 배포 후 실제 URL 재측정""",
}

T = {
 "en": dict(
  lang="en", path="", other="ko/", other_label="한국어", other_lang="ko",
  title="x-eo: fix a site for search and AI answers, and prove nothing broke",
  desc="Claude Code plugin for SEO, AEO and GEO. It audits a site, fixes the source in your repository, and verifies the build, with an evidence tier on every recommendation.",
  theme=('data-dark="Dark mode" data-light="Light mode"', "Dark mode"),
  copy='data-copied="Copied" data-failed="Copy failed"', copy_label="Copy",
  nav_start="Install", nav_repo="GitHub",
  h1="Fix your site for search and AI answers, and prove nothing else broke",
  lede="Audit tools give you a score and a to-do list. x-eo is a Claude Code plugin that works through the list in your repository, then checks the build before you deploy. Each recommendation says how strong the evidence behind it is, so you do not spend time on points no search engine uses.",
  who="For Claude Code users whose site source is in a repository. Auditing alone needs only a URL. SEO is classic search, AEO and GEO are answers in ChatGPT, Claude, Perplexity and Google AI Overviews.",
  cta="Install the plugin", cta_repo="Source on GitHub",
  report_cap="x-eo run on this page, 2026-10-10",
  get_h="What you get that an audit tool does not give",
  get_head=("", "Typical audit tool", "x-eo"),
  get=[("Output", "Score and a list of recommendations", "The same score, plus each item labeled A, B or C by evidence"),
       ("Who changes the site", "You", "Claude Code, in your repository's source (the generator, not the built files)"),
       ("After the change", "Run the audit again", "Build diff, JSON-LD parse, JavaScript on and off, then a live re-measure"),
       ("Points for llms.txt and similar files", "Counted like any other", "Reported separately as Tier C; Google says it ignores them")],
  case_h="Example: a 214-language site, 62 to 90",
  case_p=["x-eo was run on <a href=\"https://one-scroll-bible.com/\">one-scroll-bible.com</a>. The score rose by 28 points; 12 of them were Tier C. Without those, it moved from 68% to 89%.",
          "The change that mattered most did not show up in the score as much: the Korean home page had no text without JavaScript. After x-eo added a prerender step, a crawler that does not run JavaScript sees 53% of the page instead of 11%, and the page in a browser stayed byte-identical."],
  case_link="Full write-up with every category",
  start_h="Start in two steps",
  start=[("Install the plugin", "plugin"),
         ("Ask Claude Code", "ask")],
  asks=["Audit https://example.com with x-eo. Do not change anything yet.",
        "Fix the Tier A findings with x-eo-fix, then verify with x-eo-verify.",
        "We deployed. Re-measure the live URL with the same tool and version."],
  asks_p="Typical requests:",
  manual="Without the plugin system, copy the skills directly:",
  req="Needs <code>bash</code>, <code>git</code> and <code>python3</code> 3.10+. The render check also needs <code>playwright-core</code> and Chromium. Citation sampling needs an Anthropic or OpenAI API key; everything else runs without keys.",
  tiers_h="Why the recommendations can be trusted",
  tiers_p="Google's AI optimization guide (updated 2026-07-10) says Google Search ignores AI text files and special markup. Audit tools still score them. x-eo labels every finding by the evidence behind it and never counts Tier C as a result.",
  tiers=[("A", "Documented or directly observable", "The page loads, its text is in the HTML without JavaScript, canonical and hreflang are right, the sitemap is valid, JSON-LD parses and matches the page.", "Fix first."),
         ("B", "Supported only by third-party studies", "Answer-shaped paragraphs, freshness, a consistent entity name with <code>sameAs</code>, original data.", "Do it when it also helps readers."),
         ("C", "Convention without demonstrated use", "<code>llms.txt</code>, <code>ai.txt</code>, <code>/ai/*.json</code>, WebMCP.", "Only if free. Never counted as a result."),
         ("SEC", "Security", "A place where third-party text reaches crawlers, an exposed secret.", "Confirm a real write path before reporting.")],
  faq_h="Questions",
  faq=[("Does x-eo change my site on its own?", "No. The skills act only when you ask Claude Code. <code>x-eo-fix</code> edits the source in your repository, and nothing goes live until you deploy. There is no hook or background agent."),
       ("Do I need an API key?", "Only for <code>ai-recall.mjs</code>, which needs an Anthropic or OpenAI key and costs one search-enabled request per question and engine. The audit, fix and verify scripts run without keys."),
       ("Will a higher score bring more visitors?", "Not necessarily. The score follows one tool's weights, and Google says it ignores AI text files. That is why x-eo reports the score with and without Tier C points, and why citation by AI engines is only sampled."),
       ("Does it work without Claude Code?", "The scripts run on their own (see the developer section below), but choosing and applying fixes is the part Claude Code does.")],
  limits_h="Limits",
  limits=["Tier labels come from keyword rules. A label can be wrong; read the finding.",
          "Scores come from one tool and its author's weights. Compare the same tool and version before and after.",
          "Citation sampling is a sample, not a rate. Answers vary between runs; Perplexity is not covered.",
          "Tested on Linux. The evidence ledger and the Korea guide are dated; check them again before relying on them."],
  dev_h="For developers: what is inside",
  dev_sum="Four skills, the scripts, and how to run them without an agent",
  loop=[("x-eo-audit", "Measure the live site"), ("x-eo-fix", "Change the source, not the output"),
        ("x-eo-verify", "Build diff, JSON-LD, JavaScript on and off"), ("deploy", "Then audit the live URL again")],
  shared="<code>x-eo</code> holds what the other three share: the tiers, honesty rules, report template, 13 pitfalls, a Korea guide (Naver, Daum, KakaoTalk), and 12 topic guides from claude-seo (MIT).",
  skills_head=("Skill", "Scripts"),
  skills=[("x-eo-audit", "<code>audit.sh</code> (score with and without Tier C, <code>--threshold</code> for CI), <code>host-root-check.sh</code>, <code>site-sample.py</code>, <code>ai-recall.mjs</code>"),
          ("x-eo-fix", "<code>gen-robots.py</code>, JSON-LD templates, root files for sub-path sites, <code>html-to-llms-full.mjs</code>, <code>gen-ai-files.mjs</code>, <code>indexnow.mjs</code>"),
          ("x-eo-verify", "<code>diff-builds.sh</code>, <code>jsonld-lint.py</code>, <code>render-diff.mjs</code>, <code>local-audit.py</code>")],
  direct="Run the scripts directly:",
  tests="26 behaviour tests run in CI against a local fixture server.",
  foot=["MIT license. Topic guides in <code>plugins/x-eo/skills/x-eo/references/claude-seo/</code> come from claude-seo (MIT).",
        'Page built on the "Clear" design system from <a href="https://github.com/jungrok5/ai-design">ai-design</a>.'],
  author='Made by <a href="https://jungrok5.github.io/resume/">Jeongrok Oh</a>.',
 ),
 "ko": dict(
  lang="ko", path="ko/", other="../", other_label="English", other_lang="en",
  title="x-eo: 검색과 AI 답변에 맞게 사이트를 고치고 검증하는 Claude Code 플러그인",
  desc="SEO, AEO, GEO용 Claude Code 플러그인입니다. 사이트 점검, 레포 소스 수정, 빌드 검증을 맡고 모든 권고에 증거 등급을 붙입니다.",
  theme=("", "다크 모드"),
  copy="", copy_label="복사",
  nav_start="설치", nav_repo="GitHub",
  h1="검색과 AI 답변에 맞게 사이트를 고치고, 다른 곳이 깨지지 않았음을 확인합니다",
  lede="점검 도구는 점수와 할 일 목록을 줍니다. x-eo는 그 목록을 레포에서 직접 처리하고 배포 전에 빌드를 검증하는 Claude Code 플러그인입니다. 권고마다 근거의 강도를 표시하므로 어느 검색엔진도 쓰지 않는 항목에 시간을 쓰지 않습니다.",
  who="대상: 사이트 소스를 레포로 관리하는 Claude Code 사용자. 점검만 할 때는 URL만 있으면 됩니다. SEO는 일반 검색, AEO와 GEO는 ChatGPT·Claude·Perplexity·Google AI 개요의 답변 노출을 뜻합니다.",
  cta="플러그인 설치", cta_repo="GitHub 소스",
  report_cap="이 페이지에 실행한 x-eo 결과, 2026-10-10",
  get_h="점검 도구와 다른 점",
  get_head=("", "일반 점검 도구", "x-eo"),
  get=[("결과", "점수와 권고 목록", "같은 점수와 함께, 항목마다 근거에 따른 A·B·C 등급"),
       ("사이트를 고치는 주체", "사용자", "Claude Code가 레포의 소스(빌드 결과물이 아닌 생성기)를 수정"),
       ("수정 후", "점검을 다시 실행", "빌드 비교, JSON-LD 파싱, JavaScript 켬·끔 비교, 배포 후 실제 URL 재측정"),
       ("llms.txt 같은 파일의 점수", "다른 항목과 똑같이 계산", "Tier C로 따로 보고. Google은 무시한다고 밝힘")],
  case_h="사례: 214개 언어 사이트, 62점에서 90점",
  case_p=["<a href=\"https://one-scroll-bible.com/\">one-scroll-bible.com</a>에 x-eo를 실행했습니다. 점수는 28점 올랐고 그중 12점은 Tier C입니다. Tier C를 빼면 68%에서 89%로 올랐습니다.",
          "가장 중요한 변경은 점수에 크게 드러나지 않았습니다. 한국어 첫 페이지는 JavaScript 없이는 본문이 없었습니다. x-eo가 사전 렌더링을 추가한 뒤 JavaScript를 실행하지 않는 크롤러가 보는 본문이 11%에서 53%로 늘었고, 브라우저 화면은 바이트 단위로 같았습니다."],
  case_link="항목별 전체 기록",
  start_h="두 단계로 시작",
  start=[("플러그인 설치", "plugin"),
         ("Claude Code에 요청", "ask")],
  asks=["x-eo로 https://example.com 을 점검해 줘. 아직 고치지는 마.",
        "x-eo-fix로 Tier A 항목을 고치고 x-eo-verify로 검증해 줘.",
        "배포했어. 같은 도구와 버전으로 실제 URL을 다시 측정해 줘."],
  asks_p="요청 예:",
  manual="플러그인 기능을 쓰지 않으려면 스킬을 직접 복사합니다.",
  req="<code>bash</code>, <code>git</code>, <code>python3</code> 3.10 이상이 필요합니다. 렌더 비교에는 <code>playwright-core</code>와 Chromium이 추가로 필요합니다. 인용 표본 검사만 Anthropic 또는 OpenAI API 키가 필요하고 나머지는 키 없이 실행됩니다.",
  tiers_h="권고를 믿을 수 있는 이유",
  tiers_p="Google의 AI 최적화 안내(2026-07-10 갱신)는 Google 검색이 AI용 텍스트 파일과 특수 마크업을 무시한다고 밝힙니다. 점검 도구는 이런 항목에도 점수를 줍니다. x-eo는 모든 항목에 근거에 따른 등급을 붙이고 Tier C는 성과로 계산하지 않습니다.",
  tiers=[("A", "문서로 확인되거나 직접 관찰 가능", "페이지가 열리고, JavaScript 없이도 HTML에 본문이 있고, canonical과 hreflang이 맞고, 사이트맵이 유효하고, JSON-LD가 파싱되며 화면과 일치합니다.", "먼저 수정합니다."),
         ("B", "제3자 연구로만 뒷받침", "답변형 문단, 최신성, <code>sameAs</code>를 포함한 일관된 개체 이름, 자체 데이터.", "독자에게도 도움이 될 때 적용합니다."),
         ("C", "사용 근거가 없는 관례", "<code>llms.txt</code>, <code>ai.txt</code>, <code>/ai/*.json</code>, WebMCP.", "비용이 없을 때만 적용하고 성과로 계산하지 않습니다."),
         ("SEC", "보안", "제3자가 쓴 글이 크롤러에 노출되는 경로, 노출된 비밀값.", "실제 쓰기 경로를 확인한 뒤 보고합니다.")],
  faq_h="자주 묻는 질문",
  faq=[("x-eo가 사이트를 스스로 바꿉니까?", "아닙니다. 스킬은 Claude Code에 요청할 때만 동작합니다. <code>x-eo-fix</code>는 레포의 소스만 수정합니다. 배포하기 전에는 실제 사이트에 반영되지 않습니다. 훅이나 백그라운드 에이전트는 없습니다."),
       ("API 키가 필요합니까?", "<code>ai-recall.mjs</code>에만 필요합니다. Anthropic 또는 OpenAI 키가 필요하고 질문과 엔진마다 검색 요청 1회 비용이 발생합니다. 점검, 수정, 검증 스크립트는 키 없이 실행됩니다."),
       ("점수가 오르면 방문자가 늘어납니까?", "반드시 그렇지는 않습니다. 점수는 한 도구의 가중치를 따릅니다. Google은 AI용 텍스트 파일을 무시한다고 밝혔습니다. 그래서 x-eo는 점수를 Tier C 포함·제외로 함께 보고합니다. AI 엔진의 인용은 표본으로만 확인합니다."),
       ("Claude Code 없이도 쓸 수 있습니까?", "스크립트는 단독으로 실행됩니다(아래 개발자용 항목 참고). 다만 어떤 항목을 어떻게 고칠지 정하고 적용하는 부분은 Claude Code가 맡습니다.")],
  limits_h="한계",
  limits=["등급은 키워드 규칙으로 매깁니다. 틀릴 수 있으므로 항목 내용을 직접 확인합니다.",
          "점수는 한 도구의 분류와 가중치를 따릅니다. 같은 도구, 같은 버전의 변경 전후를 비교합니다.",
          "인용 검사는 표본이며 비율이 아닙니다. 실행할 때마다 답이 달라지고 Perplexity는 지원하지 않습니다.",
          "리눅스에서만 시험했습니다. 증거 기록과 한국 가이드에는 작성 날짜가 있으므로 사용 전에 다시 확인합니다."],
  dev_h="개발자용: 구성",
  dev_sum="스킬 4개, 스크립트, 에이전트 없이 실행하는 방법",
  loop=[("x-eo-audit", "실제 사이트 측정"), ("x-eo-fix", "결과물이 아닌 소스 수정"),
        ("x-eo-verify", "빌드 비교, JSON-LD, JavaScript 켬·끔 비교"), ("배포", "배포 후 실제 URL 재측정")],
  shared="<code>x-eo</code>에는 세 스킬이 함께 쓰는 내용이 있습니다. 증거 등급, 정직 원칙, 보고 양식, 함정 13개, 한국 가이드(네이버, 다음, 카카오톡), claude-seo(MIT)에서 가져온 주제별 가이드 12개입니다.",
  skills_head=("스킬", "스크립트"),
  skills=[("x-eo-audit", "<code>audit.sh</code>(Tier C 포함·제외 점수, CI용 <code>--threshold</code>), <code>host-root-check.sh</code>, <code>site-sample.py</code>, <code>ai-recall.mjs</code>"),
          ("x-eo-fix", "<code>gen-robots.py</code>, JSON-LD 템플릿, 하위 경로 사이트용 루트 파일, <code>html-to-llms-full.mjs</code>, <code>gen-ai-files.mjs</code>, <code>indexnow.mjs</code>"),
          ("x-eo-verify", "<code>diff-builds.sh</code>, <code>jsonld-lint.py</code>, <code>render-diff.mjs</code>, <code>local-audit.py</code>")],
  direct="스크립트 직접 실행:",
  tests="동작 테스트 26개가 로컬 테스트 서버로 CI에서 실행됩니다.",
  foot=["MIT 라이선스. <code>plugins/x-eo/skills/x-eo/references/claude-seo/</code>의 주제별 가이드는 claude-seo(MIT)에서 가져왔습니다.",
        '이 페이지는 <a href="https://github.com/jungrok5/ai-design">ai-design</a>의 디자인 시스템 "Clear"로 만들었습니다.'],
  author='만든 사람: <a href="https://jungrok5.github.io/resume/">오정록</a>',
 ),
}


def cmd(text, t):
    return f'<div class="ds-cmd"><pre><code>{E(text)}</code></pre><button type="button" {t["copy"]}>{t["copy_label"]}</button></div>'


NAME = re.compile(r"(?<![\\w/.@-])x-eo(?![\\w/@-])")
def nowrap_name(body):
    """Wrap bare 'x-eo' in text nodes (not inside tags) so it never splits as 'x-' / 'eo'."""
    return re.sub(r">([^<]+)<", lambda m: ">" + NAME.sub('<span class="nw">x-eo</span>', m.group(1)) + "<", body)


def page(code):
    t = T[code]; url = BASE + t["path"]; pre = "../" if t["path"] else ""
    person = {"@type": "Person", "@id": "https://jungrok5.github.io/resume/#person", "name": "오정록 (Jeongrok Oh)",
              "url": "https://jungrok5.github.io/resume/",
              "sameAs": ["https://github.com/jungrok5", "https://www.linkedin.com/in/jungrok5"]}
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "WebSite", "@id": BASE + "#website", "name": "x-eo", "url": BASE, "inLanguage": ["en", "ko"], "author": {"@id": person["@id"]}},
        {"@type": "SoftwareSourceCode", "name": "x-eo", "url": url, "codeRepository": REPO, "description": t["desc"],
         "inLanguage": t["lang"], "license": "https://opensource.org/licenses/MIT", "programmingLanguage": ["Python", "JavaScript", "Shell"],
         "runtimePlatform": "Claude Code", "author": {"@id": person["@id"]}, "isPartOf": {"@id": BASE + "#website"}},
        {"@type": "FAQPage", "inLanguage": t["lang"], "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": html.unescape(re_tags.sub("", a))}} for q, a in t["faq"]]},
        person]}
    table = lambda head, body: ("<div class=\"ds-table-wrap\"><table class=\"ds-table\"><thead><tr>" +
        "".join(f"<th>{h}</th>" for h in head) + "</tr></thead><tbody>" + body + "</tbody></table></div>")
    get = "".join(f"<tr><th scope=\"row\">{a}</th><td>{b}</td><td>{c}</td></tr>" for a, b, c in t["get"])
    skills = "".join(f"<tr><td><code>{a}</code></td><td>{b}</td></tr>" for a, b in t["skills"])
    tiers = "".join(f'<div class="tier-row"><dt><span class="tier">{k}</span>{name}</dt><dd>{ex}<br><strong>{todo}</strong></dd></div>'
                    for k, name, ex, todo in t["tiers"])
    asks = "".join(cmd(a, t) for a in t["asks"])
    steps = (f"<li><div><h3>{t['start'][0][0]}</h3>{cmd(PLUGIN, t)}</div></li>"
             f"<li><div><h3>{t['start'][1][0]}</h3><p>{t['asks_p']}</p><div class=\"asks\">{asks}</div></div></li>")
    loop = "".join(f"<li><code>{a}</code><span>{b}</span></li>" for a, b in t["loop"])
    out = f"""<!doctype html>
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
    <a href="#start">{t['nav_start']}</a>
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
    <p class="who">{t['who']}</p>
    <div class="actions"><a class="ds-btn ds-btn--primary" href="#start">{t['cta']}</a><a class="ds-btn" href="{REPO}">{t['cta_repo']}</a></div>
  </div>
  <figure class="term report"><figcaption>{t['report_cap']}</figcaption>
    <p class="ask">&gt; {E(REPORT[code]['ask'])}</p>
    <dl>{''.join(f"<div><dt>{k}</dt><dd>{'<br>'.join(v)}</dd></div>" for k, v in REPORT[code]['rows'])}</dl>
  </figure>
</section>
<section id="get">
  <h2>{t['get_h']}</h2>
  {table(t['get_head'], get)}
</section>
<section id="case">
  <h2>{t['case_h']}</h2>
  {''.join(f'<p>{p}</p>' for p in t['case_p'])}
  <p><a href="{REPO}/blob/main/examples/one-scroll-bible.md">{t['case_link']}</a></p>
</section>
<section id="start">
  <h2>{t['start_h']}</h2>
  <ol class="ds-steps">{steps}</ol>
  <p class="ds-muted">{t['manual']}</p>
  {cmd(MANUAL, t)}
  <p class="ds-muted">{t['req']}</p>
</section>
<section id="tiers">
  <h2>{t['tiers_h']}</h2>
  <p>{t['tiers_p']}</p>
  <dl class="tiers">{tiers}</dl>
</section>
<section id="faq">
  <h2>{t['faq_h']}</h2>
  <div class="faq">{''.join(f'<h3>{q}</h3><p>{a}</p>' for q, a in t['faq'])}</div>
</section>
<section id="limits">
  <h2>{t['limits_h']}</h2>
  <ul class="plain">{''.join(f'<li>{x}</li>' for x in t['limits'])}</ul>
</section>
<section id="dev">
  <h2>{t['dev_h']}</h2>
  <details class="dev"><summary>{t['dev_sum']}</summary>
    <figure class="ds-figure"><ol class="loop">{loop}</ol><p class="shared">{t['shared']}</p></figure>
    {table(t['skills_head'], skills)}
    <p>{t['direct']}</p>
    {cmd(SCRIPTS, t)}
    <p class="ds-muted">{t['tests']}</p>
  </details>
</section>
<footer class="site">{''.join(f'<p>{x}</p>' for x in t['foot'] + [t['author']])}</footer>
</main>
<script src="{pre}assets/design/copy.js" defer></script>
</body>
</html>
"""
    a, b = out.index("<main"), out.index("</main>")
    return out[:a] + nowrap_name(out[a:b]) + out[b:]


def main():
    (ROOT / "index.html").write_text(page("en"))
    (ROOT / "ko").mkdir(exist_ok=True)
    (ROOT / "ko" / "index.html").write_text(page("ko"))
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"  <url><loc>{BASE}</loc></url>\n  <url><loc>{BASE}ko/</loc></url>\n</urlset>\n")
    print("wrote site/index.html, site/ko/index.html, site/sitemap.xml")


main()

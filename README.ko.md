# x-eo

**SEO / AEO / GEO 점검을 하되, 모든 권고에 “증거 등급”을 붙이는 에이전트 스킬.** ([English](README.md))

AI 검색 준비도 도구 대부분은 0~100점과 할 일 목록을 줍니다. 그 목록에는 문서로 확인되는 것
(크롤러가 페이지를 읽을 수 있나), 그럴듯한 것, 그리고 의례에 가까운 것(`llms.txt`, `ai.txt`)이
섞여 있고, 마지막 부류는 가장 큰 검색엔진이 "무시한다"고 밝힌 것들입니다. `x-eo`는 에이전트가 이
셋을 구분하게 해서, **점수를 올리되 그 점수가 무엇을 뜻하는지 스스로 속지 않게** 합니다.

## 구성 — 스킬 4개, 하나의 루프
`x-eo-audit`(측정) → `x-eo-fix`(수정) → `x-eo-verify`(검증) → 배포 → `x-eo-audit`(실서비스 재측정). `x-eo`는 진입점·공통 규칙·지식.
- `x-eo` — 증거 등급 A(문서화)·B(그럴듯함)·C(관례), 정직 원칙, 보고 양식, 주제별 지도. `references/`에 증거 장부·함정 10개·도구 리뷰와 `korea.md`(네이버 서치어드바이저·Yeti/Daumoa·카카오톡 OG·IndexNow)와 **claude-seo(MIT)에서 가져온 주제 가이드 12개**(기술·온페이지·콘텐츠/E-E-A-T·스키마·GEO·에이전트·사이트맵·이미지·hreflang·로컬·이커머스·기획)
- `x-eo-audit` — `audit.sh`(geo-optimizer-skill, 버전 고정 임시 venv, **Tier C 제외 점수** 병기), `host-root-check.sh`(robots/llms/sitemap은 **호스트 루트에서만** 읽힘), `site-sample.py`(사이트맵에서 N페이지 표본: 제목·설명·canonical·H1·OG·JSON-LD·얇은 페이지·중복·리다이렉트 스텁 루트), `ai-recall.mjs`(브랜드 없는 질문을 검색 연동 AI에 묻고 **내 URL 인용** 여부 집계, API 키 필요)
- `x-eo-fix` — `gen-robots.py`, JSON-LD 템플릿, 하위경로→루트 스캐폴드, `html-to-llms-full.mjs`, `gen-ai-files.mjs`(Tier C), `indexnow.mjs`
- `x-eo-verify` — `diff-builds.sh`(전/후 빌드 비교), `jsonld-lint.py`, `render-diff.mjs`(JS 켬/끔), `local-audit.py`(로컬 서버)

## 설치
```bash
git clone --depth 1 https://github.com/jungrok5/x-eo.git
mkdir -p ~/.claude/skills && cp -r x-eo/skills/* ~/.claude/skills/
```
4개를 모두 설치하세요(서로 참조). 설치 스크립트·훅·전역 에이전트 없음. 스크립트가 짧으니 먼저 읽어 보세요.

## 이 스킬의 한계 (자기 검토)
등급 분류는 키워드 휴리스틱이라 틀릴 수 있고, 점수 기준은 외부 도구 작성자의 것이며, 실제 AI 인용
여부는 표본으로만 확인합니다(비율 측정 아님). `local-audit.py`는 도구 내부에 의존해 업그레이드 시 깨질 수 있고, 리눅스에서만
시험했습니다. 근거 문서는 날짜가 있으니 사용 전에 다시 확인하세요.

claude-seo 가이드는 MIT 출처 표기와 함께 포함됩니다(`skills/x-eo/references/claude-seo/NOTICE.md`).

MIT 라이선스.

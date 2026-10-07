# x-eo

**SEO / AEO / GEO 점검을 하되, 모든 권고에 “증거 등급”을 붙이는 에이전트 스킬.** ([English](README.md))

AI 검색 준비도 도구 대부분은 0~100점과 할 일 목록을 줍니다. 그 목록에는 문서로 확인되는 것
(크롤러가 페이지를 읽을 수 있나), 그럴듯한 것, 그리고 의례에 가까운 것(`llms.txt`, `ai.txt`)이
섞여 있고, 마지막 부류는 가장 큰 검색엔진이 "무시한다"고 밝힌 것들입니다. `x-eo`는 에이전트가 이
셋을 구분하게 해서, **점수를 올리되 그 점수가 무엇을 뜻하는지 스스로 속지 않게** 합니다.

## 구성
- `skills/x-eo/SKILL.md` — 워크플로, 증거 등급 A(문서화) · B(그럴듯함) · C(관례), 정직 원칙, 보고 양식
- `scripts/audit.sh` — geo-optimizer-skill(MIT)을 버전 고정 임시 venv로 실행, **Tier C 점수를 뺀 점수**도 함께 출력
- `scripts/host-root-check.sh` — `robots.txt`·`llms.txt`·`/.well-known/*`는 **호스트 루트에서만** 읽힘. 하위 경로 사이트(GitHub Pages 프로젝트 사이트)에서 조용히 무효가 되는 문제를 잡음
- `scripts/render-diff.mjs` — JS를 켠 화면과 끈 화면 비교(내용이 JS 이후에만 생기는 페이지 탐지)
- `scripts/jsonld-lint.py` — 빌드 산출물의 모든 JSON-LD 파싱 검사
- `scripts/local-audit.py` — 내 로컬 서버 테스트 전용(명시적 환경변수, 루프백만)

## 설치
```bash
git clone --depth 1 https://github.com/jungrok5/x-eo.git
cp -r x-eo/skills/x-eo ~/.claude/skills/
```
설치 스크립트·훅·전역 에이전트가 없습니다. 스크립트가 짧으니 먼저 읽어 보세요.

## 이 스킬의 한계 (자기 검토)
등급 분류는 키워드 휴리스틱이라 틀릴 수 있고, 점수 기준은 외부 도구 작성자의 것이며, 실제 AI 인용
여부는 측정하지 않습니다. `local-audit.py`는 도구 내부에 의존해 업그레이드 시 깨질 수 있고, 리눅스에서만
시험했습니다. 근거 문서는 날짜가 있으니 사용 전에 다시 확인하세요.

MIT 라이선스.

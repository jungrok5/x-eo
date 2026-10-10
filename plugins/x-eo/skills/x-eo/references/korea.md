# Korea-specific signals (Naver · Daum/Kakao · KakaoTalk previews)

Google is not the only engine a Korean audience uses. These are the parts that differ; everything else in
the skill applies unchanged. Dated 2026-10 — re-verify before relying on them.

## Naver
- **Naver Search Advisor** (searchadvisor.naver.com) is Naver's Search Console. Register the site, verify
  ownership with `<meta name="naver-site-verification" content="…">` or an HTML file, then submit the
  sitemap and (if any) RSS, and use "웹 페이지 수집 요청" for new URLs. Registration is separate from
  Google; nothing carries over. **Tier A** for Korean visibility: without it Naver may crawl late or partially.
- Crawler user-agent: **`Yeti`**. Allow it explicitly in robots.txt (gen-robots.py does).
- **IndexNow**: Naver accepts IndexNow pings (announced 2023-07; listed on indexnow.org). `x-eo-fix/scripts/indexnow.mjs`
  covers it; Google does not take IndexNow.
- Naver mixes its own properties (blog, cafe, knowledge-iN, news) with "웹문서" (web documents). A plain website
  competes mainly in 웹문서 and in the integrated page's web section; ranking factors there are not published.
  Treat anything specific about "Naver SEO" as **Tier B** unless Naver's own help pages say it.

## Daum / Kakao
- Daum's crawler: **`Daumoa`**. Allow explicitly.
- **KakaoTalk link previews** read Open Graph: `og:title`, `og:description`, `og:image` (1200×630 works).
  Kakao caches previews; after changing OG, clear the cache at developers.kakao.com/tool/clear/og.
  Missing OG = a bare link in the most used messenger in Korea — a real UX loss, not just a checker point (**Tier A** for sharing).

## Korean text lengths
- Search snippets show fewer CJK characters than Latin. Rules of thumb (not standards): title ≈ 25–30 Korean
  characters before truncation on mobile; meta description ≈ 70–90. Long is not penalised, just cut.

## Where ChatGPT's web answers come from
- OpenAI has stated that ChatGPT search draws on Bing's index (plus `OAI-SearchBot` crawling). Being indexed
  in **Bing Webmaster Tools** (it can import from Google Search Console) therefore matters for ChatGPT citations — **Tier B**.

## Checklist (Korean site or Korean audience)
1. Search Advisor registered, sitemap submitted, verification meta present.
2. robots.txt lists `Yeti` and `Daumoa` (explicit Allow).
3. OG title/description/image on every shareable page; Kakao cache cleared after changes.
4. Bing Webmaster Tools registered (GSC import) for ChatGPT.
5. IndexNow key file live; ping on publish.

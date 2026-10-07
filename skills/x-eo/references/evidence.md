# Evidence ledger

What each claim rests on, and whether it was verified. Re-check dates before relying on anything here.

## Verified against the source (2026-10)

| Claim | Source | Notes |
|---|---|---|
| Google Search ignores `llms.txt`/AI text files/special markup; structured data is not required for generative AI features, though still useful for rich-result eligibility | Google Search Central, *AI optimization guide* (page shows "last updated 2026-07-10") | Quoted: "You don't need to create new machine readable files, AI text files, markup, or Markdown to appear in Google Search"; such files "will neither harm nor help … as Google Search ignores them." |
| Anthropic runs three crawlers with different purposes: **ClaudeBot** (training), **Claude-User** (user-directed fetch), **Claude-SearchBot** (search result quality); all honour robots.txt | Anthropic Help Center, *Does Anthropic crawl data from the web…* | Blocking one does not block the others. |
| `GEO` paper: "up to 40%" source-visibility gain on GEO-BENCH from content tactics (statistics, quotations, citations …) | arXiv 2311.09735 (Aggarwal et al., 2023); repo `GEO-optim/GEO`, Apache-2.0 | A **research benchmark of rewriting tactics**, not a site audit tool. "Up to", not average. |

## Reported by others, not independently verified

- OpenAI separates **OAI-SearchBot** (search) from **GPTBot** (training) and **ChatGPT-User** (user-initiated). OpenAI's bots page returned HTTP 403 to the fetcher during research — read it yourself before advising.
- llms.txt adoption data (SE Ranking 300k-domain study; OtterlyAI server-log audit; statements by Google staff) — quoted in claude-seo's `references/llmstxt-evidence.md`; primary sources not re-fetched.
- Industry statistics (Ahrefs brand-mention correlation, SE Ranking citation-position/freshness studies, Profound citation-source mix) — vendor studies, **correlational**, with commercial interest. Treat as Tier B at best.
- Tool lists from LLM chat assistants (e.g. Elmo, OneGlance) — existence and claims not verified here.

## Heuristics that are not rules

- "130–170 word answer passages", "first 30% of page", "content under 3 months old" — heuristics from third-party studies, not search-engine requirements.

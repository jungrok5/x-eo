# Tool landscape (reviewed 2026-10)

| Tool | License / size | What it is | Verdict |
|---|---|---|---|
| **geo-optimizer-skill** (Auriti-Labs) | MIT · ~1k★ · v4.18 | CLI/Python/MCP audit, 0–100 across 8 categories (robots, llms.txt, JSON-LD, meta, content, signals, AI-discovery, brand/entity) + RAG-chunk and trust heuristics | **Default measuring tool** — no API key for `audit`, JSON/HTML/SARIF output, CI threshold. Its categories mix Tier A and Tier C; this skill re-weights. Its URL guard blocks local targets. |
| **claude-seo** (AgriciDaniel) | MIT · plugin, v2.4 | 26 sub-skills / 19 agents; Playwright rendering; strong SSRF module (`url_safety.py`: decimal/hex/octal IPs, metadata endpoints, DNS pinning) | **Best-engineered, most evidence-honest** (gives `llms.txt` zero weight, separates search vs training crawlers, labels unverified stats). **Heavy**: 5 agents on Opus, global installs into `~/.claude/{skills,agents}` (overwrites same names), always-on PostToolUse schema hook, extensions installed unconditionally, README promotes a paid community and shows an unattributed "real results" screenshot, uninstall offers `curl \| bash` despite warning against it. Overkill for one page; useful for agencies. |
| **usegeoaeo** (`npx geoaeo`) | MIT · new | audit + generators (llms.txt, JSON-LD, sitemaps), MCP | Useful generators; young project. |
| **geo-audit** (g-shevchenko) | MIT · tiny | 7 modules, P0–P3 action plan | Action-plan format worth copying. |
| **ultimate-seo-geo** (mykpono) | MIT · ~86★ | 50+ Python scripts + AGENTS.md; claims "100% pass rate" on its own evals | Unvetted claims; not tested here. |
| **GEO-optim/GEO** | Apache-2.0 · ~340★ | Paper reference code + GEO-BENCH | Research tool for content tactics, not an auditor. |
| Elmo, OneGlance | MIT (per chat assistant) | Self-hosted AI-answer monitoring | Different job (tracking mentions over time); needs LLM keys. Not verified. |

Scores from different tools are **not comparable**. Compare before/after of the *same* tool and version.

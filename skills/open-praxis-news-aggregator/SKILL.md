---
name: open-praxis-news-aggregator
description: >
  Comprehensive news aggregator that fetches, filters, and deeply analyzes real-time content
  from 28 sources including Hacker News, GitHub, Hugging Face Papers, AI Newsletters,
  WallStreetCN, Weibo, and Podcasts. Use when user requests "daily scans", "tech news",
  "finance updates", "AI briefings", "deep analysis", "今日新闻", "每日简报",
  "tech roundup", or "帮我看看今天有什么新闻".
---

# News Aggregator

Fetch real-time hot news from 28 sources, generate deep analysis reports in Chinese.

## Universal Workflow (3 Steps)

Every news request follows the same workflow:

### Step 1: Fetch Data

Use the best available access backend to gather news from the requested sources. For each source, fetch the front page / trending / hot list.

Access priority:

1. **WebSearch / WebFetch** for normal webpages and search queries.
2. **Agent-Reach** for hard-to-fetch pages, platform output, audio/video transcription, or when the user explicitly asks to use Agent-Reach.
3. **Browser automation** when interaction, login state, or visual inspection is required.
4. **User-provided raw content** when external access is unavailable.

Agent-Reach is an access-layer helper only. This skill still owns source selection, filtering, synthesis, and final report quality.

```
# Example source URLs to fetch:
Hacker News:     https://news.ycombinator.com/
GitHub Trending:  https://github.com/trending
Product Hunt:    https://www.producthunt.com/
36Kr:            https://36kr.com/hot-list/catalog
华尔街见闻:       https://wallstreetcn.com/
微博热搜:         https://weibo.com/hot/search
V2EX:            https://www.v2ex.com/?tab=hot
HF Papers:       https://huggingface.co/papers
```

With keyword filter, auto-expand common terms:
- "AI" → AI, LLM, GPT, Claude, Agent, RAG, DeepSeek
- "crypto" → crypto, Bitcoin, Ethereum, Web3, DeFi

For audio/video sources, prefer:

```bash
agent-reach transcribe <url-or-local-file> -o transcript.md
```

Then summarize the transcript using the unified report template.

### Step 2: Generate Report

Format every item using the Unified Report Template below. Translate all content to **Simplified Chinese**.

### Step 3: Save & Present

Save report to `reports/YYYY-MM-DD/<source>_report.md`, then display to user.

## Unified Report Template

```markdown
#### N. [标题 (中文翻译)](https://original-url.com)
- **Source**: 源名 | **Time**: 时间 | **Heat**: 🔥 热度值
- **Links**: [Discussion](url) | [GitHub](url)     ← only if available
- **Summary**: 一句话中文摘要。
- **Deep Dive**: 💡 **Insight**: 深度分析（背景、影响、技术价值）。
```

## GitHub Candidate Output

When a report discovers GitHub projects that may be worth long-term monitoring, add a `GitHub Watch Candidates` section.

Use this table in Markdown:

```markdown
## GitHub Watch Candidates

| repo | url | stars | language | reason | suggested_action |
|---|---|---:|---|---|---|
| owner/name | https://github.com/owner/name | 1234 | TypeScript | why this matters | ignore/star/fork/watch |
```

Use these `suggested_action` values:

- `ignore`: interesting but not relevant now.
- `star`: remember it, no monitoring needed.
- `fork`: fork for possible future use.
- `watch`: add to `github-project-watchtower` if already forked or strategically important.

Do not directly edit `github-project-watchtower/repos.yaml` from this skill unless the user explicitly asks. Produce candidates first.

### Source-Specific Adaptations

| Source | Adaptation |
|--------|-----------|
| **Hacker News** | MUST include `[Discussion](hn_url)` link |
| **GitHub** | Use `🌟 Stars` for Heat, add `Lang` field, add `#Tags` in Deep Dive |
| **Hugging Face** | Use `🔥 +N` upvotes for Heat, include `[GitHub](url)` if present |
| **Weibo** | Preserve exact heat text (e.g. "108万") |

## Available Sources (28)

| Category | Key | Name |
|----------|-----|------|
| **Global News** | `hackernews` | Hacker News |
| | `36kr` | 36氪 |
| | `wallstreetcn` | 华尔街见闻 |
| | `tencent` | 腾讯新闻 |
| | `weibo` | 微博热搜 |
| | `v2ex` | V2EX |
| | `producthunt` | Product Hunt |
| | `github` | GitHub Trending |
| **AI/Tech** | `huggingface` | HF Daily Papers |
| | `ai_newsletters` | All AI Newsletters (aggregate) |
| | `bensbites` | Ben's Bites |
| | `interconnects` | Interconnects (Nathan Lambert) |
| | `oneusefulthing` | One Useful Thing (Ethan Mollick) |
| | `chinai` | ChinAI (Jeffrey Ding) |
| | `memia` | Memia |
| | `aitoroi` | AI to ROI |
| | `kdnuggets` | KDnuggets |
| **Podcasts** | `lexfridman` | Lex Fridman |
| | `80000hours` | 80,000 Hours |
| | `latentspace` | Latent Space |
| **Essays** | `paulgraham` | Paul Graham |
| | `waitbutwhy` | Wait But Why |
| | `jamesclear` | James Clear |
| | `farnamstreet` | Farnam Street |
| | `scottyoung` | Scott Young |
| | `dankoe` | Dan Koe |

## Pre-configured Profiles (Daily Briefings)

| Profile | Sources | Best For |
|---------|---------|----------|
| `general` | HN, 36Kr, GitHub, Weibo, PH, WallStreetCN | Morning overview |
| `finance` | WallStreetCN, 36Kr, Tencent | Financial markets |
| `tech` | GitHub, HN, Product Hunt | Developer trends |
| `social` | Weibo, V2EX, Tencent | Social buzz |
| `ai_daily` | HF Papers, AI Newsletters | AI research & industry |
| `reading_list` | Essays, Podcasts | Long-form content |

## Rules (Strict)

1. **Language**: ALL output in **Simplified Chinese**. Keep well-known English proper nouns (ChatGPT, Python, etc.)
2. **Time**: MANDATORY field. Never skip. If missing, mark as "Unknown Time"
3. **Anti-Hallucination**: Only use data actually fetched. Never invent news items. Use simple SVO sentences
4. **Smart Keyword Expansion**: "AI" auto-expands to "AI,LLM,GPT,Claude,Agent,RAG,DeepSeek"
5. **Smart Fill**: If results < 5 items, supplement with high-value items from wider range, marked with ⚠️
6. **Save**: Always save report to `reports/YYYY-MM-DD/` before displaying

## Usage Examples

**User**: "帮我看看今天 AI 方面有什么新闻"
→ Fetch: HF Papers + AI Newsletters + HN (keyword: AI)
→ Generate: Chinese report with deep analysis
→ Save: `reports/2026-05-17/ai_daily_report.md`

**User**: "每日简报"
→ Use `general` profile
→ Fetch: HN + 36Kr + GitHub + Weibo + PH + WallStreetCN
→ Generate: Comprehensive morning briefing

**User**: "GitHub 今天什么项目火了"
→ Fetch: GitHub Trending
→ Generate: Chinese report with stars, language, tags

## Credits

Based on [cclank/news-aggregator-skill](https://github.com/cclank/news-aggregator-skill).

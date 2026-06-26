# SpaceRaid Runtime Agents

| Agent | File | Sponsor | Role |
|-------|------|---------|------|
| Orchestrator | `backend/graph.py` | — | LangGraph state machine |
| Auditor | `agents/auditor.py` | Google Gemini | Vision audit: 8 scores + flaws |
| Planner | `agents/planner.py` | Gemini | Flaws → Tavily search queries |
| Scout | `agents/scout.py` | Tavily | Live web search |
| Extractor | `agents/extractor.py` | Tavily | Page extract + price/capacity parse |
| Groundkeeper | `agents/groundkeeper.py` | Senso | Verify claims vs ground-truth KB |
| Skeptic | `agents/skeptic.py` | — | Re-plan if <2 viable candidates |
| Ranker | `agents/ranker.py` | Prometheux | Explainable ranking |
| Clerk | `agents/clerk_ree.py` | Gensyn REE | Cryptographic receipt |
| Actor | `agents/actor.py` | Twilio | Buy manifest or venue enquiry |
| Narrator | `agents/narrator.py` | ElevenLabs | Voice summary |
| Reporter | `agents/reporter.py` | — | Final UI payload |
| Logger | `tools/clickhouse_logger.py` | ClickHouse | Event stream sidecar |

Cursor IDE rules in `.cursor/rules/` mirror this roster for development.

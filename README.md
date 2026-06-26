# SpaceRaid

**Audit your space. Raid the web. Prove every pick.**

Multi-agent hackathon project for tokens& Hacks London. Upload a room or venue photo → autonomous agents audit, search the live web, verify facts, rank options, and take real-world action.

## Quick start

```bash
# Backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add GEMINI_API_KEY, TAVILY_API_KEY, SENSO_API_KEY
chmod +x run_backend.sh && ./run_backend.sh

# Frontend (new terminal)
cd frontend && npm install && npm run dev
```

Open http://localhost:5173

## Architecture

```
Auditor (Gemini) → Planner → Scout (Tavily) → Extractor (Tavily)
  → Groundkeeper (Senso) → Skeptic ⟲ replan
  → Ranker (Prometheux) → Clerk (Gensyn REE) → Actor (Twilio) → Narrator (ElevenLabs) → Reporter
```

All agent events stream to ClickHouse (or in-memory fallback) and the React UI.

## Sponsor integrations

| Sponsor | Integration |
|---------|-------------|
| **Tavily** | Scout `/search` + Extractor `/extract` on live listings |
| **Senso** | Groundkeeper verifies price/capacity vs `knowledge/` KB |
| **Google Gemini** | Vision audit + planner + ranker fallback |
| **Cursor** | `.cursor/rules/`, `AGENTS.md`, `CURSOR.md` — IDE rules mirror runtime agents |
| **ClickHouse** | `agent_events` logger + Raid Dashboard |
| **Gensyn REE** | Clerk cryptographic receipt on final shortlist |
| **Prometheux** | Ranker explainable provenance (Gemini fallback) |
| **Twilio** | Venue enquiry SMS (mailto fallback) |
| **ElevenLabs** | Voice summary (browser TTS fallback) |
| **Tessl** | Event sponsor — acknowledged |

## Built with Cursor

This project was scaffolded using Cursor Agent with project rules in `.cursor/rules/` that mirror the runtime multi-agent roster in `AGENTS.md`. See `CURSOR.md` for the build log.

## Demo

See [DEMO_SCRIPT.md](DEMO_SCRIPT.md) for the 3-minute presentation script.

## License

MIT

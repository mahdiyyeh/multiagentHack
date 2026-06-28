# Atelier

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
| **Gensyn REE** | Clerk cryptographic receipt on final shortlist (see [Gensyn setup](#gensyn-ree)) |
| **Prometheux** | Ranker explainable ontology via `prometheux-chain` SDK (Gemini fallback) |

## Prometheux (Ranker)

1. Sign up at https://platform.prometheux.ai/login (unlimited credits at the hackathon)
2. Copy your **API token** from account settings
3. Note your **org** and **username** from the platform URL: `.../jarvispy/<org>/<username>`
4. Add to `.env`:

```bash
PMTX_TOKEN=your_token
PROMETHEUX_ORG=your_org
PROMETHEUX_USERNAME=your_username
```

5. Bootstrap the ranking ontology:

```bash
source .venv/bin/activate
python scripts/setup_prometheux.py
./run_backend.sh   # restart backend
```

6. **Start compute** in Prometheux: **Manage → Compute** → start a machine (required before concepts can run).

The Ranker agent runs Vadalog rules for budget fit, Senso grounding, and confidence — with provenance on each card.
| **Twilio** | Venue enquiry SMS (mailto fallback) |
| **ElevenLabs** | Voice summary (browser TTS fallback) |
| **Tessl** | Event sponsor — acknowledged |

## Gensyn REE

There is **no public cloud API key** for Gensyn REE. Receipts come from one of:

1. **Hackathon sponsor desk** — ask Gensyn for `GENSYN_REE_API_URL` + `GENSYN_REE_API_KEY` if they provide a hosted endpoint
2. **Local REE** (Docker required) — run `./scripts/setup_gensyn_ree.sh`, install [Docker Desktop](https://docs.docker.com/get-docker/), optionally set `GENSYN_REE_USE_LOCAL=1`
3. **Deterministic fallback** (default) — SHA256 receipt saved to `receipts/<job_id>.json`, verifiable with `python scripts/verify_receipt.py receipts/<job_id>.json`

Docs: https://docs.gensyn.ai/tech/ree/get-started

## Built with Cursor

This project was scaffolded using Cursor Agent with project rules in `.cursor/rules/` that mirror the runtime multi-agent roster in `AGENTS.md`. See `CURSOR.md` for the build log.

## Demo

See [DEMO_SCRIPT.md](DEMO_SCRIPT.md) for the 3-minute presentation script.

## License

MIT

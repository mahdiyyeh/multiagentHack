import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

PROMPTS_DIR = BASE_DIR / "backend" / "prompts"
KNOWLEDGE_DIR = BASE_DIR / "knowledge"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_MODEL_FALLBACKS = [
    m.strip()
    for m in os.getenv(
        "GEMINI_MODEL_FALLBACKS",
        "gemini-3.1-flash-lite-preview,gemini-3-flash-preview,gemini-2.5-pro",
    ).split(",")
    if m.strip()
]

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")
SENSO_API_KEY = os.getenv("SENSO_API_KEY", "")
SENSO_API_URL = os.getenv("SENSO_API_URL", "https://api.senso.ai/v1")
SENSO_KB_ID = os.getenv("SENSO_KB_ID", "")

CLICKHOUSE_HOST = os.getenv("CLICKHOUSE_HOST", "")
CLICKHOUSE_USER = os.getenv("CLICKHOUSE_USER", "default")
CLICKHOUSE_PASSWORD = os.getenv("CLICKHOUSE_PASSWORD", "")
CLICKHOUSE_DATABASE = os.getenv("CLICKHOUSE_DATABASE", "spaceraid")

GENSYN_REE_API_KEY = os.getenv("GENSYN_REE_API_KEY", "")
# Optional hosted REE endpoint (no public default — ask Gensyn at the hackathon if provided)
GENSYN_REE_API_URL = os.getenv("GENSYN_REE_API_URL", "")
# Local REE repo path (clone https://github.com/gensyn-ai/ree); requires Docker
GENSYN_REE_LOCAL_REPO = os.getenv("GENSYN_REE_LOCAL_REPO", "")
GENSYN_REE_USE_LOCAL = os.getenv("GENSYN_REE_USE_LOCAL", "").lower() in {"1", "true", "yes"}
GENSYN_REE_MODEL = os.getenv("GENSYN_REE_MODEL", "Qwen/Qwen3-0.6B")
PROMETHEUX_API_KEY = os.getenv("PROMETHEUX_API_KEY", "")
PROMETHEUX_API_URL = os.getenv("PROMETHEUX_API_URL", "")
PROMETHEUX_ONTOLOGY_ID = os.getenv("PROMETHEUX_ONTOLOGY_ID", "")

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER", "")
TWILIO_TO_NUMBER = os.getenv("TWILIO_TO_NUMBER", "")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
ENQUIRY_TO_EMAIL = os.getenv("ENQUIRY_TO_EMAIL", "")

MAX_FLAWS = 3
MAX_REPLANS = 2
MAX_TAVILY_CALLS = 15

HOME_DOMAINS = ["ikea.com", "amazon.co.uk", "wayfair.co.uk", "johnlewis.com", "argos.co.uk"]
VENUE_DOMAINS = ["tagvenue.com", "venuescanner.com", "hirespace.com", "headbox.com"]

SCORE_DIMENSIONS = [
    "spatial_openness",
    "natural_light",
    "color_harmony",
    "biophilia",
    "ergonomics",
    "acoustic_comfort",
    "zoning",
    "venue_readiness",
]

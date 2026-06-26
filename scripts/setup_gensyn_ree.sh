#!/usr/bin/env bash
# Set up Gensyn REE for SpaceRaid Clerk receipts.
set -euo pipefail
cd "$(dirname "$0")/.."

REE_DIR="${GENSYN_REE_LOCAL_REPO:-$(pwd)/vendor/gensyn-ree}"

echo "==> SpaceRaid Gensyn REE setup"
echo

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is not installed."
  echo "Install Docker Desktop: https://docs.docker.com/get-docker/"
  echo "REE runs inference inside a container — there is no public cloud REE API key portal."
  echo
fi

if [ ! -d "$REE_DIR/.git" ]; then
  echo "==> Cloning gensyn-ai/ree into $REE_DIR"
  mkdir -p "$(dirname "$REE_DIR")"
  git clone https://github.com/gensyn-ai/ree.git "$REE_DIR"
else
  echo "==> REE repo already present at $REE_DIR"
fi

ENV_FILE=".env"
touch "$ENV_FILE"
upsert_env() {
  local key="$1" val="$2"
  if grep -q "^${key}=" "$ENV_FILE"; then
    sed -i.bak "s|^${key}=.*|${key}=${val}|" "$ENV_FILE" && rm -f "${ENV_FILE}.bak"
  else
    printf '\n%s=%s\n' "$key" "$val" >> "$ENV_FILE"
  fi
}

upsert_env "GENSYN_REE_LOCAL_REPO" "$REE_DIR"
upsert_env "GENSYN_REE_MODEL" "Qwen/Qwen3-0.6B"

echo
echo "==> Wrote GENSYN_REE_LOCAL_REPO to .env"
echo
echo "Next steps:"
echo "  1. Install Docker Desktop and start it"
echo "  2. Optional — enable slow local REE receipts during raids:"
echo "       GENSYN_REE_USE_LOCAL=1"
echo "  3. Or ask the Gensyn sponsor desk at the hackathon for a hosted REE URL + key:"
echo "       GENSYN_REE_API_URL=<url-they-provide>"
echo "       GENSYN_REE_API_KEY=<key-they-provide>"
echo "  4. Restart backend: ./run_backend.sh"
echo
echo "Without Docker or a sponsor URL, SpaceRaid still issues deterministic SHA256 receipts"
echo "(saved under receipts/<job_id>.json) — valid for demo, verifiable locally."
echo
echo "Docs: https://docs.gensyn.ai/tech/ree/get-started"

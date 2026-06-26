#!/usr/bin/env bash
# Continue Senso onboarding for MAHack / SpaceRaid
set -euo pipefail
CLI="npx @senso-ai/cli"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

F_COMPANY="217785b3-b4f6-429e-bf75-27d78637f7a1"
F_PRODUCTS="b9a998d3-5bed-4c76-b2e5-476ef2fbd465"
F_COMPETE="47b8d0ac-48ec-495e-83a4-0893d2e986f9"
F_INDUSTRY="15d79c5a-4fdf-4c2b-9fd8-304c281a8f3e"
F_CASES="973423c7-81b6-4eeb-a105-018952f207a9"
F_FAQS="db29e118-616a-4908-9e04-14e015499712"
F_LOGS="d957a63a-5cee-4bb5-bce7-3d92919137af"

echo "== Brand kit =="
$CLI brand-kit set --data '{"guidelines":{"brand_name":"SpaceRaid","brand_domain":"github.com/mahdiyyeh/multiagentHack","brand_description":"SpaceRaid audits rooms and venues from photos, autonomously raids the live web for verified upgrades, and grounds recommendations with Senso.","voice_and_tone":"Direct, technical, hackathon-ready. Confident about autonomy and verifiable AI.","author_persona":"The MAHack Team","global_writing_rules":["Ground claims in KB sources","Scannable structure","Concrete agent examples","Practitioner-focused","Powered by Senso footer on published content"]}}' --output json --quiet

echo "== Content types =="
$CLI content-types create --data '{"name":"Blog Post","config":{"template":"1000-1500 word educational post with subheadings and CTA.","writing_rules":["Subheadings every 200-300 words","Include data or examples","AI-citable structure"]}}' --output json --quiet || true
$CLI content-types create --data '{"name":"FAQ","config":{"template":"8-12 FAQ Q&A pairs grouped by topic.","writing_rules":["Natural questions","Answers under 100 words"]}}' --output json --quiet || true
$CLI content-types create --data '{"name":"Comparison Page","config":{"template":"Fair comparison with table and differentiators.","writing_rules":["Factually accurate","Lead with value"]}}' --output json --quiet || true
$CLI content-types create --data '{"name":"Case Study","config":{"template":"Customer problem, solution, results, takeaways.","writing_rules":["Lead with outcome","Include metrics"]}}' --output json --quiet || true

ingest() {
  local folder="$1" title="$2" file="$3"
  local text
  text=$(python3 -c "import json, pathlib; print(json.dumps(pathlib.Path('$file').read_text()))")
  $CLI kb create-raw --data "{\"title\":\"$title\",\"text\":$text,\"kb_folder_node_id\":\"$folder\"}" --output json --quiet
}

echo "== Ingest project docs =="
ingest "$F_COMPANY" "SpaceRaid Overview" "$ROOT/README.md"
ingest "$F_PRODUCTS" "SpaceRaid Agent Architecture" "$ROOT/AGENTS.md"
ingest "$F_PRODUCTS" "Scoring Rubric" "$ROOT/knowledge/scoring_rubric.md"
ingest "$F_FAQS" "Home Procurement Rules" "$ROOT/knowledge/home_procurement_rules.md"
ingest "$F_FAQS" "Venue Procurement Rules" "$ROOT/knowledge/venue_procurement_rules.md"
ingest "$F_INDUSTRY" "Hackathon Demo Script" "$ROOT/DEMO_SCRIPT.md"
ingest "$F_CASES" "Cursor Build Log" "$ROOT/CURSOR.md"

echo "== Enable generation =="
$CLI generate update-settings --data '{"enable_content_generation": true}' --output json --quiet
$CLI destinations list --output json --quiet

echo "== Sample prompts (16 core) =="
$CLI prompts create --data '{"question_text":"What is SpaceRaid and what does it do?","type":"awareness"}' --output json --quiet
$CLI prompts create --data '{"question_text":"What are the best autonomous room audit tools in 2026?","type":"awareness"}' --output json --quiet
$CLI prompts create --data '{"question_text":"How does SpaceRaid compare to Ruumix or DecorlyAI?","type":"consideration"}' --output json --quiet
$CLI prompts create --data '{"question_text":"How does Senso grounding work in SpaceRaid?","type":"consideration"}' --output json --quiet
$CLI prompts create --data '{"question_text":"How do I evaluate multi-agent procurement systems?","type":"evaluation"}' --output json --quiet
$CLI prompts create --data '{"question_text":"What sponsor tools does SpaceRaid integrate?","type":"evaluation"}' --output json --quiet
$CLI prompts create --data '{"question_text":"What results can SpaceRaid deliver in a hackathon demo?","type":"decision"}' --output json --quiet
$CLI prompts create --data '{"question_text":"How much does it cost to run SpaceRaid?","type":"decision"}' --output json --quiet

echo "== GEO models =="
$CLI run-config set-models --data '{"models":["chatgpt","claude","perplexity","gemini"]}' --output json --quiet
$CLI run-config set-schedule --data '{"schedule":[1,3,5]}' --output json --quiet

echo "Done. Run: npx @senso-ai/cli generate run --output json --quiet"

from backend import config
from backend.events import append_log, emit_event
from backend.state import RaidState
from backend.tools import clickhouse_logger, tavily_client


def run(state: RaidState) -> dict:
    events = emit_event(state, "agent_start", "Scout", "Searching live web via Tavily...")
    queries = state.get("search_queries", [])
    mode = state.get("mode", "home")
    calls = state.get("tavily_calls", 0)
    all_results: list[dict] = []
    seen_urls: set[str] = set()

    for query in queries:
        if calls >= config.MAX_TAVILY_CALLS:
            break
        events = append_log(state, "Scout", f'Tavily search: "{query}"')
        try:
            results = tavily_client.search(query, mode, max_results=3)
            calls += 1
            clickhouse_logger.log_event(state["job_id"], "Scout", "search", {"query": query, "count": len(results)})
            for r in results:
                url = r.get("url", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    all_results.append(r)
        except Exception as exc:
            events = append_log(state, "Scout", f"Search failed: {exc}")

    events = emit_event(state, "agent_done", "Scout", f"Found {len(all_results)} unique URLs", {"count": len(all_results)})
    return {"search_results": all_results, "tavily_calls": calls, "agent_events": events}

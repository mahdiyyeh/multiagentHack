import React from "react";

const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

export type AgentEvent = {
  type: string;
  agent: string;
  message: string;
  data?: Record<string, unknown>;
  ts?: string;
};

export type RaidReport = {
  scores: Record<string, number>;
  flaws: Array<Record<string, unknown>>;
  ranked: Array<Record<string, unknown>>;
  manifest: Record<string, unknown>;
  total_gbp: number;
  replan_count: number;
  ranking_explanation: string;
  receipt_id: string;
  receipt_type: string;
  twilio_sent: boolean;
  mailto_link: string;
  audio_b64: string;
  audio_fallback_text: string;
  mode: string;
  agent_trace: AgentEvent[];
};

export function useRaidStream() {
  const [status, setStatus] = React.useState<"idle" | "running" | "complete" | "error">("idle");
  const [events, setEvents] = React.useState<AgentEvent[]>([]);
  const [report, setReport] = React.useState<RaidReport | null>(null);
  const [dashboard, setDashboard] = React.useState({ total_searches: 0, total_extracts: 0, total_grounded: 0, total_events: 0 });
  const [error, setError] = React.useState<string | null>(null);
  const [previewUrls, setPreviewUrls] = React.useState<string[]>([]);

  const startRaid = async (files: File[], mode: string, budget: number, brief: string) => {
    setStatus("running");
    setEvents([]);
    setReport(null);
    setError(null);
    setPreviewUrls(files.map((f) => URL.createObjectURL(f)));

    const form = new FormData();
    files.forEach((file) => form.append("images", file));
    form.append("mode", mode);
    form.append("budget", String(budget));
    form.append("brief", brief);

    const res = await fetch(`${API}/api/raid`, { method: "POST", body: form });
    if (!res.ok) throw new Error(await res.text());
    const { job_id } = await res.json();

    const poll = setInterval(async () => {
      try {
        const d = await fetch(`${API}/api/dashboard/${job_id}`).then((r) => r.json());
        setDashboard(d);
      } catch { /* ignore */ }
    }, 2000);

    const es = new EventSource(`${API}/api/raid/stream/${job_id}`);
    es.onmessage = (msg) => {
      const data = JSON.parse(msg.data);
      if (data.type === "complete") {
        setReport(data.report);
        setStatus("complete");
        es.close();
        clearInterval(poll);
      } else if (data.type === "error") {
        setError(data.message);
        setStatus("error");
        es.close();
        clearInterval(poll);
      } else {
        setEvents((prev) => [...prev, data]);
      }
    };
    es.onerror = () => {
      fetch(`${API}/api/raid/status/${job_id}`)
        .then((r) => r.json())
        .then((s) => {
          if (s.status === "complete" && s.report) {
            setReport(s.report);
            setStatus("complete");
          }
        })
        .finally(() => {
          es.close();
          clearInterval(poll);
        });
    };
  };

  return { status, events, report, dashboard, error, previewUrls, startRaid };
}

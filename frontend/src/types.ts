export type View = "blueprint" | "common-room" | "about" | "home-room" | "coming-soon";

export type Flaw = {
  zone_id?: number;
  bbox_pct?: number[];
  severity?: "high" | "medium" | "low";
  search_intent?: string;
  pro?: string;
  con?: string;
  flaw?: string;
};

export type Candidate = {
  url?: string;
  title?: string;
  price_gbp?: number | null;
  capacity?: number | null;
  rank?: number;
  why?: string;
  provenance?: string[];
  grounded?: boolean;
  flaw_id?: number;
};

export type ScoreEvidence = {
  because?: string;
  improvement?: string;
};

export type Callout = {
  id: string;
  x: number;
  y: number;
  label: string;
  detail: string;
  price?: number;
  side: "left" | "right";
};

export function labelDim(key: string) {
  return key.replace(/_/g, " ");
}

export function avgScore(scores: Record<string, number>) {
  const vals = Object.values(scores);
  if (!vals.length) return 0;
  return vals.reduce((a, b) => a + b, 0) / vals.length;
}

export function projectedScores(
  scores: Record<string, number>,
  evidence: Record<string, ScoreEvidence> = {},
): Record<string, number> {
  const out: Record<string, number> = {};
  for (const [k, v] of Object.entries(scores)) {
    const imp = evidence[k]?.improvement?.trim();
    const boost = imp ? 2 : 1;
    out[k] = Math.min(10, Math.round(v + boost));
  }
  return out;
}

export function flawCallouts(flaws: Flaw[], ranked: Candidate[]): Callout[] {
  return flaws.map((f, i) => {
    const bbox = f.bbox_pct;
    const x = bbox && bbox.length >= 2 ? (bbox[0] + (bbox[2] ?? 0) / 2) * 100 : 20 + i * 25;
    const y = bbox && bbox.length >= 2 ? (bbox[1] + (bbox[3] ?? 0) / 2) * 100 : 30 + i * 20;
    const match = ranked.find((c) => c.flaw_id === f.zone_id) ?? ranked[i];
    return {
      id: `flaw-${i}`,
      x: Math.min(85, Math.max(15, x)),
      y: Math.min(85, Math.max(15, y)),
      label: f.flaw || f.search_intent || `Zone ${i + 1}`,
      detail: f.con || f.search_intent || "Identified improvement opportunity",
      price: match?.price_gbp ?? undefined,
      side: x < 50 ? "left" : "right",
    };
  });
}

export function solutionCallouts(flaws: Flaw[], ranked: Candidate[]): Callout[] {
  return flaws.map((f, i) => {
    const bbox = f.bbox_pct;
    const x = bbox && bbox.length >= 2 ? (bbox[0] + (bbox[2] ?? 0) / 2) * 100 : 25 + i * 22;
    const y = bbox && bbox.length >= 2 ? (bbox[1] + (bbox[3] ?? 0) / 2) * 100 : 35 + i * 18;
    const match = ranked.find((c) => c.flaw_id === f.zone_id) ?? ranked[i];
    const what = match?.title || f.search_intent || "Curated piece";
    const why = match?.why || f.pro || "Elevates proportion, light, and material harmony.";
    const how = match?.url
      ? `Source verified listing — place at marked zone to resolve: ${f.flaw || "layout gap"}.`
      : `Position within the highlighted zone; pair with existing palette for cohesion.`;
    return {
      id: `sol-${i}`,
      x: Math.min(85, Math.max(15, x)),
      y: Math.min(85, Math.max(15, y)),
      label: what,
      detail: `${why} ${how}`,
      price: match?.price_gbp ?? undefined,
      side: x < 50 ? "left" : "right",
    };
  });
}

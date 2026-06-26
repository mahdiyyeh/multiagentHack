import type { Flaw, ScoreEvidence } from "../types";
import { avgScore, labelDim } from "../types";

type Props = {
  scores: Record<string, number>;
  scoreEvidence?: Record<string, ScoreEvidence>;
  flaws: Flaw[];
  variant: "before" | "after";
  whyBetter?: string;
};

function shortNote(text: string, max = 72): string {
  const t = text.trim();
  if (t.length <= max) return t;
  const cut = t.slice(0, max);
  const space = cut.lastIndexOf(" ");
  return `${space > 40 ? cut.slice(0, space) : cut}…`;
}

export function AuditPanel({ scores, scoreEvidence = {}, flaws, variant, whyBetter }: Props) {
  const entries = Object.entries(scores);
  const average = avgScore(scores);
  const isAfter = variant === "after";

  if (!entries.length) return null;

  return (
    <section className={`audit-panel ${variant}`}>
      <div className="audit-panel__header">
        <div>
          <p className="eyebrow">{isAfter ? "Projected rating" : "Audit"}</p>
          <h3 className="section-title section-title--sm">
            {isAfter ? "Why this vision works" : "Pro / Con"}
          </h3>
        </div>
        <div className="audit-score-badge">
          <span className="audit-score-badge__value">{average.toFixed(1)}</span>
          <span className="audit-score-badge__of">/10</span>
        </div>
      </div>

      {isAfter && whyBetter && (
        <p className="why-better why-better--lead">{whyBetter}</p>
      )}

      <ul className="audit-bars">
        {entries.map(([k, v]) => {
          const evidence = scoreEvidence[k];
          const because = evidence?.because?.trim();
          const improvement = evidence?.improvement?.trim();
          const pro = isAfter ? (improvement || because) : because;
          const con = isAfter ? undefined : improvement;
          return (
            <li key={k} className="audit-bar-item">
              <div className="audit-bar-row">
                <span className="audit-dim">{labelDim(k)}</span>
                <div className="audit-bar-track">
                  <div className="audit-bar-fill" style={{ width: `${v * 10}%` }} />
                </div>
                <span className="audit-bar-value">{v}/10</span>
              </div>
              {(pro || con) && (
                <div className="audit-notes audit-notes--compact">
                  {pro && (
                    <p>
                      <span className={`note-tag ${isAfter ? "note-tag--works" : "note-tag--pro"}`}>
                        {isAfter ? "Works" : "Pro"}
                      </span>
                      {shortNote(pro)}
                    </p>
                  )}
                  {con && (
                    <p>
                      <span className="note-tag note-tag--con">Improve</span>
                      {shortNote(con)}
                    </p>
                  )}
                </div>
              )}
            </li>
          );
        })}
      </ul>

      {!isAfter && flaws.length > 0 && (
        <div className="flaw-list">
          <h4>What can be improved</h4>
          {flaws.map((f, i) => (
            <article key={i} className="flaw-card">
              <span className={`severity severity--${f.severity || "medium"}`}>
                {f.severity || "note"}
              </span>
              <p className="flaw-title">{f.flaw || f.search_intent || `Zone ${i + 1}`}</p>
              {f.con && <p className="flaw-con">{shortNote(f.con, 100)}</p>}
            </article>
          ))}
        </div>
      )}
    </section>
  );
}

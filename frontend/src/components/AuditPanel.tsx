import type { Flaw, ScoreEvidence } from "../types";
import { avgScore, labelDim } from "../types";

type Props = {
  scores: Record<string, number>;
  scoreEvidence?: Record<string, ScoreEvidence>;
  flaws: Flaw[];
  variant: "before" | "after";
  whyBetter?: string;
};

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

      <ul className="audit-bars">
        {entries.map(([k, v]) => {
          const evidence = scoreEvidence[k];
          const because = evidence?.because?.trim();
          const improvement = evidence?.improvement?.trim();
          return (
            <li key={k} className="audit-bar-item">
              <div className="audit-bar-row">
                <span className="audit-dim">{labelDim(k)}</span>
                <div className="audit-bar-track">
                  <div className="audit-bar-fill" style={{ width: `${v * 10}%` }} />
                </div>
                <span className="audit-bar-value">{v}/10</span>
              </div>
              {!isAfter && (because || improvement) && (
                <div className="audit-notes">
                  {because && (
                    <p><span className="note-tag note-tag--pro">Pro</span> {because}</p>
                  )}
                  {improvement && (
                    <p><span className="note-tag note-tag--con">Improve</span> {improvement}</p>
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
              <span className={`severity severity--${f.severity || "medium"}`}>{f.severity || "note"}</span>
              <p className="flaw-title">{f.flaw || f.search_intent || `Zone ${i + 1}`}</p>
              {f.con && <p className="flaw-con">{f.con}</p>}
              {f.pro && <p className="flaw-pro"><span className="note-tag note-tag--pro">Potential</span> {f.pro}</p>}
            </article>
          ))}
        </div>
      )}

      {isAfter && whyBetter && (
        <p className="why-better">{whyBetter}</p>
      )}
    </section>
  );
}

type ScoreEvidence = {
  because?: string;
  improvement?: string;
};

type Props = {
  scores: Record<string, number>;
  scoreEvidence?: Record<string, ScoreEvidence>;
};

function label(key: string) {
  return key.replace(/_/g, " ");
}

export function ScoreList({ scores, scoreEvidence = {} }: Props) {
  const entries = Object.entries(scores);
  if (!entries.length) return null;
  return (
    <section className="panel scores">
      <h2>Audit Scores</h2>
      <ul className="score-list">
        {entries.map(([k, v]) => {
          const evidence = scoreEvidence[k];
          const because = evidence?.because?.trim();
          const improvement = evidence?.improvement?.trim();
          return (
            <li key={k}>
              <div className="score-row">
                <span className="dim">{label(k)}</span>
                <div className="bar-wrap">
                  <div className="bar" style={{ width: `${v * 10}%` }} />
                </div>
                <span className="score-value">{v}/10</span>
              </div>
              {(because || improvement) && (
                <div className="score-reasoning">
                  {because && (
                    <p>
                      <span className="reason-label">Because:</span> {because}
                    </p>
                  )}
                  {improvement && (
                    <p>
                      <span className="reason-label">Could improve by:</span> {improvement}
                    </p>
                  )}
                </div>
              )}
            </li>
          );
        })}
      </ul>
    </section>
  );
}

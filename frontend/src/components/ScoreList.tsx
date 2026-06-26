type Props = {
  scores: Record<string, number>;
};

export function ScoreList({ scores }: Props) {
  const entries = Object.entries(scores);
  if (!entries.length) return null;
  return (
    <section className="panel scores">
      <h2>Audit Scores</h2>
      <ul className="score-list">
        {entries.map(([k, v]) => (
          <li key={k}>
            <span className="dim">{k.replace(/_/g, " ")}</span>
            <div className="bar-wrap"><div className="bar" style={{ width: `${v * 10}%` }} /></div>
            <span>{v}/10</span>
          </li>
        ))}
      </ul>
    </section>
  );
}

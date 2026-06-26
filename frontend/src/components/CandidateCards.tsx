type Props = {
  ranked: Array<Record<string, unknown>>;
  explanation: string;
};

export function CandidateCards({ ranked, explanation }: Props) {
  if (!ranked.length) return null;
  return (
    <section className="panel cards">
      <h2>Verified Picks</h2>
      {explanation && <p className="rank-explain">{explanation}</p>}
      <div className="card-grid">
        {ranked.map((c, i) => (
          <article key={i} className="card">
            <span className="rank-badge">#{String(c.rank ?? i + 1)}</span>
            {Boolean(c.grounded) && <span className="senso-badge">Senso Grounded ✓</span>}
            <h3>{String(c.title ?? "Listing")}</h3>
            {c.price_gbp != null && <p className="price">£{Number(c.price_gbp).toFixed(0)}</p>}
            {c.capacity != null && <p>Capacity: {String(c.capacity)}</p>}
            {c.why != null && <p className="why">{String(c.why)}</p>}
            {Array.isArray(c.provenance) && (
              <p className="provenance" title={c.provenance.join(", ")}>Provenance: {(c.provenance as string[]).slice(0, 2).join(" · ")}</p>
            )}
            {c.url != null && (
              <a href={String(c.url)} target="_blank" rel="noreferrer">View live listing →</a>
            )}
          </article>
        ))}
      </div>
    </section>
  );
}

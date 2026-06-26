type Props = {
  stats: { total_searches: number; total_extracts: number; total_grounded: number; total_events: number };
};

export function RaidDashboard({ stats }: Props) {
  return (
    <section className="panel dashboard">
      <h2>Raid Dashboard</h2>
      <div className="stats">
        <div><strong>{stats.total_searches}</strong><span>Tavily searches</span></div>
        <div><strong>{stats.total_extracts}</strong><span>Extracts</span></div>
        <div><strong>{stats.total_grounded}</strong><span>Senso grounded</span></div>
        <div><strong>{stats.total_events}</strong><span>Total events</span></div>
      </div>
    </section>
  );
}

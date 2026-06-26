import type { AgentEvent } from "../hooks/useRaidStream";

type Props = {
  events: AgentEvent[];
  running: boolean;
};

export function AgentTrace({ events, running }: Props) {
  return (
    <section className="panel trace">
      <h2>Agent Trace</h2>
      <div className="trace-list">
        {events.length === 0 && <p className="muted">{running ? "Agents raiding the web..." : "Waiting to start"}</p>}
        {events.map((ev, i) => (
          <div key={i} className={`trace-item trace-${ev.type}`}>
            <span className="trace-agent">{ev.agent}</span>
            <span className="trace-msg">{ev.message}</span>
            {ev.ts && <span className="trace-ts">{new Date(ev.ts).toLocaleTimeString()}</span>}
          </div>
        ))}
        {running && <div className="trace-item pulsing">● Autonomous loop running...</div>}
      </div>
    </section>
  );
}

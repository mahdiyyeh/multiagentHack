type Props = {
  compact?: boolean;
};

export function BuiltWithCursor({ compact = false }: Props) {
  if (compact) {
    return (
      <p className="built-with-cursor built-with-cursor--compact">
        <span className="cursor-badge">Built with Cursor</span>
        <span className="built-with-cursor__tagline">IDE rules mirror our runtime agents</span>
      </p>
    );
  }

  return (
    <aside className="built-with-cursor" aria-label="Built with Cursor">
      <span className="cursor-badge">Built with Cursor</span>
      <p className="built-with-cursor__body">
        SpaceRaid was scaffolded with Cursor Agent. Our{" "}
        <code>.cursor/rules</code> mirror the LangGraph runtime in{" "}
        <code>AGENTS.md</code> — same agent roster, same pipeline, same conventions.
      </p>
      <p className="built-with-cursor__tagline">
        One architecture, two agent systems: Cursor in the IDE, autonomous agents in production.
      </p>
    </aside>
  );
}

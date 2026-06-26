type Props = {
  mode: "home" | "venue";
  budget: number;
  brief: string;
  running: boolean;
  onMode: (m: "home" | "venue") => void;
  onBudget: (b: number) => void;
  onBrief: (b: string) => void;
  onSubmit: (file: File) => void;
};

export function UploadForm({ mode, budget, brief, running, onMode, onBudget, onBrief, onSubmit }: Props) {
  return (
    <section className="panel upload">
      <h1>SpaceRaid</h1>
      <p className="tagline">Audit your space. Raid the web. Prove every pick.</p>
      <div className="mode-toggle">
        <button type="button" className={mode === "home" ? "active" : ""} onClick={() => onMode("home")} disabled={running}>Home</button>
        <button type="button" className={mode === "venue" ? "active" : ""} onClick={() => onMode("venue")} disabled={running}>Venue</button>
      </div>
      <label>
        Budget (£)
        <input type="range" min={50} max={5000} step={50} value={budget} onChange={(e) => onBudget(Number(e.target.value))} disabled={running} />
        <span>£{budget}</span>
      </label>
      {mode === "venue" && (
        <label>
          Brief
          <textarea value={brief} onChange={(e) => onBrief(e.target.value)} placeholder="40 people, London, natural light, next month" disabled={running} rows={2} />
        </label>
      )}
      <label className="file-label">
        Upload photo
        <input type="file" accept="image/*" disabled={running} onChange={(e) => e.target.files?.[0] && onSubmit(e.target.files[0])} />
      </label>
    </section>
  );
}

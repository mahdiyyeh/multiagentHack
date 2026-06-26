import { useRef, useState } from "react";

type Props = {
  mode: "home" | "venue";
  budget: number;
  brief: string;
  running: boolean;
  onMode: (m: "home" | "venue") => void;
  onBudget: (b: number) => void;
  onBrief: (b: string) => void;
  onSubmit: (files: File[]) => void;
};

const MAX_IMAGES = 10;

export function UploadForm({ mode, budget, brief, running, onMode, onBudget, onBrief, onSubmit }: Props) {
  const [selected, setSelected] = useState<File[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFiles = (fileList: FileList | null) => {
    if (!fileList?.length) return;
    const images = Array.from(fileList).filter((f) => f.type.startsWith("image/"));
    setSelected(images.slice(0, MAX_IMAGES));
  };

  const handleSubmit = () => {
    if (selected.length > 0) onSubmit(selected);
  };

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
        Upload photos
        <input
          ref={inputRef}
          type="file"
          accept="image/*"
          multiple
          disabled={running}
          onChange={(e) => handleFiles(e.target.files)}
        />
      </label>
      {selected.length > 0 && (
        <p className="file-count">{selected.length} photo{selected.length !== 1 ? "s" : ""} selected</p>
      )}
      <button
        type="button"
        className="raid-btn"
        disabled={running || selected.length === 0}
        onClick={handleSubmit}
      >
        {running ? "Raiding…" : "Start Raid"}
      </button>
    </section>
  );
}

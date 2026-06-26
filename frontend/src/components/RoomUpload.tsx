import { useRef, useState } from "react";

type Props = {
  running: boolean;
  onSubmit: (files: File[], wantsSuggestions: boolean, isBlueprint: boolean) => void;
};

export function RoomUpload({ running, onSubmit }: Props) {
  const [selected, setSelected] = useState<File[]>([]);
  const [preview, setPreview] = useState<string | null>(null);
  const [wantsSuggestions, setWantsSuggestions] = useState(true);
  const [isBlueprint, setIsBlueprint] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFiles = (fileList: FileList | null) => {
    if (!fileList?.length) return;
    const file = Array.from(fileList).find((f) => f.type.startsWith("image/"));
    if (!file) return;
    setSelected([file]);
    setPreview(URL.createObjectURL(file));
  };

  const handleSubmit = () => {
    if (selected.length > 0) onSubmit(selected, wantsSuggestions, isBlueprint);
  };

  return (
    <section className="room-upload">
      <div className="room-upload__copy">
        <p className="eyebrow">Common room</p>
        <h2 className="section-title">Before we begin</h2>
        <p className="lede lede--narrow">
          Submit a photograph of your living space or layout drawing. We will audit proportion,
          light, and material harmony — then curate verified improvements within your budget.
        </p>
      </div>

      <div
        className={`upload-zone ${preview ? "has-image" : ""}`}
        onClick={() => !running && inputRef.current?.click()}
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => {
          e.preventDefault();
          if (!running) handleFiles(e.dataTransfer.files);
        }}
        role="button"
        tabIndex={0}
      >
        <input
          ref={inputRef}
          type="file"
          accept="image/*"
          hidden
          disabled={running}
          onChange={(e) => handleFiles(e.target.files)}
        />
        {preview ? (
          <img src={preview} alt="Your room" className="upload-preview" />
        ) : (
          <div className="upload-placeholder">
            <span className="upload-icon">+</span>
            <p>Please submit a picture</p>
            <span className="upload-hint">Drag & drop or click to browse</span>
          </div>
        )}
      </div>

      <div className="upload-options">
        <label className="lux-toggle">
          <input
            type="checkbox"
            checked={wantsSuggestions}
            onChange={(e) => setWantsSuggestions(e.target.checked)}
            disabled={running}
          />
          <span className="lux-toggle__track" />
          <span className="lux-toggle__text">
            <strong>Do you want suggestions?</strong>
            <small>Receive curated improvements and verified listings</small>
          </span>
        </label>

        <label className="lux-toggle">
          <input
            type="checkbox"
            checked={isBlueprint}
            onChange={(e) => setIsBlueprint(e.target.checked)}
            disabled={running}
          />
          <span className="lux-toggle__track" />
          <span className="lux-toggle__text">
            <strong>Is this a layout?</strong>
            <small>Floor plan or architectural drawing rather than a photograph</small>
          </span>
        </label>
      </div>

      <button
        type="button"
        className="primary-btn"
        disabled={running || selected.length === 0}
        onClick={handleSubmit}
      >
        {running ? "Analysing your space…" : "Begin audit"}
      </button>
    </section>
  );
}

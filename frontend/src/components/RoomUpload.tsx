import { useEffect, useRef, useState } from "react";

const MAX_IMAGES = 10;

type Props = {
  running: boolean;
  onSubmit: (files: File[], wantsSuggestions: boolean, isBlueprint: boolean) => void;
};

export function RoomUpload({ running, onSubmit }: Props) {
  const [selected, setSelected] = useState<File[]>([]);
  const [previews, setPreviews] = useState<string[]>([]);
  const [wantsSuggestions, setWantsSuggestions] = useState(true);
  const [isBlueprint, setIsBlueprint] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const urls = selected.map((f) => URL.createObjectURL(f));
    setPreviews(urls);
    return () => urls.forEach((u) => URL.revokeObjectURL(u));
  }, [selected]);

  const handleFiles = (fileList: FileList | null) => {
    if (!fileList?.length) return;
    const images = Array.from(fileList).filter((f) => f.type.startsWith("image/"));
    if (!images.length) return;
    setSelected((prev) => [...prev, ...images].slice(0, MAX_IMAGES));
  };

  const removeImage = (index: number) => {
    setSelected((prev) => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = () => {
    if (selected.length > 0) onSubmit(selected, wantsSuggestions, isBlueprint);
  };

  const hasImages = previews.length > 0;

  return (
    <section className="room-upload">
      <div className="room-upload__copy">
        <p className="eyebrow">Common room</p>
        <h2 className="section-title">Before we begin</h2>
        <p className="lede lede--narrow">
          Submit one or more photographs of your living space or layout drawing. We will audit
          proportion, light, and material harmony — then curate verified improvements within your budget.
        </p>
      </div>

      <div
        className={`upload-zone ${hasImages ? "has-images" : ""}`}
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
          multiple
          hidden
          disabled={running}
          onChange={(e) => {
            handleFiles(e.target.files);
            e.target.value = "";
          }}
        />
        {!hasImages ? (
          <div className="upload-placeholder">
            <span className="upload-icon">+</span>
            <p>Add your room photos</p>
            <span className="upload-hint">Drag & drop or click — select multiple at once</span>
          </div>
        ) : previews.length === 1 ? (
          <img src={previews[0]} alt="Your room" className="upload-preview" />
        ) : (
          <div className="upload-grid">
            {previews.map((url, i) => (
              <div key={url} className="upload-grid__item">
                <img src={url} alt={`Room photo ${i + 1}`} />
                <button
                  type="button"
                  className="upload-grid__remove"
                  aria-label={`Remove photo ${i + 1}`}
                  disabled={running}
                  onClick={(e) => {
                    e.stopPropagation();
                    removeImage(i);
                  }}
                >
                  ×
                </button>
              </div>
            ))}
            {selected.length < MAX_IMAGES && (
              <button
                type="button"
                className="upload-grid__add"
                disabled={running}
                onClick={(e) => {
                  e.stopPropagation();
                  inputRef.current?.click();
                }}
              >
                + Add more
              </button>
            )}
          </div>
        )}
      </div>

      {hasImages && (
        <p className="upload-count">
          {selected.length} photo{selected.length !== 1 ? "s" : ""} selected
          {selected.length < MAX_IMAGES && ` · up to ${MAX_IMAGES}`}
        </p>
      )}

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

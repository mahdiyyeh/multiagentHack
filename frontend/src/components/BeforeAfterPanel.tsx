import { useRef } from "react";
import type { Callout } from "../types";
import { DiagnosticCanvas } from "./DiagnosticCanvas";

type View = "before" | "after";

type Props = {
  imageUrl: string;
  beforeCallouts: Callout[];
  afterCallouts: Callout[];
  isBlueprint?: boolean;
  view: View;
  onViewChange: (view: View) => void;
};

export function BeforeAfterPanel({
  imageUrl,
  beforeCallouts,
  afterCallouts,
  isBlueprint,
  view,
  onViewChange,
}: Props) {
  const startX = useRef<number | null>(null);
  const dragging = useRef(false);

  const swipe = (delta: number) => {
    if (delta < -48) onViewChange("after");
    else if (delta > 48) onViewChange("before");
  };

  const onTouchStart = (e: React.TouchEvent) => {
    startX.current = e.touches[0].clientX;
    dragging.current = true;
  };

  const onTouchEnd = (e: React.TouchEvent) => {
    if (!dragging.current || startX.current == null) return;
    swipe(e.changedTouches[0].clientX - startX.current);
    dragging.current = false;
    startX.current = null;
  };

  const onPointerDown = (e: React.PointerEvent) => {
    if (e.pointerType === "mouse" && e.button !== 0) return;
    startX.current = e.clientX;
    dragging.current = true;
  };

  const onPointerUp = (e: React.PointerEvent) => {
    if (!dragging.current || startX.current == null) return;
    swipe(e.clientX - startX.current);
    dragging.current = false;
    startX.current = null;
  };

  const onPointerLeave = () => {
    dragging.current = false;
    startX.current = null;
  };

  return (
    <section className={`before-after view-${view}`}>
      <div className="before-after__tabs">
        <button
          type="button"
          className={view === "before" ? "active" : ""}
          onClick={() => onViewChange("before")}
        >
          Before
        </button>
        <button
          type="button"
          className={view === "after" ? "active" : ""}
          onClick={() => onViewChange("after")}
        >
          Vision
        </button>
        <span className="swipe-hint">
          {view === "before" ? "Swipe left for the vision →" : "← Swipe right for before"}
        </span>
      </div>

      <div
        className={`before-after__stage view-${view}`}
        onTouchStart={onTouchStart}
        onTouchEnd={onTouchEnd}
        onPointerDown={onPointerDown}
        onPointerUp={onPointerUp}
        onPointerLeave={onPointerLeave}
        onPointerCancel={onPointerLeave}
      >
        <div className="before-after__panel before-after__panel--before">
          <DiagnosticCanvas
            imageUrl={imageUrl}
            callouts={beforeCallouts}
            variant="before"
            isBlueprint={isBlueprint}
          />
        </div>
        <div className="before-after__panel before-after__panel--after">
          <DiagnosticCanvas
            imageUrl={imageUrl}
            callouts={afterCallouts}
            variant="after"
            isBlueprint={isBlueprint}
          />
        </div>
      </div>
    </section>
  );
}

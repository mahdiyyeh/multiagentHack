import { useRef, useState } from "react";
import type { Callout } from "../types";
import { DiagnosticCanvas } from "./DiagnosticCanvas";

type Props = {
  imageUrl: string;
  beforeCallouts: Callout[];
  afterCallouts: Callout[];
  isBlueprint?: boolean;
};

export function BeforeAfterPanel({ imageUrl, beforeCallouts, afterCallouts, isBlueprint }: Props) {
  const [view, setView] = useState<"before" | "after">("before");
  const touchStart = useRef<number | null>(null);

  const onTouchStart = (e: React.TouchEvent) => {
    touchStart.current = e.touches[0].clientX;
  };

  const onTouchEnd = (e: React.TouchEvent) => {
    if (touchStart.current == null) return;
    const delta = e.changedTouches[0].clientX - touchStart.current;
    if (delta < -50) setView("after");
    if (delta > 50) setView("before");
    touchStart.current = null;
  };

  return (
    <section className="before-after">
      <div className="before-after__tabs">
        <button
          type="button"
          className={view === "before" ? "active" : ""}
          onClick={() => setView("before")}
        >
          Before
        </button>
        <button
          type="button"
          className={view === "after" ? "active" : ""}
          onClick={() => setView("after")}
        >
          Vision
        </button>
        <span className="swipe-hint">Swipe right for the vision →</span>
      </div>

      <div
        className="before-after__stage"
        onTouchStart={onTouchStart}
        onTouchEnd={onTouchEnd}
      >
        <div className={`before-after__track view-${view}`}>
          <DiagnosticCanvas
            imageUrl={imageUrl}
            callouts={beforeCallouts}
            variant="before"
            isBlueprint={isBlueprint}
          />
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

import type { Callout } from "../types";

type Props = {
  imageUrl: string;
  callouts: Callout[];
  variant: "before" | "after";
  isBlueprint?: boolean;
};

export function DiagnosticCanvas({ imageUrl, callouts, variant, isBlueprint }: Props) {
  const blueprintMode = isBlueprint && variant === "before";

  return (
    <div className={`diagnostic ${variant} ${blueprintMode ? "blueprint-mode" : ""}`}>
      <div className="diagnostic__image-wrap">
        <img src={imageUrl} alt={variant === "before" ? "Current room" : "Proposed vision"} className="diagnostic__image" />
        {variant === "after" && <div className="diagnostic__warmth" aria-hidden />}
        {callouts.map((c, i) => (
          <div
            key={c.id}
            className={`callout callout--${c.side}`}
            style={{ left: `${c.x}%`, top: `${c.y}%` }}
          >
            <span className="callout__dot">{i + 1}</span>
            <div className={`callout__card callout__card--${c.side}`}>
              <p className="callout__label">{c.label}</p>
              <p className="callout__detail">{c.detail}</p>
              {c.price != null && <p className="callout__price">£{c.price.toFixed(0)}</p>}
            </div>
            <svg className="callout__line" aria-hidden>
              <line x1="0" y1="0" x2={c.side === "left" ? -40 : 40} y2={c.side === "left" ? 20 : -20} />
            </svg>
          </div>
        ))}
      </div>
    </div>
  );
}

import type { Callout } from "../types";

type Props = {
  imageUrl: string;
  callouts: Callout[];
  variant: "before" | "after";
  isBlueprint?: boolean;
};

function shortText(text: string, max = 90): string {
  const t = text.trim();
  if (t.length <= max) return t;
  const cut = t.slice(0, max);
  const space = cut.lastIndexOf(" ");
  return `${space > 50 ? cut.slice(0, space) : cut}…`;
}

export function DiagnosticCanvas({ imageUrl, callouts, variant, isBlueprint }: Props) {
  const blueprintMode = isBlueprint && variant === "before";

  return (
    <div className={`diagnostic ${variant} ${blueprintMode ? "blueprint-mode" : ""}`}>
      <div className="diagnostic__image-wrap">
        <img
          src={imageUrl}
          alt={variant === "before" ? "Current room" : "Proposed vision"}
          className="diagnostic__image"
          draggable={false}
        />
        {variant === "after" && <div className="diagnostic__warmth" aria-hidden />}
        {callouts.map((c, i) => (
          <span
            key={c.id}
            className="callout-pin"
            style={{ left: `${c.x}%`, top: `${c.y}%` }}
            title={c.label}
          >
            {i + 1}
          </span>
        ))}
      </div>

      {callouts.length > 0 && (
        <ol className="callout-legend">
          {callouts.map((c, i) => (
            <li key={c.id} className="callout-legend__item">
              <span className="callout-legend__num">{i + 1}</span>
              <div className="callout-legend__body">
                <span className="callout-legend__label">{c.label}</span>
                <span className="callout-legend__detail">{shortText(c.detail)}</span>
                {c.price != null && (
                  <span className="callout-legend__price">£{c.price.toFixed(0)}</span>
                )}
              </div>
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}

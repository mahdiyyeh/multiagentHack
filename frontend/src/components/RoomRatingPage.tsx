import { useEffect, useState } from "react";
import { AgentTrace } from "./AgentTrace";
import { AudioSummary } from "./AudioSummary";
import { AuditPanel } from "./AuditPanel";
import { BeforeAfterPanel } from "./BeforeAfterPanel";
import { CandidateCards } from "./CandidateCards";
import { ReceiptPanel } from "./ReceiptPanel";
import { RoomUpload } from "./RoomUpload";
import type { RaidReport } from "../hooks/useRaidStream";
import type { AgentEvent } from "../hooks/useRaidStream";
import {
  flawCallouts,
  projectedScores,
  solutionCallouts,
  type Candidate,
  type Flaw,
} from "../types";

type Props = {
  running: boolean;
  status: string;
  report: RaidReport | null;
  events: AgentEvent[];
  previewUrls: string[];
  error: string | null;
  isBlueprint: boolean;
  wantsSuggestions: boolean;
  onSubmit: (files: File[], wantsSuggestions: boolean, isBlueprint: boolean) => void;
  onReset: () => void;
  onVisionModeChange?: (active: boolean) => void;
};

export function RoomRatingPage({
  running,
  status,
  report,
  events,
  previewUrls,
  error,
  isBlueprint,
  wantsSuggestions,
  onSubmit,
  onReset,
  onVisionModeChange,
}: Props) {
  const [view, setView] = useState<"before" | "after">("before");
  const [activeImage, setActiveImage] = useState(0);
  const hasResults = status === "complete" && report && previewUrls.length > 0;
  const flaws = (report?.flaws || []) as Flaw[];
  const ranked = (report?.ranked || []) as Candidate[];
  const imageUrl = previewUrls[activeImage] ?? previewUrls[0];

  const beforeCallouts = flawCallouts(flaws, ranked);
  const afterCallouts = solutionCallouts(flaws, ranked);
  const afterScores = report
    ? projectedScores(report.scores, report.score_evidence)
    : {};

  const whyBetter =
    report?.ranking_explanation ||
    "Warmer materials, corrected proportions, and verified furnishings raise every dimension — especially light, zoning, and biophilia.";

  const showVision = wantsSuggestions && view === "after";

  useEffect(() => {
    setActiveImage(0);
    setView("before");
  }, [previewUrls.length, status]);

  useEffect(() => {
    onVisionModeChange?.(Boolean(hasResults && showVision));
  }, [hasResults, showVision, onVisionModeChange]);

  return (
    <div className="room-rating-page">
      {!hasResults && (
        <RoomUpload running={running} onSubmit={onSubmit} />
      )}

      {running && (
        <div className="analysing-banner">
          <span className="pulse-dot" />
          <p>Our agents are auditing your space — tracing light, proportion, and material harmony…</p>
        </div>
      )}

      {hasResults && (
        <>
          <div className="results-toolbar">
            <p className="eyebrow">Audit complete</p>
            <button type="button" className="link-btn" onClick={onReset}>New audit</button>
          </div>

          {previewUrls.length > 1 && (
            <div className="image-strip" role="tablist" aria-label="Room photos">
              {previewUrls.map((url, i) => (
                <button
                  key={url}
                  type="button"
                  role="tab"
                  aria-selected={i === activeImage}
                  className={`image-strip__thumb ${i === activeImage ? "active" : ""}`}
                  onClick={() => setActiveImage(i)}
                >
                  <img src={url} alt={`Room photo ${i + 1}`} />
                  <span>{i + 1}</span>
                </button>
              ))}
            </div>
          )}

          <BeforeAfterPanel
            imageUrl={imageUrl}
            beforeCallouts={beforeCallouts}
            afterCallouts={wantsSuggestions ? afterCallouts : beforeCallouts}
            isBlueprint={isBlueprint}
            view={wantsSuggestions ? view : "before"}
            onViewChange={wantsSuggestions ? setView : () => {}}
          />

          <div className="audit-zone">
            <AuditPanel
              scores={showVision ? afterScores : report.scores}
              scoreEvidence={report.score_evidence}
              flaws={flaws}
              variant={showVision ? "after" : "before"}
              whyBetter={showVision ? whyBetter : undefined}
            />
          </div>

          {wantsSuggestions && ranked.length > 0 && (
            <CandidateCards ranked={ranked} explanation={report.ranking_explanation} />
          )}

          <div className="studio-footer">
            <ReceiptPanel receiptId={report.receipt_id} receiptType={report.receipt_type} />
            <AudioSummary audioB64={report.audio_b64} fallbackText={report.audio_fallback_text} />
            {report.total_gbp > 0 && (
              <p className="total-line">Curated total <strong>£{report.total_gbp.toFixed(0)}</strong></p>
            )}
          </div>
        </>
      )}

      {error && <p className="error-banner">{error}</p>}

      {(running || hasResults) && (
        <details className="studio-log">
          <summary>Studio log</summary>
          <AgentTrace events={events} running={running} />
        </details>
      )}
    </div>
  );
}

import { useState } from "react";
import { AgentTrace } from "./components/AgentTrace";
import { AudioSummary } from "./components/AudioSummary";
import { CandidateCards } from "./components/CandidateCards";
import { RaidDashboard } from "./components/RaidDashboard";
import { ReceiptPanel } from "./components/ReceiptPanel";
import { ScoreList } from "./components/ScoreList";
import { UploadForm } from "./components/UploadForm";
import { useRaidStream } from "./hooks/useRaidStream";
import "./App.css";

function App() {
  const [mode, setMode] = useState<"home" | "venue">("home");
  const [budget, setBudget] = useState(200);
  const [brief, setBrief] = useState("40 people, London, natural light, under £3000");
  const { status, events, report, dashboard, error, previewUrl, startRaid } = useRaidStream();
  const running = status === "running";

  const handleSubmit = async (file: File) => {
    try {
      await startRaid(file, mode, budget, brief);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="app">
      <header className="hero">
        <UploadForm
          mode={mode}
          budget={budget}
          brief={brief}
          running={running}
          onMode={setMode}
          onBudget={setBudget}
          onBrief={setBrief}
          onSubmit={handleSubmit}
        />
        {previewUrl && <img src={previewUrl} alt="Upload preview" className="preview" />}
      </header>

      <main className="grid">
        <AgentTrace events={events} running={running} />
        <RaidDashboard stats={dashboard} />
        {report && <ScoreList scores={report.scores} />}
        {report && (
          <CandidateCards ranked={report.ranked || []} explanation={report.ranking_explanation} />
        )}
        {report && <ReceiptPanel receiptId={report.receipt_id} receiptType={report.receipt_type} />}
        {report && (
          <AudioSummary audioB64={report.audio_b64} fallbackText={report.audio_fallback_text} />
        )}
        {report?.twilio_sent && <p className="twilio-banner">Twilio: venue enquiry SMS sent</p>}
        {report?.mailto_link && !report.twilio_sent && report.mode === "venue" && (
          <a className="mailto" href={report.mailto_link}>Send venue enquiry (mailto)</a>
        )}
        {error && <p className="error">{error}</p>}
        {report && (
          <section className="panel total">
            <h2>Total</h2>
            <p className="total-gbp">£{Number(report.total_gbp || 0).toFixed(0)}</p>
            {report.replan_count > 0 && <p className="replan">Skeptic replanned {report.replan_count}× autonomously</p>}
          </section>
        )}
      </main>
    </div>
  );
}

export default App;

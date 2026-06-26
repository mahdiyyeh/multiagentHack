import { useEffect, useState } from "react";
import { HomeBlueprint } from "./components/HomeBlueprint";
import { BuiltWithCursor } from "./components/BuiltWithCursor";
import { PlaceholderPage } from "./components/PlaceholderPage";
import { RoomRatingPage } from "./components/RoomRatingPage";
import { SiteHeader } from "./components/SiteHeader";
import { useRaidStream } from "./hooks/useRaidStream";
import type { View } from "./types";
import "./App.css";

function App() {
  const [view, setView] = useState<View>("blueprint");
  const [budget] = useState(500);
  const [isBlueprint, setIsBlueprint] = useState(false);
  const [wantsSuggestions, setWantsSuggestions] = useState(true);
  const { status, events, report, error, previewUrls, startRaid, reset } = useRaidStream();
  const running = status === "running";
  const [visionMode, setVisionMode] = useState(false);

  useEffect(() => {
    document.body.classList.toggle("vision-mode", visionMode);
    return () => document.body.classList.remove("vision-mode");
  }, [visionMode]);

  const handleReset = () => {
    setVisionMode(false);
    reset();
  };

  const handleSubmit = async (files: File[], wants: boolean, blueprint: boolean) => {
    setWantsSuggestions(wants);
    setIsBlueprint(blueprint);
    const brief = [
      wants ? "wants improvement suggestions" : "audit only",
      blueprint ? "image is a floor plan/layout" : "image is a room photograph",
    ].join("; ");
    try {
      await startRaid(files, "home", budget, brief);
    } catch (e) {
      console.error(e);
    }
  };

  const goBlueprint = () => setView("blueprint");
  const showBack = view !== "blueprint";

  return (
    <div className="app">
      <SiteHeader onNavigate={setView} showBack={showBack} onBack={goBlueprint} />

      {view === "blueprint" && (
        <HomeBlueprint onSelectRoom={setView} />
      )}

      {view === "common-room" && (
        <RoomRatingPage
          running={running}
          status={status}
          report={report}
          events={events}
          previewUrls={previewUrls}
          error={error}
          isBlueprint={isBlueprint}
          wantsSuggestions={wantsSuggestions}
          onSubmit={handleSubmit}
          onReset={handleReset}
          onVisionModeChange={setVisionMode}
        />
      )}

      {view === "about" && (
        <PlaceholderPage
          title="About Atelier"
          body="We combine architectural intelligence with verified furnishings — the calm precision of a showroom, powered by autonomous agents that audit, source, and prove every recommendation."
        >
          <BuiltWithCursor />
        </PlaceholderPage>
      )}

      {view === "home-room" && (
        <PlaceholderPage
          title="Welcome"
          body="Your foyer to the plan. From here, wander into the common room to rate and refine your living space — or explore other rooms as they open."
        />
      )}

      {view === "coming-soon" && (
        <PlaceholderPage
          title="Coming soon"
          body="This room is not yet open. Return to the floor plan and visit the common room for our full room rating experience."
        />
      )}
    </div>
  );
}

export default App;

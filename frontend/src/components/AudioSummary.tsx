import { useEffect, useRef } from "react";

type Props = {
  audioB64: string;
  fallbackText: string;
};

export function AudioSummary({ audioB64, fallbackText }: Props) {
  const spoke = useRef(false);

  useEffect(() => {
    if (!fallbackText || spoke.current) return;
    spoke.current = true;
    if (audioB64) return;
    if ("speechSynthesis" in window) {
      const u = new SpeechSynthesisUtterance(fallbackText);
      window.speechSynthesis.speak(u);
    }
  }, [audioB64, fallbackText]);

  if (!fallbackText) return null;

  const src = audioB64 ? `data:audio/mpeg;base64,${audioB64}` : "";

  return (
    <section className="panel audio">
      <h2>Narrator {audioB64 ? "(ElevenLabs)" : "(Browser TTS)"}</h2>
      <p>{fallbackText}</p>
      {src && <audio controls src={src} />}
    </section>
  );
}

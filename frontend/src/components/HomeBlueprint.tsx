import type { View } from "../types";

type Room = {
  id: View;
  label: string;
  x: number;
  y: number;
  w: number;
  h: number;
  available: boolean;
  description?: string;
};

const ROOMS: Room[] = [
  { id: "home-room", label: "Home", x: 120, y: 40, w: 160, h: 90, available: true, description: "Welcome foyer" },
  { id: "about", label: "About", x: 80, y: 150, w: 240, h: 80, available: true, description: "Our philosophy" },
  { id: "common-room", label: "Common Room", x: 40, y: 250, w: 320, h: 180, available: true, description: "Room rating & audit" },
  { id: "coming-soon", label: "Bedroom", x: 40, y: 450, w: 150, h: 100, available: false },
  { id: "coming-soon", label: "Study", x: 210, y: 450, w: 150, h: 100, available: false },
];

type Props = {
  onSelectRoom: (view: View) => void;
};

export function HomeBlueprint({ onSelectRoom }: Props) {
  return (
    <section className="blueprint-page">
      <div className="blueprint-intro">
        <p className="eyebrow">Interior intelligence</p>
        <h1 className="display-title">Walk the plan.<br />Rate every room.</h1>
        <p className="lede">
          Select a room on the architectural plan below. Our common room audit reveals what works,
          what doesn&apos;t, and how to elevate your space — with verified furnishings.
        </p>
      </div>

      <div className="blueprint-frame">
        <svg viewBox="0 0 400 580" className="blueprint-svg" aria-label="House floor plan">
          <defs>
            <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
              <path d="M 20 0 L 0 0 0 20" fill="none" stroke="currentColor" strokeWidth="0.4" opacity="0.25" />
            </pattern>
          </defs>
          <rect width="400" height="580" fill="url(#grid)" className="blueprint-grid" />
          <rect x="20" y="20" width="360" height="540" fill="none" stroke="currentColor" strokeWidth="1.5" className="blueprint-outline" />

          {ROOMS.map((room) => (
            <g key={room.label} className={`blueprint-room ${room.available ? "available" : "locked"}`}>
              <rect
                x={room.x}
                y={room.y}
                width={room.w}
                height={room.h}
                className="room-shape"
                role="button"
                tabIndex={room.available ? 0 : -1}
                onClick={() => room.available && onSelectRoom(room.id)}
                onKeyDown={(e) => e.key === "Enter" && room.available && onSelectRoom(room.id)}
              />
              <text x={room.x + room.w / 2} y={room.y + room.h / 2 - 6} className="room-label">
                {room.label}
              </text>
              {room.description && (
                <text x={room.x + room.w / 2} y={room.y + room.h / 2 + 14} className="room-sublabel">
                  {room.description}
                </text>
              )}
              {!room.available && (
                <text x={room.x + room.w / 2} y={room.y + room.h - 12} className="room-soon">
                  Coming soon
                </text>
              )}
            </g>
          ))}

          {/* Furniture hints in common room */}
          <circle cx="120" cy="340" r="14" className="furniture-hint" />
          <rect x="200" y="360" width="100" height="40" rx="6" className="furniture-hint" />
        </svg>
      </div>
    </section>
  );
}

import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";

const RINGS = [84, 154, 224];
const SIGNALS = [
  { label: "Messaging", x: 640, y: 134 },
  { label: "Pricing", x: 838, y: 298 },
  { label: "Support", x: 646, y: 510 },
  { label: "Demand", x: 438, y: 312 },
];

export const RepairProductRadar = () => {
  const frame = useCurrentFrame();
  const sweep = interpolate(frame, [0, 120], [0, 360], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const reveal = interpolate(frame, [0, 60], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ backgroundColor: "#0f172a", color: "#f8fafc", fontFamily: "Avenir, sans-serif", padding: 62 }}>
      <div style={{ fontSize: 52, fontWeight: 900 }}>Product launch radar</div>
      <svg width="100%" height="560" viewBox="0 0 1280 560" style={{ marginTop: 22 }}>
        {RINGS.map((radius) => <circle key={radius} cx="640" cy="320" r={radius} fill="none" stroke="rgba(148,163,184,0.35)" strokeWidth="3" />)}
        <g transform={`rotate(${sweep} 640 320)`}>
          <line x1="640" y1="320" x2="640" y2="96" stroke="#22d3ee" strokeWidth="8" strokeLinecap="round" opacity="0.9" />
        </g>
        {SIGNALS.map((signal, index) => {
          const signalReveal = interpolate(frame, [18 + index * 10, 38 + index * 10], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
          return (
            <g key={signal.label} opacity={signalReveal}>
              <circle cx={signal.x} cy={signal.y} r={18 + 12 * reveal} fill="#22c55e" />
              <text x={signal.x} y={signal.y - 30} textAnchor="middle" fill="#f8fafc" fontSize="24" fontWeight="900">{signal.label}</text>
            </g>
          );
        })}
      </svg>
    </AbsoluteFill>
  );
};

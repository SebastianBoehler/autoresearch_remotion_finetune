import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";

const RINGS = [90, 160, 230];
const SIGNALS = [
  { label: "Beta", x: 570, y: 210 },
  { label: "Docs", x: 790, y: 315 },
  { label: "Sales", x: 490, y: 430 },
  { label: "Launch", x: 720, y: 485 },
];

export const ProductLaunchRadar = () => {
  const frame = useCurrentFrame();
  const sweep = interpolate(frame, [0, 120], [0, 360], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ backgroundColor: "#eef2ff", padding: 70, color: "#1e1b4b", fontFamily: "Avenir, sans-serif" }}>
      <div style={{ fontSize: 54, fontWeight: 900 }}>Launch readiness radar</div>
      <svg width="100%" height="520" viewBox="0 0 1280 540" style={{ marginTop: 24 }}>
        {RINGS.map((radius) => <circle key={radius} cx="640" cy="340" r={radius} fill="none" stroke="rgba(67,56,202,0.18)" strokeWidth="5" />)}
        <line x1="640" y1="340" x2="640" y2="95" stroke="#4f46e5" strokeWidth="10" strokeLinecap="round" transform={`rotate(${sweep} 640 340)`} />
        {SIGNALS.map((signal, index) => {
          const active = frame > 18 + index * 18;
          return (
            <g key={signal.label}>
              <circle cx={signal.x} cy={signal.y} r={active ? 28 : 18} fill={active ? "#4f46e5" : "#c7d2fe"} />
              <text x={signal.x} y={signal.y + 62} textAnchor="middle" fill="#312e81" fontSize="26" fontWeight="900">{signal.label}</text>
            </g>
          );
        })}
      </svg>
    </AbsoluteFill>
  );
};

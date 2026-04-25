import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";

const SIGNALS = [
  { label: "Ligand", x: 190, y: 250 },
  { label: "Receptor", x: 430, y: 250 },
  { label: "Kinase", x: 670, y: 360 },
  { label: "Nucleus", x: 930, y: 260 },
];

export const CellSignalCascade = () => {
  const frame = useCurrentFrame();
  const pulse = interpolate(Math.sin(frame / 9), [-1, 1], [0.92, 1.08]);

  return (
    <AbsoluteFill style={{ backgroundColor: "#fff1f2", padding: 72, fontFamily: "Avenir, sans-serif", color: "#3f1d2b" }}>
      <div style={{ fontSize: 54, fontWeight: 900 }}>Cell signal cascade</div>
      <svg width="100%" height="520" viewBox="0 0 1280 540" style={{ marginTop: 22 }}>
        <ellipse cx="650" cy="275" rx="520" ry="210" fill="#ffe4e6" stroke="#fb7185" strokeWidth="8" />
        {SIGNALS.slice(0, -1).map((signal, index) => {
          const next = SIGNALS[index + 1];
          const reveal = interpolate(frame, [index * 24, index * 24 + 34], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
          return <line key={signal.label} x1={signal.x} y1={signal.y} x2={next.x} y2={next.y} stroke="#be123c" strokeWidth="10" strokeLinecap="round" strokeDasharray="360" strokeDashoffset={360 * (1 - reveal)} />;
        })}
        {SIGNALS.map((signal, index) => (
          <g key={signal.label} style={{ transform: `scale(${index === Math.floor(frame / 30) % SIGNALS.length ? pulse : 1})`, transformOrigin: `${signal.x}px ${signal.y}px` }}>
            <circle cx={signal.x} cy={signal.y} r={54} fill="#fff" stroke="#be123c" strokeWidth="7" />
            <text x={signal.x} y={signal.y + 8} textAnchor="middle" fill="#3f1d2b" fontSize="23" fontWeight="900">{signal.label}</text>
          </g>
        ))}
      </svg>
    </AbsoluteFill>
  );
};

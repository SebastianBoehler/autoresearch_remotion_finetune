import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";

const NODES = [
  { label: "Email", x: 170, y: 370 },
  { label: "Laptop", x: 420, y: 250 },
  { label: "SSO", x: 660, y: 380 },
  { label: "Data", x: 920, y: 230 },
  { label: "Block", x: 1080, y: 430 },
];

export const CyberAttackPath = () => {
  const frame = useCurrentFrame();
  const reveal = interpolate(frame, [0, 110], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ backgroundColor: "#0b1020", color: "#f8fafc", fontFamily: "Avenir, sans-serif", padding: 68 }}>
      <div style={{ fontSize: 52, fontWeight: 900 }}>Attack path containment</div>
      <svg width="100%" height="520" viewBox="0 0 1280 560" style={{ marginTop: 28 }}>
        {NODES.slice(0, -1).map((node, index) => {
          const next = NODES[index + 1];
          const visible = reveal > index / 4;
          return <line key={node.label} x1={node.x} y1={node.y} x2={next.x} y2={next.y} stroke={visible ? "#fb7185" : "rgba(255,255,255,0.14)"} strokeWidth="10" strokeLinecap="round" />;
        })}
        {NODES.map((node, index) => {
          const active = reveal > index / 5;
          return (
            <g key={node.label}>
              <circle cx={node.x} cy={node.y} r={active ? 56 : 44} fill={index === 4 ? "#22c55e" : active ? "#fb7185" : "#1f2937"} />
              <text x={node.x} y={node.y + 8} textAnchor="middle" fill="#fff" fontSize="24" fontWeight="800">{node.label}</text>
            </g>
          );
        })}
      </svg>
      <div style={{ fontSize: 28, color: "#cbd5e1" }}>Signals converge before data access completes.</div>
    </AbsoluteFill>
  );
};

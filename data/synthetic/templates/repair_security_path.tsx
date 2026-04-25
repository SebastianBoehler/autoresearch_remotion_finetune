import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";

const NODES = [
  { label: "Phish", x: 120, y: 330, color: "#ef4444" },
  { label: "Endpoint", x: 330, y: 210, color: "#ef4444" },
  { label: "SSO", x: 560, y: 330, color: "#ef4444" },
  { label: "Data", x: 790, y: 205, color: "#ef4444" },
  { label: "Contain", x: 1010, y: 350, color: "#22c55e" },
];

export const RepairSecurityPath = () => {
  const frame = useCurrentFrame();
  const pathReveal = interpolate(frame, [0, 92], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ backgroundColor: "#07111f", color: "#f8fafc", fontFamily: "Avenir, sans-serif", padding: 66 }}>
      <div style={{ fontSize: 52, fontWeight: 900 }}>Cyber attack path map</div>
      <svg width="100%" height="500" viewBox="0 0 1120 500" style={{ marginTop: 32 }}>
        {NODES.slice(0, -1).map((node, index) => {
          const next = NODES[index + 1];
          const visible = pathReveal >= (index + 1) / 4;
          return <line key={`${node.label}-${next.label}`} x1={node.x} y1={node.y} x2={next.x} y2={next.y} stroke={visible ? "#ef4444" : "rgba(255,255,255,0.16)"} strokeWidth="10" strokeLinecap="round" />;
        })}
        {NODES.map((node, index) => {
          const nodeReveal = interpolate(frame, [index * 13, index * 13 + 18], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
          return (
            <g key={node.label} opacity={nodeReveal}>
              <circle cx={node.x} cy={node.y} r={50 + nodeReveal * 8} fill={node.color} />
              <circle cx={node.x} cy={node.y} r="72" fill="none" stroke={node.color} strokeOpacity="0.25" strokeWidth="4" />
              <text x={node.x} y={node.y + 8} textAnchor="middle" fill="#fff" fontSize="23" fontWeight="900">{node.label}</text>
            </g>
          );
        })}
      </svg>
      <div style={{ fontSize: 28, color: "#cbd5e1" }}>Red path reveals first; green containment closes the route.</div>
    </AbsoluteFill>
  );
};

import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";

const NODES = [
  { label: "Read", angle: 0, color: "#38bdf8" },
  { label: "Recall", angle: 1.57, color: "#a78bfa" },
  { label: "Explain", angle: 3.14, color: "#fb7185" },
  { label: "Apply", angle: 4.71, color: "#34d399" },
];

export const ConceptOrbitLoop = () => {
  const frame = useCurrentFrame();
  const pulse = interpolate(Math.sin(frame / 12), [-1, 1], [0.92, 1.08]);

  return (
    <AbsoluteFill style={{ backgroundColor: "#031018", alignItems: "center", justifyContent: "center", fontFamily: "Avenir, sans-serif" }}>
      <div style={{ position: "absolute", width: 420, height: 420, borderRadius: 999, border: "2px solid rgba(255,255,255,0.16)", transform: `scale(${pulse})` }} />
      <div style={{ width: 210, height: 210, borderRadius: 999, backgroundColor: "#f8fafc", color: "#0f172a", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 44, fontWeight: 900, boxShadow: "0 0 80px rgba(56,189,248,0.25)" }}>Loop</div>
      {NODES.map((node, index) => {
        const angle = node.angle + frame / 70;
        const x = Math.cos(angle) * 300;
        const y = Math.sin(angle) * 210;
        return (
          <div key={node.label} style={{ position: "absolute", transform: `translate(${x}px, ${y}px)`, padding: "15px 22px", borderRadius: 999, backgroundColor: node.color, color: "#020617", fontSize: 25, fontWeight: 800, opacity: 0.75 + index * 0.06 }}>
            {node.label}
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

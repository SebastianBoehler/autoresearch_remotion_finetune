import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";

const ROWS = [
  { left: "Net 60 payment", right: "Net 30 payment", tone: "#dcfce7" },
  { left: "Auto-renewal", right: "Manual renewal", tone: "#dbeafe" },
  { left: "Unlimited liability", right: "Liability capped", tone: "#fee2e2" },
];

export const ContractDiffReview = () => {
  const frame = useCurrentFrame();

  return (
    <AbsoluteFill style={{ backgroundColor: "#111827", padding: 74, color: "#f9fafb", fontFamily: "Avenir, sans-serif" }}>
      <div style={{ fontSize: 54, fontWeight: 900 }}>Contract diff review</div>
      <div style={{ marginTop: 46, display: "grid", gap: 18 }}>
        {ROWS.map((row, index) => {
          const opacity = interpolate(frame, [index * 18, index * 18 + 28], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
          return (
            <div key={row.left} style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 18, opacity }}>
              <div style={{ borderRadius: 22, padding: 28, backgroundColor: "rgba(248,113,113,0.16)", color: "#fecaca", fontSize: 30, textDecoration: "line-through" }}>{row.left}</div>
              <div style={{ borderRadius: 22, padding: 28, backgroundColor: row.tone, color: "#111827", fontSize: 30, fontWeight: 900 }}>{row.right}</div>
            </div>
          );
        })}
      </div>
      <div style={{ position: "absolute", right: 72, bottom: 66, fontSize: 28, color: "#93c5fd" }}>Risk language becomes reviewable at a glance.</div>
    </AbsoluteFill>
  );
};

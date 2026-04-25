import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";

const CELLS = [
  [0.18, 0.34, 0.52, 0.71, 0.84],
  [0.22, 0.43, 0.59, 0.76, 0.91],
  [0.29, 0.48, 0.67, 0.82, 0.95],
  [0.17, 0.36, 0.58, 0.73, 0.88],
];

export const ClimateRiskHeatmap = () => {
  const frame = useCurrentFrame();

  return (
    <AbsoluteFill style={{ backgroundColor: "#f6fbf7", padding: 74, fontFamily: "Avenir, sans-serif", color: "#13251b" }}>
      <div style={{ fontSize: 52, fontWeight: 900 }}>Coastal heat risk outlook</div>
      <div style={{ marginTop: 10, fontSize: 26, color: "#496354" }}>Four districts, five forecast windows, one visible escalation pattern.</div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 14, marginTop: 44 }}>
        {CELLS.flatMap((row, rowIndex) =>
          row.map((risk, columnIndex) => {
            const delay = rowIndex * 6 + columnIndex * 5;
            const fill = interpolate(risk, [0.15, 0.95], [80, 7]);
            const scale = interpolate(frame, [delay, delay + 22], [0.78, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
            return (
              <div key={`${rowIndex}-${columnIndex}`} style={{ height: 104, borderRadius: 20, backgroundColor: `hsl(${fill}, 78%, 52%)`, transform: `scale(${scale})`, boxShadow: "0 18px 36px rgba(20,83,45,0.14)", display: "flex", alignItems: "center", justifyContent: "center", color: risk > 0.7 ? "#fff" : "#102016", fontSize: 28, fontWeight: 900 }}>
                {Math.round(risk * 100)}
              </div>
            );
          }),
        )}
      </div>
      <div style={{ marginTop: 34, height: 18, borderRadius: 99, background: "linear-gradient(90deg,#86efac,#facc15,#fb7185)" }} />
    </AbsoluteFill>
  );
};

import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";

const HEADLINE = "Loss decreases when the step points downhill.";
const FORMULA = "w = w - learning_rate * gradient";

export const TypewriterFormulaCard = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const letters = Math.floor(interpolate(frame, [0, 2.6 * fps], [0, HEADLINE.length], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }));
  const formulaOpacity = interpolate(frame, [2.2 * fps, 3.2 * fps], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const cursorOpacity = Math.floor(frame / 14) % 2 === 0 ? 1 : 0.25;

  return (
    <AbsoluteFill style={{ backgroundColor: "#08111f", padding: 86, color: "#eff6ff", fontFamily: "Avenir, sans-serif", justifyContent: "center" }}>
      <div style={{ fontSize: 58, fontWeight: 900, lineHeight: 1.08, maxWidth: 900 }}>
        {HEADLINE.slice(0, letters)}
        <span style={{ opacity: cursorOpacity, color: "#60a5fa" }}>|</span>
      </div>
      <div style={{ marginTop: 52, width: 760, padding: 30, borderRadius: 26, backgroundColor: "#111827", border: "2px solid rgba(147,197,253,0.35)", opacity: formulaOpacity, fontSize: 34, fontWeight: 800, color: "#bfdbfe" }}>
        {FORMULA}
      </div>
    </AbsoluteFill>
  );
};

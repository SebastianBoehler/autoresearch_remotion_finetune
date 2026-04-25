import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";

const TERMS = ["Recall", "Spacing", "Feedback"];

export const TypingTermReveal = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const activeCount = Math.min(TERMS.length, Math.floor(frame / (fps * 0.9)) + 1);

  return (
    <AbsoluteFill style={{ backgroundColor: "#f8fafc", padding: 82, color: "#0f172a", fontFamily: "Avenir, sans-serif" }}>
      <div style={{ fontSize: 52, fontWeight: 900 }}>Three retrieval ingredients</div>
      <div style={{ marginTop: 58, display: "grid", gap: 22 }}>
        {TERMS.map((term, index) => {
          const letters = Math.floor(interpolate(frame - index * fps * 0.9, [0, fps * 0.7], [0, term.length], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }));
          return (
            <div key={term} style={{ height: 104, borderRadius: 26, backgroundColor: index < activeCount ? "#dbeafe" : "#e2e8f0", padding: "24px 32px", fontSize: 42, fontWeight: 900 }}>
              {term.slice(0, letters)}
              {index === activeCount - 1 && <span style={{ color: "#2563eb" }}>|</span>}
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

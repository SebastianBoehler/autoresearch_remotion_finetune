import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

const BADGES = ["Focus", "Recall", "Mastery"];

export const ProgressBadgeMeter = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const fill = interpolate(frame, [0, 90], [0, 86], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ backgroundColor: "#fff7ed", padding: 80, color: "#1c1917", fontFamily: "Avenir, sans-serif" }}>
      <div style={{ fontSize: 54, fontWeight: 900 }}>Mastery meter</div>
      <div style={{ marginTop: 56, height: 42, borderRadius: 99, backgroundColor: "#fed7aa", overflow: "hidden" }}>
        <div style={{ width: `${fill}%`, height: "100%", borderRadius: 99, backgroundColor: "#ea580c" }} />
      </div>
      <div style={{ display: "flex", gap: 18, marginTop: 58 }}>
        {BADGES.map((badge, index) => {
          const pop = spring({ frame: frame - 34 - index * 12, fps, config: { damping: 18, stiffness: 140 } });
          return <div key={badge} style={{ flex: 1, padding: 28, borderRadius: 24, backgroundColor: "#ffffff", transform: `scale(${0.88 + pop * 0.12})`, fontSize: 30, fontWeight: 900, textAlign: "center" }}>{badge}</div>;
        })}
      </div>
    </AbsoluteFill>
  );
};

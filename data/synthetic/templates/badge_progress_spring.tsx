import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

const BADGES = ["Focus", "Practice", "Recall"];

export const BadgeProgressSpring = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const fill = interpolate(frame, [0, 92], [0, 78], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ backgroundColor: "#0f172a", padding: 78, color: "#f8fafc", fontFamily: "Avenir, sans-serif" }}>
      <div style={{ fontSize: 54, fontWeight: 900 }}>Mastery progress</div>
      <div style={{ marginTop: 38, height: 26, borderRadius: 99, backgroundColor: "rgba(255,255,255,0.12)" }}>
        <div style={{ width: `${fill}%`, height: "100%", borderRadius: 99, backgroundColor: "#38bdf8" }} />
      </div>
      <div style={{ display: "flex", gap: 20, marginTop: 58 }}>
        {BADGES.map((badge, index) => {
          const enter = spring({ frame: frame - index * 10, fps, config: { damping: 16, stiffness: 120 } });
          return <div key={badge} style={{ flex: 1, padding: 30, borderRadius: 22, backgroundColor: "#172554", border: "1px solid #38bdf8", transform: `scale(${enter})`, opacity: enter }}><div style={{ fontSize: 30, fontWeight: 900 }}>{badge}</div><div style={{ marginTop: 10, fontSize: 22, color: "#bae6fd" }}>badge unlocked</div></div>;
        })}
      </div>
    </AbsoluteFill>
  );
};

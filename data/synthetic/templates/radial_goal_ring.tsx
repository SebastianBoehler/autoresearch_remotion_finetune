import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";

const RADIUS = 126;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;

export const RadialGoalRing = () => {
  const frame = useCurrentFrame();
  const progress = interpolate(frame, [0, 86], [0, 0.74], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
  const percent = Math.round(progress * 100);

  return (
    <AbsoluteFill style={{ backgroundColor: "#101820", color: "#f8fafc", fontFamily: "Avenir, sans-serif", alignItems: "center", justifyContent: "center" }}>
      <svg width="360" height="360" viewBox="0 0 360 360">
        <circle cx="180" cy="180" r={RADIUS} fill="none" stroke="rgba(255,255,255,0.14)" strokeWidth="30" />
        <circle cx="180" cy="180" r={RADIUS} fill="none" stroke="#22c55e" strokeWidth="30" strokeLinecap="round" strokeDasharray={CIRCUMFERENCE} strokeDashoffset={CIRCUMFERENCE * (1 - progress)} transform="rotate(-90 180 180)" />
      </svg>
      <div style={{ position: "absolute", fontSize: 76, fontWeight: 900 }}>{percent}%</div>
      <div style={{ position: "absolute", bottom: 92, fontSize: 32, color: "#bbf7d0", fontWeight: 800 }}>Daily goal complete</div>
    </AbsoluteFill>
  );
};

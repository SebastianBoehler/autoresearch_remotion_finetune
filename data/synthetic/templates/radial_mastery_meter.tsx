import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";

const RADIUS = 142;
const STROKE = 28;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;

export const RadialMasteryMeter = () => {
  const frame = useCurrentFrame();
  const progress = interpolate(frame, [0, 78], [0, 0.82], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.quad),
  });
  const percentage = Math.round(progress * 100);

  return (
    <AbsoluteFill style={{ backgroundColor: "#111111", alignItems: "center", justifyContent: "center", fontFamily: "Avenir, sans-serif", color: "#ffffff" }}>
      <svg width="420" height="420" viewBox="0 0 420 420">
        <circle cx="210" cy="210" r={RADIUS} fill="none" stroke="#2a2a2a" strokeWidth={STROKE} />
        <circle cx="210" cy="210" r={RADIUS} fill="none" stroke="#facc15" strokeWidth={STROKE} strokeLinecap="round" strokeDasharray={CIRCUMFERENCE} strokeDashoffset={CIRCUMFERENCE * (1 - progress)} transform="rotate(-90 210 210)" />
      </svg>
      <div style={{ position: "absolute", fontSize: 88, fontWeight: 900 }}>{percentage}%</div>
      <div style={{ position: "absolute", marginTop: 220, fontSize: 30, color: "#d4d4d4" }}>Mastery estimate</div>
    </AbsoluteFill>
  );
};

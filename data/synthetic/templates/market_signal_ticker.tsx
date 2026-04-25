import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";

const POINTS = [58, 66, 61, 74, 71, 88, 84, 96];
const BADGES = ["ARR +18%", "Churn -2.1%", "Pipeline $4.2M"];

export const MarketSignalTicker = () => {
  const frame = useCurrentFrame();
  const reveal = interpolate(frame, [0, 96], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  const path = POINTS.map((value, index) => `${index === 0 ? "M" : "L"} ${110 + index * 145} ${520 - value * 3.2}`).join(" ");
  const dash = 1200;

  return (
    <AbsoluteFill style={{ backgroundColor: "#07130f", padding: 72, color: "#e8fff5", fontFamily: "Avenir, sans-serif" }}>
      <div style={{ fontSize: 24, color: "#86efac", textTransform: "uppercase", letterSpacing: 3 }}>Revenue desk</div>
      <div style={{ fontSize: 60, fontWeight: 900, marginTop: 12 }}>Market signal recovered</div>
      <svg width="100%" height="430" viewBox="0 0 1280 520" style={{ marginTop: 18 }}>
        {[0, 1, 2, 3].map((line) => (
          <line key={line} x1="80" x2="1190" y1={120 + line * 92} y2={120 + line * 92} stroke="rgba(255,255,255,0.09)" />
        ))}
        <path d={path} fill="none" stroke="#34d399" strokeWidth="14" strokeLinecap="round" strokeLinejoin="round" strokeDasharray={dash} strokeDashoffset={dash * (1 - reveal)} />
        {POINTS.map((value, index) => {
          const active = reveal > index / (POINTS.length - 1);
          return <circle key={index} cx={110 + index * 145} cy={520 - value * 3.2} r={active ? 13 : 0} fill="#ecfdf5" stroke="#34d399" strokeWidth="6" />;
        })}
      </svg>
      <div style={{ display: "flex", gap: 18 }}>
        {BADGES.map((badge, index) => (
          <div key={badge} style={{ padding: "18px 24px", borderRadius: 18, backgroundColor: "rgba(52,211,153,0.12)", border: "1px solid rgba(134,239,172,0.35)", opacity: interpolate(frame, [42 + index * 10, 68 + index * 10], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }), fontSize: 28, fontWeight: 800 }}>
            {badge}
          </div>
        ))}
      </div>
    </AbsoluteFill>
  );
};

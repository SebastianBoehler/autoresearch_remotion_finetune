import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";

const POINTS = [40, 54, 48, 63, 72, 69, 86];
const CARDS = ["Activation +9%", "Expansion +14%", "Forecast 92%"];

export const RevenueSparklineCards = () => {
  const frame = useCurrentFrame();
  const reveal = interpolate(frame, [0, 92], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const path = POINTS.map((value, index) => `${index === 0 ? "M" : "L"} ${120 + index * 160} ${430 - value * 3}`).join(" ");

  return (
    <AbsoluteFill style={{ backgroundColor: "#fcfcfd", padding: 74, color: "#111827", fontFamily: "Avenir, sans-serif" }}>
      <div style={{ fontSize: 54, fontWeight: 900 }}>Revenue signal stack</div>
      <svg width="100%" height="360" viewBox="0 0 1280 460" style={{ marginTop: 30 }}>
        <path d={path} fill="none" stroke="#0f766e" strokeWidth="14" strokeLinecap="round" strokeLinejoin="round" strokeDasharray="1200" strokeDashoffset={1200 * (1 - reveal)} />
        {POINTS.map((value, index) => <circle key={index} cx={120 + index * 160} cy={430 - value * 3} r={reveal > index / 6 ? 12 : 0} fill="#ecfdf5" stroke="#0f766e" strokeWidth="6" />)}
      </svg>
      <div style={{ display: "flex", gap: 18 }}>
        {CARDS.map((card, index) => <div key={card} style={{ flex: 1, padding: 24, borderRadius: 22, backgroundColor: "#ecfdf5", opacity: interpolate(frame, [42 + index * 10, 62 + index * 10], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }), fontSize: 30, fontWeight: 900 }}>{card}</div>)}
      </div>
    </AbsoluteFill>
  );
};

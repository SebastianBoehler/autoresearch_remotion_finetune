import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";

const POINTS = [48, 55, 53, 64, 70, 82, 88];
const BADGES = ["MRR $86k", "QoQ +19%", "Runway 18m"];

export const CompactMarketLineCard = () => {
  const frame = useCurrentFrame();
  const reveal = interpolate(frame, [0, 92], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
  const path = POINTS.map((value, index) => `${index === 0 ? "M" : "L"} ${96 + index * 150} ${390 - value * 2.9}`).join(" ");
  return (
    <AbsoluteFill style={{ backgroundColor: "#0b1220", padding: 76, color: "#f8fafc", fontFamily: "Avenir, sans-serif" }}>
      <div style={{ fontSize: 24, color: "#67e8f9", letterSpacing: 4, textTransform: "uppercase" }}>Revenue signal</div>
      <div style={{ fontSize: 56, fontWeight: 900, marginTop: 10 }}>Growth line recovered</div>
      <svg width="100%" height="360" viewBox="0 0 1120 430" style={{ marginTop: 34 }}>
        {[0, 1, 2].map((line) => <line key={line} x1="70" x2="1080" y1={120 + line * 92} y2={120 + line * 92} stroke="rgba(255,255,255,0.1)" />)}
        <path d={path} fill="none" stroke="#22d3ee" strokeWidth="12" strokeLinecap="round" strokeLinejoin="round" strokeDasharray="1100" strokeDashoffset={1100 * (1 - reveal)} />
        {POINTS.map((value, index) => <circle key={index} cx={96 + index * 150} cy={390 - value * 2.9} r={reveal > index / 6 ? 10 : 0} fill="#f8fafc" stroke="#22d3ee" strokeWidth="5" />)}
      </svg>
      <div style={{ display: "flex", gap: 18 }}>
        {BADGES.map((badge, index) => <div key={badge} style={{ padding: "18px 24px", borderRadius: 16, backgroundColor: "rgba(34,211,238,0.13)", border: "1px solid rgba(103,232,249,0.35)", fontSize: 26, fontWeight: 900, opacity: interpolate(frame, [42 + index * 8, 60 + index * 8], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) }}>{badge}</div>)}
      </div>
    </AbsoluteFill>
  );
};

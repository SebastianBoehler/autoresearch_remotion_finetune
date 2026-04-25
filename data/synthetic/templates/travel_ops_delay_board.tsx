import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";

const ROUTES = [
  { code: "NYC-LON", delay: 12, status: "Boarding" },
  { code: "SFO-NRT", delay: 38, status: "Crew hold" },
  { code: "MAD-FCO", delay: 8, status: "On time" },
  { code: "BER-AMS", delay: 21, status: "Weather" },
  { code: "DXB-SIN", delay: 17, status: "Gate swap" },
];
const POINTS = [18, 32, 22, 40, 28, 34];

export const TravelOpsDelayBoard = () => {
  const frame = useCurrentFrame();
  const reveal = interpolate(frame, [0, 92], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const path = POINTS.map((value, index) => `${index === 0 ? "M" : "L"} ${20 + index * 54} ${92 - value}`).join(" ");
  return (
    <AbsoluteFill style={{ backgroundColor: "#07111f", padding: 66, color: "#f8fafc", fontFamily: "Avenir, sans-serif" }}>
      <div style={{ fontSize: 54, fontWeight: 900 }}>Travel operations delay board</div>
      <div style={{ display: "grid", gridTemplateColumns: "1.3fr 360px", gap: 34, marginTop: 40 }}>
        <div style={{ display: "grid", gap: 14 }}>
          {ROUTES.map((route, index) => {
            const opacity = interpolate(frame, [index * 7, index * 7 + 22], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
            return (
              <div key={route.code} style={{ display: "grid", gridTemplateColumns: "170px 1fr 120px", alignItems: "center", padding: 20, borderRadius: 18, backgroundColor: "rgba(255,255,255,0.08)", opacity }}>
                <div style={{ fontSize: 27, fontWeight: 900 }}>{route.code}</div>
                <div style={{ fontSize: 23, color: "#cbd5e1" }}>{route.status}</div>
                <div style={{ padding: "10px 14px", borderRadius: 99, backgroundColor: route.delay > 30 ? "#fb7185" : "#38bdf8", color: "#06111f", textAlign: "center", fontSize: 22, fontWeight: 900 }}>{route.delay} min</div>
              </div>
            );
          })}
        </div>
        <div style={{ borderRadius: 26, padding: 26, backgroundColor: "rgba(255,255,255,0.08)", border: "1px solid rgba(125,211,252,0.25)" }}>
          <div style={{ fontSize: 28, fontWeight: 900 }}>Network status</div>
          <div style={{ marginTop: 18, height: 18, borderRadius: 99, backgroundColor: "#1f2937" }}>
            <div style={{ width: `${Math.round(68 * reveal)}%`, height: "100%", borderRadius: 99, backgroundColor: "#38bdf8" }} />
          </div>
          <svg width="300" height="120" viewBox="0 0 300 120" style={{ marginTop: 44 }}>
            <path d={path} fill="none" stroke="#38bdf8" strokeWidth="8" strokeLinecap="round" strokeLinejoin="round" strokeDasharray="360" strokeDashoffset={360 * (1 - reveal)} />
          </svg>
        </div>
      </div>
    </AbsoluteFill>
  );
};

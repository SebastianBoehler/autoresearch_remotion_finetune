import { AbsoluteFill, spring, useCurrentFrame, useVideoConfig } from "remotion";

const PATIENTS = [
  { id: "A12", need: "Vitals drift", level: "Observe", color: "#bfdbfe" },
  { id: "B04", need: "Lab result ready", level: "Review", color: "#fde68a" },
  { id: "C31", need: "Escalation rule", level: "Act now", color: "#fecaca" },
];

export const HealthcareTriageQueue = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return (
    <AbsoluteFill style={{ backgroundColor: "#f8fafc", padding: 70, fontFamily: "Avenir, sans-serif", color: "#0f172a" }}>
      <div style={{ fontSize: 54, fontWeight: 900 }}>Triage queue, explainable order</div>
      <div style={{ display: "flex", gap: 24, marginTop: 48 }}>
        {PATIENTS.map((patient, index) => {
          const enter = spring({ frame: frame - index * 14, fps, config: { damping: 18, stiffness: 150 } });
          return (
            <div key={patient.id} style={{ flex: 1, minHeight: 360, borderRadius: 28, backgroundColor: patient.color, padding: 34, transform: `translateY(${42 - enter * 42}px)`, boxShadow: "0 24px 55px rgba(15,23,42,0.14)" }}>
              <div style={{ fontSize: 28, fontWeight: 900, color: "#334155" }}>Patient {patient.id}</div>
              <div style={{ marginTop: 42, fontSize: 44, fontWeight: 900 }}>{patient.level}</div>
              <div style={{ marginTop: 20, fontSize: 26, lineHeight: 1.3 }}>{patient.need}</div>
              <div style={{ marginTop: 42, height: 14, borderRadius: 99, backgroundColor: "rgba(15,23,42,0.16)" }}>
                <div style={{ width: `${50 + index * 22}%`, height: "100%", borderRadius: 99, backgroundColor: "#0f172a" }} />
              </div>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

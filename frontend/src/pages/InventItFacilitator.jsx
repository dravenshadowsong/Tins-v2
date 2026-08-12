import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";

const BASE = import.meta.env.DEV ? "/api" : (import.meta.env.VITE_API_URL || "https://tins-v2-1.onrender.com/api");

const OBSERVATIONS = [
  { key: "obs_continued_without_prompting",  label: "Continued exploring without prompting" },
  { key: "obs_multiple_ideas",               label: "Generated multiple ideas" },
  { key: "obs_revised_idea",                 label: "Voluntarily revised an idea" },
  { key: "obs_experimented_alternatives",    label: "Experimented with alternatives" },
  { key: "obs_stuck_after_first",            label: "Became stuck after the first idea" },
  { key: "obs_persisted_after_difficulty",   label: "Persisted after facing difficulty" },
  { key: "obs_explained_reasoning",          label: "Explained the reasoning behind an idea" },
];

const SCALE = [
  { val: -1, label: "Unable to observe" },
  { val: 0,  label: "0 — Not observed" },
  { val: 1,  label: "1 — Slightly observed" },
  { val: 2,  label: "2 — Clearly observed" },
  { val: 3,  label: "3 — Strongly observed" },
];

export default function InventItFacilitator() {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const [scores, setScores] = useState(() =>
    Object.fromEntries(OBSERVATIONS.map(o => [o.key, -1]))
  );
  const [notes, setNotes] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState(null);

  const setScore = (key, val) => setScores(prev => ({ ...prev, [key]: val }));

  const handleSubmit = async () => {
    setSubmitting(true);
    setError(null);
    const token = sessionStorage.getItem("goat_token");
    try {
      const res = await fetch(`${BASE}/invent-it/sessions/${sessionId}/facilitator-observation`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}) },
        body: JSON.stringify({ ...scores, additional_notes: notes }),
      });
      if (!res.ok) throw new Error("Failed to save");
      setSubmitted(true);
    } catch (e) {
      setError("Could not save observations. Please try again.");
    }
    setSubmitting(false);
  };

  return (
    <div style={{
      minHeight: "100vh",
      background: "#0d1117",
      color: "#e6edf3",
      fontFamily: "'Nunito', sans-serif",
      padding: "40px 20px",
    }}>
      <div style={{ maxWidth: 640, margin: "0 auto" }}>

        {/* Header */}
        <div style={{ marginBottom: 32 }}>
          <div style={{
            display: "inline-flex", alignItems: "center", gap: 8,
            background: "rgba(245,166,35,0.1)", border: "1px solid rgba(245,166,35,0.3)",
            borderRadius: 30, padding: "6px 16px", fontSize: 12, fontWeight: 800,
            color: "#f5a623", textTransform: "uppercase", letterSpacing: 1, marginBottom: 16,
          }}>
            📋 Facilitator Observation
          </div>
          <h1 style={{ fontSize: 28, fontWeight: 900, margin: "0 0 8px" }}>
            Invent It — Observation Checklist
          </h1>
          <p style={{ color: "#8b949e", margin: 0, lineHeight: 1.5 }}>
            Please complete this checklist <strong style={{ color: "#e6edf3" }}>after</strong> the child has finished.
            Record what you actually observed — do not guess.
          </p>
          {sessionId && (
            <div style={{ marginTop: 12, fontSize: 12, color: "#6e7681", fontFamily: "monospace" }}>
              Session: {sessionId}
            </div>
          )}
        </div>

        {submitted ? (
          <div style={{
            background: "rgba(34,197,94,0.1)", border: "1px solid rgba(34,197,94,0.3)",
            borderRadius: 16, padding: "40px 32px", textAlign: "center",
          }}>
            <div style={{ fontSize: 64, marginBottom: 16 }}>✅</div>
            <h2 style={{ color: "#22c55e", margin: "0 0 8px" }}>Observation Saved</h2>
            <p style={{ color: "#8b949e" }}>Thank you. Your observation has been recorded for this session.</p>
            <button onClick={() => navigate("/dashboard")} style={{
              marginTop: 24, padding: "12px 32px", background: "#6366f1", color: "#fff",
              border: "none", borderRadius: 30, fontFamily: "Nunito", fontWeight: 800,
              fontSize: 16, cursor: "pointer",
            }}>Back to Dashboard</button>
          </div>
        ) : (
          <>
            {/* Instructions */}
            <div style={{
              background: "rgba(99,102,241,0.08)", border: "1px solid rgba(99,102,241,0.2)",
              borderRadius: 12, padding: "16px 20px", marginBottom: 28,
              fontSize: 14, color: "#a5b4fc", lineHeight: 1.5,
            }}>
              💡 Use the scale: <strong>0</strong> = Not observed, <strong>1</strong> = Slightly,{" "}
              <strong>2</strong> = Clearly, <strong>3</strong> = Strongly,{" "}
              <strong>"Unable"</strong> = You could not see this behaviour clearly.
              <br /><br />
              Do <strong>not</strong> see the AI's interpretation before submitting your own observations.
            </div>

            {/* Observation Items */}
            <div style={{ display: "flex", flexDirection: "column", gap: 16, marginBottom: 28 }}>
              {OBSERVATIONS.map(obs => (
                <div key={obs.key} style={{
                  background: "#161b22", border: "1px solid #30363d", borderRadius: 12, padding: "18px 20px",
                }}>
                  <div style={{ fontWeight: 700, fontSize: 15, marginBottom: 14, color: "#e6edf3" }}>
                    {obs.label}
                  </div>
                  <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                    {SCALE.map(s => (
                      <button key={s.val} onClick={() => setScore(obs.key, s.val)} style={{
                        padding: "8px 12px", borderRadius: 8, border: "1px solid",
                        borderColor: scores[obs.key] === s.val ? "#f5a623" : "#30363d",
                        background: scores[obs.key] === s.val ? "rgba(245,166,35,0.15)" : "#21262d",
                        color: scores[obs.key] === s.val ? "#f5a623" : "#8b949e",
                        fontSize: 13, fontWeight: 700, cursor: "pointer", transition: "all 0.15s",
                        fontFamily: "Nunito",
                        minHeight: 40,
                      }}>
                        {s.label}
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            {/* Notes */}
            <div style={{ marginBottom: 28 }}>
              <label style={{ display: "block", fontWeight: 700, marginBottom: 8, fontSize: 15 }}>
                Additional Notes (optional)
              </label>
              <textarea value={notes} onChange={e => setNotes(e.target.value)}
                placeholder="Any other observations about the child's behaviour, engagement, or approach..."
                rows={4}
                style={{
                  width: "100%", background: "#161b22", border: "1px solid #30363d",
                  borderRadius: 10, color: "#e6edf3", fontFamily: "Nunito",
                  fontSize: 15, padding: "14px 16px", resize: "vertical", outline: "none",
                  boxSizing: "border-box",
                }} />
            </div>

            {error && (
              <div style={{
                background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.3)",
                borderRadius: 10, padding: "12px 16px", marginBottom: 16,
                color: "#ef4444", fontSize: 14,
              }}>
                {error}
              </div>
            )}

            <button onClick={handleSubmit} disabled={submitting} style={{
              width: "100%", padding: "18px", background: "linear-gradient(135deg, #f5a623, #d4841a)",
              color: "#000", border: "none", borderRadius: 50, fontFamily: "Nunito",
              fontWeight: 900, fontSize: 18, cursor: submitting ? "not-allowed" : "pointer",
              opacity: submitting ? 0.6 : 1, transition: "all 0.2s",
            }}>
              {submitting ? "Saving..." : "Submit Observation ✓"}
            </button>
          </>
        )}
      </div>
    </div>
  );
}

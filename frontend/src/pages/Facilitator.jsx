import { useEffect, useState } from "react";
import { useParams, useSearchParams, useNavigate } from "react-router-dom";
import { api } from "../api";
import { DOMAINS } from "../data/questions";

export default function Facilitator() {
  const { sid } = useParams();
  const [params] = useSearchParams();
  const cid = params.get("cid");
  const navigate = useNavigate();

  const [session, setSession]   = useState(null);
  const [child, setChild]       = useState(null);
  const [saving, setSaving]     = useState(false);
  const [saved, setSaved]       = useState(false);
  const [form, setForm] = useState({
    facilitator: "", confirmed: 1,
    observation: "", override_domain: "", notes: "",
    agreement: "Agree",
    strengths_observed: "",
    concerns: "",
    suggested_workshop: "",
    obs_curiosity: 3,
    obs_confidence: 3,
    obs_focus: 3,
    obs_creativity: 3,
    obs_communication: 3,
    obs_leadership: 3,
    obs_persistence: 3,
    obs_emotional_regulation: 3
  });

  useEffect(() => {
    async function load() {
      // Validate the existing JWT session — never prompt for a second login
      try {
        await api.me();
      } catch (_) {
        navigate("/login");
        return;
      }
      const [s, c] = await Promise.all([api.getSession(sid), api.getChild(cid)]);
      setSession(s); setChild(c);
      setForm(f => ({ ...f, override_domain: s.top_domain || "" }));
    }
    load();
  }, [sid, cid]);

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }));

  const submit = async () => {
    if (!form.facilitator.trim()) return alert("Please enter your name.");
    setSaving(true);
    try {
      await api.addNote({
        session_id: parseInt(sid), child_id: parseInt(cid),
        ...form, confirmed: form.confirmed ? 1 : 0,
      });
      setSaved(true);
      const updated = await api.getSession(sid);
      setSession(updated);
    } finally { setSaving(false); }
  };

  if (!session) return <div style={{ textAlign:"center", marginTop:60, color:"#777" }}>Loading...</div>;

  const integ  = JSON.parse(session.integrated_score || "{}");
  const sorted = Object.entries(integ).sort((a, b) => b[1] - a[1]);
  const topD   = DOMAINS[session.top_domain];

  return (
    <div>
      <div className="page-header">
        <h1>Facilitator Review</h1>
        <p>Validate the system's output with your direct observation of {child?.name}.</p>
      </div>

      <div className="card section-card">
        <h2 className="card-title">System output for {child?.name}</h2>
        <div className="domain-panel" style={{ background: topD?.light || "#E6F1FB", marginBottom:20 }}>
          <span style={{ fontSize:36, lineHeight: 1 }}>{topD?.emoji}</span>
          <div>
            <div style={{ fontWeight:800, color: topD?.color, fontSize:18 }}>{topD?.label}</div>
            <div style={{ fontSize:13, color:"#666" }}>Top domain - integrated score: {integ[session.top_domain]}</div>
          </div>
        </div>

        {sorted.slice(0, 4).map(([domain, score]) => {
          const d = DOMAINS[domain];
          return (
            <div key={domain} className="score-row">
              <div className="score-row-header">
                <span>{d?.emoji} {d?.label}</span>
                <span style={{ fontWeight:700, color: d?.color }}>{score}</span>
              </div>
              <div className="score-bar-bg">
                <div className="score-bar-fill" style={{ width:`${score}%`, background: d?.color }} />
              </div>
            </div>
          );
        })}
      </div>

      {!saved ? (
        <div className="card">
          <h2 className="card-title">Mentor Validation Layer</h2>

          <div className="form-group">
            <label>Your Name (Mentor / Facilitator)</label>
            <input placeholder="e.g. Sunita Devi" value={form.facilitator} onChange={e => set("facilitator", e.target.value)} />
          </div>

          <div className="form-group">
            <label>Validation Decision</label>
            <div className="segmented-control" style={{ marginTop:6 }}>
              {["Agree", "Partially Agree", "Needs Review"]
                .map(opt => (
                  <button key={opt}
                    type="button"
                    className={`segment-button${form.agreement === opt ? " active" : ""}`}
                    onClick={() => {
                      set("agreement", opt);
                      set("confirmed", opt === "Needs Review" ? 0 : 1);
                    }}>
                    {opt}
                  </button>
                ))}
            </div>
          </div>

          <div className="form-group" style={{ marginBottom: "24px" }}>
            <label style={{ fontWeight: 800, color: "var(--text)", display: "block", marginBottom: "12px" }}>Facilitator Observation Ratings (1-5)</label>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "16px" }}>
              {[
                { key: "obs_curiosity", label: "Curiosity (जिज्ञासा)" },
                { key: "obs_confidence", label: "Confidence (आत्मविश्वास)" },
                { key: "obs_focus", label: "Focus (एकाग्रता)" },
                { key: "obs_creativity", label: "Creativity (रचनात्मकता)" },
                { key: "obs_communication", label: "Communication (संचार)" },
                { key: "obs_leadership", label: "Leadership (नेतृत्व)" },
                { key: "obs_persistence", label: "Persistence (दृढ़ता)" },
                { key: "obs_emotional_regulation", label: "Emotional Regulation (भावना नियंत्रण)" }
              ].map(indicator => (
                <div key={indicator.key} style={{ display: "flex", flexDirection: "column", gap: "6px", padding: "12px", background: "#f9fafb", borderRadius: "8px", border: "1px solid #e5e7eb" }}>
                  <span style={{ fontSize: "13.5px", fontWeight: 600, color: "#374151" }}>{indicator.label}</span>
                  <div style={{ display: "flex", gap: "4px" }}>
                    {[1, 2, 3, 4, 5].map(val => (
                      <button
                        key={val}
                        type="button"
                        onClick={() => set(indicator.key, val)}
                        style={{
                          flex: 1,
                          padding: "6px 0",
                          fontSize: "13px",
                          fontWeight: 700,
                          borderRadius: "6px",
                          border: "1px solid",
                          borderColor: form[indicator.key] === val ? "#5b4cf0" : "#d1d5db",
                          background: form[indicator.key] === val ? "#5b4cf0" : "#ffffff",
                          color: form[indicator.key] === val ? "#ffffff" : "#374151",
                          cursor: "pointer",
                          transition: "all 0.2s"
                        }}
                      >
                        {val}
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="form-group">
            <label>Override Domain (optional, if you disagree or partially agree)</label>
            <select value={form.override_domain} onChange={e => set("override_domain", e.target.value)}>
              {Object.entries(DOMAINS).map(([k, d]) => (
                <option key={k} value={k}>{d.emoji} {d.label}</option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>Strengths Observed</label>
            <textarea rows={3} placeholder="What notable strengths, talents, or abilities did you observe in this child directly during assessment tasks?"
              value={form.strengths_observed} onChange={e => {
                set("strengths_observed", e.target.value);
              }} />
          </div>

          <div className="form-group">
            <label>Concerns (Mental blockages, anxiety, or challenges)</label>
            <textarea rows={2} placeholder="Note any learning difficulties, performance anxiety, or contextual hurdles observed..."
              value={form.concerns} onChange={e => {
                set("concerns", e.target.value);
                set("notes", e.target.value);
              }} />
          </div>

          <div className="form-group">
            <label>Suggested Workshop Domain</label>
            <select value={form.suggested_workshop} onChange={e => set("suggested_workshop", e.target.value)}>
              <option value="">Select a workshop focus</option>
              {Object.entries(DOMAINS).map(([k, d]) => (
                <option key={k} value={k}>{d.emoji} {d.label} Workshop</option>
              ))}
            </select>
          </div>

          <button className="btn btn-primary btn-full" onClick={submit} disabled={saving}>
            {saving ? "Saving..." : "Save Facilitator Validation"}
          </button>
        </div>
      ) : (
        <div className="card text-center" style={{ background:"#E1F5EE", border:"none" }}>
          <div style={{ fontSize:40, marginBottom:8 }}>✓</div>
          <h2 style={{ color:"#0F6E56", marginBottom:8 }}>Validation saved</h2>
          <p style={{ color:"#555", marginBottom:20 }}>
            The facilitator note has been recorded alongside the system result.
          </p>
          <button className="btn btn-teal" onClick={() => navigate(`/mentor/${cid}?domain=${form.override_domain}&sid=${sid}`)}>
            Continue to Mentor Matching
          </button>
        </div>
      )}
    </div>
  );
}

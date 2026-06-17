import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";

const EXPOSURE_QUESTIONS = [
  { id: "q1", title: "Computers & Technology", desc: "Have you ever used a computer, a laptop, coding apps, or technology projects?" },
  { id: "q2", title: "Science Experiments", desc: "Have you ever done science experiments or science activities?" },
  { id: "q3", title: "Building & Making", desc: "Have you ever built something using blocks, cardboard, tools, kits, or recycled materials?" },
  { id: "q4", title: "Art & Design", desc: "Have you ever taken part in drawing, painting, craft, design, or creative art activities?" },
  { id: "q5", title: "Music, Dance & Performance", desc: "Have you ever performed, danced, acted, sung, or played music in front of others?" },
  { id: "q6", title: "Public Speaking", desc: "Have you ever spoken in front of a group, class, audience, or on stage?" },
  { id: "q7", title: "Leadership Activities", desc: "Have you ever been chosen to lead a team, group, activity, class task, or event?" },
  { id: "q8", title: "Sports & Physical Training", desc: "Have you ever received coaching, training, or participated in sports competitions?" },
  { id: "q9", title: "Nature & Environment", desc: "Have you ever cared for plants, animals, gardens, or taken part in nature activities?" },
  { id: "q10", title: "Business & Money Activities", desc: "Have you ever helped sell something, manage money, run a stall, or help in a family business?" },
  { id: "q11", title: "Reading & Writing", desc: "Have you ever regularly read books, written stories, journals, poems, or articles?" },
  { id: "q12", title: "Competitions & Events", desc: "Have you ever participated in competitions, exhibitions, tournaments, talent shows, or contests?" }
];

export default function Intake() {
  const navigate = useNavigate();
  const [saving, setSaving] = useState(false);
  const [centers, setCenters] = useState([]);
  const [form, setForm] = useState({
    name: "", age: "", language: "Hindi", school_year: "", gender: "", center_id: "",
    exposure_data: {
      q1: 0, q2: 0, q3: 0, q4: 0, q5: 0, q6: 0, q7: 0, q8: 0, q9: 0, q10: 0, q11: 0, q12: 0
    }
  });

  useEffect(() => {
    api.getPublicCenters()
      .then(setCenters)
      .catch(() => {
        setCenters([
          { id: 1, name: "Khadar Centre" },
          { id: 2, name: "Okhla Centre" },
          { id: 3, name: "Govindpuri Centre" },
          { id: 4, name: "Yamuna Centre" }
        ]);
      });
  }, []);

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }));

  const submit = async () => {
    if (!form.name.trim() || !form.age || !form.center_id) {
      return alert("Please fill in name, age, and select a center.");
    }
    setSaving(true);

    const q = form.exposure_data;
    // Map 12 questions (0-4 scale) to the 8 legacy fields (0-3 scale) for database backward compatibility
    const legacy_exp = {
      exp_logical: Math.min(3, Math.round(((q.q1 + q.q2) / 2) * (3/4))),
      exp_spatial: Math.min(3, Math.round(((q.q3 + q.q1) / 2) * (3/4))),
      exp_creative: Math.min(3, Math.round(((q.q4 + q.q5) / 2) * (3/4))),
      exp_kinesthetic: Math.min(3, Math.round(((q.q8 + q.q5) / 2) * (3/4))),
      exp_language: Math.min(3, Math.round(((q.q11 + q.q6) / 2) * (3/4))),
      exp_social: Math.min(3, Math.round(((q.q7 + q.q6) / 2) * (3/4))),
      exp_naturalist: Math.min(3, Math.round((q.q9) * (3/4))),
      exp_intrapersonal: Math.min(3, Math.round(((q.q11 + q.q12) / 2) * (3/4)))
    };

    try {
      const child = await api.createChild({ 
        ...form, 
        ...legacy_exp,
        age: parseInt(form.age),
        center_id: parseInt(form.center_id)
      });
      const session = await api.createSession(child.id);
      navigate(`/discovery/${session.id}?cid=${child.id}`);
    } catch (e) {
      alert("Could not connect to backend. Make sure the server is running.");
    } finally { setSaving(false); }
  };

  const isYounger = form.school_year === "Class 4" || form.school_year === "Class 5" || form.school_year === "Class 6" || (form.age && parseInt(form.age) <= 12);
  const currentScale = isYounger
    ? ["Never", "Heard Of It", "Tried It", "Sometimes", "Many Times"]
    : ["Never Seen It", "Heard About It", "Tried Once", "Sometimes", "Regularly"];

  return (
    <div>
      <div className="page-header">
        <h1>About You</h1>
        <p>First, let's get a few details. This helps us understand your background.</p>
      </div>

      <div className="card section-card">
        <h2 className="card-title">Basic information</h2>

        <div className="form-row">
          <div className="form-group">
            <label>Full name</label>
            <input placeholder="e.g. Aarav Singh" value={form.name} onChange={e => set("name", e.target.value)} />
          </div>
          <div className="form-group">
            <label>Age</label>
            <input type="number" min={8} max={18} placeholder="8-18" value={form.age} onChange={e => set("age", e.target.value)} />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Preferred language</label>
            <select value={form.language} onChange={e => set("language", e.target.value)}>
              {["Hindi","Urdu","Bengali","Tamil","Telugu","Marathi","Punjabi","English","Other"].map(l =>
                <option key={l}>{l}</option>
              )}
            </select>
          </div>
          <div className="form-group">
            <label>Gender (optional)</label>
            <select value={form.gender} onChange={e => set("gender", e.target.value)}>
              <option value="">Prefer not to say</option>
              <option>Girl</option><option>Boy</option><option>Other</option>
            </select>
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>School class</label>
            <select value={form.school_year} onChange={e => set("school_year", e.target.value)}>
              <option value="">Select class</option>
              {["Class 4","Class 5","Class 6","Class 7","Class 8","Class 9","Class 10","Class 11","Class 12","Not in school"].map(c =>
                <option key={c}>{c}</option>
              )}
            </select>
          </div>
          <div className="form-group">
            <label>Centre Name</label>
            <select value={form.center_id} onChange={e => set("center_id", e.target.value)} required>
              <option value="">Select centre</option>
              {centers.map(c =>
                <option key={c.id} value={c.id}>{c.name}</option>
              )}
            </select>
          </div>
        </div>
      </div>

      <div className="card section-card">
        <h2 className="card-title-tight">Environmental Exposure & Opportunity Access</h2>
        <p className="muted-copy" style={{ marginBottom: "20px" }}>
          For each area below, tell us how much you have done it before — not how good you are, just how often you've had access or opportunity.
        </p>

        <div className="exposure-list" style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
          {EXPOSURE_QUESTIONS.map((q, idx) => (
            <div key={q.id} className="exposure-row" style={{ display: "flex", flexDirection: "column", gap: "10px", padding: "16px", background: "#f9fafb", borderRadius: "12px", border: "1px solid #e5e7eb" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
                <span style={{ fontSize: "11px", fontWeight: 800, textTransform: "uppercase", color: "#6b7280" }}>Exposure Question {idx + 1} of 12</span>
                <span style={{ fontSize: "11px", fontWeight: 800, color: "#5b4cf0", textTransform: "uppercase" }}>Opportunity Access</span>
              </div>
              <div>
                <div style={{ fontWeight: 800, fontSize: "16px", color: "#1e1b4b" }}>{q.title}</div>
                <div style={{ fontSize: "13.5px", color: "#4b5563", marginTop: "4px", lineHeight: "1.5" }}>{q.desc}</div>
              </div>
              <div className="segmented-control" style={{ display: "flex", gap: "6px", flexWrap: "wrap", marginTop: "8px" }}>
                {currentScale.map((lbl, i) => (
                  <button
                    key={i}
                    className={`segment-button${form.exposure_data[q.id] === i ? " active" : ""}`}
                    onClick={() => {
                      const newExp = { ...form.exposure_data, [q.id]: i };
                      setForm(f => ({ ...f, exposure_data: newExp }));
                    }}
                    type="button"
                    style={{ flex: "1 1 auto", padding: "8px 12px", fontSize: "13px", fontWeight: 600 }}
                  >
                    {lbl}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      <button className="btn btn-primary btn-lg btn-full" onClick={submit} disabled={saving}>
        {saving ? "Saving..." : "Start Assessment"}
      </button>
    </div>
  );
}

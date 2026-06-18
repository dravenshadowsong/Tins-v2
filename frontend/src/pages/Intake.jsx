import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";

const EXPOSURE_QUESTIONS = [
  { id: "exp_language", title: "Language & Communication", desc: "Have you ever spoken or performed on a stage in front of a group?", desc_hi: "क्या आपने कभी किसी समूह के सामने मंच पर बात की है या कोई प्रस्तुति दी है?" },
  { id: "exp_creative", title: "Creative & Artistic", desc: "Have you ever made art, crafts, or creative projects?", desc_hi: "क्या आपने कभी कला, शिल्प (क्राफ्ट) या कोई रचनात्मक चीज़ बनाई है?" },
  { id: "exp_logical", title: "Logical & Analytical", desc: "Have you ever solved riddles, code puzzles, or math games?", desc_hi: "क्या आपने कभी पहेलियाँ, कोड पहेलियाँ या गणित के खेल हल किए हैं?" },
  { id: "exp_social", title: "Social & Leadership", desc: "Have you ever led a team, group, or classroom activity?", desc_hi: "क्या आपने कभी किसी टीम, समूह या कक्षा की गतिविधि का नेतृत्व किया है?" },
  { id: "exp_spatial", title: "Spatial & Making", desc: "Have you ever built models with blocks, cardboard, or toys?", desc_hi: "क्या आपने कभी ब्लॉक, गत्ते या खिलौनों से मॉडल बनाए हैं?" },
  { id: "exp_kinesthetic", title: "Kinesthetic & Physical", desc: "Have you ever participated in running games, sports, or dance?", desc_hi: "क्या आपने कभी दौड़ने वाले खेलों, खेलकूद या नृत्य में भाग लिया है?" },
  { id: "exp_naturalist", title: "Naturalist & Environmental", desc: "Have you ever sowed seeds, watered gardens, or cared for animals?", desc_hi: "क्या आपने कभी बीज बोए हैं, बगीचे में पानी दिया है या जानवरों की देखभाल की है?" },
  { id: "exp_intrapersonal", title: "Intrapersonal & Reflective", desc: "Have you ever set personal goals or written in a diary?", desc_hi: "क्या आपने कभी अपने लिए लक्ष्य तय किए हैं या डायरी में लिखा है?" }
];

export default function Intake() {
  const navigate = useNavigate();
  const [saving, setSaving] = useState(false);
  const [centers, setCenters] = useState([]);
  const [form, setForm] = useState({
    name: "", age: "", language: "Hindi", school_year: "", gender: "", center_id: "",
    exposure_data: {
      exp_language: 0,
      exp_creative: 0,
      exp_logical: 0,
      exp_spatial: 0,
      exp_kinesthetic: 0,
      exp_naturalist: 0,
      exp_social: 0,
      exp_intrapersonal: 0
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

    try {
      const child = await api.createChild({ 
        ...form, 
        exp_language: q.exp_language,
        exp_creative: q.exp_creative,
        exp_logical: q.exp_logical,
        exp_spatial: q.exp_spatial,
        exp_kinesthetic: q.exp_kinesthetic,
        exp_naturalist: q.exp_naturalist,
        exp_social: q.exp_social,
        exp_intrapersonal: q.exp_intrapersonal,
        age: parseInt(form.age),
        center_id: parseInt(form.center_id)
      });
      const session = await api.createSession(child.id);
      navigate(`/discovery/${session.id}?cid=${child.id}`);
    } catch (e) {
      alert("Could not connect to backend. Make sure the server is running.");
    } finally { setSaving(false); }
  };

  const currentScale = ["Never", "Once", "A Few Times", "Many Times"];

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
                <span style={{ fontSize: "11px", fontWeight: 800, textTransform: "uppercase", color: "#6b7280" }}>Exposure Question {idx + 1} of 8</span>
                <span style={{ fontSize: "11px", fontWeight: 800, color: "#5b4cf0", textTransform: "uppercase" }}>Opportunity Access</span>
              </div>
              <div>
                <div style={{ fontWeight: 800, fontSize: "16px", color: "#1e1b4b" }}>{q.title}</div>
                <div style={{ fontSize: "13.5px", color: "#4b5563", marginTop: "4px", lineHeight: "1.5" }}>{q.desc}</div>
                <div style={{ fontSize: "13.5px", color: "#4b5563", marginTop: "2px", lineHeight: "1.5", fontStyle: "italic" }}>{q.desc_hi}</div>
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

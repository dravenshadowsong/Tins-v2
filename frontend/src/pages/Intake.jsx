import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";

const EXPOSURE_QUESTIONS = [
  { id: "lang_1", title: "Speaking & Stage", desc: "Have you ever spoken or performed on a stage in front of a group?" },
  { id: "lang_2", title: "Storytelling to Kids", desc: "Have you ever told stories or read books aloud to younger children?" },
  { id: "lang_3", title: "Speech Competitions", desc: "Have you ever participated in a speech, debate, or poetry competition?" },
  
  { id: "creative_1", title: "Drawing & Art", desc: "Have you ever drawn, painted, or sketched pictures in your free time?" },
  { id: "creative_2", title: "Music & Dance", desc: "Have you ever sung, danced, hummed, or played music for others?" },
  { id: "creative_3", title: "Creative Drama", desc: "Have you ever made up a play, script, or song for friends to watch?" },
  
  { id: "logical_1", title: "Math Puzzles", desc: "Have you ever solved math riddles, puzzles, or board games?" },
  { id: "logical_2", title: "Strategy Games", desc: "Have you ever played strategy games or worked with calculators/apps?" },
  { id: "logical_3", title: "Patterns & Magic", desc: "Have you ever tried to understand how magic tricks or patterns work?" },
  
  { id: "spatial_1", title: "Blocks & Making", desc: "Have you ever built models with blocks, cardboard, or construction kits?" },
  { id: "spatial_2", title: "3D Art & Folding", desc: "Have you ever sketched 3D shapes, drew maps, or folded origami?" },
  { id: "spatial_3", title: "Fixing Things", desc: "Have you ever taken toys or sharpeners apart to fix them?" },
  
  { id: "kinesthetic_1", title: "Sports & Tag", desc: "Have you ever participated in physical sports or playground tag?" },
  { id: "kinesthetic_2", title: "Active Moves", desc: "Have you ever practiced dance steps, karate, gymnastics, or yoga?" },
  { id: "kinesthetic_3", title: "Balance Games", desc: "Have you ever played balance or target throwing games?" },
  
  { id: "naturalist_1", title: "Gardening & Seeds", desc: "Have you ever sowed seeds, watered gardens, or cared for house plants?" },
  { id: "naturalist_2", title: "Observing Animals", desc: "Have you ever watched animal tracks, insects, or birds outdoors?" },
  { id: "naturalist_3", title: "Nature Collections", desc: "Have you ever collected and sorted rocks, leaves, or feathers by pattern?" },
  
  { id: "social_1", title: "Leading Groups", desc: "Have you ever led school teams, projects, or classroom cleanliness activities?" },
  { id: "social_2", title: "Settling Arguments", desc: "Have you ever helped classmates settle a loud dispute or playground argument?" },
  { id: "social_3", title: "Helping Events", desc: "Have you ever welcomed new students or organized center activities?" },
  
  { id: "intrapersonal_1", title: "Planning Routines", desc: "Have you ever planned studying or practice routines and tracked progress?" },
  { id: "intrapersonal_2", title: "Writing Journals", desc: "Have you ever logged thoughts, journals, or daily reflection lists?" },
  { id: "intrapersonal_3", title: "Quiet Reflection", desc: "Have you ever spent quiet time thinking about personal strengths and weaknesses?" }
];

export default function Intake() {
  const navigate = useNavigate();
  const [saving, setSaving] = useState(false);
  const [centers, setCenters] = useState([]);
  const [form, setForm] = useState({
    name: "", age: "", language: "Hindi", school_year: "", gender: "", center_id: "",
    exposure_data: {
      lang_1: 0, lang_2: 0, lang_3: 0,
      creative_1: 0, creative_2: 0, creative_3: 0,
      logical_1: 0, logical_2: 0, logical_3: 0,
      spatial_1: 0, spatial_2: 0, spatial_3: 0,
      kinesthetic_1: 0, kinesthetic_2: 0, kinesthetic_3: 0,
      naturalist_1: 0, naturalist_2: 0, naturalist_3: 0,
      social_1: 0, social_2: 0, social_3: 0,
      intrapersonal_1: 0, intrapersonal_2: 0, intrapersonal_3: 0
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
    // Map the 24 V4 questions (0-3 scale) directly to the 8 legacy fields for database compatibility
    const legacy_exp = {
      exp_language: Math.min(3, Math.round((q.lang_1 + q.lang_2 + q.lang_3) / 3)),
      exp_creative: Math.min(3, Math.round((q.creative_1 + q.creative_2 + q.creative_3) / 3)),
      exp_logical: Math.min(3, Math.round((q.logical_1 + q.logical_2 + q.logical_3) / 3)),
      exp_spatial: Math.min(3, Math.round((q.spatial_1 + q.spatial_2 + q.spatial_3) / 3)),
      exp_kinesthetic: Math.min(3, Math.round((q.kinesthetic_1 + q.kinesthetic_2 + q.kinesthetic_3) / 3)),
      exp_naturalist: Math.min(3, Math.round((q.naturalist_1 + q.naturalist_2 + q.naturalist_3) / 3)),
      exp_social: Math.min(3, Math.round((q.social_1 + q.social_2 + q.social_3) / 3)),
      exp_intrapersonal: Math.min(3, Math.round((q.intrapersonal_1 + q.intrapersonal_2 + q.intrapersonal_3) / 3))
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

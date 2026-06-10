import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";

const DOMAINS = ["kinesthetic","creative","logical","spatial","social","language","naturalist","intrapersonal"];
const DOMAIN_LABELS = {
  kinesthetic:"Sports / Dance / Movement", creative:"Drawing / Music / Art",
  logical:"Maths / Puzzles", spatial:"Building / Making things",
  social:"Leading / Helping others", language:"Talking / Storytelling",
  naturalist:"Nature / Animals / Plants", intrapersonal:"Thinking deeply / Writing"
};
const EXP_LABELS = ["Never tried it", "Tried a few times", "Do it sometimes", "Do it regularly"];

export default function Intake() {
  const navigate = useNavigate();
  const [saving, setSaving] = useState(false);
  const [centers, setCenters] = useState([]);
  const [form, setForm] = useState({
    name: "", age: "", language: "Hindi", school_year: "", gender: "", center_id: "",
    exp_kinesthetic:0, exp_creative:0, exp_logical:0, exp_spatial:0,
    exp_social:0, exp_language:0, exp_naturalist:0, exp_intrapersonal:0,
  });

  useEffect(() => {
    api.getPublicCenters()
      .then(setCenters)
      .catch(() => {
        // Fallback to hardcoded centers if API is offline or not found
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
    try {
      const child = await api.createChild({ 
        ...form, 
        age: parseInt(form.age),
        center_id: parseInt(form.center_id)
      });
      const session = await api.createSession(child.id);
      navigate(`/discovery/${session.id}?cid=${child.id}`);
    } catch (e) {
      alert("Could not connect to backend. Make sure the server is running.");
    } finally { setSaving(false); }
  };

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
            <input type="number" min={9} max={15} placeholder="9-15" value={form.age} onChange={e => set("age", e.target.value)} />
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
              {["Class 4","Class 5","Class 6","Class 7","Class 8","Class 9","Class 10","Not in school"].map(c =>
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
        <h2 className="card-title-tight">Your exposure</h2>
        <p className="muted-copy">
          For each area below, tell us how much you have done it before - not how good you are, just how often.
        </p>

        <div className="exposure-list">
          {DOMAINS.map(d => (
            <div key={d} className="exposure-row">
              <div className="exposure-label">{DOMAIN_LABELS[d]}</div>
              <div className="segmented-control">
                {EXP_LABELS.map((lbl, i) => (
                  <button
                    key={i}
                    className={`segment-button${form[`exp_${d}`] === i ? " active" : ""}`}
                    onClick={() => set(`exp_${d}`, i)}
                    type="button"
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

import { useEffect, useState } from "react";
import { useParams, useSearchParams, useNavigate } from "react-router-dom";
import { api } from "../api";
import { DOMAINS } from "../data/questions";

const spinStyle = {
  display: "inline-block",
  animation: "mentorSpin 0.8s linear infinite",
  marginRight: 6,
  fontSize: 18,
  lineHeight: 1,
};

const spinKeyframes = `
@keyframes mentorSpin {
  from { transform: rotate(0deg); }
  to   { transform: rotate(360deg); }
}
`;

export default function MentorMatch() {
  const { cid } = useParams();
  const [params] = useSearchParams();
  const domain   = params.get("domain") || "";
  const sid      = params.get("sid");
  const navigate = useNavigate();

  const [mentors,  setMentors]  = useState([]);
  const [child,    setChild]    = useState(null);
  const [matches,  setMatches]  = useState([]);
  const [selected, setSelected] = useState(null);
  const [matching, setMatching] = useState(false);
  const [done,     setDone]     = useState(false);
  const [matchData, setMatchData] = useState(null);

  useEffect(() => {
    async function load() {
      const [c, ms, mx] = await Promise.all([
        api.getChild(cid),
        api.getMentors(domain),
        api.childMatches(cid),
      ]);
      setChild(c); setMentors(ms); setMatches(mx);
      if (mx.length > 0) { setDone(true); setMatchData(mx[0]); }
    }
    load();
  }, [cid, domain]);

  const doMatch = async () => {
    if (!selected) return;
    setMatching(true);
    try {
      const result = await api.createMatch({ child_id: parseInt(cid), mentor_id: selected, domain });
      setDone(true);
      setMatchData({ ...mentors.find(m => m.id === selected), plan: result.plan });
    } finally { setMatching(false); }
  };

  const domainInfo = DOMAINS[domain];

  return (
    <div>
      <style>{spinKeyframes}</style>
      <div className="page-header">
        <h1>Mentor Matching</h1>
        <p>Connect {child?.name} with a mentor in their top talent domain.</p>
      </div>

      <div className="card section-card" style={{ background: domainInfo?.light || "#E6F1FB", border:"none" }}>
        <div className="domain-panel" style={{ padding: 0 }}>
          <span style={{ fontSize:40, lineHeight: 1 }}>{domainInfo?.emoji}</span>
          <div>
            <div style={{ fontWeight:800, fontSize:18, color: domainInfo?.color }}>{domainInfo?.label}</div>
            <div style={{ fontSize:13, color:"#666" }}>Top talent domain for {child?.name}</div>
          </div>
        </div>
      </div>

      {!done ? (
        <>
          <div className="card section-card">
            <h2 className="card-title">Available mentors in {domainInfo?.label}</h2>
            {mentors.length === 0 ? (
              <p style={{ color:"#777" }}>No mentors registered in this domain yet. Add mentors via the dashboard.</p>
            ) : (
              <div className="button-stack" style={{ gap:10 }}>
                {mentors.map(m => (
                  <div key={m.id}
                    onClick={() => setSelected(m.id)}
                    className={`mentor-card${selected === m.id ? " selected" : ""}`}
                    style={{
                      borderColor: selected === m.id ? domainInfo?.color : undefined,
                      background: selected === m.id ? (domainInfo?.light || "#E6F1FB") : undefined,
                    }}>
                    <div style={{ fontWeight:700, marginBottom:4 }}>{m.name}</div>
                    <div style={{ fontSize:13, color:"#666", marginBottom:4 }}>{m.bio}</div>
                    <div style={{ fontSize:12, color:"#999" }}>{m.contact}</div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <button
            className="btn btn-teal btn-lg btn-full"
            onClick={doMatch}
            disabled={!selected || matching}
          >
            {matching ? (
              <span style={{ display: "flex", alignItems: "center", justifyContent: "center" }}>
                <span style={spinStyle}>↻</span>
                Creating match...
              </span>
            ) : "Confirm Mentor Match"}
          </button>
        </>
      ) : (
        <>
          <div className="card text-center section-card" style={{ background:"#E1F5EE", border:"none" }}>
            <div style={{ fontSize:40, marginBottom:8 }}>🤝</div>
            <h2 style={{ color:"#0F6E56", marginBottom:4 }}>Match confirmed!</h2>
            <p style={{ color:"#555" }}>
              {child?.name} has been matched with <strong>{matchData?.mentor_name || matchData?.name}</strong>
            </p>
          </div>

          <div className="card section-card">
            <h2 className="card-title-tight">6-month nurturing plan</h2>
            <p className="muted-copy">
              Three key milestones. Facilitator marks these off as they are completed.
            </p>
            {(matchData?.plan || []).map((milestone, i) => (
              <div key={i} className="milestone-row">
                <div className="milestone-badge" style={{
                  background: domainInfo?.light,
                  color: domainInfo?.color,
                }}>
                  {milestone.month}
                </div>
                <div>
                  <div style={{ fontWeight:600, fontSize:14, marginBottom:2 }}>Month {milestone.month}</div>
                  <div style={{ fontSize:14, color:"#444" }}>{milestone.title}</div>
                </div>
                <span className="status-pill" style={{
                  background: milestone.done ? "#E1F5EE" : "#F5F5F5",
                  color: milestone.done ? "#0F6E56" : "#999",
                }}>
                  {milestone.done ? "Done" : "Pending"}
                </span>
              </div>
            ))}
          </div>

          <div className="button-stack" style={{ gap:10 }}>
            <button className="btn btn-primary btn-full" onClick={() => navigate("/dashboard")}>
              View Dashboard
            </button>
            <button className="btn btn-ghost btn-full" onClick={() => navigate("/")}>
              Start new assessment
            </button>
          </div>
        </>
      )}
    </div>
  );
}

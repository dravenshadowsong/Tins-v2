import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

const BASE = import.meta.env.DEV ? "/api" : (import.meta.env.VITE_API_URL || "https://tins-v2-1.onrender.com/api");

const CONFIDENCE_COLOR = { high: "#22c55e", moderate: "#f5a623", low: "#ef4444" };
const RUBRIC_LABEL = { 0: "No evidence", 1: "Emerging", 2: "Developing", 3: "Strong", 4: "Exceptional" };

function BehaviourBar({ label, value, max = 3 }) {
  const pct = (value / max) * 100;
  return (
    <div style={{ marginBottom: 10 }}>
      <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13, marginBottom: 4 }}>
        <span style={{ color: "#8b949e" }}>{label}</span>
        <span style={{ fontWeight: 700, color: "#f5a623" }}>{value.toFixed(2)}</span>
      </div>
      <div style={{ height: 8, background: "#21262d", borderRadius: 4, overflow: "hidden" }}>
        <div style={{ width: `${pct}%`, height: "100%", background: "linear-gradient(90deg, #6366f1, #f5a623)", borderRadius: 4, transition: "width 0.5s ease" }} />
      </div>
    </div>
  );
}

function EventTimeline({ events }) {
  if (!events?.length) return <p style={{ color: "#6e7681", fontSize: 13 }}>No events recorded.</p>;
  return (
    <div style={{ maxHeight: 300, overflowY: "auto", fontSize: 12, fontFamily: "monospace" }}>
      {events.map((ev, i) => (
        <div key={i} style={{
          padding: "4px 0", borderBottom: "1px solid #21262d", display: "flex", gap: 12, alignItems: "flex-start"
        }}>
          <span style={{ color: "#6e7681", minWidth: 30 }}>R{ev.round_id}</span>
          <span style={{ color: "#6366f1", minWidth: 160 }}>{ev.event_type}</span>
          <span style={{ color: "#8b949e" }}>
            {typeof ev.event_data === "object" ? JSON.stringify(ev.event_data).slice(0, 80) : ev.event_data}
          </span>
        </div>
      ))}
    </div>
  );
}

function ResponseCard({ resp, analysis }) {
  const [expanded, setExpanded] = useState(false);
  const be = analysis?.behaviour_evidence;
  const beObj = typeof be === "string" ? (() => { try { return JSON.parse(be); } catch { return {}; } })() : (be || {});
  return (
    <div style={{ background: "#161b22", border: "1px solid #30363d", borderRadius: 12, padding: "14px 16px", marginBottom: 10 }}>
      <div style={{ display: "flex", gap: 12, alignItems: "flex-start", marginBottom: 8 }}>
        <span style={{
          padding: "3px 10px", borderRadius: 20, fontSize: 11, fontWeight: 800,
          background: resp.input_type === "draw" ? "#21262d" : resp.input_type === "voice" ? "rgba(99,102,241,0.15)" : "rgba(245,166,35,0.1)",
          color: resp.input_type === "draw" ? "#8b949e" : resp.input_type === "voice" ? "#6366f1" : "#f5a623",
          border: "1px solid #30363d", textTransform: "uppercase",
        }}>
          R{resp.round_id} · {resp.input_type}
        </span>
        {analysis?.evidence_quality && (
          <span style={{ fontSize: 11, fontWeight: 700, color: CONFIDENCE_COLOR[analysis.evidence_quality] || "#8b949e", padding: "3px 10px", background: "rgba(0,0,0,0.3)", borderRadius: 20 }}>
            {analysis.evidence_quality} evidence
          </span>
        )}
      </div>

      {resp.drawing_url ? (
        <img src={resp.drawing_url} alt="drawing" style={{ maxWidth: 240, borderRadius: 8, border: "1px solid #30363d" }} />
      ) : (
        <div style={{ fontSize: 15, color: "#e6edf3", lineHeight: 1.5, marginBottom: 8 }}>
          {resp.text_content || resp.voice_transcript || <em style={{ color: "#6e7681" }}>No text content</em>}
        </div>
      )}

      {analysis && (
        <>
          <button onClick={() => setExpanded(e => !e)} style={{
            background: "none", border: "1px solid #30363d", color: "#8b949e", borderRadius: 8,
            padding: "4px 12px", fontSize: 12, cursor: "pointer", fontFamily: "Nunito",
          }}>
            {expanded ? "▲ Hide AI analysis" : "▼ Show AI analysis"}
          </button>
          {expanded && (
            <div style={{ marginTop: 12, padding: "12px", background: "#0d1117", borderRadius: 10, border: "1px solid #21262d" }}>
              <div style={{ fontSize: 11, fontWeight: 800, color: "#6366f1", textTransform: "uppercase", letterSpacing: 1, marginBottom: 8 }}>
                AI Behaviour Evidence (O1–O6)
              </div>
              <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 8 }}>
                {["o1","o2","o3","o4","o5","o6"].map(k => (
                  <div key={k} style={{
                    padding: "4px 12px", borderRadius: 20, fontSize: 12, fontWeight: 700,
                    background: "rgba(99,102,241,0.1)", color: "#a5b4fc", border: "1px solid rgba(99,102,241,0.2)",
                  }}>
                    {k.toUpperCase()}: {beObj[k] ?? "—"}
                  </div>
                ))}
              </div>
              {analysis.reasoning && (
                <div style={{ fontSize: 13, color: "#8b949e", fontStyle: "italic" }}>"{analysis.reasoning}"</div>
              )}
              <div style={{ fontSize: 11, color: "#6e7681", marginTop: 6 }}>Model: {analysis.model_version || "—"}</div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

function SessionDetailView({ session, onBack }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState(null);

  useEffect(() => {
    const token = sessionStorage.getItem("goat_token");
    fetch(`${BASE}/invent-it/admin/sessions/${session.session_uuid}/research`, {
      headers: { ...(token ? { Authorization: `Bearer ${token}` } : {}) },
    })
      .then(r => r.ok ? r.json() : Promise.reject(r.status))
      .then(d => { setData(d); setLoading(false); })
      .catch(e => { setErr(`Error ${e}`); setLoading(false); });
  }, [session.session_uuid]);

  if (loading) return (
    <div style={{ padding: 40, textAlign: "center" }}>
      <div style={{ width: 40, height: 40, border: "3px solid #30363d", borderTopColor: "#f5a623", borderRadius: "50%", animation: "spin 0.8s linear infinite", margin: "0 auto 12px" }} />
      Loading research data…
    </div>
  );
  if (err) return <div style={{ color: "#ef4444", padding: 20 }}>{err}</div>;
  if (!data) return null;

  const { session: s, responses, events, ai_analysis, behaviour_evidence: be, facilitator_observations, child } = data;
  const analysisMap = Object.fromEntries((ai_analysis || []).map(a => [a.response_id, a]));
  const crossRound = typeof be?.cross_round_analysis === "string"
    ? (() => { try { return JSON.parse(be.cross_round_analysis); } catch { return {}; } })()
    : (be?.cross_round_analysis || {});

  return (
    <div>
      <button onClick={onBack} style={{
        background: "#21262d", border: "1px solid #30363d", color: "#8b949e",
        borderRadius: 8, padding: "8px 16px", cursor: "pointer", fontFamily: "Nunito",
        fontWeight: 700, fontSize: 13, marginBottom: 24,
      }}>← Back to Sessions</button>

      {/* Session Header */}
      <div style={{ background: "#161b22", borderRadius: 16, padding: "20px 24px", marginBottom: 20, border: "1px solid #30363d" }}>
        <div style={{ display: "flex", gap: 12, flexWrap: "wrap", marginBottom: 12 }}>
          <span style={{ fontWeight: 900, fontSize: 18 }}>Session: {s.session_uuid?.slice(0,18)}…</span>
          <span style={{
            padding: "3px 12px", borderRadius: 20, fontSize: 12, fontWeight: 800,
            background: s.status === "complete" ? "rgba(34,197,94,0.1)" : "rgba(245,166,35,0.1)",
            color: s.status === "complete" ? "#22c55e" : "#f5a623",
            border: `1px solid ${s.status === "complete" ? "rgba(34,197,94,0.3)" : "rgba(245,166,35,0.3)"}`,
          }}>{s.status}</span>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))", gap: 12, fontSize: 13 }}>
          {child?.name && <div><span style={{ color: "#6e7681" }}>Child: </span><strong>{child.name}</strong></div>}
          {child?.age && <div><span style={{ color: "#6e7681" }}>Age: </span><strong>{child.age}</strong></div>}
          {child?.school_year && <div><span style={{ color: "#6e7681" }}>Class: </span><strong>{child.school_year}</strong></div>}
          <div><span style={{ color: "#6e7681" }}>Language: </span><strong>{s.language?.toUpperCase()}</strong></div>
          <div><span style={{ color: "#6e7681" }}>Total Ideas: </span><strong>{s.number_of_ideas}</strong></div>
          <div><span style={{ color: "#6e7681" }}>Hints: </span><strong>{s.hint_count}</strong></div>
          <div><span style={{ color: "#6e7681" }}>Duration: </span><strong>{s.total_duration_ms ? `${Math.round(s.total_duration_ms/1000)}s` : "—"}</strong></div>
          <div><span style={{ color: "#6e7681" }}>First Response: </span><strong>{s.time_to_first_response_ms ? `${Math.round(s.time_to_first_response_ms/1000)}s` : "—"}</strong></div>
          <div><span style={{ color: "#6e7681" }}>Draws: </span><strong>{s.number_of_drawings}</strong></div>
          <div><span style={{ color: "#6e7681" }}>Voice: </span><strong>{s.number_of_voice_responses}</strong></div>
          <div><span style={{ color: "#6e7681" }}>Text: </span><strong>{s.number_of_text_responses}</strong></div>
        </div>
      </div>

      {/* Behaviour Evidence */}
      {be && Object.keys(be).length > 0 && (
        <div style={{ background: "#161b22", borderRadius: 16, padding: "20px 24px", marginBottom: 20, border: "1px solid #30363d" }}>
          <h3 style={{ margin: "0 0 16px", fontSize: 16, fontWeight: 800 }}>
            📊 Provisional Behaviour Evidence
            <span style={{ marginLeft: 10, fontSize: 11, fontWeight: 600, color: "#6e7681" }}>[PROTOTYPE — Not Validated]</span>
          </h3>
          <div style={{ display: "flex", gap: 16, marginBottom: 20, flexWrap: "wrap" }}>
            <div style={{
              padding: "12px 20px", background: "#0d1117", borderRadius: 12,
              border: `1px solid ${CONFIDENCE_COLOR[be.evidence_confidence] || "#30363d"}`,
              textAlign: "center",
            }}>
              <div style={{ fontSize: 11, color: "#6e7681", marginBottom: 4 }}>PROVISIONAL RUBRIC</div>
              <div style={{ fontSize: 32, fontWeight: 900, color: "#f5a623" }}>{be.provisional_rubric_score ?? "—"}</div>
              <div style={{ fontSize: 12, color: "#8b949e" }}>{RUBRIC_LABEL[be.provisional_rubric_score] || "—"}</div>
            </div>
            <div style={{
              padding: "12px 20px", background: "#0d1117", borderRadius: 12,
              border: `1px solid ${CONFIDENCE_COLOR[be.evidence_confidence] || "#30363d"}`,
              textAlign: "center",
            }}>
              <div style={{ fontSize: 11, color: "#6e7681", marginBottom: 4 }}>EVIDENCE CONFIDENCE</div>
              <div style={{ fontSize: 24, fontWeight: 900, color: CONFIDENCE_COLOR[be.evidence_confidence] || "#8b949e", textTransform: "uppercase" }}>
                {be.evidence_confidence || "—"}
              </div>
            </div>
          </div>
          <BehaviourBar label="O1 — Uncommon Idea Generation" value={be.o1_score || 0} />
          <BehaviourBar label="O2 — Concept Combination"        value={be.o2_score || 0} />
          <BehaviourBar label="O3 — Transformation"             value={be.o3_score || 0} />
          <BehaviourBar label="O4 — Non-obvious Solution"       value={be.o4_score || 0} />
          <BehaviourBar label="O5 — Independent Generation"     value={be.o5_score || 0} />
          <BehaviourBar label="O6 — Meaningful Novelty"         value={be.o6_score || 0} />
          {crossRound && (
            <div style={{ marginTop: 12, padding: "10px 14px", background: "#0d1117", borderRadius: 10, fontSize: 13, color: "#8b949e" }}>
              <strong style={{ color: "#e6edf3" }}>Round comparison:</strong>{" "}
              R1: {crossRound.round1_idea_count ?? 0} ideas →
              R2: {crossRound.round2_idea_count ?? 0} ideas
              {crossRound.continued_in_round2 ? " · Continued in R2 ✓" : " · No R2 ideas"}
            </div>
          )}
          {be.notes && (
            <div style={{ marginTop: 10, fontSize: 12, color: "#6e7681", fontStyle: "italic" }}>{be.notes}</div>
          )}
        </div>
      )}

      {/* Responses */}
      <div style={{ background: "#161b22", borderRadius: 16, padding: "20px 24px", marginBottom: 20, border: "1px solid #30363d" }}>
        <h3 style={{ margin: "0 0 16px", fontSize: 16, fontWeight: 800 }}>💬 Raw Responses ({responses?.length || 0})</h3>
        {(responses || []).map(r => (
          <ResponseCard key={r.id} resp={r} analysis={analysisMap[r.id]} />
        ))}
        {(!responses?.length) && <p style={{ color: "#6e7681", fontSize: 13 }}>No responses recorded.</p>}
      </div>

      {/* Facilitator Observations */}
      {(facilitator_observations || []).length > 0 && (
        <div style={{ background: "#161b22", borderRadius: 16, padding: "20px 24px", marginBottom: 20, border: "1px solid #30363d" }}>
          <h3 style={{ margin: "0 0 16px", fontSize: 16, fontWeight: 800 }}>👁 Facilitator Observations</h3>
          {facilitator_observations.map((obs, i) => {
            const KEYS = [
              ["obs_continued_without_prompting", "Continued without prompting"],
              ["obs_multiple_ideas", "Generated multiple ideas"],
              ["obs_revised_idea", "Revised an idea"],
              ["obs_experimented_alternatives", "Experimented with alternatives"],
              ["obs_stuck_after_first", "Stuck after first idea"],
              ["obs_persisted_after_difficulty", "Persisted after difficulty"],
              ["obs_explained_reasoning", "Explained reasoning"],
            ];
            return (
              <div key={i} style={{ marginBottom: 16 }}>
                <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginBottom: 8 }}>
                  {KEYS.map(([k, label]) => (
                    <div key={k} style={{
                      padding: "4px 12px", borderRadius: 20, fontSize: 12, fontWeight: 700,
                      background: obs[k] === -1 ? "#21262d" : obs[k] >= 2 ? "rgba(34,197,94,0.1)" : "rgba(245,166,35,0.1)",
                      color: obs[k] === -1 ? "#6e7681" : obs[k] >= 2 ? "#22c55e" : "#f5a623",
                      border: `1px solid ${obs[k] === -1 ? "#30363d" : obs[k] >= 2 ? "rgba(34,197,94,0.3)" : "rgba(245,166,35,0.3)"}`,
                    }}>
                      {label}: {obs[k] === -1 ? "—" : obs[k]}
                    </div>
                  ))}
                </div>
                {obs.additional_notes && (
                  <div style={{ fontSize: 13, color: "#8b949e", fontStyle: "italic" }}>"{obs.additional_notes}"</div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Event Timeline (Research Mode) */}
      <div style={{ background: "#161b22", borderRadius: 16, padding: "20px 24px", border: "1px solid #30363d" }}>
        <h3 style={{ margin: "0 0 16px", fontSize: 16, fontWeight: 800 }}>
          🔬 Interaction Timeline — Research Mode
          <span style={{ marginLeft: 8, fontSize: 11, color: "#6366f1", fontWeight: 600 }}>Raw Data</span>
        </h3>
        <EventTimeline events={events} />
      </div>
    </div>
  );
}

export default function InventItAdmin() {
  const navigate = useNavigate();
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState(null);
  const [selectedSession, setSelectedSession] = useState(null);
  const [page, setPage] = useState(1);

  useEffect(() => {
    const token = sessionStorage.getItem("goat_token");
    if (!token) {
      navigate("/login");
      return;
    }
    fetch(`${BASE}/invent-it/admin/sessions?page=${page}&limit=20`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then(r => r.ok ? r.json() : Promise.reject(r.status))
      .then(d => { setSessions(d.sessions || []); setLoading(false); })
      .catch(e => { setErr(`Error ${e} — You may need admin privileges.`); setLoading(false); });
  }, [page]);

  const statusColor = { complete: "#22c55e", in_progress: "#f5a623" };

  return (
    <div style={{
      minHeight: "100vh", background: "#0d1117", color: "#e6edf3",
      fontFamily: "'Nunito', sans-serif", padding: "40px 20px",
    }}>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      <div style={{ maxWidth: 1000, margin: "0 auto" }}>
        {selectedSession ? (
          <SessionDetailView session={selectedSession} onBack={() => setSelectedSession(null)} />
        ) : (
          <>
            {/* Header */}
            <div style={{ marginBottom: 32 }}>
              <div style={{
                display: "inline-flex", alignItems: "center", gap: 8,
                background: "rgba(99,102,241,0.1)", border: "1px solid rgba(99,102,241,0.3)",
                borderRadius: 30, padding: "6px 16px", fontSize: 12, fontWeight: 800,
                color: "#6366f1", textTransform: "uppercase", letterSpacing: 1, marginBottom: 16,
              }}>
                🔬 Admin / Research View
              </div>
              <h1 style={{ fontSize: 28, fontWeight: 900, margin: "0 0 8px" }}>
                Invent It — Session Browser
              </h1>
              <p style={{ color: "#8b949e", margin: 0 }}>
                Research mode · Raw data · Not for child-facing use
              </p>
            </div>

            {/* Warning Banner */}
            <div style={{
              background: "rgba(239,68,68,0.08)", border: "1px solid rgba(239,68,68,0.25)",
              borderRadius: 12, padding: "14px 20px", marginBottom: 28, fontSize: 14,
              color: "#fca5a5", lineHeight: 1.5,
            }}>
              ⚠️ <strong>Prototype:</strong> This module is not empirically validated. Provisional rubric scores and AI classifications are for research purposes only. Do not use these scores as final talent diagnoses.
            </div>

            {/* New Session Button */}
            <div style={{ marginBottom: 24, display: "flex", gap: 12 }}>
              <button onClick={() => navigate("/invent-it")} style={{
                padding: "12px 28px", background: "linear-gradient(135deg, #f5a623, #d4841a)",
                color: "#000", border: "none", borderRadius: 30, fontFamily: "Nunito",
                fontWeight: 800, fontSize: 15, cursor: "pointer",
              }}>+ Start New Session</button>
            </div>

            {/* Sessions Table */}
            {loading ? (
              <div style={{ textAlign: "center", padding: 60 }}>
                <div style={{ width: 40, height: 40, border: "3px solid #30363d", borderTopColor: "#f5a623", borderRadius: "50%", animation: "spin 0.8s linear infinite", margin: "0 auto 12px" }} />
                Loading sessions…
              </div>
            ) : err ? (
              <div style={{ color: "#ef4444", padding: 20, background: "rgba(239,68,68,0.08)", borderRadius: 12, border: "1px solid rgba(239,68,68,0.2)" }}>
                {err}
              </div>
            ) : sessions.length === 0 ? (
              <div style={{ textAlign: "center", padding: 60, color: "#6e7681" }}>
                <div style={{ fontSize: 48, marginBottom: 16 }}>📭</div>
                No Invent It sessions yet. Start one to see it here.
              </div>
            ) : (
              <div style={{ overflowX: "auto" }}>
                <table style={{ width: "100%", borderCollapse: "collapse" }}>
                  <thead>
                    <tr style={{ borderBottom: "1px solid #30363d" }}>
                      {["Session UUID", "Student ID", "Status", "Language", "Ideas", "Hints", "Start Time", "Actions"].map(h => (
                        <th key={h} style={{ padding: "10px 14px", textAlign: "left", fontSize: 12, fontWeight: 800, color: "#6e7681", textTransform: "uppercase", letterSpacing: 0.5 }}>
                          {h}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {sessions.map(s => (
                      <tr key={s.session_uuid} style={{ borderBottom: "1px solid #21262d" }}
                        onMouseEnter={e => e.currentTarget.style.background = "#161b22"}
                        onMouseLeave={e => e.currentTarget.style.background = "transparent"}>
                        <td style={{ padding: "12px 14px", fontSize: 13, fontFamily: "monospace", color: "#8b949e" }}>
                          {s.session_uuid?.slice(0,12)}…
                        </td>
                        <td style={{ padding: "12px 14px", fontSize: 13 }}>{s.student_id || "—"}</td>
                        <td style={{ padding: "12px 14px" }}>
                          <span style={{
                            padding: "3px 10px", borderRadius: 20, fontSize: 11, fontWeight: 800,
                            color: statusColor[s.status] || "#8b949e",
                            background: `${statusColor[s.status]}18` || "rgba(139,148,158,0.1)",
                            border: `1px solid ${statusColor[s.status]}44` || "rgba(139,148,158,0.2)",
                          }}>{s.status}</span>
                        </td>
                        <td style={{ padding: "12px 14px", fontSize: 13, textTransform: "uppercase" }}>{s.language}</td>
                        <td style={{ padding: "12px 14px", fontSize: 13, fontWeight: 700 }}>{s.number_of_ideas || 0}</td>
                        <td style={{ padding: "12px 14px", fontSize: 13 }}>{s.hint_count || 0}</td>
                        <td style={{ padding: "12px 14px", fontSize: 12, color: "#6e7681" }}>
                          {s.start_ts ? new Date(s.start_ts).toLocaleString() : "—"}
                        </td>
                        <td style={{ padding: "12px 14px" }}>
                          <button onClick={() => setSelectedSession(s)} style={{
                            padding: "6px 14px", background: "rgba(99,102,241,0.1)",
                            border: "1px solid rgba(99,102,241,0.3)", color: "#a5b4fc",
                            borderRadius: 8, cursor: "pointer", fontFamily: "Nunito", fontWeight: 700, fontSize: 12,
                          }}>View →</button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>

                {/* Pagination */}
                <div style={{ marginTop: 20, display: "flex", gap: 10, justifyContent: "center" }}>
                  <button disabled={page === 1} onClick={() => setPage(p => p - 1)} style={{
                    padding: "8px 20px", background: "#21262d", border: "1px solid #30363d",
                    color: page === 1 ? "#6e7681" : "#e6edf3", borderRadius: 8, cursor: page === 1 ? "not-allowed" : "pointer",
                    fontFamily: "Nunito", fontWeight: 700,
                  }}>← Prev</button>
                  <span style={{ display: "flex", alignItems: "center", color: "#8b949e", fontSize: 14 }}>Page {page}</span>
                  <button disabled={sessions.length < 20} onClick={() => setPage(p => p + 1)} style={{
                    padding: "8px 20px", background: "#21262d", border: "1px solid #30363d",
                    color: sessions.length < 20 ? "#6e7681" : "#e6edf3", borderRadius: 8, cursor: sessions.length < 20 ? "not-allowed" : "pointer",
                    fontFamily: "Nunito", fontWeight: 700,
                  }}>Next →</button>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

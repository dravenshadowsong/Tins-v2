import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";
import { DOMAINS } from "../data/questions";

export default function Dashboard() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [activeTab, setActiveTab] = useState("overview");
  const [loading, setLoading] = useState(true);

  // Core Data States
  const [analytics, setAnalytics] = useState(null);
  const [children, setChildren] = useState([]);
  const [users, setUsers] = useState([]);
  const [centers, setCenters] = useState([]);
  const [workshops, setWorkshops] = useState([]);
  const [puzzles, setPuzzles] = useState([]);

  // Forms States
  const [newUser, setNewUser] = useState({ name: "", email: "", password: "", role: "facilitator", center_id: "" });
  const [newCenter, setNewCenter] = useState({ name: "", location: "" });
  const [newWorkshop, setNewWorkshop] = useState({ name: "", domain: "logical", center_id: "", description: "" });
  const [newSession, setNewSession] = useState({ workshop_id: "", session_date: "", notes: "", attendance: {} });
  const [newValidation, setNewValidation] = useState({ child_id: "", domain: "logical", rating: 3, strengths: "", growth_areas: "", notes: "" });

  // UI state
  const [editingPuzzleId, setEditingPuzzleId] = useState(null);
  const [editingPuzzleJSON, setEditingPuzzleJSON] = useState("");
  const [formMsg, setFormMsg] = useState("");

  useEffect(() => {
    const cachedUser = localStorage.getItem("goat_user");
    if (!cachedUser || !localStorage.getItem("goat_token")) {
      navigate("/login");
      return;
    }
    const parsed = JSON.parse(cachedUser);
    setUser(parsed);

    async function loadData() {
      try {
        const stats = await api.getAnalytics().catch(() => null);
        setAnalytics(stats);

        const kids = await api.getChildren().catch(() => []);
        setChildren(kids);

        if (parsed.role === "master_admin" || parsed.role === "admin") {
          const u = await api.getUsers().catch(() => []);
          setUsers(u);
          const c = await api.getCenters().catch(() => []);
          setCenters(c);
          const w = await api.getWorkshops().catch(() => []);
          setWorkshops(w);
        }

        if (parsed.role === "master_admin") {
          const p = await api.getPuzzles().catch(() => []);
          setPuzzles(p);
        }

        if (parsed.role === "mentor") {
          const w = await api.getWorkshops().catch(() => []);
          setWorkshops(w);
        }
      } catch (err) {
        console.error("Dashboard data load error:", err);
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, [navigate]);

  if (loading) {
    return <div style={{ textAlign: "center", marginTop: 80, color: "#6b7280", fontSize: "16px", fontWeight: 500 }}>Loading Portal Workspace...</div>;
  }

  const role = user?.role || "facilitator";

  return (
    <div style={{ maxWidth: "1200px", margin: "0 auto", padding: "20px 15px" }}>
      {/* Header Banner */}
      <div className="page-header" style={{ marginBottom: "24px" }}>
        <div className="page-header-row" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "12px" }}>
          <div>
            <h1 style={{ margin: 0, fontSize: "28px", fontWeight: 800, color: "#1e1b4b" }}>TINS Talent Management Portal</h1>
            <p className="text-light" style={{ margin: "4px 0 0 0", fontSize: "14px" }}>
              Active Session: <strong style={{ color: "#5b4cf0" }}>{user?.name}</strong> | Role: <span className="domain-badge" style={{ background: "#5b4cf0", color: "#fff", padding: "2px 8px", fontSize: "11px", fontWeight: 700 }}>{role.toUpperCase()}</span>
            </p>
          </div>
          <div style={{ display: "flex", gap: "10px" }}>
            {role === "facilitator" && (
              <button className="btn btn-primary" onClick={() => navigate("/intake")}>
                + Register New Child
              </button>
            )}
            <button className="btn btn-outline" onClick={() => {
              localStorage.clear();
              navigate("/login");
            }}>
              Sign Out
            </button>
          </div>
        </div>
      </div>

      {/* Role Tabs Nav */}
      <div style={{ display: "flex", gap: "8px", borderBottom: "2px solid #e5e7eb", paddingBottom: "10px", marginBottom: "24px", overflowX: "auto" }}>
        <button className={`btn ${activeTab === "overview" ? "btn-primary" : "btn-ghost"}`} onClick={() => setActiveTab("overview")}>
          📊 Analytics Dashboard
        </button>

        {role === "master_admin" && (
          <>
            <button className={`btn ${activeTab === "users" ? "btn-primary" : "btn-ghost"}`} onClick={() => setActiveTab("users")}>
              👥 User Accounts
            </button>
            <button className={`btn ${activeTab === "centers" ? "btn-primary" : "btn-ghost"}`} onClick={() => setActiveTab("centers")}>
              🏢 Center Registry
            </button>
            <button className={`btn ${activeTab === "puzzles" ? "btn-primary" : "btn-ghost"}`} onClick={() => setActiveTab("puzzles")}>
              🧩 Question Bank
            </button>
          </>
        )}

        {role === "admin" && (
          <>
            <button className={`btn ${activeTab === "workshops" ? "btn-primary" : "btn-ghost"}`} onClick={() => setActiveTab("workshops")}>
              🛠️ Workshop Planning
            </button>
            <button className={`btn ${activeTab === "team" ? "btn-primary" : "btn-ghost"}`} onClick={() => setActiveTab("team")}>
              🤝 Team Directories
            </button>
          </>
        )}

        {role === "mentor" && (
          <>
            <button className={`btn ${activeTab === "workshops" ? "btn-primary" : "btn-ghost"}`} onClick={() => setActiveTab("workshops")}>
              📓 Workshop Logbook
            </button>
            <button className={`btn ${activeTab === "validations" ? "btn-primary" : "btn-ghost"}`} onClick={() => setActiveTab("validations")}>
              ✅ Milestones & Validations
            </button>
          </>
        )}

        <button className={`btn ${activeTab === "children" ? "btn-primary" : "btn-ghost"}`} onClick={() => setActiveTab("children")}>
          👦 Child Records
        </button>
      </div>

      {formMsg && (
        <div style={{ background: "#f0fdf4", border: "1px solid #bbf7d0", color: "#166534", padding: "12px", borderRadius: "8px", marginBottom: "20px", fontWeight: 600 }}>
          {formMsg}
        </div>
      )}

      {/* RENDER ACTIVE TAB VIEW */}

      {/* OVERVIEW / ANALYTICS TAB */}
      {activeTab === "overview" && (
        <div>
          {analytics ? (
            <>
              {/* Stats Funnel Row */}
              <div className="stats-grid" style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "16px", marginBottom: "24px" }}>
                <div className="stat-card" style={{ padding: "20px", borderRadius: "12px", border: "1px solid #e5e7eb" }}>
                  <div className="stat-num" style={{ fontSize: "36px", fontWeight: 800, color: "#5b4cf0" }}>{analytics.progress_funnel?.registered || children.length}</div>
                  <div className="stat-label" style={{ fontSize: "13px", color: "#6b7280", fontWeight: 600 }}>Students Registered</div>
                </div>
                <div className="stat-card" style={{ padding: "20px", borderRadius: "12px", border: "1px solid #e5e7eb" }}>
                  <div className="stat-num" style={{ fontSize: "36px", fontWeight: 800, color: "#10b981" }}>{analytics.progress_funnel?.assessed || 0}</div>
                  <div className="stat-label" style={{ fontSize: "13px", color: "#6b7280", fontWeight: 600 }}>Assessed Completed</div>
                </div>
                <div className="stat-card" style={{ padding: "20px", borderRadius: "12px", border: "1px solid #e5e7eb" }}>
                  <div className="stat-num" style={{ fontSize: "36px", fontWeight: 800, color: "#f59e0b" }}>{analytics.progress_funnel?.matched || 0}</div>
                  <div className="stat-label" style={{ fontSize: "13px", color: "#6b7280", fontWeight: 600 }}>Active Mentor Matches</div>
                </div>
                <div className="stat-card" style={{ padding: "20px", borderRadius: "12px", border: "1px solid #e5e7eb" }}>
                  <div className="stat-num" style={{ fontSize: "36px", fontWeight: 800, color: "#06b6d4" }}>{analytics.progress_funnel?.enrolled || 0}</div>
                  <div className="stat-label" style={{ fontSize: "13px", color: "#6b7280", fontWeight: 600 }}>Workshop Active Attendees</div>
                </div>
              </div>

              <div className="grid-2" style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(450px, 1fr))", gap: "24px", marginBottom: "24px" }}>
                {/* Talent Distribution Bar Chart */}
                <div className="card" style={{ padding: "24px", borderRadius: "16px" }}>
                  <h2 className="card-title-tight" style={{ fontSize: "18px", fontWeight: 800, marginBottom: "16px" }}>Talent Domain Distribution</h2>
                  {Object.keys(DOMAINS).map(dom => {
                    const cnt = analytics.talent_distribution?.[dom] || 0;
                    const d = DOMAINS[dom];
                    const maxCount = Math.max(...Object.values(analytics.talent_distribution || {}).concat([1]));
                    return (
                      <div key={dom} className="score-row" style={{ marginBottom: "12px" }}>
                        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "4px", fontSize: "13.5px" }}>
                          <span style={{ fontWeight: 600 }}>{d.emoji} {d.label}</span>
                          <span style={{ fontWeight: 700, color: d.color }}>{cnt} children</span>
                        </div>
                        <div className="score-bar-bg" style={{ height: "10px", background: "#f3f4f6", borderRadius: "5px" }}>
                          <div style={{ width: `${(cnt / maxCount) * 100}%`, height: "100%", background: d.color, borderRadius: "5px", transition: "width 0.5s ease" }} />
                        </div>
                      </div>
                    );
                  })}
                </div>

                {/* Workshop Demand distribution */}
                <div className="card" style={{ padding: "24px", borderRadius: "16px" }}>
                  <h2 className="card-title-tight" style={{ fontSize: "18px", fontWeight: 800, marginBottom: "16px" }}>Nurturing Workshop Planners</h2>
                  {Object.keys(DOMAINS).map(dom => {
                    const cnt = analytics.workshop_demand?.[dom] || 0;
                    const d = DOMAINS[dom];
                    const maxDemand = Math.max(...Object.values(analytics.workshop_demand || {}).concat([1]));
                    return (
                      <div key={dom} className="score-row" style={{ marginBottom: "12px" }}>
                        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "4px", fontSize: "13.5px" }}>
                          <span style={{ fontWeight: 600 }}>{d.emoji} {d.label} Workshops</span>
                          <span style={{ fontWeight: 700, color: d.color }}>{cnt} active</span>
                        </div>
                        <div className="score-bar-bg" style={{ height: "10px", background: "#f3f4f6", borderRadius: "5px" }}>
                          <div style={{ width: `${(cnt / maxDemand) * 100}%`, height: "100%", background: d.color, borderRadius: "5px", transition: "width 0.5s ease" }} />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Untapped Potential Indicator */}
              <div className="card" style={{ padding: "24px", borderRadius: "16px", marginBottom: "24px" }}>
                <h2 className="card-title-tight" style={{ fontSize: "18px", fontWeight: 800, marginBottom: "16px" }}>🔍 Secondary Untapped Potential Index</h2>
                <div style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
                  {Object.entries(analytics.untapped_potential || {}).map(([dom, cnt]) => {
                    const d = DOMAINS[dom];
                    return (
                      <div key={dom} style={{ border: `1.5px solid ${d?.color}20`, background: `${d?.color}08`, padding: "10px 16px", borderRadius: "12px", display: "flex", alignItems: "center", gap: "8px" }}>
                        <span style={{ fontSize: "20px" }}>{d?.emoji}</span>
                        <div>
                          <div style={{ fontSize: "11px", fontWeight: 800, textTransform: "uppercase", color: "#6b7280" }}>{d?.label}</div>
                          <div style={{ fontSize: "14px", fontWeight: 700, color: d?.color }}>{cnt} Students</div>
                        </div>
                      </div>
                    );
                  })}
                  {Object.keys(analytics.untapped_potential || {}).length === 0 && (
                    <span style={{ color: "#999", fontSize: "14px" }}>No secondary potential indexed yet.</span>
                  )}
                </div>
              </div>

              {/* Data Exporter Component */}
              {(role === "master_admin" || role === "admin") && (
                <div className="card" style={{ padding: "20px", borderRadius: "12px", background: "linear-gradient(135deg, #f5f3ff 0%, #edd8ff 100%)", display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "16px" }}>
                  <div>
                    <h3 style={{ margin: 0, fontWeight: 800, color: "#4c1d95" }}>📥 Longitudinal Talent Data Export</h3>
                    <p style={{ margin: "4px 0 0 0", fontSize: "13px", color: "#6d28d9" }}>Download standard CSV format comprising registered profiles, top domain results, and test scores.</p>
                  </div>
                  <a href="http://localhost:5050/api/export/csv" download className="btn btn-primary" style={{ background: "#5b4cf0" }}>
                    Export CSV Ledger (.csv)
                  </a>
                </div>
              )}
            </>
          ) : (
            <div style={{ textAlign: "center", padding: "40px", color: "#999" }}>Analytics metrics currently offline. Ensure assessments are conducted first.</div>
          )}
        </div>
      )}

      {/* USER ACCOUNTS TAB */}
      {activeTab === "users" && role === "master_admin" && (
        <div className="grid-3" style={{ display: "grid", gridTemplateColumns: "1fr 2fr", gap: "24px" }}>
          {/* Add User Panel */}
          <div className="card" style={{ padding: "20px", borderRadius: "12px", height: "fit-content" }}>
            <h3 style={{ margin: "0 0 16px 0", fontWeight: 800 }}>Add System Account</h3>
            <form onSubmit={async (e) => {
              e.preventDefault();
              try {
                await api.createUser(newUser);
                setFormMsg(`Successfully created user: ${newUser.name}`);
                setNewUser({ name: "", email: "", password: "", role: "facilitator", center_id: "" });
                const u = await api.getUsers();
                setUsers(u);
              } catch (err) {
                alert("Failed to create account. Check if email is unique.");
              }
            }}>
              <div className="form-group">
                <label>Account Name</label>
                <input type="text" value={newUser.name} onChange={e => setNewUser({ ...newUser, name: e.target.value })} required />
              </div>
              <div className="form-group">
                <label>Email Address</label>
                <input type="email" value={newUser.email} onChange={e => setNewUser({ ...newUser, email: e.target.value })} required />
              </div>
              <div className="form-group">
                <label>Password</label>
                <input type="password" value={newUser.password} onChange={e => setNewUser({ ...newUser, password: e.target.value })} required />
              </div>
              <div className="form-group">
                <label>System Role</label>
                <select value={newUser.role} onChange={e => setNewUser({ ...newUser, role: e.target.value })} style={{ width: "100%", height: "38px", border: "1px solid #e5e7eb", borderRadius: "8px", padding: "0 8px" }}>
                  <option value="master_admin">👑 Master Admin</option>
                  <option value="admin">🛡️ Admin</option>
                  <option value="facilitator">🧑‍🏫 Facilitator</option>
                  <option value="mentor">🤝 Mentor</option>
                </select>
              </div>
              <div className="form-group">
                <label>Assigned Center</label>
                <select value={newUser.center_id} onChange={e => setNewUser({ ...newUser, center_id: e.target.value })} style={{ width: "100%", height: "38px", border: "1px solid #e5e7eb", borderRadius: "8px", padding: "0 8px" }}>
                  <option value="">-- No Assigned Center --</option>
                  {centers.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                </select>
              </div>
              <button type="submit" className="btn btn-primary btn-full mt-16">Create Account</button>
            </form>
          </div>

          {/* User List Panel */}
          <div className="card" style={{ padding: "20px", borderRadius: "12px" }}>
            <h3 style={{ margin: "0 0 16px 0", fontWeight: 800 }}>Active System Users</h3>
            <div className="table-wrap">
              <table className="goat-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Role</th>
                    <th>Center</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map(u => (
                    <tr key={u.id}>
                      <td>{u.id}</td>
                      <td style={{ fontWeight: 600 }}>{u.name}</td>
                      <td>{u.email}</td>
                      <td><span style={{ fontSize: "11px", fontWeight: 700 }} className="domain-badge">{u.role.toUpperCase()}</span></td>
                      <td>{centers.find(c => c.id === u.center_id)?.name || "Global / Main"}</td>
                      <td>
                        <button className="btn btn-ghost btn-sm" style={{ color: "#ef4444" }} onClick={async () => {
                          if (confirm(`Are you sure you want to delete ${u.name}?`)) {
                            await api.deleteUser(u.id);
                            setUsers(users.filter(x => x.id !== u.id));
                          }
                        }}>Delete</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* CENTERS REGISTRY TAB */}
      {activeTab === "centers" && role === "master_admin" && (
        <div className="grid-3" style={{ display: "grid", gridTemplateColumns: "1fr 2fr", gap: "24px" }}>
          {/* Add Center Panel */}
          <div className="card" style={{ padding: "20px", borderRadius: "12px", height: "fit-content" }}>
            <h3 style={{ margin: "0 0 16px 0", fontWeight: 800 }}>Registry New Center</h3>
            <form onSubmit={async (e) => {
              e.preventDefault();
              await api.createCenter(newCenter);
              setFormMsg(`Successfully registered center: ${newCenter.name}`);
              setNewCenter({ name: "", location: "" });
              const c = await api.getCenters();
              setCenters(c);
            }}>
              <div className="form-group">
                <label>Center Name</label>
                <input type="text" value={newCenter.name} onChange={e => setNewCenter({ ...newCenter, name: e.target.value })} required placeholder="e.g. Mumbai Center" />
              </div>
              <div className="form-group">
                <label>Location Details</label>
                <input type="text" value={newCenter.location} onChange={e => setNewCenter({ ...newCenter, location: e.target.value })} required placeholder="e.g. Dharavi, Mumbai" />
              </div>
              <button type="submit" className="btn btn-primary btn-full mt-16">Registry Center</button>
            </form>
          </div>

          {/* Center List Panel */}
          <div className="card" style={{ padding: "20px", borderRadius: "12px" }}>
            <h3 style={{ margin: "0 0 16px 0", fontWeight: 800 }}>Registered Centers</h3>
            <div className="table-wrap">
              <table className="goat-table">
                <thead>
                  <tr>
                    <th>Center ID</th>
                    <th>Center Name</th>
                    <th>Location</th>
                    <th>Registered At</th>
                  </tr>
                </thead>
                <tbody>
                  {centers.map(c => (
                    <tr key={c.id}>
                      <td>{c.id}</td>
                      <td style={{ fontWeight: 600 }}>{c.name}</td>
                      <td>{c.location}</td>
                      <td>{c.created_at}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* QUESTION BANK / PUZZLE BANK TAB */}
      {activeTab === "puzzles" && role === "master_admin" && (
        <div className="card" style={{ padding: "20px", borderRadius: "12px" }}>
          <h3 style={{ margin: "0 0 8px 0", fontWeight: 800 }}>Master Question Bank Manager</h3>
          <p className="text-light" style={{ fontSize: "13.5px", marginBottom: "20px" }}>Modify raw JSON properties of standard seeded tasks. Updates immediately affect new child assessment flows.</p>
          <div className="table-wrap">
            <table className="goat-table">
              <thead>
                <tr>
                  <th>Task Key</th>
                  <th>Domain</th>
                  <th>Component</th>
                  <th>Type</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {puzzles.map(p => (
                  <tr key={p.id}>
                    <td><code style={{ fontSize: "12px", background: "#f3f4f6", padding: "2px 6px", borderRadius: "4px" }}>{p.key}</code></td>
                    <td>
                      <span className="domain-badge" style={{ background: DOMAINS[p.domain]?.light, color: DOMAINS[p.domain]?.color }}>
                        {DOMAINS[p.domain]?.emoji} {DOMAINS[p.domain]?.label}
                      </span>
                    </td>
                    <td>{p.component}</td>
                    <td><span className="domain-badge">{p.type}</span></td>
                    <td>
                      <button className="btn btn-ghost btn-sm" onClick={() => {
                        setEditingPuzzleId(p.id);
                        setEditingPuzzleJSON(JSON.stringify(JSON.parse(p.data), null, 2));
                      }}>Edit JSON</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {editingPuzzleId && (
            <div style={{ position: "fixed", top: 0, left: 0, right: 0, bottom: 0, background: "rgba(0,0,0,0.5)", display: "flex", justifyContent: "center", alignItems: "center", zIndex: 1000 }}>
              <div className="card" style={{ width: "90%", maxWidth: "600px", padding: "24px" }}>
                <h3 style={{ margin: "0 0 10px 0" }}>Edit Puzzle Config JSON</h3>
                <p style={{ fontSize: "12px", color: "#6b7280" }}>Ensure proper brackets syntax. Check schema parameters before committing.</p>
                <textarea
                  style={{ width: "100%", height: "300px", fontFamily: "monospace", fontSize: "12.5px", border: "1.5px solid #d1d5db", borderRadius: "8px", padding: "8px", boxSizing: "border-box", marginBottom: "16px" }}
                  value={editingPuzzleJSON}
                  onChange={e => setEditingPuzzleJSON(e.target.value)}
                />
                <div style={{ display: "flex", gap: "10px", justifyContent: "flex-end" }}>
                  <button className="btn btn-ghost" onClick={() => setEditingPuzzleId(null)}>Cancel</button>
                  <button className="btn btn-primary" onClick={async () => {
                    try {
                      const data = JSON.parse(editingPuzzleJSON);
                      await api.editPuzzle(editingPuzzleId, { data });
                      setFormMsg(`Successfully updated puzzle configuration.`);
                      setEditingPuzzleId(null);
                      const p = await api.getPuzzles();
                      setPuzzles(p);
                    } catch (err) {
                      alert("Invalid JSON syntax schema! Correct spelling or bracket closures.");
                    }
                  }}>Commit Modifications</button>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* WORKSHOP PLANNING TAB (ADMIN & MENTOR VIEW) */}
      {activeTab === "workshops" && (role === "admin" || role === "master_admin" || role === "mentor") && (
        <div className="grid-3" style={{ display: "grid", gridTemplateColumns: role === "mentor" ? "1fr" : "1fr 2fr", gap: "24px" }}>
          {/* Add Workshop Panel */}
          {role !== "mentor" && (
            <div className="card" style={{ padding: "20px", borderRadius: "12px", height: "fit-content" }}>
              <h3 style={{ margin: "0 0 16px 0", fontWeight: 800 }}>Schedule New Workshop</h3>
              <form onSubmit={async (e) => {
                e.preventDefault();
                await api.createWorkshop(newWorkshop);
                setFormMsg(`Successfully created workshop: ${newWorkshop.name}`);
                setNewWorkshop({ name: "", domain: "logical", center_id: "", description: "" });
                const w = await api.getWorkshops();
                setWorkshops(w);
              }}>
                <div className="form-group">
                  <label>Workshop Topic / Name</label>
                  <input type="text" value={newWorkshop.name} onChange={e => setNewWorkshop({ ...newWorkshop, name: e.target.value })} required placeholder="e.g. Robot Coding Basics" />
                </div>
                <div className="form-group">
                  <label>Primary Skill Domain</label>
                  <select value={newWorkshop.domain} onChange={e => setNewWorkshop({ ...newWorkshop, domain: e.target.value })} style={{ width: "100%", height: "38px", border: "1px solid #e5e7eb", borderRadius: "8px", padding: "0 8px" }}>
                    {Object.entries(DOMAINS).map(([k, v]) => <option key={k} value={k}>{v.emoji} {v.label}</option>)}
                  </select>
                </div>
                <div className="form-group">
                  <label>Hosting Center</label>
                  <select value={newWorkshop.center_id} onChange={e => setNewWorkshop({ ...newWorkshop, center_id: e.target.value })} required style={{ width: "100%", height: "38px", border: "1px solid #e5e7eb", borderRadius: "8px", padding: "0 8px" }}>
                    <option value="">-- Select Center --</option>
                    {centers.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                  </select>
                </div>
                <div className="form-group">
                  <label>Description Details</label>
                  <input type="text" value={newWorkshop.description} onChange={e => setNewWorkshop({ ...newWorkshop, description: e.target.value })} placeholder="e.g. Advanced logical thinking puzzles session." />
                </div>
                <button type="submit" className="btn btn-primary btn-full mt-16">Register Workshop</button>
              </form>
            </div>
          )}

          {/* Active Workshops / Mentor Logging Panel */}
          <div className="card" style={{ padding: "20px", borderRadius: "12px" }}>
            <h3 style={{ margin: "0 0 16px 0", fontWeight: 800 }}>Active Skill Nurturing Workshops</h3>
            <div className="table-wrap" style={{ marginBottom: "24px" }}>
              <table className="goat-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Topic</th>
                    <th>Domain</th>
                    <th>Center</th>
                    <th>Description</th>
                    {role === "mentor" && <th>Action</th>}
                  </tr>
                </thead>
                <tbody>
                  {workshops.map(w => (
                    <tr key={w.id}>
                      <td>{w.id}</td>
                      <td style={{ fontWeight: 600 }}>{w.name}</td>
                      <td>
                        <span className="domain-badge" style={{ background: DOMAINS[w.domain]?.light, color: DOMAINS[w.domain]?.color }}>
                          {DOMAINS[w.domain]?.emoji} {DOMAINS[w.domain]?.label}
                        </span>
                      </td>
                      <td>{w.center_name || "Assigned Center"}</td>
                      <td>{w.description}</td>
                      {role === "mentor" && (
                        <td>
                          <button className="btn btn-ghost btn-sm" onClick={() => {
                            setNewSession({ ...newSession, workshop_id: w.id });
                            setFormMsg(`Now logging session for: ${w.name}`);
                          }}>Log Session</button>
                        </td>
                      )}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Mentor Session Logging Form */}
            {role === "mentor" && newSession.workshop_id && (
              <div className="card" style={{ padding: "20px", borderRadius: "12px", border: "1px dashed #5b4cf0", background: "#fcfcff" }}>
                <h3 style={{ margin: "0 0 12px 0", color: "#5b4cf0" }}> Log Workshop Session Attendance</h3>
                <form onSubmit={async (e) => {
                  e.preventDefault();
                  try {
                    await api.createWorkshopSession(newSession.workshop_id, newSession);
                    setFormMsg("Session logs and child attendance registered successfully!");
                    setNewSession({ workshop_id: "", session_date: "", notes: "", attendance: {} });
                  } catch (err) {
                    alert("Ensure session details are complete.");
                  }
                }}>
                  <div className="form-group">
                    <label>Session Date</label>
                    <input type="date" value={newSession.session_date} onChange={e => setNewSession({ ...newSession, session_date: e.target.value })} required />
                  </div>
                  <div className="form-group">
                    <label>Class Activity / Evaluation Notes</label>
                    <input type="text" value={newSession.notes} onChange={e => setNewSession({ ...newSession, notes: e.target.value })} required placeholder="e.g. Conducted building activities with bricks." />
                  </div>
                  <div className="form-group">
                    <label>Mark Attendance (Present Checkbox)</label>
                    <div style={{ maxHeight: "150px", overflowY: "auto", border: "1.5px solid #d1d5db", borderRadius: "8px", padding: "8.5px" }}>
                      {children.map(c => (
                        <div key={c.id} style={{ display: "flex", alignItems: "center", gap: "8px", margin: "6px 0" }}>
                          <input
                            type="checkbox"
                            checked={newSession.attendance[c.id] === "Present"}
                            onChange={e => {
                              const checked = e.target.checked;
                              setNewSession({
                                ...newSession,
                                attendance: { ...newSession.attendance, [c.id]: checked ? "Present" : "Absent" }
                              });
                            }}
                          />
                          <span style={{ fontSize: "14px", fontWeight: 500 }}>{c.name} (Age: {c.age})</span>
                        </div>
                      ))}
                    </div>
                  </div>
                  <button type="submit" className="btn btn-primary mt-16">Submit Attendance Log</button>
                </form>
              </div>
            )}
          </div>
        </div>
      )}

      {/* TEAM DIRECTORIES TAB */}
      {activeTab === "team" && role === "admin" && (
        <div className="card" style={{ padding: "20px", borderRadius: "12px" }}>
          <h3 style={{ margin: "0 0 16px 0", fontWeight: 800 }}>Center Staff & Mentors Directory</h3>
          <div className="table-wrap">
            <table className="goat-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Name</th>
                  <th>Email</th>
                  <th>System Role</th>
                </tr>
              </thead>
              <tbody>
                {users.map(u => (
                  <tr key={u.id}>
                    <td>{u.id}</td>
                    <td style={{ fontWeight: 600 }}>{u.name}</td>
                    <td>{u.email}</td>
                    <td><span className="domain-badge">{u.role.toUpperCase()}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* MILESTONES & VALIDATIONS TAB (MENTOR VIEW) */}
      {activeTab === "validations" && role === "mentor" && (
        <div className="grid-3" style={{ display: "grid", gridTemplateColumns: "1fr 2fr", gap: "24px" }}>
          {/* Submit Validation Panel */}
          <div className="card" style={{ padding: "20px", borderRadius: "12px", height: "fit-content" }}>
            <h3 style={{ margin: "0 0 16px 0", fontWeight: 800 }}>Submit Mentor Validation</h3>
            <form onSubmit={async (e) => {
              e.preventDefault();
              await api.submitMentorValidation({ ...newValidation, match_id: 1 });
              setFormMsg("Mentor validation successfully committed to student growth record!");
              setNewValidation({ child_id: "", domain: "logical", rating: 3, strengths: "", growth_areas: "", notes: "" });
            }}>
              <div className="form-group">
                <label>Select Child / Student</label>
                <select value={newValidation.child_id} onChange={e => setNewValidation({ ...newValidation, child_id: e.target.value })} required style={{ width: "100%", height: "38px", border: "1px solid #e5e7eb", borderRadius: "8px", padding: "0 8px" }}>
                  <option value="">-- Select Student --</option>
                  {children.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                </select>
              </div>
              <div className="form-group">
                <label>Validated Talent Domain</label>
                <select value={newValidation.domain} onChange={e => setNewValidation({ ...newValidation, domain: e.target.value })} style={{ width: "100%", height: "38px", border: "1px solid #e5e7eb", borderRadius: "8px", padding: "0 8px" }}>
                  {Object.entries(DOMAINS).map(([k, v]) => <option key={k} value={k}>{v.emoji} {v.label}</option>)}
                </select>
              </div>
              <div className="form-group">
                <label>Rating (1 to 5 Stars)</label>
                <input type="number" min="1" max="5" value={newValidation.rating} onChange={e => setNewValidation({ ...newValidation, rating: parseInt(e.target.value) })} required />
              </div>
              <div className="form-group">
                <label>Core Strengths Observed</label>
                <input type="text" value={newValidation.strengths} onChange={e => setNewValidation({ ...newValidation, strengths: e.target.value })} placeholder="e.g. Exceptional spatial construction" />
              </div>
              <div className="form-group">
                <label>Growth Areas</label>
                <input type="text" value={newValidation.growth_areas} onChange={e => setNewValidation({ ...newValidation, growth_areas: e.target.value })} placeholder="e.g. Needs language storytelling focus" />
              </div>
              <div className="form-group">
                <label>Evaluation Notes</label>
                <input type="text" value={newValidation.notes} onChange={e => setNewValidation({ ...newValidation, notes: e.target.value })} placeholder="Additional feedback observations..." />
              </div>
              <button type="submit" className="btn btn-primary btn-full mt-16">Submit Validation</button>
            </form>
          </div>

          {/* Validation Logs */}
          <div className="card" style={{ padding: "20px", borderRadius: "12px" }}>
            <h3 style={{ margin: "0 0 16px 0", fontWeight: 800 }}>Children Records & Development Timeline</h3>
            <div className="table-wrap">
              <table className="goat-table">
                <thead>
                  <tr>
                    <th>Student</th>
                    <th>Age</th>
                    <th>Assigned Center</th>
                    <th>Validation Progress</th>
                  </tr>
                </thead>
                <tbody>
                  {children.map(c => (
                    <tr key={c.id}>
                      <td style={{ fontWeight: 600 }}>{c.name}</td>
                      <td>{c.age}</td>
                      <td>New Delhi Center</td>
                      <td>
                        <button className="btn btn-ghost btn-sm" onClick={async () => {
                          const v = await api.getMentorValidations(c.id).catch(() => []);
                          alert(`Validation Logs for ${c.name}:\n\n` + (v.length === 0 ? "No evaluations logged." : v.map(x => `Domain: ${x.domain.toUpperCase()} | Rating: ${x.rating}/5 stars\nStrengths: ${x.strengths || "N/A"}\nNotes: ${x.notes || "N/A"}`).join("\n\n")));
                        }}>View Developmental Log</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* CHILDREN RECORDS TAB */}
      {activeTab === "children" && (
        <div className="card" style={{ padding: "20px", borderRadius: "12px" }}>
          <h3 style={{ margin: "0 0 16px 0", fontWeight: 800 }}>Assessments & Registry List</h3>
          <div className="table-wrap">
            <table className="goat-table">
              <thead>
                <tr>
                  <th>Student Name</th>
                  <th>Age</th>
                  <th>Gender</th>
                  <th>Assessed Top Talent</th>
                  <th>Registry Date</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {children.map(c => (
                  <ChildRecordRow key={c.id} child={c} navigate={navigate} role={role} />
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

function ChildRecordRow({ child, navigate, role }) {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.childSessions(child.id)
      .then(setSessions)
      .finally(() => setLoading(false));
  }, [child.id]);

  const latest = sessions[0];
  const topDomain = latest?.top_domain;
  const d = DOMAINS[topDomain];

  return (
    <tr>
      <td style={{ fontWeight: 600 }}>{child.name}</td>
      <td>{child.age}</td>
      <td>{child.gender || "Not specified"}</td>
      <td>
        {d ? (
          <span className="domain-badge" style={{ background: d.light, color: d.color }}>
            {d.emoji} {d.label}
          </span>
        ) : (
          <span style={{ color: "#999", fontSize: "13px" }}>Discovery Phase</span>
        )}
      </td>
      <td>{child.created_at?.slice(0, 10)}</td>
      <td>
        <div style={{ display: "flex", gap: "6px" }}>
          {latest ? (
            <>
              <button className="btn btn-ghost btn-sm" onClick={() => navigate(`/results/${latest.id}?cid=${child.id}`)}>
                View Evaluation
              </button>
              {(role === "facilitator" || role === "master_admin") && (
                <button className="btn btn-outline btn-sm" onClick={async () => {
                  if (confirm(`Trigger longitudinal re-assessment for ${child.name}? This preserves the historical assessments.`)) {
                    const res = await api.scheduleReassessment(child.id);
                    navigate(`/discovery/${res.session_id}`);
                  }
                }}>
                  🔄 Re-Assess
                </button>
              )}
            </>
          ) : (
            (role === "facilitator" || role === "master_admin") && (
              <button className="btn btn-primary btn-sm" onClick={async () => {
                const s = await api.createSession(child.id);
                navigate(`/discovery/${s.id}`);
              }}>
                Start Assessment
              </button>
            )
          )}
        </div>
      </td>
    </tr>
  );
}

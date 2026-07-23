import { useEffect, useState, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { api, BASE } from "../api";
import { DOMAINS } from "../data/questions";
import { supabase } from "../supabaseClient";

function clearAllCache() {
  // Clear backend session token + user profile
  sessionStorage.clear();
  // Clear any Supabase browser-persisted auth state
  Object.keys(localStorage).forEach(key => {
    if (key.startsWith("sb-") || key.includes("supabase")) {
      localStorage.removeItem(key);
    }
  });
}

export default function Dashboard() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [activeTab, setActiveTab] = useState("overview");
  const [loading, setLoading] = useState(true);

  // Core Data States
  const [analytics, setAnalytics] = useState(null);
  const [children, setChildren] = useState([]);
  const [selectedCenterFilter, setSelectedCenterFilter] = useState("");
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
  const [showPassModal, setShowPassModal] = useState(false);
  const [passForm, setPassForm] = useState({ old_password: "", new_password: "" });
  const [passError, setPassError] = useState("");
  const [passSuccess, setPassSuccess] = useState("");

  useEffect(() => {
    const cachedUser = sessionStorage.getItem("goat_user");
    if (!cachedUser || !sessionStorage.getItem("goat_token")) {
      navigate("/login");
      return;
    }
    const parsed = JSON.parse(cachedUser);
    setUser(parsed);

    async function loadData() {
      try {
        // 1. Fetch fresh user profile from backend
        let activeUser = parsed;
        const profileResponse = await api.me().catch(() => null);
        if (profileResponse && profileResponse.user) {
          activeUser = profileResponse.user;
          setUser(profileResponse.user);
          sessionStorage.setItem("goat_user", JSON.stringify(profileResponse.user));
        }

        const activeRole = (activeUser.role || "").toLowerCase();

        const stats = await api.getAnalytics().catch(() => null);
        setAnalytics(stats);

        const kids = await api.getChildren().catch(() => []);
        setChildren(kids);

        if (activeRole === "master_admin" || activeRole === "admin") {
          const u = await api.getUsers().catch(() => []);
          setUsers(u);
          const c = await api.getCenters().catch(() => []);
          setCenters(c);
          const w = await api.getWorkshops().catch(() => []);
          setWorkshops(w);
        }

        if (activeRole === "master_admin") {
          const p = await api.getPuzzles().catch(() => []);
          setPuzzles(p);
        }

        if (activeRole === "mentor") {
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

  // ── Derived state: must be above all early returns (Rules of Hooks) ──────────
  const role = (user?.role || "facilitator").toLowerCase();

  const aggregates = useMemo(() => {
    let highPotentialStudents = [];
    let lowExposureStudents = [];
    let workshopCounts = {};

    children.forEach(child => {
      const pdata = typeof child.personality_data === "string" ? JSON.parse(child.personality_data) : child.personality_data;
      const tq = typeof child.tq_scores === "string" ? JSON.parse(child.tq_scores) : child.tq_scores || {};

      // 1. High-Potential Students: scored >= 85 in any domain
      let highDomains = [];
      Object.entries(tq).forEach(([dom, score]) => {
        if (score >= 85) {
          highDomains.push({ domain: dom, score });
        }
      });
      if (highDomains.length > 0 && child.latest_session_id) {
        highPotentialStudents.push({
          id: child.id,
          name: child.name,
          age: child.age,
          center: child.center_name || "Unassigned",
          latest_session_id: child.latest_session_id,
          highDomains
        });
      }

      // 2. Low-Exposure Opportunities: TEG status "High Potential, Low Exposure"
      if (pdata && pdata.teg_data) {
        let lowExpDomains = [];
        Object.entries(pdata.teg_data).forEach(([dom, details]) => {
          if (details.teg_status === "High Potential, Low Exposure" || (details.talent_score >= 75 && details.exposure_score <= 33)) {
            lowExpDomains.push({
              domain: dom,
              talent_score: details.talent_score,
              exposure_score: details.exposure_score,
              opportunity_score: details.opportunity_score
            });
          }
        });
        if (lowExpDomains.length > 0 && child.latest_session_id) {
          lowExposureStudents.push({
            id: child.id,
            name: child.name,
            age: child.age,
            center: child.center_name || "Unassigned",
            latest_session_id: child.latest_session_id,
            lowExpDomains
          });
        }
      }

      // 3. Workshop Recommendations: aggregate recommended workshops
      if (pdata && pdata.workshops) {
        pdata.workshops.forEach(ws => {
          const title = ws.title;
          if (!workshopCounts[title]) {
            workshopCounts[title] = {
              title,
              desc: ws.desc,
              count: 0,
              reasons: [],
              students: []
            };
          }
          workshopCounts[title].count += 1;
          if (!workshopCounts[title].students.includes(child.name)) {
            workshopCounts[title].students.push(child.name);
          }
          if (ws.reason && !workshopCounts[title].reasons.includes(ws.reason)) {
            workshopCounts[title].reasons.push(ws.reason);
          }
        });
      }
    });

    // 4. Talent Clusters: Group children by top_domain and untapped_potential
    const domainCounts = {};
    children.forEach(child => {
      if (child.top_domain) {
        domainCounts[child.top_domain] = (domainCounts[child.top_domain] || 0) + 1;
      }
      const pdata = typeof child.personality_data === "string" ? JSON.parse(child.personality_data) : child.personality_data;
      if (pdata && pdata.secondary_domains) {
        pdata.secondary_domains.forEach(dom => {
          domainCounts[dom] = (domainCounts[dom] || 0) + 0.5;
        });
      }
    });

    const sortedDomains = Object.entries(domainCounts)
      .sort((a, b) => b[1] - a[1])
      .map(([dom, val]) => [dom, val]);

    return {
      highPotentialStudents,
      lowExposureStudents,
      workshopCounts: Object.values(workshopCounts).sort((a, b) => b.count - a.count),
      sortedDomains
    };
  }, [children]);

  const pendingUsers = users.filter(u => u.role && u.role.toLowerCase().startsWith("pending_"));
  const activeUsers = users.filter(u => !u.role || !u.role.toLowerCase().startsWith("pending_"));

  // ── Early returns (after all hooks) ─────────────────────────────────────────
  if (loading) {
    return <div style={{ textAlign: "center", marginTop: 80, color: "#6b7280", fontSize: "16px", fontWeight: 500 }}>Loading Portal Workspace...</div>;
  }

  if (role.startsWith("pending_")) {
    const reqRole = role.replace("pending_", "").toUpperCase();
    return (
      <div className="auth-layout" style={{ padding: "80px 10px", textAlign: "center", display: "flex", justifyContent: "center", alignItems: "center", minHeight: "80vh" }}>
        <div className="card" style={{ width: "100%", maxWidth: "500px", padding: "40px 30px", borderRadius: "16px", border: "1.5px solid rgba(91, 76, 240, 0.12)", boxShadow: "0 10px 25px -5px rgba(0, 0, 0, 0.05)" }}>
          <div style={{ fontSize: "56px", marginBottom: "16px" }}>⏳</div>
          <h1 style={{ fontSize: "24px", fontWeight: 800, color: "#1e1b4b", margin: "0 0 12px 0" }}>Account Pending Approval</h1>
          <p className="text-light" style={{ fontSize: "14.5px", lineHeight: "1.6", marginBottom: "24px" }}>
            Hello <strong>{user?.name}</strong>! Your request to join as a <strong style={{ color: "#5b4cf0" }}>{reqRole}</strong> is currently pending review. 
            A system administrator must approve your account once before you can access the portal features.
          </p>
          <div style={{ padding: "12px", background: "#f5f3ff", borderRadius: "8px", color: "#6d28d9", fontSize: "13.5px", fontWeight: 600, marginBottom: "24px" }}>
            Registered Email: {user?.email}
          </div>
          <button className="btn btn-outline btn-full" onClick={async () => {
            await supabase.auth.signOut().catch(() => {});
            clearAllCache();
            navigate("/login");
          }} style={{ fontWeight: 700 }}>
            Sign Out & Back to Login
          </button>
        </div>
      </div>
    );
  }

  function getClusterNarrative(sortedDomains) {
    if (!sortedDomains || sortedDomains.length === 0) {
      return "Complete assessments to analyze student talent clusters and generate custom curriculum strategies.";
    }
    
    const top1 = sortedDomains[0]?.[0];
    const top2 = sortedDomains[1]?.[0];
    
    if (!top2) {
      return `We observe a singular focus in the ${top1} domain. Establish introductory groups to nurture this potential.`;
    }

    const keys = [top1, top2].sort().join("-");
    
    const narrativeMap = {
      "creative-logical": "STEAM Fusion: A strong combination of analytical minds and creative spirits. We recommend projects like block coding with visual design, generative art, and building customized puzzles.",
      "logical-spatial": "Engineering & Tinkering: Strong spatial reasoning paired with logical aptitude. Prioritize hands-on physics modeling, robotics assembly, electronics kit-making, or woodwork designs.",
      "creative-spatial": "Maker Crafts & Design: High visual-spatial skills combined with creative artistry. Students will thrive in design-build projects, building scale models, sculpture, painting, and visual installations.",
      "language-social": "Community Advocates & Debaters: Prominent linguistic ability and peer leadership. Perfect alignment for Model UN, structured debate groups, collaborative storytelling, drama, or running community-focused journals.",
      "creative-language": "Expressive Arts & Storytellers: Strong artistic expression coupled with language competency. Excellent for scriptwriting, illustrated storytelling, poetry slams, theater productions, or comic creation.",
      "kinesthetic-social": "Cooperative Sports & Drama: Physical agility and active social coordination. Ideal for team sports tournaments, collaborative dance productions, street play acting, or outdoor leadership camps.",
      "naturalist-spatial": "Eco-Builders & Eco-Tech: Naturalist observation combined with spatial construction. Focus on planting system design, nature-mapping boards, building bird feeders, composting model construction, or soil chemistry tools.",
      "intrapersonal-language": "Reflective Writers & Thinkers: Self-awareness coupled with language strengths. Encourage journaling circles, creative writing workshops, personal goal-setting plans, and individual reading programs.",
      "intrapersonal-logical": "Problem-Solvers & Strategists: Analytical skills paired with a reflective mindset. Highly suited for independent coding challenges, chess instruction, logic puzzles, and strategic scientific research projects."
    };

    if (narrativeMap[keys]) {
      return narrativeMap[keys];
    }
    
    const label1 = DOMAINS[top1]?.label || top1;
    const label2 = DOMAINS[top2]?.label || top2;
    return `Multi-disciplinary Opportunities: The dominant talent clusters are ${label1} and ${label2}. Consider hosting collaborative workshops that blend these two domains to encourage peer learning and cross-domain development.`;
  }

  return (
    <div style={{ maxWidth: "1200px", margin: "0 auto", padding: "20px 15px" }}>
      {/* Header Banner */}
      <div className="page-header" style={{ marginBottom: "24px" }}>
        <div className="page-header-row" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "12px" }}>
          <div>
            <h1 style={{ margin: 0, fontSize: "28px", fontWeight: 800, color: "#1e1b4b" }}>GOAT Talent Management Portal</h1>
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
            <button className="btn btn-outline" onClick={() => setShowPassModal(true)}>
              🔑 Change Password
            </button>
            <button
              className="btn btn-outline"
              title="Clear all cached assessment data for a fresh talent evaluation session"
              style={{ color: "#059669", borderColor: "#059669" }}
              onClick={async () => {
                if (confirm("This will clear all cached assessment data and sign you out. Proceed with a fresh talent assessment session?")) {
                  await supabase.auth.signOut().catch(() => {});
                  clearAllCache();
                  navigate("/login");
                }
              }}
            >
              🗑️ Clear Cache
            </button>
            <button className="btn btn-outline" onClick={async () => {
              await supabase.auth.signOut().catch(() => {});
              clearAllCache();
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

        {(role === "master_admin" || role === "admin") && (
          <button className={`btn ${activeTab === "users" ? "btn-primary" : "btn-ghost"}`} onClick={() => setActiveTab("users")}>
            👥 User Accounts
          </button>
        )}

        {role === "master_admin" && (
          <>
            <button className={`btn ${activeTab === "centers" ? "btn-primary" : "btn-ghost"}`} onClick={() => setActiveTab("centers")}>
              🏢 Center Registry
            </button>
            <button className={`btn ${activeTab === "puzzles" ? "btn-primary" : "btn-ghost"}`} onClick={() => setActiveTab("puzzles")}>
              🧩 Question Bank
            </button>
            <button className={`btn ${activeTab === "science" ? "btn-primary" : "btn-ghost"}`} onClick={() => setActiveTab("science")}>
              🔬 Scientific Foundations
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

              {/* TALENT INTELLIGENCE & RECOMMENDATIONS SECTION */}
              <div style={{ margin: "28px 0" }}>
                <h2 style={{ fontSize: "22px", fontWeight: 800, color: "#1e1b4b", marginBottom: "18px", display: "flex", alignItems: "center", gap: "8px" }}>
                  <span>🎯</span> Talent Intelligence & Nurturing Recommendations
                </h2>
                
                <div className="grid-2" style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(450px, 1fr))", gap: "24px", marginBottom: "24px" }}>
                  
                  {/* Talent Clusters Card */}
                  <div className="card" style={{ padding: "24px", borderRadius: "16px", display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
                    <div>
                      <h3 style={{ fontSize: "18px", fontWeight: 800, margin: "0 0 12px 0", color: "#1e1b4b", display: "flex", alignItems: "center", gap: "8px" }}>
                        <span>🧬</span> Center Talent Clusters
                      </h3>
                      <p className="text-light" style={{ fontSize: "14px", margin: "0 0 16px 0", lineHeight: "1.5" }}>
                        Aggregated analysis of top talent domains and secondary potentials across all active student assessments.
                      </p>
                      
                      {aggregates.sortedDomains.length > 0 ? (
                        <div>
                          <div style={{ display: "flex", flexDirection: "column", gap: "10px", marginBottom: "16px" }}>
                            {aggregates.sortedDomains.slice(0, 3).map(([dom, val], idx) => {
                              const d = DOMAINS[dom] || { emoji: "⭐", label: dom, color: "#5b4cf0" };
                              const totalWeight = aggregates.sortedDomains.reduce((acc, curr) => acc + curr[1], 0);
                              const ratio = Math.round((val / (totalWeight || 1)) * 100);
                              return (
                                <div key={dom} style={{ display: "flex", alignItems: "center", gap: "12px", background: "#f9fafb", padding: "10px 14px", borderRadius: "12px", borderLeft: `4px solid ${d.color}`, border: "1px solid #e5e7eb", borderLeftWidth: "4px" }}>
                                  <span style={{ fontSize: "22px" }}>{d.emoji}</span>
                                  <div style={{ flex: 1 }}>
                                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
                                      <span style={{ fontWeight: 700, fontSize: "14.5px", color: "#1e1b4b" }}>{d.label}</span>
                                      <span style={{ fontSize: "12px", fontWeight: 700, color: d.color }}>Weight: {val.toFixed(1)}</span>
                                    </div>
                                    <div style={{ fontSize: "12px", color: "#6b7280", marginTop: "2px" }}>
                                      Rank #{idx + 1} Cluster · Contributing {ratio}% of center's overall talent profile.
                                    </div>
                                  </div>
                                </div>
                              );
                            })}
                          </div>
                          
                          <div style={{ background: "linear-gradient(135deg, #f5f3ff 0%, #eef2ff 100%)", padding: "16px", borderRadius: "12px", border: "1px solid rgba(91, 76, 240, 0.15)", fontSize: "14px", lineHeight: "1.6", color: "#3730a3" }}>
                            <strong>💡 Educational Strategy:</strong> {getClusterNarrative(aggregates.sortedDomains)}
                          </div>
                        </div>
                      ) : (
                        <div style={{ color: "#9ca3af", textAlign: "center", padding: "20px 0" }}>No completed assessments to generate clusters.</div>
                      )}
                    </div>
                  </div>

                  {/* Aggregate Workshop Recommendations */}
                  <div className="card" style={{ padding: "24px", borderRadius: "16px" }}>
                    <h3 style={{ fontSize: "18px", fontWeight: 800, margin: "0 0 12px 0", color: "#1e1b4b", display: "flex", alignItems: "center", gap: "8px" }}>
                      <span>🛠️</span> Demanded Workshops (Aggregated Recommendations)
                    </h3>
                    <p className="text-light" style={{ fontSize: "14px", margin: "0 0 16px 0", lineHeight: "1.5" }}>
                      Cumulative workshop demands recommended to nurture active student profiles in this center.
                    </p>
                    
                    <div style={{ display: "flex", flexDirection: "column", gap: "12px", maxHeight: "320px", overflowY: "auto", paddingRight: "4px" }}>
                      {aggregates.workshopCounts.length > 0 ? (
                        aggregates.workshopCounts.map(ws => {
                          const domainKey = Object.keys(DOMAINS).find(k => {
                            const map = {
                              "creative": "Art & Design",
                              "logical": "STEM & Coding",
                              "spatial": "Tinkering & Making",
                              "social": "Peer Leadership",
                              "language": "Debate & Storytelling",
                              "naturalist": "Young Naturalist Trails",
                              "kinesthetic": "Sports & Movement",
                              "intrapersonal": "Goal Setting & Reflective Writing"
                            };
                            return map[k] === ws.title;
                          });
                          const d = DOMAINS[domainKey] || { emoji: "📚", color: "#4b5563", light: "#f3f4f6" };
                          
                          return (
                            <div key={ws.title} style={{ border: "1px solid #e5e7eb", borderRadius: "12px", padding: "12px 16px", display: "flex", gap: "12px", background: "#fff" }}>
                              <span style={{ fontSize: "24px", background: d.light, borderRadius: "8px", width: "42px", height: "42px", display: "flex", alignItems: "center", justifyContent: "center" }}>{d.emoji}</span>
                              <div style={{ flex: 1 }}>
                                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                                  <span style={{ fontWeight: 800, fontSize: "14.5px", color: "#1e1b4b" }}>{ws.title}</span>
                                  <span className="domain-badge" style={{ background: d.light, color: d.color, fontSize: "11px", fontWeight: 700 }}>
                                    {ws.count} {ws.count === 1 ? "student" : "students"}
                                  </span>
                                </div>
                                <div style={{ fontSize: "13px", color: "#4b5563", marginTop: "4px" }}>{ws.desc}</div>
                                <div style={{ fontSize: "11px", color: "#6b7280", marginTop: "6px", fontStyle: "italic" }}>
                                  Target: {ws.students.slice(0, 4).join(", ")}{ws.students.length > 4 ? ` (+${ws.students.length - 4} more)` : ""}
                                </div>
                              </div>
                            </div>
                          );
                        })
                      ) : (
                        <div style={{ color: "#9ca3af", textAlign: "center", padding: "20px 0" }}>No workshops recommended yet. Complete assessments first.</div>
                      )}
                    </div>
                  </div>

                </div>

                <div className="grid-2" style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(450px, 1fr))", gap: "24px", marginBottom: "24px" }}>
                  
                  {/* High-Potential Students Card */}
                  <div className="card" style={{ padding: "24px", borderRadius: "16px" }}>
                    <h3 style={{ fontSize: "18px", fontWeight: 800, margin: "0 0 12px 0", color: "#1e1b4b", display: "flex", alignItems: "center", gap: "8px" }}>
                      <span>🚀</span> High-Potential Students (Stretched Domain Score ≥ 85%)
                    </h3>
                    <p className="text-light" style={{ fontSize: "14px", margin: "0 0 16px 0", lineHeight: "1.5" }}>
                      Students exhibiting outstanding aptitude. Provide advanced mentoring or accelerated learning opportunities.
                    </p>
                    
                    <div style={{ display: "flex", flexDirection: "column", gap: "10px", maxHeight: "320px", overflowY: "auto", paddingRight: "4px" }}>
                      {aggregates.highPotentialStudents.length > 0 ? (
                        aggregates.highPotentialStudents.map(student => (
                          <div key={student.id} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", background: "#f9fafb", padding: "10px 14px", borderRadius: "12px", border: "1px solid #e5e7eb" }}>
                            <div style={{ flex: 1, marginRight: "10px" }}>
                              <div style={{ fontWeight: 700, fontSize: "14.5px", color: "#1e1b4b" }}>
                                {student.name} <span style={{ fontSize: "12px", color: "#6b7280", fontWeight: 500 }}>(Age {student.age} · {student.center})</span>
                              </div>
                              <div style={{ display: "flex", gap: "6px", marginTop: "6px", flexWrap: "wrap" }}>
                                {student.highDomains.map(dInfo => {
                                  const d = DOMAINS[dInfo.domain] || { emoji: "⭐", label: dInfo.domain, color: "#4b5563" };
                                  return (
                                    <span key={dInfo.domain} style={{ fontSize: "11px", fontWeight: 700, background: "#f3f4f6", border: `1px solid ${d.color}20`, padding: "2px 6px", borderRadius: "6px", color: d.color, display: "flex", alignItems: "center", gap: "4px" }}>
                                      <span>{d.emoji}</span> {d.label.split(" ")[0]} ({dInfo.score}%)
                                    </span>
                                  );
                                })}
                              </div>
                            </div>
                            <button className="btn btn-ghost btn-sm" style={{ fontWeight: 700, color: "#5b4cf0", whiteSpace: "nowrap" }} onClick={() => navigate(`/results/${student.latest_session_id}?cid=${student.id}`)}>
                              View Report
                            </button>
                          </div>
                        ))
                      ) : (
                        <div style={{ color: "#9ca3af", textAlign: "center", padding: "20px 0" }}>No high-potential students identified yet (Stretched score ≥ 85%).</div>
                      )}
                    </div>
                  </div>

                  {/* Low-Exposure Opportunities Card (TEG gaps) */}
                  <div className="card" style={{ padding: "24px", borderRadius: "16px" }}>
                    <h3 style={{ fontSize: "18px", fontWeight: 800, margin: "0 0 12px 0", color: "#1e1b4b", display: "flex", alignItems: "center", gap: "8px" }}>
                      <span>🔍</span> Untapped Talent Exposure Gaps (TEG)
                    </h3>
                    <p className="text-light" style={{ fontSize: "14px", margin: "0 0 16px 0", lineHeight: "1.5" }}>
                      Children with high natural talent but low exposure. Prioritize enrolling these students in relevant workshops.
                    </p>
                    
                    <div style={{ display: "flex", flexDirection: "column", gap: "10px", maxHeight: "320px", overflowY: "auto", paddingRight: "4px" }}>
                      {aggregates.lowExposureStudents.length > 0 ? (
                        aggregates.lowExposureStudents.map(student => (
                          <div key={student.id} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", background: "#fffbf2", padding: "10px 14px", borderRadius: "12px", border: "1px solid #fde68a" }}>
                            <div style={{ flex: 1, marginRight: "10px" }}>
                              <div style={{ fontWeight: 700, fontSize: "14.5px", color: "#854F0B" }}>
                                {student.name} <span style={{ fontSize: "12px", color: "#b45309", fontWeight: 500 }}>(Age {student.age} · {student.center})</span>
                              </div>
                              <div style={{ display: "flex", gap: "6px", marginTop: "6px", flexWrap: "wrap" }}>
                                {student.lowExpDomains.map(dInfo => {
                                  const d = DOMAINS[dInfo.domain] || { emoji: "⭐", label: dInfo.domain, color: "#854F0B" };
                                  return (
                                    <span key={dInfo.domain} style={{ fontSize: "11px", fontWeight: 700, background: "#fffbeb", border: "1px solid #fcd34d", padding: "2px 6px", borderRadius: "6px", color: "#b45309", display: "flex", alignItems: "center", gap: "4px" }}>
                                      <span>{d.emoji}</span> {d.label.split(" ")[0]} (Aptitude: {dInfo.talent_score}% | Exposure: {dInfo.exposure_score}%)
                                    </span>
                                  );
                                })}
                              </div>
                            </div>
                            <button className="btn btn-ghost btn-sm" style={{ fontWeight: 700, color: "#b45309", whiteSpace: "nowrap" }} onClick={() => navigate(`/results/${student.latest_session_id}?cid=${student.id}`)}>
                              View Report
                            </button>
                          </div>
                        ))
                      ) : (
                        <div style={{ color: "#9ca3af", textAlign: "center", padding: "20px 0" }}>No significant talent exposure gaps found.</div>
                      )}
                    </div>
                  </div>

                </div>
              </div>

              {/* Data Exporter Component */}
              {(role === "master_admin" || role === "admin") && (
                <div className="card" style={{ padding: "20px", borderRadius: "12px", background: "linear-gradient(135deg, #f5f3ff 0%, #edd8ff 100%)", display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "16px" }}>
                  <div>
                    <h3 style={{ margin: 0, fontWeight: 800, color: "#4c1d95" }}>📥 Longitudinal Talent Data Export</h3>
                    <p style={{ margin: "4px 0 0 0", fontSize: "13px", color: "#6d28d9" }}>Download standard CSV format comprising registered profiles, top domain results, and test scores.</p>
                  </div>
                  <a href={`${BASE}/export/csv`} download className="btn btn-primary" style={{ background: "#5b4cf0" }}>
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
      {activeTab === "users" && (role === "master_admin" || role === "admin") && (
        <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
          
          {/* Pending Approvals Section */}
          {pendingUsers.length > 0 && (
            <div className="card" style={{ padding: "24px", borderRadius: "16px", border: "2px solid #5b4cf0", background: "#fcfcff" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "16px" }}>
                <span style={{ fontSize: "24px" }}>⏳</span>
                <h2 style={{ fontSize: "20px", fontWeight: 800, color: "#1e1b4b", margin: 0 }}>Pending Account Approvals</h2>
              </div>
              <p className="text-light" style={{ fontSize: "14px", marginBottom: "20px" }}>
                The following users self-registered and require approval. Please assign them a role and optional center to grant them system access.
              </p>
              
              <div className="table-wrap">
                <table className="goat-table">
                  <thead>
                    <tr>
                      <th>Name</th>
                      <th>Email Address</th>
                      <th>Requested Role</th>
                      <th>Assign Center</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {pendingUsers.map(u => {
                      const reqRole = u.role.replace("pending_", "");
                      return (
                        <tr key={u.id}>
                          <td style={{ fontWeight: 700 }}>{u.name}</td>
                          <td>{u.email}</td>
                          <td>
                            <span className="domain-badge" style={{ background: "#e0f2fe", color: "#0369a1", fontSize: "11px", fontWeight: 700 }}>
                              {reqRole.toUpperCase()} (PENDING)
                            </span>
                          </td>
                          <td>
                            <select 
                              id={`center-select-${u.id}`}
                              style={{ height: "32px", border: "1.5px solid #d1d5db", borderRadius: "6px", fontSize: "13px", padding: "0 4px" }}
                            >
                              <option value="">-- No Center --</option>
                              {centers.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                            </select>
                          </td>
                          <td>
                            <div style={{ display: "flex", gap: "8px" }}>
                              <button 
                                className="btn btn-primary btn-sm" 
                                style={{ background: "#10b981", borderColor: "#10b981", fontWeight: 700 }}
                                onClick={async () => {
                                  const selCenter = document.getElementById(`center-select-${u.id}`)?.value || null;
                                  try {
                                    await api.approveUser(u.id, { role: reqRole, center_id: selCenter });
                                    setFormMsg(`Successfully approved ${u.name} as ${reqRole.toUpperCase()}`);
                                    const allUsers = await api.getUsers();
                                    setUsers(allUsers);
                                  } catch (err) {
                                    alert("Failed to approve user.");
                                  }
                                }}
                              >
                                Approve
                              </button>
                              <button 
                                className="btn btn-ghost btn-sm" 
                                style={{ color: "#ef4444", fontWeight: 700 }}
                                onClick={async () => {
                                  if (confirm(`Reject and delete registration for ${u.name}?`)) {
                                    try {
                                      await api.deleteUser(u.id);
                                      setFormMsg(`Rejected registration for ${u.name}`);
                                      const allUsers = await api.getUsers();
                                      setUsers(allUsers);
                                    } catch (err) {
                                      alert("Failed to reject user.");
                                    }
                                  }
                                }}
                              >
                                Reject
                              </button>
                            </div>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* User Creator & List Grid */}
          <div className="grid-3" style={{ display: "grid", gridTemplateColumns: "1fr 2fr", gap: "24px" }}>
            {/* Add User Panel */}
            <div className="card" style={{ padding: "20px", borderRadius: "12px", height: "fit-content" }}>
              <h3 style={{ margin: "0 0 16px 0", fontWeight: 800 }}>Add System Account</h3>
              <form onSubmit={async (e) => {
                e.preventDefault();
                try {
                  // Sign up on Supabase Auth
                  const { data, error } = await supabase.auth.signUp({
                    email: newUser.email,
                    password: newUser.password,
                    options: {
                      data: {
                        name: newUser.name,
                        role: newUser.role
                      }
                    }
                  });
                  if (error) throw error;
                  
                  setFormMsg(`Successfully registered user ${newUser.name} on Supabase!`);
                  setNewUser({ name: "", email: "", password: "", role: "facilitator", center_id: "" });
                  const u = await api.getUsers();
                  setUsers(u);
                } catch (err) {
                  console.error("Supabase signUp failed, trying fallback:", err);
                  // Fallback for offline SQLite mode
                  try {
                    await api.createUser(newUser);
                    setFormMsg(`Successfully created local user: ${newUser.name}`);
                    setNewUser({ name: "", email: "", password: "", role: "facilitator", center_id: "" });
                    const u = await api.getUsers();
                    setUsers(u);
                  } catch (fallbackErr) {
                    alert("Failed to create account. Check if email is unique.");
                  }
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
                    {activeUsers.map(u => (
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
          {(() => {
            const filteredChildren = children.filter(c => {
              if (!selectedCenterFilter) return true;
              if (selectedCenterFilter === "Unassigned") return !c.center_name;
              return c.center_name === selectedCenterFilter;
            });

            return (
              <div className="card" style={{ padding: "20px", borderRadius: "12px" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px", flexWrap: "wrap", gap: "10px" }}>
                  <h3 style={{ margin: 0, fontWeight: 800 }}>Children Records & Development Timeline</h3>
                  <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                    <span style={{ fontSize: "14px", fontWeight: 600, color: "#4b5563" }}>Filter by Centre:</span>
                    <select
                      value={selectedCenterFilter}
                      onChange={e => setSelectedCenterFilter(e.target.value)}
                      style={{ height: "36px", border: "1.5px solid #d1d5db", borderRadius: "8px", padding: "0 8px", fontSize: "14px", background: "#fff" }}
                    >
                      <option value="">All Centres</option>
                      <option value="Khadar Centre">Khadar Centre</option>
                      <option value="Okhla Centre">Okhla Centre</option>
                      <option value="Govindpuri Centre">Govindpuri Centre</option>
                      <option value="Yamuna Centre">Yamuna Centre</option>
                      <option value="Unassigned">Unassigned</option>
                    </select>
                  </div>
                </div>
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
                      {filteredChildren.map(c => (
                        <tr key={c.id}>
                          <td style={{ fontWeight: 600 }}>{c.name}</td>
                          <td>{c.age}</td>
                          <td>{c.center_name || "Unassigned"}</td>
                          <td>
                            <button className="btn btn-ghost btn-sm" onClick={async () => {
                              const v = await api.getMentorValidations(c.id).catch(() => []);
                              alert(`Validation Logs for ${c.name}:\n\n` + (v.length === 0 ? "No evaluations logged." : v.map(x => `Domain: ${x.domain.toUpperCase()} | Rating: ${x.rating}/5 stars\nStrengths: ${x.strengths || "N/A"}\nNotes: ${x.notes || "N/A"}`).join("\n\n")));
                            }}>View Developmental Log</button>
                          </td>
                        </tr>
                      ))}
                      {filteredChildren.length === 0 && (
                        <tr>
                          <td colSpan={4} style={{ textAlign: "center", color: "#9ca3af", padding: "20px 0" }}>
                            No children registered in this centre yet.
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            );
          })()}
        </div>
      )}

      {/* CHILDREN RECORDS TAB */}
      {activeTab === "children" && (() => {
        const filteredChildren = children.filter(c => {
          if (!selectedCenterFilter) return true;
          if (selectedCenterFilter === "Unassigned") return !c.center_name;
          return c.center_name === selectedCenterFilter;
        });

        return (
          <div className="card" style={{ padding: "20px", borderRadius: "12px" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px", flexWrap: "wrap", gap: "10px" }}>
              <h3 style={{ margin: 0, fontWeight: 800 }}>Assessments & Registry List</h3>
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <span style={{ fontSize: "14px", fontWeight: 600, color: "#4b5563" }}>Filter by Centre:</span>
                <select
                  value={selectedCenterFilter}
                  onChange={e => setSelectedCenterFilter(e.target.value)}
                  style={{ height: "36px", border: "1.5px solid #d1d5db", borderRadius: "8px", padding: "0 8px", fontSize: "14px", background: "#fff" }}
                >
                  <option value="">All Centres</option>
                  <option value="Khadar Centre">Khadar Centre</option>
                  <option value="Okhla Centre">Okhla Centre</option>
                  <option value="Govindpuri Centre">Govindpuri Centre</option>
                  <option value="Yamuna Centre">Yamuna Centre</option>
                  <option value="Unassigned">Unassigned</option>
                </select>
              </div>
            </div>
            <div className="table-wrap">
              <table className="goat-table">
                <thead>
                  <tr>
                    <th>Student Name</th>
                    <th>Age</th>
                    <th>Class</th>
                    <th>Gender</th>
                    <th>Centre</th>
                    <th>Assessed Top Talent</th>
                    <th>Registry Date</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredChildren.map(c => (
                    <ChildRecordRow key={c.id} child={c} navigate={navigate} role={role} />
                  ))}
                  {filteredChildren.length === 0 && (
                    <tr>
                      <td colSpan={8} style={{ textAlign: "center", color: "#9ca3af", padding: "20px 0" }}>
                        No children registered in this centre yet.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        );
      })()}

      {/* SCIENTIFIC FOUNDATIONS TAB */}
      {activeTab === "science" && role === "master_admin" && (
        <div className="card" style={{ padding: "32px", borderRadius: "16px" }}>
          <div style={{ borderBottom: "2px solid #e5e7eb", paddingBottom: "16px", marginBottom: "24px" }}>
            <span className="domain-badge" style={{ background: "#fee2e2", color: "#dc2626", fontWeight: 700 }}>CONFIDENTIAL — FOR INTERNAL USE & STAKEHOLDER REVIEW</span>
            <h2 style={{ fontSize: "28px", fontWeight: 900, color: "#1e1b4b", marginTop: "8px" }}>Scientific Foundations & System Design</h2>
          </div>

          <div style={{ marginBottom: "32px", textAlign: "center" }}>
            <img 
              src="/multiple_intelligences_grid.png" 
              alt="Multiple Intelligences Grid" 
              style={{ maxWidth: "600px", width: "100%", borderRadius: "16px", border: "1px solid #e5e7eb", boxShadow: "0 10px 25px rgba(0,0,0,0.05)" }}
            />
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "32px" }}>
            {/* Executive Summary */}
            <div>
              <h3 style={{ fontSize: "20px", fontWeight: 800, color: "#1e1b4b", borderLeft: "4px solid #5b4cf0", paddingLeft: "12px", marginBottom: "12px" }}>Executive Summary</h3>
              <p style={{ color: "#4b5563", lineHeight: "1.7", fontSize: "15px" }}>
                This note establishes the credibility of the <strong>Greatest of All Talents System (GOAT)</strong> proposed for <strong>Project WHY, New Delhi</strong>. It sets out the scientific foundations of the system's design, the rationale for its framework choices, the limitations of comparable existing tools, and the specific design decisions made to address the realities of underprivileged children aged 9–15 in an Indian urban context.
              </p>
              <div style={{ background: "#eef2ff", border: "1.5px solid #c7d2fe", color: "#3730a3", padding: "16px", borderRadius: "12px", fontSize: "14.5px", lineHeight: "1.6", marginTop: "16px" }}>
                <strong>Core Claim:</strong> GOAT is a five-phase, evidence-grounded system for identifying and nurturing natural talent in children aged 9–15, designed to be bias-aware, literacy-independent in its discovery phase, mother-tongue-compatible, and validated by trained facilitator observation — not algorithmic output alone.
              </div>
            </div>

            {/* Section 1 */}
            <div>
              <h3 style={{ fontSize: "20px", fontWeight: 800, color: "#1e1b4b", borderLeft: "4px solid #5b4cf0", paddingLeft: "12px", marginBottom: "12px" }}>1. The Problem We Are Solving</h3>
              <p style={{ color: "#4b5563", lineHeight: "1.7", fontSize: "15px" }}>
                India produces approximately <strong>14.5 million school dropouts per year</strong>, the majority from economically disadvantaged urban and semi-urban households. Research consistently shows that the primary driver is not lack of ability — it is the failure of educational systems to identify, validate, and nurture the specific abilities each child naturally possesses.
              </p>
              <p style={{ color: "#4b5563", lineHeight: "1.7", fontSize: "15px" }}>
                The system works with children in underserved communities. These children face compounding disadvantages:
              </p>
              <ul style={{ paddingLeft: "20px", color: "#4b5563", lineHeight: "1.6", fontSize: "14.5px" }}>
                <li style={{ marginBottom: "8px" }}><strong>Limited exposure to diverse domains:</strong> Most have never painted, played an instrument, or used a computer before arriving at the program.</li>
                <li style={{ marginBottom: "8px" }}><strong>Assessment in a second or third language (English):</strong> This systematically suppresses performance on verbal and linguistic tasks.</li>
                <li style={{ marginBottom: "8px" }}><strong>No existing formal mechanism:</strong> Lack of structural tools to identify talent outside of standard academic performance and sports.</li>
                <li style={{ marginBottom: "8px" }}><strong>Social and familial pressure:</strong> Heavy pressure to pursue immediate income-generating paths rather than talent-aligned ones.</li>
              </ul>
            </div>

            {/* Section 2 */}
            <div>
              <h3 style={{ fontSize: "20px", fontWeight: 800, color: "#1e1b4b", borderLeft: "4px solid #5b4cf0", paddingLeft: "12px", marginBottom: "12px" }}>2. Scientific Foundations</h3>
              <p style={{ color: "#4b5563", lineHeight: "1.7", fontSize: "15px", marginBottom: "20px" }}>
                The system draws on four independently validated research traditions. These represent the mainstream of talent science as of 2026 and are cross-referenced to identify areas of convergence:
              </p>

              <div style={{ background: "#f9fafb", border: "1px solid #e5e7eb", padding: "18px", borderRadius: "12px", marginBottom: "16px" }}>
                <h4 style={{ color: "#5b4cf0", fontSize: "15px", fontWeight: 800, margin: "0 0 8px 0" }}>2.1 Cattell-Horn-Carroll (CHC) Theory of Cognitive Abilities</h4>
                <p style={{ color: "#4b5563", fontSize: "14px", margin: 0, lineHeight: "1.6" }}>
                  CHC theory is the most psychometrically validated model of human cognitive ability, developed over six decades of factor-analytic research. It identifies broad ability domains—including fluid intelligence (Gf), crystallized intelligence (Gc), visual-spatial processing (Gv), short-term memory, and psychomotor speed—each with established independence. GOAT uses CHC's taxonomy as the backbone for its 8-domain framework.
                </p>
              </div>

              <div style={{ background: "#f9fafb", border: "1px solid #e5e7eb", padding: "18px", borderRadius: "12px", marginBottom: "16px" }}>
                <h4 style={{ color: "#5b4cf0", fontSize: "15px", fontWeight: 800, margin: "0 0 8px 0" }}>2.2 Howard Gardner's Theory of Multiple Intelligences</h4>
                <p style={{ color: "#4b5563", fontSize: "14px", margin: 0, lineHeight: "1.6" }}>
                  Gardner's framework identified 8 intelligences, challenging the dominant view that intelligence is a single general factor (g). While facing criticism for psychometric validation, Gardner's framework provides a child-accessible conceptual map that provides an effective linguistic bridge to children and facilitators.
                </p>
              </div>

              <div style={{ background: "#f9fafb", border: "1px solid #e5e7eb", padding: "18px", borderRadius: "12px", marginBottom: "16px" }}>
                <h4 style={{ color: "#5b4cf0", fontSize: "15px", fontWeight: 800, margin: "0 0 8px 0" }}>2.3 Gagné's Differentiated Model of Giftedness and Talent (DMGT)</h4>
                <p style={{ color: "#4b5563", fontSize: "14px", margin: 0, lineHeight: "1.6" }}>
                  Gagné's DMGT is critical for one specific design decision in GOAT: the distinction between <strong>natural abilities (aptitudes)</strong> and <strong>developed talents (systematically trained skills)</strong>. This prevents the system from confusing exposure with ability. It also establishes the basis for GOAT Phase 4 (facilitator review) and Phase 5 (mentor matching).
                </p>
              </div>

              <div style={{ background: "#f9fafb", border: "1px solid #e5e7eb", padding: "18px", borderRadius: "12px", marginBottom: "20px" }}>
                <h4 style={{ color: "#5b4cf0", fontSize: "15px", fontWeight: 800, margin: "0 0 8px 0" }}>2.4 Torrance's Creativity Research & Divergent Thinking</h4>
                <p style={{ color: "#4b5563", fontSize: "14px", margin: 0, lineHeight: "1.6" }}>
                  E. Paul Torrance's longitudinal research demonstrated that divergent thinking is a measurable, stable ability in children from age 8 onwards, and is a stronger predictor of adult creative achievement than IQ. Domain 2 (Creative & Artistic) in GOAT uses Torrance-inspired task types (picture completion, unusual uses) that are image-based and literacy-independent.
                </p>
              </div>

              {/* Framework table */}
              <div style={{ overflowX: "auto", border: "1px solid #e5e7eb", borderRadius: "12px", marginTop: "24px" }}>
                <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "14px", background: "#fff" }}>
                  <thead>
                    <tr style={{ background: "#f9fafb", borderBottom: "2px solid #e5e7eb" }}>
                      <th style={{ textAlign: "left", padding: "12px 16px", color: "#5b4cf0", fontWeight: 800 }}>Framework / Source</th>
                      <th style={{ textAlign: "left", padding: "12px 16px", color: "#5b4cf0", fontWeight: 800 }}>How it supports this system</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr style={{ borderBottom: "1px solid #e5e7eb" }}>
                      <td style={{ padding: "12px 16px", fontWeight: 700 }}>CHC Theory</td>
                      <td style={{ padding: "12px 16px", color: "#4b5563" }}>Maps each GOAT domain to an independently validated cognitive ability construct.</td>
                    </tr>
                    <tr style={{ borderBottom: "1px solid #e5e7eb" }}>
                      <td style={{ padding: "12px 16px", fontWeight: 700 }}>Gardner (1983)</td>
                      <td style={{ padding: "12px 16px", color: "#4b5563" }}>Provides child-accessible language and 8-way domain taxonomy used in GOAT.</td>
                    </tr>
                    <tr style={{ borderBottom: "1px solid #e5e7eb" }}>
                      <td style={{ padding: "12px 16px", fontWeight: 700 }}>Gagné DMGT</td>
                      <td style={{ padding: "12px 16px", color: "#4b5563" }}>Basis for separating aptitude from exposure; justifies facilitator layer.</td>
                    </tr>
                    <tr style={{ borderBottom: "1px solid #e5e7eb" }}>
                      <td style={{ padding: "12px 16px", fontWeight: 700 }}>Torrance TTCT</td>
                      <td style={{ padding: "12px 16px", color: "#4b5563" }}>Validates picture-based, literacy-independent creativity assessment.</td>
                    </tr>
                    <tr style={{ borderBottom: "1px solid #e5e7eb" }}>
                      <td style={{ padding: "12px 16px", fontWeight: 700 }}>Mayer-Salovey EQ</td>
                      <td style={{ padding: "12px 16px", color: "#4b5563" }}>Basis for the EQ component in Phase 3 integrated scoring.</td>
                    </tr>
                    <tr>
                      <td style={{ padding: "12px 16px", fontWeight: 700 }}>Raven's Matrices</td>
                      <td style={{ padding: "12px 16px", color: "#4b5563" }}>Supports short, culturally fair fluid intelligence assessment in Domain 3.</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            {/* Section 4 */}
            <div>
              <h3 style={{ fontSize: "20px", fontWeight: 800, color: "#1e1b4b", borderLeft: "4px solid #5b4cf0", paddingLeft: "12px", marginBottom: "12px" }}>3. Why Existing Tools Are Insufficient</h3>
              <p style={{ color: "#4b5563", lineHeight: "1.7", fontSize: "15px" }}>
                Several established tools address related problems but fall short for our specific population:
              </p>
              <ul style={{ paddingLeft: "20px", color: "#4b5563", lineHeight: "1.6", fontSize: "14.5px" }}>
                <li style={{ marginBottom: "8px" }}><strong>Myers-Briggs Type Indicator (MBTI):</strong> Measures personality type, not capability. A personality classification does not tell you if a child has exceptional spatial reasoning or musical aptitude.</li>
                <li style={{ marginBottom: "8px" }}><strong>Gallup StrengthsFinder:</strong> Measures self-reported preference patterns in adults, requires strong English literacy, and is not validated for children under 15.</li>
                <li style={{ marginBottom: "8px" }}><strong>ProMytheUs:</strong> The closest comparable tool. However, it lacks a human validation layer, has no published inter-rater reliability data, and displays significant English-language bias.</li>
              </ul>
              <div style={{ background: "#d1f7ec", border: "1.5px solid rgba(0, 184, 148, 0.2)", color: "#00b894", padding: "16px", borderRadius: "12px", fontSize: "14.5px", lineHeight: "1.6", marginTop: "16px" }}>
                <strong>Key Differentiator:</strong> GOAT does not replace existing tools—it builds on their valid instincts while adding three layers they lack: a published scientific framework, a mandatory human validation checkpoint, and mother-tongue compatibility in all assessment tasks.
              </div>
            </div>

            {/* Section 5 */}
            <div>
              <h3 style={{ fontSize: "20px", fontWeight: 800, color: "#1e1b4b", borderLeft: "4px solid #5b4cf0", paddingLeft: "12px", marginBottom: "12px" }}>4. Core Design Decisions & Justifications</h3>
              <ul style={{ paddingLeft: "20px", color: "#4b5563", lineHeight: "1.6", fontSize: "14.5px" }}>
                <li style={{ marginBottom: "8px" }}><strong>Literacy-Independent Discovery Phase:</strong> The discovery funnel uses picture selection, drag-and-drop, and visual puzzles—zero text reading required. Literacy levels among Delhi’s underprivileged kids vary widely; gatekeeping by reading will miss high spatial, physical, or creative talent.</li>
                <li style={{ marginBottom: "8px" }}><strong>Mother-Tongue Assessment:</strong> All language-domain tasks are administered in the child's first language (English or Hindi). A verbally gifted Hindi speaker assessed in English would represent a false negative.</li>
                <li style={{ marginBottom: "8px" }}><strong>Mandatory Facilitator Validation:</strong> No 20-minute test is an absolute verdict. A trained facilitator spends 10 minutes observing the child to capture and flag test anxiety, lucky guessing, or suppressed performance.</li>
                <li style={{ marginBottom: "8px" }}><strong>Exposure-Corrected Scoring:</strong> Records prior exposure levels. Zero-exposure children are compared against zero-exposure cohort baselines, correcting long-standing inequities in standardized testing.</li>
              </ul>
            </div>

            {/* Section 7 */}
            <div>
              <h3 style={{ fontSize: "20px", fontWeight: 800, color: "#1e1b4b", borderLeft: "4px solid #5b4cf0", paddingLeft: "12px", marginBottom: "12px" }}>5. Pilot Validation Roadmap</h3>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "16px", marginTop: "16px" }}>
                <div style={{ background: "#f9fafb", border: "1px solid #e5e7eb", borderRadius: "12px", padding: "20px" }}>
                  <h5 style={{ fontSize: "14px", fontWeight: 800, color: "#5b4cf0", margin: "0 0 8px 0" }}>Phase A — Pilot (Months 1–3)</h5>
                  <p style={{ fontSize: "13px", lineHeight: "1.5", color: "#6b7280", margin: 0 }}>Administer GOAT to 30–50 children. Compare GOAT domain output against blind facilitator assessment. Target: ≥70% concordance.</p>
                </div>
                <div style={{ background: "#f9fafb", border: "1px solid #e5e7eb", borderRadius: "12px", padding: "20px" }}>
                  <h5 style={{ fontSize: "14px", fontWeight: 800, color: "#5b4cf0", margin: "0 0 8px 0" }}>Phase B — Reliability (Months 4–6)</h5>
                  <p style={{ fontSize: "13px", lineHeight: "1.5", color: "#6b7280", margin: 0 }}>Re-administer GOAT to the same cohort 8 weeks later without intervening instruction. Target: ≥80% test-retest reliability.</p>
                </div>
                <div style={{ background: "#f9fafb", border: "1px solid #e5e7eb", borderRadius: "12px", padding: "20px" }}>
                  <h5 style={{ fontSize: "14px", fontWeight: 800, color: "#5b4cf0", margin: "0 0 8px 0" }}>Phase C — Longitudinal (Year 2)</h5>
                  <p style={{ fontSize: "13px", lineHeight: "1.5", color: "#6b7280", margin: 0 }}>Track whether children placed in mentor programs aligned with their GOAT domain show greater attendance and fulfillment than comparison groups.</p>
                </div>
              </div>
            </div>
          </div>

          <div style={{ borderTop: "1px solid #e5e7eb", marginTop: "32px", paddingTop: "16px", display: "flex", justifyContent: "space-between", fontSize: "12.5px", color: "#9ca3af", flexWrap: "wrap", gap: "12px" }}>
            <p style={{ margin: 0 }}>© 2026 GOAT Labs · Talent Systems Design Team</p>
            <p style={{ margin: 0 }}>For questions regarding the scientific basis of this system, please contact the Talent Systems Design Team.</p>
          </div>
        </div>
      )}

      {showPassModal && (
        <div style={{ position: "fixed", top: 0, left: 0, right: 0, bottom: 0, background: "rgba(0,0,0,0.5)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 2000 }}>
          <div className="card" style={{ width: "100%", maxWidth: "400px", padding: "24px", borderRadius: "12px", background: "#fff", border: "1px solid #e5e7eb", boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.1)" }}>
            <h3 style={{ margin: "0 0 16px 0", fontWeight: 800, fontSize: "18px", color: "#1e1b4b" }}>Change Portal Password</h3>
            {passError && <div style={{ color: "#dc2626", background: "#fee2e2", padding: "8px 12px", borderRadius: "6px", fontSize: "13px", marginBottom: "12px", fontWeight: 600 }}>⚠️ {passError}</div>}
            {passSuccess && <div style={{ color: "#166534", background: "#f0fdf4", padding: "8px 12px", borderRadius: "6px", fontSize: "13px", marginBottom: "12px", fontWeight: 600 }}>✅ {passSuccess}</div>}
            <form onSubmit={async (e) => {
              e.preventDefault();
              setPassError("");
              setPassSuccess("");
              try {
                await api.changePassword(passForm);
                setPassSuccess("Password updated successfully!");
                setPassForm({ old_password: "", new_password: "" });
                setTimeout(() => {
                  setShowPassModal(false);
                  setPassSuccess("");
                }, 1500);
              } catch (err) {
                setPassError("Failed to change password. Double check current password.");
              }
            }}>
              <div className="form-group" style={{ marginBottom: "12px" }}>
                <label style={{ display: "block", marginBottom: "4px", fontSize: "13px", fontWeight: 700 }}>Current Password</label>
                <input type="password" value={passForm.old_password} onChange={e => setPassForm({ ...passForm, old_password: e.target.value })} required style={{ border: "1.5px solid #d1d5db", borderRadius: "8px", height: "38px", width: "100%", padding: "0 8px", fontSize: "14px" }} />
              </div>
              <div className="form-group" style={{ marginBottom: "20px" }}>
                <label style={{ display: "block", marginBottom: "4px", fontSize: "13px", fontWeight: 700 }}>New Password</label>
                <input type="password" value={passForm.new_password} onChange={e => setPassForm({ ...passForm, new_password: e.target.value })} required style={{ border: "1.5px solid #d1d5db", borderRadius: "8px", height: "38px", width: "100%", padding: "0 8px", fontSize: "14px" }} />
              </div>
              <div style={{ display: "flex", gap: "10px", justifyContent: "flex-end" }}>
                <button type="button" className="btn btn-outline" onClick={() => { setShowPassModal(false); setPassError(""); setPassSuccess(""); }}>Cancel</button>
                <button type="submit" className="btn btn-primary" style={{ background: "#5b4cf0" }}>Update Password</button>
              </div>
            </form>
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
      <td>{child.school_year || "—"}</td>
      <td>{child.gender || "Not specified"}</td>
      <td>{child.center_name || "Unassigned"}</td>
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

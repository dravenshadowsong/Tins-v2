import { Link, useLocation, useNavigate } from "react-router-dom";
import { api } from "../api";

export default function Nav() {
  const { pathname } = useLocation();
  const navigate = useNavigate();
  const isAssessment = pathname.includes("/discovery") || pathname.includes("/assess");
  const loggedIn = Boolean(sessionStorage.getItem("goat_token"));
  const userJson = sessionStorage.getItem("goat_user");
  const user = userJson ? JSON.parse(userJson) : null;

  const handleLogout = async () => {
    try {
      await api.logout();
    } catch (e) {
      console.error("Logout request failed:", e);
    }
    sessionStorage.removeItem("goat_token");
    sessionStorage.removeItem("goat_user");
    navigate("/");
  };

  const getRoleLabel = (role) => {
    if (!role) return "";
    const roles = {
      master_admin: "Master Admin",
      admin: "Admin",
      facilitator: "Facilitator",
      mentor: "Mentor",
      pending_facilitator: "Pending Facilitator",
      pending_mentor: "Pending Mentor"
    };
    return roles[role.toLowerCase()] || role;
  };

  return (
    <nav className="top-nav">
      <Link to="/" className="brand-link">
        <span className="brand-mark">G</span>
        <span className="brand-text">
          <span className="brand-name">GOAT</span>
          <span className="brand-subtitle">Greatest of All Talents System</span>
        </span>
      </Link>

      {!isAssessment && (
        <div className="nav-actions" style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <Link to="/" className="btn btn-ghost btn-sm">Home</Link>
          {loggedIn ? (
            <>
              <Link to="/dashboard" className="btn btn-ghost btn-sm">Dashboard</Link>
              <Link to="/art-spark" className="btn btn-ghost btn-sm" style={{ color: "#8b5cf6" }}>🎨 ArtSpark</Link>
              <div style={{ display: "flex", alignItems: "center", gap: "8px", background: "rgba(108, 92, 231, 0.05)", padding: "4px 10px", borderRadius: "20px", border: "1px solid rgba(108, 92, 231, 0.15)" }}>
                <span style={{ fontSize: "11px", fontWeight: 800, background: "#5B4CF0", color: "#fff", padding: "2px 6px", borderRadius: "10px", textTransform: "uppercase" }}>
                  {getRoleLabel(user?.role)}
                </span>
                <span style={{ fontSize: "12.5px", fontWeight: 600, color: "#2D3436" }}>
                  {user?.name}
                </span>
              </div>
              <button onClick={handleLogout} className="btn btn-outline btn-sm" style={{ border: "1px solid #ff4d4f", color: "#ff4d4f", minHeight: "32px", padding: "4px 10px" }}>
                Logout
              </button>
            </>
          ) : (
            <Link to="/login" className="btn btn-primary btn-sm" style={{ minHeight: "32px", padding: "6px 16px" }}>
              Login
            </Link>
          )}
        </div>
      )}

      {isAssessment && (
        <span className="nav-status">Assessment in progress...</span>
      )}
    </nav>
  );
}


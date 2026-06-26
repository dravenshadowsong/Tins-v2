import { useState, useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { api } from "../api";
import { supabase } from "../supabaseClient";

// Clear all stale assessment/session cache on login page load
// This ensures talent assessments always start fresh
function clearAssessmentCache() {
  const keysToKeep = []; // nothing to keep — full clean slate
  sessionStorage.clear();
  // Clear any lingering Supabase auth session so a fresh login is forced
  localStorage.removeItem("sb-ubsjcfaokemckctswnzi-auth-token");
}

export default function Login() {
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const redirect = params.get("redirect");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [requestedRole, setRequestedRole] = useState("facilitator");
  const [isRegister, setIsRegister] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  const [successMsg, setSuccessMsg] = useState("");
  const [cacheCleared, setCacheCleared] = useState(false);

  // Clear assessment cache on page mount for a fresh session
  useEffect(() => {
    clearAssessmentCache();
    setCacheCleared(true);
  }, []);

  const doNavigate = (result) => {
    sessionStorage.setItem("goat_token", result.token);
    sessionStorage.setItem("goat_user", JSON.stringify(result.user));
    if (redirect) {
      navigate(redirect);
    } else {
      navigate("/dashboard");
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg("");
    setSuccessMsg("");
    try {
      // Fast path: send credentials directly to backend.
      // The backend handles Supabase auth internally, saving one extra round-trip.
      const result = await api.login({ email, password });
      doNavigate(result);
    } catch (backendErr) {
      // If backend direct login fails (e.g. Supabase-only account not yet in local DB),
      // fall back to the frontend Supabase → token exchange flow.
      try {
        const { data, error } = await supabase.auth.signInWithPassword({ email, password });
        if (error) throw error;
        const result = await api.loginSupabase({ token: data.session.access_token });
        doNavigate(result);
      } catch (fallbackErr) {
        setErrorMsg("Login failed. Please check your credentials.");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg("");
    setSuccessMsg("");
    const role = "pending_" + requestedRole;
    try {
      // 1. Sign up via Supabase Auth
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: {
            name,
            role
          }
        }
      });
      if (error) throw error;

      setSuccessMsg("Registration successful! Your account is now pending approval from a Master Admin or Admin.");
      setIsRegister(false);
      setName("");
      setEmail("");
      setPassword("");
    } catch (err) {
      console.error("Supabase registration failed, trying local fallback:", err);
      try {
        await api.register({ name, email, password, role });
        setSuccessMsg("Registration successful! Your account is now pending approval from a Master Admin or Admin.");
        setIsRegister(false);
        setName("");
        setEmail("");
        setPassword("");
      } catch (fallbackErr) {
        setErrorMsg("Registration failed. The email address may already be in use.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-layout" style={{ padding: "40px 10px" }}>
      <div style={{ width: "100%", maxWidth: "440px" }}>
        
        <form className="card" onSubmit={isRegister ? handleRegister : handleLogin} style={{ padding: "30px 24px", marginBottom: "16px", borderRadius: "16px", border: "1px solid rgba(91, 76, 240, 0.12)" }}>
          <h1 style={{ fontSize: "24px", fontWeight: 800, color: "#5B4CF0", margin: "0 0 6px 0", textAlign: "center" }}>GOAT System Portal</h1>
          <p className="text-light" style={{ fontSize: "13.5px", textAlign: "center", marginBottom: "24px" }}>
            {isRegister ? "Create a Facilitator or Mentor Account" : "Talent Identification, Validation, Nurturing & Tracking"}
          </p>

          {cacheCleared && !isRegister && (
            <div style={{ background: "#F0FDF4", border: "1px solid #BBF7D0", color: "#166534", padding: "8px 12px", borderRadius: "8px", fontSize: "12px", fontWeight: 600, marginBottom: "14px", display: "flex", alignItems: "center", gap: "6px" }}>
              ✅ Assessment cache cleared — ready for fresh talent evaluation
            </div>
          )}

          {errorMsg && (
            <div style={{ background: "#FFF5F5", border: "1px solid #FFCCC7", color: "#FF4D4F", padding: "10px 12px", borderRadius: "8px", fontSize: "13px", fontWeight: 600, marginBottom: "16px" }}>
              ⚠️ {errorMsg}
            </div>
          )}

          {successMsg && (
            <div style={{ background: "#F6FFED", border: "1px solid #B7EB8F", color: "#52C41A", padding: "10px 12px", borderRadius: "8px", fontSize: "13px", fontWeight: 600, marginBottom: "16px" }}>
              🎉 {successMsg}
            </div>
          )}

          {isRegister && (
            <div className="form-group">
              <label style={{ fontWeight: 700 }}>Full Name</label>
              <input 
                type="text" 
                value={name} 
                onChange={e => setName(e.target.value)} 
                required 
                style={{ border: "1.5px solid rgba(0,0,0,0.1)", borderRadius: "8px", fontSize: "14px" }}
              />
            </div>
          )}

          <div className="form-group">
            <label style={{ fontWeight: 700 }}>Email Address</label>
            <input 
              type="email" 
              value={email} 
              onChange={e => setEmail(e.target.value)} 
              required 
              autoComplete="email"
              style={{ border: "1.5px solid rgba(0,0,0,0.1)", borderRadius: "8px", fontSize: "14px" }}
            />
          </div>

          <div className="form-group" style={{ marginBottom: isRegister ? "16px" : "24px" }}>
            <label style={{ fontWeight: 700 }}>Password</label>
            <input 
              type="password" 
              value={password} 
              onChange={e => setPassword(e.target.value)} 
              required 
              autoComplete={isRegister ? "new-password" : "current-password"}
              style={{ border: "1.5px solid rgba(0,0,0,0.1)", borderRadius: "8px", fontSize: "14px" }}
            />
          </div>

          {isRegister && (
            <div className="form-group" style={{ marginBottom: "24px" }}>
              <label style={{ fontWeight: 700 }}>Requested System Role</label>
              <select 
                value={requestedRole} 
                onChange={e => setRequestedRole(e.target.value)} 
                style={{ width: "100%", height: "38px", border: "1.5px solid rgba(0,0,0,0.1)", borderRadius: "8px", padding: "0 8px", fontSize: "14px" }}
              >
                <option value="facilitator">🧑‍🏫 Facilitator</option>
                <option value="mentor">🤝 Mentor</option>
              </select>
            </div>
          )}

          <button className="btn btn-primary btn-full" disabled={loading} style={{ background: "#5B4CF0", fontWeight: 700, borderRadius: "8px" }}>
            {loading 
              ? (isRegister ? "Creating Account..." : "Verifying Credentials...") 
              : (isRegister ? "Register Account" : "Sign In to Portal")
            }
          </button>
          
          <div style={{ textAlign: "center", marginTop: "16px", fontSize: "14px" }}>
            {isRegister ? (
              <span className="text-light">
                Already have an account?{" "}
                <button type="button" onClick={() => { setIsRegister(false); setErrorMsg(""); }} style={{ background: "none", border: "none", color: "#5B4CF0", fontWeight: 700, cursor: "pointer", padding: 0 }}>
                  Sign In
                </button>
              </span>
            ) : (
              <span className="text-light">
                Need account credentials?{" "}
                <button type="button" onClick={() => { setIsRegister(true); setErrorMsg(""); }} style={{ background: "none", border: "none", color: "#5B4CF0", fontWeight: 700, cursor: "pointer", padding: 0 }}>
                  Register Here
                </button>
              </span>
            )}
          </div>
        </form>
      </div>
    </div>
  );
}

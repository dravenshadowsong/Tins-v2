import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";
import { supabase } from "../supabaseClient";

export default function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg("");
    try {
      // 1. Sign in via Supabase Auth client
      const { data, error } = await supabase.auth.signInWithPassword({ email, password });
      if (error) throw error;

      // 2. Exchange Supabase session token for local session
      const result = await api.loginSupabase({ token: data.session.access_token });
      localStorage.setItem("goat_token", result.token);
      localStorage.setItem("goat_user", JSON.stringify(result.user));
      navigate("/dashboard");
    } catch (err) {
      console.error("Supabase login failed, trying fallback:", err);
      // Fallback for offline testing or legacy seeded accounts
      try {
        const result = await api.login({ email, password });
        localStorage.setItem("goat_token", result.token);
        localStorage.setItem("goat_user", JSON.stringify(result.user));
        navigate("/dashboard");
      } catch (fallbackErr) {
        setErrorMsg("Login failed. Please check your credentials.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-layout" style={{ padding: "40px 10px" }}>
      <div style={{ width: "100%", maxWidth: "440px" }}>
        
        <form className="card" onSubmit={submit} style={{ padding: "30px 24px", marginBottom: "16px", borderRadius: "16px", border: "1px solid rgba(91, 76, 240, 0.12)" }}>
          <h1 style={{ fontSize: "24px", fontWeight: 800, color: "#5B4CF0", margin: "0 0 6px 0", textAlign: "center" }}>TINS System Portal</h1>
          <p className="text-light" style={{ fontSize: "13.5px", textAlign: "center", marginBottom: "24px" }}>
            Talent Identification, Validation, Nurturing &amp; Tracking
          </p>

          {errorMsg && (
            <div style={{ background: "#FFF5F5", border: "1px solid #FFCCC7", color: "#FF4D4F", padding: "10px 12px", borderRadius: "8px", fontSize: "13px", fontWeight: 600, marginBottom: "16px" }}>
              ⚠️ {errorMsg}
            </div>
          )}

          <div className="form-group">
            <label style={{ fontWeight: 700 }}>Email Address</label>
            <input 
              type="email" 
              value={email} 
              onChange={e => setEmail(e.target.value)} 
              required 
              style={{ border: "1.5px solid rgba(0,0,0,0.1)", borderRadius: "8px", fontSize: "14px" }}
            />
          </div>

          <div className="form-group" style={{ marginBottom: "24px" }}>
            <label style={{ fontWeight: 700 }}>Password</label>
            <input 
              type="password" 
              value={password} 
              onChange={e => setPassword(e.target.value)} 
              required 
              style={{ border: "1.5px solid rgba(0,0,0,0.1)", borderRadius: "8px", fontSize: "14px" }}
            />
          </div>

          <button className="btn btn-primary btn-full" disabled={loading} style={{ background: "#5B4CF0", fontWeight: 700, borderRadius: "8px" }}>
            {loading ? "Verifying Credentials..." : "Sign In to Portal"}
          </button>
        </form>
      </div>
    </div>
  );
}


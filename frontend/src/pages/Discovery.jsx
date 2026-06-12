import { useState, useEffect, useMemo } from "react";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import { DISCOVERY_QUESTIONS, DOMAINS, getAdaptedDiscoveryQuestions } from "../data/questions";
import { api } from "../api";

export default function Discovery() {
  const { sid } = useParams();
  const [params] = useSearchParams();
  const cid = params.get("cid");
  const navigate = useNavigate();

  const [step, setStep] = useState(0);
  const [answers, setAnswers] = useState({});
  const [generating, setGenerating] = useState(false);
  const [showSummary, setShowSummary] = useState(false);
  const [child, setChild] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadChild() {
      try {
        const c = await api.getChild(cid);
        setChild(c);
      } catch (e) {
        console.error("Error loading child profile:", e);
      } finally {
        setLoading(false);
      }
    }
    loadChild();
  }, [cid]);

  const questions = useMemo(() => {
    if (!child) return DISCOVERY_QUESTIONS;
    return getAdaptedDiscoveryQuestions(child.school_year, child.age, child.language);
  }, [child]);

  const q = questions[step];
  const total = questions.length;

  const select = (idx) => {
    setAnswers(a => ({ ...a, [q.id]: idx }));
  };

  const next = async () => {
    if (answers[q.id] === undefined) return;
    if (step < total - 1) {
      setStep(s => s + 1);
    } else {
      setGenerating(true);
      try {
        // Submit Discovery to trigger backend AI custom puzzle generation
        await api.submitDiscovery(sid, {
          child_id: parseInt(cid),
          answers: answers
        });
        setGenerating(false);
        setShowSummary(true);
      } catch (e) {
        console.error("Error creating AI assessment:", e);
        alert("Failed to build personalized assessment. Check if backend is running.");
        setGenerating(false);
      }
    }
  };

  const selected = answers[q.id];
  const pct = Math.round((step / total) * 100);

  const getTopDomains = () => {
    const domainCounts = {};
    questions.forEach((quest) => {
      const chosenOptIdx = answers[quest.id];
      if (chosenOptIdx !== undefined) {
        const opt = quest.options[chosenOptIdx];
        if (opt && opt.domains) {
          opt.domains.forEach(d => {
            domainCounts[d] = (domainCounts[d] || 0) + 1;
          });
        }
      }
    });

    return Object.entries(domainCounts)
      .sort((a, b) => b[1] - a[1])
      .map(([key, val]) => ({
        key,
        count: val,
        ...DOMAINS[key]
      }));
  };

  if (loading) {
    return <div style={{ textAlign: "center", marginTop: 80, color: "#777" }}>Loading discovery...</div>;
  }

  if (showSummary) {
    const topDomains = getTopDomains();
    return (
      <div className="card" style={{ padding: "40px 30px", maxWidth: "680px", margin: "20px auto", borderRadius: "20px", boxShadow: "var(--shadow)", border: "1px solid rgba(91, 76, 240, 0.15)" }}>
        <div style={{ textAlign: "center", marginBottom: "32px" }}>
          <span style={{ fontSize: "64px", display: "block", marginBottom: "16px" }}>🎉</span>
          <h1 style={{ fontSize: "28px", fontWeight: 800, color: "#5B4CF0", marginBottom: "8px" }}>Surface Profile Completed!</h1>
          <p style={{ color: "var(--text-mid)", fontSize: "16px", maxWidth: "480px", margin: "0 auto" }}>
            We've completed the initial screening of your child's natural cognitive leanings. Here is their preliminary profile!
          </p>
        </div>

        <div style={{ marginBottom: "32px" }}>
          <h3 style={{ fontSize: "16px", fontWeight: 700, color: "var(--text)", marginBottom: "16px", textTransform: "uppercase", letterSpacing: "1px" }}>Identified Cognitive Strengths</h3>
          <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            {topDomains.slice(0, 3).map((dom, i) => (
              <div key={dom.key} style={{ display: "flex", alignItems: "center", gap: "16px", padding: "16px 20px", borderRadius: "14px", border: `1px solid ${dom.color}22`, background: `${dom.color}08` }}>
                <span style={{ fontSize: "32px", padding: "10px", borderRadius: "10px", background: `${dom.color}15`, display: "flex", alignItems: "center", justifyContent: "center" }}>{dom.emoji}</span>
                <div style={{ flex: 1 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "4px" }}>
                    <span style={{ fontWeight: 700, fontSize: "16px", color: "var(--text)" }}>{dom.label}</span>
                    <span style={{ fontSize: "12px", fontWeight: 700, color: dom.color, background: `${dom.color}15`, padding: "2px 8px", borderRadius: "99px" }}>
                      {i === 0 ? "PRIMARY STRENGTH" : "SECONDARY POTENTIAL"}
                    </span>
                  </div>
                  <div style={{ fontSize: "13.5px", color: "var(--text-mid)" }}>
                    Natural affinity detected during active decision-making challenges.
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div style={{ background: "var(--blue-light)", padding: "24px", borderRadius: "16px", border: "1px solid rgba(91, 76, 240, 0.15)", marginBottom: "32px", textAlign: "center" }}>
          <h4 style={{ fontSize: "18px", fontWeight: 800, color: "#3C2EB9", marginBottom: "10px" }}>Unlock the Deep Assessment 🚀</h4>
          <p style={{ fontSize: "14px", color: "var(--text-mid)", lineHeight: 1.6, marginBottom: "20px" }}>
            The Surface Assessment provides a quick glimpse, but true talent development requires precision. Unlock the <strong>Deep Assessment</strong> to access interactive gamified mental puzzles, full validation reviews from domain-expert mentors, and a <strong>premium PDF reports dossier</strong>.
          </p>
          <button 
            className="btn btn-primary btn-full btn-lg" 
            style={{ background: "#5B4CF0", fontWeight: 700, borderRadius: "10px", boxShadow: "0 4px 12px rgba(91, 76, 240, 0.3)" }}
            onClick={() => navigate(`/login?redirect=${encodeURIComponent(`/assess/${sid}?cid=${cid}`)}`)}
          >
            Unlock Deep Assessment & Mental Puzzles 🔑
          </button>
        </div>
      </div>
    );
  }

  if (generating) {
    return (
      <div className="processing-wrap">
        <div className="ai-loader">
          <div className="ai-spinner" />
          <h2 style={{ color: "var(--blue)", fontWeight: 800 }}>Tailoring Your Cognitive Lab...</h2>
          <p style={{ color: "var(--text-mid)", fontSize: "16px", marginTop: "4px" }}>
            Our AI engine is analyzing your likings and exposure levels to construct 8 customized, kid-friendly puzzles in your preferred language!
          </p>
          <div style={{ fontSize: "12px", color: "var(--text-light)", fontStyle: "italic", marginTop: "12px" }}>
            This will take just a few seconds...
          </div>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="page-header">
        <h1>Quick Questions</h1>
        <p>Just {total} quick questions - pick the answer that feels most true for you.</p>
      </div>

      <div className="progress-wrap">
        <div className="progress-label">
          <span>Question {step + 1} of {total}</span>
          <span>{pct}%</span>
        </div>
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${pct}%` }} />
        </div>
      </div>

      <div className="card q-card">
        <p className="q-text">{q.question}</p>

        <div className="choice-grid" style={{ marginTop: 24 }}>
          {q.options.map((opt, i) => (
            <button
              key={i}
              className={`choice-card${selected === i ? " selected" : ""}`}
              onClick={() => select(i)}
            >
              <span className="emoji">{opt.emoji}</span>
              <span className="clabel">{opt.label}</span>
            </button>
          ))}
        </div>
      </div>

      <div className="button-row">
        <button
          className="btn btn-ghost"
          onClick={() => setStep(s => Math.max(0, s - 1))}
          disabled={step === 0}
        >Back</button>
        <button
          className="btn btn-primary"
          onClick={next}
          disabled={selected === undefined}
        >
          {step < total - 1 ? "Next" : "Start Deep Assessment"}
        </button>
      </div>
    </div>
  );
}

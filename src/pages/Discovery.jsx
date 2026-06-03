import { useState } from "react";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import { DISCOVERY_QUESTIONS } from "../data/questions";
import { api } from "../api";

export default function Discovery() {
  const { sid } = useParams();
  const [params] = useSearchParams();
  const cid = params.get("cid");
  const navigate = useNavigate();

  const [step, setStep] = useState(0);
  const [answers, setAnswers] = useState({});
  const [generating, setGenerating] = useState(false);

  const q = DISCOVERY_QUESTIONS[step];
  const total = DISCOVERY_QUESTIONS.length;

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
        navigate(`/assess/${sid}?cid=${cid}`);
      } catch (e) {
        console.error("Error creating AI assessment:", e);
        alert("Failed to build personalized assessment. Check if backend is running.");
        setGenerating(false);
      }
    }
  };

  const selected = answers[q.id];
  const pct = Math.round((step / total) * 100);

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

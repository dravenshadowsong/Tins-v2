import { useState, useEffect, useRef, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { api } from "../api";
import "./ArtSpark.css";

// ── Domain Config ─────────────────────────────────────────────────────────────
const DOMAINS = {
  visual_art:      { label: "Visual Art",      icon: "🎨", color: "#a855f7" },
  music:           { label: "Music",            icon: "🎵", color: "#06d6c7" },
  storytelling:    { label: "Storytelling",     icon: "📖", color: "#f97316" },
  drama:           { label: "Drama",            icon: "🎭", color: "#ec4899" },
  dance_movement:  { label: "Dance & Movement", icon: "💃", color: "#22d3a0" },
  craft_design:    { label: "Craft & Design",   icon: "🔧", color: "#f59e0b" },
};

const MEDAL_ICONS = { none: "—", bronze: "🥉", silver: "🥈", gold: "🥇", platinum: "💎" };
const TIER_LABELS  = { easy: "Starter", medium: "Explorer", hard: "Challenger", expert: "Master" };

const DEFAULT_DOMAINS = Object.keys(DOMAINS);

// ── Main Component ────────────────────────────────────────────────────────────
export default function ArtSpark() {
  const { uuid } = useParams();
  const navigate  = useNavigate();

  // ── State ─────────────────────────────────────────────────────────────────
  const [screen, setScreen]             = useState("intro");   // intro | playing | complete
  const [selectedDomains, setSelectedDomains] = useState([...DEFAULT_DOMAINS]);
  const [session, setSession]           = useState(null);
  const [question, setQuestion]         = useState(null);
  const [answer, setAnswer]             = useState(null);     // selected option key / text
  const [seqOrder, setSeqOrder]         = useState([]);
  const [feedback, setFeedback]         = useState(null);     // { type, text, explanation }
  const [xp, setXp]                     = useState(0);
  const [streak, setStreak]             = useState(0);
  const [theta, setTheta]               = useState({});
  const [medals, setMedals]             = useState({});
  const [domainSummary, setDomainSummary] = useState({});
  const [levelUp, setLevelUp]           = useState(null);     // tier name or null
  const [streakBadge, setStreakBadge]   = useState(0);        // key for re-mount animation
  const [loading, setLoading]           = useState(false);
  const [submitting, setSubmitting]     = useState(false);
  const [error, setError]               = useState(null);
  const [currentDomain, setCurrentDomain] = useState(null);
  const [domainIdx, setDomainIdx]       = useState(0);
  const [qIdx, setQIdx]                 = useState(0);
  const [qAnswered, setQAnswered]       = useState(0);
  const [xpBurst, setXpBurst]           = useState(false);

  const startTs = useRef(null);
  const xpPrev  = useRef(0);

  // ── Resume session from UUID ───────────────────────────────────────────────
  useEffect(() => {
    if (uuid) {
      setLoading(true);
      api.artSpark.getSession(uuid)
        .then(data => {
          setSession(data);
          setXp(data.xp_total || 0);
          xpPrev.current = data.xp_total || 0;
          setTheta(data.theta || {});
          setMedals(data.medals || {});
          setCurrentDomain(data.current_domain);
          setDomainIdx(data.domain_idx || 0);
          setQIdx(data.q_idx || 0);
          setQAnswered(data.questions_answered || 0);
          setQuestion(data.next_question);
          if (data.status === "completed") {
            setScreen("complete");
          } else {
            setScreen("playing");
            startTs.current = Date.now();
          }
        })
        .catch(() => setError("Could not load session"))
        .finally(() => setLoading(false));
    }
  }, [uuid]);

  // ── Toggle domain selection ────────────────────────────────────────────────
  const toggleDomain = useCallback(domain => {
    setSelectedDomains(prev =>
      prev.includes(domain)
        ? prev.filter(d => d !== domain)
        : [...prev, domain]
    );
  }, []);

  // ── Start Session ──────────────────────────────────────────────────────────
  const handleStart = async () => {
    if (selectedDomains.length === 0) return;
    setLoading(true);
    setError(null);
    try {
      const data = await api.artSpark.createSession({ domains: selectedDomains });
      setSession(data);
      setXp(0);
      xpPrev.current = 0;
      setTheta(data.theta || {});
      setMedals(data.medals || {});
      setCurrentDomain(data.domain);
      setDomainIdx(data.domain_idx || 0);
      setQIdx(data.q_idx || 0);
      setQAnswered(0);
      setQuestion(data.next_question);
      setScreen("playing");
      startTs.current = Date.now();
      navigate(`/art-spark/${data.session_uuid}`, { replace: true });
    } catch (e) {
      setError("Failed to start session. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  // ── Submit Answer ──────────────────────────────────────────────────────────
  const handleSubmit = async () => {
    if (!question || submitting) return;
    const responseMs = startTs.current ? Date.now() - startTs.current : 0;
    const responseValue = question.q_type === "sequence"
      ? JSON.stringify(seqOrder)
      : (answer ?? "");

    if (!responseValue && !answer) return;

    setSubmitting(true);
    try {
      const res = await api.artSpark.respond(session.session_uuid, {
        item_uuid:     question.item_uuid,
        response_value: responseValue,
        response_ms:   responseMs,
      });

      // XP burst animation
      xpPrev.current = xp;
      setXp(res.xp_total);
      setXpBurst(true);
      setTimeout(() => setXpBurst(false), 700);

      // Streak badge if >= 3 streak
      if (res.streak >= 3) {
        setStreakBadge(prev => prev + 1);
      }
      setStreak(res.streak || 0);
      setTheta(res.theta || {});
      setMedals(res.medals || {});
      setQAnswered(prev => prev + 1);
      setQIdx(res.q_idx || 0);
      setDomainIdx(res.domain_idx || 0);
      setCurrentDomain(res.domain || currentDomain);

      // Feedback
      if (res.scored === true) {
        setFeedback({ type: "correct", text: "✓ Correct!", explanation: res.explanation });
      } else if (res.scored === false) {
        setFeedback({ type: "wrong", text: "✗ Not quite.", explanation: res.explanation });
      } else {
        setFeedback({ type: "open", text: "🎨 Response recorded!", explanation: null });
      }

      // Level-up
      if (res.level_up) {
        setLevelUp(res.tier_after);
      }

      if (res.session_complete) {
        // Complete the session
        try {
          const comp = await api.artSpark.complete(session.session_uuid);
          setDomainSummary(comp.domain_summary || {});
          setTheta(comp.theta || {});
          setMedals(comp.medals || {});
          setXp(comp.xp_total || res.xp_total);
        } catch (_) {}
        setTimeout(() => setScreen("complete"), 1600);
      } else {
        // Advance to next question after feedback delay
        setTimeout(() => {
          setQuestion(res.next_question);
          setAnswer(null);
          setSeqOrder(res.next_question?.options ? [...(Array.isArray(res.next_question.options) ? res.next_question.options.map(o => (typeof o === 'object' ? o.label : o)) : [])] : []);
          setFeedback(null);
          startTs.current = Date.now();
        }, 1800);
      }
    } catch (e) {
      setError("Failed to submit. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  // ── Sequence drag state ────────────────────────────────────────────────────
  useEffect(() => {
    if (question?.q_type === "sequence" && question.options) {
      const opts = Array.isArray(question.options) ? question.options : [];
      setSeqOrder([...opts]);
    }
    setAnswer(null);
    setFeedback(null);
  }, [question]);

  const dragItem = useRef(null);
  const dragOver = useRef(null);

  const handleSeqDragStart = i => { dragItem.current = i; };
  const handleSeqDragEnter = i => { dragOver.current = i; };
  const handleSeqDrop = () => {
    if (dragItem.current === null) return;
    const copy = [...seqOrder];
    const dragged = copy.splice(dragItem.current, 1)[0];
    copy.splice(dragOver.current, 0, dragged);
    setSeqOrder(copy);
    dragItem.current = null;
    dragOver.current = null;
  };

  // ── Level-up dismiss ──────────────────────────────────────────────────────
  const dismissLevelUp = () => setLevelUp(null);

  // ── Helpers ───────────────────────────────────────────────────────────────
  const thetaToPercent = t => Math.round(((t + 3) / 6) * 100);
  const canSubmit = () => {
    if (!question) return false;
    if (question.q_type === "image_choice") return answer !== null;
    if (question.q_type === "likert")       return answer !== null;
    if (question.q_type === "open_text")    return typeof answer === "string" && answer.trim().length > 0;
    if (question.q_type === "sequence")     return seqOrder.length > 0;
    return false;
  };

  // ── Progress calc ─────────────────────────────────────────────────────────
  const totalDomains  = session?.domains?.length || selectedDomains.length;
  const progressPct   = totalDomains > 0 ? Math.min(Math.round((qAnswered / (totalDomains * 8)) * 100), 100) : 0;

  // ═══════════════════════════════════════════════════════════════════════════
  // RENDER
  // ═══════════════════════════════════════════════════════════════════════════

  if (loading) {
    return (
      <div className="as-shell">
        <div className="as-loading">
          <div className="as-spinner" />
          <p>Loading ArtSpark...</p>
        </div>
      </div>
    );
  }

  if (error && screen === "intro") {
    return (
      <div className="as-shell">
        <div className="as-error">
          <p style={{ fontSize: "2rem" }}>⚠️</p>
          <p>{error}</p>
          <button className="as-start-btn" style={{ marginTop: 20 }} onClick={() => setError(null)}>
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="as-shell">

      {/* ── HUD ── */}
      {screen !== "intro" && (
        <header className="as-hud">
          <span className="as-hud-brand">🎨 ArtSpark</span>

          {currentDomain && (
            <div className="as-domain-pill" style={{ "--domain-color": DOMAINS[currentDomain]?.color }}>
              {DOMAINS[currentDomain]?.icon} {DOMAINS[currentDomain]?.label}
            </div>
          )}

          <div className={`as-xp-pill ${xpBurst ? "as-xp-burst" : ""}`}>
            <span className="xp-icon">⚡</span>
            {xp} XP
          </div>

          {streak >= 2 && (
            <div className="as-streak-pill">
              🔥 ×{streak}
            </div>
          )}

          <div className="as-progress-bar">
            <div className="as-progress-fill" style={{ width: `${progressPct}%` }} />
          </div>
        </header>
      )}

      {/* ── Streak Badge Popup ── */}
      {streakBadge > 0 && (
        <div className="as-streak-badge" key={streakBadge}>
          <div className="sb-num">🔥 ×{streak}</div>
          <div className="sb-text">On Fire!</div>
        </div>
      )}

      {/* ── Level-Up Overlay ── */}
      {levelUp && (
        <div className="as-levelup-overlay" onClick={dismissLevelUp}>
          <div className="as-levelup-card" onClick={e => e.stopPropagation()}>
            <span className="as-levelup-star">⭐</span>
            <h2>Level Up!</h2>
            <p>You reached <strong>{TIER_LABELS[levelUp] || levelUp}</strong> level!<br/>Questions are getting harder — you&apos;re ready.</p>
            <button className="as-next-btn" onClick={dismissLevelUp}>Keep Going →</button>
          </div>
        </div>
      )}

      <main className="as-main">

        {/* ══════════════════════════════════════════════════
            INTRO SCREEN
            ══════════════════════════════════════════════════ */}
        {screen === "intro" && (
          <div className="as-intro">
            <span className="as-intro-badge">🎨 Adaptive Assessment</span>
            <h1>ArtSpark</h1>
            <p className="as-intro-sub">
              Discover your creative and artistic strengths through an intelligent,
              gamified assessment that adapts to your level.
            </p>

            <p style={{ color: "rgba(240,236,255,0.7)", fontWeight: 600, marginBottom: 16, fontSize: "0.95rem" }}>
              Choose the domains you want to explore:
            </p>

            <div className="as-domain-grid">
              {DEFAULT_DOMAINS.map(d => (
                <div
                  key={d}
                  className={`as-domain-card ${selectedDomains.includes(d) ? "selected" : ""}`}
                  style={{ "--domain-color": DOMAINS[d].color }}
                  onClick={() => toggleDomain(d)}
                >
                  <span className="as-domain-icon">{DOMAINS[d].icon}</span>
                  <span className="as-domain-name">{DOMAINS[d].label}</span>
                </div>
              ))}
            </div>

            <button
              className="as-start-btn"
              disabled={selectedDomains.length === 0 || loading}
              onClick={handleStart}
            >
              {loading ? "Starting..." : `Start Assessment 🚀`}
            </button>

            {selectedDomains.length > 0 && (
              <p style={{ color: "var(--as-muted)", fontSize: "0.85rem", marginTop: 16 }}>
                {selectedDomains.length} domain{selectedDomains.length > 1 ? "s" : ""} selected
                · ~{Math.round(selectedDomains.length * 8)} adaptive questions
              </p>
            )}

            {error && <p style={{ color: "var(--as-coral)", marginTop: 16 }}>{error}</p>}
          </div>
        )}

        {/* ══════════════════════════════════════════════════
            PLAYING SCREEN
            ══════════════════════════════════════════════════ */}
        {screen === "playing" && question && (
          <div className="as-question-card" key={question.item_uuid}>

            {/* Meta badges */}
            <div className="as-q-meta">
              <span className="as-q-type-badge">
                {{ image_choice: "Choice", likert: "Self-Report", open_text: "Open Response", sequence: "Sequence" }[question.q_type] || question.q_type}
              </span>
              <span className={`as-q-tier-badge ${question.tier}`}>
                {TIER_LABELS[question.tier] || question.tier}
              </span>
              {currentDomain && (
                <span style={{ color: DOMAINS[currentDomain]?.color, fontSize: "0.85rem", fontWeight: 700 }}>
                  {DOMAINS[currentDomain]?.icon} {DOMAINS[currentDomain]?.label}
                </span>
              )}
            </div>

            {/* Prompt */}
            <p className="as-q-prompt">{question.prompt}</p>

            {/* ── Multiple Choice ── */}
            {question.q_type === "image_choice" && (
              <div className="as-options">
                {(question.options || []).map(opt => {
                  const key   = typeof opt === "object" ? opt.key   : opt;
                  const label = typeof opt === "object" ? opt.label : opt;
                  const isSelected = answer === key;
                  const wasCorrect = feedback?.type === "correct" && isSelected;
                  const wasWrong   = feedback?.type === "wrong"   && isSelected;
                  return (
                    <button
                      key={key}
                      className={`as-option ${isSelected ? "selected" : ""} ${wasCorrect ? "correct" : ""} ${wasWrong ? "wrong" : ""}`}
                      onClick={() => !feedback && setAnswer(key)}
                      disabled={!!feedback || submitting}
                    >
                      <span className="as-option-key">{key}</span>
                      {label}
                    </button>
                  );
                })}
              </div>
            )}

            {/* ── Likert ── */}
            {question.q_type === "likert" && (
              <div className="as-likert">
                {(question.options || ["Never","Rarely","Sometimes","Often","Always"]).map((opt, i) => (
                  <button
                    key={i}
                    className={`as-likert-option ${answer === i ? "selected" : ""}`}
                    onClick={() => !feedback && setAnswer(i)}
                    disabled={!!feedback || submitting}
                  >
                    <span className="as-likert-dot" />
                    {opt}
                  </button>
                ))}
              </div>
            )}

            {/* ── Open Text ── */}
            {question.q_type === "open_text" && (
              <textarea
                className="as-open-textarea"
                placeholder="Write your response here — there are no wrong answers…"
                value={typeof answer === "string" ? answer : ""}
                onChange={e => setAnswer(e.target.value)}
                disabled={!!feedback || submitting}
              />
            )}

            {/* ── Sequence ── */}
            {question.q_type === "sequence" && (
              <div className="as-sequence">
                <p style={{ color: "var(--as-muted)", fontSize: "0.85rem", marginBottom: 8 }}>
                  Drag to reorder ↕
                </p>
                {seqOrder.map((item, i) => (
                  <div
                    key={`${item}-${i}`}
                    className="as-seq-item"
                    draggable
                    onDragStart={() => handleSeqDragStart(i)}
                    onDragEnter={() => handleSeqDragEnter(i)}
                    onDragEnd={handleSeqDrop}
                    onDragOver={e => e.preventDefault()}
                  >
                    <span className="as-seq-handle">⠿</span>
                    <span className="as-seq-num">{i + 1}</span>
                    <span className="as-seq-label">{item}</span>
                  </div>
                ))}
                {seqOrder.length === 0 && (
                  <p style={{ color: "var(--as-muted)" }}>Loading options…</p>
                )}
              </div>
            )}

            {/* ── Feedback ── */}
            {feedback && (
              <div className={`as-feedback ${feedback.type}`}>
                <span className="as-feedback-icon">
                  {{ correct: "✅", wrong: "❌", open: "🎨" }[feedback.type]}
                </span>
                <div>
                  <strong>{feedback.text}</strong>
                  {feedback.explanation && (
                    <p style={{ margin: "4px 0 0", fontWeight: 400, opacity: 0.85 }}>
                      {feedback.explanation}
                    </p>
                  )}
                </div>
              </div>
            )}

            {/* Submit */}
            {!feedback && (
              <button
                className="as-submit-btn"
                disabled={!canSubmit() || submitting}
                onClick={handleSubmit}
              >
                {submitting ? "Submitting…" : "Submit Answer →"}
              </button>
            )}

            {error && <p style={{ color: "var(--as-coral)", marginTop: 12, fontSize: "0.9rem" }}>{error}</p>}
          </div>
        )}

        {/* Playing but no question (between domains) */}
        {screen === "playing" && !question && (
          <div className="as-loading">
            <div className="as-spinner" />
            <p>Loading next question…</p>
          </div>
        )}

        {/* ══════════════════════════════════════════════════
            COMPLETION SCREEN
            ══════════════════════════════════════════════════ */}
        {screen === "complete" && (
          <div className="as-completion">
            <span className="as-trophy">🏆</span>
            <h1>Assessment Complete!</h1>
            <p className="as-completion-sub">
              You explored {Object.keys(domainSummary).length || Object.keys(medals).length} creative domains.
              Here are your results:
            </p>

            {/* XP Banner */}
            <div className="as-xp-banner">
              <div>
                <div className="xp-val">{xp}</div>
                <div className="xp-label">Total XP Earned</div>
              </div>
            </div>

            {/* Domain Results */}
            <div className="as-domain-results">
              {(Object.keys(domainSummary).length > 0 ? Object.keys(domainSummary) : Object.keys(medals)).map(d => {
                const summary = domainSummary[d] || {};
                const medal   = summary.medal || medals[d] || "none";
                const t       = summary.theta ?? theta[d] ?? 0;
                const pct     = thetaToPercent(t);
                const dom     = DOMAINS[d] || { icon: "🎨", label: d, color: "#8b5cf6" };
                return (
                  <div key={d} className="as-domain-result-card">
                    <div className="as-domain-result-icon">{dom.icon}</div>
                    <div className="as-domain-result-name">{dom.label}</div>
                    <span className={`as-medal-badge ${medal}`}>
                      {MEDAL_ICONS[medal] || "—"} {medal.charAt(0).toUpperCase() + medal.slice(1)}
                    </span>
                    {summary.questions > 0 && (
                      <p style={{ color: "var(--as-muted)", fontSize: "0.8rem", margin: "0 0 8px" }}>
                        {summary.correct ?? "—"} / {summary.questions} correct
                      </p>
                    )}
                    <div className="as-theta-bar-wrap">
                      <div className="as-theta-bar" style={{ width: `${pct}%` }} />
                    </div>
                    <div className="as-theta-label">
                      Ability: {t >= 0 ? "+" : ""}{t.toFixed ? t.toFixed(2) : t}σ
                    </div>
                  </div>
                );
              })}
            </div>

            <button className="as-start-btn" onClick={() => { setScreen("intro"); setSession(null); setQuestion(null); setAnswer(null); setFeedback(null); setXp(0); setStreak(0); setQAnswered(0); navigate("/art-spark", { replace: true }); }}>
              Try Again 🔄
            </button>
            &nbsp;&nbsp;
            <button className="as-next-btn" onClick={() => navigate("/dashboard")}>
              Dashboard →
            </button>
          </div>
        )}

      </main>
    </div>
  );
}

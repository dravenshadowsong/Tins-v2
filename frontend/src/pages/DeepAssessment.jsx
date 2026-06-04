import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import { ASSESSMENT_TASKS, DOMAINS } from "../data/questions";
import { api } from "../api";

const SCALE_LABELS = {
  English: ["Not at all", "A little", "Sometimes", "Mostly", "Always / Easily"],
  Hindi: ["बिल्कुल नहीं", "थोड़ा सा", "कभी-कभी", "ज्यादातर", "हमेशा / आसानी से"]
};

function baseAnswer(task, value, extra = {}) {
  return {
    task_type: task.type,
    domain: task.domain,
    component: task.component,
    metric: task.metric,
    value,
    ...extra,
  };
}

function scoreChoice(task, selectedValue, startedAt) {
  const value = Number(selectedValue);
  return baseAnswer(task, value, {
    correct: value >= 4,
    response_ms: Date.now() - startedAt,
  });
}

export default function DeepAssessment() {
  const { sid } = useParams();
  const [params] = useSearchParams();
  const cid = params.get("cid");
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("goat_token");
    if (!token) {
      navigate(`/login?redirect=${encodeURIComponent(`/assess/${sid}?cid=${cid}`)}`);
    }
  }, [navigate, sid, cid]);

  const [step, setStep] = useState(0);
  const [answers, setAnswers] = useState({});
  const [startedAt, setStartedAt] = useState(Date.now());
  const [submitting, setSubmitting] = useState(false);
  
  // Multilingual Child & Session States
  const [child, setChild] = useState(null);
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [s, c] = await Promise.all([
          api.getSession(sid),
          api.getChild(cid)
        ]);
        setSession(s);
        setChild(c);
      } catch (e) {
        console.error("Error loading assessment data:", e);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [sid, cid]);

  // Dynamically resolve AI generated tasks or default fallback
  const taskList = useMemo(() => {
    if (session?.generated_tasks) {
      try {
        return JSON.parse(session.generated_tasks);
      } catch (e) {
        console.error("Error parsing AI generated tasks:", e);
      }
    }
    return ASSESSMENT_TASKS;
  }, [session]);

  const task = taskList[step];
  const total = taskList.length;
  const pct = Math.round((step / total) * 100);
  const domainInfo = task ? DOMAINS[task.domain] : null;
  const currentAnswer = task ? answers[task.key] : null;

  useEffect(() => {
    setStartedAt(Date.now());
  }, [task?.key]);

  const setAnswer = (answer) => {
    setAnswers(prev => ({ ...prev, [task.key]: answer }));
  };

  const next = async () => {
    if (!currentAnswer) return;
    if (step < total - 1) {
      setStep(s => s + 1);
      return;
    }

    setSubmitting(true);
    try {
      await api.analyzeSession(parseInt(sid), {
        child_id: parseInt(cid),
        responses: answers,
      });
      navigate(`/results/${sid}?cid=${cid}`);
    } catch (e) {
      alert("Submission failed. Check the backend is running.");
      setSubmitting(false);
    }
  };

  if (loading) {
    return <div style={{ textAlign: "center", marginTop: 80, color: "#777" }}>Loading assessment...</div>;
  }

  if (!task) {
    return <div style={{ textAlign: "center", marginTop: 80, color: "#777" }}>No tasks available.</div>;
  }

  const selectedLanguage = child?.language === "Hindi" ? "Hindi" : "English";

  // Localized Main Layout Elements
  const layoutStrings = {
    English: {
      title: "Interactive Assessment",
      subtitle: "Complete each short puzzle or activity. The backend analyses accuracy, timing, memory, attention, and judgement.",
      taskProgress: `Task ${step + 1} of ${total}`,
      back: "Back",
      next: "Next",
      results: "See My Results",
      analyzing: "Analysing..."
    },
    Hindi: {
      title: "इंटरएक्टिव मूल्यांकन",
      subtitle: "प्रत्येक छोटी पहेली या गतिविधि को पूरा करें। बैकएंड आपकी सटीकता, समय, याददाश्त और सूझबूझ का विश्लेषण करता है।",
      taskProgress: `पहेली ${step + 1} / ${total}`,
      back: "पीछे",
      next: "आगे",
      results: "मेरा परिणाम देखें",
      analyzing: "विश्लेषण हो रहा है..."
    }
  }[selectedLanguage];

  // Resolve localized task texts
  const taskTitle = typeof task.title === "object" ? (task.title[selectedLanguage] || task.title["English"]) : task.title;
  const taskPrompt = typeof task.prompt === "object" ? (task.prompt[selectedLanguage] || task.prompt["English"]) : task.prompt;

  return (
    <div>
      <div className="page-header">
        <h1>{layoutStrings.title}</h1>
        <p>{layoutStrings.subtitle}</p>
      </div>

      <div className="progress-wrap">
        <div className="progress-label">
          <span>{layoutStrings.taskProgress}</span>
          <span>{pct}%</span>
        </div>
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${pct}%` }} />
        </div>
      </div>

      <div style={{ marginBottom: 16 }}>
        <span className="domain-badge" style={{
          background: domainInfo.light,
          color: domainInfo.color,
          border: `1px solid ${domainInfo.color}22`,
        }}>
          {domainInfo.emoji} {domainInfo.label}
        </span>
      </div>

      <div className="card q-card">
        <h2 className="card-title-tight">{taskTitle}</h2>
        <p className="q-text">{taskPrompt}</p>
        <TaskRenderer
          task={task}
          answer={currentAnswer}
          startedAt={startedAt}
          setAnswer={setAnswer}
          selectedLanguage={selectedLanguage}
        />
      </div>

      <div className="button-row">
        <button
          className="btn btn-ghost"
          onClick={() => setStep(s => Math.max(0, s - 1))}
          disabled={step === 0 || submitting}
        >
          {layoutStrings.back}
        </button>
        <button
          className="btn btn-primary"
          onClick={next}
          disabled={!currentAnswer || submitting}
        >
          {submitting
            ? layoutStrings.analyzing
            : step < total - 1
            ? layoutStrings.next
            : layoutStrings.results}
        </button>
      </div>

      <div className="domain-progress">
        {Object.entries(DOMAINS).map(([key, d]) => {
          const domTasks = taskList.filter(t => t.domain === key);
          const answered = domTasks.filter(t => answers[t.key]).length;
          if (!domTasks.length) return null;
          const current = task.domain === key;
          return (
            <div key={key} title={d.label} className="domain-chip" style={{
              background: current ? "#E6F1FB" : answered === domTasks.length ? d.light : "#F5F5F5",
              color: current ? "#185FA5" : answered === domTasks.length ? d.color : "#999",
              borderColor: current ? "#185FA5" : "transparent",
            }}>
              {d.emoji} {answered}/{domTasks.length}
            </div>
          );
        })}
      </div>
    </div>
  );
}

function TaskRenderer({ task, answer, startedAt, setAnswer, selectedLanguage }) {
  if (task.type === "pattern_choice") {
    return <PatternChoice task={task} answer={answer} startedAt={startedAt} setAnswer={setAnswer} selectedLanguage={selectedLanguage} />;
  }
  if (task.type === "symbol_scan") {
    return <SymbolScan task={task} answer={answer} startedAt={startedAt} setAnswer={setAnswer} selectedLanguage={selectedLanguage} />;
  }
  if (task.type === "memory_grid") {
    return <MemoryGrid task={task} answer={answer} setAnswer={setAnswer} selectedLanguage={selectedLanguage} />;
  }
  if (task.type === "order_steps") {
    return <OrderSteps task={task} answer={answer} startedAt={startedAt} setAnswer={setAnswer} selectedLanguage={selectedLanguage} />;
  }
  if (task.type === "idea_list") {
    return <IdeaList task={task} answer={answer} startedAt={startedAt} setAnswer={setAnswer} selectedLanguage={selectedLanguage} />;
  }
  if (task.type === "reaction") {
    return <ReactionTask task={task} answer={answer} setAnswer={setAnswer} selectedLanguage={selectedLanguage} />;
  }
  if (task.type === "choice") {
    return <JudgementChoice task={task} answer={answer} startedAt={startedAt} setAnswer={setAnswer} selectedLanguage={selectedLanguage} />;
  }
  return <ScaleTask task={task} answer={answer} setAnswer={setAnswer} selectedLanguage={selectedLanguage} />;
}

function PatternChoice({ task, answer, startedAt, setAnswer, selectedLanguage }) {
  return (
    <>
      <div className="puzzle-sequence">
        {task.sequence.map((item, i) => <span key={`${item}-${i}`}>{item}</span>)}
      </div>
      <div className="choice-grid compact-choice-grid">
        {task.options.map(option => (
          <button
            key={option}
            className={`choice-card${answer?.value === option ? " selected" : ""}`}
            onClick={() => setAnswer(baseAnswer(task, option, {
              correct: option === task.answer,
              response_ms: Date.now() - startedAt,
            }))}
          >
            <span className="clabel puzzle-option">{option}</span>
          </button>
        ))}
      </div>
    </>
  );
}

function SymbolScan({ task, answer, startedAt, setAnswer, selectedLanguage }) {
  const [count, setCount] = useState(answer?.value || "");

  const submit = () => {
    const numeric = Number(count);
    const difference = Math.abs(numeric - task.answer);
    setAnswer(baseAnswer(task, numeric, {
      correct: difference === 0,
      accuracy: Math.max(0, 1 - difference / task.answer),
      response_ms: Date.now() - startedAt,
    }));
  };

  const strings = {
    English: {
      placeholder: `Number of ${task.target}`,
      lock: "Lock answer"
    },
    Hindi: {
      placeholder: `${task.target} की संख्या`,
      lock: "उत्तर लॉक करें"
    }
  }[selectedLanguage];

  return (
    <div className="task-stack">
      <div className="symbol-grid">
        {task.symbols.map((symbol, i) => <span key={`${symbol}-${i}`}>{symbol}</span>)}
      </div>
      <div className="form-row">
        <input
          type="number"
          min="0"
          value={count}
          onChange={e => setCount(e.target.value)}
          placeholder={strings.placeholder}
        />
        <button className="btn btn-primary" onClick={submit} disabled={count === ""}>
          {strings.lock}
        </button>
      </div>
    </div>
  );
}

function MemoryGrid({ task, answer, setAnswer, selectedLanguage }) {
  const [revealing, setRevealing] = useState(true);
  const [selected, setSelected] = useState(answer?.selected || []);
  const started = useMemo(() => Date.now(), [task.key]);

  useEffect(() => {
    setRevealing(true);
    setSelected([]);
    const timer = setTimeout(() => setRevealing(false), task.revealMs);
    return () => clearTimeout(timer);
  }, [task]);

  const toggle = (idx) => {
    if (revealing) return;
    const next = selected.includes(idx)
      ? selected.filter(i => i !== idx)
      : [...selected, idx];
    setSelected(next);

    const correctSelected = next.filter(i => task.highlights.includes(i)).length;
    const extraSelected = next.filter(i => !task.highlights.includes(i)).length;
    const score = Math.max(0, correctSelected - extraSelected) / task.highlights.length;
    setAnswer(baseAnswer(task, score * 4, {
      selected: next,
      correct: score === 1,
      memory_score: score,
      response_ms: Date.now() - started,
    }));
  };

  const strings = {
    English: {
      memorise: "Memorise the highlighted squares.",
      select: "Now select the squares you remember."
    },
    Hindi: {
      memorise: "चमकते हुए खानों को याद रखें।",
      select: "अब उन खानों को चुनें जो आपको याद हैं।"
    }
  }[selectedLanguage];

  return (
    <div className="task-stack">
      <p className="text-light">{revealing ? strings.memorise : strings.select}</p>
      <div className="memory-grid">
        {Array.from({ length: task.gridSize }, (_, idx) => {
          const active = revealing ? task.highlights.includes(idx) : selected.includes(idx);
          return (
            <button
              key={idx}
              className={active ? "memory-cell active" : "memory-cell"}
              onClick={() => toggle(idx)}
              type="button"
            />
          );
        })}
      </div>
    </div>
  );
}

function OrderSteps({ task, answer, startedAt, setAnswer, selectedLanguage }) {
  const stepsList = Array.isArray(task.steps)
    ? task.steps
    : (task.steps[selectedLanguage] || task.steps["English"]);
  const shuffledList = Array.isArray(task.shuffled)
    ? task.shuffled
    : (task.shuffled[selectedLanguage] || task.shuffled["English"]);

  const [ordered, setOrdered] = useState(answer?.ordered || shuffledList);

  useEffect(() => {
    setOrdered(answer?.ordered || shuffledList);
  }, [task, selectedLanguage]);

  const move = (idx, direction) => {
    const target = idx + direction;
    if (target < 0 || target >= ordered.length) return;
    const next = [...ordered];
    [next[idx], next[target]] = [next[target], next[idx]];
    setOrdered(next);
  };

  const submit = () => {
    const correct = ordered.filter((step, idx) => step === stepsList[idx]).length;
    setAnswer(baseAnswer(task, (correct / stepsList.length) * 4, {
      ordered,
      correct: correct === stepsList.length,
      accuracy: correct / stepsList.length,
      response_ms: Date.now() - startedAt,
    }));
  };

  const strings = {
    English: {
      up: "Up",
      down: "Down",
      lock: "Lock order"
    },
    Hindi: {
      up: "ऊपर",
      down: "नीचे",
      lock: "क्रम लॉक करें"
    }
  }[selectedLanguage];

  return (
    <div className="task-stack">
      <div className="order-list">
        {ordered.map((step, idx) => (
          <div key={step} className="order-row">
            <span>{idx + 1}. {step}</span>
            <div className="row-actions">
              <button className="btn btn-ghost btn-sm" onClick={() => move(idx, -1)} disabled={idx === 0}>
                {strings.up}
              </button>
              <button className="btn btn-ghost btn-sm" onClick={() => move(idx, 1)} disabled={idx === ordered.length - 1}>
                {strings.down}
              </button>
            </div>
          </div>
        ))}
      </div>
      <button className="btn btn-primary" onClick={submit}>
        {strings.lock}
      </button>
    </div>
  );
}

function IdeaList({ task, answer, startedAt, setAnswer, selectedLanguage }) {
  const [text, setText] = useState(answer?.text || "");

  const submit = () => {
    const ideas = text.split(/\n|,/).map(item => item.trim()).filter(Boolean);
    const uniqueIdeas = new Set(ideas.map(i => i.toLowerCase())).size;
    setAnswer(baseAnswer(task, Math.min(4, uniqueIdeas), {
      text,
      idea_count: uniqueIdeas,
      fluency_score: Math.min(1, uniqueIdeas / task.minIdeas),
      response_ms: Date.now() - startedAt,
    }));
  };

  const strings = {
    English: {
      placeholder: "One idea per line, or separate ideas with commas",
      lock: "Lock ideas"
    },
    Hindi: {
      placeholder: "प्रति पंक्ति एक विचार लिखें, या विचारों को अल्पविराम (comma) से अलग करें",
      lock: "विचार लॉक करें"
    }
  }[selectedLanguage];

  return (
    <div className="task-stack">
      <textarea
        rows={5}
        value={text}
        onChange={e => setText(e.target.value)}
        placeholder={strings.placeholder}
      />
      <button className="btn btn-primary" onClick={submit} disabled={!text.trim()}>
        {strings.lock}
      </button>
    </div>
  );
}

function JudgementChoice({ task, answer, startedAt, setAnswer, selectedLanguage }) {
  return (
    <div className="choice-grid">
      {task.options.map(option => {
        const labelStr = typeof option.label === "object"
          ? (option.label[selectedLanguage] || option.label["English"])
          : option.label;
        return (
          <button
            key={labelStr}
            className={`choice-card${answer?.label === labelStr ? " selected" : ""}`}
            onClick={() => setAnswer({
              ...scoreChoice(task, option.value, startedAt),
              label: labelStr,
            })}
          >
            <span className="clabel">{labelStr}</span>
          </button>
        );
      })}
    </div>
  );
}

function ScaleTask({ task, answer, setAnswer, selectedLanguage }) {
  const lowStr = typeof task.low === "object" ? (task.low[selectedLanguage] || task.low["English"]) : (task.low || "Not at all");
  const highStr = typeof task.high === "object" ? (task.high[selectedLanguage] || task.high["English"]) : (task.high || "Completely");
  const labels = SCALE_LABELS[selectedLanguage] || SCALE_LABELS["English"];

  return (
    <div className="scale-wrap">
      <div className="scale-dots">
        {[0, 1, 2, 3, 4].map(v => (
          <button
            key={v}
            className={`scale-dot${answer?.value === v ? " active" : ""}`}
            onClick={() => setAnswer(baseAnswer(task, v))}
            title={labels[v]}
          >
            {v + 1}
          </button>
        ))}
      </div>
      <div className="scale-labels">
        <span>{lowStr}</span>
        <span>{highStr}</span>
      </div>
      {answer && (
        <div className="text-center mt-16" style={{ fontSize: 14, color: "#0F6E56", fontWeight: 600 }}>
          {labels[answer.value]}
        </div>
      )}
    </div>
  );
}

function ReactionTask({ task, answer, setAnswer, selectedLanguage }) {
  const [ready, setReady] = useState(false);
  const [activeAt, setActiveAt] = useState(null);
  const [started, setStarted] = useState(false);

  const start = () => {
    setStarted(true);
    setReady(false);
    setActiveAt(null);
    setTimeout(() => {
      setReady(true);
      setActiveAt(Date.now());
    }, task.waitMs);
  };

  const tap = () => {
    if (!ready || !activeAt) return;
    const reactionMs = Date.now() - activeAt;
    const value = Math.max(0, Math.min(4, 4 - ((reactionMs - 250) / 300)));
    setAnswer(baseAnswer(task, value, {
      reaction_ms: reactionMs,
      correct: reactionMs < 1200,
    }));
    setReady(false);
  };

  const strings = {
    English: {
      start: "Start",
      tap: "Tap now",
      wait: "Wait..."
    },
    Hindi: {
      start: "शुरू करें",
      tap: "अभी दबाएं",
      wait: "इंतज़ार करें..."
    }
  }[selectedLanguage];

  return (
    <div className="task-stack">
      <button className={ready ? "reaction-target active" : "reaction-target"} onClick={ready ? tap : start}>
        {!started
          ? strings.start
          : ready
          ? strings.tap
          : answer
          ? `${answer.reaction_ms} ms`
          : strings.wait}
      </button>
    </div>
  );
}

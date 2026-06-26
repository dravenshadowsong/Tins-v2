import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import { ASSESSMENT_TASKS, DOMAINS, getAdaptedDeepTasks } from "../data/questions";
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
    const token = sessionStorage.getItem("goat_token");
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
  const [taskList, setTaskList] = useState([]);

  useEffect(() => {
    async function loadData() {
      try {
        const [s, c] = await Promise.all([
          api.getSession(sid),
          api.getChild(cid)
        ]);
        setSession(s);
        setChild(c);
        
        let tasks = ASSESSMENT_TASKS;
        if (s?.generated_tasks) {
          try {
            tasks = JSON.parse(s.generated_tasks);
          } catch (e) {
            console.error("Error parsing AI generated tasks:", e);
          }
        }
        if (c) {
          tasks = getAdaptedDeepTasks(tasks, c.school_year, c.age, c.language);
        }
        setTaskList(tasks);
      } catch (e) {
        console.error("Error loading assessment data:", e);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [sid, cid]);

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

    if (step === 19 && taskList.length === 20) {
      setSubmitting(true);
      try {
        const res = await api.getAdaptiveQuestions(parseInt(sid), {
          child_id: parseInt(cid),
          responses: answers,
        });
        let adaptive = res.adaptive_tasks || [];
        if (child) {
          adaptive = getAdaptedDeepTasks(adaptive, child.school_year, child.age, child.language);
        }
        setTaskList(prev => [...prev, ...adaptive]);
        setStep(s => s + 1);
      } catch (e) {
        console.error("Failed to load adaptive questions:", e);
        alert("Failed to load adaptive questions. Check if backend is running.");
      } finally {
        setSubmitting(false);
      }
      return;
    }

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
          key={task.key}
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
  if (task.type === "open_ended") {
    return <OpenEndedTask task={task} answer={answer} startedAt={startedAt} setAnswer={setAnswer} selectedLanguage={selectedLanguage} />;
  }
  return <ScaleTask task={task} answer={answer} setAnswer={setAnswer} selectedLanguage={selectedLanguage} />;
}


function PatternChoice({ task, answer, startedAt, setAnswer, selectedLanguage }) {
  const sequence = Array.isArray(task.sequence) ? task.sequence : [];
  const options = Array.isArray(task.options) ? task.options : [];
  return (
    <>
      <div className="puzzle-sequence">
        {sequence.map((item, i) => <span key={`${item}-${i}`}>{item}</span>)}
      </div>
      <div className="choice-grid compact-choice-grid">
        {options.map(option => (
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
  const [count, setCount] = useState(answer?.value !== undefined ? answer.value : "");
  const symbols = Array.isArray(task.symbols) ? task.symbols : [];

  const handleChange = (val) => {
    setCount(val);
    if (val !== "") {
      const numeric = Number(val);
      const expected = task.answer || 0;
      const difference = Math.abs(numeric - expected);
      setAnswer(baseAnswer(task, numeric, {
        correct: difference === 0,
        accuracy: expected > 0 ? Math.max(0, 1 - difference / expected) : numeric === 0 ? 1 : 0,
        response_ms: Date.now() - startedAt,
      }));
    } else {
      setAnswer(null);
    }
  };

  const strings = {
    English: {
      placeholder: `Number of ${task.target || "items"}`
    },
    Hindi: {
      placeholder: `${task.target || "चीज़ें"} की संख्या`
    }
  }[selectedLanguage];

  return (
    <div className="task-stack">
      <div className="symbol-grid">
        {symbols.map((symbol, i) => <span key={`${symbol}-${i}`}>{symbol}</span>)}
      </div>
      <div className="form-row" style={{ justifyContent: "center" }}>
        <input
          type="number"
          min="0"
          value={count}
          onChange={e => handleChange(e.target.value)}
          placeholder={strings.placeholder}
          style={{ maxWidth: "200px", textAlign: "center" }}
        />
      </div>
    </div>
  );
}

function MemoryGrid({ task, answer, setAnswer, selectedLanguage }) {
  // Support both 'highlights' (component name) and 'path' (base data field)
  const highlights = Array.isArray(task.highlights) ? task.highlights
    : Array.isArray(task.path) ? task.path
    : [];
  const gridSize = task.gridSize || 9;
  const revealMs = task.revealMs || 2000;

  const [revealing, setRevealing] = useState(true);
  const [selected, setSelected] = useState(answer?.selected || []);
  const started = useMemo(() => Date.now(), [task.key]);

  useEffect(() => {
    setRevealing(true);
    setSelected([]);
    const timer = setTimeout(() => setRevealing(false), revealMs);
    return () => clearTimeout(timer);
  }, [task]);

  const toggle = (idx) => {
    if (revealing) return;
    const next = selected.includes(idx)
      ? selected.filter(i => i !== idx)
      : [...selected, idx];
    setSelected(next);

    const correctSelected = highlights.length > 0
      ? next.filter(i => highlights.includes(i)).length
      : next.length;
    const extraSelected = highlights.length > 0
      ? next.filter(i => !highlights.includes(i)).length
      : 0;
    const score = highlights.length > 0
      ? Math.max(0, correctSelected - extraSelected) / highlights.length
      : 1;
    setAnswer(baseAnswer(task, score * 4, {
      selected: next,
      correct: highlights.length > 0 ? score === 1 : true,
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
        {Array.from({ length: gridSize }, (_, idx) => {
          const active = revealing ? highlights.includes(idx) : selected.includes(idx);
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
    : (task.steps?.[selectedLanguage] || task.steps?.["English"] || []);
  const shuffledList = Array.isArray(task.shuffled)
    ? task.shuffled
    : (task.shuffled?.[selectedLanguage] || task.shuffled?.["English"] || [...stepsList]);

  const [ordered, setOrdered] = useState(answer?.ordered || shuffledList);

  useEffect(() => {
    setOrdered(answer?.ordered || shuffledList);
    if (!answer) {
      const correct = shuffledList.filter((step, idx) => step === stepsList[idx]).length;
      setAnswer(baseAnswer(task, (correct / stepsList.length) * 4, {
        ordered: shuffledList,
        correct: correct === stepsList.length,
        accuracy: correct / stepsList.length,
        response_ms: Date.now() - startedAt,
      }));
    }
  }, [task, selectedLanguage]);

  const move = (idx, direction) => {
    const target = idx + direction;
    if (target < 0 || target >= ordered.length) return;
    const next = [...ordered];
    [next[idx], next[target]] = [next[target], next[idx]];
    setOrdered(next);

    const correct = next.filter((step, idx) => step === stepsList[idx]).length;
    setAnswer(baseAnswer(task, (correct / stepsList.length) * 4, {
      ordered: next,
      correct: correct === stepsList.length,
      accuracy: correct / stepsList.length,
      response_ms: Date.now() - startedAt,
    }));
  };

  const strings = {
    English: {
      up: "Up",
      down: "Down"
    },
    Hindi: {
      up: "ऊपर",
      down: "नीचे"
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
    </div>
  );
}

function IdeaList({ task, answer, startedAt, setAnswer, selectedLanguage }) {
  const [ideas, setIdeas] = useState(() => {
    if (answer?.text) {
      const parts = answer.text.split(/\n/).map(item => item.trim()).filter(Boolean);
      return [parts[0] || "", parts[1] || "", parts[2] || ""];
    }
    return ["", "", ""];
  });

  const handleIdeaChange = (index, val) => {
    const nextIdeas = [...ideas];
    nextIdeas[index] = val;
    setIdeas(nextIdeas);

    const filtered = nextIdeas.map(i => i.trim()).filter(Boolean);
    const uniqueCount = new Set(filtered.map(i => i.toLowerCase())).size;

    if (filtered.length > 0) {
      setAnswer(baseAnswer(task, Math.min(4, uniqueCount), {
        text: filtered.join("\n"),
        idea_count: uniqueCount,
        fluency_score: Math.min(1, uniqueCount / (task.minIdeas || 1)),
        response_ms: Date.now() - startedAt,
      }));
    } else {
      setAnswer(null);
    }
  };

  const isCreativeTask = ["creative_box", "creative_circles", "creative_cloud"].includes(task.key);
  const emoji = task.key === "creative_box" ? "📦🎨🎁" : task.key === "creative_circles" ? "⭕🎨📐" : "☁️☕🥤";

  const strings = {
    English: {
      labels: [
        "First creative idea:",
        "Second creative idea:",
        "Third creative idea:"
      ],
      placeholders: task.key === "creative_box" ? [
        "e.g. Build a toy spaceship to fly to Mars",
        "e.g. Turn it into a puppet theater and put on a show",
        "e.g. Cut holes in it to make a secret fort"
      ] : task.key === "creative_circles" ? [
        "e.g. A smiling yellow sun",
        "e.g. A round wall clock pointing to lunch time",
        "e.g. A delicious pepperoni pizza"
      ] : task.key === "creative_cloud" ? [
        "e.g. Liquid gold that turns objects into treasure",
        "e.g. Melted chocolate rain that makes children happy",
        "e.g. Magic invisibility juice"
      ] : [
        "e.g. Write your first idea here",
        "e.g. Write your second idea here",
        "e.g. Write your third idea here"
      ],
      alertTitle: task.key === "creative_box" ? "Box Challenge Alert!" : task.key === "creative_circles" ? "Circles Challenge Alert!" : "Cloud Challenge Alert!",
      alertDesc: task.key === "creative_box" 
        ? "Imagine all the fun things you can make from a simple cardboard box. Think of completely different uses!"
        : task.key === "creative_circles" 
          ? "Think of how simple circles can be transformed into real objects by drawing around them."
          : "Think of what creative and unusual liquids could fall from a teacup-shaped cloud!"
    },
    Hindi: {
      labels: [
        "पहला विचार:",
        "दूसरा विचार:",
        "तीसरा विचार:"
      ],
      placeholders: task.key === "creative_box" ? [
        "उदा. मंगल ग्रह पर जाने के लिए एक खिलौना स्पेसशिप बनाएं",
        "उदा. इसे एक पपेट थिएटर (कटपुतली थियेटर) में बदलें",
        "उदा. एक गुप्त किला (secret fort) बनाने के लिए इसमें छेद काटें"
      ] : task.key === "creative_circles" ? [
        "उदा. मुस्कुराता हुआ पीला सूरज",
        "उदा. एक गोल दीवार घड़ी जो लंच के समय की ओर इशारा करती हो",
        "उदा. एक स्वादिष्ट गोल पिज्जा"
      ] : task.key === "creative_cloud" ? [
        "उदा. तरल सोना (liquid gold) जो वस्तुओं को खजाने में बदल देता है",
        "उदा. पिघली हुई चॉकलेट की बारिश जो बच्चों को खुश करती है",
        "उदा. जादुई अदृश्य होने का रस (magic invisibility juice)"
      ] : [
        "अपना पहला विचार लिखें",
        "अपना दूसरा विचार लिखें",
        "अपना तीसरा विचार लिखें"
      ],
      alertTitle: task.key === "creative_box" ? "डिब्बा चुनौती!" : task.key === "creative_circles" ? "गोला चुनौती!" : "बादल चुनौती!",
      alertDesc: task.key === "creative_box"
        ? "कल्पना कीजिए कि आप एक साधारण गत्ते के डिब्बे से क्या-क्या बना सकते हैं। बिल्कुल अलग-अलग उपयोग सोचें!"
        : task.key === "creative_circles"
          ? "सोचें कि आप गोलों (circles) के ऊपर या आस-पास चित्र बनाकर उन्हें किन अलग चीजों में बदल सकते हैं।"
          : "सोचें कि एक चाय के कप के आकार के बादल से कौन से अनोखे तरल पदार्थ गिर सकते हैं!"
    }
  }[selectedLanguage] || strings.English;

  return (
    <div className="task-stack" style={{ display: "flex", flexDirection: "column", gap: "16px", marginTop: "16px" }}>
      {isCreativeTask && (
        <div style={{
          background: "linear-gradient(135deg, #f5f3ff 0%, #e879f915 100%)",
          padding: "16px",
          borderRadius: "16px",
          border: "1.5px dashed #c084fc",
          display: "flex",
          alignItems: "center",
          gap: "16px",
          textAlign: "left"
        }}>
          <div style={{ fontSize: "40px", display: "inline-block" }}>{emoji}</div>
          <div style={{ flex: 1 }}>
            <strong style={{ color: "#7c3aed", fontSize: "14.5px", display: "block", marginBottom: "4px" }}>
              {strings.alertTitle}
            </strong>
            <span style={{ fontSize: "13px", lineHeight: "1.4", color: "#5b21b6", display: "block" }}>
              {strings.alertDesc}
            </span>
          </div>
        </div>
      )}

      {ideas.map((idea, idx) => (
        <div key={idx} style={{ display: "flex", flexDirection: "column", gap: "6px", textAlign: "left" }}>
          <label style={{ fontSize: "14.5px", fontWeight: 700, color: "#1e1b4b" }}>
            {strings.labels[idx]}
          </label>
          <input
            type="text"
            value={idea}
            onChange={e => handleIdeaChange(idx, e.target.value)}
            placeholder={strings.placeholders[idx]}
            style={{
              padding: "12px",
              borderRadius: "10px",
              border: "1px solid #cbd5e1",
              fontSize: "14.5px",
              outline: "none",
              background: "#fff",
              transition: "border-color 0.2s"
            }}
          />
        </div>
      ))}
    </div>
  );
}

function JudgementChoice({ task, answer, startedAt, setAnswer, selectedLanguage }) {
  const options = Array.isArray(task.options) ? task.options : [];
  return (
    <div className="choice-grid">
      {options.map(option => {
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

function OpenEndedTask({ task, answer, startedAt, setAnswer, selectedLanguage }) {
  const [text, setText] = useState(answer?.text || "");

  const handleChange = (val) => {
    setText(val);
    if (val.trim()) {
      setAnswer(baseAnswer(task, val, {
        text: val,
        response_ms: Date.now() - startedAt,
      }));
    } else {
      setAnswer(null);
    }
  };

  const strings = {
    English: {
      placeholder: "Type your thoughts here... Write as much as you like!"
    },
    Hindi: {
      placeholder: "अपने विचार यहाँ लिखें... आप जितना चाहें उतना लिख सकते हैं!"
    }
  }[selectedLanguage];

  return (
    <div className="task-stack">
      <textarea
        rows={6}
        value={text}
        onChange={e => handleChange(e.target.value)}
        placeholder={strings.placeholder}
        style={{
          width: "100%",
          padding: "16px",
          borderRadius: "12px",
          border: "1px solid #E2E8F0",
          fontSize: "15px",
          lineHeight: "1.6",
          fontFamily: "inherit",
          resize: "vertical",
          outline: "none",
          transition: "border-color 0.2s",
          marginBottom: "16px"
        }}
      />
    </div>
  );
}

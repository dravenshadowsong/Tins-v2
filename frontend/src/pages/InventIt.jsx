import { useState, useEffect, useRef, useCallback } from "react";
import { useParams } from "react-router-dom";
import { api } from "../api";
import "./InventIt.css";

// ──────────────────────────────────────────────────────────────────────────────
// Translations (EN / HI)
// ──────────────────────────────────────────────────────────────────────────────
const T = {
  en: {
    badge: "🔧 Inventor's Workshop",
    introTitle: "INVENT IT",
    introSub: "Turn ordinary things into extraordinary ideas!",
    missionLabel: "📋 Your Mission",
    introText: `Welcome, Inventor! 🤖

Our invention machine has stopped working.

We need someone who can think of unusual ideas.

Your mission is to turn a cardboard box into something useful, surprising, or completely new.

There are no right answers — every idea matters!

Ready?`,
    startBtn: "Start Mission 🚀",
    round1Badge: "Round 1 — Free Invention",
    round1Title: "CARDBOARD BOX",
    round1Prompt: "You have 60 seconds. Think of as many different things as you can make or do with this box.",
    round1Tip: "You can draw it, describe it, or use your voice!",
    round2Badge: "Round 2 — New Challenge",
    round2Title: "CARDBOARD BOX",
    round2Prompt: "Great! But now there is a problem.",
    constraint: "Your invention must help someone carry water without spilling it. Can you change your idea or invent a new one?",
    tabDraw: "Draw",
    tabType: "Type",
    tabVoice: "Voice",
    drawPlaceholder: "Draw your idea on the canvas →",
    typePlaceholder: "Describe your idea here... (in English or Hindi — your choice!)",
    recordStart: "Tap to record your idea",
    recordStop: "Recording... tap to stop",
    recordReplay: "▶ Play",
    recordAgain: "🔴 Record Again",
    submitIdea: "Submit Idea ✓",
    hintBtn: "Need a hint? 💡",
    hints1: [
      "What if you changed its shape? (fold it, cut it, roll it...)",
      "What if you added another material to the box?",
      "Who could this help? (someone far away, someone with a problem?)",
    ],
    hints2: [
      "What if you sealed the inside of the box?",
      "What if you lined it with something waterproof?",
      "How do you stop water from leaking through the sides?",
    ],
    ideasLabel: "Your ideas:",
    noIdeasYet: "No ideas submitted yet — go ahead!",
    round1EndTitle: "Round 1 Complete! 🎉",
    round1EndText: "Nice work! Get ready for your next challenge.",
    nextRound: "Next Challenge →",
    completionTitle: "Mission Complete!",
    completionSubtitle: "Your Inventor's Workshop is growing!",
    completionTagline: "You explored some really interesting ideas today.",
    statIdeas: "Ideas Explored",
    statRound1: "Round 1 Ideas",
    statRound2: "Round 2 Ideas",
    doneLbl: "All done! The facilitator will continue from here.",
    voiceNotSupported: "Voice recording is not supported on this device. Please use Draw or Type instead.",
    ideaAdded: "✓ Idea saved!",
    timerWarning: "Hurry! 10 seconds left!",
    timerDone: "Time's up!",
    undo: "Undo",
    erase: "Erase",
    clear: "Clear",
    done: "Done Drawing",
    colorPen: "Pen colour:",
    size: "Size:",
  },
  hi: {
    badge: "🔧 आविष्कारक की कार्यशाला",
    introTitle: "INVENT IT",
    introSub: "साधारण चीज़ों को असाधारण विचारों में बदलो!",
    missionLabel: "📋 तुम्हारा मिशन",
    introText: `नमस्ते, आविष्कारक! 🤖

हमारी आविष्कार मशीन काम करना बंद कर दिया है।

हमें किसी ऐसे की जरूरत है जो अनोखे विचार सोच सके।

तुम्हारा मिशन है — इस कार्डबोर्ड बॉक्स को कुछ उपयोगी, अचरज भरा, या बिल्कुल नया बनाना।

कोई गलत जवाब नहीं है — हर विचार मायने रखता है!

तैयार हो?`,
    startBtn: "मिशन शुरू करो 🚀",
    round1Badge: "राउंड 1 — स्वतंत्र आविष्कार",
    round1Title: "कार्डबोर्ड बॉक्स",
    round1Prompt: "तुम्हारे पास 60 सेकंड हैं। इस बॉक्स से जितने हो सके उतने अलग-अलग चीज़ें बना सकते हो या कर सकते हो, सोचो।",
    round1Tip: "चित्र बना सकते हो, लिख सकते हो, या बोल सकते हो!",
    round2Badge: "राउंड 2 — नई चुनौती",
    round2Title: "कार्डबोर्ड बॉक्स",
    round2Prompt: "बहुत बढ़िया! लेकिन अब एक समस्या है।",
    constraint: "तुम्हारे आविष्कार से किसी की मदद होनी चाहिए पानी बिना गिराए ले जाने में। क्या तुम अपना विचार बदल सकते हो या नया बना सकते हो?",
    tabDraw: "चित्र",
    tabType: "लिखो",
    tabVoice: "बोलो",
    drawPlaceholder: "कैनवास पर अपना विचार बनाओ →",
    typePlaceholder: "यहाँ अपना विचार लिखो... (हिंदी या अंग्रेज़ी में — तुम्हारी पसंद!)",
    recordStart: "अपना विचार रिकॉर्ड करने के लिए टैप करो",
    recordStop: "रिकॉर्ड हो रहा है... रोकने के लिए टैप करो",
    recordReplay: "▶ सुनो",
    recordAgain: "🔴 फिर से रिकॉर्ड करो",
    submitIdea: "विचार जमा करो ✓",
    hintBtn: "संकेत चाहिए? 💡",
    hints1: [
      "क्या होगा अगर आकार बदल दो? (मोड़ो, काटो, लपेटो...)",
      "क्या होगा अगर बॉक्स में कोई और चीज़ जोड़ दो?",
      "इससे किसकी मदद हो सकती है? (कोई दूर है, या किसी को कोई समस्या है?)",
    ],
    hints2: [
      "क्या होगा अगर बॉक्स के अंदर को बंद कर दो?",
      "क्या होगा अगर अंदर कुछ वाटरप्रूफ लगाओ?",
      "पानी को किनारों से टपकने से कैसे रोकोगे?",
    ],
    ideasLabel: "तुम्हारे विचार:",
    noIdeasYet: "अभी तक कोई विचार नहीं — आगे बढ़ो!",
    round1EndTitle: "राउंड 1 पूरा! 🎉",
    round1EndText: "बहुत बढ़िया! अगली चुनौती के लिए तैयार हो जाओ।",
    nextRound: "अगली चुनौती →",
    completionTitle: "मिशन पूरा!",
    completionSubtitle: "तुम्हारी आविष्कारक कार्यशाला बड़ी हो रही है!",
    completionTagline: "आज तुमने बहुत रोचक विचार खोजे।",
    statIdeas: "खोजे गए विचार",
    statRound1: "राउंड 1 के विचार",
    statRound2: "राउंड 2 के विचार",
    doneLbl: "सब हो गया! अब सुविधाकर्ता आगे ले जाएंगे।",
    voiceNotSupported: "इस डिवाइस पर वॉइस रिकॉर्डिंग नहीं चलती। कृपया चित्र या लिखो विकल्प इस्तेमाल करें।",
    ideaAdded: "✓ विचार सेव हुआ!",
    timerWarning: "जल्दी! 10 सेकंड बचे!",
    timerDone: "समय खत्म!",
    undo: "पूर्ववत",
    erase: "मिटाओ",
    clear: "साफ करो",
    done: "चित्र बना लिया",
    colorPen: "पेन रंग:",
    size: "आकार:",
  },
};

const ROUND_DURATION = 60; // seconds
const PALETTE = ["#1a1a2e","#e63946","#457b9d","#2d6a4f","#f4a261","#6366f1","#f72585","#06b6d4"];
const CONFETTI_COLORS = ["#f5a623","#6366f1","#22c55e","#ef4444","#06b6d4","#f72585"];

// ──────────────────────────────────────────────────────────────────────────────
// Timer Ring Component
// ──────────────────────────────────────────────────────────────────────────────
function TimerRing({ seconds, total = ROUND_DURATION }) {
  const r = 26;
  const circ = 2 * Math.PI * r;
  const offset = circ - (seconds / total) * circ;
  const pct = seconds / total;
  const cls = pct < 0.2 ? "danger" : pct < 0.4 ? "warning" : "";
  return (
    <div className="ii-timer-ring-wrap">
      <svg width={64} height={64} style={{ transform: "rotate(-90deg)" }}>
        <circle className="timer-bg" cx={32} cy={32} r={r} />
        <circle className={`timer-fg ${cls}`} cx={32} cy={32} r={r}
          strokeDasharray={circ} strokeDashoffset={offset} />
      </svg>
      <span className="ii-timer-digits" style={{ color: pct < 0.2 ? "#ef4444" : pct < 0.4 ? "#f97316" : "#f5a623" }}>
        {seconds}
      </span>
    </div>
  );
}

// ──────────────────────────────────────────────────────────────────────────────
// Drawing Canvas Component
// ──────────────────────────────────────────────────────────────────────────────
function DrawingCanvas({ onReady, t }) {
  const canvasRef = useRef(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [isErasing, setIsErasing] = useState(false);
  const [color, setColor] = useState("#1a1a2e");
  const [brushSize, setBrushSize] = useState(4);
  const [history, setHistory] = useState([]);
  const lastPt = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    canvas.width = canvas.offsetWidth * window.devicePixelRatio;
    canvas.height = 320 * window.devicePixelRatio;
    canvas.style.height = "320px";
    ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    ctx.fillStyle = "#ffffff";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    saveHistory();
  }, []);

  const saveHistory = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    setHistory(h => [...h.slice(-19), canvas.toDataURL()]);
  };

  const getPos = (e) => {
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const touch = e.touches ? e.touches[0] : e;
    return {
      x: (touch.clientX - rect.left),
      y: (touch.clientY - rect.top),
    };
  };

  const startDraw = (e) => {
    e.preventDefault();
    setIsDrawing(true);
    const pos = getPos(e);
    lastPt.current = pos;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    ctx.beginPath();
    ctx.arc(pos.x, pos.y, (isErasing ? brushSize * 4 : brushSize) / 2, 0, Math.PI * 2);
    ctx.fillStyle = isErasing ? "#ffffff" : color;
    ctx.fill();
  };

  const draw = (e) => {
    e.preventDefault();
    if (!isDrawing) return;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    const pos = getPos(e);
    ctx.globalCompositeOperation = isErasing ? "source-over" : "source-over";
    ctx.strokeStyle = isErasing ? "#ffffff" : color;
    ctx.lineWidth = isErasing ? brushSize * 4 : brushSize;
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    ctx.beginPath();
    ctx.moveTo(lastPt.current.x, lastPt.current.y);
    ctx.lineTo(pos.x, pos.y);
    ctx.stroke();
    lastPt.current = pos;
  };

  const endDraw = () => {
    if (isDrawing) {
      setIsDrawing(false);
      saveHistory();
    }
  };

  const handleUndo = () => {
    if (history.length < 2) return;
    const prev = history[history.length - 2];
    const img = new Image();
    img.onload = () => {
      const canvas = canvasRef.current;
      const ctx = canvas.getContext("2d");
      ctx.clearRect(0, 0, canvas.offsetWidth, canvas.offsetHeight);
      ctx.drawImage(img, 0, 0, canvas.offsetWidth, canvas.offsetHeight);
    };
    img.src = prev;
    setHistory(h => h.slice(0, -1));
  };

  const handleClear = () => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    ctx.fillStyle = "#ffffff";
    ctx.fillRect(0, 0, canvas.offsetWidth, canvas.offsetHeight);
    saveHistory();
  };

  const getDataUrl = () => canvasRef.current?.toDataURL("image/png");

  // Expose via ref callback
  useEffect(() => {
    if (onReady) onReady({ getDataUrl, clear: handleClear });
  }, []);

  return (
    <div className="ii-canvas-wrap">
      <canvas ref={canvasRef} className="ii-canvas"
        onMouseDown={startDraw} onMouseMove={draw} onMouseUp={endDraw} onMouseLeave={endDraw}
        onTouchStart={startDraw} onTouchMove={draw} onTouchEnd={endDraw}
      />
      <div className="ii-canvas-toolbar">
        <button className="ii-canvas-btn" onClick={handleUndo}>↩ {t.undo}</button>
        <button className={`ii-canvas-btn ${isErasing ? "active" : ""}`} onClick={() => setIsErasing(e => !e)}>
          🧹 {t.erase}
        </button>
        <button className="ii-canvas-btn" onClick={handleClear}>🗑 {t.clear}</button>
        <span style={{ marginLeft: 4, fontSize: 12, color: "var(--ii-text-muted)" }}>{t.colorPen}</span>
        {PALETTE.map(c => (
          <div key={c} className={`ii-color-swatch ${color === c ? "selected" : ""}`}
            style={{ background: c }} onClick={() => { setColor(c); setIsErasing(false); }} />
        ))}
        <span className="ii-brush-size">
          {t.size}
          <input type="range" min="2" max="20" value={brushSize} className="ii-brush-slider"
            onChange={e => setBrushSize(Number(e.target.value))} />
        </span>
      </div>
    </div>
  );
}

// ──────────────────────────────────────────────────────────────────────────────
// Voice Recorder Component
// ──────────────────────────────────────────────────────────────────────────────
function VoiceRecorder({ onSubmit, t, language }) {
  const [recording, setRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const [audioUrl, setAudioUrl] = useState(null);
  const [transcript, setTranscript] = useState("");
  const [bars, setBars] = useState(Array(24).fill(4));
  const [supported] = useState(() => !!(navigator.mediaDevices && window.MediaRecorder));
  const mediaRef = useRef(null);
  const chunksRef = useRef([]);
  const analyserRef = useRef(null);
  const rafRef = useRef(null);
  const recognitionRef = useRef(null);

  const animateBars = () => {
    if (!analyserRef.current) return;
    const data = new Uint8Array(analyserRef.current.frequencyBinCount);
    analyserRef.current.getByteFrequencyData(data);
    const step = Math.floor(data.length / 24);
    setBars(Array.from({ length: 24 }, (_, i) => Math.max(4, (data[i * step] / 255) * 48)));
    rafRef.current = requestAnimationFrame(animateBars);
  };

  const startRecording = async () => {
    if (!supported) return;
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const ctx = new AudioContext();
      const src = ctx.createMediaStreamSource(stream);
      const analyser = ctx.createAnalyser();
      analyser.fftSize = 256;
      src.connect(analyser);
      analyserRef.current = analyser;

      const mr = new MediaRecorder(stream);
      chunksRef.current = [];
      mr.ondataavailable = (e) => chunksRef.current.push(e.data);
      mr.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: "audio/webm" });
        setAudioBlob(blob);
        setAudioUrl(URL.createObjectURL(blob));
        stream.getTracks().forEach(t => t.stop());
        cancelAnimationFrame(rafRef.current);
        setBars(Array(24).fill(4));
      };
      mr.start();
      mediaRef.current = mr;
      setRecording(true);
      setTranscript("");
      animateBars();

      // Speech recognition for transcript
      const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (SR) {
        const rec = new SR();
        rec.lang = language === "hi" ? "hi-IN" : "en-US";
        rec.continuous = true;
        rec.interimResults = true;
        rec.onresult = (ev) => {
          const txt = Array.from(ev.results).map(r => r[0].transcript).join(" ");
          setTranscript(txt);
        };
        rec.start();
        recognitionRef.current = rec;
      }
    } catch (err) {
      console.error("Microphone error:", err);
    }
  };

  const stopRecording = () => {
    mediaRef.current?.stop();
    recognitionRef.current?.stop();
    setRecording(false);
  };

  const handleSubmit = () => {
    if (audioBlob || transcript) {
      onSubmit({ audioBlob, transcript, type: "voice" });
      setAudioBlob(null);
      setAudioUrl(null);
      setTranscript("");
    }
  };

  if (!supported) {
    return (
      <div className="ii-voice-panel">
        <div style={{ color: "var(--ii-text-muted)", textAlign: "center", maxWidth: 320 }}>
          {t.voiceNotSupported}
        </div>
      </div>
    );
  }

  return (
    <div className="ii-voice-panel">
      <button className={`ii-record-btn ${recording ? "recording" : ""}`}
        onClick={recording ? stopRecording : startRecording}>
        {recording ? "⏹" : "🎤"}
      </button>
      <div className={`ii-record-status ${recording ? "active" : ""}`}>
        {recording ? t.recordStop : audioUrl ? "✓ Recording saved" : t.recordStart}
      </div>
      {recording && (
        <div className="ii-voice-waveform">
          {bars.map((h, i) => (
            <div key={i} className="ii-wave-bar" style={{ height: h }} />
          ))}
        </div>
      )}
      {audioUrl && !recording && (
        <div className="ii-voice-playback">
          <audio controls src={audioUrl} style={{ maxWidth: 280 }} />
          <button className="ii-canvas-btn" onClick={() => { setAudioBlob(null); setAudioUrl(null); setTranscript(""); }}>
            {t.recordAgain}
          </button>
        </div>
      )}
      {transcript && (
        <div className="ii-voice-transcript">"{transcript}"</div>
      )}
      {(audioBlob || transcript) && (
        <button className="ii-submit-btn" onClick={handleSubmit}>
          {t.submitIdea}
        </button>
      )}
    </div>
  );
}

// ──────────────────────────────────────────────────────────────────────────────
// Mascot Component
// ──────────────────────────────────────────────────────────────────────────────
function Mascot() {
  return (
    <div className="ii-mascot">
      <div className="ii-mascot-inner">
        <div className="ii-mascot-head">
          <div className="ii-mascot-antenna" />
          <div className="ii-mascot-eyes">
            <div className="ii-mascot-eye" />
            <div className="ii-mascot-eye" />
          </div>
          <div className="ii-mascot-mouth" />
        </div>
        <div className="ii-mascot-body">
          <div className="ii-mascot-arm-l" />
          <div className="ii-mascot-arm-r" />
        </div>
      </div>
    </div>
  );
}

// ──────────────────────────────────────────────────────────────────────────────
// Confetti Component
// ──────────────────────────────────────────────────────────────────────────────
function Confetti() {
  const pieces = Array.from({ length: 60 }, (_, i) => ({
    id: i,
    color: CONFETTI_COLORS[i % CONFETTI_COLORS.length],
    left: `${Math.random() * 100}%`,
    delay: `${Math.random() * 3}s`,
    duration: `${2 + Math.random() * 3}s`,
    size: `${6 + Math.random() * 8}px`,
    rotation: `${Math.random() * 360}deg`,
  }));

  return (
    <div className="ii-completion-confetti">
      {pieces.map(p => (
        <div key={p.id} className="confetti-piece" style={{
          background: p.color,
          left: p.left,
          animationDelay: p.delay,
          animationDuration: p.duration,
          width: p.size,
          height: p.size,
          transform: `rotate(${p.rotation})`,
        }} />
      ))}
    </div>
  );
}

// ──────────────────────────────────────────────────────────────────────────────
// Toast Notification
// ──────────────────────────────────────────────────────────────────────────────
function Toast({ msg, type = "success", onDone }) {
  useEffect(() => {
    const t = setTimeout(onDone, 2500);
    return () => clearTimeout(t);
  }, []);
  return <div className={`ii-toast ${type}`}>{msg}</div>;
}

// ──────────────────────────────────────────────────────────────────────────────
// Main InventIt Component
// ──────────────────────────────────────────────────────────────────────────────
export default function InventIt() {
  const { sid } = useParams();
  const [lang, setLang] = useState("en");
  const t = T[lang];

  // Game state
  const [phase, setPhase] = useState("intro"); // intro | round1 | round1end | round2 | complete | loading
  const [sessionUuid, setSessionUuid] = useState(null);
  const [mode, setMode] = useState("type"); // type | draw | voice
  const [textInput, setTextInput] = useState("");
  const [ideas, setIdeas] = useState([]); // { id, text, type, dataUrl?, round }
  const [hintVisible, setHintVisible] = useState(false);
  const [hintIndex, setHintIndex] = useState(0);
  const [toast, setToast] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Timer
  const [timeLeft, setTimeLeft] = useState(ROUND_DURATION);
  const [timerActive, setTimerActive] = useState(false);
  const timerRef = useRef(null);
  const startTsRef = useRef(null);
  const firstResponseTsRef = useRef(null);

  // Event buffer
  const eventBuffer = useRef([]);
  const ideaIndexRef = useRef(0);

  // Canvas
  const canvasApiRef = useRef(null);

  const currentRound = phase === "round1" ? 1 : phase === "round2" ? 2 : null;
  const hints = currentRound === 2 ? t.hints2 : t.hints1;

  // ── Session Creation ──────────────────────────────────────────────────────
  const createSession = async (langOverride) => {
    setPhase("loading");
    const token = sessionStorage.getItem("goat_token");
    try {
      const res = await fetch(`${import.meta.env.DEV ? "/api" : (import.meta.env.VITE_API_URL || "https://tins-v2-1.onrender.com/api")}/invent-it/sessions`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}) },
        body: JSON.stringify({ student_id: sid ? Number(sid) : null, language: langOverride || lang }),
      });
      const data = await res.json();
      setSessionUuid(data.session_uuid);
    } catch (e) {
      // Create a local UUID fallback so the game can still run
      setSessionUuid(`local-${Date.now()}`);
    }
  };

  // ── Timer Logic ───────────────────────────────────────────────────────────
  const startTimer = () => {
    setTimerActive(true);
    startTsRef.current = Date.now();
    timerRef.current = setInterval(() => {
      setTimeLeft(prev => {
        if (prev <= 1) {
          clearInterval(timerRef.current);
          setTimerActive(false);
          handleTimerEnd();
          return 0;
        }
        if (prev === 10) showToast(t.timerWarning, "warning");
        return prev - 1;
      });
    }, 1000);
  };

  const handleTimerEnd = () => {
    if (phase === "round1") {
      logEvent("timer_end", { round: 1 });
      setPhase("round1end");
    } else if (phase === "round2") {
      logEvent("timer_end", { round: 2 });
      completeSession();
    }
  };

  useEffect(() => () => clearInterval(timerRef.current), []);

  // ── Start Rounds ──────────────────────────────────────────────────────────
  const startRound1 = async () => {
    await createSession(lang);
    setPhase("round1");
    setTimeLeft(ROUND_DURATION);
    setIdeas([]);
    startTimer();
    logEvent("round_start", { round: 1 });
  };

  const startRound2 = () => {
    setPhase("round2");
    setTimeLeft(ROUND_DURATION);
    startTimer();
    logEvent("round_start", { round: 2 });
  };

  // ── Event Logging ─────────────────────────────────────────────────────────
  const logEvent = (type, data = {}) => {
    eventBuffer.current.push({ round_id: currentRound, event_type: type, event_data: data, ts: Date.now() });
  };

  const flushEvents = async (uuid) => {
    if (!eventBuffer.current.length || !uuid) return;
    const events = [...eventBuffer.current];
    eventBuffer.current = [];
    const base = import.meta.env.DEV ? "/api" : (import.meta.env.VITE_API_URL || "https://tins-v2-1.onrender.com/api");
    const token = sessionStorage.getItem("goat_token");
    try {
      await fetch(`${base}/invent-it/sessions/${uuid}/events`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}) },
        body: JSON.stringify({ events }),
      });
    } catch (e) { /* non-critical */ }
  };

  // ── Submit Idea ───────────────────────────────────────────────────────────
  const submitIdea = async (overrideData = null) => {
    const round = currentRound;
    if (!round) return;
    if (!firstResponseTsRef.current) firstResponseTsRef.current = Date.now();

    let inputType = overrideData?.type || mode;
    let textContent = "";
    let drawingDataUrl = null;
    let voiceTranscript = "";

    if (overrideData?.type === "voice") {
      voiceTranscript = overrideData.transcript || "";
      textContent = voiceTranscript;
    } else if (inputType === "draw") {
      drawingDataUrl = canvasApiRef.current?.getDataUrl();
      if (!drawingDataUrl) { showToast("Draw something first!", "warning"); return; }
      textContent = "";
    } else {
      textContent = textInput.trim();
      if (!textContent) { showToast("Write something first! ✏️", "warning"); return; }
    }

    setIsSubmitting(true);
    const idx = ++ideaIndexRef.current;
    const newIdea = { id: idx, text: textContent || voiceTranscript || "🎨 Drawing", type: inputType, dataUrl: drawingDataUrl, round };
    setIdeas(prev => [...prev, newIdea]);

    logEvent("idea_submit", { round, input_type: inputType, idea_index: idx });

    // API call
    if (sessionUuid && !sessionUuid.startsWith("local-")) {
      const base = import.meta.env.DEV ? "/api" : (import.meta.env.VITE_API_URL || "https://tins-v2-1.onrender.com/api");
      const token = sessionStorage.getItem("goat_token");
      try {
        await fetch(`${base}/invent-it/sessions/${sessionUuid}/round/${round}/response`, {
          method: "POST",
          headers: { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}) },
          body: JSON.stringify({
            input_type: inputType,
            text_content: textContent,
            voice_transcript: voiceTranscript,
            language: lang,
            idea_index: idx,
            duration_ms: startTsRef.current ? Date.now() - startTsRef.current : 0,
          }),
        });
      } catch (e) { /* offline graceful */ }
    }

    // Clear inputs
    if (inputType === "text") setTextInput("");
    if (inputType === "draw") canvasApiRef.current?.clear();
    setIsSubmitting(false);
    setHintVisible(false);
    showToast(t.ideaAdded, "success");
  };

  // ── Hint ──────────────────────────────────────────────────────────────────
  const showHint = async () => {
    const nextIdx = hintVisible ? (hintIndex + 1) % hints.length : hintIndex;
    setHintIndex(nextIdx);
    setHintVisible(true);
    logEvent("hint_requested", { hint_index: nextIdx });
    if (sessionUuid && !sessionUuid.startsWith("local-")) {
      const base = import.meta.env.DEV ? "/api" : (import.meta.env.VITE_API_URL || "https://tins-v2-1.onrender.com/api");
      const token = sessionStorage.getItem("goat_token");
      try {
        await fetch(`${base}/invent-it/sessions/${sessionUuid}/hint`, {
          method: "POST",
          headers: { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}) },
        });
      } catch (e) {}
    }
  };

  // ── Complete Session ──────────────────────────────────────────────────────
  const completeSession = async () => {
    clearInterval(timerRef.current);
    setPhase("complete");
    const totalMs = startTsRef.current ? Date.now() - startTsRef.current : 0;
    const timeToFirst = firstResponseTsRef.current && startTsRef.current
      ? firstResponseTsRef.current - startTsRef.current : 0;
    const r1Ideas = ideas.filter(i => i.round === 1);
    const r2Ideas = ideas.filter(i => i.round === 2);

    await flushEvents(sessionUuid);

    if (sessionUuid && !sessionUuid.startsWith("local-")) {
      const base = import.meta.env.DEV ? "/api" : (import.meta.env.VITE_API_URL || "https://tins-v2-1.onrender.com/api");
      const token = sessionStorage.getItem("goat_token");
      try {
        await fetch(`${base}/invent-it/sessions/${sessionUuid}/complete`, {
          method: "POST",
          headers: { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}) },
          body: JSON.stringify({
            total_duration_ms: totalMs,
            time_to_first_response_ms: timeToFirst,
            hint_count: hintIndex + (hintVisible ? 0 : -1) >= 0 ? hintIndex : 0,
            round1_output: { ideas: r1Ideas.map(i => ({ text: i.text, type: i.type })) },
            round2_output: { ideas: r2Ideas.map(i => ({ text: i.text, type: i.type })) },
          }),
        });
      } catch (e) {}
    }
  };

  // ── Toast helper ──────────────────────────────────────────────────────────
  const showToast = (msg, type = "success") => setToast({ msg, type, key: Date.now() });

  // ── Mode switch event ─────────────────────────────────────────────────────
  const switchMode = (m) => {
    setMode(m);
    logEvent("mode_switch", { to: m });
  };

  // ── Render helpers ────────────────────────────────────────────────────────
  const round1Ideas = ideas.filter(i => i.round === 1);
  const round2Ideas = ideas.filter(i => i.round === 2);
  const currentIdeas = phase === "round2" ? round2Ideas : round1Ideas;

  const canSubmitText = mode === "text" && textInput.trim().length > 0;
  const canSubmit = mode !== "voice" && (mode === "draw" || canSubmitText);

  // ── RENDER ────────────────────────────────────────────────────────────────
  return (
    <div className="ii-container">
      {/* Decorative gears */}
      <div className="ii-gear ii-gear-1">⚙</div>
      <div className="ii-gear ii-gear-2">⚙</div>

      {/* Language Toggle */}
      <div className="ii-lang-toggle">
        <button className={`ii-lang-btn ${lang === "en" ? "active" : ""}`} onClick={() => setLang("en")}>EN</button>
        <button className={`ii-lang-btn ${lang === "hi" ? "active" : ""}`} onClick={() => setLang("hi")}>हि</button>
      </div>

      {/* Toast */}
      {toast && <Toast key={toast.key} msg={toast.msg} type={toast.type} onDone={() => setToast(null)} />}

      {/* ── INTRO ── */}
      {phase === "intro" && (
        <div className="ii-intro">
          <div className="ii-logo-badge">{t.badge}</div>
          <Mascot />
          <h1 className="ii-intro-title">{t.introTitle}</h1>
          <p className="ii-intro-subtitle">{t.introSub}</p>
          <div className="ii-mission-card">
            <div className="ii-mission-label">{t.missionLabel}</div>
            <div className="ii-mission-text">{t.introText}</div>
          </div>
          <button className="ii-start-btn" onClick={() => startRound1()}>
            {t.startBtn}
          </button>
        </div>
      )}

      {/* ── LOADING ── */}
      {phase === "loading" && (
        <div className="ii-loader">
          <div className="ii-spinner" />
          <p style={{ color: "var(--ii-text-muted)", fontWeight: 600 }}>Setting up your workshop...</p>
        </div>
      )}

      {/* ── ROUND 1 ── */}
      {phase === "round1" && (
        <div className="ii-round-wrap">
          <div className="ii-round-header">
            <span className="ii-round-badge">🔧 {t.round1Badge}</span>
            <TimerRing seconds={timeLeft} />
          </div>
          <div className="ii-prompt-card">
            <div className="ii-prompt-object">
              <span className="ii-object-icon">📦</span>
              <div className="ii-prompt-text">
                <h3>{t.round1Title}</h3>
                <p>{t.round1Prompt}</p>
                <p style={{ marginTop: 8, fontSize: 14, color: "var(--ii-amber)" }}>💡 {t.round1Tip}</p>
              </div>
            </div>
          </div>

          {/* Mode Tabs */}
          <div className="ii-mode-tabs">
            {[["draw","✏️","Draw"],["type","⌨️","Type"],["voice","🎤","Voice"]].map(([m, icon, label]) => (
              <button key={m} className={`ii-mode-tab ${mode === m ? "active" : ""}`} onClick={() => switchMode(m)}>
                <span className="tab-icon">{icon}</span>
                <span className="tab-label">{t[`tab${label}`]}</span>
              </button>
            ))}
          </div>

          {/* Input Panel */}
          <div className="ii-input-panel">
            {mode === "draw" && (
              <DrawingCanvas t={t} onReady={api => { canvasApiRef.current = api; }} />
            )}
            {mode === "type" && (
              <textarea className="ii-text-area" placeholder={t.typePlaceholder}
                value={textInput} onChange={e => setTextInput(e.target.value)}
                onKeyDown={e => { if (e.key === "Enter" && e.ctrlKey) submitIdea(); }} />
            )}
            {mode === "voice" && (
              <VoiceRecorder onSubmit={(d) => submitIdea(d)} t={t} language={lang} />
            )}
          </div>

          {/* Submit Bar */}
          {mode !== "voice" && (
            <div className="ii-submit-bar">
              <button className="ii-submit-btn" onClick={() => submitIdea()} disabled={isSubmitting || !canSubmit}>
                {isSubmitting ? "⏳" : t.submitIdea}
              </button>
              <button className="ii-hint-btn" onClick={showHint}>{t.hintBtn}</button>
            </div>
          )}

          {hintVisible && (
            <div className="ii-hint-bubble">💡 {hints[hintIndex % hints.length]}</div>
          )}

          {/* Idea Gallery */}
          <div className="ii-idea-gallery">
            <div className="ii-gallery-header">{t.ideasLabel} ({round1Ideas.length})</div>
            {round1Ideas.length === 0 ? (
              <p style={{ color: "var(--ii-text-dim)", fontSize: 14 }}>{t.noIdeasYet}</p>
            ) : (
              <div className="ii-idea-list">
                {round1Ideas.map((idea, i) => (
                  <div key={idea.id} className={`ii-idea-card ${idea.type === "draw" ? "draw-type" : ""}`}>
                    <span className="ii-idea-card-type">{idea.type === "draw" ? "✏️" : idea.type === "voice" ? "🎤" : "✍️"}</span>
                    {idea.dataUrl ? (
                      <img src={idea.dataUrl} alt={`idea ${i+1}`} />
                    ) : (
                      <>
                        <div className="ii-idea-card-index">#{i + 1}</div>
                        {idea.text}
                      </>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* ── ROUND 1 END ── */}
      {phase === "round1end" && (
        <div className="ii-round-wrap">
          <div className="ii-round-end">
            <div style={{ fontSize: 72, marginBottom: 24 }}>🎉</div>
            <h2>{t.round1EndTitle}</h2>
            <p>{t.round1EndText}</p>
            <div style={{ margin: "0 0 32px", padding: "16px 24px", background: "var(--ii-surface)", borderRadius: "var(--ii-radius)", border: "1px solid var(--ii-border)" }}>
              <strong style={{ color: "var(--ii-amber)" }}>Round 1:</strong>{" "}
              {round1Ideas.length} ideas explored
            </div>
            <button className="ii-next-btn" onClick={startRound2}>{t.nextRound}</button>
          </div>
        </div>
      )}

      {/* ── ROUND 2 ── */}
      {phase === "round2" && (
        <div className="ii-round-wrap">
          <div className="ii-round-header">
            <span className="ii-round-badge" style={{ background: "linear-gradient(135deg, #f97316, #dc2626)" }}>
              🌊 {t.round2Badge}
            </span>
            <TimerRing seconds={timeLeft} />
          </div>
          <div className="ii-prompt-card">
            <div className="ii-prompt-object">
              <span className="ii-object-icon">📦</span>
              <div className="ii-prompt-text">
                <h3>{t.round2Title}</h3>
                <p>{t.round2Prompt}</p>
              </div>
            </div>
            <div className="ii-constraint-banner">
              <span className="ii-constraint-icon">💧</span>
              <div className="ii-constraint-text">
                <strong>{t.constraint}</strong>
              </div>
            </div>
          </div>

          {/* Mode Tabs */}
          <div className="ii-mode-tabs">
            {[["draw","✏️","Draw"],["type","⌨️","Type"],["voice","🎤","Voice"]].map(([m, icon, label]) => (
              <button key={m} className={`ii-mode-tab ${mode === m ? "active" : ""}`} onClick={() => switchMode(m)}>
                <span className="tab-icon">{icon}</span>
                <span className="tab-label">{t[`tab${label}`]}</span>
              </button>
            ))}
          </div>

          {/* Input Panel */}
          <div className="ii-input-panel">
            {mode === "draw" && (
              <DrawingCanvas t={t} onReady={api => { canvasApiRef.current = api; }} />
            )}
            {mode === "type" && (
              <textarea className="ii-text-area" placeholder={t.typePlaceholder}
                value={textInput} onChange={e => setTextInput(e.target.value)}
                onKeyDown={e => { if (e.key === "Enter" && e.ctrlKey) submitIdea(); }} />
            )}
            {mode === "voice" && (
              <VoiceRecorder onSubmit={(d) => submitIdea(d)} t={t} language={lang} />
            )}
          </div>

          {mode !== "voice" && (
            <div className="ii-submit-bar">
              <button className="ii-submit-btn" onClick={() => submitIdea()} disabled={isSubmitting || !canSubmit}>
                {isSubmitting ? "⏳" : t.submitIdea}
              </button>
              <button className="ii-hint-btn" onClick={showHint}>{t.hintBtn}</button>
            </div>
          )}

          {hintVisible && (
            <div className="ii-hint-bubble">💡 {hints[hintIndex % hints.length]}</div>
          )}

          <div className="ii-idea-gallery">
            <div className="ii-gallery-header">{t.ideasLabel} ({round2Ideas.length})</div>
            {round2Ideas.length === 0 ? (
              <p style={{ color: "var(--ii-text-dim)", fontSize: 14 }}>{t.noIdeasYet}</p>
            ) : (
              <div className="ii-idea-list">
                {round2Ideas.map((idea, i) => (
                  <div key={idea.id} className={`ii-idea-card ${idea.type === "draw" ? "draw-type" : ""}`}>
                    <span className="ii-idea-card-type">{idea.type === "draw" ? "✏️" : idea.type === "voice" ? "🎤" : "✍️"}</span>
                    {idea.dataUrl ? (
                      <img src={idea.dataUrl} alt={`idea ${i+1}`} />
                    ) : (
                      <>
                        <div className="ii-idea-card-index">#{i + 1}</div>
                        {idea.text}
                      </>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* ── COMPLETION ── */}
      {phase === "complete" && (
        <div className="ii-completion">
          <Confetti />
          <span className="ii-completion-star">⭐</span>
          <h1>{t.completionTitle}</h1>
          <h2>{t.completionSubtitle}</h2>
          <p className="tagline">{t.completionTagline}</p>
          <div className="ii-stats-grid">
            <div className="ii-stat-card">
              <div className="ii-stat-value">{ideas.length}</div>
              <div className="ii-stat-label">{t.statIdeas}</div>
            </div>
            <div className="ii-stat-card">
              <div className="ii-stat-value">{round1Ideas.length}</div>
              <div className="ii-stat-label">{t.statRound1}</div>
            </div>
            <div className="ii-stat-card">
              <div className="ii-stat-value">{round2Ideas.length}</div>
              <div className="ii-stat-label">{t.statRound2}</div>
            </div>
          </div>
          <p style={{ color: "var(--ii-text-muted)", fontSize: 15, maxWidth: 400 }}>
            {t.doneLbl}
          </p>
          {sessionUuid && (
            <div style={{ marginTop: 24, padding: "10px 20px", background: "var(--ii-surface)", borderRadius: 10, border: "1px solid var(--ii-border)", fontSize: 12, color: "var(--ii-text-dim)", fontFamily: "monospace" }}>
              Session: {sessionUuid.slice(0, 18)}…
            </div>
          )}
        </div>
      )}
    </div>
  );
}

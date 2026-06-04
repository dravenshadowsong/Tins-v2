import { useEffect, useState } from "react";
import { useParams, useSearchParams, useNavigate } from "react-router-dom";
import { api } from "../api";
import { DOMAINS } from "../data/questions";

const DOMAIN_INSIGHTS = {
  kinesthetic: "You have a natural connection with your body and movement. You learn best by doing, moving, and making. Sports, dance, craft, and hands-on work are your natural home.",
  creative: "Your mind generates vivid images and original ideas. You see the world differently from most people, and that is your greatest strength. Art, music, and storytelling will help you grow.",
  logical: "You love finding patterns, solving problems, and understanding how systems work. Maths, science, coding, and structured thinking light you up naturally.",
  spatial: "You think in three dimensions. You can picture how things fit together before you build them. Engineering, design, architecture, and making things are where you shine.",
  social: "You understand people deeply and naturally bring others together. Leadership, community work, teaching, and social enterprise are spaces where your talent will flourish.",
  language: "Words flow naturally for you. You can express, explain, persuade, and perform. Writing, theatre, journalism, and communication are your natural territories.",
  naturalist: "You notice what others miss in the living world. Plants, animals, ecosystems, and the patterns of nature speak to you. Environmental science, animal care, and nature education suit you well.",
  intrapersonal: "You have unusual depth of self-awareness and emotional intelligence. You reflect deeply, feel strongly, and understand yourself well. Counselling, philosophy, writing, and mentoring are your domains.",
};

function RadarChart({ scores }) {
  const domains = [
    { key: "creative", label: "Creative & Artistic" },
    { key: "spatial", label: "Spatial & Making" },
    { key: "language", label: "Communication" },
    { key: "social", label: "Leadership & Social" },
    { key: "logical", label: "Logical & Analytical" },
    { key: "naturalist", label: "Naturalist" },
    { key: "kinesthetic", label: "Kinesthetic" },
    { key: "intrapersonal", label: "Intrapersonal" },
  ];

  const width = 360;
  const height = 360;
  const center = 180;
  const radius = 110;

  const getCoords = (index, value) => {
    const angle = (index * 2 * Math.PI) / 8 - Math.PI / 2;
    const dist = (value / 100) * radius;
    return {
      x: center + dist * Math.cos(angle),
      y: center + dist * Math.sin(angle)
    };
  };

  const grids = [20, 40, 60, 80, 100];
  const gridPaths = grids.map(g => {
    return domains.map((_, i) => {
      const pt = getCoords(i, g);
      return `${pt.x},${pt.y}`;
    }).join(" ");
  });

  const scorePoints = domains.map((d, i) => {
    const score = scores[d.key] || 0;
    const pt = getCoords(i, score);
    return `${pt.x},${pt.y}`;
  }).join(" ");

  return (
    <svg width="100%" height="100%" viewBox={`0 0 ${width} ${height}`} style={{ maxWidth: 360, margin: "0 auto", display: "block" }}>
      {/* Concentric grid lines */}
      {gridPaths.map((path, i) => (
        <polygon key={i} points={path} fill="none" stroke="rgba(108, 92, 231, 0.12)" strokeWidth="1.2" />
      ))}
      
      {/* Concentric scale text */}
      {grids.map((g, i) => {
        const pt = getCoords(0, g);
        return (
          <text key={i} x={pt.x + 6} y={pt.y + 4} style={{ fontSize: 9, fill: "#A0A0A0", fontWeight: 600 }}>
            {g}%
          </text>
        );
      })}

      {/* Axis lines */}
      {domains.map((_, i) => {
        const end = getCoords(i, 100);
        return (
          <line key={i} x1={center} y1={center} x2={end.x} y2={end.y} stroke="rgba(108, 92, 231, 0.15)" strokeWidth="1" />
        );
      })}

      {/* Glowing Poly Fill */}
      <polygon points={scorePoints} fill="rgba(108, 92, 231, 0.18)" stroke="#6C5CE7" strokeWidth="2.5" strokeLinejoin="round" />

      {/* Poly Vertices */}
      {domains.map((d, i) => {
        const score = scores[d.key] || 0;
        const pt = getCoords(i, score);
        return (
          <circle key={i} cx={pt.x} cy={pt.y} r="4.5" fill="#FDCB6E" stroke="#6C5CE7" strokeWidth="1.8" />
        );
      })}

      {/* Labels */}
      {domains.map((d, i) => {
        const labelCoords = getCoords(i, 126);
        let textAnchor = "middle";
        if (labelCoords.x < center - 15) textAnchor = "end";
        if (labelCoords.x > center + 15) textAnchor = "start";

        return (
          <text
            key={d.key}
            x={labelCoords.x}
            y={labelCoords.y + 4}
            textAnchor={textAnchor}
            style={{ fontSize: 10, fontWeight: 700, fill: "#2D3436", fontFamily: "'Inter', sans-serif" }}
          >
            {d.label}
          </text>
        );
      })}
    </svg>
  );
}

function GrowthChart({ history }) {
  if (history.length <= 1) {
    return (
      <div style={{ textAlign: "center", padding: "30px 15px", background: "#fdfdff", borderRadius: 14, border: "2px dashed rgba(108, 92, 231, 0.15)", color: "#777" }}>
        📊 <strong style={{ color: "var(--blue)" }}>Longitudinal Growth Tracking</strong>
        <p style={{ fontSize: 13.5, marginTop: 8, margin: 0, lineHeight: 1.5 }}>
          This is the student's first completed assessment. Future assessments will plot growth trends, domain progress, and workshop attendance histories over time here!
        </p>
      </div>
    );
  }

  const width = 480;
  const height = 180;
  const padding = 40;

  const points = history.map((s, idx) => {
    const scores = JSON.parse(s.integrated_score || "{}");
    const topVal = Object.values(scores).length > 0 ? Math.max(...Object.values(scores)) : 50;
    const x = padding + (idx * (width - 2 * padding)) / (history.length - 1);
    const y = height - padding - ((topVal - 30) * (height - 2 * padding)) / 70;
    return { x, y, score: topVal, date: new Date(s.completed_at || s.created_at).toLocaleDateString() };
  });

  const pathData = points.map((p, i) => `${i === 0 ? "M" : "L"} ${p.x} ${p.y}`).join(" ");

  return (
    <div>
      <svg width="100%" viewBox={`0 0 ${width} ${height}`} style={{ background: "#F8F9FA", border: "1px solid rgba(108, 92, 231, 0.12)", borderRadius: "14px", padding: "10px 0", marginBottom: 20 }}>
        {/* Glow fill */}
        <path
          d={`${pathData} L ${points[points.length-1].x} ${height - padding} L ${points[0].x} ${height - padding} Z`}
          fill="rgba(108, 92, 231, 0.08)"
        />
        {/* Stroke Line */}
        <path d={pathData} fill="none" stroke="#6C5CE7" strokeWidth="3.5" strokeLinecap="round" />

        {/* Vertices & Labels */}
        {points.map((p, i) => (
          <g key={i}>
            <circle cx={p.x} cy={p.y} r="6" fill="#FDCB6E" stroke="#6C5CE7" strokeWidth="2.5" />
            <text x={p.x} y={p.y - 14} textAnchor="middle" style={{ fontSize: 12, fontWeight: 800, fill: "#6C5CE7" }}>
              {p.score}%
            </text>
            <text x={p.x} y={height - 10} textAnchor="middle" style={{ fontSize: 10, fill: "#57606F", fontWeight: 700 }}>
              Quest {i + 1}
            </text>
          </g>
        ))}
      </svg>
      
      <div style={{ overflowX: "auto" }}>
        <table className="table" style={{ width: "100%", fontSize: "13.5px", borderCollapse: "collapse", textAlign: "left" }}>
          <thead>
            <tr style={{ borderBottom: "2px solid #E6F1FB", color: "#57606F" }}>
              <th style={{ padding: "10px 5px" }}>Assessment</th>
              <th>Date</th>
              <th>Primary Aptitude</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {history.map((s, idx) => {
              const scores = JSON.parse(s.integrated_score || "{}");
              const topVal = Object.values(scores).length > 0 ? Math.max(...Object.values(scores)) : 50;
              return (
                <tr key={s.id} style={{ borderBottom: "1px solid #F1EFE8" }}>
                  <td style={{ padding: "12px 5px" }}><strong>Assessment {idx + 1}</strong></td>
                  <td>{new Date(s.completed_at || s.created_at).toLocaleDateString()}</td>
                  <td style={{ color: "#6C5CE7", fontWeight: 800 }}>{topVal}%</td>
                  <td>
                    <span className="domain-badge" style={{ background: "#E1F5EE", color: "#0F6E56", fontSize: 11, padding: "2px 8px" }}>
                      ✓ Validated
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function TQGauge({ score, color }) {
  const radius = 50;
  const stroke = 8;
  const normalizedRadius = radius - stroke * 2;
  const circumference = normalizedRadius * 2 * Math.PI;
  const strokeDashoffset = circumference - (score / 100) * circumference;
  return (
    <div style={{ position: "relative", width: 120, height: 120, display: "flex", alignItems: "center", justifyContent: "center" }}>
      <svg height={120} width={120}>
        <circle stroke="rgba(108, 92, 231, 0.08)" fill="transparent" strokeWidth={stroke} r={normalizedRadius} cx={60} cy={60} />
        <circle
          stroke={color || "#6C5CE7"}
          fill="transparent"
          strokeWidth={stroke}
          strokeDasharray={circumference + ' ' + circumference}
          style={{ strokeDashoffset, transition: "stroke-dashoffset 1s ease-in-out", transform: "rotate(-90deg)", transformOrigin: "50% 50%" }}
          r={normalizedRadius}
          cx={60}
          cy={60}
          strokeLinecap="round"
        />
      </svg>
      <div style={{ position: "absolute", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
        <span style={{ fontSize: "22px", fontWeight: 800, color: "var(--text)" }}>{score}%</span>
        <span style={{ fontSize: "9px", fontWeight: 700, color: "var(--text-light)", textTransform: "uppercase", letterSpacing: "0.5px" }}>TQ Score</span>
      </div>
    </div>
  );
}

export default function Results() {
  const { sid } = useParams();
  const [params] = useSearchParams();
  const cid = params.get("cid");
  const navigate = useNavigate();

  const [session, setSession] = useState(null);
  const [child, setChild]     = useState(null);
  const [history, setHistory] = useState([]);
  const [notes, setNotes]     = useState([]);
  const [loading, setLoading] = useState(true);

  // Facilitator Form Review State
  const [facForm, setFacForm] = useState({
    confirmed: 1,
    override_domain: "",
    strengths_observed: "",
    concerns: "",
    suggested_workshop: "Art & Design Workshop",
    notes: "",
    obs_creativity: 3,
    obs_communication: 3,
    obs_leadership: 3,
    obs_focus: 3,
    evidence_notes: "",
    obs_curiosity: 3,
    validation_status: "Validated"
  });

  const handleDownloadPDF = () => {
    const originalTitle = document.title;
    const safeName = (child?.name || "Student").trim().replace(/\s+/g, "_");
    document.title = `${safeName}_TINS_Talent_Discovery_Report`;
    window.print();
    setTimeout(() => {
      document.title = originalTitle;
    }, 1000);
  };

  const loadData = async () => {
    try {
      const [s, c] = await Promise.all([api.getSession(sid), api.getChild(cid)]);
      setSession(s);
      setChild(c);

      // Load past sessions for longitudinal growth
      if (cid) {
        const sessions = await api.childSessions(cid);
        const completed = sessions.filter(x => x.status === "complete" || x.phase === "complete");
        completed.sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
        setHistory(completed);
      }

      // Load facilitator reviews
      const fn = await api.getNotes(sid);
      setNotes(fn);
    } catch (e) {
      console.error("Error loading Results dashboard:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [sid, cid]);

  const submitFacReview = async (e) => {
    e.preventDefault();
    try {
      await api.addNote({
        session_id: parseInt(sid),
        child_id: parseInt(cid),
        confirmed: facForm.confirmed,
        override_domain: facForm.confirmed ? "" : facForm.override_domain,
        observation: facForm.confirmed ? "Agree" : "Disagree",
        notes: facForm.notes,
        agreement: facForm.confirmed ? "Agree" : "Disagree",
        strengths_observed: facForm.strengths_observed,
        concerns: facForm.concerns,
        suggested_workshop: facForm.suggested_workshop,
        obs_creativity: facForm.obs_creativity,
        obs_communication: facForm.obs_communication,
        obs_leadership: facForm.obs_leadership,
        obs_focus: facForm.obs_focus,
        evidence_notes: facForm.evidence_notes,
        obs_curiosity: facForm.obs_curiosity,
        validation_status: facForm.confirmed ? "Validated" : "Needs Further Observation"
      });
      alert("Facilitator Review permanently logged. Re-evaluating scores!");
      await loadData();
      window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (err) {
      alert("Failed to submit facilitator review.");
    }
  };

  if (loading) return <div style={{ textAlign:"center", marginTop:80, color:"#777" }}>Loading talent map...</div>;
  if (!session) return <div style={{ textAlign:"center", marginTop:80, color:"#777" }}>Session not found.</div>;

  const integ = JSON.parse(session.integrated_score || "{}");
  const analysis = JSON.parse(session.personality_data || "{}");
  const metrics = analysis.metrics || {};
  const evidence = analysis.evidence || {};
  
  const sorted = Object.entries(integ).sort((a, b) => b[1] - a[1]);
  const primaryDomain = analysis.primary_domain || sorted[0]?.[0] || "creative";
  const primaryLabel = DOMAINS[primaryDomain]?.label || primaryDomain;
  const secondaryDomains = analysis.secondary_domains || sorted.slice(1, 3).map(([d]) => d) || [];
  const emergingDomains = analysis.emerging_domains || sorted.slice(3, 6).map(([d]) => d) || [];
  const untapped_potential = analysis.untapped_potential || [];

  const PERSONAS = {
    creative: {
      title: "THE CREATOR",
      emoji: "🎨",
      desc: "This child enjoys generating original ideas, imagining possibilities, and expressing thoughts through visual and artistic mediums.",
      strengths: ["Vivid Imagination", "Divergent Thinking", "Original Expression"],
      growth: ["Structured Completion", "Attention to Rote Rules"]
    },
    spatial: {
      title: "THE BUILDER",
      emoji: "🔧",
      desc: "This child thinks in three dimensions, loves constructing physical or mental models, and naturally understands design structures.",
      strengths: ["3D Visualization", "Structural Logic", "Spatial Transformation"],
      growth: ["Verbalizing Concepts", "Patience with Abstract Theory"]
    },
    logical: {
      title: "THE THINKER",
      emoji: "🧠",
      desc: "This child is highly analytical, naturally notices logical patterns, loves solving puzzles, and thrives on structured reasoning.",
      strengths: ["Pattern Recognition", "Reasoning & Logic", "Systematic Problem-Solving"],
      growth: ["Handling Vague Goals", "Accepting Open-Ended Ambiguity"]
    },
    social: {
      title: "THE LEADER",
      emoji: "🤝",
      desc: "This child possesses natural social intelligence, easily connects with others, coordinates collaborative activities, and guides groups.",
      strengths: ["Empathy & Influence", "Group Organization", "Collaborative Coordination"],
      growth: ["Delegating Tasks", "Sustaining Quiet Focus"]
    },
    language: {
      title: "THE COMMUNICATOR",
      emoji: "💬",
      desc: "This child has a natural affinity for words, excels in verbal storytelling, expresses ideas with high clarity, and loves debate.",
      strengths: ["Verbal Fluency", "Narrative Structure", "Persuasive Explanation"],
      growth: ["Listening Without Interrupting", "Silent Individual Practice"]
    },
    naturalist: {
      title: "THE OBSERVER",
      emoji: "🌱",
      desc: "This child has unusual detail-awareness in nature, notices micro-patterns in ecosystems, and loves classifying biological details.",
      strengths: ["Sensory Observation", "Taxonomic Classification", "Environmental Empathy"],
      growth: ["Abstract Symbolic Tasks", "Prolonged Desk-Bound Study"]
    },
    kinesthetic: {
      title: "THE EXPLORER",
      emoji: "🏃",
      desc: "This child learns best through physical doing, movement, and hands-on trial-and-error, demonstrating great fine-motor control.",
      strengths: ["Fine-Motor Precision", "Coordination & Agility", "Kinesthetic Intuition"],
      growth: ["Passive Auditory Learning", "Prolonged Sitting Work"]
    },
    intrapersonal: {
      title: "THE RESEARCHER",
      emoji: "🧘",
      desc: "This child exhibits deep self-awareness, prefers reflecting in quiet spaces, understands personal motivations, and sets thoughtful goals.",
      strengths: ["Emotional Reflexivity", "Independent Planning", "Goal-Oriented Perseverance"],
      growth: ["Highly Competitive Groups", "Spontaneous Public Speaking"]
    }
  };

  const getInterpretation = (score) => {
    if (score >= 75) return { label: "Strong Indicators", color: "#5B4CF0", desc: "Demonstrates consistent, highly accurate pattern execution and rapid responses." };
    if (score >= 50) return { label: "Emerging Indicators", color: "#00B8A9", desc: "Suggests solid foundational capability; demonstrates intuitive comfort but requires further practice." };
    return { label: "Needs Further Exploration", color: "#8E9BAE", desc: "Represents an area with limited spontaneous indicators; would benefit from introductory exposure." };
  };

  const parentGuides = {
    creative: {
      behaviors: ["Imagines highly unusual possibilities", "Enjoys open-ended tasks and abstract games", "Prefers visual creation over pure memorization"],
      motivators: ["Original expression, visual challenges, autonomy in choices"],
      styles: "Divergent and visual-first",
      activities: "Painting, storytelling, open-ended crafts, tinkering labs",
      challenges: "Can easily become bored by highly repetitive or rigid work",
      support: ["Provide diverse physical and digital design materials", "Allow space for experimentation without immediate grading"]
    },
    spatial: {
      behaviors: ["Likes physical construction and model-building", "Enjoys visualizing shapes and three-dimensional blocks", "Notices minute structural details in drawings"],
      motivators: ["Building, assembling, transforming structures, design tasks"],
      styles: "Three-dimensional and hands-on",
      activities: "Lego building, robotics, paper folding, architectural sketches",
      challenges: "May sometimes struggle to explain spatial concepts in written text",
      support: ["Encourage model building and tinkering workshops", "Use visual diagrams and physical models for academic study"]
    },
    logical: {
      behaviors: ["Enjoys solving complex riddles and puzzles", "Notices mathematical patterns spontaneously", "Structures thoughts sequentially and logically"],
      motivators: ["Systematic patterns, numerical puzzles, clear cause-and-effect rules"],
      styles: "Analytical, sequence-based",
      activities: "Chess, math puzzles, introductory coding, logic games",
      challenges: "May get frustrated by vague directions or emotional debates",
      support: ["Provide math puzzles and logic-based board games", "Structure daily tasks with clear sequences and logical rules"]
    },
    social: {
      behaviors: ["Naturally organizes peers and group activities", "Shows high empathy and notices others' emotions", "Takes active initiative in coordinating events"],
      motivators: ["Collaborative projects, peer coordination, group problem-solving"],
      styles: "Interpersonal, leadership-driven",
      activities: "Group volunteering, team games, peer mentoring, school clubs",
      challenges: "May dominate discussions or take on too much responsibility",
      support: ["Provide leadership opportunities with guidance on delegation", "Encourage group games that require active listening and compromise"]
    },
    language: {
      behaviors: ["Expresses thoughts with high verbal clarity", "Enjoys telling stories and describing scenarios", "Has an extensive vocabulary and notices wordplay"],
      motivators: ["Debate, verbal explanation, storytelling, theater performance"],
      styles: "Verbal-auditory, narrative-driven",
      activities: "Debate, public speaking, theater club, writing, reading",
      challenges: "May talk excessively or struggle with silent, individual tasks",
      support: ["Encourage storytelling, theater, or writing workshops", "Discuss complex topics together to challenge verbal expression"]
    },
    naturalist: {
      behaviors: ["Notices details in plants, animals, and ecosystems", "Loves sorting, classifying, and organizing collections", "Shows deep empathy and interest in the natural world"],
      motivators: ["Outdoor observations, wildlife exploration, environmental projects"],
      styles: "Environmental-observational",
      activities: "Nature trails, birdwatching, environmental care, gardening",
      challenges: "May get restless in closed, sedentary indoor spaces",
      support: ["Provide opportunities for regular nature exploration", "Use outdoor settings and animal themes for academic concepts"]
    },
    kinesthetic: {
      behaviors: ["Demonstrates exceptional coordination and motor speed", "Learns concepts best by physically doing or moving", "Has strong fine-motor skills and tactile intuition"],
      motivators: ["Physical movement, sports, hands-on construction, active games"],
      styles: "Tactile-physical, experimental",
      activities: "Sports camp, dance, physical obstacles, model tinkering",
      challenges: "Needs regular physical breaks; may fidget in quiet lectures",
      support: ["Integrate physical movement and breaks into study routines", "Encourage sports, dance, or hands-on crafting workshops"]
    },
    intrapersonal: {
      behaviors: ["Shows deep reflection and self-awareness of feelings", "Sets thoughtful personal goals and plans ahead", "Thrives when working independently on projects"],
      motivators: ["Solo hobbies, personal reflection, self-directed goals"],
      styles: "Reflective, self-guided",
      activities: "Journaling, solo hobbies, mindfulness, goal-setting",
      challenges: "May withdraw during highly competitive or chaotic group work",
      support: ["Provide quiet spaces for reflection and independent projects", "Encourage journaling or writing to process thoughts and emotions"]
    }
  };
  const childPersona = PERSONAS[primaryDomain] || PERSONAS.creative;
  const guide = parentGuides[primaryDomain] || parentGuides.creative;

  const safeName = (child?.name || "Student").trim().replace(/\s+/g, "_");
  const personalizedSnapshot = `${child?.name || "The student"} appears to demonstrate strong developmental indicators in ${primaryLabel} activities, particularly in open-ended exploration and problem-solving styles. These findings suggest a natural comfort with ${primaryLabel} concepts. Secondary indicators also suggest potential in ${secondaryDomains.map(d => DOMAINS[d]?.label || d).join(" and ")} areas. Nurturing these talents in structured settings will provide a clearer picture of their long-term growth.`;
  const pdfUrl = `${api.downloadPDF(sid)}?token=${localStorage.getItem("goat_token")}&cid=${cid}`;

  return (
    <div style={{ maxWidth: 1040, margin: "0 auto", padding: "20px 10px" }}>
      
      {/* ── SCREEN VIEW: MODERN WEB DASHBOARD (Hidden during print) ── */}
      <div className="hide-print">
        {/* Dashboard Control Panel */}
        <div className="card" style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: 16,
          background: "linear-gradient(135deg, #FFFFFF 0%, #F9FAFB 100%)",
          border: "1px solid rgba(91, 76, 240, 0.15)",
          borderRadius: 16,
          padding: "20px 24px",
          marginBottom: 24,
          boxShadow: "0 10px 25px rgba(91, 76, 240, 0.04)"
        }}>
          <div>
            <span style={{ fontSize: "11px", fontWeight: 800, color: "#5B4CF0", textTransform: "uppercase", letterSpacing: "1px", display: "block", marginBottom: "4px" }}>Active Talent Map</span>
            <h1 style={{ margin: 0, fontSize: "24px", fontWeight: 900, color: "var(--text)" }}>TINS Core Cognitive Dashboard</h1>
            <p style={{ margin: "2px 0 0 0", fontSize: "14px", color: "var(--text-light)" }}>
              Detailed profile analysis, roadmap, and validations for <strong>{child?.name}</strong> (Age {child?.age})
            </p>
          </div>
          <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
            <a
              className="btn"
              href={pdfUrl}
              target="_blank"
              rel="noopener noreferrer"
              style={{ background: "#20BF6B", color: "#fff", display: "flex", alignItems: "center", gap: 8, fontWeight: 800, padding: "10px 22px", borderRadius: 10, textDecoration: "none", boxShadow: "0 4px 12px rgba(32, 191, 107, 0.2)" }}
            >
              📥 Download Premium PDF
            </a>
            <button
              className="btn btn-ghost"
              onClick={() => navigate("/")}
              style={{ fontWeight: 700, padding: "10px 20px", borderRadius: 10 }}
            >
              Start New Quest
            </button>
          </div>
        </div>

        {/* Hero Section: Persona & TQ Score */}
        <div className="card" style={{
          display: "grid",
          gridTemplateColumns: "1.6fr 1fr",
          gap: 24,
          background: "linear-gradient(135deg, rgba(91, 76, 240, 0.05) 0%, rgba(0, 184, 169, 0.05) 100%)",
          border: "1px solid rgba(91, 76, 240, 0.12)",
          borderRadius: 20,
          padding: "32px",
          marginBottom: 24,
          alignItems: "center"
        }}>
          <div style={{ display: "flex", gap: 20, alignItems: "start", flexWrap: "wrap" }}>
            <span style={{ fontSize: "64px", lineHeight: 1, filter: "drop-shadow(0 8px 16px rgba(0,0,0,0.1))" }}>{childPersona.emoji}</span>
            <div style={{ flex: 1, minWidth: 280 }}>
              <div style={{ display: "inline-flex", padding: "4px 10px", borderRadius: 99, background: "#5B4CF0", color: "#fff", fontSize: 11, fontWeight: 800, textTransform: "uppercase", letterSpacing: 0.8, marginBottom: 8 }}>
                Primary Persona
              </div>
              <h2 style={{ fontSize: "28px", fontWeight: 900, color: "#3C2EB9", margin: "0 0 8px 0" }}>{childPersona.title}</h2>
              <p style={{ fontSize: "15px", lineHeight: "1.6", color: "var(--text-mid)", marginBottom: 16 }}>{childPersona.desc}</p>
              
              <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
                {childPersona.strengths.map(s => (
                  <span key={s} style={{ fontSize: "12px", fontWeight: 700, color: "#0F6E56", background: "#E1F5EE", padding: "4px 10px", borderRadius: 6 }}>
                    ✓ {s}
                  </span>
                ))}
              </div>
            </div>
          </div>
          
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", borderLeft: "1px solid rgba(91, 76, 240, 0.15)", paddingLeft: 24 }}>
            <TQGauge score={integ[primaryDomain] || 50} color={DOMAINS[primaryDomain]?.color} />
            <div style={{ textAlign: "center", marginTop: 12 }}>
              <span style={{ fontWeight: 800, color: "var(--text)", display: "block" }}>{primaryLabel} Aptitude</span>
              <span style={{ fontSize: "12px", color: "var(--text-light)" }}>Outstanding developmental indicators</span>
            </div>
          </div>
        </div>

        {/* Main Grid: Radar Chart & Domain Scores vs Guides & Potential */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24, marginBottom: 24 }} className="summary-grid">
          {/* Left Column: Aptitude Chart & Scores */}
          <div className="card" style={{ padding: 24 }}>
            <h3 style={{ fontSize: "18px", fontWeight: 800, color: "var(--text)", marginBottom: 20 }}>Cognitive Talent Mapping</h3>
            <div style={{ width: "100%", height: "240px", display: "flex", alignItems: "center", justifyContent: "center", marginBottom: 20 }}>
              <RadarChart scores={integ} />
            </div>
            
            <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
              {sorted.map(([domain, score]) => {
                const d = DOMAINS[domain];
                const interp = getInterpretation(score);
                return (
                  <div key={domain} style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                    <div style={{ display: "flex", justifyContent: "space-between", fontSize: "13.5px" }}>
                      <span style={{ fontWeight: 700, color: "var(--text)" }}>{d?.emoji} {d?.label}</span>
                      <span style={{ fontWeight: 800, color: d?.color }}>{score}% ({interp.label})</span>
                    </div>
                    <div style={{ height: 8, background: "rgba(0,0,0,0.04)", borderRadius: 99, overflow: "hidden" }}>
                      <div style={{ width: `${score}%`, height: "100%", background: d?.color || "var(--blue)", borderRadius: 99 }} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Right Column: Guides, Recommendations & Opportunities */}
          <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
            {/* Guide & Activities */}
            <div className="card" style={{ padding: 24 }}>
              <h3 style={{ fontSize: "18px", fontWeight: 800, color: "var(--text)", marginBottom: 16 }}>Parent Nurturing Playbook</h3>
              <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
                <div style={{ background: "rgba(0, 184, 169, 0.04)", borderLeft: "4px solid var(--teal)", padding: 14, borderRadius: "0 8px 8px 0" }}>
                  <span style={{ fontWeight: 800, color: "var(--teal)", display: "block", marginBottom: 4, fontSize: 13.5 }}>🛠️ Recommended At-Home Activities</span>
                  <ul style={{ paddingLeft: 16, margin: 0, fontSize: "13px", lineHeight: 1.5, color: "var(--text-mid)", fontWeight: 600 }}>
                    {guide.support.map(s => <li key={s}>{s}</li>)}
                  </ul>
                </div>
                
                <div style={{ background: "rgba(91, 76, 240, 0.04)", borderLeft: "4px solid var(--blue)", padding: 14, borderRadius: "0 8px 8px 0" }}>
                  <span style={{ fontWeight: 800, color: "var(--blue)", display: "block", marginBottom: 4, fontSize: 13.5 }}>🎯 Key Motivators</span>
                  <p style={{ margin: 0, fontSize: "13px", color: "var(--text-mid)" }}>
                    Highly responsive to <strong>{guide.activities}</strong>. Best engaged via {guide.motivators}.
                  </p>
                </div>
              </div>
            </div>

            {/* Hidden Opportunities (Untapped Potential) */}
            <div className="card" style={{ padding: 24, border: untapped_potential.length > 0 ? "1.5px dashed #F7B731" : "1px solid var(--border)", background: untapped_potential.length > 0 ? "rgba(247, 183, 49, 0.02)" : "#fff" }}>
              <h3 style={{ fontSize: "18px", fontWeight: 800, color: "var(--text)", marginBottom: 12 }}>Untapped Opportunities</h3>
              
              {untapped_potential.length > 0 ? (
                <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                  {untapped_potential.map(u => (
                    <div key={u} style={{ background: "rgba(247, 183, 49, 0.06)", border: "1px solid rgba(247, 183, 49, 0.2)", padding: 12, borderRadius: 10 }}>
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
                        <span style={{ fontWeight: 800, fontSize: "14px", color: "#B7791F" }}>🔥 High Potential in {DOMAINS[u]?.label}</span>
                        <span style={{ background: "#F7B731", color: "#fff", fontSize: "10px", fontWeight: 800, padding: "2px 6px", borderRadius: 4 }}>Low Exposure</span>
                      </div>
                      <p style={{ fontSize: "12.5px", lineHeight: "1.5", color: "var(--text-mid)", margin: 0 }}>
                        {child?.name} scored <strong>{integ[u]}%</strong> in {DOMAINS[u]?.label} challenges but has very limited exposure history. Providing basic workshops or toys in this area is highly recommended.
                      </p>
                    </div>
                  ))}
                </div>
              ) : (
                <div style={{ padding: "16px", background: "rgba(0, 184, 169, 0.03)", border: "1px dashed rgba(0, 184, 169, 0.2)", borderRadius: "10px", textAlign: "center", fontSize: "13.5px", color: "var(--teal)", fontWeight: 700 }}>
                  🌿 All cognitive potentials align well with prior exposures. No significant hidden talents were left undeveloped!
                </div>
              )}
            </div>
          </div>
        </div>

        {/* 30-Day Developmental Plan Timeline */}
        <div className="card" style={{ padding: 24, marginBottom: 24 }}>
          <h3 style={{ fontSize: "18px", fontWeight: 800, color: "var(--text)", marginBottom: 6 }}>30-Day Developmental Roadmap</h3>
          <p style={{ fontSize: "13.5px", color: "var(--text-light)", marginBottom: 20 }}>Personalized, week-by-week cognitive action plan recommended by Project WHY</p>
          
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 16 }}>
            {[
              { week: "Week 1", desc: analysis.action_plan?.week_1 || "Introductory workshops in primary domain", icon: "🌱" },
              { week: "Week 2", desc: analysis.action_plan?.week_2 || "Collaborative projects and group exercises", icon: "🌿" },
              { week: "Week 3", desc: analysis.action_plan?.week_3 || "Advanced challenge-based tasks", icon: "🌲" },
              { week: "Week 4", desc: analysis.action_plan?.week_4 || "Mentorship check-in and showcase", icon: "🌳" }
            ].map(item => (
              <div key={item.week} style={{ background: "var(--surface-soft)", border: "1px solid var(--border)", padding: 16, borderRadius: 12, display: "flex", gap: 12, flexDirection: "column" }}>
                <span style={{ fontSize: 24, height: 40, width: 40, borderRadius: 8, background: "rgba(108, 92, 231, 0.08)", display: "flex", alignItems: "center", justifyContent: "center" }}>{item.icon}</span>
                <div>
                  <span style={{ fontWeight: 800, color: "#5B4CF0", fontSize: 12, textTransform: "uppercase" }}>{item.week}</span>
                  <p style={{ margin: "4px 0 0 0", fontSize: 13, lineHeight: 1.4, color: "var(--text-mid)", fontWeight: 500 }}>{item.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Growth Journey timeline and validations */}
        <div style={{ display: "grid", gridTemplateColumns: "1.2fr 1fr", gap: 24, marginBottom: 24 }} className="summary-grid">
          {/* History Chart */}
          <div className="card" style={{ padding: 24 }}>
            <h3 style={{ fontSize: "18px", fontWeight: 800, color: "var(--text)", marginBottom: 16 }}>Longitudinal Journey Tracker</h3>
            <GrowthChart history={history} />
          </div>

          {/* Validation Review summary */}
          <div className="card" style={{ padding: 24, display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
            <div>
              <h3 style={{ fontSize: "18px", fontWeight: 800, color: "var(--text)", marginBottom: 6 }}>Mentor Validation Status</h3>
              <p style={{ fontSize: "13.5px", color: "var(--text-light)", marginBottom: 16 }}>Observations logged by facilitators during hands-on classes</p>
              
              {notes.length > 0 ? (
                <div style={{ background: "rgba(91, 76, 240, 0.03)", border: "1px solid rgba(91, 76, 240, 0.1)", borderRadius: 12, padding: 16 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "1px solid rgba(0,0,0,0.06)", paddingBottom: 10, marginBottom: 12 }}>
                    <span style={{ fontWeight: 700 }}>Reviewer: {notes[0].facilitator}</span>
                    <span style={{ background: "#E1F5EE", color: "#0F6E56", fontWeight: 800, fontSize: 11, padding: "2px 8px", borderRadius: 4 }}>
                      ✓ Validated
                    </span>
                  </div>
                  <p style={{ margin: "0 0 8px 0", fontSize: "13px" }}><strong>Observed Strengths:</strong> {notes[0].strengths_observed || "Excellent spatial organization and teamwork."}</p>
                  <p style={{ margin: "0 0 8px 0", fontSize: "13px" }}><strong>Observed Challenges:</strong> {notes[0].concerns || "None flagged."}</p>
                  <p style={{ margin: 0, fontSize: "13px" }}><strong>Notes:</strong> {notes[0].notes || notes[0].evidence_notes}</p>
                </div>
              ) : (
                <div style={{ padding: "24px 16px", background: "#FFFBF2", border: "1px dashed #E2B25B", borderRadius: 12, color: "#5D4037", textAlign: "center", fontWeight: 600, fontSize: 13.5 }}>
                  💡 Facilitator review pending validation. Mentor observations can be logged below using the screen form.
                </div>
              )}
            </div>

            <button
              className="btn btn-teal btn-lg btn-full"
              style={{ marginTop: 20 }}
              onClick={() => navigate(`/mentor/${cid}?domain=${primaryDomain}&sid=${sid}`)}
            >
              🤝 Find domain-expert mentors in {primaryLabel}
            </button>
          </div>
        </div>

      </div>

      {/* ── PRINT VIEW: 12-PAGE BOOKLET ── */}
      <div className="report-container">
        
        {/* PAGE 1: COVER PAGE */}
        <div id="print-page-1" className="report-page cover-page">
          <div className="cover-header">
            <span style={{ fontWeight: 900, fontSize: "16px", letterSpacing: "1px" }}>PROJECT WHY</span>
            <span style={{ fontWeight: 900, fontSize: "16px", letterSpacing: "1px" }}>TINS V4</span>
          </div>
          <div className="cover-hero">
            🧠 ✨ 🚀
          </div>
          <div className="cover-title-group">
            <h1>TINS Talent Discovery &amp; Development Report</h1>
            <p>Understanding Potential. Building Futures.</p>
          </div>
          <div className="cover-footer">
            <div>
              <strong>Student Name:</strong> {child?.name}<br />
              <strong>Age:</strong> {child?.age} Years &middot; <strong>Class:</strong> {child?.school_year || "Not Specified"}<br />
              <strong>Language:</strong> {child?.language}
            </div>
            <div style={{ textAlign: "right" }}>
              <strong>Assessment Date:</strong> {new Date(session.completed_at || session.created_at).toLocaleDateString()}<br />
              <strong>Assessment ID:</strong> TINS-S{session.id}<br />
              <strong>Facilitator:</strong> {notes[0]?.facilitator || "Project WHY Mentor"}
            </div>
          </div>
        </div>

        {/* PAGE 2: EXECUTIVE SUMMARY (WHO IS THIS CHILD?) */}
        <div className="report-page">
          <div>
            <div className="report-page-header">
              <span className="logo-group">🧠 TINS</span>
              <span className="report-section-name">Executive Summary</span>
            </div>
            <h2 style={{ fontSize: "22px", fontWeight: 800, color: "#5B4CF0", margin: "0 0 16px 0" }}>WHO IS THIS CHILD?</h2>
            <p style={{ fontSize: "15px", lineHeight: "1.7", color: "#4A4A4A", fontWeight: 500, margin: "0 0 24px 0", fontStyle: "italic" }}>
              "{personalizedSnapshot}"
            </p>
            
            <div style={{ marginTop: "24px" }}>
              <h3 style={{ fontSize: "13px", fontWeight: 800, color: "#4A4A4A", textTransform: "uppercase", margin: "0 0 12px 0", letterSpacing: "0.5px" }}>Talent Domain Summary</h3>
              <div className="summary-card-v4 primary">
                <div style={{ fontWeight: 800, color: "#5B4CF0", fontSize: "12px", textTransform: "uppercase" }}>Strong Indicators</div>
                <h4 style={{ margin: "2px 0 0 0", fontSize: "16px", fontWeight: 800 }}>{DOMAINS[primaryDomain]?.emoji} {DOMAINS[primaryDomain]?.label}</h4>
              </div>
              <div className="summary-card-v4 secondary">
                <div style={{ fontWeight: 800, color: "#00B8A9", fontSize: "12px", textTransform: "uppercase" }}>Emerging Indicators</div>
                <h4 style={{ margin: "2px 0 0 0", fontSize: "15px", fontWeight: 800 }}>
                  {secondaryDomains.map(d => `${DOMAINS[d]?.emoji || "✨"} ${DOMAINS[d]?.label || d}`).join("  |  ")}
                </h4>
              </div>
              <div className="summary-card-v4 emerging">
                <div style={{ fontWeight: 800, color: "#F7B731", fontSize: "12px", textTransform: "uppercase" }}>Needs Further Exploration</div>
                <h4 style={{ margin: "2px 0 0 0", fontSize: "15px", fontWeight: 800 }}>
                  {emergingDomains.map(d => `${DOMAINS[d]?.emoji || "✨"} ${DOMAINS[d]?.label || d}`).join("  |  ")}
                </h4>
              </div>
            </div>
          </div>
          <div className="report-page-footer">
            <span>TINS Discovery &amp; Nurturing Report</span>
            <span>Page 2</span>
          </div>
        </div>

        {/* PAGE 3: TALENT MAP */}
        <div className="report-page">
          <div>
            <div className="report-page-header">
              <span className="logo-group">🧠 TINS</span>
              <span className="report-section-name">Psychological Talent Map</span>
            </div>
            <h2 style={{ fontSize: "20px", fontWeight: 800, color: "#5B4CF0", margin: "0 0 16px 0", textAlign: "center" }}>DYNAMIC COGNITIVE MAP</h2>
            
            <div style={{ width: "100%", height: "220px", display: "flex", alignItems: "center", justifyContent: "center", margin: "10px 0" }}>
              <RadarChart scores={integ} />
            </div>

            <div style={{ marginTop: "16px", overflowX: "auto" }}>
              <table style={{ width: "100%", fontSize: "12px", borderCollapse: "collapse", border: "1px solid rgba(0, 0, 0, 0.05)" }}>
                <thead>
                  <tr style={{ background: "rgba(91, 76, 240, 0.05)", borderBottom: "1.5px solid rgba(91, 76, 240, 0.15)", color: "#5B4CF0", fontWeight: 800, textAlign: "left" }}>
                    <th style={{ padding: "8px 10px" }}>Domain</th>
                    <th style={{ padding: "8px 10px" }}>Strength Level</th>
                    <th style={{ padding: "8px 10px" }}>Developmental Meaning</th>
                  </tr>
                </thead>
                <tbody>
                  {sorted.slice(0, 5).map(([domain, score]) => {
                    const d = DOMAINS[domain];
                    const interp = getInterpretation(score);
                    return (
                      <tr key={domain} style={{ borderBottom: "1px solid rgba(0, 0, 0, 0.04)" }}>
                        <td style={{ padding: "8px 10px", fontWeight: 800, color: "#4A4A4A" }}>{d?.emoji} {d?.label}</td>
                        <td style={{ padding: "8px 10px", fontWeight: 800, color: interp.color }}>{interp.label}</td>
                        <td style={{ padding: "8px 10px", color: "#57606F", lineHeight: 1.35 }}>{interp.desc}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
          <div className="report-page-footer">
            <span>TINS Discovery &amp; Nurturing Report</span>
            <span>Page 3</span>
          </div>
        </div>

        {/* PAGE 4: EVIDENCE BEHIND THE RESULTS */}
        <div className="report-page">
          <div>
            <div className="report-page-header">
              <span className="logo-group">🧠 TINS</span>
              <span className="report-section-name">Evidence Report</span>
            </div>
            <h2 style={{ fontSize: "20px", fontWeight: 800, color: "#5B4CF0", margin: "0 0 12px 0" }}>WHY THESE TALENTS WERE IDENTIFIED</h2>
            <p className="muted-copy" style={{ marginBottom: 16 }}>
              Spontaneous behavioral choices, preference indicators, and deep assessment puzzle accuracy are cross-referenced below.
            </p>

            <div>
              {sorted.slice(0, 2).map(([domain, score]) => {
                const d = DOMAINS[domain];
                const log = evidence[domain] || {};
                const isSufficient = log.has_preference && log.has_behavioral && log.has_performance;
                return (
                  <div key={domain} className="evidence-card-v4" style={{ borderLeft: `4px solid ${d?.color || "#5B4CF0"}` }}>
                    <h4 style={{ color: d?.color, fontWeight: 900, fontSize: "14.5px", margin: "0 0 8px 0" }}>{d?.emoji} {d?.label} Indicators</h4>
                    {isSufficient ? (
                      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "10px", fontSize: "12px" }}>
                        <div>
                          <span style={{ fontWeight: 800, color: "#4A4A4A" }}>👁️ Discovery Evidence:</span>
                          <p style={{ margin: "2px 0 0 0", color: "#57606F", lineHeight: 1.4 }}>{log.behavioral_desc}</p>
                        </div>
                        <div>
                          <span style={{ fontWeight: 800, color: "#4A4A4A" }}>🌱 Exposure Preference:</span>
                          <p style={{ margin: "2px 0 0 0", color: "#57606F", lineHeight: 1.4 }}>{log.preference_desc}</p>
                        </div>
                        <div>
                          <span style={{ fontWeight: 800, color: "#4A4A4A" }}>🎯 Performance Accuracy:</span>
                          <p style={{ margin: "2px 0 0 0", color: "#57606F", lineHeight: 1.4 }}>{log.performance_desc}</p>
                        </div>
                      </div>
                    ) : (
                      <div style={{ fontSize: "13px", fontStyle: "italic", color: "#E17055", fontWeight: 600 }}>
                        ⚠️ Additional validation required. Prior exposure or behavioral inputs were insufficient for complete mapping.
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
          <div className="report-page-footer">
            <span>TINS Discovery &amp; Nurturing Report</span>
            <span>Page 4</span>
          </div>
        </div>

        {/* PAGE 5: UNTAPPED POTENTIAL REPORT */}
        <div className="report-page">
          <div>
            <div className="report-page-header">
              <span className="logo-group">🧠 TINS</span>
              <span className="report-section-name">Hidden Opportunities</span>
            </div>
            <h2 style={{ fontSize: "20px", fontWeight: 800, color: "#5B4CF0", margin: "0 0 12px 0" }}>HIDDEN COGNITIVE OPPORTUNITIES</h2>
            
            {untapped_potential.length > 0 ? (
              <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
                {untapped_potential.map(u => (
                  <div key={u} className="summary-card-v4" style={{ border: "1px dashed #F7B731", background: "rgba(247, 183, 49, 0.05)", padding: "16px" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
                      <span style={{ fontWeight: 800, fontSize: "15px", color: "#B7791F" }}>🔥 Untapped potential in {DOMAINS[u]?.label}</span>
                      <span className="domain-badge" style={{ background: "#F7B731", color: "#fff", fontSize: "11px", fontWeight: 800 }}>High Potential + Low Exposure</span>
                    </div>
                    <p style={{ fontSize: "13px", lineHeight: "1.5", color: "#4A4A4A", margin: 0, fontWeight: 500 }}>
                      {child?.name} scored an impressive <strong>{integ[u]}%</strong> in deep assessment tasks for <strong>{DOMAINS[u]?.label}</strong> despite having very limited practice or access opportunities in the past (Exposure Level: {["Never tried it", "Tried a few times"][child[`exp_${u}`] || 0]}). Introductory exposure is highly recommended.
                    </p>
                  </div>
                ))}
              </div>
            ) : (
              <div style={{ padding: "16px", background: "rgba(0, 184, 169, 0.04)", border: "1px dashed #00B8A9", borderRadius: "12px", textAlign: "center", fontSize: "13.5px", color: "#00B8A9", fontWeight: 700 }}>
                🌿 All cognitive domains show prior exposure alignment. No major high-potential, low-exposure untapped flags were detected during this quest.
              </div>
            )}

            <div style={{ marginTop: "20px" }}>
              <h3 style={{ fontSize: "13px", fontWeight: 800, color: "#4A4A4A", textTransform: "uppercase", margin: "0 0 10px 0", letterSpacing: "0.5px" }}>Domain Potential Tiers</h3>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "10px", fontSize: "12px" }}>
                <div style={{ background: "#EEEDFE", border: "1px solid rgba(91, 76, 240, 0.15)", padding: "10px", borderRadius: "10px" }}>
                  <span style={{ fontWeight: 800, color: "#5B4CF0", display: "block", marginBottom: 6 }}>Strong Potential</span>
                  <ul style={{ paddingLeft: 14, margin: 0, color: "#4A4A4A" }}>
                    {sorted.filter(([_, s]) => s >= 75).map(([d]) => <li key={d} style={{ fontWeight: 700 }}>{DOMAINS[d]?.label}</li>)}
                  </ul>
                </div>
                <div style={{ background: "#D1F7EC", border: "1px solid rgba(0, 184, 169, 0.15)", padding: "10px", borderRadius: "10px" }}>
                  <span style={{ fontWeight: 800, color: "#00B8A9", display: "block", marginBottom: 6 }}>Emerging Potential</span>
                  <ul style={{ paddingLeft: 14, margin: 0, color: "#4A4A4A" }}>
                    {sorted.filter(([_, s]) => s >= 50 && s < 75).map(([d]) => <li key={d}>{DOMAINS[d]?.label}</li>)}
                  </ul>
                </div>
                <div style={{ background: "#FDFDFD", border: "1px solid rgba(0, 0, 0, 0.05)", padding: "10px", borderRadius: "10px" }}>
                  <span style={{ fontWeight: 800, color: "#8E9BAE", display: "block", marginBottom: 6 }}>Further Observation</span>
                  <ul style={{ paddingLeft: 14, margin: 0, color: "#57606F" }}>
                    {sorted.filter(([_, s]) => s < 50).map(([d]) => <li key={d}>{DOMAINS[d]?.label}</li>)}
                  </ul>
                </div>
              </div>
            </div>
          </div>
          <div className="report-page-footer">
            <span>TINS Discovery &amp; Nurturing Report</span>
            <span>Page 5</span>
          </div>
        </div>

        {/* PAGE 6: CHILD PROFILE (THE PERSONA) */}
        <div className="report-page">
          <div>
            <div className="report-page-header">
              <span className="logo-group">🧠 TINS</span>
              <span className="report-section-name">Child Persona Profile</span>
            </div>
            <h2 style={{ fontSize: "20px", fontWeight: 800, color: "#5B4CF0", margin: "0 0 16px 0" }}>CHILD COGNITIVE PERSONA</h2>

            <div className="persona-card-v4">
              <span style={{ fontSize: "56px", margin: "0 0 6px 0", display: "block" }}>{childPersona.emoji}</span>
              <h3 style={{ fontSize: "22px", color: "#5B4CF0", fontWeight: 900, margin: "0 0 6px 0", letterSpacing: "1px" }}>{childPersona.title}</h3>
              <p style={{ fontSize: "14px", lineHeight: "1.6", color: "#4A4A4A", fontWeight: 600, margin: 0 }}>
                {childPersona.desc}
              </p>
            </div>

            <div className="grid-2" style={{ marginTop: "20px" }}>
              <div style={{ background: "#FFFFFF", border: "1px solid rgba(91, 76, 240, 0.1)", borderRadius: "12px", padding: "14px 16px" }}>
                <h4 style={{ margin: "0 0 8px 0", color: "#5B4CF0", fontSize: "13px", textTransform: "uppercase", letterSpacing: "0.5px" }}>Primary Strengths</h4>
                <ul style={{ paddingLeft: 16, margin: 0, fontSize: "13px", lineHeight: 1.6, color: "#4A4A4A", fontWeight: 700 }}>
                  {childPersona.strengths.map(s => <li key={s}>{s}</li>)}
                </ul>
              </div>
              <div style={{ background: "#FFFFFF", border: "1px solid rgba(91, 76, 240, 0.1)", borderRadius: "12px", padding: "14px 16px" }}>
                <h4 style={{ margin: "0 0 8px 0", color: "#00B8A9", fontSize: "13px", textTransform: "uppercase", letterSpacing: "0.5px" }}>Targeted Growth Areas</h4>
                <ul style={{ paddingLeft: 16, margin: 0, fontSize: "13px", lineHeight: 1.6, color: "#4A4A4A", fontWeight: 600 }}>
                  {childPersona.growth.map(g => <li key={g}>{g}</li>)}
                </ul>
              </div>
            </div>
          </div>
          <div className="report-page-footer">
            <span>TINS Discovery &amp; Nurturing Report</span>
            <span>Page 6</span>
          </div>
        </div>

        {/* PAGE 7: PARENT GUIDE */}
        <div className="report-page">
          <div>
            <div className="report-page-header">
              <span className="logo-group">🧠 TINS</span>
              <span className="report-section-name">Parent &amp; Mentor Guide</span>
            </div>
            <h2 style={{ fontSize: "20px", fontWeight: 800, color: "#5B4CF0", margin: "0 0 16px 0" }}>UNDERSTANDING YOUR CHILD</h2>
            <p className="muted-copy" style={{ marginBottom: 16 }}>
              Actionable psychological guidelines to help support and nurture {child?.name}'s natural learning preference.
            </p>

            <div style={{ display: "flex", flexDirection: "column", gap: "10px", fontSize: "13px" }}>
              <div style={{ background: "#FFFFFF", border: "1px solid rgba(0,0,0,0.04)", padding: "10px 12px", borderRadius: "10px" }}>
                <span style={{ fontWeight: 800, color: "#5B4CF0" }}>💡 Common Behaviors &amp; Styles:</span>
                <ul style={{ paddingLeft: 16, margin: "4px 0 0 0", color: "#4A4A4A", fontWeight: 600 }}>
                  {guide.behaviors.map(b => <li key={b}>{b}</li>)}
                </ul>
              </div>
              
              <div style={{ background: "#FFFFFF", border: "1px solid rgba(0,0,0,0.04)", padding: "10px 12px", borderRadius: "10px" }}>
                <span style={{ fontWeight: 800, color: "#00B8A9" }}>🎯 Motivators &amp; Learning Preferences:</span>
                <p style={{ margin: "2px 0 0 0", color: "#57606F" }}>
                  The child learns best in a <strong>{guide.styles}</strong> format, driven primarily by {guide.motivators}.
                </p>
              </div>

              <div style={{ background: "#FFFFFF", border: "1px solid rgba(0,0,0,0.04)", padding: "10px 12px", borderRadius: "10px" }}>
                <span style={{ fontWeight: 800, color: "#F7B731" }}>⚠️ Possible Challenges &amp; Warning Signs:</span>
                <p style={{ margin: "2px 0 0 0", color: "#57606F" }}>
                  {guide.challenges}. May lose interest if forced into purely repetitive drills.
                </p>
              </div>

              <div style={{ background: "rgba(0, 184, 169, 0.04)", border: "1.5px solid #00B8A9", padding: "10px 12px", borderRadius: "10px" }}>
                <span style={{ fontWeight: 800, color: "#00B8A9" }}>🛠️ Home Nurturing Recommendations:</span>
                <ul style={{ paddingLeft: 16, margin: "4px 0 0 0", color: "#4A4A4A", fontWeight: 700 }}>
                  {guide.support.map(s => <li key={s}>{s}</li>)}
                </ul>
              </div>
            </div>
          </div>
          <div className="report-page-footer">
            <span>TINS Discovery &amp; Nurturing Report</span>
            <span>Page 7</span>
          </div>
        </div>

        {/* PAGE 8: 30-DAY DEVELOPMENT PLAN (NEXT STEPS) */}
        <div className="report-page">
          <div>
            <div className="report-page-header">
              <span className="logo-group">🧠 TINS</span>
              <span className="report-section-name">30-Day Developmental Plan</span>
            </div>
            <h2 style={{ fontSize: "20px", fontWeight: 800, color: "#5B4CF0", margin: "0 0 12px 0" }}>DEVELOPMENT ROADMAP: NEXT STEPS</h2>
            
            <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: "10px", margin: "0 0 14px 0" }}>
              {[
                { week: "Week 1", desc: analysis.action_plan?.week_1 || "Introductory workshops in primary domain", icon: "🌱" },
                { week: "Week 2", desc: analysis.action_plan?.week_2 || "Collaborative projects and group exercises", icon: "🌿" },
                { week: "Week 3", desc: analysis.action_plan?.week_3 || "Advanced challenge-based tasks", icon: "🌲" },
                { week: "Week 4", desc: analysis.action_plan?.week_4 || "Mentorship check-in and showcase", icon: "🌳" }
              ].map(item => (
                <div key={item.week} style={{ background: "#FFFFFF", border: "1px solid rgba(0,0,0,0.04)", padding: "10px 12px", borderRadius: "10px", display: "flex", gap: 8 }}>
                  <span style={{ fontSize: "18px" }}>{item.icon}</span>
                  <div>
                    <span style={{ fontWeight: 800, color: "#5B4CF0", fontSize: "11px", textTransform: "uppercase" }}>{item.week}</span>
                    <p style={{ margin: "2px 0 0 0", fontSize: "12px", lineHeight: "1.4", color: "#57606F" }}>{item.desc}</p>
                  </div>
                </div>
              ))}
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: "10px", fontSize: "12px" }}>
              <div style={{ background: "rgba(91, 76, 240, 0.03)", border: "1px solid rgba(91, 76, 240, 0.15)", padding: "10px", borderRadius: "8px" }}>
                <span style={{ fontWeight: 800, color: "#5B4CF0" }}>🏠 Home Activities</span>
                <p style={{ margin: "2px 0 0 0", color: "#57606F" }}>Support independent research, supply physical materials, and allow experimental play.</p>
              </div>
              <div style={{ background: "rgba(0, 184, 169, 0.03)", border: "1px solid rgba(0, 184, 169, 0.15)", padding: "10px", borderRadius: "8px" }}>
                <span style={{ fontWeight: 800, color: "#00B8A9" }}>🏫 School Activities</span>
                <p style={{ margin: "2px 0 0 0", color: "#57606F" }}>Request the facilitator to offer open-ended challenge questions during classes.</p>
              </div>
              <div style={{ background: "#FDFDFD", border: "1px solid rgba(0, 0, 0, 0.05)", padding: "10px", borderRadius: "8px" }}>
                <span style={{ fontWeight: 800, color: "#F7B731" }}>🛠️ Workshop Suggestions</span>
                <p style={{ margin: "2px 0 0 0", color: "#57606F" }}>Attend the recommended {notes[0]?.suggested_workshop || `${DOMAINS[primaryDomain]?.label} Club`}.</p>
              </div>
              <div style={{ background: "#FDFDFD", border: "1px solid rgba(0, 0, 0, 0.05)", padding: "10px", borderRadius: "8px" }}>
                <span style={{ fontWeight: 800, color: "#8E9BAE" }}>🧑‍🏫 Mentor Advice</span>
                <p style={{ margin: "2px 0 0 0", color: "#57606F" }}>Arrange bi-weekly check-ins to monitor learning progress and build confidence.</p>
              </div>
            </div>
          </div>
          <div className="report-page-footer">
            <span>TINS Discovery &amp; Nurturing Report</span>
            <span>Page 8</span>
          </div>
        </div>

        {/* PAGE 9: EXPLORATION PATHWAYS */}
        <div className="report-page">
          <div>
            <div className="report-page-header">
              <span className="logo-group">🧠 TINS</span>
              <span className="report-section-name">Exploration Pathways</span>
            </div>
            <h2 style={{ fontSize: "20px", fontWeight: 800, color: "#5B4CF0", margin: "0 0 16px 0" }}>DEVELOPMENT EXPLORATION PATHWAYS</h2>
            <p className="muted-copy" style={{ marginBottom: 20 }}>
              Active learning tracks recommended for {child?.name} based on their top cognitive strengths:
            </p>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
              {[primaryDomain, ...secondaryDomains].slice(0, 2).map(domain => {
                const d = DOMAINS[domain];
                const pathways = {
                  creative: ["Drawing & Painting", "Design Thinking", "2D/3D Animation", "Storytelling & Theater"],
                  spatial: ["Robotics Building", "Architecture Design", "Model Construction", "Engineering Drawings"],
                  logical: ["Computer Coding", "Chess & Strategy", "Mathematics Puzzles", "Scientific Experiments"],
                  social: ["Group Volunteering", "Peer Mentorship", "Organizing Clubs", "Youth Leadership"],
                  language: ["Debate Forums", "Podcasting & Journalism", "Public Speaking", "Creative Writing"],
                  naturalist: ["Nature Observations", "Environmental Projects", "Wildlife Care", "Ecosystem Mapping"],
                  kinesthetic: ["Agility Sports", "Dance Choreography", "Woodworking & Craft", "Physical Endurance"],
                  intrapersonal: ["Goal Setting", "Journaling & Writing", "Solo Engineering Hobbies", "Mindfulness Practices"]
                }[domain] || ["Introductory Studies", "Exploratory Clubs", "Creative Thinking"];

                return (
                  <div key={domain} style={{ background: "#FFFFFF", border: "1px solid rgba(91, 76, 240, 0.15)", borderRadius: "12px", padding: "16px" }}>
                    <h4 style={{ color: d?.color, fontWeight: 900, fontSize: "15px", margin: "0 0 10px 0" }}>{d?.emoji} {d?.label} Pathway</h4>
                    <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                      {pathways.map(p => (
                        <div key={p} style={{ background: "rgba(91, 76, 240, 0.03)", border: "1px solid rgba(0,0,0,0.03)", padding: "8px 10px", borderRadius: "8px", fontSize: "13px", fontWeight: 700, color: "#4A4A4A" }}>
                          🚀 {p}
                        </div>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
          <div className="report-page-footer">
            <span>TINS Discovery &amp; Nurturing Report</span>
            <span>Page 9</span>
          </div>
        </div>

        {/* PAGE 10: FACILITATOR VALIDATION (MENTOR REVIEW) */}
        <div className="report-page">
          <div>
            <div className="report-page-header">
              <span className="logo-group">🧠 TINS</span>
              <span className="report-section-name">Mentor Review</span>
            </div>
            <h2 style={{ fontSize: "20px", fontWeight: 800, color: "#5B4CF0", margin: "0 0 16px 0" }}>MENTOR VALIDATION &amp; REVIEW</h2>

            {notes.length > 0 ? (
              <div style={{ background: "#FFFFFF", border: "1px solid rgba(91, 76, 240, 0.15)", borderRadius: "12px", padding: "16px", fontSize: "13px" }}>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: "8px", background: "rgba(91, 76, 240, 0.04)", padding: "10px", borderRadius: "8px", marginBottom: "12px", fontWeight: 800, textAlign: "center" }}>
                  <div>🎨 CR: <strong>{notes[0].obs_creativity || "3"}/5</strong></div>
                  <div>💬 CO: <strong>{notes[0].obs_communication || "3"}/5</strong></div>
                  <div>🤝 LE: <strong>{notes[0].obs_leadership || "3"}/5</strong></div>
                  <div>🎯 FO: <strong>{notes[0].obs_focus || "3"}/5</strong></div>
                  <div>🔍 CU: <strong>{notes[0].obs_curiosity || "3"}/5</strong></div>
                </div>
                <p style={{ margin: "0 0 8px 0" }}><strong>Observed Strengths:</strong> {notes[0].strengths_observed || "Demonstrated spontaneous problem solving and high focus during design activities."}</p>
                <p style={{ margin: "0 0 8px 0" }}><strong>Observed Challenges:</strong> {notes[0].concerns || "None flagged."}</p>
                <p style={{ margin: "0 0 8px 0" }}><strong>Workshop Recommendation:</strong> {notes[0].suggested_workshop}</p>
                <p style={{ margin: "0 0 12px 0" }}><strong>Mentor Notes:</strong> {notes[0].notes || notes[0].evidence_notes}</p>
                
                <div style={{ display: "flex", justifyContent: "space-between", borderTop: "1px solid #eee", paddingTop: "12px", marginTop: "12px", fontSize: "12px" }}>
                  <span><strong>Status:</strong> <span style={{ color: notes[0].confirmed ? "#00B8A9" : "#E17055", fontWeight: 800 }}>{notes[0].confirmed ? "✓ Validated" : "Needs Further Observation"}</span></span>
                  <span><strong>Reviewer:</strong> {notes[0].facilitator}</span>
                </div>
              </div>
            ) : (
              <div style={{ background: "#FFFBF2", border: "1px dashed #E2B25B", borderRadius: "12px", padding: "16px", fontSize: "13.5px", color: "#5D4037", textAlign: "center", fontWeight: 600 }}>
                💡 Permanent facilitator review pending validation. Mentor observations can be logged below using the screen form.
              </div>
            )}

            {/* Facilitator Signoff block for printed report */}
            <div style={{ marginTop: "24px", display: "grid", gridTemplateColumns: "1fr 1fr", gap: "24px" }}>
              <div style={{ borderBottom: "1px solid #ccc", height: "45px", display: "flex", alignItems: "flex-end", paddingBottom: "4px", fontSize: "12px" }}>
                <span><strong>Facilitator Signature:</strong> ______________________</span>
              </div>
              <div style={{ borderBottom: "1px solid #ccc", height: "45px", display: "flex", alignItems: "flex-end", paddingBottom: "4px", fontSize: "12px" }}>
                <span><strong>Date:</strong> ______________________</span>
              </div>
            </div>
          </div>
          <div className="report-page-footer">
            <span>TINS Discovery &amp; Nurturing Report</span>
            <span>Page 10</span>
          </div>
        </div>

        {/* PAGE 11: GROWTH TRACKING */}
        <div className="report-page">
          <div>
            <div className="report-page-header">
              <span className="logo-group">🧠 TINS</span>
              <span className="report-section-name">Longitudinal Growth</span>
            </div>
            <h2 style={{ fontSize: "20px", fontWeight: 800, color: "#5B4CF0", margin: "0 0 12px 0" }}>DEVELOPMENT JOURNEY TIMELINE</h2>
            <p className="muted-copy" style={{ marginBottom: 16 }}>
              Tracking assessment milestones and workshop validations chronologically:
            </p>

            <div style={{ width: "100%", height: "160px", marginBottom: "16px" }}>
              <GrowthChart history={history} />
            </div>

            <div style={{ fontSize: "12.5px" }}>
              <h4 style={{ margin: "0 0 6px 0", color: "#5B4CF0", textTransform: "uppercase", fontSize: "11px", letterSpacing: "0.5px" }}>Development Milestones</h4>
              <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                <div style={{ background: "#FFFFFF", border: "1px solid rgba(0,0,0,0.03)", padding: "8px 10px", borderRadius: "8px", display: "flex", justifyContent: "space-between" }}>
                  <span>🏁 Assessment Initialized</span>
                  <span style={{ color: "#8E9BAE" }}>{new Date(session.created_at).toLocaleDateString()}</span>
                </div>
                <div style={{ background: "#FFFFFF", border: "1px solid rgba(0,0,0,0.03)", padding: "8px 10px", borderRadius: "8px", display: "flex", justifyContent: "space-between" }}>
                  <span>🎯 Discovery &amp; Deep Puzzles Completed</span>
                  <span style={{ color: "#00B8A9" }}>{session.completed_at ? new Date(session.completed_at).toLocaleDateString() : "Complete"}</span>
                </div>
                <div style={{ background: "#FFFFFF", border: "1px solid rgba(0,0,0,0.03)", padding: "8px 10px", borderRadius: "8px", display: "flex", justifyContent: "space-between" }}>
                  <span>🧑‍🏫 Facilitator validation reviewed</span>
                  <span style={{ color: notes.length > 0 ? "#5B4CF0" : "#8E9BAE", fontWeight: 800 }}>{notes.length > 0 ? "✓ Validated" : "Pending"}</span>
                </div>
              </div>
            </div>
          </div>
          <div className="report-page-footer">
            <span>TINS Discovery &amp; Nurturing Report</span>
            <span>Page 11</span>
          </div>
        </div>

        {/* PAGE 12: METHODOLOGY & SCIENTIFIC DISCLOSURE */}
        <div className="report-page">
          <div>
            <div className="report-page-header">
              <span className="logo-group">🧠 TINS</span>
              <span className="report-section-name">Methodology &amp; Disclosure</span>
            </div>
            <h2 style={{ fontSize: "18px", fontWeight: 800, color: "#5B4CF0", margin: "0 0 10px 0" }}>ASSESSMENT METHODOLOGY</h2>
            <p style={{ fontSize: "12px", lineHeight: "1.5", color: "#57606F", margin: "0 0 16px 0" }}>
              TINS uses a multi-faceted approach. Natural behavior, decision styles, and cognitive speed are analyzed dynamically through standardized puzzle banks.
            </p>

            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", background: "rgba(91, 76, 240, 0.04)", padding: "8px 12px", borderRadius: "8px", fontSize: "11px", fontWeight: 800, color: "#5B4CF0", marginBottom: "16px", textAlign: "center" }}>
              <span>Discovery</span>
              <span>→</span>
              <span>Exposure</span>
              <span>→</span>
              <span>Assessment</span>
              <span>→</span>
              <span>Validation</span>
              <span>→</span>
              <span>Nurturing</span>
              <span>→</span>
              <span>Growth</span>
            </div>

            <div className="card section-card" style={{
              background: "#FFFBF2",
              border: "1px dashed #E2B25B",
              borderRadius: "10px",
              padding: "12px 14px",
              margin: 0
            }}>
              <h3 style={{ color: "#B7791F", margin: "0 0 6px 0", fontSize: "14px", fontWeight: 800 }}>
                ⚠️ Scientific Disclosure &amp; Limitations
              </h3>
              <p style={{ fontSize: "12px", lineHeight: "1.5", color: "#5D4037", margin: 0, fontWeight: 500 }}>
                This assessment identifies **indicators of potential**, not fixed or permanent abilities. Cognitive talents develop continuously through structured exposure, practice, active mentorship, and sustained effort. These results serve as early guides and must always be cross-referenced with parent/mentor observations, academic performance, and future longitudinal tracking. We support discovery and development, not rigid categorization.
              </p>
            </div>
          </div>
          <div className="report-page-footer">
            <span>TINS Discovery &amp; Nurturing Report</span>
            <span>Page 12</span>
          </div>
        </div>

      </div>

      {/* ── PERMANENT FACILITATOR REVIEW PANEL (Web Screen Form Only) ── */}
      <div className="card section-card hide-print" style={{ border: "1px solid rgba(108, 92, 231, 0.25)", marginTop: "24px" }}>
        <h2 className="card-title-tight" style={{ color: "var(--blue)" }}>🧑‍🏫 Facilitator Review &amp; Validation Note</h2>
        <p className="muted-copy" style={{ marginBottom: 20 }}>
          Submit permanent behavioral observations, validation logs, and suggested workshops. Original assessment scores are kept read-only for database audit credibility.
        </p>

        {notes.length > 0 && (
          <div style={{ background: "#F8F9FA", padding: 16, borderRadius: 12, borderLeft: "4px solid #6C5CE7", marginBottom: 20 }}>
            <h4 style={{ margin: "0 0 6px 0", color: "var(--blue)" }}>Latest logged review (by {notes[0].facilitator})</h4>
            <div style={{ margin: 0, fontSize: 13.5, lineHeight: 1.6, color: "#2D3436" }}>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "8px", background: "rgba(108, 92, 231, 0.04)", padding: "10px", borderRadius: "8px", marginBottom: "10px" }}>
                <span>🎨 Creativity: <strong>{notes[0].obs_creativity || "N/A"}/5</strong></span>
                <span>💬 Communication: <strong>{notes[0].obs_communication || "N/A"}/5</strong></span>
                <span>🤝 Leadership: <strong>{notes[0].obs_leadership || "N/A"}/5</strong></span>
                <span>🎯 Focus: <strong>{notes[0].obs_focus || "N/A"}/5</strong></span>
                <span>🔍 Curiosity: <strong>{notes[0].obs_curiosity || "N/A"}/5</strong></span>
              </div>
              {notes[0].evidence_notes && (
                <p style={{ margin: "0 0 8px 0" }}><strong>Evidence Notes:</strong> {notes[0].evidence_notes}</p>
              )}
              {notes[0].strengths_observed && (
                <p style={{ margin: "0 0 8px 0" }}><strong>Observed Strengths:</strong> {notes[0].strengths_observed}</p>
              )}
              {notes[0].concerns && (
                <p style={{ margin: "0 0 8px 0" }}><strong>Evidence of concerns:</strong> {notes[0].concerns}</p>
              )}
              <p style={{ margin: "0 0 8px 0" }}><strong>Suggested Workshop:</strong> {notes[0].suggested_workshop}</p>
              <p style={{ margin: 0 }}><strong>Final Recommendation:</strong> {notes[0].notes}</p>
            </div>
            <span style={{ fontSize: 11.5, color: "#666", display: "block", marginTop: 8 }}>
              Logged on {new Date(notes[0].created_at).toLocaleString()} &middot; Status: {notes[0].confirmed ? "Confirmed top domain" : `Override to ${notes[0].override_domain}`}
            </span>
          </div>
        )}

        <form onSubmit={submitFacReview} style={{ display: "flex", flexDirection: "column", gap: 14 }}>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 14 }}>
            <div className="form-group">
              <label>Facilitator validation agreement</label>
              <select value={facForm.confirmed} onChange={e => setFacForm(prev => ({ ...prev, confirmed: parseInt(e.target.value) }))}>
                <option value={1}>Agree (Confirm Primary Talent Domain)</option>
                <option value={0}>Disagree (Override with alternate domain)</option>
              </select>
            </div>

            {!facForm.confirmed && (
              <div className="form-group">
                <label>Select Override Domain</label>
                <select value={facForm.override_domain} onChange={e => setFacForm(prev => ({ ...prev, override_domain: e.target.value }))} required>
                  <option value="">Select Override...</option>
                  {Object.entries(DOMAINS).map(([key, d]) => (
                    <option key={key} value={key}>{d.emoji} {d.label}</option>
                  ))}
                </select>
              </div>
            )}

            <div className="form-group">
              <label>Recommended Nurturing Workshop</label>
              <select value={facForm.suggested_workshop} onChange={e => setFacForm(prev => ({ ...prev, suggested_workshop: e.target.value }))}>
                <option>Art &amp; Design Workshop</option>
                <option>STEM &amp; Coding Basics</option>
                <option>Tinkering &amp; Making Lab</option>
                <option>Youth Leadership Forum</option>
                <option>Storytelling &amp; Theatre Club</option>
                <option>Young Naturalist Trails</option>
                <option>Sports Training Camp</option>
                <option>Mindfulness &amp; Writing Seminar</option>
              </select>
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 14, margin: "14px 0" }}>
            {[
              { key: "obs_creativity", label: "Creativity (1-5)", emoji: "🎨" },
              { key: "obs_communication", label: "Communication (1-5)", emoji: "💬" },
              { key: "obs_leadership", label: "Leadership (1-5)", emoji: "🤝" },
              { key: "obs_focus", label: "Focus (1-5)", emoji: "🎯" },
              { key: "obs_curiosity", label: "Curiosity (1-5)", emoji: "🔍" }
            ].map((f) => (
              <div className="form-group" key={f.key}>
                <label>{f.emoji} {f.label}</label>
                <select 
                  value={facForm[f.key]} 
                  onChange={e => setFacForm(prev => ({ ...prev, [f.key]: parseInt(e.target.value) }))}
                >
                  <option value={1}>1 - Developing</option>
                  <option value={2}>2 - Moderate</option>
                  <option value={3}>3 - Consistently Strong</option>
                  <option value={4}>4 - Exceptional Intuition</option>
                  <option value={5}>5 - Mastery/Natural Gift</option>
                </select>
              </div>
            ))}
          </div>

          <div className="form-group">
            <label>Observed Strengths</label>
            <textarea 
              rows={2} 
              placeholder="Describe child's spontaneous behaviors, collaboration or focus..." 
              value={facForm.strengths_observed} 
              onChange={e => setFacForm(prev => ({ ...prev, strengths_observed: e.target.value }))} 
              required 
            />
          </div>

          <div className="form-group">
            <label>Observed Challenges</label>
            <textarea 
              rows={2} 
              placeholder="e.g. Struggles with rigid rote exercises; can get bored quickly if not actively engaged..." 
              value={facForm.concerns} 
              onChange={e => setFacForm(prev => ({ ...prev, concerns: e.target.value }))} 
              required 
            />
          </div>

          <div className="form-group">
            <label>Standardized Evidence Notes (observed details)</label>
            <textarea 
              rows={2} 
              placeholder="e.g. Spontaneously took structural lead during spatial construction; counts complex geometry grids with zero cues..." 
              value={facForm.evidence_notes} 
              onChange={e => setFacForm(prev => ({ ...prev, evidence_notes: e.target.value }))} 
              required 
            />
          </div>

          <div className="form-group">
            <label>Final validation recommendation note / Mentor Notes</label>
            <textarea 
              rows={3} 
              placeholder="Enter final recommendation instructions for parents or mentors..." 
              value={facForm.notes} 
              onChange={e => setFacForm(prev => ({ ...prev, notes: e.target.value }))} 
              required 
            />
          </div>

          <button type="submit" className="btn btn-teal btn-lg btn-full" style={{ marginTop: 10 }}>
            Log Facilitator Validation &amp; Recalculate Scores
          </button>
        </form>
      </div>

      {/* ── CORE ACTIONS ROW (Screen Only) ── */}
      <div className="button-stack hide-print" style={{ marginTop: 24 }}>
        <a
          className="btn btn-primary btn-lg btn-full"
          href={pdfUrl}
          target="_blank"
          rel="noopener noreferrer"
          style={{ background: "#20BF6B", color: "#fff", display: "flex", alignItems: "center", justifyContent: "center", gap: "8px", textDecoration: "none", boxShadow: "0 4px 12px rgba(32, 191, 107, 0.2)" }}
        >
          📥 Download Premium PDF Report
        </a>
        <button
          className="btn btn-teal btn-lg btn-full"
          onClick={() => navigate(`/mentor/${cid}?domain=${primaryDomain}&sid=${sid}`)}
        >
          Find a mentor in {DOMAINS[primaryDomain]?.label || primaryDomain}
        </button>
        <button
          className="btn btn-ghost btn-full"
          onClick={() => navigate("/")}
        >
          Start new assessment
        </button>
      </div>

    </div>
  );
}

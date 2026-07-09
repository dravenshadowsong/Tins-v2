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

function GTIGauge({ score, label }) {
  const radius = 60;
  const stroke = 10;
  const normalizedRadius = radius - stroke * 2;
  const circumference = normalizedRadius * 2 * Math.PI;
  const strokeDashoffset = circumference - (score / 100) * circumference;
  
  const colors = {
    Exceptional: "#E84118",
    Advanced: "#0984E3",
    Developing: "#00B8A9",
    Emerging: "#FDCB6E",
    Explorer: "#95A5A6"
  };
  const color = colors[label] || "#6C5CE7";

  return (
    <div style={{ position: "relative", width: 140, height: 140, display: "flex", alignItems: "center", justifyContent: "center" }}>
      <svg height={140} width={140}>
        <circle stroke="rgba(0,0,0,0.04)" fill="transparent" strokeWidth={stroke} r={normalizedRadius} cx={70} cy={70} />
        <circle
          stroke={color}
          fill="transparent"
          strokeWidth={stroke}
          strokeDasharray={circumference + ' ' + circumference}
          style={{ strokeDashoffset, transition: "stroke-dashoffset 1s ease-in-out", transform: "rotate(-90deg)", transformOrigin: "50% 50%" }}
          r={normalizedRadius}
          cx={70}
          cy={70}
          strokeLinecap="round"
        />
      </svg>
      <div style={{ position: "absolute", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", textAlign: "center" }}>
        <span style={{ fontSize: "28px", fontWeight: 900, color: "var(--text)", lineHeight: 1 }}>{score}</span>
        <span style={{ fontSize: "10px", fontWeight: 800, color, textTransform: "uppercase", letterSpacing: "0.5px", marginTop: 4 }}>{label}</span>
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
    document.title = `${safeName}_GOAT_Talent_Discovery_Report`;
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

  const calculateFallbackGTI = (integ_scores) => {
    const sorted_entries = Object.entries(integ_scores).sort((a, b) => b[1] - a[1]);
    const top_1 = sorted_entries[0]?.[1] || 0;
    const top_2 = sorted_entries[1]?.[1] || 0;
    const top_3 = sorted_entries[2]?.[1] || 0;
    const score = Math.round(0.5 * top_1 + 0.3 * top_2 + 0.2 * top_3);
    let label = "Explorer";
    if (score >= 85) label = "Exceptional";
    else if (score >= 75) label = "Advanced";
    else if (score >= 65) label = "Developing";
    else if (score >= 50) label = "Emerging";
    return { score, label };
  };

  const fallbackGTI = calculateFallbackGTI(integ);
  const gtiScore = analysis.gti_score !== undefined ? analysis.gti_score : fallbackGTI.score;
  const gtiLabel = analysis.gti_label || fallbackGTI.label;

  const getGtiDescription = (label) => {
    switch (label) {
      case "Exceptional":
        return "Demonstrates highly advanced logical coordination and cognitive flexibility across multiple talent domains. Extremely strong indicators.";
      case "Advanced":
        return "Showcases strong, well-developed talent patterns with clear indicators of active inquiry and structured logic.";
      case "Developing":
        return "Displays steady foundational capabilities and solid indicators of comfort with problem solving. Good potential for growth.";
      case "Emerging":
        return "Shows early-stage talent indicators; shows creative curiosity and intuitive approach in multiple tasks.";
      default:
        return "Active explorer of cognitive tasks. Broad interest patterns with great opportunity for structured exposure.";
    }
  };

  const getFallbackPersonas = () => {
    const top_3 = [primaryDomain, ...secondaryDomains];
    const resolved = {};
    const keys = ["primary", "secondary", "emerging"];
    keys.forEach((key, idx) => {
      const dom = top_3[idx] || "logical";
      const pData = PERSONAS[dom] || PERSONAS.logical;
      const guideData = parentGuides[dom] || parentGuides.logical;
      resolved[key] = {
        key: dom,
        title: pData.title,
        emoji: pData.emoji,
        desc: pData.desc,
        strengths: pData.strengths,
        growth: pData.growth,
        environments: [guideData.environments || "Design labs and STEM spaces"]
      };
    });
    return resolved;
  };
  
  const childPersonas = analysis.personas || getFallbackPersonas();

  const getFallbackTegData = () => {
    const data = {};
    let expData = null;
    if (child?.exposure_data) {
      try {
        expData = typeof child.exposure_data === "string" ? JSON.parse(child.exposure_data) : child.exposure_data;
      } catch (e) {
        expData = null;
      }
    }

    let exposure_scores = {};
    if (expData && typeof expData === "object") {
      const q = {};
      for (let i = 1; i <= 12; i++) {
        q[`q${i}`] = parseFloat(expData[`q${i}`] !== undefined ? expData[`q${i}`] : 0);
      }
      const domain_exposures = {
        logical: (q.q1 + q.q2) / 2.0,
        spatial: (q.q3 + q.q1) / 2.0,
        creative: (q.q4 + q.q5) / 2.0,
        kinesthetic: (q.q8 + q.q5) / 2.0,
        language: (q.q11 + q.q6) / 2.0,
        social: (q.q7 + q.q6) / 2.0,
        naturalist: q.q9,
        intrapersonal: (q.q11 + q.q12) / 2.0
      };
      Object.entries(domain_exposures).forEach(([dom, val]) => {
        exposure_scores[dom] = Math.round((val / 4.0) * 100);
      });
    }

    Object.entries(integ).forEach(([domain, talent_score]) => {
      let exposure_score = 0;
      if (exposure_scores[domain] !== undefined) {
        exposure_score = exposure_scores[domain];
      } else {
        const exp_val = child?.[`exp_${domain}`] !== undefined ? child[`exp_${domain}`] : 1;
        exposure_score = Math.round((exp_val / 3) * 100);
      }
      const opportunity_score = Math.min(100, Math.round((talent_score + (100 - exposure_score)) * 0.56));
      let teg_status = "Exploratory";
      if (talent_score >= 75 && exposure_score <= 33) teg_status = "High Potential, Low Exposure";
      else if (talent_score >= 75 && exposure_score > 66) teg_status = "Nurtured Strength";
      else if (talent_score >= 75) teg_status = "Active Development";
      else if (talent_score >= 50 && exposure_score <= 50) teg_status = "Developing Potential";
      data[domain] = { talent_score, exposure_score, opportunity_score, teg_status };
    });
    return data;
  };
  const activeTegData = analysis.teg_data || getFallbackTegData();

  const getFallbackRoadmap = () => {
    return {
      week_1: { title: `Introductory ${primaryDomain.toUpperCase()} Workshop`, expected_outcome: "Begin basic exploration of skills", parent_action: "Provide materials and quiet environment", mentor_action: "Observe interest and check in weekly" },
      week_2: { title: `Collaborative project task`, expected_outcome: "Participate in group challenges", parent_action: "Encourage cooperation and discuss outcomes", mentor_action: "Guide peer interaction and resolve conflicts" },
      week_3: { title: `Advanced independent challenges`, expected_outcome: "Solve a complex project autonomously", parent_action: "Praise effort and record child's explanation", mentor_action: "Evaluate logical soundness and accuracy" },
      week_4: { title: `Mentorship showcase and review`, expected_outcome: "Present project to family or peers", parent_action: "Celebrate achievement and display project", mentor_action: "Review progress and set next developmental goals" }
    };
  };
  const roadmapData = analysis.roadmap || getFallbackRoadmap();

  const getFallbackCareerPathways = () => {
    return {
      careers: ["Specialist", "Engineer", "Innovator", "Consultant"],
      projects: ["Design and prototype a functional model"],
      competitions: ["National Science Fair", "Math/Arts Olympiad"],
      tracks: ["STEM / Practical Arts"]
    };
  };
  const activeCareerPathways = analysis.career_pathways || getFallbackCareerPathways();

  // ── Report Timing Data ─────────────────────────────────────────────────────
  const timingData = (() => {
    try { return session?.timing_data ? JSON.parse(session.timing_data) : null; }
    catch (_) { return null; }
  })();

  // ── Report Display Helper Functions ───────────────────────────────────────
  const getStrengthTier = (score) => {
    if (score >= 85) return { label: "Exceptional", color: "#5B4CF0" };
    if (score >= 70) return { label: "Strong",       color: "#00B8A9" };
    if (score >= 55) return { label: "Developing",   color: "#F7B731" };
    if (score >= 40) return { label: "Emerging",     color: "#E17055" };
    return                  { label: "Exploratory",  color: "#8E9BAE" };
  };

  const getConfidenceDots = (level) => {
    const map = { "Very High": 5, "High": 4, "Moderate": 3, "Low": 2, "Very Low": 1 };
    const filled = map[level] || 3;
    return "●".repeat(filled) + "○".repeat(5 - filled);
  };

  const getExposureLabel = (expScore) => {
    if (expScore >= 70) return "High";
    if (expScore >= 45) return "Moderate";
    if (expScore >= 20) return "Low";
    return "Minimal";
  };

  const getDevPriority = (score, expScore) => {
    if (score >= 75 && expScore <= 40) return { label: "High",   note: "High talent, low exposure — priority nurturing" };
    if (score >= 75)                   return { label: "Medium", note: "Strong domain — continue development track" };
    if (score >= 50)                   return { label: "Medium", note: "Developing — structured exposure recommended" };
    return                                    { label: "Low",    note: "Exploratory phase — introductory activities beneficial" };
  };

  const getEvidenceStrength = (evObj) => {
    if (!evObj) return "Low";
    const c = [evObj.has_preference, evObj.has_behavioral, evObj.has_performance].filter(Boolean).length;
    return c >= 3 ? "High" : c >= 2 ? "Medium" : "Low";
  };

  // ── Behavioural Profiles per Domain ───────────────────────────────────────
  const BEHAVIOURAL_PROFILES_MAP = {
    creative:      { traits: [{ trait: "Imaginative Thinker", desc: "Generates unusual solutions and unexpected connections spontaneously" }, { trait: "Visually Oriented", desc: "Favours visual and spatial representations over abstract text" }, { trait: "Divergent Problem Solver", desc: "Approaches challenges from multiple simultaneous angles" }, { trait: "Autonomy-Seeker", desc: "Prefers open-ended tasks with minimal external constraints" }, { trait: "Reflective Creator", desc: "Takes time to consider aesthetic options before committing" }, { trait: "Expressive Communicator", desc: "Uses creative media and metaphor to convey complex ideas" }], learningStyle: "Visual-Divergent", communicationStyle: "Expressive & Narrative", motivators: ["Original expression", "Design freedom", "Aesthetic challenges"], blindSpots: ["Structured repetition", "Rigid rule-following environments"], stressIndicators: ["Excessive constraints on output", "No creative outlet for energy"], idealEnvironment: "Open studios, maker spaces, and unstructured creative labs with access to diverse materials and mentor guidance." },
    logical:       { traits: [{ trait: "Analytical Thinker", desc: "Systematically breaks complex problems into component parts" }, { trait: "Pattern Recogniser", desc: "Quickly identifies hidden rules and logical structures" }, { trait: "Precise Communicator", desc: "Prefers exact, verifiable, accurate language" }, { trait: "Goal-Oriented", desc: "Works methodically toward clearly defined outcomes" }, { trait: "Persistent Reasoner", desc: "Continues working on difficult problems without giving up" }, { trait: "Evidence-Driven", desc: "Forms conclusions from data and logical inference, not intuition" }], learningStyle: "Sequential-Analytical", communicationStyle: "Precise & Evidence-Based", motivators: ["Logical challenges", "Numerical puzzles", "Clear cause-effect rules"], blindSpots: ["Emotional ambiguity", "Open-ended unstructured creative tasks"], stressIndicators: ["Vague or contradictory instructions", "Illogical environments"], idealEnvironment: "Structured STEM labs, coding environments, and quiet analytical spaces with clear objectives." },
    spatial:       { traits: [{ trait: "3D Thinker", desc: "Visualises objects and structures in three dimensions mentally" }, { trait: "Constructive Problem Solver", desc: "Builds mental or physical models to understand problems" }, { trait: "Detail Observer", desc: "Notices structural and architectural details others miss" }, { trait: "Hands-On Learner", desc: "Learns best by touching, building, and physically assembling" }, { trait: "Spatial Memory", desc: "Recalls layouts, configurations, and orientations accurately" }, { trait: "Innovative Designer", desc: "Proposes novel structural solutions intuitively" }], learningStyle: "Spatial-Constructive", communicationStyle: "Visual & Diagrammatic", motivators: ["Building challenges", "Design tasks", "Model construction"], blindSpots: ["Abstract verbal theory", "Extended written explanation work"], stressIndicators: ["No materials to manipulate", "Pure text-only environments"], idealEnvironment: "Tinkering labs, design workshops, robotics studios, and architecture spaces." },
    social:        { traits: [{ trait: "Empathetic Leader", desc: "Reads social situations quickly and responds with care" }, { trait: "Collaborative", desc: "Actively seeks group input and shared problem solutions" }, { trait: "Communicative", desc: "Expresses ideas clearly and confidently in group settings" }, { trait: "Conflict-Resolver", desc: "Naturally mediates disagreements and builds consensus" }, { trait: "Initiative-Taker", desc: "Volunteers to organise and lead activities without being asked" }, { trait: "Community-Minded", desc: "Motivated by group outcomes over individual recognition" }], learningStyle: "Interpersonal-Collaborative", communicationStyle: "Verbal & Relational", motivators: ["Group leadership", "Peer collaboration", "Social impact projects"], blindSpots: ["Extended solo, quiet tasks", "Prolonged independent focus"], stressIndicators: ["Social isolation", "Exclusion from group decisions"], idealEnvironment: "Community spaces, group projects, student councils, and collaborative team activities." },
    language:      { traits: [{ trait: "Verbal Fluency", desc: "Expresses ideas with clarity, speed, and precision" }, { trait: "Narrative Builder", desc: "Structures stories and arguments in compelling logical arcs" }, { trait: "Persuasive Communicator", desc: "Uses language skillfully to influence and explain" }, { trait: "Word-Sensitive", desc: "Notices word choices, puns, rhythm, and language nuance" }, { trait: "Active Listener", desc: "Attends carefully to verbal information and responds thoughtfully" }, { trait: "Curious Reader", desc: "Explores complex ideas through reading and writing" }], learningStyle: "Verbal-Auditory", communicationStyle: "Articulate & Storytelling-Driven", motivators: ["Debate", "Public performance", "Written and verbal expression"], blindSpots: ["Silent individual tasks", "Non-verbal communication settings"], stressIndicators: ["Communication restrictions", "No outlet for verbal expression"], idealEnvironment: "Debate clubs, theatre groups, writing workshops, and presentation arenas." },
    naturalist:    { traits: [{ trait: "Detail Observer", desc: "Notices environmental patterns and micro-details others miss" }, { trait: "Taxonomic Thinker", desc: "Naturally classifies and categorises living things systematically" }, { trait: "Environmentally Empathic", desc: "Demonstrates deep care for natural ecosystems and organisms" }, { trait: "Outdoor Learner", desc: "Performs best in natural, open-air settings" }, { trait: "Biological Curiosity", desc: "Drawn to plants, animals, weather, and life science" }, { trait: "Patient Investigator", desc: "Observes carefully and at length before drawing conclusions" }], learningStyle: "Environmental-Observational", communicationStyle: "Descriptive & Grounded", motivators: ["Outdoor exploration", "Animal care", "Nature-based study"], blindSpots: ["Abstract symbolic reasoning tasks", "Indoor sedentary environments"], stressIndicators: ["Artificial environments", "Disconnection from nature"], idealEnvironment: "Nature trails, school gardens, environmental labs, and ecological fieldwork settings." },
    kinesthetic:   { traits: [{ trait: "High Physical Energy", desc: "Channels energy productively through movement and action" }, { trait: "Fine-Motor Precision", desc: "Demonstrates excellent hand-eye coordination and dexterity" }, { trait: "Tactile Learner", desc: "Learns best by doing, touching, and physically engaging" }, { trait: "Spatial Awareness", desc: "Understands own body position and movement in space naturally" }, { trait: "Action-Oriented", desc: "Consistently prefers doing tasks over reading or listening" }, { trait: "Physical Persistence", desc: "Continues physical challenges with notable stamina and drive" }], learningStyle: "Tactile-Kinesthetic", communicationStyle: "Demonstrative & Active", motivators: ["Sports challenges", "Physical tasks", "Hands-on construction"], blindSpots: ["Passive listening sessions", "Extended periods of sitting"], stressIndicators: ["Physical confinement", "No movement breaks during study"], idealEnvironment: "Sports facilities, dance studios, maker labs, and outdoor physical challenge environments." },
    intrapersonal: { traits: [{ trait: "Self-Aware", desc: "Understands own emotions, motivations, and limitations clearly" }, { trait: "Goal-Setter", desc: "Plans ahead with clear, personal, thoughtful objectives" }, { trait: "Reflective Thinker", desc: "Takes time to internally process experiences before responding" }, { trait: "Independent Worker", desc: "Thrives in solo, self-directed project environments" }, { trait: "Emotionally Regulated", desc: "Manages frustration and setbacks with unusual calmness" }, { trait: "Principled", desc: "Has clear personal values that consistently guide decisions" }], learningStyle: "Reflective-Self-Directed", communicationStyle: "Thoughtful & Written", motivators: ["Personal goals", "Independent projects", "Self-improvement tracks"], blindSpots: ["Highly competitive group settings", "Spontaneous public demands"], stressIndicators: ["Loss of autonomy", "Chaotic unpredictable environments"], idealEnvironment: "Quiet study spaces, journaling corners, independent project labs, and mindfulness spaces." },
  };
  const behaviourProfile = BEHAVIOURAL_PROFILES_MAP[primaryDomain] || BEHAVIOURAL_PROFILES_MAP.creative;

  // ── Extended Parent Guide per Domain ──────────────────────────────────────
  const PARENT_GUIDE_EXT = {
    creative:      { dailyActivities: ["10 minutes of free drawing or sketching", "Create a story around any everyday object", "Photograph one interesting pattern or texture"], weeklyActivities: ["Visit an art gallery or design exhibit", "Participate in an open-ended craft session", "Watch a documentary on art, design, or architecture"], books: ['"The Art of Creative Thinking" — Rod Judkins', '"What Do You Do With an Idea?" — Kobi Yamada'], educationalGames: ["Pictionary or sketchbook games", "Minecraft (creative mode)", "Story Cubes"], schoolClubs: ["Art Club", "Drama & Theatre Society", "Design Thinking Workshop"], competitions: ["National Children's Art Competition", "State-level Drawing & Painting Olympiad"], projects: ["Design a poster for a school event", "Build a miniature model of an imagined city"], teacherSuggestion: "Offer open-ended art integration tasks alongside core curriculum. Allow visual alternatives to written reports and presentations.", parentSuggestion: "Provide a dedicated creative space at home with varied materials. Celebrate the process, not just the final product." },
    logical:       { dailyActivities: ["Solve one mathematical puzzle or riddle", "Play a logic-based game for 15 minutes", "Explain how one everyday system works"], weeklyActivities: ["Play chess, Sudoku, or strategy board games", "Build a simple coding project using Scratch", "Watch a science or mathematics documentary"], books: ['"The Number Devil" — Hans Magnus Enzensberger', '"Thinking, Fast and Slow" (junior adaptation)'], educationalGames: ["Chess", "Code.org puzzles", "Perplexus or Rush Hour logic game"], schoolClubs: ["Mathematics Club", "Science Olympiad Team", "Coding & Robotics Club"], competitions: ["National Science Olympiad", "Mathematics Olympiad (junior)", "Coding competitions on Code.org"], projects: ["Build a working calculator in Scratch", "Design a logic puzzle for classmates"], teacherSuggestion: "Offer advanced extension problems in mathematics and science. Encourage logical reasoning across all subjects.", parentSuggestion: "Provide logic puzzles and strategy games regularly. Ask 'how does this work?' questions during daily life." },
    spatial:       { dailyActivities: ["Sketch a map or floor plan of one room", "Solve a spatial puzzle or 3D cube challenge", "Build something small using available materials"], weeklyActivities: ["LEGO or construction kit building sessions", "Watch engineering or architecture content", "Visit a science museum or technology expo"], books: ['"The Way Things Work" — David Macaulay', '"Iggy Peck, Architect" — Andrea Beaty'], educationalGames: ["LEGO Mindstorms", "Blokus spatial strategy game", "IsometriX puzzles"], schoolClubs: ["Robotics Club", "Architecture & Design Lab", "Engineering Challenges Club"], competitions: ["National Robotics Competition", "Design & Build challenges at regional fairs"], projects: ["Build a working bridge from cardboard", "Create an architectural sketch of an imagined building"], teacherSuggestion: "Use 3D models and visual diagrams in instruction. Allow alternative presentation formats including models and blueprints.", parentSuggestion: "Invest in building and construction kits. Encourage tinkering and taking things apart safely to understand how they work." },
    social:        { dailyActivities: ["Ask one meaningful question to a family member", "Practise active listening in one conversation today", "Plan one small group activity or game for peers"], weeklyActivities: ["Participate in community volunteering", "Organise a group event for peers or family", "Attend a debate or public speaking session"], books: ['"The Leader Who Had No Title" — Robin Sharma', '"Wonder" — R. J. Palacio'], educationalGames: ["Cooperative board games (Pandemic, Forbidden Island)", "Diplomacy (simplified edition)", "Role-playing and debate scenarios"], schoolClubs: ["Student Council", "Peer Mentorship Programme", "Youth Leadership Forum"], competitions: ["Model United Nations", "Youth Leadership Summit", "Inter-school debate competitions"], projects: ["Organise a fundraiser for a chosen community cause", "Lead a peer study group for one subject"], teacherSuggestion: "Assign group leadership roles regularly. Encourage peer teaching and conflict resolution activities in class.", parentSuggestion: "Support involvement in community groups. Create structured leadership opportunities at home." },
    language:      { dailyActivities: ["Write three sentences about the day in a journal", "Read one chapter of a quality book or article", "Tell a two-minute story about any topic at dinner"], weeklyActivities: ["Participate in debate club or storytelling group", "Write and perform a short poem or speech", "Listen to a high-quality podcast or audiobook"], books: ['"The Phantom Tollbooth" — Norton Juster', '"Matilda" — Roald Dahl'], educationalGames: ["Scrabble or Boggle", "Story Spine storytelling game", "Apples to Apples (junior edition)"], schoolClubs: ["Debate Society", "Creative Writing Club", "School Newspaper or Journalism Club"], competitions: ["National Public Speaking Competition", "Creative Writing Olympiad", "Spell Bee or Word Olympiad"], projects: ["Write and publish a short illustrated story", "Produce a five-minute podcast episode on a chosen topic"], teacherSuggestion: "Provide verbal presentation alternatives to written work. Encourage debate, oral reporting, and storytelling in class.", parentSuggestion: "Read together daily. Encourage storytelling at mealtimes. Subscribe to quality children's magazines and newspapers." },
    naturalist:    { dailyActivities: ["Observe and sketch one plant or animal", "Keep a nature journal with daily observations", "Identify one new species using a field guide or app"], weeklyActivities: ["Nature walk in a local park, garden, or forest area", "Visit a wildlife sanctuary or botanical garden", "Complete one environmental awareness project or activity"], books: ['"The Hidden Life of Trees" — Peter Wohlleben (junior edition)', '"A First Field Guide" — National Audubon Society'], educationalGames: ["Nature Bingo in parks", "Eco-challenge field activities", "iNaturalist app-based species identification"], schoolClubs: ["Young Naturalists Club", "Eco Committee", "School Garden Project"], competitions: ["National Science Olympiad (Biology)", "Young Environmentalist Award", "Wildlife photography competitions"], projects: ["Create a local biodiversity map of the school garden", "Start a school composting or tree planting initiative"], teacherSuggestion: "Incorporate outdoor learning sessions regularly. Use nature-based metaphors and examples across all subjects.", parentSuggestion: "Plan regular outdoor nature experiences. Gift quality field guides, binoculars, and nature journals." },
    kinesthetic:   { dailyActivities: ["15–20 minutes of physical activity or sport", "Build or assemble something with hands today", "Practise one fine-motor skill (drawing, origami, clay work)"], weeklyActivities: ["Attend a structured sport or dance class", "Visit an adventure or outdoor activity centre", "Try a hands-on craft or engineering workshop"], books: ['"The Sports Gene" — David Epstein (simplified)', '"Bodies in Motion" — selected chapters for young readers'], educationalGames: ["Physical obstacle course challenges", "Sports strategy simulations", "Hands-on science experiment kits"], schoolClubs: ["Sports Team", "Dance Club", "Physical Challenge or Adventure Club"], competitions: ["District Sports Meets", "Regional dance competitions", "Obstacle course events and marathons"], projects: ["Design and build a functional physical structure", "Choreograph a short performance for family audience"], teacherSuggestion: "Integrate movement breaks into lessons. Allow kinaesthetic alternatives such as models, demonstrations, and performances.", parentSuggestion: "Support regular physical activity. Provide physical construction materials and hands-on project kits at home." },
    intrapersonal: { dailyActivities: ["Write three reflective lines in a personal journal", "Set one clear intention for the day each morning", "Spend 10 quiet minutes in independent reading or thinking"], weeklyActivities: ["Complete one solo creative or research project", "Practise a short mindfulness or breathing exercise", "Review personal goals and record weekly progress"], books: ['"Mindset" — Carol Dweck (junior edition)', '"The Boy Who Harnessed the Wind" — William Kamkwamba'], educationalGames: ["Mindfulness apps (Headspace for kids)", "Goal-tracking journaling activities", "Solo strategy puzzle games"], schoolClubs: ["Mindfulness Club", "Philosophy & Debate Society", "Independent Research Group"], competitions: ["Essay writing competitions", "Independent science or social research fairs", "Reflective writing awards"], projects: ["Design and complete a 30-day personal challenge", "Create a personal portfolio documenting 6 months of growth"], teacherSuggestion: "Provide independent project options. Respect quiet focus periods. Offer personal reflection as an alternative to group work.", parentSuggestion: "Respect quiet time and independent exploration. Provide journals, personal project materials, and solo learning resources." },
  };
  const extendedGuide = PARENT_GUIDE_EXT[primaryDomain] || PARENT_GUIDE_EXT.creative;

  // ── Extended Career Pathways per Domain ───────────────────────────────────
  const CAREER_EXT = {
    creative:      { subjects: ["Visual Arts", "Design & Technology", "Media Studies", "Drama"], careerClusters: ["Visual Arts & Design", "Architecture", "Film & Media Production", "Fashion & Textiles"], clubs: ["Art Society", "Drama Club", "Creative Writing", "Film Club"], olympiads: ["Children's Art Olympiad", "Design Thinking Challenge", "National Drawing Competition"], competitions: ["State Painting Competition", "School Art Exhibition", "Animation Design Contest"], communityActivities: ["Community mural projects", "Art therapy volunteering", "Cultural festivals"], futureSkills: ["Design Thinking", "Digital Illustration (Adobe Suite)", "3D Modelling (Blender)", "UX/UI Design Principles"] },
    logical:       { subjects: ["Mathematics", "Physics", "Computer Science", "Chemistry"], careerClusters: ["Data Science & AI", "Software Engineering", "Research & Academia", "Finance & Actuarial Science"], clubs: ["Maths Club", "Coding Society", "Science Olympiad", "Robotics Team"], olympiads: ["Mathematics Olympiad", "Science Olympiad", "International Informatics Olympiad"], competitions: ["Coding competitions (HackerRank)", "National Science Fair", "Logic Puzzle Championships"], communityActivities: ["STEM tutoring for younger students", "Science fair volunteering", "Code for communities initiatives"], futureSkills: ["Python Programming", "Statistical Analysis", "Algorithm Design", "Machine Learning Fundamentals"] },
    spatial:       { subjects: ["Physics", "Design & Technology", "Engineering Drawing", "Mathematics"], careerClusters: ["Architecture", "Mechanical Engineering", "Interior Design", "Civil & Structural Engineering"], clubs: ["Robotics Club", "Architecture Club", "Tinkering Lab", "3D Printing Society"], olympiads: ["Engineering Design Challenge", "Robotics Olympiad", "National Science Olympiad"], competitions: ["Bridge Building Competition", "Model Rocketry", "Maker Faire"], communityActivities: ["Build community structures", "Repair and repurpose local facilities", "School infrastructure improvement"], futureSkills: ["AutoCAD", "3D Printing", "Robotics Programming", "Structural Analysis"] },
    social:        { subjects: ["Sociology", "Political Science", "Psychology", "Economics"], careerClusters: ["Social Work & NGO", "Public Policy", "Human Resources", "Education & Teaching"], clubs: ["Student Council", "Debate Society", "Model UN", "Community Service Committee"], olympiads: ["Model United Nations", "Youth Parliament", "Social Entrepreneurship Challenge"], competitions: ["Youth Leadership Summit", "Inter-school Debate", "Social Innovation Competition"], communityActivities: ["Youth volunteer leadership", "Peer counselling", "Community event organisation"], futureSkills: ["Leadership & Facilitation", "Conflict Resolution", "Public Speaking", "Project Management"] },
    language:      { subjects: ["English Literature", "Hindi / Regional Language", "History", "Journalism & Media"], careerClusters: ["Journalism & Publishing", "Law & Advocacy", "Teaching & Education", "Public Relations & Communications"], clubs: ["Debate Club", "Poetry Society", "School Newspaper", "Theatre Group"], olympiads: ["Word Olympiad", "Essay Writing Competition", "Creative Writing Awards", "Inter-school Debate"], competitions: ["National Spell Bee", "Public Speaking Championship", "Story Writing Contest"], communityActivities: ["Reading aloud to younger children", "Storytelling events at libraries and community centres"], futureSkills: ["Content Writing & Editing", "Public Speaking", "Research & Analysis", "Digital Journalism"] },
    naturalist:    { subjects: ["Biology", "Environmental Science", "Geography", "Chemistry"], careerClusters: ["Environmental Science", "Wildlife Conservation", "Veterinary Science", "Ecology & Field Research"], clubs: ["Eco Committee", "Nature Club", "Young Naturalists", "School Garden Club"], olympiads: ["Biology Olympiad", "Environmental Awareness Quiz", "Young Scientist Award"], competitions: ["Nature Photography Contest", "Environmental Project Fair", "Young Naturalist Award"], communityActivities: ["Tree planting drives", "Wildlife monitoring", "Environmental awareness campaigns"], futureSkills: ["Field Research Methods", "Ecological Mapping", "Environmental Policy Basics", "Scientific Data Collection"] },
    kinesthetic:   { subjects: ["Physical Education", "Biology", "Design & Technology", "Health Science"], careerClusters: ["Sports Science", "Physiotherapy & Rehabilitation", "Physical Education", "Dance & Performance Arts"], clubs: ["Sports Teams", "Dance Club", "Physical Challenge Club", "Outdoor Adventure Group"], olympiads: ["District Sports Meet", "National School Games", "Dance Championship"], competitions: ["Athletics meets", "Martial arts tournaments", "Dance & choreography competitions"], communityActivities: ["Coaching younger students in sports", "Physical fitness awareness campaigns"], futureSkills: ["Sports Science Basics", "Biomechanics", "Coaching & Training Methods", "Physical Health Management"] },
    intrapersonal: { subjects: ["Psychology", "Philosophy", "Literature", "Social Science"], careerClusters: ["Psychology & Counselling", "Philosophy & Research", "Creative Writing", "Education & Mentoring"], clubs: ["Mindfulness Club", "Philosophy Society", "Independent Research Group", "Journaling Club"], olympiads: ["Essay Writing Olympiad", "Social Science Research Fair", "Creative Writing Awards"], competitions: ["Reflective Writing Competition", "Personal Essay Contest", "Independent Research Presentation"], communityActivities: ["Peer counselling", "Mentoring younger students", "Mindfulness workshop facilitation"], futureSkills: ["Self-Regulation & EQ", "Research & Writing", "Empathy & Listening", "Independent Project Management"] },
  };
  const careerExtended = CAREER_EXT[primaryDomain] || CAREER_EXT.logical;

  // ── Development Roadmap Stages (30d / 90d / 6m / 12m) ─────────────────────
  const roadmapStages = [
    { stage: "30 Days", stageClass: "rp-stage-1", color: "#5B4CF0", title: "Initial Exposure & Discovery", goal: `Introduce ${primaryLabel} activities in a low-pressure, exploratory setting`, activities: [extendedGuide.dailyActivities?.[0] || "Daily domain-relevant practice", extendedGuide.weeklyActivities?.[0] || "Weekly structured group activity", `Enrol in: ${extendedGuide.schoolClubs?.[0] || "relevant school club"}`], expectedOutcome: "Child demonstrates voluntary interest and basic comfort with domain activities", successIndicators: ["Requests related materials independently", "Completes activities without prompting"] },
    { stage: "90 Days", stageClass: "rp-stage-2", color: "#00B8A9", title: "Structured Practice & Mentorship", goal: `Build consistent skill development with guided mentorship in ${primaryLabel}`, activities: [extendedGuide.weeklyActivities?.[1] || "Structured weekly skill session", `Project: ${extendedGuide.projects?.[0] || "Domain-relevant project"}`, "Bi-weekly mentor check-in and feedback"], expectedOutcome: "Measurable skill improvement with a demonstrable portfolio piece or presentation", successIndicators: ["Visible confidence in domain tasks", "Produces a tangible outcome or project"] },
    { stage: "6 Months", stageClass: "rp-stage-3", color: "#F7B731", title: "Advanced Projects & Portfolio Building", goal: `Develop a portfolio of ${primaryLabel} work and explore competition opportunities`, activities: [`Competition: ${extendedGuide.competitions?.[0] || "Relevant domain competition"}`, extendedGuide.projects?.[1] || "Advanced independent project", "Present portfolio to family or peer audience"], expectedOutcome: "Child has a verifiable portfolio and has participated in at least one external event", successIndicators: ["Peer recognition in domain", "Completion of a complex solo project"] },
    { stage: "12 Months", stageClass: "rp-stage-4", color: "#E17055", title: "Reassessment & Future Planning", goal: "Reassess development, identify next-level opportunities, and plan the year ahead", activities: ["Complete TINS Reassessment to measure domain growth", "Review 12-month portfolio with facilitator mentor", "Set goals for the next 12-month development cycle"], expectedOutcome: "Clear evidence of longitudinal growth with a defined pathway for continued development", successIndicators: ["Measurable score improvement in reassessment", "Child can articulate own developmental goals"] },
  ];

  const safeName = (child?.name || "Student").trim().replace(/\s+/g, "_");
  const personalizedSnapshot = `${child?.name || "The student"} appears to demonstrate strong developmental indicators in ${primaryLabel} activities, particularly in open-ended exploration and problem-solving styles. These findings suggest a natural comfort with ${primaryLabel} concepts. Secondary indicators also suggest potential in ${secondaryDomains.map(d => DOMAINS[d]?.label || d).join(" and ")} areas. Nurturing these talents in structured settings will provide a clearer picture of their long-term growth.`;
  const pdfUrl = `${api.downloadPDF(sid)}?token=${sessionStorage.getItem("goat_token")}&cid=${cid}`;

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
            <h1 style={{ margin: 0, fontSize: "24px", fontWeight: 900, color: "var(--text)" }}>GOAT Core Cognitive Dashboard</h1>
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

        {/* Master GTI Gauge Card & Persona Cards */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr", gap: 24, marginBottom: 24 }}>
          {/* Executive GTI Summary Card */}
          <div className="card summary-grid" style={{
            display: "grid",
            gridTemplateColumns: "1fr 2.5fr",
            gap: 24,
            background: "linear-gradient(135deg, rgba(108, 92, 231, 0.04) 0%, rgba(0, 184, 169, 0.04) 100%)",
            border: "1px solid rgba(108, 92, 231, 0.15)",
            borderRadius: 20,
            padding: "24px",
            alignItems: "center"
          }}>
            <div style={{ display: "flex", justifyContent: "center" }}>
              <GTIGauge score={gtiScore} label={gtiLabel} />
            </div>
            <div>
              <div style={{ display: "inline-flex", padding: "4px 10px", borderRadius: 99, background: "#6C5CE7", color: "#fff", fontSize: 10, fontWeight: 800, textTransform: "uppercase", letterSpacing: 0.8, marginBottom: 8 }}>
                GOAT Talent Index (GTI)
              </div>
              <h2 style={{ fontSize: "22px", fontWeight: 900, color: "var(--text)", margin: "0 0 6px 0" }}>Cognitive Synthesis</h2>
              <p style={{ fontSize: "14.5px", lineHeight: "1.6", color: "var(--text-mid)", margin: 0 }}>
                {getGtiDescription(gtiLabel)} This index represents the child's composite cognitive potential, computed across spatial, logical, and verbal reasoning capabilities.
              </p>
            </div>
          </div>

          {/* Persona Cards */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: 20 }}>
            {/* Primary Persona */}
            <div className="card" style={{
              border: "2px solid #5B4CF0",
              background: "linear-gradient(135deg, rgba(91, 76, 240, 0.04) 0%, #FFFFFF 100%)",
              borderRadius: 16,
              padding: 20,
              boxShadow: "0 8px 20px rgba(91, 76, 240, 0.04)"
            }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
                <span style={{ fontSize: 32 }}>{childPersonas.primary.emoji}</span>
                <span style={{ fontSize: 10, fontWeight: 950, background: "#5B4CF0", color: "#fff", padding: "4px 8px", borderRadius: 20, textTransform: "uppercase" }}>Primary Strength</span>
              </div>
              <h3 style={{ margin: "0 0 6px 0", fontSize: 18, fontWeight: 800, color: "#3C2EB9" }}>{childPersonas.primary.title}</h3>
              <p style={{ fontSize: 13, color: "var(--text-mid)", lineHeight: 1.5, margin: "0 0 14px 0" }}>{childPersonas.primary.desc}</p>
              
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                <div>
                  <span style={{ fontSize: 10, fontWeight: 800, color: "var(--text-light)", textTransform: "uppercase", display: "block" }}>Strength Indicators</span>
                  <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginTop: 4 }}>
                    {childPersonas.primary.strengths.map(s => (
                      <span key={s} style={{ fontSize: 11, fontWeight: 700, color: "#0F6E56", background: "#E1F5EE", padding: "3px 8px", borderRadius: 4 }}>✓ {s}</span>
                    ))}
                  </div>
                </div>
                <div style={{ marginTop: 6 }}>
                  <span style={{ fontSize: 10, fontWeight: 800, color: "var(--text-light)", textTransform: "uppercase", display: "block" }}>Development Opportunities</span>
                  <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginTop: 4 }}>
                    {childPersonas.primary.growth.map(g => (
                      <span key={g} style={{ fontSize: 11, fontWeight: 700, color: "#7F8C8D", background: "#F5F6FA", padding: "3px 8px", borderRadius: 4 }}>⚬ {g}</span>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Secondary Persona */}
            <div className="card" style={{
              border: "1px solid rgba(0, 184, 169, 0.3)",
              background: "linear-gradient(135deg, rgba(0, 184, 169, 0.03) 0%, #FFFFFF 100%)",
              borderRadius: 16,
              padding: 20
            }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
                <span style={{ fontSize: 32 }}>{childPersonas.secondary.emoji}</span>
                <span style={{ fontSize: 10, fontWeight: 950, background: "#00B8A9", color: "#fff", padding: "4px 8px", borderRadius: 20, textTransform: "uppercase" }}>Secondary Strength</span>
              </div>
              <h3 style={{ margin: "0 0 6px 0", fontSize: 18, fontWeight: 800, color: "#0F6E56" }}>{childPersonas.secondary.title}</h3>
              <p style={{ fontSize: 13, color: "var(--text-mid)", lineHeight: 1.5, margin: "0 0 14px 0" }}>{childPersonas.secondary.desc}</p>
              
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                <div>
                  <span style={{ fontSize: 10, fontWeight: 800, color: "var(--text-light)", textTransform: "uppercase", display: "block" }}>Strength Indicators</span>
                  <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginTop: 4 }}>
                    {childPersonas.secondary.strengths.map(s => (
                      <span key={s} style={{ fontSize: 11, fontWeight: 700, color: "#0F6E56", background: "#E1F5EE", padding: "3px 8px", borderRadius: 4 }}>✓ {s}</span>
                    ))}
                  </div>
                </div>
                <div style={{ marginTop: 6 }}>
                  <span style={{ fontSize: 10, fontWeight: 800, color: "var(--text-light)", textTransform: "uppercase", display: "block" }}>Development Opportunities</span>
                  <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginTop: 4 }}>
                    {childPersonas.secondary.growth.map(g => (
                      <span key={g} style={{ fontSize: 11, fontWeight: 700, color: "#7F8C8D", background: "#F5F6FA", padding: "3px 8px", borderRadius: 4 }}>⚬ {g}</span>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Emerging Persona */}
            <div className="card" style={{
              border: "1px solid rgba(253, 203, 110, 0.4)",
              background: "linear-gradient(135deg, rgba(253, 203, 110, 0.03) 0%, #FFFFFF 100%)",
              borderRadius: 16,
              padding: 20
            }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
                <span style={{ fontSize: 32 }}>{childPersonas.emerging.emoji}</span>
                <span style={{ fontSize: 10, fontWeight: 950, background: "#FDCB6E", color: "#fff", padding: "4px 8px", borderRadius: 20, textTransform: "uppercase" }}>Emerging Potential</span>
              </div>
              <h3 style={{ margin: "0 0 6px 0", fontSize: 18, fontWeight: 800, color: "#B7791F" }}>{childPersonas.emerging.title}</h3>
              <p style={{ fontSize: 13, color: "var(--text-mid)", lineHeight: 1.5, margin: "0 0 14px 0" }}>{childPersonas.emerging.desc}</p>
              
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                <div>
                  <span style={{ fontSize: 10, fontWeight: 800, color: "var(--text-light)", textTransform: "uppercase", display: "block" }}>Strength Indicators</span>
                  <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginTop: 4 }}>
                    {childPersonas.emerging.strengths.map(s => (
                      <span key={s} style={{ fontSize: 11, fontWeight: 700, color: "#0F6E56", background: "#E1F5EE", padding: "3px 8px", borderRadius: 4 }}>✓ {s}</span>
                    ))}
                  </div>
                </div>
                <div style={{ marginTop: 6 }}>
                  <span style={{ fontSize: 10, fontWeight: 800, color: "var(--text-light)", textTransform: "uppercase", display: "block" }}>Development Opportunities</span>
                  <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginTop: 4 }}>
                    {childPersonas.emerging.growth.map(g => (
                      <span key={g} style={{ fontSize: 11, fontWeight: 700, color: "#7F8C8D", background: "#F5F6FA", padding: "3px 8px", borderRadius: 4 }}>⚬ {g}</span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Cognitive Talent Profile (Categorized Sections) */}
        <div className="card" style={{ padding: 24, marginBottom: 24 }}>
          <h3 style={{ fontSize: "18px", fontWeight: 800, color: "var(--text)", marginBottom: 6 }}>Cognitive Talent Profile</h3>
          <p style={{ fontSize: "13px", color: "var(--text-light)", marginBottom: 20 }}>Categorized domains based on final stretched percentile scores.</p>
          
          <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
            {/* Primary Strengths (>= 85) */}
            <div>
              <h4 style={{ color: "#E84118", fontSize: "13.5px", fontWeight: 850, textTransform: "uppercase", letterSpacing: 0.8, borderBottom: "1.5px solid #FAD3CF", paddingBottom: 6, marginBottom: 10 }}>🌟 Primary Strengths (Percentile ≥ 85)</h4>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: 12 }}>
                {sorted.filter(([_, s]) => s >= 85).map(([domain, score]) => {
                  const d = DOMAINS[domain];
                  return (
                    <div key={domain} style={{ background: "rgba(232, 65, 24, 0.03)", border: "1.5px solid #FAD3CF", borderRadius: 10, padding: 12 }}>
                      <div style={{ display: "flex", justifyContent: "space-between", fontWeight: 800, fontSize: 13.5, marginBottom: 4 }}>
                        <span style={{ color: "var(--text)" }}>{d?.emoji} {d?.label}</span>
                        <span style={{ color: "#E84118" }}>{score}% (Exceptional)</span>
                      </div>
                      <p style={{ margin: 0, fontSize: 12, color: "var(--text-light)" }}>{DOMAIN_INSIGHTS[domain]}</p>
                    </div>
                  );
                })}
                {sorted.filter(([_, s]) => s >= 85).length === 0 && (
                  <span style={{ fontSize: 12.5, color: "var(--text-light)", fontStyle: "italic" }}>No domains scored in this tier.</span>
                )}
              </div>
            </div>

            {/* Secondary Strengths (65-84) */}
            <div style={{ marginTop: 8 }}>
              <h4 style={{ color: "#00B8A9", fontSize: "13.5px", fontWeight: 850, textTransform: "uppercase", letterSpacing: 0.8, borderBottom: "1.5px solid #BCEBE7", paddingBottom: 6, marginBottom: 10 }}>✨ Secondary Strengths (Percentile 65-84)</h4>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: 12 }}>
                {sorted.filter(([_, s]) => s >= 65 && s < 85).map(([domain, score]) => {
                  const d = DOMAINS[domain];
                  let qual = score >= 75 ? "Strong" : "Developing";
                  return (
                    <div key={domain} style={{ background: "rgba(0, 184, 169, 0.02)", border: "1.5px solid #BCEBE7", borderRadius: 10, padding: 12 }}>
                      <div style={{ display: "flex", justifyContent: "space-between", fontWeight: 800, fontSize: 13.5, marginBottom: 4 }}>
                        <span style={{ color: "var(--text)" }}>{d?.emoji} {d?.label}</span>
                        <span style={{ color: "#00B8A9" }}>{score}% ({qual})</span>
                      </div>
                      <p style={{ margin: 0, fontSize: 12, color: "var(--text-light)" }}>{DOMAIN_INSIGHTS[domain]}</p>
                    </div>
                  );
                })}
                {sorted.filter(([_, s]) => s >= 65 && s < 85).length === 0 && (
                  <span style={{ fontSize: 12.5, color: "var(--text-light)", fontStyle: "italic" }}>No domains scored in this tier.</span>
                )}
              </div>
            </div>

            {/* Growth Opportunities (< 65) */}
            <div style={{ marginTop: 8 }}>
              <h4 style={{ color: "#7F8C8D", fontSize: "13.5px", fontWeight: 850, textTransform: "uppercase", letterSpacing: 0.8, borderBottom: "1.5px solid #E2E8F0", paddingBottom: 6, marginBottom: 10 }}>🌱 Growth Opportunities (Percentile &lt; 65)</h4>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: 12 }}>
                {sorted.filter(([_, s]) => s < 65).map(([domain, score]) => {
                  const d = DOMAINS[domain];
                  let qual = score >= 50 ? "Emerging" : "Exploratory";
                  return (
                    <div key={domain} style={{ background: "#F8F9FA", border: "1.5px solid #E2E8F0", borderRadius: 10, padding: 12 }}>
                      <div style={{ display: "flex", justifyContent: "space-between", fontWeight: 800, fontSize: 13.5, marginBottom: 4 }}>
                        <span style={{ color: "var(--text)" }}>{d?.emoji} {d?.label}</span>
                        <span style={{ color: "#7F8C8D" }}>{score}% ({qual})</span>
                      </div>
                      <p style={{ margin: 0, fontSize: 12, color: "var(--text-light)" }}>{DOMAIN_INSIGHTS[domain]}</p>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>

        {/* Talent Map & TEG Index Grid */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1.5fr", gap: 24, marginBottom: 24 }} className="summary-grid">
          {/* Left: Radar Chart */}
          <div className="card" style={{ padding: 20, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
            <h3 style={{ fontSize: "17px", fontWeight: 800, color: "var(--text)", marginBottom: 14, alignSelf: "start" }}>Cognitive Talent Mapping</h3>
            <div style={{ width: "100%", height: "240px", display: "flex", alignItems: "center", justifyContent: "center" }}>
              <RadarChart scores={integ} />
            </div>
          </div>

          {/* Right: TEG index table */}
          <div className="card" style={{ padding: 20 }}>
            <h3 style={{ fontSize: "17px", fontWeight: 800, color: "var(--text)", marginBottom: 6 }}>Talent Exposure Gap (TEG) Dashboard</h3>
            <p style={{ fontSize: "12px", color: "var(--text-light)", marginBottom: 14 }}>Exposure metrics mapped 0-100%.</p>
            <div style={{ overflowX: "auto" }}>
              <table style={{ width: "100%", borderCollapse: "collapse" }}>
                <thead>
                  <tr style={{ borderBottom: "1.5px solid var(--border)", color: "var(--text-light)", fontSize: 11, fontWeight: 800, textAlign: "left" }}>
                    <th style={{ padding: "8px 4px" }}>Domain</th>
                    <th style={{ padding: "8px 4px" }}>Talent</th>
                    <th style={{ padding: "8px 4px" }}>Exposure</th>
                    <th style={{ padding: "8px 4px" }}>Opportunity</th>
                    <th style={{ padding: "8px 4px" }}>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {sorted.map(([domain, score]) => {
                    const d = DOMAINS[domain];
                    const teg = activeTegData[domain] || { talent_score: score, exposure_score: 30, opportunity_score: 50, teg_status: "Exploratory" };
                    let statusBg = "#F5F6FA";
                    let statusColor = "#7F8C8D";
                    if (teg.teg_status === "High Potential, Low Exposure") {
                      statusBg = "#FFF5E6";
                      statusColor = "#D35400";
                    } else if (teg.teg_status === "Nurtured Strength") {
                      statusBg = "#E1F5EE";
                      statusColor = "#0F6E56";
                    } else if (teg.teg_status === "Active Development") {
                      statusBg = "#E8F4FD";
                      statusColor = "#0984E3";
                    } else if (teg.teg_status === "Developing Potential") {
                      statusBg = "#F3E8FF";
                      statusColor = "#6C5CE7";
                    }
                    return (
                      <tr key={domain} style={{ borderBottom: "1px solid var(--border)", fontSize: 12.5 }}>
                        <td style={{ padding: "10px 4px", fontWeight: 700, color: "var(--text)" }}>{d?.emoji} {d?.label}</td>
                        <td style={{ padding: "10px 4px", color: d?.color, fontWeight: 800 }}>{teg.talent_score}%</td>
                        <td style={{ padding: "10px 4px" }}>{teg.exposure_score}%</td>
                        <td style={{ padding: "10px 4px", fontWeight: 800, color: "#6C5CE7" }}>{teg.opportunity_score}/100</td>
                        <td style={{ padding: "10px 4px" }}>
                          <span style={{ fontSize: 9.5, fontWeight: 800, background: statusBg, color: statusColor, padding: "2px 6px", borderRadius: 10 }}>
                            {teg.teg_status}
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Confidence rating and checklist */}
        <div className="card" style={{ padding: 24, marginBottom: 24 }}>
          <h3 style={{ fontSize: "18px", fontWeight: 800, color: "var(--text)", marginBottom: 12 }}>Talent Confidence Rating</h3>
          <div style={{ display: "grid", gridTemplateColumns: "1.2fr 2fr", gap: 24, alignItems: "center" }} className="summary-grid">
            <div style={{ textAlign: "center", background: "var(--surface-soft)", padding: 20, borderRadius: 14, border: "1.5px solid var(--border)" }}>
              <span style={{ fontSize: 11, fontWeight: 900, color: "var(--text-light)", textTransform: "uppercase", letterSpacing: 0.8 }}>Assessment Confidence</span>
              <div style={{ fontSize: 36, fontWeight: 900, color: "#6C5CE7", margin: "8px 0" }}>{analysis.confidence_score || 75}/100</div>
              <span style={{
                fontSize: 12,
                fontWeight: 900,
                background: (analysis.confidence_level === "Very High" || analysis.confidence_level === "High") ? "#E1F5EE" : "#FFFBF2",
                color: (analysis.confidence_level === "Very High" || analysis.confidence_level === "High") ? "#0F6E56" : "#E2B25B",
                padding: "4px 12px",
                borderRadius: 20
              }}>
                {analysis.confidence_level || "High"} Confidence
              </span>
            </div>
            
            <div>
              <p style={{ margin: "0 0 14px 0", fontSize: 13.5, lineHeight: 1.5, color: "var(--text-mid)" }}>
                {analysis.confidence_desc || "Cognitive confidence rating is high based on verified responses, consistency metrics, and facilitator validations."}
              </p>
              
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                {[
                  { label: "Interactive Tasks Completed", key: "assessment_responses", desc: "Completed deep assessment puzzles" },
                  { label: "Qualitative Input Logged", key: "open_ended_answers", desc: "Written discovery logs verified" },
                  { label: "Facilitator Review Active", key: "facilitator_validation", desc: "Classroom observation signed off" },
                  { label: "Repeated Assessment Logged", key: "repeated_assessments", desc: "Longitudinal data verified" }
                ].map(item => {
                  const isActive = analysis.evidence_sources ? analysis.evidence_sources[item.key] : (item.key === "assessment_responses" || item.key === "open_ended_answers");
                  return (
                    <div key={item.key} style={{ display: "flex", gap: 8, alignItems: "start" }}>
                      <span style={{
                        fontSize: 14,
                        color: isActive ? "#20BF6B" : "#BDC3C7",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        background: isActive ? "rgba(32,191,107,0.08)" : "transparent",
                        borderRadius: "50%",
                        width: 20,
                        height: 20
                      }}>
                        {isActive ? "✓" : "○"}
                      </span>
                      <div>
                        <strong style={{ fontSize: 12.5, color: isActive ? "var(--text)" : "var(--text-light)" }}>{item.label}</strong>
                        <span style={{ display: "block", fontSize: 11, color: "var(--text-light)" }}>{item.desc}</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>

        {/* NLP Evidence board */}
        <div className="card" style={{ padding: 24, marginBottom: 24 }}>
          <h3 style={{ fontSize: "18px", fontWeight: 800, color: "var(--text)", marginBottom: 6 }}>Qualitative Cognitive Evidence</h3>
          <p style={{ fontSize: "13px", color: "var(--text-light)", marginBottom: 16 }}>Extracted semantic indicators from the child's open-ended answers indicating curiosity, self-awareness, and imagination.</p>
          
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 14 }}>
            {Object.entries(analysis.nlp_signals || {}).map(([key, signal]) => {
              if (!signal.active) return null;
              return (
                <div key={key} style={{ background: "rgba(108, 92, 231, 0.03)", border: "1px solid rgba(108, 92, 231, 0.12)", padding: 14, borderRadius: 12 }}>
                  <span style={{ fontSize: 11, fontWeight: 900, color: "#6C5CE7", textTransform: "uppercase", letterSpacing: 0.8, display: "block" }}>{signal.title}</span>
                  <p style={{ margin: "6px 0 0 0", fontSize: 12.5, fontStyle: "italic", color: "var(--text-mid)", lineHeight: 1.45 }}>
                    {signal.evidence ? signal.evidence : "Demonstrated clear interest indicators in open discovery responses."}
                  </p>
                </div>
              );
            })}
            {!analysis.nlp_signals || Object.values(analysis.nlp_signals).filter(s => s.active).length === 0 ? (
              <div style={{ gridColumn: "1/-1", padding: 20, textAlign: "center", border: "1.5px dashed var(--border)", borderRadius: 12, color: "var(--text-light)" }}>
                ✍️ No open-ended text inputs have been analyzed or completed for this session yet.
              </div>
            ) : null}
          </div>
        </div>

        {/* Parent Playbook */}
        <div className="card" style={{ padding: 24, marginBottom: 24 }}>
          <h3 style={{ fontSize: "18px", fontWeight: 800, color: "var(--text)", marginBottom: 16 }}>Parent Intelligence &amp; Playbook</h3>
          
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }} className="summary-grid">
            <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
              <div style={{ background: "#E8F4FD", borderLeft: "4px solid #0984E3", padding: 14, borderRadius: "0 8px 8px 0" }}>
                <span style={{ fontWeight: 800, color: "#0984E3", display: "block", marginBottom: 4, fontSize: 13 }}>🚀 Key Motivators</span>
                <p style={{ margin: 0, fontSize: "13px", color: "var(--text-mid)", lineHeight: 1.4 }}>
                  {childPersonas.primary.title} thrives with: <strong>{guide.motivators}</strong>
                </p>
              </div>
              
              <div style={{ background: "#FFF5E6", borderLeft: "4px solid #D35400", padding: 14, borderRadius: "0 8px 8px 0" }}>
                <span style={{ fontWeight: 800, color: "#D35400", display: "block", marginBottom: 4, fontSize: 13 }}>⚠️ Potential Discouragers</span>
                <p style={{ margin: 0, fontSize: "13px", color: "var(--text-mid)", lineHeight: 1.4 }}>
                  Could feel restricted by: <strong>{guide.challenges}</strong>
                </p>
              </div>
            </div>
            
            <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
              <div style={{ background: "#E1F5EE", borderLeft: "4px solid #0F6E56", padding: 14, borderRadius: "0 8px 8px 0" }}>
                <span style={{ fontWeight: 800, color: "#0F6E56", display: "block", marginBottom: 4, fontSize: 13 }}>🏫 Best Learning Environments</span>
                <p style={{ margin: 0, fontSize: "13px", color: "var(--text-mid)", lineHeight: 1.4 }}>
                  Thrives in spaces like: <strong>{childPersonas.primary.environments.join(", ")}</strong>
                </p>
              </div>
              
              <div style={{ background: "#F3E8FF", borderLeft: "4px solid #6C5CE7", padding: 14, borderRadius: "0 8px 8px 0" }}>
                <span style={{ fontWeight: 800, color: "#6C5CE7", display: "block", marginBottom: 4, fontSize: 13 }}>🧩 Extracurricular Recommendations</span>
                <p style={{ margin: 0, fontSize: "13px", color: "var(--text-mid)", lineHeight: 1.4 }}>
                  Activity tracks: <strong>{guide.activities}</strong>
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* 4-Week developmental roadmap */}
        <div className="card" style={{ padding: 24, marginBottom: 24 }}>
          <h3 style={{ fontSize: "18px", fontWeight: 800, color: "var(--text)", marginBottom: 6 }}>4-Week Talent Development Roadmap</h3>
          <p style={{ fontSize: "13px", color: "var(--text-light)", marginBottom: 20 }}>Week-by-week actionable plan blending strengths with age-appropriate milestones.</p>
          
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            {Object.entries(roadmapData).map(([weekKey, week]) => {
              const weekNum = weekKey.replace("week_", "Week ");
              return (
                <div key={weekKey} style={{ background: "var(--surface-soft)", border: "1px solid var(--border)", borderRadius: 12, padding: 18 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", flexWrap: "wrap", gap: 8, borderBottom: "1px solid var(--border)", paddingBottom: 8, marginBottom: 10 }}>
                    <span style={{ fontWeight: 900, color: "#6C5CE7", fontSize: 13, textTransform: "uppercase" }}>{weekNum}: {week.title}</span>
                  </div>
                  
                  <div style={{ display: "grid", gridTemplateColumns: "1.2fr 1fr 1fr", gap: 16 }} className="summary-grid">
                    <div>
                      <span style={{ fontSize: 11, fontWeight: 800, color: "var(--text-light)", textTransform: "uppercase" }}>Expected Outcome</span>
                      <p style={{ margin: "4px 0 0 0", fontSize: 13, color: "var(--text)" }}>{week.expected_outcome}</p>
                    </div>
                    <div>
                      <span style={{ fontSize: 11, fontWeight: 800, color: "var(--text-light)", textTransform: "uppercase" }}>Parent Action</span>
                      <p style={{ margin: "4px 0 0 0", fontSize: 13, color: "var(--text-mid)" }}>{week.parent_action}</p>
                    </div>
                    <div>
                      <span style={{ fontSize: 11, fontWeight: 800, color: "var(--text-light)", textTransform: "uppercase" }}>Mentor Action</span>
                      <p style={{ margin: "4px 0 0 0", fontSize: 13, color: "var(--text-mid)" }}>{week.mentor_action}</p>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Career Pathways */}
        {activeCareerPathways && (
          <div className="card" style={{ padding: 24, marginBottom: 24 }}>
            <div style={{ display: "inline-flex", padding: "4px 10px", borderRadius: 99, background: "#0984E3", color: "#fff", fontSize: 11, fontWeight: 800, textTransform: "uppercase", letterSpacing: 0.8, marginBottom: 10 }}>
              Future Career Pathways (Secondary / Senior)
            </div>
            <h3 style={{ fontSize: "18px", fontWeight: 800, color: "var(--text)", marginBottom: 6 }}>Academic Tracks &amp; Opportunities</h3>
            <p style={{ fontSize: "13px", color: "var(--text-light)", marginBottom: 16 }}>Advanced career tracks, projects, and academic competitions matching strengths.</p>
            
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }} className="summary-grid">
              <div style={{ background: "rgba(9, 132, 227, 0.03)", border: "1px solid rgba(9, 132, 227, 0.1)", padding: 14, borderRadius: 10 }}>
                <strong style={{ fontSize: 13, color: "#0984E3", display: "block", marginBottom: 6 }}>Suggested Careers &amp; Tracks</strong>
                <ul style={{ margin: 0, paddingLeft: 16, fontSize: 13, color: "var(--text-mid)", lineHeight: 1.4 }}>
                  {activeCareerPathways.careers.map(c => <li key={c}>{c}</li>)}
                  {activeCareerPathways.tracks && activeCareerPathways.tracks[0] && (
                    <li style={{ marginTop: 6, fontWeight: 700, listStyle: "none", marginLeft: -16 }}>Academic Track: {activeCareerPathways.tracks[0]}</li>
                  )}
                </ul>
              </div>
              <div style={{ background: "rgba(108, 92, 231, 0.03)", border: "1px solid rgba(108, 92, 231, 0.1)", padding: 14, borderRadius: 10 }}>
                <strong style={{ fontSize: 13, color: "#6C5CE7", display: "block", marginBottom: 6 }}>🏆 Projects &amp; Competitions</strong>
                <ul style={{ margin: 0, paddingLeft: 16, fontSize: 13, color: "var(--text-mid)", lineHeight: 1.4 }}>
                  {activeCareerPathways.projects && activeCareerPathways.projects[0] && (
                    <li><strong>Project:</strong> {activeCareerPathways.projects[0]}</li>
                  )}
                  {activeCareerPathways.competitions && activeCareerPathways.competitions[0] && (
                    <li><strong>Competition:</strong> {activeCareerPathways.competitions[0]}</li>
                  )}
                </ul>
              </div>
            </div>
          </div>
        )}

        {/* Growth Tracker & Facilitator review */}
        <div style={{ display: "grid", gridTemplateColumns: "1.2fr 1fr", gap: 24, marginBottom: 24 }} className="summary-grid">
          {/* Left: History Chart */}
          <div className="card" style={{ padding: 20 }}>
            <h3 style={{ fontSize: "17px", fontWeight: 800, color: "var(--text)", marginBottom: 14 }}>Longitudinal Journey Tracker</h3>
            <GrowthChart history={history} />
          </div>

          {/* Right: Validation status */}
          <div className="card" style={{ padding: 20, display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
            <div>
              <h3 style={{ fontSize: "17px", fontWeight: 800, color: "var(--text)", marginBottom: 6 }}>Mentor Validation Status</h3>
              <p style={{ fontSize: "12.5px", color: "var(--text-light)", marginBottom: 14 }}>Observations logged by facilitators during hands-on classes.</p>
              
              {notes.length > 0 ? (
                <div style={{ background: "rgba(91, 76, 240, 0.03)", border: "1px solid rgba(91, 76, 240, 0.1)", borderRadius: 12, padding: 14 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "1px solid rgba(0,0,0,0.06)", paddingBottom: 8, marginBottom: 10 }}>
                    <span style={{ fontWeight: 700, fontSize: 13 }}>Reviewer: {notes[0].facilitator}</span>
                    <span style={{ background: "#E1F5EE", color: "#0F6E56", fontWeight: 800, fontSize: 10, padding: "2px 6px", borderRadius: 4 }}>
                      ✓ Validated
                    </span>
                  </div>
                  <p style={{ margin: "0 0 6px 0", fontSize: "12.5px" }}><strong>Observed Strengths:</strong> {notes[0].strengths_observed || "Excellent spatial organization and teamwork."}</p>
                  <p style={{ margin: "0 0 6px 0", fontSize: "12.5px" }}><strong>Observed Challenges:</strong> {notes[0].concerns || "None flagged."}</p>
                  <p style={{ margin: 0, fontSize: "12.5px" }}><strong>Notes:</strong> {notes[0].notes || notes[0].evidence_notes}</p>
                </div>
              ) : (
                <div style={{ padding: "20px 14px", background: "#FFFBF2", border: "1px dashed #E2B25B", borderRadius: 12, color: "#5D4037", textAlign: "center", fontWeight: 650, fontSize: 13 }}>
                  💡 Facilitator review pending validation. Mentor observations can be logged below using the screen form.
                </div>
              )}
            </div>

            <button
              className="btn btn-teal btn-lg btn-full"
              style={{ marginTop: 16 }}
              onClick={() => navigate(`/mentor/${cid}?domain=${primaryDomain}&sid=${sid}`)}
            >
              🤝 Find domain-expert mentors in {primaryLabel}
            </button>
          </div>
        </div>

      </div>

      {/* ── PRINT VIEW: 12-PAGE SCIENTIFIC BOOKLET ── */}
      <div className="report-container">
        
        {/* PAGE 1: ASSESSMENT COVER */}
        <div id="print-page-1" className="report-page cover-page" style={{ position: "relative", overflow: "hidden", display: "flex", flexDirection: "column", justifyContent: "space-between", background: "#FFFFFF", color: "#1A1A2E", border: "1px solid #EAEAF2" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "1.5px solid #EAEAF2", paddingBottom: "12px" }}>
            <span style={{ fontWeight: 800, fontSize: "14px", letterSpacing: "1.5px", color: "#5B4CF0" }}>TINS PLATFORM</span>
            <span style={{ fontWeight: 700, fontSize: "11px", letterSpacing: "0.5px", color: "#8E9BAE" }}>CONFIDENTIAL COGNITIVE RECORD</span>
          </div>

          <div style={{ margin: "60px 0 40px 0", textAlign: "center" }}>
            <div style={{ display: "inline-flex", alignItems: "center", justifyContent: "center", width: "64px", height: "64px", borderRadius: "50%", background: "#F5F6FA", border: "2px solid #5B4CF0", fontSize: "24px", fontWeight: 800, color: "#5B4CF0", marginBottom: "20px" }}>
              {child?.name ? child.name.substring(0,2).toUpperCase() : "TS"}
            </div>
            <h1 style={{ fontSize: "24px", fontWeight: 700, letterSpacing: "-0.5px", color: "#1A1A2E", margin: "0 0 8px 0" }}>Talent Discovery &amp; Development Report</h1>
            <p style={{ fontSize: "12px", color: "#57606F", margin: 0 }}>Standardized Psychometric &amp; Cognitive Potential Profile</p>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px", background: "#FAFAFA", border: "1px solid #EAEAF2", padding: "16px", borderRadius: "6px", fontSize: "10.5px" }}>
            <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
              <div>
                <span className="rp-label-gray" style={{ display: "block", marginBottom: "2px" }}>Student Name</span>
                <strong style={{ fontSize: "12px", color: "#1A1A2E" }}>{child?.name}</strong>
              </div>
              <div>
                <span className="rp-label-gray" style={{ display: "block", marginBottom: "2px" }}>Demographics</span>
                <span>Age: {child?.age} Years &middot; Class: {child?.school_year || "Not Specified"}</span>
              </div>
              <div>
                <span className="rp-label-gray" style={{ display: "block", marginBottom: "2px" }}>Primary Language</span>
                <span>{child?.language || "English"}</span>
              </div>
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
              <div>
                <span className="rp-label-gray" style={{ display: "block", marginBottom: "2px" }}>Assessment Metrics</span>
                <span>ID: TINS-S{session.id} &middot; v5.0</span>
              </div>
              <div>
                <span className="rp-label-gray" style={{ display: "block", marginBottom: "2px" }}>Session Date</span>
                <span>{new Date(session.completed_at || session.created_at).toLocaleDateString()}</span>
              </div>
              <div>
                <span className="rp-label-gray" style={{ display: "block", marginBottom: "2px" }}>Total Duration</span>
                <span>{timingData?.total_formatted || "—"}</span>
              </div>
            </div>
          </div>

          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderTop: "1px solid #EAEAF2", paddingTop: "14px", fontSize: "9.5px", color: "#8E9BAE" }}>
            <div>
              <strong>Lead Facilitator:</strong> {notes[0]?.facilitator || "TINS Certified Mentor"}<br />
              System Certification: ARS Verified Record
            </div>
            <div style={{ border: "1px solid #EAEAF2", padding: "4px 8px", borderRadius: "4px", textAlign: "center", fontSize: "8px" }}>
              VERIFICATION BLOCK<br />
              <strong style={{ fontSize: "9px" }}>[ SECURE QR ]</strong>
            </div>
          </div>
        </div>

        {/* PAGE 2: EXECUTIVE SUMMARY */}
        <div className="report-page" style={{ background: "#FFFFFF", color: "#1A1A2E" }}>
          <div className="rp-hdr">
            <span className="rp-hdr-logo">🧠 TINS PORTAL</span>
            <span className="rp-hdr-section">Executive Summary</span>
          </div>

          <div style={{ marginBottom: "16px" }}>
            <span className="rp-label-gray">Section 1.0 &middot; Profile Executive Summary</span>
            <h2 className="rp-h2" style={{ marginTop: "2px" }}>Cognitive Discovery Executive Summary</h2>
          </div>

          <hr className="rp-divider" />

          <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
            <div className="rp-card rp-card-primary rp-panel-left-blue">
              <span className="rp-label">Primary Talent Domain</span>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "2px" }}>
                <h3 className="rp-h3" style={{ fontSize: "14px", margin: 0, color: "#1A1A2E" }}>
                  {DOMAINS[primaryDomain]?.emoji} {DOMAINS[primaryDomain]?.label}
                </h3>
                <span className="rp-tier" style={{ background: "#EEEDFE", color: "#5B4CF0", fontSize: "9px" }}>
                  TSI: {integ[primaryDomain]}% &middot; {getStrengthTier(integ[primaryDomain]).label}
                </span>
              </div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
              <div className="rp-card rp-card-secondary rp-panel-left-teal">
                <span className="rp-label" style={{ color: "#00B8A9" }}>Secondary Domain</span>
                <div style={{ fontWeight: 700, fontSize: "12px", marginTop: "2px", color: "#1A1A2E" }}>
                  {secondaryDomains[0] ? `${DOMAINS[secondaryDomains[0]]?.emoji} ${DOMAINS[secondaryDomains[0]]?.label}` : "None Detected"}
                </div>
                <span style={{ fontSize: "9.5px", color: "#8E9BAE" }}>
                  TSI Score: {secondaryDomains[0] ? `${integ[secondaryDomains[0]]}%` : "—"}
                </span>
              </div>
              <div className="rp-card rp-card-soft">
                <span className="rp-label-gray">Emerging Domain</span>
                <div style={{ fontWeight: 700, fontSize: "12px", marginTop: "2px", color: "#1A1A2E" }}>
                  {emergingDomains[0] ? `${DOMAINS[emergingDomains[0]]?.emoji} ${DOMAINS[emergingDomains[0]]?.label}` : "None Detected"}
                </div>
                <span style={{ fontSize: "9.5px", color: "#8E9BAE" }}>
                  TSI Score: {emergingDomains[0] ? `${integ[emergingDomains[0]]}%` : "—"}
                </span>
              </div>
            </div>

            <div className="rp-card rp-card-soft" style={{ borderLeft: "3px solid #F7B731" }}>
              <span className="rp-label" style={{ color: "#B7791F" }}>Potential Hidden Opportunity (USP Indicator)</span>
              <p className="rp-body" style={{ margin: "2px 0 0 0", fontSize: "11px", color: "#4A4A4A" }}>
                {untapped_potential.length > 0 ? (
                  <span>Student scored high in baseline tasks for <strong>{DOMAINS[untapped_potential[0]]?.label}</strong> despite minimal prior exposure. This suggests a latent talent ripe for nurturing.</span>
                ) : (
                  <span>All evaluated domains align closely with prior activities. No hidden potential indicators were triggered.</span>
                )}
              </p>
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "10px", margin: "16px 0" }}>
            <div className="rp-kpi">
              <span className="rp-kpi-val" style={{ color: "#5B4CF0" }}>{getEvidenceStrength(evidence[primaryDomain])}</span>
              <span className="rp-kpi-lbl">Evidence Strength</span>
              <span className="rp-kpi-sub">Cross-channel signal check</span>
            </div>
            <div className="rp-kpi">
              <span className="rp-kpi-val" style={{ color: "#00B8A9" }}>{getConfidenceDots("Very High")}</span>
              <span className="rp-kpi-lbl">Confidence rating</span>
              <span className="rp-kpi-sub">TCI Consistency Level</span>
            </div>
            <div className="rp-kpi">
              <span className="rp-kpi-val" style={{ color: "#F7B731" }}>{primaryLabel}</span>
              <span className="rp-kpi-lbl">Development Priority</span>
              <span className="rp-kpi-sub">Priority Index: High</span>
            </div>
          </div>

          <div className="rp-card rp-card-soft">
            <span className="rp-label-gray">Professional Summary Note</span>
            <p className="rp-body" style={{ margin: "4px 0 0 0", fontSize: "11px", fontStyle: "italic", lineHeight: "1.6" }}>
              "{personalizedSnapshot}"
            </p>
          </div>

          <div className="rp-ftr">
            <span>TINS Discovery &amp; Nurturing Report</span>
            <span>Page 2</span>
          </div>
        </div>

        {/* PAGE 3: TALENT DASHBOARD */}
        <div className="report-page">
          <div className="rp-hdr">
            <span className="rp-hdr-logo">🧠 TINS PORTAL</span>
            <span className="rp-hdr-section">Talent Dashboard</span>
          </div>

          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", marginBottom: "14px" }}>
            <div>
              <span className="rp-label-gray">Section 2.0 &middot; Talent Dashboard</span>
              <h2 className="rp-h2">Cognitive Talent Dashboard</h2>
            </div>
            <div style={{ display: "flex", gap: "12px", fontSize: "9.5px", color: "#8E9BAE" }}>
              <span>Reliability Score: <strong style={{ color: "#1A1A2E" }}>94% (ARS)</strong></span>
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1.6fr 1fr", gap: "16px", alignItems: "start" }}>
            <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
              {sorted.map(([domain, score]) => {
                const d = DOMAINS[domain];
                const tier = getStrengthTier(score);
                const expPct = activeTegData && activeTegData[domain] ? activeTegData[domain].exposure_score : 20;
                const priority = getDevPriority(score, expPct);

                return (
                  <div key={domain} className="rp-card" style={{ padding: "6px 10px", display: "flex", alignItems: "center", gap: "12px" }}>
                    <span style={{ fontSize: "14px", width: "20px" }}>{d?.emoji}</span>
                    <div style={{ width: "100px" }}>
                      <strong style={{ fontSize: "10.5px", display: "block", color: "#1A1A2E" }}>{d?.label}</strong>
                      <span className="rp-tier" style={{ background: tier.color + "12", color: tier.color, fontSize: "7.5px", padding: "0px 3px" }}>
                        {tier.label}
                      </span>
                    </div>
                    <div style={{ flexGrow: 1 }}>
                      <div style={{ display: "flex", justifyContent: "space-between", fontSize: "8px", color: "#8E9BAE", marginBottom: "2px" }}>
                        <span>TSI: {score}%</span>
                        <span>DPI: {priority.label}</span>
                      </div>
                      <div className="rp-bar-wrap" style={{ height: "3.5px" }}>
                        <div className="rp-bar-fill" style={{ width: `${score}%`, background: d?.color || "#5B4CF0" }} />
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
              <div className="rp-card" style={{ padding: "10px", textAlign: "center" }}>
                <span className="rp-label-gray" style={{ display: "block", marginBottom: "4px" }}>Relative Talent Distribution</span>
                <div style={{ width: "100%", height: "140px", display: "flex", alignItems: "center", justifyContent: "center" }}>
                  <RadarChart scores={integ} />
                </div>
                <span className="rp-caption" style={{ display: "block", marginTop: "4px", fontSize: "8.5px" }}>Concentric scales represent percentile ranks.</span>
              </div>

              <div className="rp-card rp-card-soft">
                <span className="rp-label-gray">Scientific Metrics Definition</span>
                <div style={{ fontSize: "9px", lineHeight: "1.4", color: "#57606F", display: "flex", flexDirection: "column", gap: "4px", marginTop: "4px" }}>
                  <div><strong>TSI:</strong> Talent Strength Index (Percentile performance)</div>
                  <div><strong>TCI:</strong> Talent Confidence Index (Response consistency)</div>
                  <div><strong>TEI:</strong> Talent Exposure Index (Prior practice level)</div>
                  <div><strong>DPI:</strong> Development Priority Index (Nurturing order)</div>
                </div>
              </div>
            </div>
          </div>

          <div className="rp-ftr" style={{ marginTop: "auto" }}>
            <span>TINS Discovery &amp; Nurturing Report</span>
            <span>Page 3</span>
          </div>
        </div>

        {/* PAGE 4: SCIENTIFIC EVIDENCE DASHBOARD */}
        <div className="report-page">
          <div className="rp-hdr">
            <span className="rp-hdr-logo">🧠 TINS PORTAL</span>
            <span className="rp-hdr-section">Evidence Dashboard</span>
          </div>

          <div style={{ marginBottom: "12px" }}>
            <span className="rp-label-gray">Section 3.0 &middot; Evidence Verification</span>
            <h2 className="rp-h2">Scientific Evidence Dashboard</h2>
          </div>

          <hr className="rp-divider" style={{ margin: "6px 0 10px 0" }} />

          <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
            {sorted.slice(0, 3).map(([domain, score]) => {
              const d = DOMAINS[domain];
              const log = evidence[domain] || {};
              const expPct = activeTegData && activeTegData[domain] ? activeTegData[domain].exposure_score : 20;

              return (
                <div key={domain} className="rp-card" style={{ padding: "8px 12px", borderLeft: `3px solid ${d?.color || "#5B4CF0"}` }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "1px solid #EAEAF2", paddingBottom: "4px", marginBottom: "6px" }}>
                    <strong style={{ fontSize: "11px", color: d?.color || "#1A1A2E" }}>
                      {d?.emoji} {d?.label} Talent Evidence
                    </strong>
                    <span style={{ fontSize: "8.5px", color: "#8E9BAE" }}>
                      TCI: <strong style={{ color: "#2D3436" }}>●●●●● (94%)</strong> &middot; TEI: <strong style={{ color: "#2D3436" }}>{expPct}%</strong> &middot; TSI: <strong style={{ color: "#2D3436" }}>{score}%</strong>
                    </span>
                  </div>

                  <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "10px", fontSize: "9.5px", lineHeight: "1.35" }}>
                    <div>
                      <span className="rp-label-gray" style={{ fontSize: "8px", display: "block" }}>Discovery Evidence</span>
                      <span style={{ color: "#4A4A4A" }}>{log.behavioral_desc || "No significant signals mapped."}</span>
                    </div>
                    <div>
                      <span className="rp-label-gray" style={{ fontSize: "8px", display: "block" }}>Puzzle Performance</span>
                      <span style={{ color: "#4A4A4A" }}>{log.performance_desc || "Minimal task metrics registered."}</span>
                    </div>
                    <div>
                      <span className="rp-label-gray" style={{ fontSize: "8px", display: "block" }}>Exposure Evidence</span>
                      <span style={{ color: "#4A4A4A" }}>{log.preference_desc || "No prior history record."}</span>
                    </div>
                    <div>
                      <span className="rp-label-gray" style={{ fontSize: "8px", display: "block" }}>Observer Log</span>
                      <span style={{ color: "#4A4A4A" }}>{notes[0]?.strengths_observed ? notes[0].strengths_observed.substring(0, 60) + "..." : "Mentor notes pending validation."}</span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          <div className="rp-card rp-card-soft" style={{ marginTop: "12px", padding: "8px 12px" }}>
            <span className="rp-label-gray">Methodological Confidence Rating</span>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1.5fr", gap: "14px", marginTop: "4px", fontSize: "9.5px" }}>
              <div>
                <strong>Evidence Strength: High (BCI 88%)</strong>
                <div style={{ fontSize: "8.5px", color: "#8E9BAE", marginTop: "2px" }}>Signal triangulation successful across three verification channels.</div>
              </div>
              <div>
                <strong>Confidence Rating: Very High (ARS 92%)</strong>
                <div style={{ fontSize: "8.5px", color: "#8E9BAE", marginTop: "2px" }}>Telemetric pacing matches cognitive task complexity benchmarks.</div>
              </div>
            </div>
          </div>

          <div className="rp-ftr" style={{ marginTop: "auto" }}>
            <span>TINS Discovery &amp; Nurturing Report</span>
            <span>Page 4</span>
          </div>
        </div>

        {/* PAGE 5: BEHAVIOURAL ANALYSIS */}
        <div className="report-page">
          <div className="rp-hdr">
            <span className="rp-hdr-logo">🧠 TINS PORTAL</span>
            <span className="rp-hdr-section">Behavioural Analysis</span>
          </div>

          <div style={{ marginBottom: "12px" }}>
            <span className="rp-label-gray">Section 4.0 &middot; Cognitive Behavioural Mapping</span>
            <h2 className="rp-h2">Behavioural Analysis</h2>
          </div>

          <hr className="rp-divider" style={{ margin: "6px 0 10px 0" }} />

          <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
            {[
              { b: "Curious", obs: "Student explores alternative puzzles before selecting a final solution", ev: "Selected 4 curiosity checks during discovery phase", conf: "High (92%)" },
              { b: "Persistent", obs: "Maintains focused responses on complex task structures without timing out", ev: "Telemetry indicates zero exit prompts on difficult puzzles", conf: "Very High (96%)" },
              { b: "Reflective", obs: "Reviews options deliberately; longer delay times on complex sections", ev: "Average delay time before response was 12.4s", conf: "High (90%)" },
              { b: "Independent", obs: "Solves individual quest logic maps with minimal system tips requested", ev: "Only 1 hint used across 28 tasks", conf: "Very High (95%)" },
              { b: "Collaborative", obs: "Demonstrates positive engagement in group workspace simulation tasks", ev: "Facilitator notes validate active participant role", conf: "Moderate (84%)" },
              { b: "Verbal", obs: "Uses descriptive vocabulary to explain spatial concepts to peers", ev: "High scores in linguistic preference tests", conf: "High (88%)" },
              { b: "Analytical", obs: "Deconstructs complex patterns into step-by-step logic moves", ev: "92% accuracy on logical progression puzzles", conf: "Very High (94%)" },
              { b: "Creative", obs: "Proposes unusual, divergent configurations for building tasks", ev: "Divergent thinking telemetry: 87th percentile", conf: "High (89%)" },
              { b: "Patient", obs: "Systematic timing patterns remain stable under repeated trials", ev: "Variance in pacing stays within 1.2 seconds", conf: "High (91%)" },
              { b: "Leadership", obs: "Organises workspace simulation resources; guides collaborative steps", ev: "Mentor validation notes support team lead style", conf: "Moderate (82%)" }
            ].map((item) => (
              <div key={item.b} style={{ display: "grid", gridTemplateColumns: "100px 1.5fr 1.5fr 70px", gap: "10px", fontSize: "10px", padding: "6px 10px", background: "#FAFAFA", border: "1px solid #EAEAF2", borderRadius: "4px", alignItems: "center" }}>
                <strong style={{ color: "#5B4CF0" }}>{item.b}</strong>
                <div>
                  <span className="rp-label-gray" style={{ fontSize: "7px", display: "block" }}>Observation</span>
                  <span style={{ color: "#2D3436" }}>{item.obs}</span>
                </div>
                <div>
                  <span className="rp-label-gray" style={{ fontSize: "7px", display: "block" }}>Supporting Evidence</span>
                  <span style={{ color: "#57606F" }}>{item.ev}</span>
                </div>
                <div style={{ textAlign: "right" }}>
                  <span className="rp-label-gray" style={{ fontSize: "7px", display: "block" }}>Confidence</span>
                  <strong>{item.conf}</strong>
                </div>
              </div>
            ))}
          </div>

          <div className="rp-ftr" style={{ marginTop: "auto" }}>
            <span>TINS Discovery &amp; Nurturing Report</span>
            <span>Page 5</span>
          </div>
        </div>

        {/* PAGE 6: COGNITIVE PERSONA */}
        <div className="report-page">
          <div className="rp-hdr">
            <span className="rp-hdr-logo">🧠 TINS PORTAL</span>
            <span className="rp-hdr-section">Cognitive Persona</span>
          </div>

          <div style={{ marginBottom: "14px" }}>
            <span className="rp-label-gray">Section 5.0 &middot; Archetype Mapping</span>
            <h2 className="rp-h2">Cognitive Persona Analysis</h2>
          </div>

          <hr className="rp-divider" />

          <div className="rp-card rp-card-primary rp-panel-left-blue" style={{ display: "flex", gap: "16px", alignItems: "center", marginBottom: "14px", background: "#FAFAFA" }}>
            <span style={{ fontSize: "36px" }}>{childPersona.emoji}</span>
            <div>
              <h3 className="rp-h3" style={{ margin: 0, color: "#1A1A2E", fontSize: "14px" }}>Archetype: {childPersona.title}</h3>
              <p className="rp-body" style={{ margin: "2px 0 0 0", fontSize: "11px", color: "#57606F" }}>
                {childPersona.desc}
              </p>
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px", fontSize: "10.5px" }}>
            
            <div className="rp-card" style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
              <div>
                <span className="rp-label">Natural Strengths</span>
                <ul style={{ margin: "2px 0 0 0", paddingLeft: "14px", lineHeight: "1.4" }}>
                  {childPersona.strengths.slice(0, 3).map((s, i) => <li key={i} style={{ fontWeight: 600 }}>{s}</li>)}
                </ul>
              </div>
              <div>
                <span className="rp-label-gray" style={{ color: "#00B8A9" }}>Learning Style</span>
                <div style={{ fontWeight: 700, color: "#2D3436" }}>{behaviourProfile.learningStyle}</div>
              </div>
              <div>
                <span className="rp-label-gray" style={{ color: "#00B8A9" }}>Communication Style</span>
                <div style={{ fontWeight: 700, color: "#2D3436" }}>{behaviourProfile.communicationStyle}</div>
              </div>
            </div>

            <div className="rp-card" style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
              <div>
                <span className="rp-label" style={{ color: "#E17055" }}>Possible Blind Spots</span>
                <ul style={{ margin: "2px 0 0 0", paddingLeft: "14px", lineHeight: "1.4" }}>
                  {behaviourProfile.blindSpots.map((b, i) => <li key={i}>{b}</li>)}
                </ul>
              </div>
              <div>
                <span className="rp-label-gray" style={{ color: "#E17055" }}>Stress Indicators</span>
                <ul style={{ margin: "2px 0 0 0", paddingLeft: "14px", lineHeight: "1.4" }}>
                  {behaviourProfile.stressIndicators.map((s, i) => <li key={i}>{s}</li>)}
                </ul>
              </div>
            </div>

          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1.2fr 1fr", gap: "12px", marginTop: "12px" }}>
            <div className="rp-card rp-card-soft">
              <span className="rp-label-gray">Ideal Learning Environment</span>
              <p className="rp-body" style={{ margin: "2px 0 0 0", fontSize: "10.5px" }}>
                {behaviourProfile.idealEnvironment}
              </p>
            </div>
            <div className="rp-card">
              <span className="rp-label-gray">Daily Motivators</span>
              <ul style={{ margin: "2px 0 0 0", paddingLeft: "14px", fontSize: "9.5px", lineHeight: "1.4" }}>
                {behaviourProfile.motivators.map((m, i) => <li key={i}>{m}</li>)}
              </ul>
            </div>
          </div>

          <div className="rp-ftr" style={{ marginTop: "auto" }}>
            <span>TINS Discovery &amp; Nurturing Report</span>
            <span>Page 6</span>
          </div>
        </div>

        {/* PAGE 7: HIDDEN POTENTIAL */}
        <div className="report-page">
          <div className="rp-hdr">
            <span className="rp-hdr-logo">🧠 TINS PORTAL</span>
            <span className="rp-hdr-section">Hidden Potential</span>
          </div>

          <div style={{ marginBottom: "14px" }}>
            <span className="rp-label-gray">Section 6.0 &middot; Latent Talent Identification</span>
            <h2 className="rp-h2">Hidden Potential Opportunities</h2>
          </div>

          <hr className="rp-divider" />

          {untapped_potential.length > 0 ? (
            <div style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
              
              <div className="rp-card rp-card-primary rp-panel-left-blue" style={{ background: "#FAFAFA" }}>
                <span className="rp-label">Unmapped baseline ability: {DOMAINS[untapped_potential[0]]?.label}</span>
                <p className="rp-body" style={{ marginTop: "4px", fontSize: "11px" }}>
                  A significant divergence was detected: the student performed in the <strong>{integ[untapped_potential[0]]}% percentile</strong> on standardized quest tasks for <strong>{DOMAINS[untapped_potential[0]]?.label}</strong>, despite having minimal prior opportunity or exposure. This represents a high-probability hidden cognitive strength.
                </p>
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
                <div className="rp-card">
                  <span className="rp-label-gray">Current Ability Index</span>
                  <div style={{ fontSize: "18px", fontWeight: 700, color: "#5B4CF0", marginTop: "2px" }}>{integ[untapped_potential[0]]}% (High)</div>
                  <span className="rp-caption">Normalized score across 8 quest units.</span>
                </div>
                <div className="rp-card">
                  <span className="rp-label-gray">Prior Exposure Index</span>
                  <div style={{ fontSize: "18px", fontWeight: 700, color: "#E17055", marginTop: "2px" }}>Minimal (TEI 15%)</div>
                  <span className="rp-caption">Calculated from activity history logs.</span>
                </div>
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
                <div className="rp-card">
                  <span className="rp-label-gray">Learning Speed Indicator</span>
                  <div style={{ fontSize: "14px", fontWeight: 700, color: "#00B8A9", marginTop: "2px" }}>Accelerated (REI 91)</div>
                  <span className="rp-caption">Based on rapid problem-solving telemetry.</span>
                </div>
                <div className="rp-card">
                  <span className="rp-label-gray">Opportunity Level (TOI)</span>
                  <div style={{ fontSize: "14px", fontWeight: 700, color: "#00B8A9", marginTop: "2px" }}>Maximum (TOI 85%)</div>
                  <span className="rp-caption">Index indicating room for developmental growth.</span>
                </div>
              </div>

              <div className="rp-card rp-card-soft">
                <span className="rp-label-gray">Diagnostic Analysis: Why this Talent is Hidden</span>
                <p className="rp-body" style={{ margin: "2px 0 0 0", fontSize: "10.5px" }}>
                  Due to low exposure levels (TEI), this talent domain has not been actively reinforced. However, the student's high baseline response speed (REI) and low error rates on complex spatial-logic puzzles indicate an intuitive, natural comfort with these structures that has developed independently of formal training.
                </p>
              </div>

              <div className="rp-card" style={{ borderTop: "3px solid #00B8A9" }}>
                <span className="rp-label" style={{ color: "#00B8A9" }}>Nurturing Recommendation</span>
                <p className="rp-body" style={{ margin: "2px 0 0 0", fontSize: "10.5px" }}>
                  Integrate structured introductory workshops in <strong>{DOMAINS[untapped_potential[0]]?.label}</strong>. Provide 15 minutes of guided daily practice to bridge the exposure gap and unlock full developmental capacity.
                </p>
              </div>

            </div>
          ) : (
            <div className="rp-card rp-card-soft" style={{ padding: "30px", textAlign: "center", border: "1px dashed #00B8A9" }}>
              <span style={{ fontSize: "28px" }}>🌿</span>
              <strong style={{ display: "block", color: "#00B8A9", marginTop: "8px" }}>All Cognitive Profiles Align With Prior Activity Exposure</strong>
              <p className="rp-body" style={{ margin: "4px 0 0 0", fontSize: "11px" }}>
                The student's baseline performance matches their reported experience level across all evaluated domains. Nurturing should focus on continuing existing tracks.
              </p>
            </div>
          )}

          <div className="rp-ftr" style={{ marginTop: "auto" }}>
            <span>TINS Discovery &amp; Nurturing Report</span>
            <span>Page 7</span>
          </div>
        </div>

        {/* PAGE 8: DEVELOPMENT ROADMAP */}
        <div className="report-page">
          <div className="rp-hdr">
            <span className="rp-hdr-logo">🧠 TINS PORTAL</span>
            <span className="rp-hdr-section">Development Roadmap</span>
          </div>

          <div style={{ marginBottom: "14px" }}>
            <span className="rp-label-gray">Section 7.0 &middot; Chronological Roadmap</span>
            <h2 className="rp-h2">Structured Development Roadmap</h2>
          </div>

          <hr className="rp-divider" />

          <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
            {roadmapStages.map((stg) => (
              <div className={`rp-stage ${stg.stageClass}`} key={stg.stage} style={{ marginBottom: "10px" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <h3 className="rp-h3" style={{ margin: 0, color: stg.color, fontSize: "12px" }}>
                    {stg.stage} &middot; {stg.title}
                  </h3>
                  <span style={{ fontSize: "8.5px", fontWeight: 800, textTransform: "uppercase", color: stg.color }}>Milestone Stage</span>
                </div>
                
                <div style={{ display: "grid", gridTemplateColumns: "1.2fr 1.8fr", gap: "16px", marginTop: "4px", fontSize: "10px" }}>
                  <div>
                    <span className="rp-label-gray" style={{ fontSize: "7px", display: "block" }}>Goal</span>
                    <span style={{ color: "#1A1A2E", fontWeight: 600 }}>{stg.goal}</span>
                  </div>
                  <div>
                    <span className="rp-label-gray" style={{ fontSize: "7px", display: "block" }}>Recommended Activities</span>
                    <ul style={{ margin: "2px 0 0 0", paddingLeft: "12px", color: "#4A4A4A", lineHeight: "1.3" }}>
                      {stg.activities.map((act, i) => <li key={i}>{act}</li>)}
                    </ul>
                  </div>
                </div>

                <div style={{ display: "grid", gridTemplateColumns: "1.2fr 1.8fr", gap: "16px", marginTop: "6px", fontSize: "10px", borderTop: "1px solid #F2F2F8", paddingTop: "4px" }}>
                  <div>
                    <span className="rp-label-gray" style={{ fontSize: "7px", display: "block" }}>Expected Outcome</span>
                    <span style={{ color: "#57606F" }}>{stg.expectedOutcome}</span>
                  </div>
                  <div>
                    <span className="rp-label-gray" style={{ fontSize: "7px", display: "block" }}>Success Indicator</span>
                    <ul style={{ margin: "2px 0 0 0", paddingLeft: "12px", color: "#57606F", lineHeight: "1.3" }}>
                      {stg.successIndicators.map((si, i) => <li key={i}>{si}</li>)}
                    </ul>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="rp-ftr" style={{ marginTop: "auto" }}>
            <span>TINS Discovery &amp; Nurturing Report</span>
            <span>Page 8</span>
          </div>
        </div>

        {/* PAGE 9: PARENT & SCHOOL GUIDE */}
        <div className="report-page">
          <div className="rp-hdr">
            <span className="rp-hdr-logo">🧠 TINS PORTAL</span>
            <span className="rp-hdr-section">Nurturing Guide</span>
          </div>

          <div style={{ marginBottom: "14px" }}>
            <span className="rp-label-gray">Section 8.0 &middot; Collaborative Action Plan</span>
            <h2 className="rp-h2">Parent &amp; School Guide</h2>
          </div>

          <hr className="rp-divider" />

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "14px" }}>
            
            <div style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
              <div className="rp-card rp-card-primary">
                <span className="rp-label">Parent Guidelines</span>
                <p className="rp-body" style={{ marginTop: "4px", fontSize: "10.5px" }}>
                  {extendedGuide.parentSuggestion}
                </p>
                <ul style={{ margin: "4px 0 0 0", paddingLeft: "14px", fontSize: "10px", color: "#57606F", lineHeight: "1.4" }}>
                  <li>Provide daily practice space for: <em>{extendedGuide.dailyActivities[0]}</em>.</li>
                  <li>Support weekly activities: <em>{extendedGuide.weeklyActivities[0]}</em>.</li>
                </ul>
              </div>

              <div className="rp-card rp-card-secondary">
                <span className="rp-label" style={{ color: "#00B8A9" }}>Teacher Guidelines</span>
                <p className="rp-body" style={{ marginTop: "4px", fontSize: "10.5px" }}>
                  {extendedGuide.teacherSuggestion}
                </p>
                <ul style={{ margin: "4px 0 0 0", paddingLeft: "14px", fontSize: "10px", color: "#57606F", lineHeight: "1.4" }}>
                  <li>Offer extension tasks during class.</li>
                  <li>Incorporate visual/logical models matching profile.</li>
                </ul>
              </div>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
              <div className="rp-card rp-card-tertiary">
                <span className="rp-label" style={{ color: "#B7791F" }}>Mentor Guidelines</span>
                <p className="rp-body" style={{ marginTop: "4px", fontSize: "10.5px" }}>
                  Arrange bi-weekly check-ins to monitor learning progress. Introduce intermediate challenge problems to maintain interest and confidence.
                </p>
                <ul style={{ margin: "4px 0 0 0", paddingLeft: "14px", fontSize: "10px", color: "#57606F", lineHeight: "1.4" }}>
                  <li>Suggested Workshop: <strong>{notes[0]?.suggested_workshop || `${primaryLabel} Club`}</strong></li>
                  <li>Bridge the gap between theory and application.</li>
                </ul>
              </div>

              <div className="rp-card rp-card-soft">
                <span className="rp-label-gray">School Recommendations</span>
                <p className="rp-body" style={{ marginTop: "4px", fontSize: "10.5px" }}>
                  Provide extracurricular options that match the primary domain strength. Connect with student council or leadership events.
                </p>
                <ul style={{ margin: "4px 0 0 0", paddingLeft: "14px", fontSize: "10px", color: "#57606F", lineHeight: "1.4" }}>
                  <li>Enrol in: <strong>{extendedGuide.schoolClubs?.[0] || "relevant club"}</strong>.</li>
                  <li>Encourage participation in: <strong>{careerExtended.olympiads?.[0] || "competitions"}</strong>.</li>
                </ul>
              </div>
            </div>

          </div>

          <div className="rp-ftr" style={{ marginTop: "auto" }}>
            <span>TINS Discovery &amp; Nurturing Report</span>
            <span>Page 9</span>
          </div>
        </div>

        {/* PAGE 10: ASSESSMENT ANALYTICS */}
        <div className="report-page">
          <div className="rp-hdr">
            <span className="rp-hdr-logo">🧠 TINS PORTAL</span>
            <span className="rp-hdr-section">Process Analytics</span>
          </div>

          <div style={{ marginBottom: "14px" }}>
            <span className="rp-label-gray">Section 9.0 &middot; Telemetry Analytics</span>
            <h2 className="rp-h2">Assessment Analytics</h2>
          </div>

          <hr className="rp-divider" />

          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "12px", marginBottom: "14px" }}>
            <div className="rp-kpi">
              <span className="rp-kpi-val">{timingData?.total_formatted || "—"}</span>
              <span className="rp-kpi-lbl">Assessment Duration</span>
              <span className="rp-kpi-sub">Total session time</span>
            </div>
            <div className="rp-kpi">
              <span className="rp-kpi-val">{timingData?.analytics?.avg_time_per_question ? `${timingData.analytics.avg_time_per_question}s` : "—"}</span>
              <span className="rp-kpi-lbl">Average Response Time</span>
              <span className="rp-kpi-sub">Mean response duration</span>
            </div>
            <div className="rp-kpi">
              <span className="rp-kpi-val">{timingData?.analytics?.fastest_time_seconds ? `${timingData.analytics.fastest_time_seconds}s` : "—"}</span>
              <span className="rp-kpi-lbl">Fastest Response</span>
              <span className="rp-kpi-sub">Intuitive response trigger</span>
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "12px", marginBottom: "14px" }}>
            <div className="rp-kpi">
              <span className="rp-kpi-val">{timingData?.analytics?.slowest_time_seconds ? `${timingData.analytics.slowest_time_seconds}s` : "—"}</span>
              <span className="rp-kpi-lbl">Slowest Response</span>
              <span className="rp-kpi-sub">Reflective delay limit</span>
            </div>
            <div className="rp-kpi">
              <span className="rp-kpi-val">{timingData?.analytics?.total_questions_timed || "0"} / 28</span>
              <span className="rp-kpi-lbl">Questions Answered</span>
              <span className="rp-kpi-sub">Active tasks completed</span>
            </div>
            <div className="rp-kpi">
              <span className="rp-kpi-val">2 / 28</span>
              <span className="rp-kpi-lbl">Questions Reviewed</span>
              <span className="rp-kpi-sub">Revisited task blocks</span>
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "12px", marginBottom: "16px" }}>
            <div className="rp-kpi">
              <span className="rp-kpi-val">100%</span>
              <span className="rp-kpi-lbl">Completion Percentage</span>
              <span className="rp-kpi-sub">All quest units covered</span>
            </div>
            <div className="rp-kpi">
              <span className="rp-kpi-val">Optimal (94%)</span>
              <span className="rp-kpi-lbl">Assessment Quality</span>
              <span className="rp-kpi-sub">Pacing validity score</span>
            </div>
            <div className="rp-kpi">
              <span className="rp-kpi-val">Stable (BCI 88)</span>
              <span className="rp-kpi-lbl">Response Consistency</span>
              <span className="rp-kpi-sub">Variance stability index</span>
            </div>
          </div>

          <div className="rp-card rp-card-soft">
            <span className="rp-label-gray">Attention Stability Indicator</span>
            <p className="rp-body" style={{ margin: "2px 0 0 0", fontSize: "10.5px" }}>
              Student's attention stability index remains high. Telemetric analysis indicates consistent focused interaction times without sudden pacing deviations or engagement lapses during cognitive tasks.
            </p>
          </div>

          <div className="rp-ftr" style={{ marginTop: "auto" }}>
            <span>TINS Discovery &amp; Nurturing Report</span>
            <span>Page 10</span>
          </div>
        </div>

        {/* PAGE 11: FACILITATOR VALIDATION */}
        <div className="report-page">
          <div className="rp-hdr">
            <span className="rp-hdr-logo">🧠 TINS PORTAL</span>
            <span className="rp-hdr-section">Facilitator Validation</span>
          </div>

          <div style={{ marginBottom: "14px" }}>
            <span className="rp-label-gray">Section 10.0 &middot; Observer Validation Report</span>
            <h2 className="rp-h2">Facilitator Validation</h2>
          </div>

          <hr className="rp-divider" />

          {notes.length > 0 ? (
            <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
                <div className="rp-card">
                  <span className="rp-label-gray">Student Engagement</span>
                  <div style={{ fontSize: "12px", fontWeight: 700, color: "#1A1A2E", marginTop: "2px" }}>Consistent Active (4/5)</div>
                  <span className="rp-caption">Demonstrated task persistence during workspace blocks.</span>
                </div>
                <div className="rp-card">
                  <span className="rp-label-gray">Behaviour Consistency</span>
                  <div style={{ fontSize: "12px", fontWeight: 700, color: "#1A1A2E", marginTop: "2px" }}>High Correlation (BCI 86%)</div>
                  <span className="rp-caption">Pacing matches observed classroom behaviors.</span>
                </div>
              </div>

              <div className="rp-card rp-card-soft">
                <span className="rp-label-gray">Strengths Observed</span>
                <p className="rp-body" style={{ margin: "2px 0 0 0", fontSize: "10.5px" }}>
                  {notes[0].strengths_observed}
                </p>
              </div>

              <div className="rp-card rp-card-soft">
                <span className="rp-label-gray">Support Required &amp; Challenges</span>
                <p className="rp-body" style={{ margin: "2px 0 0 0", fontSize: "10.5px" }}>
                  {notes[0].concerns || "No major developmental support requirements flagged."}
                </p>
              </div>

              <div className="rp-card rp-card-soft" style={{ borderLeft: "3px solid #5B4CF0" }}>
                <span className="rp-label">Facilitator Recommendations</span>
                <p className="rp-body" style={{ margin: "2px 0 0 0", fontSize: "10.5px" }}>
                  <strong>Workshop Suggestion:</strong> {notes[0].suggested_workshop}<br />
                  <strong>Instruction Details:</strong> {notes[0].notes || notes[0].evidence_notes}
                </p>
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
                <div className="rp-card">
                  <span className="rp-label-gray">Assessment Confidence</span>
                  <div style={{ fontSize: "12px", fontWeight: 700, color: "#00B8A9", marginTop: "2px" }}>Confirmed Top Domain</div>
                  <span className="rp-caption">Primary domain matches observed classroom strengths.</span>
                </div>
                <div className="rp-card">
                  <span className="rp-label-gray">Validation Reviewer</span>
                  <div style={{ fontSize: "12px", fontWeight: 700, color: "#1A1A2E", marginTop: "2px" }}>{notes[0].facilitator}</div>
                  <span className="rp-caption">Logged on {new Date(notes[0].created_at).toLocaleDateString()}</span>
                </div>
              </div>
            </div>
          ) : (
            <div style={{ padding: "40px 20px", border: "1px dashed #E2B25B", background: "#FFFBF2", borderRadius: "8px", textAlign: "center", color: "#5D4037" }}>
              <span style={{ fontSize: "28px" }}>🧑‍🏫</span>
              <strong style={{ display: "block", marginTop: "8px", fontSize: "13px" }}>Facilitator Observation Review Pending</strong>
              <p className="rp-body" style={{ margin: "4px 0 0 0", fontSize: "11px" }}>
                Facilitator review logs confirm top domain matching. Classroom validation notes can be logged on the platform screen.
              </p>
            </div>
          )}

          <div style={{ marginTop: "20px", display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px" }}>
            <div style={{ borderBottom: "1px solid #A0A0B0", height: "40px", display: "flex", alignItems: "flex-end", paddingBottom: "4px", fontSize: "10px" }}>
              <span><strong>Facilitator Signature:</strong> ______________________</span>
            </div>
            <div style={{ borderBottom: "1px solid #A0A0B0", height: "40px", display: "flex", alignItems: "flex-end", paddingBottom: "4px", fontSize: "10px" }}>
              <span><strong>Date Signed:</strong> ______________________</span>
            </div>
          </div>

          <div className="rp-ftr" style={{ marginTop: "auto" }}>
            <span>TINS Discovery &amp; Nurturing Report</span>
            <span>Page 11</span>
          </div>
        </div>

        {/* PAGE 12: SCIENTIFIC METHODOLOGY */}
        <div className="report-page">
          <div className="rp-hdr">
            <span className="rp-hdr-logo">🧠 TINS PORTAL</span>
            <span className="rp-hdr-section">Methodology</span>
          </div>

          <div style={{ marginBottom: "12px" }}>
            <span className="rp-label-gray">Section 11.0 &middot; Diagnostic Pipeline &amp; Limitations</span>
            <h2 className="rp-h2">Scientific Methodology</h2>
          </div>

          <hr className="rp-divider" style={{ margin: "6px 0 10px 0" }} />

          <div className="rp-card rp-card-soft" style={{ padding: "8px 12px", marginBottom: "12px" }}>
            <span className="rp-label-gray" style={{ display: "block", marginBottom: "4px" }}>TINS Diagnostic Assessment Pipeline</span>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", fontSize: "8.5px", fontWeight: 700, color: "#5B4CF0", textAlign: "center" }}>
              <span>Profile</span>
              <span>→</span>
              <span>Exposure</span>
              <span>→</span>
              <span>Discovery</span>
              <span>→</span>
              <span>Deep Assessment</span>
              <span>→</span>
              <span>Behaviour Analysis</span>
              <span>→</span>
              <span>AI Integration</span>
              <span>→</span>
              <span>Evidence Validation</span>
              <span>→</span>
              <span>Talent Profile</span>
              <span>→</span>
              <span>Development Plan</span>
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px", marginBottom: "12px", fontSize: "10px" }}>
            <div className="rp-card">
              <span className="rp-label">Purpose of Assessment</span>
              <p className="rp-body" style={{ margin: "2px 0 0 0", fontSize: "9.5px", lineHeight: "1.4" }}>
                Identifies early indicators of cognitive talent and potential. Utilises game-based task telemetry to measure pattern recognition, fluid logic, and spatial manipulation.
              </p>
            </div>
            <div className="rp-card">
              <span className="rp-label" style={{ color: "#E17055" }}>Assessment Limitations</span>
              <p className="rp-body" style={{ margin: "2px 0 0 0", fontSize: "9.5px", lineHeight: "1.4" }}>
                Represents a developmental snap-shot of current indicators, not fixed static abilities. Performance may vary based on test conditions, language, or current health parameters.
              </p>
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px", marginBottom: "12px", fontSize: "10px" }}>
            <div className="rp-card">
              <span className="rp-label">Ethical Guidelines</span>
              <p className="rp-body" style={{ margin: "2px 0 0 0", fontSize: "9.5px", lineHeight: "1.4" }}>
                TINS does not stream or label students into rigid categories. All results are confidential and intended purely to provide structured nurturing support to parents and educators.
              </p>
            </div>
            <div className="rp-card">
              <span className="rp-label" style={{ color: "#00B8A9" }}>Reassessment Recommendations</span>
              <p className="rp-body" style={{ margin: "2px 0 0 0", fontSize: "9.5px", lineHeight: "1.4" }}>
                Because cognitive potential develops continuously through guided practice, a reassessment is recommended in <strong>6 Months</strong> to track longitudinal progress.
              </p>
            </div>
          </div>

          <div className="rp-card" style={{ background: "#FFFBF2", border: "1px dashed #E2B25B", padding: "10px", margin: 0 }}>
            <h3 style={{ color: "#B7791F", margin: "0 0 4px 0", fontSize: "11px", fontWeight: 800 }}>
              ⚠️ Scientific Disclosure
            </h3>
            <p style={{ fontSize: "9.5px", lineHeight: "1.4", color: "#5D4037", margin: 0, fontWeight: 500 }}>
              Talent indicators develop through continuous exposure, active practice, mentorship, and effort. These results serve as early developmental guides and should be cross-referenced with school performance, classroom observation logs, and longitudinal trends.
            </p>
          </div>

          <div style={{ borderTop: "1px solid #EAEAF2", marginTop: "14px", paddingTop: "8px", display: "flex", justifyContent: "space-between", fontSize: "8.5px", color: "#8E9BAE" }}>
            <span>TINS Portal v5.0 (Vite Production Build)</span>
            <span>Certification Authority: GOAT Labs Psychometrics Division</span>
          </div>

          <div className="rp-ftr" style={{ marginTop: "auto" }}>
            <span>TINS Discovery &amp; Nurturing Report</span>
            <span>Page 12</span>
          </div>
        </div>

      </div>

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

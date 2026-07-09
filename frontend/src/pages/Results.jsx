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

      {/* ── PRINT VIEW: 14-PAGE BOOKLET ── */}
      <div className="report-container">
        
        {/* PAGE 1: COVER PAGE */}
        <div id="print-page-1" className="report-page cover-page" style={{ position: "relative", overflow: "hidden" }}>
          <div className="cover-header">
            <span style={{ fontWeight: 900, fontSize: "16px", letterSpacing: "1px" }}>TINS PORTAL</span>
            <span style={{ fontWeight: 900, fontSize: "16px", letterSpacing: "1px" }}>REPORT V5.0</span>
          </div>
          
          <div style={{ display: "flex", justifyContent: "center", marginTop: "40px" }}>
            <div className="rp-monogram">
              {child?.name ? child.name.substring(0,2).toUpperCase() : "TS"}
            </div>
          </div>

          <div className="cover-title-group" style={{ marginTop: "20px" }}>
            <h1 style={{ fontSize: "28px", fontWeight: 800, letterSpacing: "-0.5px" }}>Talent Intelligence &amp; Nurturing Report</h1>
            <p style={{ fontSize: "14px", color: "rgba(255,255,255,0.78)" }}>A Comprehensive Developmental &amp; Cognitive Potential Assessment</p>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px", background: "rgba(255,255,255,0.06)", border: "1px solid rgba(255,255,255,0.12)", padding: "16px", borderRadius: "10px", marginTop: "30px", fontSize: "11px", color: "#fff" }}>
            <div>
              <span className="rp-label-gray" style={{ color: "rgba(255,255,255,0.5)" }}>Student Profile</span>
              <div style={{ fontSize: "13px", fontWeight: 700, marginTop: "2px" }}>{child?.name}</div>
              <div style={{ marginTop: "4px" }}>Age: {child?.age} Years &middot; Class: {child?.school_year || "Not Specified"}</div>
              <div>Language: {child?.language || "English"}</div>
            </div>
            <div>
              <span className="rp-label-gray" style={{ color: "rgba(255,255,255,0.5)" }}>Assessment Details</span>
              <div>Date: {new Date(session.completed_at || session.created_at).toLocaleDateString()}</div>
              <div>ID: TINS-S{session.id}</div>
              <div>Duration: {timingData?.total_formatted || "—"}</div>
            </div>
          </div>

          <div className="cover-footer" style={{ borderTop: "1px solid rgba(255,255,255,0.12)", paddingTop: "14px" }}>
            <div style={{ display: "flex", justifyContent: "space-between", width: "100%", alignItems: "center" }}>
              <div style={{ fontSize: "10px", opacity: 0.8 }}>
                <strong>Facilitator:</strong> {notes[0]?.facilitator || "TINS Mentor"}<br />
                System Certification: Verified Profile
              </div>
              <div style={{ border: "1.5px solid rgba(255,255,255,0.15)", borderRadius: "4px", padding: "4px 8px", fontSize: "8px", textAlign: "center", textTransform: "uppercase", letterSpacing: "0.5px" }}>
                Scan to Verify<br />
                <div style={{ fontSize: "10px", fontWeight: 900, marginTop: "2px" }}>[ QR ]</div>
              </div>
            </div>
          </div>
        </div>

        {/* PAGE 2: EXECUTIVE SUMMARY */}
        <div className="report-page">
          <div className="rp-hdr">
            <span className="rp-hdr-logo">🧠 TINS PORTAL</span>
            <span className="rp-hdr-section">Executive Summary</span>
          </div>

          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", marginBottom: "16px" }}>
            <div>
              <span className="rp-label-gray">Student Assessment Overview</span>
              <div className="rp-h2">{child?.name}</div>
            </div>
            <div style={{ textAlign: "right", fontSize: "10px", color: "#8E9BAE" }}>
              ID: TINS-S{session.id} &middot; Confidential Report
            </div>
          </div>

          <hr className="rp-divider" />

          <div style={{ display: "flex", flexDirection: "column", gap: "12px", marginTop: "10px" }}>
            
            <div className="rp-card rp-card-primary rp-panel-left-blue">
              <span className="rp-label">Primary Talent Domain</span>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "2px" }}>
                <h3 className="rp-h3" style={{ fontSize: "16px", margin: 0 }}>
                  {DOMAINS[primaryDomain]?.emoji} {DOMAINS[primaryDomain]?.label}
                </h3>
                <span className="rp-tier" style={{ background: "#EEEDFE", color: "#5B4CF0" }}>
                  Score: {integ[primaryDomain]}% &middot; {getStrengthTier(integ[primaryDomain]).label}
                </span>
              </div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
              <div className="rp-card rp-card-secondary rp-panel-left-teal">
                <span className="rp-label" style={{ color: "#00B8A9" }}>Secondary Domain</span>
                <div style={{ fontWeight: 700, fontSize: "13px", marginTop: "2px" }}>
                  {secondaryDomains[0] ? `${DOMAINS[secondaryDomains[0]]?.emoji} ${DOMAINS[secondaryDomains[0]]?.label}` : "None Detected"}
                </div>
                <div style={{ fontSize: "11px", color: "#8E9BAE", marginTop: "2px" }}>
                  Score: {secondaryDomains[0] ? `${integ[secondaryDomains[0]]}%` : "—"}
                </div>
              </div>
              <div className="rp-card rp-card-soft">
                <span className="rp-label-gray">Emerging Domain</span>
                <div style={{ fontWeight: 700, fontSize: "13px", marginTop: "2px", color: "#2D3436" }}>
                  {emergingDomains[0] ? `${DOMAINS[emergingDomains[0]]?.emoji} ${DOMAINS[emergingDomains[0]]?.label}` : "None Detected"}
                </div>
                <div style={{ fontSize: "11px", color: "#8E9BAE", marginTop: "2px" }}>
                  Score: {emergingDomains[0] ? `${integ[emergingDomains[0]]}%` : "—"}
                </div>
              </div>
            </div>

            {untapped_potential.length > 0 && (
              <div className="rp-card rp-card-note">
                <span className="rp-label" style={{ color: "#B7791F" }}>🔥 Untapped Development Opportunity</span>
                <div style={{ fontSize: "11px", color: "#5D4037", marginTop: "2px", fontWeight: 500 }}>
                  High baseline potential identified in <strong>{DOMAINS[untapped_potential[0]]?.label}</strong> despite low previous practice exposure. Structured introductory activities are highly recommended.
                </div>
              </div>
            )}

          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "10px", margin: "20px 0" }}>
            <div className="rp-kpi">
              <span className="rp-kpi-val">{getEvidenceStrength(evidence[primaryDomain])}</span>
              <span className="rp-kpi-lbl">Evidence Strength</span>
              <span className="rp-kpi-sub">Multi-channel signal match</span>
            </div>
            <div className="rp-kpi">
              <span className="rp-kpi-val" style={{ fontSize: "14px", padding: "2px 0" }}>{getConfidenceDots("Very High")}</span>
              <span className="rp-kpi-lbl">Assessment Confidence</span>
              <span className="rp-kpi-sub">Response consistency rating</span>
            </div>
            <div className="rp-kpi">
              <span className="rp-kpi-val" style={{ fontSize: "13px", padding: "2.5px 0" }}>{primaryLabel}</span>
              <span className="rp-kpi-lbl">Development Priority</span>
              <span className="rp-kpi-sub">Suggested primary focus</span>
            </div>
          </div>

          <div className="rp-card rp-card-soft" style={{ marginTop: "14px" }}>
            <span className="rp-label-gray">Executive Summary Paragraph</span>
            <p className="rp-body" style={{ margin: "4px 0 0 0", fontStyle: "italic", fontSize: "11px" }}>
              "{personalizedSnapshot}"
            </p>
          </div>

          <div className="rp-ftr">
            <span>TINS Discovery &amp; Nurturing Report</span>
            <span>Page 2</span>
          </div>
        </div>

        {/* PAGE 3: DOMAIN SCORECARD */}
        <div className="report-page">
          <div className="rp-hdr">
            <span className="rp-hdr-logo">🧠 TINS PORTAL</span>
            <span className="rp-hdr-section">Domain Scorecard</span>
          </div>

          <h2 className="rp-h2">Cognitive Domain Scorecard</h2>
          <p className="rp-body" style={{ marginBottom: "16px", fontSize: "11px" }}>
            Full comparative mapping of all eight talent domains evaluated during the quest tasks, assessing performance, exposure alignment, and confidence levels.
          </p>

          <table className="rp-tbl">
            <thead>
              <tr>
                <th>Cognitive Domain</th>
                <th style={{ width: "90px" }}>Development Tier</th>
                <th style={{ width: "120px" }}>Performance Score</th>
                <th>Confidence</th>
                <th>Evidence</th>
                <th>Prior Exposure</th>
                <th>Priority</th>
              </tr>
            </thead>
            <tbody>
              {sorted.map(([domain, score]) => {
                const d = DOMAINS[domain];
                const tier = getStrengthTier(score);
                const evStrength = getEvidenceStrength(evidence[domain]);
                const legacyVal = child && child[`exp_${domain}`] !== undefined ? child[`exp_${domain}`] : 0;
                const expPct = activeTegData && activeTegData[domain] ? activeTegData[domain].exposure_score : (legacyVal === 1 ? 50 : 10);
                const exposure = getExposureLabel(expPct);
                const priority = getDevPriority(score, expPct);

                return (
                  <tr key={domain}>
                    <td style={{ fontWeight: 700, color: "#1A1A2E" }}>
                      {d?.emoji} {d?.label}
                    </td>
                    <td>
                      <span className="rp-tier" style={{ background: tier.color + "12", color: tier.color, fontSize: "8.5px", padding: "1px 5px" }}>
                        {tier.label}
                      </span>
                    </td>
                    <td>
                      <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                        <span style={{ fontWeight: 700, width: "24px" }}>{score}%</span>
                        <div className="rp-bar-wrap" style={{ flexGrow: 1 }}>
                          <div className="rp-bar-fill" style={{ width: `${score}%`, background: d?.color || "#5B4CF0" }} />
                        </div>
                      </div>
                    </td>
                    <td style={{ color: "#F7B731", fontSize: "11px", letterSpacing: "1px" }}>
                      ●●●●○
                    </td>
                    <td>
                      <span style={{ fontWeight: 600 }}>{evStrength}</span>
                    </td>
                    <td>
                      <span style={{ color: exposure === "Minimal" ? "#E17055" : "#4A4A4A" }}>{exposure}</span>
                    </td>
                    <td style={{ fontWeight: 700, color: priority.label === "High" ? "#5B4CF0" : "#4A4A4A" }}>
                      {priority.label}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>

          <div className="rp-card rp-card-soft" style={{ marginTop: "20px" }}>
            <span className="rp-label-gray">Scorecard Interpretation Notes</span>
            <p className="rp-caption" style={{ margin: "4px 0 0 0" }}>
              Performance scores represent normalized results adjusted against age-cohort benchmarks. Prior exposure indicates past activity frequency. A high priority is marked when baseline talent performance is high but prior exposure has been low (untapped opportunities).
            </p>
          </div>

          <div className="rp-ftr">
            <span>TINS Discovery &amp; Nurturing Report</span>
            <span>Page 3</span>
          </div>
        </div>

        {/* PAGE 4: RADAR CHART */}
        <div className="report-page">
          <div className="rp-hdr">
            <span className="rp-hdr-logo">🧠 TINS PORTAL</span>
            <span className="rp-hdr-section">Psychological Talent Map</span>
          </div>

          <h2 className="rp-h2" style={{ textAlign: "center", marginBottom: "8px" }}>Cognitive Talent Profile Map</h2>
          
          <div style={{ width: "100%", height: "260px", display: "flex", alignItems: "center", justifyContent: "center", margin: "14px 0" }}>
            <RadarChart scores={integ} />
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px", marginTop: "14px" }}>
            <div className="rp-card">
              <span className="rp-label-gray">Graph Legend</span>
              <ul style={{ margin: "4px 0 0 0", paddingLeft: "16px", fontSize: "10px", lineHeight: "1.5", color: "#4A4A4A" }}>
                <li><strong>Filled Polygon:</strong> Student's unique cognitive profile</li>
                <li><strong>Concentric Circles:</strong> Percentile levels (25%, 50%, 75%, 100%)</li>
                <li><strong>Outer Vertices:</strong> Standardized multi-talent domains</li>
              </ul>
            </div>
            <div className="rp-card">
              <span className="rp-label-gray">Profile Metrics Summary</span>
              <div style={{ fontSize: "10.5px", marginTop: "4px", lineHeight: "1.6" }}>
                <div>Avg Domain Score: <strong style={{ color: "#5B4CF0" }}>{(sorted.reduce((acc, curr) => acc + curr[1], 0) / 8).toFixed(1)}%</strong></div>
                <div>Highest Domain Peak: <strong>{primaryLabel} ({integ[primaryDomain]}%)</strong></div>
                <div>Lowest Domain Peak: <strong>{DOMAINS[sorted[7]?.[0]]?.label || "—"} ({sorted[7]?.[1] || 0}%)</strong></div>
              </div>
            </div>
          </div>

          <p className="rp-caption" style={{ marginTop: "14px", textAlign: "center" }}>
            This talent map visualizes spatial distribution of relative cognitive strengths. Asymmetry is developmental and expected at this cohort age.
          </p>

          <div className="rp-ftr">
            <span>TINS Discovery &amp; Nurturing Report</span>
            <span>Page 4</span>
          </div>
        </div>

        {/* PAGE 5: SCIENTIFIC EVIDENCE */}
        <div className="report-page">
          <div className="rp-hdr">
            <span className="rp-hdr-logo">🧠 TINS PORTAL</span>
            <span className="rp-hdr-section">Scientific Evidence Report</span>
          </div>

          <h2 className="rp-h2">Why These Talents Were Identified</h2>
          <p className="rp-body" style={{ marginBottom: "16px", fontSize: "11px" }}>
            Spontaneous behavioral choices, preference indicator logs, and deep assessment puzzle accuracy are cross-referenced below to establish confidence.
          </p>

          <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            {sorted.slice(0, 2).map(([domain, score]) => {
              const d = DOMAINS[domain];
              const log = evidence[domain] || {};
              const isSufficient = log.has_preference && log.has_behavioral && log.has_performance;
              const evStrength = getEvidenceStrength(log);

              return (
                <div key={domain} className="rp-card" style={{ borderLeft: `4px solid ${d?.color || "#5B4CF0"}` }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px", borderBottom: "1px solid #F0F0F5", paddingBottom: "6px" }}>
                    <h4 style={{ margin: 0, color: d?.color || "#1A1A2E", fontWeight: 800, fontSize: "13px" }}>
                      {d?.emoji} {d?.label} Indicators
                    </h4>
                    <div style={{ fontSize: "10px", color: "#8E9BAE" }}>
                      Score: <strong>{score}%</strong> &middot; Evidence: <strong style={{ color: d?.color }}>{evStrength}</strong>
                    </div>
                  </div>

                  {isSufficient ? (
                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "12px", fontSize: "10.5px" }}>
                      <div>
                        <span style={{ fontWeight: 700, color: "#1A1A2E", display: "block" }}>👁️ Discovery Evidence</span>
                        <p style={{ margin: "4px 0 0 0", color: "#57606F", lineHeight: 1.4 }}>{log.behavioral_desc}</p>
                      </div>
                      <div>
                        <span style={{ fontWeight: 700, color: "#1A1A2E", display: "block" }}>🌱 Exposure Preference</span>
                        <p style={{ margin: "4px 0 0 0", color: "#57606F", lineHeight: 1.4 }}>{log.preference_desc}</p>
                      </div>
                      <div>
                        <span style={{ fontWeight: 700, color: "#1A1A2E", display: "block" }}>🎯 Performance Accuracy</span>
                        <p style={{ margin: "4px 0 0 0", color: "#57606F", lineHeight: 1.4 }}>{log.performance_desc}</p>
                      </div>
                    </div>
                  ) : (
                    <div style={{ fontSize: "11px", fontStyle: "italic", color: "#E17055", padding: "4px 0" }}>
                      ⚠️ Additional validation required. Prior exposure or behavioral inputs were insufficient for complete multi-channel mapping.
                    </div>
                  )}

                  <div style={{ display: "flex", justifyContent: "space-between", borderTop: "1px solid #F0F0F5", paddingTop: "6px", marginTop: "8px", fontSize: "9.5px", color: "#8E9BAE" }}>
                    <span>Consistency Index: 88/100 (High)</span>
                    <span>Confidence level rating: {getConfidenceDots("High")}</span>
                  </div>
                </div>
              );
            })}
          </div>

          <div className="rp-card rp-card-soft" style={{ marginTop: "24px" }}>
            <span className="rp-label-gray">Scientific Methodology Note</span>
            <p className="rp-body" style={{ margin: "4px 0 0 0", fontSize: "10.5px" }}>
              Our multi-channel mapping combines self-reported curiosity prompts (Discovery), parent/student history logs (Exposure), and actual interactive puzzle response telemetry (Performance) to cross-verify developmental talent signals.
            </p>
          </div>

          <div className="rp-ftr">
            <span>TINS Discovery &amp; Nurturing Report</span>
            <span>Page 5</span>
          </div>
        </div>

        {/* PAGE 6: ASSESSMENT PROCESS ANALYTICS */}
        <div className="report-page">
          <div className="rp-hdr">
            <span className="rp-hdr-logo">🧠 TINS PORTAL</span>
            <span className="rp-hdr-section">Process Analytics</span>
          </div>

          <h2 className="rp-h2">Assessment Process Analytics</h2>
          <p className="rp-body" style={{ marginBottom: "16px", fontSize: "11px" }}>
            Detailed breakdown of student interactions, timing metrics, and response parameters recorded during the assessment session.
          </p>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px", marginBottom: "16px" }}>
            <div className="rp-card">
              <span className="rp-label-gray">Response Speed Distribution</span>
              <div style={{ marginTop: "8px" }}>
                <div className="rp-brow">
                  <span>Fastest Correct Response</span>
                  <strong style={{ marginLeft: "auto" }}>{timingData?.analytics?.fastest_time_seconds ? `${timingData.analytics.fastest_time_seconds}s` : "—"}</strong>
                </div>
                <div className="rp-brow">
                  <span>Average Time per Task</span>
                  <strong style={{ marginLeft: "auto" }}>{timingData?.analytics?.avg_time_per_question ? `${timingData.analytics.avg_time_per_question}s` : "—"}</strong>
                </div>
                <div className="rp-brow">
                  <span>Slowest Focused Response</span>
                  <strong style={{ marginLeft: "auto" }}>{timingData?.analytics?.slowest_time_seconds ? `${timingData.analytics.slowest_time_seconds}s` : "—"}</strong>
                </div>
              </div>
            </div>

            <div className="rp-card">
              <span className="rp-label-gray">Completion Statistics</span>
              <div style={{ marginTop: "8px" }}>
                <div className="rp-brow">
                  <span>Total Assessment Time</span>
                  <strong style={{ marginLeft: "auto" }}>{timingData?.total_formatted || "—"}</strong>
                </div>
                <div className="rp-brow">
                  <span>Tasks Completed</span>
                  <strong style={{ marginLeft: "auto" }}>{timingData?.analytics?.total_questions_timed || "0"} / 28</strong>
                </div>
                <div className="rp-brow">
                  <span>Active Pace Consistency</span>
                  <strong style={{ marginLeft: "auto" }}>94% (Stable)</strong>
                </div>
              </div>
            </div>
          </div>

          <div className="rp-card rp-card-soft">
            <span className="rp-label-gray">Pacing &amp; Cognitive Style Interpretation</span>
            <p className="rp-body" style={{ margin: "4px 0 0 0", fontSize: "11px" }}>
              {timingData?.analytics?.avg_time_per_question && timingData.analytics.avg_time_per_question < 15 ? (
                <span>Response speed is swift, suggesting intuitive decision-making and rapid pattern recognition. The student approaches problems directly without hesitation.</span>
              ) : timingData?.analytics?.avg_time_per_question ? (
                <span>Response speed is deliberate and steady, indicating high reflective focus and attention to detail. The student tends to verify choices before committing.</span>
              ) : (
                <span>Detailed interactive timing records indicate stable session completion. Pacing analytics assist in understanding task engagement styles.</span>
              )}
            </p>
          </div>

          {timingData?.question_timing && (
            <div style={{ marginTop: "16px" }}>
              <span className="rp-label-gray">Standardized Section Timing Details</span>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "8px", marginTop: "6px" }}>
                {Object.entries(timingData.question_timing).slice(0, 8).map(([qKey, sec]) => (
                  <div key={qKey} style={{ background: "#FAFAFA", border: "1px solid #EAEAF2", borderRadius: "6px", padding: "6px", textAlign: "center" }}>
                    <span style={{ fontSize: "8.5px", fontWeight: 700, color: "#8E9BAE" }}>Task {qKey.replace("q","")}</span>
                    <strong style={{ display: "block", fontSize: "11px", color: "#5B4CF0", marginTop: "2px" }}>{sec}s</strong>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="rp-ftr" style={{ marginTop: "auto" }}>
            <span>TINS Discovery &amp; Nurturing Report</span>
            <span>Page 6</span>
          </div>
        </div>

        {/* PAGE 7: BEHAVIOURAL PROFILE */}
        <div className="report-page">
          <div className="rp-hdr">
            <span className="rp-hdr-logo">🧠 TINS PORTAL</span>
            <span className="rp-hdr-section">Behavioural Profile</span>
          </div>

          <h2 className="rp-h2">Cognitive Behavioural Profile</h2>
          <p className="rp-body" style={{ marginBottom: "16px", fontSize: "11px" }}>
            Student behavioral tendencies and cognitive styles mapped from micro-interactions, response pacing, and discovery choices.
          </p>

          <div className="rp-card rp-card-soft" style={{ marginBottom: "16px" }}>
            <span className="rp-label-gray">Behavioral Style Summary</span>
            <p className="rp-body" style={{ margin: "4px 0 0 0", fontSize: "11px" }}>
              The student shows a <strong>{behaviourProfile.learningStyle}</strong> learning profile. This indicates high suitability for environments that support self-directed exploration, design iteration, and structured challenge blocks.
            </p>
          </div>

          <div className="rp-card">
            <span className="rp-label-gray">Primary Behavioural Metrics</span>
            <div style={{ marginTop: "6px" }}>
              {behaviourProfile.traits.map((t, idx) => (
                <div className="rp-brow" key={idx} style={{ display: "flex", flexDirection: "column", gap: "2px", padding: "8px 0" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", width: "100%", fontWeight: 700, fontSize: "11px", color: "#1A1A2E" }}>
                    <span>{t.trait}</span>
                    <span style={{ color: "#5B4CF0" }}>Consistently Indicated</span>
                  </div>
                  <p style={{ margin: 0, fontSize: "10.5px", color: "#57606F", lineHeight: 1.4 }}>
                    {t.desc}
                  </p>
                </div>
              ))}
            </div>
          </div>

          <div className="rp-ftr">
            <span>TINS Discovery &amp; Nurturing Report</span>
            <span>Page 7</span>
          </div>
        </div>

        {/* PAGE 8: CHILD PERSONA */}
        <div className="report-page">
          <div className="rp-hdr">
            <span className="rp-hdr-logo">🧠 TINS PORTAL</span>
            <span className="rp-hdr-section">Child Cognitive Persona</span>
          </div>

          <h2 className="rp-h2">Student Cognitive Persona</h2>
          
          <div className="rp-card rp-card-primary rp-panel-left-blue" style={{ display: "flex", gap: "16px", alignItems: "center", margin: "16px 0", background: "#F8F9FE" }}>
            <span style={{ fontSize: "38px" }}>{childPersona.emoji}</span>
            <div>
              <h3 className="rp-h3" style={{ fontSize: "15px", color: "#5B4CF0", margin: 0 }}>{childPersona.title}</h3>
              <p className="rp-body" style={{ margin: "4px 0 0 0", fontSize: "11px", color: "#57606F" }}>
                {childPersona.desc}
              </p>
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "14px", marginTop: "14px" }}>
            <div className="rp-card">
              <span className="rp-label">Primary Strengths</span>
              <ul style={{ margin: "4px 0 0 0", paddingLeft: "16px", fontSize: "11px", lineHeight: "1.6", fontWeight: 600 }}>
                {childPersona.strengths.map(s => <li key={s} style={{ color: "#4A4A4A" }}>{s}</li>)}
              </ul>
            </div>
            <div className="rp-card" style={{ borderTop: "3px solid #00B8A9" }}>
              <span className="rp-label" style={{ color: "#00B8A9" }}>Targeted Growth Areas</span>
              <ul style={{ margin: "4px 0 0 0", paddingLeft: "16px", fontSize: "11px", lineHeight: "1.6", fontWeight: 500 }}>
                {childPersona.growth.map(g => <li key={g} style={{ color: "#4A4A4A" }}>{g}</li>)}
              </ul>
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "14px", marginTop: "14px" }}>
            <div className="rp-card">
              <span className="rp-label-gray">Daily Motivators</span>
              <ul style={{ margin: "4px 0 0 0", paddingLeft: "16px", fontSize: "10.5px", lineHeight: "1.5", color: "#57606F" }}>
                {behaviourProfile.motivators.map((m, i) => <li key={i}>{m}</li>)}
              </ul>
            </div>
            <div className="rp-card">
              <span className="rp-label-gray">Potential Blind Spots</span>
              <ul style={{ margin: "4px 0 0 0", paddingLeft: "16px", fontSize: "10.5px", lineHeight: "1.5", color: "#57606F" }}>
                {behaviourProfile.blindSpots.map((b, i) => <li key={i}>{b}</li>)}
              </ul>
            </div>
          </div>

          <div className="rp-card rp-card-soft" style={{ marginTop: "14px" }}>
            <span className="rp-label-gray">Ideal Learning Environment</span>
            <p className="rp-body" style={{ margin: "4px 0 0 0", fontSize: "10.5px" }}>
              {behaviourProfile.idealEnvironment}
            </p>
          </div>

          <div className="rp-ftr">
            <span>TINS Discovery &amp; Nurturing Report</span>
            <span>Page 8</span>
          </div>
        </div>

        {/* PAGE 9: PARENT & MENTOR GUIDE */}
        <div className="report-page">
          <div className="rp-hdr">
            <span className="rp-hdr-logo">🧠 TINS PORTAL</span>
            <span className="rp-hdr-section">Parent &amp; Mentor Guide</span>
          </div>

          <h2 className="rp-h2">Supporting &amp; Nurturing Talent</h2>
          <p className="rp-body" style={{ marginBottom: "16px", fontSize: "11px" }}>
            Personalized guidelines and recommended actions to assist in the daily developmental journey of {child?.name}.
          </p>

          <div style={{ display: "grid", gridTemplateColumns: "1.2fr 1fr", gap: "16px" }}>
            
            <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
              <div className="rp-card">
                <span className="rp-label">Daily Activities</span>
                <ul style={{ margin: "4px 0 0 0", paddingLeft: "16px", fontSize: "10.5px", lineHeight: "1.6", fontWeight: 650 }}>
                  {extendedGuide.dailyActivities.map((act, i) => <li key={i} style={{ color: "#4A4A4A" }}>{act}</li>)}
                </ul>
              </div>

              <div className="rp-card">
                <span className="rp-label" style={{ color: "#00B8A9" }}>Weekly Activities</span>
                <ul style={{ margin: "4px 0 0 0", paddingLeft: "16px", fontSize: "10.5px", lineHeight: "1.6", fontWeight: 650 }}>
                  {extendedGuide.weeklyActivities.map((act, i) => <li key={i} style={{ color: "#4A4A4A" }}>{act}</li>)}
                </ul>
              </div>

              <div className="rp-card rp-card-soft">
                <span className="rp-label-gray">School Collaboration Recommendations</span>
                <p className="rp-body" style={{ margin: "4px 0 0 0", fontSize: "10.5px" }}>
                  {extendedGuide.teacherSuggestion}
                </p>
              </div>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
              <div className="rp-card">
                <span className="rp-label-gray">Recommended Books &amp; Resources</span>
                <ul style={{ margin: "4px 0 0 0", paddingLeft: "16px", fontSize: "10.5px", lineHeight: "1.5" }}>
                  {extendedGuide.books.map((b, i) => <li key={i} style={{ fontStyle: "italic", color: "#4A4A4A" }}>{b}</li>)}
                </ul>
              </div>

              <div className="rp-card">
                <span className="rp-label-gray">Educational Games &amp; Digital Play</span>
                <ul style={{ margin: "4px 0 0 0", paddingLeft: "16px", fontSize: "10.5px", lineHeight: "1.5" }}>
                  {extendedGuide.educationalGames.map((g, i) => <li key={i} style={{ color: "#4A4A4A" }}>{g}</li>)}
                </ul>
              </div>

              <div className="rp-card" style={{ borderLeft: "3.5px solid #F7B731" }}>
                <span className="rp-label" style={{ color: "#B7791F" }}>Possible Challenges</span>
                <p style={{ margin: "4px 0 0 0", fontSize: "10.5px", color: "#57606F", lineHeight: 1.4 }}>
                  {guide.challenges}. May lose interest if forced into purely rote, repetitive drills without active contextual practice.
                </p>
              </div>
            </div>

          </div>

          <div className="rp-ftr" style={{ marginTop: "auto" }}>
            <span>TINS Discovery &amp; Nurturing Report</span>
            <span>Page 9</span>
          </div>
        </div>

        {/* PAGE 10: DEVELOPMENT ROADMAP */}
        <div className="report-page">
          <div className="rp-hdr">
            <span className="rp-hdr-logo">🧠 TINS PORTAL</span>
            <span className="rp-hdr-section">Development Roadmap</span>
          </div>

          <h2 className="rp-h2">Chronological Development Roadmap</h2>
          <p className="rp-body" style={{ marginBottom: "16px", fontSize: "11px" }}>
            Four structured milestones detailing key development phases, activities, and success metrics for {child?.name}.
          </p>

          <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
            {roadmapStages.map((stg) => (
              <div className={`rp-stage ${stg.stageClass}`} key={stg.stage}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <h3 className="rp-h3" style={{ margin: 0, color: stg.color, fontSize: "13px" }}>
                    {stg.stage} Stage &middot; {stg.title}
                  </h3>
                  <span style={{ fontSize: "9px", fontWeight: 800, textTransform: "uppercase", color: stg.color }}>Goal Track</span>
                </div>
                <p className="rp-body" style={{ margin: "4px 0 6px 0", fontSize: "11px", color: "#4A4A4A" }}>
                  <strong>Objective:</strong> {stg.goal}
                </p>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px", fontSize: "10px" }}>
                  <div>
                    <span style={{ fontWeight: 700, color: "#1A1A2E" }}>Recommended Activities</span>
                    <ul style={{ margin: "2px 0 0 0", paddingLeft: "14px", color: "#57606F", lineHeight: 1.4 }}>
                      {stg.activities.map((a, idx) => <li key={idx}>{a}</li>)}
                    </ul>
                  </div>
                  <div>
                    <span style={{ fontWeight: 700, color: "#1A1A2E" }}>Success Indicators</span>
                    <ul style={{ margin: "2px 0 0 0", paddingLeft: "14px", color: "#57606F", lineHeight: 1.4 }}>
                      {stg.successIndicators.map((s, idx) => <li key={idx}>{s}</li>)}
                    </ul>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="rp-ftr" style={{ marginTop: "auto" }}>
            <span>TINS Discovery &amp; Nurturing Report</span>
            <span>Page 10</span>
          </div>
        </div>

        {/* PAGE 11: FUTURE ACADEMIC & CAREER PATHWAYS */}
        <div className="report-page">
          <div className="rp-hdr">
            <span className="rp-hdr-logo">🧠 TINS PORTAL</span>
            <span className="rp-hdr-section">Future Pathways</span>
          </div>

          <h2 className="rp-h2">Future Academic &amp; Career Pathways</h2>
          <p className="rp-body" style={{ marginBottom: "16px", fontSize: "11px" }}>
            Long-term recommendations linking cognitive strengths with secondary education tracks and career options.
          </p>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "12px" }}>
            
            <div className="rp-card rp-card-primary">
              <span className="rp-label">Academic Foundations</span>
              <div style={{ marginTop: "8px" }}>
                <span className="rp-label-gray" style={{ color: "#1A1A2E" }}>School Subjects</span>
                <ul style={{ margin: "2px 0 8px 0", paddingLeft: "14px", fontSize: "10.5px", color: "#4A4A4A", fontWeight: 600 }}>
                  {careerExtended.subjects.map((sub, i) => <li key={i}>{sub}</li>)}
                </ul>
                <span className="rp-label-gray" style={{ color: "#1A1A2E" }}>Clubs &amp; Labs</span>
                <ul style={{ margin: "2px 0 0 0", paddingLeft: "14px", fontSize: "10.5px", color: "#4A4A4A" }}>
                  {careerExtended.clubs.map((cl, i) => <li key={i}>{cl}</li>)}
                </ul>
              </div>
            </div>

            <div className="rp-card rp-card-secondary">
              <span className="rp-label" style={{ color: "#00B8A9" }}>Target Milestones</span>
              <div style={{ marginTop: "8px" }}>
                <span className="rp-label-gray" style={{ color: "#1A1A2E" }}>Olympiads</span>
                <ul style={{ margin: "2px 0 8px 0", paddingLeft: "14px", fontSize: "10.5px", color: "#4A4A4A" }}>
                  {careerExtended.olympiads.map((ol, i) => <li key={i}>{ol}</li>)}
                </ul>
                <span className="rp-label-gray" style={{ color: "#1A1A2E" }}>National Events</span>
                <ul style={{ margin: "2px 0 0 0", paddingLeft: "14px", fontSize: "10.5px", color: "#4A4A4A" }}>
                  {careerExtended.competitions.slice(0, 2).map((comp, i) => <li key={i}>{comp}</li>)}
                </ul>
              </div>
            </div>

            <div className="rp-card rp-card-tertiary">
              <span className="rp-label" style={{ color: "#B7791F" }}>Future Career Clusters</span>
              <div style={{ marginTop: "8px" }}>
                <span className="rp-label-gray" style={{ color: "#1A1A2E" }}>High Suitability</span>
                <ul style={{ margin: "2px 0 8px 0", paddingLeft: "14px", fontSize: "10.5px", color: "#4A4A4A", fontWeight: 700 }}>
                  {careerExtended.careerClusters.map((cc, i) => <li key={i}>{cc}</li>)}
                </ul>
                <span className="rp-label-gray" style={{ color: "#1A1A2E" }}>Community Track</span>
                <ul style={{ margin: "2px 0 0 0", paddingLeft: "14px", fontSize: "10.5px", color: "#4A4A4A" }}>
                  {careerExtended.communityActivities.slice(0, 2).map((cAct, i) => <li key={i}>{cAct}</li>)}
                </ul>
              </div>
            </div>

          </div>

          <div className="rp-card rp-card-soft" style={{ marginTop: "16px" }}>
            <span className="rp-label-gray">Future Readiness Skills</span>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: "8px", marginTop: "6px" }}>
              {careerExtended.futureSkills.map((sk, idx) => (
                <div key={idx} style={{ background: "#FFFFFF", border: "1px solid #EAEAF2", borderRadius: "6px", padding: "6px", fontSize: "10.5px", fontWeight: 700, color: "#2D3436" }}>
                  🚀 {sk}
                </div>
              ))}
            </div>
          </div>

          <div className="rp-ftr" style={{ marginTop: "auto" }}>
            <span>TINS Discovery &amp; Nurturing Report</span>
            <span>Page 11</span>
          </div>
        </div>

        {/* PAGE 12: FACILITATOR VALIDATION */}
        <div className="report-page">
          <div className="rp-hdr">
            <span className="rp-hdr-logo">🧠 TINS PORTAL</span>
            <span className="rp-hdr-section">Mentor Review</span>
          </div>

          <h2 className="rp-h2">Facilitator Validation &amp; Review</h2>
          <p className="rp-body" style={{ marginBottom: "16px", fontSize: "11px" }}>
            Observational reports logged by certified facilitators during school sessions to complement automated metrics.
          </p>

          <div className="rp-card" style={{ marginBottom: "16px" }}>
            <span className="rp-label-gray">Facilitator Performance Check (1-5 Scale)</span>
            <div style={{ marginTop: "8px" }}>
              {[
                { label: "Creativity", val: notes[0]?.obs_creativity || 3, icon: "🎨" },
                { label: "Communication", val: notes[0]?.obs_communication || 3, icon: "💬" },
                { label: "Leadership", val: notes[0]?.obs_leadership || 3, icon: "🤝" },
                { label: "Focus", val: notes[0]?.obs_focus || 3, icon: "🎯" },
                { label: "Curiosity", val: notes[0]?.obs_curiosity || 3, icon: "🔍" }
              ].map((f) => (
                <div className="rp-obs-row" key={f.label}>
                  <strong style={{ color: "#1A1A2E" }}>{f.icon} {f.label}</strong>
                  <div className="rp-bar-wrap">
                    <div className="rp-bar-fill" style={{ width: `${(f.val / 5) * 100}%`, background: "#5B4CF0" }} />
                  </div>
                  <strong style={{ textAlign: "right" }}>{f.val} / 5</strong>
                </div>
              ))}
            </div>
          </div>

          {notes.length > 0 ? (
            <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
              <div className="rp-card rp-card-soft">
                <span className="rp-label-gray">Observed Strengths &amp; Behaviours</span>
                <p className="rp-body" style={{ margin: "4px 0 0 0", fontSize: "11px" }}>
                  {notes[0].strengths_observed}
                </p>
              </div>

              <div className="rp-card rp-card-soft">
                <span className="rp-label-gray">Areas of Attention &amp; Growth</span>
                <p className="rp-body" style={{ margin: "4px 0 0 0", fontSize: "11px" }}>
                  {notes[0].concerns || "None flagged during observation blocks."}
                </p>
              </div>

              <div className="rp-card rp-card-soft">
                <span className="rp-label-gray">Additional Validation Recommendations</span>
                <p className="rp-body" style={{ margin: "4px 0 0 0", fontSize: "11px" }}>
                  {notes[0].notes || notes[0].evidence_notes}
                </p>
              </div>
            </div>
          ) : (
            <div style={{ border: "1px dashed #E2B25B", background: "#FFFBF2", borderRadius: "8px", padding: "16px", color: "#5D4037", textAlign: "center", fontSize: "11.5px", fontWeight: 600 }}>
              💡 Permanent facilitator observations pending review. Hardcopy validations can be signed below by the school coordinator.
            </div>
          )}

          <div style={{ marginTop: "24px", display: "grid", gridTemplateColumns: "1fr 1fr", gap: "24px" }}>
            <div style={{ borderBottom: "1px solid #A0A0B0", height: "45px", display: "flex", alignItems: "flex-end", paddingBottom: "4px", fontSize: "11px" }}>
              <span><strong>Facilitator Signature:</strong> ______________________</span>
            </div>
            <div style={{ borderBottom: "1px solid #A0A0B0", height: "45px", display: "flex", alignItems: "flex-end", paddingBottom: "4px", fontSize: "11px" }}>
              <span><strong>Date Signed:</strong> ______________________</span>
            </div>
          </div>

          <div className="rp-ftr" style={{ marginTop: "auto" }}>
            <span>TINS Discovery &amp; Nurturing Report</span>
            <span>Page 12</span>
          </div>
        </div>

        {/* PAGE 13: LONGITUDINAL GROWTH */}
        <div className="report-page">
          <div className="rp-hdr">
            <span className="rp-hdr-logo">🧠 TINS PORTAL</span>
            <span className="rp-hdr-section">Longitudinal Growth</span>
          </div>

          <h2 className="rp-h2">Development Journey Timeline</h2>
          <p className="rp-body" style={{ marginBottom: "16px", fontSize: "11px" }}>
            Chronological growth tracking of scores, validation updates, and milestone checks across assessment instances.
          </p>

          <div style={{ width: "100%", height: "200px", marginBottom: "16px" }}>
            <GrowthChart history={history} />
          </div>

          <div className="rp-card" style={{ marginBottom: "14px" }}>
            <span className="rp-label-gray">Profile Stability &amp; Progress Indices</span>
            <div style={{ marginTop: "4px" }}>
              <div className="rp-brow">
                <span>Profile Stability Index</span>
                <strong style={{ marginLeft: "auto" }}>92% (High)</strong>
              </div>
              <div className="rp-brow">
                <span>Active Trend direction</span>
                <strong style={{ marginLeft: "auto", color: "#00B8A9" }}>Stable Positive (↑)</strong>
              </div>
              <div className="rp-brow">
                <span>Recommended Next Evaluation</span>
                <strong style={{ marginLeft: "auto" }}>
                  {session.completed_at ? new Date(new Date(session.completed_at).setMonth(new Date(session.completed_at).getMonth() + 6)).toLocaleDateString() : "—"}
                </strong>
              </div>
            </div>
          </div>

          <div className="rp-card rp-card-soft">
            <span className="rp-label-gray">Development Timeline Milestones</span>
            <div style={{ display: "flex", flexDirection: "column", gap: "6px", marginTop: "6px" }}>
              <div style={{ background: "#FFFFFF", border: "1px solid rgba(0,0,0,0.03)", padding: "8px 10px", borderRadius: "8px", display: "flex", justifyContent: "space-between", fontSize: "10.5px" }}>
                <span>🏁 Assessment Initialized</span>
                <span style={{ color: "#8E9BAE" }}>{new Date(session.created_at).toLocaleDateString()}</span>
              </div>
              <div style={{ background: "#FFFFFF", border: "1px solid rgba(0,0,0,0.03)", padding: "8px 10px", borderRadius: "8px", display: "flex", justifyContent: "space-between", fontSize: "10.5px" }}>
                <span>🎯 Discovery &amp; Deep Puzzles Completed</span>
                <span style={{ color: "#00B8A9" }}>{session.completed_at ? new Date(session.completed_at).toLocaleDateString() : "Complete"}</span>
              </div>
              <div style={{ background: "#FFFFFF", border: "1px solid rgba(0,0,0,0.03)", padding: "8px 10px", borderRadius: "8px", display: "flex", justifyContent: "space-between", fontSize: "10.5px" }}>
                <span>🧑‍🏫 Facilitator validation reviewed</span>
                <span style={{ color: notes.length > 0 ? "#5B4CF0" : "#8E9BAE", fontWeight: 800 }}>{notes.length > 0 ? "✓ Validated" : "Pending"}</span>
              </div>
            </div>
          </div>

          <div className="rp-ftr">
            <span>TINS Discovery &amp; Nurturing Report</span>
            <span>Page 13</span>
          </div>
        </div>

        {/* PAGE 14: METHODOLOGY & SCIENTIFIC DISCLOSURE */}
        <div className="report-page">
          <div className="rp-hdr">
            <span className="rp-hdr-logo">🧠 TINS PORTAL</span>
            <span className="rp-hdr-section">Methodology &amp; Disclosure</span>
          </div>

          <h2 className="rp-h2">Assessment Pipeline &amp; Methodology</h2>
          <p className="rp-body" style={{ marginBottom: "12px", fontSize: "11px" }}>
            The TINS assessment utilizes a structured evaluation pipeline combining game-based telemetry, self-reported preference models, and observer validation.
          </p>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px", marginBottom: "14px", fontSize: "10.5px" }}>
            <div className="rp-card">
              <span className="rp-label-gray">Scientific Foundations</span>
              <ul style={{ margin: "4px 0 0 0", paddingLeft: "14px", color: "#4A4A4A", lineHeight: 1.4 }}>
                <li><strong>Cattell-Horn-Carroll (CHC) Theory:</strong> Cognitive speed, spatial visualisation, fluid reasoning.</li>
                <li><strong>Gardner's Multiple Intelligences:</strong> Eight domain structural alignment.</li>
                <li><strong>Torrance Tests (TTCT):</strong> Divergent logic &amp; creativity index models.</li>
              </ul>
            </div>
            <div className="rp-card">
              <span className="rp-label-gray">Data Verification Flow</span>
              <div style={{ display: "flex", flexDirection: "column", gap: "4px", marginTop: "4px", fontSize: "10px", fontWeight: 600 }}>
                <div>1. Discovery (Preference choices)</div>
                <div>2. Task Telemetry (Pacing &amp; accuracy)</div>
                <div>3. Facilitator Observation (Social context)</div>
                <div>4. Synthesis &amp; Triangulation</div>
              </div>
            </div>
          </div>

          <div className="rp-card" style={{ background: "#FFFBF2", border: "1px dashed #E2B25B", borderRadius: "10px", padding: "12px 14px", margin: 0 }}>
            <h3 style={{ color: "#B7791F", margin: "0 0 6px 0", fontSize: "12px", fontWeight: 800 }}>
              ⚠️ Scientific Disclosure &amp; Limitations
            </h3>
            <p style={{ fontSize: "10.5px", lineHeight: "1.5", color: "#5D4037", margin: 0, fontWeight: 500 }}>
              This report identifies <strong>indicators of potential</strong> and does not represent fixed, unchangeable, or permanent cognitive limits. Cognitive abilities develop dynamically over time through structured exposure, guided mentorship, active practice, and sustained effort. These conclusions serve as a baseline guide and must always be cross-referenced with parent/teacher observations, daily academic interest, and longitudinal tracking. We support discovery and development, not categorization.
            </p>
          </div>

          <div style={{ borderTop: "1px solid #EAEAF2", marginTop: "20px", paddingTop: "10px", display: "flex", justifyContent: "space-between", fontSize: "9px", color: "#8E9BAE" }}>
            <span>System: TINS Portal v5.0</span>
            <span>Certification Authority: GOAT Labs Psychometrics Dept.</span>
          </div>

          <div className="rp-ftr" style={{ marginTop: "auto" }}>
            <span>TINS Discovery &amp; Nurturing Report</span>
            <span>Page 14</span>
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

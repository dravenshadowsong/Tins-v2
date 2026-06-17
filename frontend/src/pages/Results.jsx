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
    Object.entries(integ).forEach(([domain, talent_score]) => {
      const exp_val = child?.[`exp_${domain}`] !== undefined ? child[`exp_${domain}`] : 1;
      const exposure_score = Math.round((exp_val / 3) * 100);
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

      {/* ── PRINT VIEW: 12-PAGE BOOKLET ── */}
      <div className="report-container">
        
        {/* PAGE 1: COVER PAGE */}
        <div id="print-page-1" className="report-page cover-page">
          <div className="cover-header">
            <span style={{ fontWeight: 900, fontSize: "16px", letterSpacing: "1px" }}>GOAT LABS</span>
            <span style={{ fontWeight: 900, fontSize: "16px", letterSpacing: "1px" }}>GOAT V4</span>
          </div>
          <div className="cover-hero">
            🧠 ✨ 🚀
          </div>
          <div className="cover-title-group">
            <h1>GOAT Talent Discovery &amp; Development Report</h1>
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
              <strong>Assessment ID:</strong> GOAT-S{session.id}<br />
              <strong>Facilitator:</strong> {notes[0]?.facilitator || "GOAT Mentor"}
            </div>
          </div>
        </div>

        {/* PAGE 2: EXECUTIVE SUMMARY (WHO IS THIS CHILD?) */}
        <div className="report-page">
          <div>
            <div className="report-page-header">
              <span className="logo-group">🧠 GOAT</span>
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
            <span>GOAT Discovery &amp; Nurturing Report</span>
            <span>Page 2</span>
          </div>
        </div>

        {/* PAGE 3: TALENT MAP */}
        <div className="report-page">
          <div>
            <div className="report-page-header">
              <span className="logo-group">🧠 GOAT</span>
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
            <span>GOAT Discovery &amp; Nurturing Report</span>
            <span>Page 3</span>
          </div>
        </div>

        {/* PAGE 4: EVIDENCE BEHIND THE RESULTS */}
        <div className="report-page">
          <div>
            <div className="report-page-header">
              <span className="logo-group">🧠 GOAT</span>
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
            <span>GOAT Discovery &amp; Nurturing Report</span>
            <span>Page 4</span>
          </div>
        </div>

        {/* PAGE 5: UNTAPPED POTENTIAL REPORT */}
        <div className="report-page">
          <div>
            <div className="report-page-header">
              <span className="logo-group">🧠 GOAT</span>
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
            <span>GOAT Discovery &amp; Nurturing Report</span>
            <span>Page 5</span>
          </div>
        </div>

        {/* PAGE 6: CHILD PROFILE (THE PERSONA) */}
        <div className="report-page">
          <div>
            <div className="report-page-header">
              <span className="logo-group">🧠 GOAT</span>
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
            <span>GOAT Discovery &amp; Nurturing Report</span>
            <span>Page 6</span>
          </div>
        </div>

        {/* PAGE 7: PARENT GUIDE */}
        <div className="report-page">
          <div>
            <div className="report-page-header">
              <span className="logo-group">🧠 GOAT</span>
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
            <span>GOAT Discovery &amp; Nurturing Report</span>
            <span>Page 7</span>
          </div>
        </div>

        {/* PAGE 8: 30-DAY DEVELOPMENT PLAN (NEXT STEPS) */}
        <div className="report-page">
          <div>
            <div className="report-page-header">
              <span className="logo-group">🧠 GOAT</span>
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
            <span>GOAT Discovery &amp; Nurturing Report</span>
            <span>Page 8</span>
          </div>
        </div>

        {/* PAGE 9: EXPLORATION PATHWAYS */}
        <div className="report-page">
          <div>
            <div className="report-page-header">
              <span className="logo-group">🧠 GOAT</span>
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
            <span>GOAT Discovery &amp; Nurturing Report</span>
            <span>Page 9</span>
          </div>
        </div>

        {/* PAGE 10: FACILITATOR VALIDATION (MENTOR REVIEW) */}
        <div className="report-page">
          <div>
            <div className="report-page-header">
              <span className="logo-group">🧠 GOAT</span>
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
            <span>GOAT Discovery &amp; Nurturing Report</span>
            <span>Page 10</span>
          </div>
        </div>

        {/* PAGE 11: GROWTH TRACKING */}
        <div className="report-page">
          <div>
            <div className="report-page-header">
              <span className="logo-group">🧠 GOAT</span>
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
            <span>GOAT Discovery &amp; Nurturing Report</span>
            <span>Page 11</span>
          </div>
        </div>

        {/* PAGE 12: METHODOLOGY & SCIENTIFIC DISCLOSURE */}
        <div className="report-page">
          <div>
            <div className="report-page-header">
              <span className="logo-group">🧠 GOAT</span>
              <span className="report-section-name">Methodology &amp; Disclosure</span>
            </div>
            <h2 style={{ fontSize: "18px", fontWeight: 800, color: "#5B4CF0", margin: "0 0 10px 0" }}>ASSESSMENT METHODOLOGY</h2>
            <p style={{ fontSize: "12px", lineHeight: "1.5", color: "#57606F", margin: "0 0 16px 0" }}>
              GOAT uses a multi-faceted approach. Natural behavior, decision styles, and cognitive speed are analyzed dynamically through standardized puzzle banks.
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
            <span>GOAT Discovery &amp; Nurturing Report</span>
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

import { useNavigate } from "react-router-dom";

export default function Welcome() {
  const navigate = useNavigate();

  const handleScroll = (id) => {
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: "smooth" });
    }
  };

  return (
    <div className="landing-container">
      {/* ── STICKY BLURRED NAVIGATION BAR ──────────────────────────────── */}
      <div className="landing-nav-wrapper">
        <nav className="landing-nav">
          <div className="lnav-logo" onClick={() => handleScroll("home")}>
            <span className="lnav-mark">G</span>
            <span className="lnav-text">GOAT Labs</span>
          </div>
          <div className="lnav-links">
            <button onClick={() => handleScroll("home")}>Home</button>
            <button onClick={() => handleScroll("features")}>Talent Domains</button>
            <button onClick={() => handleScroll("how-it-works")}>Assessment Quest</button>
          </div>
          <button className="btn btn-teal btn-sm" onClick={() => navigate("/intake")}>
            Get Started
          </button>
        </nav>
      </div>

      {/* ── SECTION: HERO / HOME ───────────────────────────────────────── */}
      <header id="home" className="hero-section">
        <div className="hero-content">
          <div className="welcome-kicker">
            <span className="kicker-dot" /> Greatest of All Talents System
          </div>
          <h1>
            Discover the <br />
            <span className="gradient-text">Greatest of All Talents</span> <br />
            in Every Child!
          </h1>
          <p className="hero-lead">
            Welcome to the GOAT Lab! An evidence-grounded, culturally fair, and literacy-independent cognitive quest designed for children aged <strong>9–15</strong>.
          </p>
          <div className="hero-actions">
            <button className="btn btn-primary btn-lg pulse-button" onClick={() => navigate("/intake")}>
              Begin Quest 🚀
            </button>
            <button className="btn btn-outline btn-lg" onClick={() => handleScroll("features")}>
              Talent Domains 🧬
            </button>
          </div>
        </div>
        
        <div className="hero-visual">
          <div className="radar-glass-card">
            <div className="radar-header">
              <span className="radar-pill">Ages 9–15</span>
              <h4>Psychological Profile Radar</h4>
            </div>
            <div className="radar-image-container">
              <img 
                src="/psychological_profile_radar.png" 
                alt="Psychological Profiling Radar" 
                className="radar-img" 
              />
            </div>
            <div className="radar-badge-row">
              <span>🧠 8 Domains</span>
              <span>🔬 CHC Model</span>
            </div>
          </div>
        </div>
      </header>

      {/* ── SECTION: THE 8 TALENT DOMAINS ──────────────────────────────── */}
      <section id="features" className="section-container bg-surface">
        <div className="section-header-center">
          <div className="section-label">THE GOAT LABORATORY</div>
          <h2>Our 8 Core Intelligence Domains</h2>
          <p>
            We measure raw human potential and natural learning speeds rather than socio-economic exposure or privileged academic training.
          </p>
        </div>

        <div className="domain-cards-grid">
          {[
            {
              icon: "🏃",
              title: "Kinesthetic & Physical",
              basis: "Gardner Bodily-Kinesthetic · CHC Gp (Psychomotor)",
              subs: "Athletics, Dance, Fine Motor Crafts",
              desc: "Measures visual-motor coordination speed and physical kinetic intuition."
            },
            {
              icon: "🎨",
              title: "Creative & Artistic",
              basis: "Gardner Musical · Torrance TTCT · CHC Gr (Retrieval)",
              subs: "Visual Art, Music, Non-linear Ideas",
              desc: "Evaluates cognitive flexibility, visual recall, and non-linear divergent thinking."
            },
            {
              icon: "🧠",
              title: "Logical & Analytical",
              basis: "CHC Fluid Intelligence (Gf) · Raven's Matrices",
              subs: "Math Reasoning, Patterns, Coding logic",
              desc: "Assesses pattern induction, mental arithmetic, and logical sequence tracking."
            },
            {
              icon: "🔧",
              title: "Spatial & Making",
              basis: "Gardner Spatial · CHC Visual-Spatial (Gv)",
              subs: "Building, Design, Mechanical blueprints",
              desc: "Tests structural visualization, 3D mental rotation, and mechanical intuition."
            },
            {
              icon: "🤝",
              title: "Social & Leadership",
              basis: "Gardner Interpersonal · Mayer-Salovey EQ",
              subs: "Empathy, Conflict Resolution, Teamwork",
              desc: "Measures emotional intelligence, collaborative leadership, and peer coordination."
            },
            {
              icon: "💬",
              title: "Language & Communication",
              basis: "Gardner Linguistic · CHC Gc (Crystallized)",
              subs: "Verbal Expression, Storytelling, Analogies",
              desc: "Evaluates narrative sequencing, verbal analogies, and vocabulary relations."
            },
            {
              icon: "🌱",
              title: "Naturalist & Environmental",
              basis: "Gardner Naturalist · Ecosystem Taxonomy",
              subs: "Living Systems, Animal Empathy, Ecology",
              desc: "Tests ecological balance prediction, nature observation, and classification."
            },
            {
              icon: "🪞",
              title: "Intrapersonal & Reflective",
              basis: "Gardner Intrapersonal · DMGT Catalysts",
              subs: "Self-Regulation, Reflection, Grit",
              desc: "Measures mindfulness, resilience signals, and cognitive frustration management."
            }
          ].map((d, i) => (
            <div className="domain-highlight-card" key={i}>
              <div className="dcard-header">
                <span className="dcard-emoji">{d.icon}</span>
                <div>
                  <h4>{d.title}</h4>
                  <span className="dcard-basis">{d.basis}</span>
                </div>
              </div>
              <p className="dcard-desc">{d.desc}</p>
              <div className="dcard-subs">
                <strong>Focus:</strong> {d.subs}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ── SECTION: QUEST JOURNEY (HOW IT WORKS) ──────────────────────── */}
      <section id="how-it-works" className="section-container">
        <div className="section-header-center">
          <div className="section-label">THE ADVENTURE ROADMAP</div>
          <h2>Your 5-Phase Cognitive Quest</h2>
          <p>
            GOAT builds a dynamic, gamified path from raw childhood aptitude to direct professional mentoring.
          </p>
        </div>

        <div className="quest-journey-timeline">
          {[
            {
              step: "01",
              title: "Background Intake",
              desc: "A facilitator logs details and exposure parameters. We calculate a baseline so underprivileged kids with zero device access are scored fairly.",
              emoji: "📝",
              color: "#6C5CE7"
            },
            {
              step: "02",
              title: "12-Question Discovery",
              desc: "A 100% balanced, everyday preference questionnaire. Zero reading blockages; strictly maps children's interests to the 8 domains.",
              emoji: "🎯",
              color: "#00B894"
            },
            {
              step: "03",
              title: "AI Custom Assessment",
              desc: "Our backend AI (Google Gemini) constructs 8 interactive puzzles customized to their native language, exposure levels, and age (9–15).",
              emoji: "🧩",
              color: "#FF7675"
            },
            {
              step: "04",
              title: "Facilitator Calibration",
              desc: "GOAT mentors spend 10 minutes checking in with the child, verifying score integrity against test anxiety or language gaps.",
              emoji: "🤝",
              color: "#FDCB6E"
            },
            {
              step: "05",
              title: "Mentorship Matching",
              desc: "We match top cognitive score domains directly with local experts and craft mentors (art, logic, mechanics, leadership) for structured growth.",
              emoji: "🏆",
              color: "#0984E3"
            }
          ].map((s, i) => (
            <div className="quest-step-card" key={i} style={{ "--step-color": s.color }}>
              <div className="qstep-num-bg">{s.step}</div>
              <div className="qstep-emoji">{s.emoji}</div>
              <h3>{s.title}</h3>
              <p>{s.desc}</p>
            </div>
          ))}
        </div>

        <div className="assessment-banner-cta">
          <h2>Ready to unlock your child's natural talent profile?</h2>
          <p>The assessment quest takes about 20 minutes in simple Hindi or English.</p>
          <button className="btn btn-teal btn-lg pulse-button" onClick={() => navigate("/intake")}>
            Start My Quest Now ⚡
          </button>
        </div>
      </section>

      {/* ── SECTION: SCIENTIFIC CREDIBILITY NOTE MOVED TO MASTER ADMIN PORTAL ── */}

      {/* ── LANDING PAGE CSS STYLING ──────────────────────────────────── */}
      <style>{`
        .landing-container {
          background: #F4F7FC;
          color: #2D3436;
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
          overflow-x: hidden;
        }
        
        /* Sticky blurred nav */
        .landing-nav-wrapper {
          position: sticky;
          top: 0;
          z-index: 1000;
          background: rgba(255, 255, 255, 0.85);
          backdrop-filter: blur(20px);
          -webkit-backdrop-filter: blur(20px);
          border-bottom: 1px solid rgba(108, 92, 231, 0.12);
        }
        .landing-nav {
          max-width: 1140px;
          margin: 0 auto;
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 12px 24px;
          height: 70px;
        }
        .lnav-logo {
          display: flex;
          align-items: center;
          gap: 10px;
          cursor: pointer;
        }
        .lnav-mark {
          width: 36px;
          height: 36px;
          background: linear-gradient(135deg, #6C5CE7 0%, #a29bfe 100%);
          color: #FFFFFF;
          font-weight: 900;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: 10px;
          box-shadow: 0 4px 12px rgba(108, 92, 231, 0.3);
        }
        .lnav-text {
          font-weight: 800;
          font-size: 20px;
          background: linear-gradient(135deg, #6C5CE7 0%, #00B894 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
        }
        .lnav-links {
          display: flex;
          gap: 24px;
        }
        .lnav-links button {
          background: none;
          border: none;
          color: #57606F;
          font-weight: 700;
          font-size: 14.5px;
          cursor: pointer;
          transition: color 0.2s, transform 0.2s;
        }
        .lnav-links button:hover {
          color: #6C5CE7;
          transform: translateY(-1px);
        }

        /* Hero Section Redesign */
        .hero-section {
          max-width: 1140px;
          margin: 0 auto;
          padding: 80px 24px;
          display: grid;
          grid-template-columns: 1.1fr 0.9fr;
          align-items: center;
          gap: 60px;
          min-height: calc(100vh - 70px);
        }
        .welcome-kicker {
          display: inline-flex;
          align-items: center;
          gap: 8px;
          background: rgba(108, 92, 231, 0.08);
          color: #6C5CE7;
          padding: 6px 14px;
          border-radius: 20px;
          font-size: 13.5px;
          font-weight: 700;
          border: 1px solid rgba(108, 92, 231, 0.12);
        }
        .kicker-dot {
          width: 8px;
          height: 8px;
          background: #00B894;
          border-radius: 50%;
          display: inline-block;
          box-shadow: 0 0 8px #00B894;
        }
        .hero-content h1 {
          font-size: 52px;
          line-height: 1.15;
          font-weight: 900;
          color: #2D3436;
          margin-top: 20px;
          margin-bottom: 24px;
          letter-spacing: -0.02em;
        }
        .gradient-text {
          background: linear-gradient(135deg, #6C5CE7 0%, #00B894 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
        }
        .hero-lead {
          font-size: 19px;
          color: #57606F;
          line-height: 1.65;
          margin-bottom: 36px;
        }
        .hero-actions {
          display: flex;
          gap: 16px;
        }
        
        /* Modern Glass Card Visual */
        .hero-visual {
          display: flex;
          justify-content: center;
          align-items: center;
        }
        .radar-glass-card {
          background: #FFFFFF;
          border: 1px solid rgba(108, 92, 231, 0.12);
          border-radius: 24px;
          padding: 24px;
          box-shadow: 0 20px 40px rgba(108, 92, 231, 0.08);
          max-width: 380px;
          width: 100%;
          transform: rotate(2deg);
          transition: transform 0.3s ease;
        }
        .radar-glass-card:hover {
          transform: rotate(0deg) scale(1.02);
        }
        .radar-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 16px;
        }
        .radar-pill {
          background: #E8F0FE;
          color: #1A73E8;
          font-size: 11px;
          font-weight: 800;
          padding: 4px 10px;
          border-radius: 20px;
        }
        .radar-header h4 {
          font-size: 13px;
          font-weight: 800;
          color: #8E9BAE;
          margin: 0;
          text-transform: uppercase;
        }
        .radar-image-container {
          background: #F8F9FE;
          border-radius: 18px;
          padding: 16px;
          border: 1px solid rgba(108, 92, 231, 0.06);
          margin-bottom: 16px;
        }
        .radar-img {
          width: 100%;
          height: auto;
          display: block;
        }
        .radar-badge-row {
          display: flex;
          gap: 8px;
        }
        .radar-badge-row span {
          flex: 1;
          background: #EEECFF;
          color: #6C5CE7;
          text-align: center;
          font-size: 12px;
          font-weight: 700;
          padding: 8px;
          border-radius: 12px;
        }

        /* Generic Container */
        .section-container {
          max-width: 1140px;
          margin: 0 auto;
          padding: 90px 24px;
        }
        .bg-surface {
          background: #FFFFFF;
          border-top: 1px solid rgba(108, 92, 231, 0.08);
          border-bottom: 1px solid rgba(108, 92, 231, 0.08);
          max-width: 100% !important;
        }
        .bg-surface > .section-container,
        .bg-surface.credibility-note-section {
          max-width: 1140px;
          margin: 0 auto;
        }
        .section-header-center {
          text-align: center;
          max-width: 720px;
          margin: 0 auto 60px;
        }
        .section-label {
          font-size: 13px;
          font-weight: 900;
          text-transform: uppercase;
          color: #6C5CE7;
          letter-spacing: 0.15em;
          margin-bottom: 10px;
        }
        .section-header-center h2 {
          font-size: 38px;
          font-weight: 900;
          color: #2D3436;
          margin-bottom: 16px;
          letter-spacing: -0.01em;
        }
        .section-header-center p {
          color: #57606F;
          font-size: 17.5px;
          line-height: 1.6;
        }

        /* Domain Cards Grid */
        .domain-cards-grid {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 24px;
        }
        .domain-highlight-card {
          background: #F8F9FE;
          border: 1px solid rgba(108, 92, 231, 0.08);
          border-radius: 20px;
          padding: 28px;
          box-shadow: 0 4px 20px rgba(108, 92, 231, 0.01);
          transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275), box-shadow 0.3s;
        }
        .domain-highlight-card:hover {
          transform: translateY(-5px);
          box-shadow: 0 16px 36px rgba(108, 92, 231, 0.08);
          border-color: rgba(108, 92, 231, 0.25);
        }
        .dcard-header {
          display: flex;
          align-items: center;
          gap: 16px;
          margin-bottom: 18px;
        }
        .dcard-emoji {
          font-size: 36px;
          background: #FFFFFF;
          width: 56px;
          height: 56px;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: 14px;
          box-shadow: 0 4px 12px rgba(108, 92, 231, 0.06);
        }
        .dcard-header h4 {
          font-size: 19px;
          font-weight: 850;
          color: #2D3436;
          margin: 0;
        }
        .dcard-basis {
          font-size: 11px;
          color: #6C5CE7;
          font-weight: 750;
          display: block;
          margin-top: 3px;
        }
        .dcard-desc {
          font-size: 14.5px;
          color: #57606F;
          margin-bottom: 18px;
          line-height: 1.6;
        }
        .dcard-subs {
          font-size: 12.5px;
          color: #8E9BAE;
        }

        /* Quest Journey Timeline Redesign (Fascinating Playboard) */
        .quest-journey-timeline {
          display: grid;
          grid-template-columns: repeat(5, 1fr);
          gap: 18px;
          margin-bottom: 60px;
          position: relative;
        }
        .quest-step-card {
          background: #FFFFFF;
          border: 1px solid rgba(108, 92, 231, 0.1);
          border-radius: 22px;
          padding: 24px;
          position: relative;
          box-shadow: 0 10px 25px rgba(108, 92, 231, 0.03);
          transition: transform 0.25s ease, border-color 0.25s ease;
        }
        .quest-step-card:hover {
          transform: translateY(-4px);
          border-color: var(--step-color);
        }
        .qstep-num-bg {
          font-size: 40px;
          font-weight: 950;
          color: rgba(108, 92, 231, 0.06);
          line-height: 1;
          position: absolute;
          top: 14px;
          right: 20px;
        }
        .qstep-emoji {
          font-size: 28px;
          margin-bottom: 16px;
          background: rgba(108, 92, 231, 0.05);
          width: 50px;
          height: 50px;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: 12px;
        }
        .quest-step-card h3 {
          font-size: 15px;
          font-weight: 850;
          color: #2D3436;
          margin-bottom: 8px;
        }
        .quest-step-card p {
          font-size: 12.5px;
          color: #57606F;
          line-height: 1.55;
        }

        /* Call To Action Banner */
        .assessment-banner-cta {
          background: linear-gradient(135deg, #EEECFF 0%, #E3FCF5 100%);
          border: 1px solid rgba(108, 92, 231, 0.18);
          border-radius: 24px;
          padding: 50px 36px;
          text-align: center;
          max-width: 840px;
          margin: 0 auto;
          box-shadow: 0 12px 35px rgba(108, 92, 231, 0.08);
        }
        .assessment-banner-cta h2 {
          font-size: 28px;
          font-weight: 900;
          color: #6C5CE7;
          margin-bottom: 10px;
        }
        .assessment-banner-cta p {
          font-size: 16px;
          color: #57606F;
          margin-bottom: 28px;
        }
        
        .pulse-button {
          box-shadow: 0 0 0 0 rgba(108, 92, 231, 0.6);
          animation: pulse 2s infinite;
        }
        @keyframes pulse {
          0% {
            box-shadow: 0 0 0 0 rgba(108, 92, 231, 0.4);
          }
          70% {
            box-shadow: 0 0 0 12px rgba(108, 92, 231, 0);
          }
          100% {
            box-shadow: 0 0 0 0 rgba(108, 92, 231, 0);
          }
        }



        /* Responsive Design */
        @media (max-width: 960px) {
          .hero-section {
            grid-template-columns: 1fr;
            padding: 50px 24px;
            gap: 40px;
            text-align: center;
          }
          .hero-content h1 {
            font-size: 42px;
          }
          .hero-actions {
            justify-content: center;
          }
          .domain-cards-grid {
            grid-template-columns: 1fr;
          }
          .quest-journey-timeline {
            grid-template-columns: 1fr;
            gap: 16px;
          }
          .roadmap-grid {
            grid-template-columns: 1fr;
          }
        }
        @media (max-width: 600px) {
          .lnav-links {
            display: none;
          }
          .hero-content h1 {
            font-size: 34px;
          }
        }
      `}</style>
    </div>
  );
}

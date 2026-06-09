# GOAT — Greatest of All Talents System


---

## What this is
A full-stack web application for identifying and nurturing talent in underprivileged children aged 10–15.
Runs entirely offline on any laptop or tablet. No internet required after setup.

---

## Tech stack
- **Frontend:** React + Vite (runs in browser)
- **Backend:** Python Flask (API server)
- **Database:** SQLite (single file, zero setup)

---

## First-time setup

### 1. Install Node.js
Download from https://nodejs.org — choose the LTS version.

### 2. Install Python dependencies (Flask is likely already installed)
```bash
pip install flask --break-system-packages
```

### 3. Install frontend dependencies
```bash
cd tins_v2/frontend
npm install
cd ..
```

---

## Running the system

You need TWO terminal windows open at the same time.

### Terminal 1 — Backend
```bash
cd tins_v2/backend
python3 server.py
```
You should see: `✅  GOAT backend running at http://localhost:5050`

### Terminal 2 — Frontend
```bash
cd tins_v2/frontend
npm run dev
```
You should see: `Local: http://localhost:5173`

### Open in browser
Go to: **http://localhost:5173**

---

## How to use

### For a child assessment:
1. Click **Begin Assessment**
2. Fill in the child's name, age, language, and prior exposure
3. Complete 4 quick discovery questions (picture-based)
4. Complete the deep assessment (scaled 1–5 questions per domain)
5. See the results — top talent domain with full score breakdown

### For a facilitator:
1. After results, click **Facilitator Review**
2. Add your observation, confirm or override the system result
3. Proceed to **Mentor Matching** to connect the child with a mentor
4. Track progress via the **Dashboard**

---

## File structure
```
tins_v2/
├── backend/
│   ├── server.py          ← Flask API + scoring engine
│   └── db/
│       └── goat.db        ← SQLite database (auto-created on first run)
└── frontend/
    └── src/
        ├── pages/
        │   ├── Welcome.jsx
        │   ├── Intake.jsx         ← Child profile + exposure
        │   ├── Discovery.jsx      ← Phase 2: quick questions
        │   ├── DeepAssessment.jsx ← Phase 3: 30+ questions
        │   ├── Results.jsx        ← Scores + insights
        │   ├── Facilitator.jsx    ← Phase 4: human validation
        │   ├── MentorMatch.jsx    ← Phase 5: match + plan
        │   └── Dashboard.jsx      ← All children + stats
        ├── data/
        │   └── questions.js       ← All assessment questions
        ├── api.js                 ← Backend API calls
        └── App.css                ← All styles
```

---

## The 8 talent domains
1. 🤸 Kinesthetic & Physical
2. 🎨 Creative & Artistic
3. 🧠 Logical & Analytical
4. 🔧 Spatial & Making
5. 🤝 Social & Leadership
6. 💬 Language & Communication
7. 🌱 Naturalist & Environmental
8. 🪞 Intrapersonal & Reflective

---

## Scoring
- **TQ score:** Weighted average of 16–22 ability sub-components per domain (0–100)
- **Exposure correction:** Children with zero prior exposure get a boost multiplier (1.18×)
- **Integrated score:** 70% TQ + 15% EQ + 15% Visualizer score

---

Built for GOAT Labs. May 2026.

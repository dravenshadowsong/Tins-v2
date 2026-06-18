// GOAT Assessment Questions for V5 Rebuild
// Auto-generated from extended_bank.json. Do not edit directly.

export const DOMAINS = {
  kinesthetic:   { label: 'Kinesthetic & Physical',     emoji: '🏃', color: '#0F6E56', light: '#E1F5EE' },
  creative:      { label: 'Creative & Artistic',        emoji: '🎨', color: '#993556', light: '#FBEAF0' },
  logical:       { label: 'Logical & Analytical',       emoji: '🧠', color: '#185FA5', light: '#E6F1FB' },
  spatial:       { label: 'Spatial & Making',           emoji: '🔧', color: '#854F0B', light: '#FAEEDA' },
  social:        { label: 'Social & Leadership',        emoji: '🤝', color: '#534AB7', light: '#EEEDFE' },
  language:      { label: 'Language & Communication',   emoji: '💬', color: '#993C1D', light: '#FAECE7' },
  naturalist:    { label: 'Naturalist & Environmental', emoji: '🌱', color: '#3B6D11', light: '#EAF3DE' },
  intrapersonal: { label: 'Intrapersonal & Reflective', emoji: '🪞', color: '#5F5E5A', light: '#F1EFE8' },
};

export const EQ_QUESTIONS = [
  { key: 'eq_overall', q: 'Overall, how well do you understand and manage your own feelings?', type: 'scale', low: 'Struggle a lot', high: 'Very well' },
];

export const VISUALIZER_QUESTIONS = [
  { key: 'visualizer_overall', q: 'When you imagine something in your mind - a room, a face, a place - how clearly can you see it?', type: 'scale', low: 'Very fuzzy', high: 'Like a photograph' },
];

export const DISCOVERY_QUESTIONS = [
  {
    id: "q_discovery_1",
    question: "You get one free afternoon. What sounds most fun?",
    type: 'choice',
    options: [
      { label: "Tell or write a story", emoji: "\ud83d\udde3\ufe0f", domains: ["language", "creative"] },
      { label: "Solve a tricky puzzle", emoji: "\ud83e\udde9", domains: ["logical", "spatial"] },
      { label: "Organize a group game", emoji: "\ud83e\udd1d", domains: ["social", "language"] },
      { label: "Plan a personal goal", emoji: "\ud83e\udd14", domains: ["intrapersonal"] },
    ]
  },
  {
    id: "q_discovery_2",
    question: "You receive a box of cardboard and sticks. What do you do?",
    type: 'choice',
    options: [
      { label: "Design an artistic toy castle", emoji: "\ud83c\udfa8", domains: ["creative", "spatial"] },
      { label: "Build a model bridge", emoji: "\ud83d\udd28", domains: ["spatial", "logical"] },
      { label: "Invite friends to build together", emoji: "\ud83e\udd1d", domains: ["social", "language"] },
      { label: "Inspect the materials quietly", emoji: "\ud83e\udd14", domains: ["intrapersonal"] },
    ]
  },
  {
    id: "q_discovery_3",
    question: "You see a strange pattern of lights on a building. What do you do?",
    type: 'choice',
    options: [
      { label: "Try to figure out the code", emoji: "\ud83e\udde9", domains: ["logical", "spatial"] },
      { label: "Draw the pattern in a notebook", emoji: "\ud83c\udfa8", domains: ["creative", "spatial"] },
      { label: "Explain it to a friend", emoji: "\ud83d\udde3\ufe0f", domains: ["language", "social"] },
      { label: "Sit and watch it quietly", emoji: "\ud83e\udd14", domains: ["intrapersonal"] },
    ]
  },
  {
    id: "q_discovery_4",
    question: "If you could design a new playground game, what would it look like?",
    type: 'choice',
    options: [
      { label: "A maze with hidden routes", emoji: "\ud83d\udd28", domains: ["spatial", "logical"] },
      { label: "A physical obstacle course", emoji: "\ud83c\udfc3", domains: ["kinesthetic", "spatial"] },
      { label: "A team game with roles", emoji: "\ud83e\udd1d", domains: ["social", "language"] },
      { label: "A puzzle game for one person", emoji: "\ud83e\udd14", domains: ["intrapersonal"] },
    ]
  },
  {
    id: "q_discovery_5",
    question: "You hear a fast drumbeat. What is your reaction?",
    type: 'choice',
    options: [
      { label: "Dance or clap to the rhythm", emoji: "\ud83c\udfc3", domains: ["kinesthetic", "creative"] },
      { label: "Listen to the pattern of beats", emoji: "\ud83e\udde9", domains: ["logical", "naturalist"] },
      { label: "Call friends to join in", emoji: "\ud83e\udd1d", domains: ["social", "language"] },
      { label: "Close eyes and feel the music", emoji: "\ud83e\udd14", domains: ["intrapersonal"] },
    ]
  },
  {
    id: "q_discovery_6",
    question: "You find a sick plant in the garden. What do you do?",
    type: 'choice',
    options: [
      { label: "Inspect leaves and add soil", emoji: "\ud83c\udf31", domains: ["naturalist", "logical"] },
      { label: "Draw the leaves in a diary", emoji: "\ud83c\udfa8", domains: ["creative", "naturalist"] },
      { label: "Ask a teacher to help solve it", emoji: "\ud83d\udde3\ufe0f", domains: ["language", "social"] },
      { label: "Quietly wonder how it grows", emoji: "\ud83e\udd14", domains: ["intrapersonal"] },
    ]
  },
  {
    id: "q_discovery_7",
    question: "A classmate is feeling lonely at lunch break. What do you do?",
    type: 'choice',
    options: [
      { label: "Go sit, talk, and tell jokes", emoji: "\ud83d\udde3\ufe0f", domains: ["language", "social"] },
      { label: "Invite them to a sports game", emoji: "\ud83c\udfc3", domains: ["kinesthetic", "social"] },
      { label: "Think about how they feel", emoji: "\ud83e\udd14", domains: ["intrapersonal"] },
      { label: "Invent a two-person game", emoji: "\ud83c\udfa8", domains: ["creative", "social"] },
    ]
  },
  {
    id: "q_discovery_8",
    question: "When you make a mistake in a drawing or project, what do you do?",
    type: 'choice',
    options: [
      { label: "Calm down and plan how to fix it", emoji: "\ud83e\udd14", domains: ["intrapersonal", "logical"] },
      { label: "Start over with a completely new idea", emoji: "\ud83c\udfa8", domains: ["creative"] },
      { label: "Ask a friend for advice", emoji: "\ud83e\udd1d", domains: ["social", "language"] },
      { label: "Throw it away and walk outside", emoji: "\ud83c\udfc3", domains: ["kinesthetic"] },
    ]
  },
];

export const ASSESSMENT_TASKS = [
  {
    key: "language_race",
    type: "order_steps",
    domain: "language",
    component: "core_deep",
    title: {"English": "Story Order", "Hindi": "\u0915\u0939\u093e\u0928\u0940 \u0915\u093e \u0915\u094d\u0930\u092e"},
    prompt: {"English": "Put these steps in the correct order to tell a story:", "Hindi": "\u0915\u0939\u093e\u0928\u0940 \u092c\u0924\u093e\u0928\u0947 \u0915\u0947 \u0932\u093f\u090f \u0907\u0928 \u091a\u0930\u0923\u094b\u0902 \u0915\u094b \u0938\u0939\u0940 \u0915\u094d\u0930\u092e \u092e\u0947\u0902 \u0930\u0916\u0947\u0902:"},
    steps: {"English": ["We lined up at the starting line.", "The whistle blew and we ran fast.", "I crossed the finish line third.", "We clapped and cheered for the winner."], "Hindi": ["\u0939\u092e \u0936\u0941\u0930\u0941\u0906\u0924\u0940 \u0930\u0947\u0916\u093e \u092a\u0930 \u0916\u0921\u093c\u0947 \u0939\u0941\u090f\u0964", "\u0938\u0940\u091f\u0940 \u092c\u091c\u0940 \u0914\u0930 \u0939\u092e \u0924\u0947\u091c\u0940 \u0938\u0947 \u0926\u094c\u0921\u093c\u0947\u0964", "\u092e\u0948\u0902\u0928\u0947 \u0924\u0940\u0938\u0930\u0947 \u0938\u094d\u0925\u093e\u0928 \u092a\u0930 \u092b\u093f\u0928\u093f\u0936 \u0932\u093e\u0907\u0928 \u092a\u093e\u0930 \u0915\u0940\u0964", "\u0939\u092e\u0928\u0947 \u0935\u093f\u091c\u0947\u0924\u093e \u0915\u0947 \u0932\u093f\u090f \u0924\u093e\u0932\u093f\u092f\u093e\u0901 \u092c\u091c\u093e\u0908\u0902\u0964"]},
    shuffled: {"English": ["We clapped and cheered for the winner.", "We lined up at the starting line.", "I crossed the finish line third.", "The whistle blew and we ran fast."], "Hindi": ["\u0939\u092e\u0928\u0947 \u0935\u093f\u091c\u0947\u0924\u093e \u0915\u0947 \u0932\u093f\u090f \u0924\u093e\u0932\u093f\u092f\u093e\u0901 \u092c\u091c\u093e\u0908\u0902\u0964", "\u0939\u092e \u0936\u0941\u0930\u0941\u0906\u0924\u0940 \u0930\u0947\u0916\u093e \u092a\u0930 \u0916\u0921\u093c\u0947 \u0939\u0941\u090f\u0964", "\u092e\u0948\u0902\u0928\u0947 \u0924\u0940\u0938\u0930\u0947 \u0938\u094d\u0925\u093e\u0928 \u092a\u0930 \u092b\u093f\u0928\u093f\u0936 \u0932\u093e\u0907\u0928 \u092a\u093e\u0930 \u0915\u0940\u0964", "\u0938\u0940\u091f\u0940 \u092c\u091c\u0940 \u0914\u0930 \u0939\u092e \u0924\u0947\u091c\u0940 \u0938\u0947 \u0926\u094c\u0921\u093c\u0947\u0964"]},
    metric: "sequence_accuracy",
    difficulty: "easy",
    ai_interpretation_notes: "Story building sequencing task."
  },
  {
    key: "language_explain_game",
    type: "choice",
    domain: "language",
    component: "core_deep",
    title: {"English": "Teaching a Game", "Hindi": "\u0916\u0947\u0932 \u0938\u093f\u0916\u093e\u0928\u093e"},
    prompt: {"English": "You want to teach a new Class 1 student how to play your favorite playground game. What is the best way to explain it?", "Hindi": "\u0906\u092a \u092a\u0939\u0932\u0940 \u0915\u0915\u094d\u0937\u093e \u0915\u0947 \u090f\u0915 \u0928\u090f \u091b\u093e\u0924\u094d\u0930 \u0915\u094b \u0905\u092a\u0928\u093e \u092a\u0938\u0902\u0926\u0940\u0926\u093e \u0916\u0947\u0932 \u0938\u093f\u0916\u093e\u0928\u093e \u091a\u093e\u0939\u0924\u0947 \u0939\u0948\u0902\u0964 \u0907\u0938\u0947 \u0938\u092e\u091d\u093e\u0928\u0947 \u0915\u093e \u0938\u092c\u0938\u0947 \u0905\u091a\u094d\u091b\u093e \u0924\u0930\u0940\u0915\u093e \u0915\u094d\u092f\u093e \u0939\u0948?"},
    options: [{"label": {"English": "Show them the actions slowly and play a practice round together", "Hindi": "\u0909\u0928\u094d\u0939\u0947\u0902 \u0927\u0940\u0930\u0947-\u0927\u0940\u0930\u0947 \u0907\u0936\u093e\u0930\u094b\u0902 \u0938\u0947 \u0938\u092e\u091d\u093e\u090f\u0902 \u0914\u0930 \u0938\u093e\u0925 \u092e\u0947\u0902 \u090f\u0915 \u0905\u092d\u094d\u092f\u093e\u0938 \u0916\u0947\u0932 \u0916\u0947\u0932\u0947\u0902"}, "value": 4}, {"label": {"English": "Read the full rulebook to them very quickly", "Hindi": "\u0928\u093f\u092f\u092e\u094b\u0902 \u0915\u0940 \u092a\u0942\u0930\u0940 \u0915\u093f\u0924\u093e\u092c \u0909\u0928\u094d\u0939\u0947\u0902 \u092c\u0939\u0941\u0924 \u0924\u0947\u091c\u0940 \u0938\u0947 \u092a\u0922\u093c\u0915\u0930 \u0938\u0941\u0928\u093e\u090f\u0902"}, "value": 1}, {"label": {"English": "Tell them to watch other students play from far away", "Hindi": "\u0909\u0928\u094d\u0939\u0947\u0902 \u0926\u0942\u0930 \u0938\u0947 \u0905\u0928\u094d\u092f \u091b\u093e\u0924\u094d\u0930\u094b\u0902 \u0915\u094b \u0916\u0947\u0932\u0924\u0947 \u0939\u0941\u090f \u0926\u0947\u0916\u0928\u0947 \u0915\u0947 \u0932\u093f\u090f \u0915\u0939\u0947\u0902"}, "value": 2}, {"label": {"English": "Write down a list of rules and give it to them to read", "Hindi": "\u0928\u093f\u092f\u092e\u094b\u0902 \u0915\u0940 \u090f\u0915 \u0938\u0942\u091a\u0940 \u0932\u093f\u0916\u0915\u0930 \u0909\u0928\u094d\u0939\u0947\u0902 \u092a\u0922\u093c\u0928\u0947 \u0915\u0947 \u0932\u093f\u090f \u0926\u0947 \u0926\u0947\u0902"}, "value": 0}],
    answer: "Show them the actions slowly and play a practice round together",
    metric: "correctness",
    difficulty: "easy",
    ai_interpretation_notes: "Situational logic measuring empathetic communication."
  },
  {
    key: "creative_circles",
    type: "idea_list",
    domain: "creative",
    component: "core_deep",
    title: {"English": "Circles Challenge", "Hindi": "\u0917\u094b\u0932\u093e \u091a\u0941\u0928\u094c\u0924\u0940"},
    prompt: {"English": "Imagine 3 empty circles. Write down 3 different and unique things you could draw by adding lines to these circles!", "Hindi": "3 \u0916\u093e\u0932\u0940 \u0917\u094b\u0932\u094b\u0902 (circles) \u0915\u0940 \u0915\u0932\u094d\u092a\u0928\u093e \u0915\u0930\u0947\u0902\u0964 \u0915\u0941\u091b \u0932\u093e\u0907\u0928\u0947\u0902 \u091c\u094b\u0921\u093c\u0915\u0930 \u0906\u092a \u0909\u0928\u0938\u0947 3 \u0905\u0932\u0917 \u0914\u0930 \u0905\u0928\u094b\u0916\u0940 \u091a\u0940\u091c\u0947\u0902 \u0915\u094d\u092f\u093e \u092c\u0928\u093e \u0938\u0915\u0924\u0947 \u0939\u0948\u0902, \u0932\u093f\u0916\u0947\u0902!"},
    minIdeas: 3,
    metric: "fluency",
    difficulty: "adaptive",
    ai_interpretation_notes: "Visual circle transformation test."
  },
  {
    key: "creative_box_situational",
    type: "choice",
    domain: "creative",
    component: "core_deep",
    title: {"English": "Cardboard Box Use", "Hindi": "\u0917\u0924\u094d\u0924\u0947 \u0915\u0947 \u0921\u093f\u092c\u094d\u092c\u0947 \u0915\u093e \u0909\u092a\u092f\u094b\u0917"},
    prompt: {"English": "You find a large, empty cardboard box. What is the most creative way to use it?", "Hindi": "\u0906\u092a\u0915\u094b \u090f\u0915 \u092c\u0921\u093c\u093e, \u0916\u093e\u0932\u0940 \u0917\u0924\u094d\u0924\u0947 \u0915\u093e \u0921\u093f\u092c\u094d\u092c\u093e \u092e\u093f\u0932\u0924\u093e \u0939\u0948\u0964 \u0907\u0938\u0915\u093e \u0909\u092a\u092f\u094b\u0917 \u0915\u0930\u0928\u0947 \u0915\u093e \u0938\u092c\u0938\u0947 \u0930\u091a\u0928\u093e\u0924\u094d\u092e\u0915 \u0924\u0930\u0940\u0915\u093e \u0915\u094d\u092f\u093e \u0939\u0948?"},
    options: [{"label": {"English": "Turn it into a puppet theater with cut-out windows for a show", "Hindi": "\u0907\u0938\u0947 \u090f\u0915 \u092a\u092a\u0947\u091f \u0925\u093f\u092f\u0947\u091f\u0930 (\u0915\u091f\u092a\u0941\u0924\u0932\u0940 \u0925\u093f\u092f\u0947\u091f\u0930) \u092e\u0947\u0902 \u092c\u0926\u0932\u0947\u0902 \u0914\u0930 \u0928\u093e\u091f\u0915 \u0926\u093f\u0916\u093e\u090f\u0902"}, "value": 4}, {"label": {"English": "Use it to store old school notebooks neatly", "Hindi": "\u092a\u0941\u0930\u093e\u0928\u0940 \u0938\u094d\u0915\u0942\u0932 \u0928\u094b\u091f\u092c\u0941\u0915\u094d\u0938 \u0915\u094b \u0930\u0916\u0928\u0947 \u0915\u0947 \u0932\u093f\u090f \u0907\u0938\u0915\u093e \u0909\u092a\u092f\u094b\u0917 \u0915\u0930\u0947\u0902"}, "value": 2}, {"label": {"English": "Flatten it and throw it in the dustbin", "Hindi": "\u0907\u0938\u0947 \u092e\u094b\u0921\u093c\u0915\u0930 \u0915\u091a\u0930\u0947 \u0915\u0947 \u0921\u093f\u092c\u094d\u092c\u0947 \u092e\u0947\u0902 \u092b\u0947\u0902\u0915 \u0926\u0947\u0902"}, "value": 1}, {"label": {"English": "Keep it in the corner of the room empty", "Hindi": "\u0915\u092e\u0930\u0947 \u0915\u0947 \u0915\u094b\u0928\u0947 \u092e\u0947\u0902 \u0907\u0938\u0947 \u0916\u093e\u0932\u0940 \u0930\u0916 \u0926\u0947\u0902"}, "value": 0}],
    answer: "Turn it into a puppet theater with cut-out windows for a show",
    metric: "correctness",
    difficulty: "easy",
    ai_interpretation_notes: "Situational creative divergent thinking."
  },
  {
    key: "logical_lock",
    type: "choice",
    domain: "logical",
    component: "core_deep",
    title: {"English": "Number Lock", "Hindi": "\u0938\u0902\u0916\u094d\u092f\u093e \u0915\u093e \u0924\u093e\u0932\u093e"},
    prompt: {"English": "A number pattern goes: 3, 6, 12, 24, ... What number comes next?", "Hindi": "\u090f\u0915 \u0938\u0902\u0916\u094d\u092f\u093e \u092a\u0948\u091f\u0930\u094d\u0928 \u0907\u0938 \u092a\u094d\u0930\u0915\u093e\u0930 \u0939\u0948: 3, 6, 12, 24, ... \u0905\u0917\u0932\u093e \u0928\u0902\u092c\u0930 \u0915\u094d\u092f\u093e \u0939\u094b\u0917\u093e?"},
    options: [{"label": {"English": "30", "Hindi": "30"}, "value": 0}, {"label": {"English": "48", "Hindi": "48"}, "value": 4}, {"label": {"English": "36", "Hindi": "36"}, "value": 0}, {"label": {"English": "40", "Hindi": "40"}, "value": 0}],
    answer: "48",
    metric: "correctness",
    difficulty: "easy",
    ai_interpretation_notes: "Numerical progression pattern reasoning."
  },
  {
    key: "logical_legs",
    type: "choice",
    domain: "logical",
    component: "core_deep",
    title: {"English": "Animal Legs", "Hindi": "\u091c\u093e\u0928\u0935\u0930\u094b\u0902 \u0915\u0947 \u092a\u0948\u0930"},
    prompt: {"English": "A duck has 2 legs, a dog has 4 legs, and a spider has 8 legs. Which of these fits the pattern of legs (2, 4, 8) increasing?", "Hindi": "\u090f\u0915 \u092c\u0924\u094d\u0924\u0916 \u0915\u0947 2 \u092a\u0948\u0930 \u0939\u094b\u0924\u0947 \u0939\u0948\u0902, \u090f\u0915 \u0915\u0941\u0924\u094d\u0924\u0947 \u0915\u0947 4 \u092a\u0948\u0930 \u0939\u094b\u0924\u0947 \u0939\u0948\u0902, \u0914\u0930 \u090f\u0915 \u092e\u0915\u0921\u093c\u0940 \u0915\u0947 8 \u092a\u0948\u0930 \u0939\u094b\u0924\u0947 \u0939\u0948\u0902\u0964 \u0907\u0928\u092e\u0947\u0902 \u0938\u0947 \u0915\u094c\u0928 \u092a\u0948\u0930\u094b\u0902 \u0915\u0947 \u092c\u0922\u093c\u0924\u0947 \u0939\u0941\u090f \u092a\u0948\u091f\u0930\u094d\u0928 (2, 4, 8) \u092e\u0947\u0902 \u092b\u093f\u091f \u092c\u0948\u0920\u0924\u093e \u0939\u0948?"},
    options: [{"label": {"English": "A sparrow (2 legs), a cat (4 legs), a crab (10 legs)", "Hindi": "\u090f\u0915 \u0917\u094c\u0930\u0948\u092f\u093e (2 \u092a\u0948\u0930), \u090f\u0915 \u092c\u093f\u0932\u094d\u0932\u0940 (4 \u092a\u0948\u0930), \u090f\u0915 \u0915\u0947\u0915\u0921\u093c\u093e (10 \u092a\u0948\u0930)"}, "value": 4}, {"label": {"English": "A snake (0 legs), a monkey (2 legs), a horse (4 legs)", "Hindi": "\u090f\u0915 \u0938\u093e\u0902\u092a (0 \u092a\u0948\u0930), \u090f\u0915 \u092c\u0902\u0926\u0930 (2 \u092a\u0948\u0930), \u090f\u0915 \u0918\u094b\u0921\u093c\u093e (4 \u092a\u0948\u0930)"}, "value": 1}, {"label": {"English": "A fish (0 legs), a bird (2 legs), a spider (8 legs)", "Hindi": "\u090f\u0915 \u092e\u091b\u0932\u0940 (0 \u092a\u0948\u0930), \u090f\u0915 \u092a\u0915\u094d\u0937\u0940 (2 \u092a\u0948\u0930), \u090f\u0915 \u092e\u0915\u0921\u093c\u0940 (8 \u092a\u0948\u0930)"}, "value": 0}, {"label": {"English": "A goat (4 legs), an ant (6 legs), a centipede (many legs)", "Hindi": "\u090f\u0915 \u092c\u0915\u0930\u0940 (4 \u092a\u0948\u0930), \u090f\u0915 \u091a\u0940\u0902\u091f\u0940 (6 \u092a\u0948\u0930), \u090f\u0915 \u0915\u0928\u0916\u091c\u0942\u0930\u093e (\u0915\u0908 \u092a\u0948\u0930)"}, "value": 2}],
    answer: "A sparrow (2 legs), a cat (4 legs), a crab (10 legs)",
    metric: "correctness",
    difficulty: "medium",
    ai_interpretation_notes: "Pattern recognition and classification logic."
  },
  {
    key: "spatial_shape_match",
    type: "choice",
    domain: "spatial",
    component: "core_deep",
    title: {"English": "Corner Blocks", "Hindi": "\u0915\u094b\u0928\u0947 \u0915\u0947 \u092c\u094d\u0932\u0949\u0915"},
    prompt: {"English": "You have a large solid cube with one corner block missing. Which single shape can fit perfectly into the empty corner to make the cube complete?", "Hindi": "\u0906\u092a\u0915\u0947 \u092a\u093e\u0938 \u090f\u0915 \u092c\u0921\u093c\u093e \u0920\u094b\u0938 \u0918\u0928 (cube) \u0939\u0948 \u091c\u093f\u0938\u0915\u093e \u090f\u0915 \u0915\u094b\u0928\u0947 \u0915\u093e \u092c\u094d\u0932\u0949\u0915 \u0917\u093e\u092f\u092c \u0939\u0948\u0964 \u0918\u0928 \u0915\u094b \u092a\u0942\u0930\u093e \u0915\u0930\u0928\u0947 \u0915\u0947 \u0932\u093f\u090f \u0916\u093e\u0932\u0940 \u0915\u094b\u0928\u0947 \u092e\u0947\u0902 \u0915\u094c\u0928 \u0938\u093e \u0906\u0915\u093e\u0930 \u092c\u093f\u0932\u094d\u0915\u0941\u0932 \u0938\u0939\u0940 \u092b\u093f\u091f \u0939\u094b \u0938\u0915\u0924\u093e \u0939\u0948?"},
    options: [{"label": {"English": "A small corner block matching the cutout size", "Hindi": "\u0915\u091f\u0906\u0909\u091f \u0906\u0915\u093e\u0930 \u0938\u0947 \u092e\u0947\u0932 \u0916\u093e\u0924\u093e \u0939\u0941\u0906 \u090f\u0915 \u091b\u094b\u091f\u093e \u0915\u094b\u0928\u093e \u092c\u094d\u0932\u0949\u0915"}, "value": 4}, {"label": {"English": "A flat rectangular sheet", "Hindi": "\u090f\u0915 \u0938\u092a\u093e\u091f \u0906\u092f\u0924\u093e\u0915\u093e\u0930 \u0936\u0940\u091f"}, "value": 1}, {"label": {"English": "A long cylindrical stick", "Hindi": "\u090f\u0915 \u0932\u0902\u092c\u0940 \u092c\u0947\u0932\u0928\u093e\u0915\u093e\u0930 \u091b\u0921\u093c\u0940"}, "value": 0}, {"label": {"English": "A round ball of the same height", "Hindi": "\u0909\u0938\u0940 \u090a\u0902\u091a\u093e\u0908 \u0915\u0940 \u090f\u0915 \u0917\u094b\u0932 \u0917\u0947\u0902\u0926"}, "value": 2}],
    answer: "A small corner block matching the cutout size",
    metric: "correctness",
    difficulty: "easy",
    ai_interpretation_notes: "Measures 3D spatial fitting and object completion visualization."
  },
  {
    key: "spatial_clock",
    type: "choice",
    domain: "spatial",
    component: "core_deep",
    title: {"English": "Clock Rotation", "Hindi": "\u0918\u0921\u093c\u0940 \u0915\u093e \u0918\u0942\u092e\u0928\u093e"},
    prompt: {"English": "A clock hand points straight UP (at 12). If it rotates a quarter turn (90 degrees) clockwise, where does it point?", "Hindi": "\u090f\u0915 \u0918\u0921\u093c\u0940 \u0915\u0940 \u0938\u0941\u0908 \u0938\u0940\u0927\u0947 \u090a\u092a\u0930 (12 \u092a\u0930) \u0907\u0936\u093e\u0930\u093e \u0915\u0930\u0924\u0940 \u0939\u0948\u0964 \u092f\u0926\u093f \u092f\u0939 \u0918\u0921\u093c\u0940 \u0915\u0940 \u0926\u093f\u0936\u093e \u092e\u0947\u0902 \u090f\u0915 \u091a\u094c\u0925\u093e\u0908 \u091a\u0915\u094d\u0915\u0930 (90 \u0921\u093f\u0917\u094d\u0930\u0940) \u0918\u0942\u092e\u0924\u0940 \u0939\u0948, \u0924\u094b \u092f\u0939 \u0915\u0939\u093e\u0901 \u0907\u0936\u093e\u0930\u093e \u0915\u0930\u0947\u0917\u0940?"},
    options: [{"label": {"English": "Right (at 3)", "Hindi": "\u0926\u093e\u090f\u0901 (3 \u092a\u0930)"}, "value": 4}, {"label": {"English": "Down (at 6)", "Hindi": "\u0928\u0940\u091a\u0947 (6 \u092a\u0930)"}, "value": 1}, {"label": {"English": "Left (at 9)", "Hindi": "\u092c\u093e\u090f\u0901 (9 \u092a\u0930)"}, "value": 0}, {"label": {"English": "It stays at 12", "Hindi": "\u092f\u0939 12 \u092a\u0930 \u0939\u0940 \u0930\u0939\u0924\u0940 \u0939\u0948"}, "value": 0}],
    answer: "Right (at 3)",
    metric: "correctness",
    difficulty: "easy",
    ai_interpretation_notes: "Measures 2D rotation and orientation tracking."
  },
  {
    key: "visualizer_memory_grid",
    type: "memory_grid",
    domain: "kinesthetic",
    component: "core_deep",
    title: {"English": "Step Memory", "Hindi": "\u0915\u0926\u092e \u092f\u093e\u0926 \u0930\u0916\u0928\u093e"},
    prompt: {"English": "Repeat the highlighted path of footsteps accurately. The speed, accuracy, and sequence of moves are checked.", "Hindi": "\u092a\u0926\u091a\u093f\u0939\u094d\u0928\u094b\u0902 \u0915\u0947 \u0939\u093e\u0907\u0932\u093e\u0907\u091f \u0915\u093f\u090f \u0917\u090f \u092e\u093e\u0930\u094d\u0917 \u0915\u094b \u092c\u093f\u0932\u094d\u0915\u0941\u0932 \u0938\u0939\u0940 \u0926\u094b\u0939\u0930\u093e\u090f\u0902\u0964 \u0915\u0926\u092e\u094b\u0902 \u0915\u0940 \u0917\u0924\u093f, \u0938\u091f\u0940\u0915\u0924\u093e \u0914\u0930 \u0915\u094d\u0930\u092e \u0915\u0940 \u091c\u093e\u0902\u091a \u0915\u0940 \u091c\u093e\u0924\u0940 \u0939\u0948\u0964"},
    gridSize: 3,
    path: [0, 4, 8, 7],
    metric: "spatial_navigation",
    difficulty: "medium",
    ai_interpretation_notes: "Measures sequence learning and motor-planning recall."
  },
  {
    key: "kinesthetic_catch",
    type: "choice",
    domain: "kinesthetic",
    component: "core_deep",
    title: {"English": "Catching a Ball", "Hindi": "\u0917\u0947\u0902\u0926 \u092a\u0915\u0921\u093c\u0928\u093e"},
    prompt: {"English": "A friend throws a high ball toward you, but the wind is blowing it to your left. Where should you run to catch it?", "Hindi": "\u090f\u0915 \u0926\u094b\u0938\u094d\u0924 \u0906\u092a\u0915\u0940 \u0913\u0930 \u090f\u0915 \u090a\u0902\u091a\u0940 \u0917\u0947\u0902\u0926 \u092b\u0947\u0902\u0915\u0924\u093e \u0939\u0948, \u0932\u0947\u0915\u093f\u0928 \u0939\u0935\u093e \u0909\u0938\u0947 \u0906\u092a\u0915\u0940 \u092c\u093e\u0908\u0902 \u0913\u0930 \u0927\u0915\u0947\u0932 \u0930\u0939\u0940 \u0939\u0948\u0964 \u0917\u0947\u0902\u0926 \u0915\u094b \u092a\u0915\u0921\u093c\u0928\u0947 \u0915\u0947 \u0932\u093f\u090f \u0906\u092a\u0915\u094b \u0915\u093f\u0938 \u0913\u0930 \u0926\u094c\u0921\u093c\u0928\u093e \u091a\u093e\u0939\u093f\u090f?"},
    options: [{"label": {"English": "Run to your left side and slightly back", "Hindi": "\u0905\u092a\u0928\u0940 \u092c\u093e\u0908\u0902 \u0913\u0930 \u0914\u0930 \u0925\u094b\u0921\u093c\u093e \u092a\u0940\u091b\u0947 \u0915\u0940 \u0913\u0930 \u0926\u094c\u0921\u093c\u0947\u0902"}, "value": 4}, {"label": {"English": "Stand completely still in the center", "Hindi": "\u0915\u0947\u0902\u0926\u094d\u0930 \u092e\u0947\u0902 \u092c\u093f\u0932\u094d\u0915\u0941\u0932 \u0938\u094d\u0925\u093f\u0930 \u0916\u0921\u093c\u0947 \u0930\u0939\u0947\u0902"}, "value": 1}, {"label": {"English": "Run to your right side and forward", "Hindi": "\u0905\u092a\u0928\u0940 \u0926\u093e\u0908\u0902 \u0913\u0930 \u0914\u0930 \u0906\u0917\u0947 \u0915\u0940 \u0913\u0930 \u0926\u094c\u0921\u093c\u0947\u0902"}, "value": 0}, {"label": {"English": "Run directly forward toward your friend", "Hindi": "\u0938\u0940\u0927\u0947 \u0905\u092a\u0928\u0947 \u0926\u094b\u0938\u094d\u0924 \u0915\u0940 \u0913\u0930 \u0906\u0917\u0947 \u0926\u094c\u0921\u093c\u0947\u0902"}, "value": 2}],
    answer: "Run to your left side and slightly back",
    metric: "correctness",
    difficulty: "easy",
    ai_interpretation_notes: "Biomechanical coordinate reasoning and anticipation."
  },
  {
    key: "naturalist_weather",
    type: "choice",
    domain: "naturalist",
    component: "core_deep",
    title: {"English": "Nature Weather Sign", "Hindi": "\u092a\u094d\u0930\u0915\u0943\u0924\u093f \u0915\u0947 \u092e\u094c\u0938\u092e \u0938\u0902\u0915\u0947\u0924"},
    prompt: {"English": "You notice that swallow birds are flying very low to the ground and ants are piling soil around their holes. What weather change is likely coming?", "Hindi": "\u0906\u092a \u0926\u0947\u0916\u0924\u0947 \u0939\u0948\u0902 \u0915\u093f \u0917\u094c\u0930\u0948\u092f\u093e \u092a\u0915\u094d\u0937\u0940 \u091c\u092e\u0940\u0928 \u0915\u0947 \u092c\u0939\u0941\u0924 \u0915\u0930\u0940\u092c \u0909\u0921\u093c \u0930\u0939\u0947 \u0939\u0948\u0902 \u0914\u0930 \u091a\u0940\u0902\u091f\u093f\u092f\u093e\u0902 \u0905\u092a\u0928\u0947 \u092c\u093f\u0932\u094b\u0902 \u0915\u0947 \u0906\u0938\u092a\u093e\u0938 \u092e\u093f\u091f\u094d\u091f\u0940 \u0915\u093e \u0922\u0947\u0930 \u0932\u0917\u093e \u0930\u0939\u0940 \u0939\u0948\u0902\u0964 \u092e\u094c\u0938\u092e \u092e\u0947\u0902 \u0915\u094d\u092f\u093e \u092c\u0926\u0932\u093e\u0935 \u0906\u0928\u0947 \u0915\u0940 \u0938\u0902\u092d\u093e\u0935\u0928\u093e \u0939\u0948?"},
    options: [{"label": {"English": "It is going to rain soon", "Hindi": "\u091c\u0932\u094d\u0926 \u0939\u0940 \u092c\u093e\u0930\u093f\u0936 \u0939\u094b\u0928\u0947 \u0935\u093e\u0932\u0940 \u0939\u0948"}, "value": 4}, {"label": {"English": "A hot dry wind is starting", "Hindi": "\u0917\u0930\u094d\u092e \u0938\u0942\u0916\u0940 \u0939\u0935\u093e \u091a\u0932\u0928\u0947 \u0935\u093e\u0932\u0940 \u0939\u0948"}, "value": 1}, {"label": {"English": "The weather will stay sunny and dry", "Hindi": "\u092e\u094c\u0938\u092e \u0927\u0942\u092a \u0935\u093e\u0932\u093e \u0914\u0930 \u0936\u0941\u0937\u094d\u0915 \u0930\u0939\u0947\u0917\u093e"}, "value": 0}, {"label": {"English": "It will start snowing", "Hindi": "\u092c\u0930\u094d\u092b\u092c\u093e\u0930\u0940 \u0936\u0941\u0930\u0942 \u0939\u094b \u091c\u093e\u090f\u0917\u0940"}, "value": 0}],
    answer: "It is going to rain soon",
    metric: "correctness",
    difficulty: "easy",
    ai_interpretation_notes: "Measures environmental awareness and reading nature indicators."
  },
  {
    key: "naturalist_plants",
    type: "choice",
    domain: "naturalist",
    component: "core_deep",
    title: {"English": "Spotting Leaf Spot", "Hindi": "\u092a\u0924\u094d\u0924\u0940 \u0915\u0947 \u0927\u092c\u094d\u092c\u0947 \u092a\u0939\u091a\u093e\u0928\u0928\u093e"},
    prompt: {"English": "Your tomato plant's lower leaves have dark circular spots with yellow rings. The top leaves look healthy. What should you do first to save it?", "Hindi": "\u0906\u092a\u0915\u0947 \u091f\u092e\u093e\u091f\u0930 \u0915\u0947 \u092a\u094c\u0927\u0947 \u0915\u0940 \u0928\u093f\u091a\u0932\u0940 \u092a\u0924\u094d\u0924\u093f\u092f\u094b\u0902 \u092a\u0930 \u092a\u0940\u0932\u0947 \u0918\u0947\u0930\u0947 \u0915\u0947 \u0938\u093e\u0925 \u0917\u0939\u0930\u0947 \u0930\u0902\u0917 \u0915\u0947 \u0917\u094b\u0932 \u0927\u092c\u094d\u092c\u0947 \u0939\u0948\u0902\u0964 \u090a\u092a\u0930 \u0915\u0940 \u092a\u0924\u094d\u0924\u093f\u092f\u093e\u0901 \u0938\u094d\u0935\u0938\u094d\u0925 \u0926\u093f\u0916\u0924\u0940 \u0939\u0948\u0902\u0964 \u0907\u0938\u0947 \u092c\u091a\u093e\u0928\u0947 \u0915\u0947 \u0932\u093f\u090f \u0906\u092a\u0915\u094b \u0938\u092c\u0938\u0947 \u092a\u0939\u0932\u0947 \u0915\u094d\u092f\u093e \u0915\u0930\u0928\u093e \u091a\u093e\u0939\u093f\u090f?"},
    options: [{"label": {"English": "Cut off the spotted lower leaves and water the roots, not the leaves", "Hindi": "\u0927\u092c\u094d\u092c\u0947\u0926\u093e\u0930 \u0928\u093f\u091a\u0932\u0940 \u092a\u0924\u094d\u0924\u093f\u092f\u094b\u0902 \u0915\u094b \u0915\u093e\u091f \u0926\u0947\u0902 \u0914\u0930 \u092a\u0924\u094d\u0924\u093f\u092f\u094b\u0902 \u092a\u0930 \u0928\u0939\u0940\u0902 \u092c\u0932\u094d\u0915\u093f \u091c\u0921\u093c\u094b\u0902 \u092e\u0947\u0902 \u092a\u093e\u0928\u0940 \u0926\u0947\u0902"}, "value": 4}, {"label": {"English": "Cut down the entire plant from the base", "Hindi": "\u092a\u0942\u0930\u0947 \u092a\u094c\u0927\u0947 \u0915\u094b \u0906\u0927\u093e\u0930 \u0938\u0947 \u0915\u093e\u091f \u0926\u0947\u0902"}, "value": 1}, {"label": {"English": "Pour extra water on all the green leaves", "Hindi": "\u0938\u092d\u0940 \u0939\u0930\u0940 \u092a\u0924\u094d\u0924\u093f\u092f\u094b\u0902 \u092a\u0930 \u0905\u0924\u093f\u0930\u093f\u0915\u094d\u0924 \u092a\u093e\u0928\u0940 \u0921\u093e\u0932\u0947\u0902"}, "value": 0}, {"label": {"English": "Move it into a completely dark room", "Hindi": "\u0907\u0938\u0947 \u092a\u0942\u0930\u0940 \u0924\u0930\u0939 \u0938\u0947 \u0905\u0902\u0927\u0947\u0930\u0947 \u0915\u092e\u0930\u0947 \u092e\u0947\u0902 \u0932\u0947 \u091c\u093e\u090f\u0902"}, "value": 0}],
    answer: "Cut off the spotted lower leaves and water the roots, not the leaves",
    metric: "correctness",
    difficulty: "medium",
    ai_interpretation_notes: "Practical botanical diagnostics and naturalist care reasoning."
  },
  {
    key: "social_planning",
    type: "choice",
    domain: "social",
    component: "core_deep",
    title: {"English": "Cleaning Team", "Hindi": "\u0938\u092b\u093e\u0908 \u091f\u0940\u092e"},
    prompt: {"English": "Your teacher asks your group of 4 students to clean the classroom. What is the best way to lead the work?", "Hindi": "\u0906\u092a\u0915\u0940 \u0936\u093f\u0915\u094d\u0937\u093f\u0915\u093e \u0906\u092a\u0915\u0947 4 \u091b\u093e\u0924\u094d\u0930\u094b\u0902 \u0915\u0947 \u0938\u092e\u0942\u0939 \u0915\u094b \u0915\u0915\u094d\u0937\u093e \u0938\u093e\u092b \u0915\u0930\u0928\u0947 \u0915\u0947 \u0932\u093f\u090f \u0915\u0939\u0924\u0940 \u0939\u0948\u0902\u0964 \u0915\u093e\u092e \u0915\u093e \u0928\u0947\u0924\u0943\u0924\u094d\u0935 \u0915\u0930\u0928\u0947 \u0915\u093e \u0938\u092c\u0938\u0947 \u0905\u091a\u094d\u091b\u093e \u0924\u0930\u0940\u0915\u093e \u0915\u094d\u092f\u093e \u0939\u0948?"},
    options: [{"label": {"English": "Assign different tasks to each person based on what they like doing, and clean together", "Hindi": "\u092a\u094d\u0930\u0924\u094d\u092f\u0947\u0915 \u0935\u094d\u092f\u0915\u094d\u0924\u093f \u0915\u094b \u0909\u0928\u0915\u0940 \u092a\u0938\u0902\u0926 \u0915\u0947 \u0906\u0927\u093e\u0930 \u092a\u0930 \u0905\u0932\u0917-\u0905\u0932\u0917 \u0915\u093e\u092e \u0938\u094c\u0902\u092a\u0947\u0902, \u0914\u0930 \u092e\u093f\u0932\u0915\u0930 \u0938\u092b\u093e\u0908 \u0915\u0930\u0947\u0902"}, "value": 4}, {"label": {"English": "Do all the cleaning yourself while the other 3 students watch", "Hindi": "\u092c\u093e\u0915\u0940 3 \u091b\u093e\u0924\u094d\u0930\u094b\u0902 \u0915\u0947 \u0926\u0947\u0916\u0928\u0947 \u0915\u0947 \u0926\u094c\u0930\u093e\u0928 \u0938\u093e\u0930\u093e \u0938\u092b\u093e\u0908 \u0915\u093e\u0930\u094d\u092f \u0938\u094d\u0935\u092f\u0902 \u0915\u0930\u0947\u0902"}, "value": 1}, {"label": {"English": "Tell the other 3 students to clean everything while you sit and supervise", "Hindi": "\u092c\u093e\u0915\u0940 3 \u091b\u093e\u0924\u094d\u0930\u094b\u0902 \u0915\u094b \u0938\u092c \u0915\u0941\u091b \u0938\u093e\u092b \u0915\u0930\u0928\u0947 \u0915\u0947 \u0932\u093f\u090f \u0915\u0939\u0947\u0902 \u091c\u092c\u0915\u093f \u0906\u092a \u092c\u0948\u0920\u0915\u0930 \u0928\u093f\u0917\u0930\u093e\u0928\u0940 \u0915\u0930\u0947\u0902"}, "value": 2}, {"label": {"English": "Leave the classroom and hope the teacher cleans it instead", "Hindi": "\u0915\u0915\u094d\u0937\u093e \u0938\u0947 \u092c\u093e\u0939\u0930 \u091a\u0932\u0947 \u091c\u093e\u090f\u0902 \u0914\u0930 \u0906\u0936\u093e \u0915\u0930\u0947\u0902 \u0915\u093f \u0936\u093f\u0915\u094d\u0937\u093f\u0915\u093e \u0939\u0940 \u0907\u0938\u0947 \u0938\u093e\u092b \u0915\u0930\u0947\u0902\u0917\u0940"}, "value": 0}],
    answer: "Assign different tasks to each person based on what they like doing, and clean together",
    metric: "correctness",
    difficulty: "easy",
    ai_interpretation_notes: "Situational task delegation and team coordination."
  },
  {
    key: "social_conflict_resolution",
    type: "choice",
    domain: "social",
    component: "core_deep",
    title: {"English": "Playground Dispute", "Hindi": "\u092e\u0948\u0926\u093e\u0928 \u0915\u093e \u091d\u0917\u0921\u093c\u093e"},
    prompt: {"English": "During a playground game, two friends are arguing loudly about who got out first. What is the best action to resolve this?", "Hindi": "\u0916\u0947\u0932 \u0915\u0947 \u092e\u0948\u0926\u093e\u0928 \u092e\u0947\u0902 \u090f\u0915 \u0916\u0947\u0932 \u0915\u0947 \u0926\u094c\u0930\u093e\u0928, \u0926\u094b \u0926\u094b\u0938\u094d\u0924 \u091c\u093c\u094b\u0930-\u091c\u093c\u094b\u0930 \u0938\u0947 \u092c\u0939\u0938 \u0915\u0930 \u0930\u0939\u0947 \u0939\u0948\u0902 \u0915\u093f \u092a\u0939\u0932\u0947 \u0915\u094c\u0928 \u0906\u0909\u091f \u0939\u0941\u0906\u0964 \u0907\u0938\u0947 \u0938\u0941\u0932\u091d\u093e\u0928\u0947 \u0915\u0947 \u0932\u093f\u090f \u0938\u092c\u0938\u0947 \u0905\u091a\u094d\u091b\u093e \u0915\u0926\u092e \u0915\u094d\u092f\u093e \u0939\u0948?"},
    options: [{"label": {"English": "Suggest a quick toss or game-point rule to decide, then continue playing", "Hindi": "\u0924\u092f \u0915\u0930\u0928\u0947 \u0915\u0947 \u0932\u093f\u090f \u090f\u0915 \u0924\u094d\u0935\u0930\u093f\u0924 \u091f\u0949\u0938 \u092f\u093e \u0917\u0947\u092e-\u092a\u0949\u0907\u0902\u091f \u0928\u093f\u092f\u092e \u0915\u093e \u0938\u0941\u091d\u093e\u0935 \u0926\u0947\u0902\u0917\u0947, \u092b\u093f\u0930 \u0916\u0947\u0932 \u091c\u093e\u0930\u0940 \u0930\u0916\u0947\u0902\u0917\u0947"}, "value": 4}, {"label": {"English": "Take the bat away and stop the game for everyone", "Hindi": "\u092c\u0932\u094d\u0932\u093e \u091b\u0940\u0928 \u0932\u0947\u0902\u0917\u0947 \u0914\u0930 \u0938\u092d\u0940 \u0915\u0947 \u0932\u093f\u090f \u0916\u0947\u0932 \u092c\u0902\u0926 \u0915\u0930 \u0926\u0947\u0902\u0917\u0947"}, "value": 1}, {"label": {"English": "Support the friend you like more and ignore the other", "Hindi": "\u0905\u092a\u0928\u0947 \u092a\u0938\u0902\u0926\u0940\u0926\u093e \u0926\u094b\u0938\u094d\u0924 \u0915\u093e \u0938\u092e\u0930\u094d\u0925\u0928 \u0915\u0930\u0947\u0902\u0917\u0947 \u0914\u0930 \u0926\u0942\u0938\u0930\u0947 \u0915\u0940 \u0905\u0928\u0926\u0947\u0916\u0940 \u0915\u0930\u0947\u0902\u0917\u0947"}, "value": 2}, {"label": {"English": "Shout at both of them to go back to class", "Hindi": "\u0926\u094b\u0928\u094b\u0902 \u092a\u0930 \u091a\u093f\u0932\u094d\u0932\u093e\u0915\u0930 \u0909\u0928\u094d\u0939\u0947\u0902 \u0935\u093e\u092a\u0938 \u0915\u0915\u094d\u0937\u093e \u092e\u0947\u0902 \u091c\u093e\u0928\u0947 \u0915\u0947 \u0932\u093f\u090f \u0915\u0939\u0947\u0902\u0917\u0947"}, "value": 0}],
    answer: "Suggest a quick toss or game-point rule to decide, then continue playing",
    metric: "correctness",
    difficulty: "easy",
    ai_interpretation_notes: "Measures conflict resolution and democratic playground mediation."
  },
  {
    key: "intrapersonal_goals",
    type: "choice",
    domain: "intrapersonal",
    component: "core_deep",
    title: {"English": "Learning a Skill", "Hindi": "\u0915\u094c\u0936\u0932 \u0938\u0940\u0916\u0928\u093e"},
    prompt: {"English": "You want to learn a difficult new skill, like sketching or a sport, in one month. What is the best way to practice?", "Hindi": "\u0906\u092a \u090f\u0915 \u092e\u0939\u0940\u0928\u0947 \u092e\u0947\u0902 \u0938\u094d\u0915\u0947\u091a\u093f\u0902\u0917 \u092f\u093e \u0915\u094b\u0908 \u0916\u0947\u0932 \u091c\u0948\u0938\u093e \u0915\u0920\u093f\u0928 \u0928\u092f\u093e \u0915\u094c\u0936\u0932 \u0938\u0940\u0916\u0928\u093e \u091a\u093e\u0939\u0924\u0947 \u0939\u0948\u0902\u0964 \u0905\u092d\u094d\u092f\u093e\u0938 \u0915\u0930\u0928\u0947 \u0915\u093e \u0938\u092c\u0938\u0947 \u0905\u091a\u094d\u091b\u093e \u0924\u0930\u0940\u0915\u093e \u0915\u094d\u092f\u093e \u0939\u0948?"},
    options: [{"label": {"English": "Practice for 15 minutes every single day and track your progress", "Hindi": "\u0939\u0930 \u0926\u093f\u0928 15 \u092e\u093f\u0928\u091f \u0905\u092d\u094d\u092f\u093e\u0938 \u0915\u0930\u0947\u0902 \u0914\u0930 \u0905\u092a\u0928\u0940 \u092a\u094d\u0930\u0917\u0924\u093f \u0915\u094b \u091f\u094d\u0930\u0948\u0915 \u0915\u0930\u0947\u0902"}, "value": 4}, {"label": {"English": "Practice for 5 hours on the last day of the month only", "Hindi": "\u092e\u0939\u0940\u0928\u0947 \u0915\u0947 \u0915\u0947\u0935\u0932 \u0905\u0902\u0924\u093f\u092e \u0926\u093f\u0928 5 \u0918\u0902\u091f\u0947 \u0905\u092d\u094d\u092f\u093e\u0938 \u0915\u0930\u0947\u0902"}, "value": 1}, {"label": {"English": "Only practice when you feel very happy or excited", "Hindi": "\u0915\u0947\u0935\u0932 \u0924\u092d\u0940 \u0905\u092d\u094d\u092f\u093e\u0938 \u0915\u0930\u0947\u0902 \u091c\u092c \u0906\u092a \u092c\u0939\u0941\u0924 \u0916\u0941\u0936 \u092f\u093e \u0909\u0924\u094d\u0938\u093e\u0939\u093f\u0924 \u092e\u0939\u0938\u0942\u0938 \u0915\u0930\u0947\u0902"}, "value": 2}, {"label": {"English": "Wait for someone to force you to practice", "Hindi": "\u0915\u093f\u0938\u0940 \u0915\u0947 \u0926\u094d\u0935\u093e\u0930\u093e \u0905\u092d\u094d\u092f\u093e\u0938 \u0915\u0947 \u0932\u093f\u090f \u092e\u091c\u092c\u0942\u0930 \u0915\u0930\u0928\u0947 \u0915\u093e \u0907\u0902\u0924\u091c\u093e\u0930 \u0915\u0930\u0947\u0902"}, "value": 0}],
    answer: "Practice for 15 minutes every single day and track your progress",
    metric: "correctness",
    difficulty: "easy",
    ai_interpretation_notes: "Self-regulation and systematic planning logic."
  },
  {
    key: "intrapersonal_reflection",
    type: "choice",
    domain: "intrapersonal",
    component: "core_deep",
    title: {"English": "Unsolved Puzzle", "Hindi": "\u0905\u0928\u0938\u0941\u0932\u091d\u0940 \u092a\u0939\u0947\u0932\u0940"},
    prompt: {"English": "You fail to solve a very hard puzzle after trying for a long time. What is your thought?", "Hindi": "\u0932\u0902\u092c\u0947 \u0938\u092e\u092f \u0924\u0915 \u0915\u094b\u0936\u093f\u0936 \u0915\u0930\u0928\u0947 \u0915\u0947 \u092c\u093e\u0926 \u092d\u0940 \u0906\u092a \u090f\u0915 \u092c\u0939\u0941\u0924 \u0915\u0920\u093f\u0928 \u092a\u0939\u0947\u0932\u0940 \u0915\u094b \u0939\u0932 \u0915\u0930\u0928\u0947 \u092e\u0947\u0902 \u0935\u093f\u092b\u0932 \u0930\u0939\u0924\u0947 \u0939\u0948\u0902\u0964 \u0906\u092a\u0915\u093e \u0935\u093f\u091a\u093e\u0930 \u0915\u094d\u092f\u093e \u0939\u0948?"},
    options: [{"label": {"English": "This is a good challenge, let me look at it differently and try again", "Hindi": "\u092f\u0939 \u090f\u0915 \u0905\u091a\u094d\u091b\u0940 \u091a\u0941\u0928\u094c\u0924\u0940 \u0939\u0948, \u092e\u0941\u091d\u0947 \u0907\u0938\u0947 \u0905\u0932\u0917 \u0924\u0930\u0940\u0915\u0947 \u0938\u0947 \u0926\u0947\u0916\u0928\u093e \u091a\u093e\u0939\u093f\u090f \u0914\u0930 \u092b\u093f\u0930 \u0938\u0947 \u092a\u094d\u0930\u092f\u093e\u0938 \u0915\u0930\u0928\u093e \u091a\u093e\u0939\u093f\u090f"}, "value": 4}, {"label": {"English": "I am not smart enough to solve puzzles", "Hindi": "\u092e\u0948\u0902 \u092a\u0939\u0947\u0932\u093f\u092f\u093e\u0901 \u0939\u0932 \u0915\u0930\u0928\u0947 \u0915\u0947 \u0932\u093f\u090f \u092a\u0930\u094d\u092f\u093e\u092a\u094d\u0924 \u0938\u094d\u092e\u093e\u0930\u094d\u091f \u0928\u0939\u0940\u0902 \u0939\u0942\u0901"}, "value": 1}, {"label": {"English": "This puzzle has a wrong question and is broken", "Hindi": "\u092f\u0939 \u092a\u0939\u0947\u0932\u0940 \u0917\u0932\u0924 \u092a\u094d\u0930\u0936\u094d\u0928 \u0939\u0948 \u0914\u0930 \u0916\u0930\u093e\u092c \u0939\u0948"}, "value": 2}, {"label": {"English": "I will never try a puzzle again", "Hindi": "\u092e\u0948\u0902 \u092b\u093f\u0930 \u0915\u092d\u0940 \u092a\u0939\u0947\u0932\u0940 \u0915\u093e \u092a\u094d\u0930\u092f\u093e\u0938 \u0928\u0939\u0940\u0902 \u0915\u0930\u0942\u0901\u0917\u093e"}, "value": 0}],
    answer: "This is a good challenge, let me look at it differently and try again",
    metric: "correctness",
    difficulty: "easy",
    ai_interpretation_notes: "Growth mindset and cognitive resilience indicator."
  },
  {
    key: "reflection_pride",
    type: "open_ended",
    domain: "intrapersonal",
    component: "reflection",
    title: {"English": "Proudest Achievement", "Hindi": "\u0917\u0930\u094d\u0935 \u0915\u0940 \u0909\u092a\u0932\u092c\u094d\u0927\u093f"},
    prompt: {"English": "What achievement or moment in your life are you most proud of?", "Hindi": "\u0906\u092a\u0915\u0947 \u091c\u0940\u0935\u0928 \u0915\u0940 \u0915\u094c\u0928 \u0938\u0940 \u0909\u092a\u0932\u092c\u094d\u0927\u093f \u092f\u093e \u0915\u094d\u0937\u0923 \u0910\u0938\u093e \u0939\u0948 \u091c\u093f\u0938 \u092a\u0930 \u0906\u092a\u0915\u094b \u0938\u092c\u0938\u0947 \u0905\u0927\u093f\u0915 \u0917\u0930\u094d\u0935 \u0939\u0948?"},
    metric: "narrative_expression",
    difficulty: "easy",
    ai_interpretation_notes: "Exposes core values, pride drivers, and self-awareness."
  },
  {
    key: "reflection_flow",
    type: "open_ended",
    domain: "intrapersonal",
    component: "reflection",
    title: {"English": "Forget Time", "Hindi": "\u0938\u092e\u092f \u092d\u0942\u0932 \u091c\u093e\u0928\u093e"},
    prompt: {"English": "What activity or hobby makes you completely forget about time?", "Hindi": "\u0915\u094c\u0928 \u0938\u0940 \u0917\u0924\u093f\u0935\u093f\u0927\u093f \u092f\u093e \u0936\u094c\u0915 \u0910\u0938\u093e \u0939\u0948 \u091c\u094b \u0906\u092a\u0915\u094b \u0938\u092e\u092f \u0915\u093e \u0905\u0939\u0938\u093e\u0938 \u092a\u0942\u0930\u0940 \u0924\u0930\u0939 \u0938\u0947 \u092d\u0941\u0932\u093e \u0926\u0947\u0924\u093e \u0939\u0948?"},
    metric: "narrative_expression",
    difficulty: "easy",
    ai_interpretation_notes: "Measures spontaneous flow state and deep intrinsic interest patterns."
  },
  {
    key: "reflection_learning",
    type: "open_ended",
    domain: "intrapersonal",
    component: "reflection",
    title: {"English": "Want to Learn", "Hindi": "\u0938\u0940\u0916\u0928\u0947 \u0915\u0940 \u0907\u091a\u094d\u091b\u093e"},
    prompt: {"English": "What is one new thing you would love to learn how to do this year?", "Hindi": "\u0910\u0938\u0940 \u0915\u094c\u0928 \u0938\u0940 \u090f\u0915 \u0928\u0908 \u091a\u0940\u091c\u093c \u0939\u0948 \u091c\u093f\u0938\u0947 \u0906\u092a \u0907\u0938 \u0938\u093e\u0932 \u0938\u0940\u0916\u0928\u093e \u092a\u0938\u0902\u0926 \u0915\u0930\u0947\u0902\u0917\u0947?"},
    metric: "narrative_expression",
    difficulty: "easy",
    ai_interpretation_notes: "Measures child's curiosities and proactive growth mindset targets."
  },
  {
    key: "reflection_community",
    type: "open_ended",
    domain: "social",
    component: "reflection",
    title: {"English": "School Improvement", "Hindi": "\u0938\u094d\u0915\u0942\u0932 \u0938\u0941\u0927\u093e\u0930"},
    prompt: {"English": "If you could improve one thing in your school or community, what would it be?", "Hindi": "\u092f\u0926\u093f \u0906\u092a \u0905\u092a\u0928\u0947 \u0938\u094d\u0915\u0942\u0932 \u092f\u093e \u0938\u092e\u0941\u0926\u093e\u092f \u092e\u0947\u0902 \u0915\u094b\u0908 \u090f\u0915 \u091a\u0940\u091c\u093c \u0938\u0941\u0927\u093e\u0930 \u0938\u0915\u0947\u0902, \u0924\u094b \u0935\u0939 \u0915\u094d\u092f\u093e \u0939\u094b\u0917\u0940?"},
    metric: "narrative_expression",
    difficulty: "easy",
    ai_interpretation_notes: "Exposes empathy, civic values, and social/leadership problem-solving leanings."
  },
];

export function getAdaptedDiscoveryQuestions(schoolYear, age, language) {
  const isHindi = language === 'Hindi';
  return [
    {
      id: "q_discovery_1",
      question: isHindi ? "\u0924\u0941\u092e\u094d\u0939\u0947\u0902 \u090f\u0915 \u0916\u093e\u0932\u0940 \u0926\u094b\u092a\u0939\u0930 \u092e\u093f\u0932\u0924\u0940 \u0939\u0948\u0964 \u0924\u0941\u092e \u0938\u092c\u0938\u0947 \u091c\u093c\u094d\u092f\u093e\u0926\u093e \u0915\u094d\u092f\u093e \u0915\u0930\u0928\u093e \u091a\u093e\u0939\u094b\u0917\u0947?" : "You get one free afternoon. What sounds most fun?",
      type: 'choice',
      options: [
        { label: isHindi ? "\u0915\u0939\u093e\u0928\u0940 \u0938\u0941\u0928\u093e\u0928\u093e \u092f\u093e \u0932\u093f\u0916\u0928\u093e" : "Tell or write a story", emoji: "\ud83d\udde3\ufe0f", domains: ["language", "creative"] },
        { label: isHindi ? "\u090f\u0915 \u0915\u0920\u093f\u0928 \u092a\u0939\u0947\u0932\u0940 \u0939\u0932 \u0915\u0930\u0928\u093e" : "Solve a tricky puzzle", emoji: "\ud83e\udde9", domains: ["logical", "spatial"] },
        { label: isHindi ? "\u090f\u0915 \u0938\u093e\u092e\u0942\u0939\u093f\u0915 \u0916\u0947\u0932 \u0915\u093e \u0906\u092f\u094b\u091c\u0928 \u0915\u0930\u0928\u093e" : "Organize a group game", emoji: "\ud83e\udd1d", domains: ["social", "language"] },
        { label: isHindi ? "\u090f\u0915 \u0935\u094d\u092f\u0915\u094d\u0924\u093f\u0917\u0924 \u0932\u0915\u094d\u0937\u094d\u092f \u0915\u0940 \u092f\u094b\u091c\u0928\u093e \u092c\u0928\u093e\u0928\u093e" : "Plan a personal goal", emoji: "\ud83e\udd14", domains: ["intrapersonal"] },
      ]
    },
    {
      id: "q_discovery_2",
      question: isHindi ? "\u0906\u092a\u0915\u094b \u0917\u0924\u094d\u0924\u0947 \u0915\u093e \u090f\u0915 \u0921\u093f\u092c\u094d\u092c\u093e \u0914\u0930 \u0932\u0915\u0921\u093c\u093f\u092f\u093e\u0901 \u092e\u093f\u0932\u0924\u0940 \u0939\u0948\u0902\u0964 \u0906\u092a \u0915\u094d\u092f\u093e \u0915\u0930\u0947\u0902\u0917\u0947?" : "You receive a box of cardboard and sticks. What do you do?",
      type: 'choice',
      options: [
        { label: isHindi ? "\u090f\u0915 \u0915\u0932\u093e\u0924\u094d\u092e\u0915 \u0916\u093f\u0932\u094c\u0928\u093e \u0915\u093f\u0932\u093e \u092c\u0928\u093e\u0928\u093e" : "Design an artistic toy castle", emoji: "\ud83c\udfa8", domains: ["creative", "spatial"] },
        { label: isHindi ? "\u090f\u0915 \u092e\u0949\u0921\u0932 \u092a\u0941\u0932 \u0915\u093e \u0928\u093f\u0930\u094d\u092e\u093e\u0923 \u0915\u0930\u0928\u093e" : "Build a model bridge", emoji: "\ud83d\udd28", domains: ["spatial", "logical"] },
        { label: isHindi ? "\u0926\u094b\u0938\u094d\u0924\u094b\u0902 \u0915\u094b \u092e\u093f\u0932\u0915\u0930 \u092c\u0928\u093e\u0928\u0947 \u0915\u0947 \u0932\u093f\u090f \u092c\u0941\u0932\u093e\u0928\u093e" : "Invite friends to build together", emoji: "\ud83e\udd1d", domains: ["social", "language"] },
        { label: isHindi ? "\u0938\u093e\u092e\u0917\u094d\u0930\u0940 \u0915\u093e \u0936\u093e\u0902\u0924\u093f \u0938\u0947 \u0928\u093f\u0930\u0940\u0915\u094d\u0937\u0923 \u0915\u0930\u0928\u093e" : "Inspect the materials quietly", emoji: "\ud83e\udd14", domains: ["intrapersonal"] },
      ]
    },
    {
      id: "q_discovery_3",
      question: isHindi ? "\u0906\u092a \u0915\u093f\u0938\u0940 \u0907\u092e\u093e\u0930\u0924 \u092a\u0930 \u0930\u094b\u0936\u0928\u0940 \u0915\u093e \u090f\u0915 \u0905\u091c\u0940\u092c \u092a\u0948\u091f\u0930\u094d\u0928 \u0926\u0947\u0916\u0924\u0947 \u0939\u0948\u0902\u0964 \u0906\u092a \u0915\u094d\u092f\u093e \u0915\u0930\u0947\u0902\u0917\u0947?" : "You see a strange pattern of lights on a building. What do you do?",
      type: 'choice',
      options: [
        { label: isHindi ? "\u0915\u094b\u0921 \u0915\u093e \u092a\u0924\u093e \u0932\u0917\u093e\u0928\u0947 \u0915\u0940 \u0915\u094b\u0936\u093f\u0936 \u0915\u0930\u0928\u093e" : "Try to figure out the code", emoji: "\ud83e\udde9", domains: ["logical", "spatial"] },
        { label: isHindi ? "\u0928\u094b\u091f\u092c\u0941\u0915 \u092e\u0947\u0902 \u092a\u0948\u091f\u0930\u094d\u0928 \u092c\u0928\u093e\u0928\u093e" : "Draw the pattern in a notebook", emoji: "\ud83c\udfa8", domains: ["creative", "spatial"] },
        { label: isHindi ? "\u090f\u0915 \u0926\u094b\u0938\u094d\u0924 \u0915\u094b \u0907\u0938\u0947 \u0938\u092e\u091d\u093e\u0928\u093e" : "Explain it to a friend", emoji: "\ud83d\udde3\ufe0f", domains: ["language", "social"] },
        { label: isHindi ? " \u092c\u0948\u0920\u0915\u0930 \u091a\u0941\u092a\u091a\u093e\u092a \u0907\u0938\u0947 \u0926\u0947\u0916\u0928\u093e" : "Sit and watch it quietly", emoji: "\ud83e\udd14", domains: ["intrapersonal"] },
      ]
    },
    {
      id: "q_discovery_4",
      question: isHindi ? "\u092f\u0926\u093f \u0906\u092a \u0916\u0947\u0932 \u0915\u0947 \u092e\u0948\u0926\u093e\u0928 \u0915\u0947 \u0932\u093f\u090f \u090f\u0915 \u0928\u092f\u093e \u0916\u0947\u0932 \u092c\u0928\u093e \u0938\u0915\u0947\u0902, \u0924\u094b \u0935\u0939 \u0915\u0948\u0938\u093e \u0926\u093f\u0916\u0947\u0917\u093e?" : "If you could design a new playground game, what would it look like?",
      type: 'choice',
      options: [
        { label: isHindi ? "\u091b\u093f\u092a\u0947 \u0939\u0941\u090f \u0930\u093e\u0938\u094d\u0924\u094b\u0902 \u0935\u093e\u0932\u0940 \u092d\u0942\u0932\u092d\u0941\u0932\u0948\u092f\u093e" : "A maze with hidden routes", emoji: "\ud83d\udd28", domains: ["spatial", "logical"] },
        { label: isHindi ? "\u090f\u0915 \u0936\u093e\u0930\u0940\u0930\u093f\u0915 \u092c\u093e\u0927\u093e \u0926\u094c\u0921\u093c \u0915\u093e \u0930\u093e\u0938\u094d\u0924\u093e" : "A physical obstacle course", emoji: "\ud83c\udfc3", domains: ["kinesthetic", "spatial"] },
        { label: isHindi ? "\u0905\u0932\u0917-\u0905\u0932\u0917 \u092d\u0942\u092e\u093f\u0915\u093e\u0913\u0902 \u0935\u093e\u0932\u093e \u091f\u0940\u092e \u0916\u0947\u0932" : "A team game with roles", emoji: "\ud83e\udd1d", domains: ["social", "language"] },
        { label: isHindi ? "\u090f\u0915 \u0935\u094d\u092f\u0915\u094d\u0924\u093f \u0915\u0947 \u0932\u093f\u090f \u090f\u0915 \u092a\u0939\u0947\u0932\u0940 \u0916\u0947\u0932" : "A puzzle game for one person", emoji: "\ud83e\udd14", domains: ["intrapersonal"] },
      ]
    },
    {
      id: "q_discovery_5",
      question: isHindi ? "\u0906\u092a \u090f\u0915 \u0924\u0947\u091c\u093c \u0922\u094b\u0932 \u0915\u0940 \u0906\u0935\u093e\u091c\u093c \u0938\u0941\u0928\u0924\u0947 \u0939\u0948\u0902\u0964 \u0906\u092a\u0915\u0940 \u0915\u094d\u092f\u093e \u092a\u094d\u0930\u0924\u093f\u0915\u094d\u0930\u093f\u092f\u093e \u0939\u094b\u0917\u0940?" : "You hear a fast drumbeat. What is your reaction?",
      type: 'choice',
      options: [
        { label: isHindi ? "\u0924\u093e\u0932 \u092a\u0930 \u0928\u093e\u091a\u0928\u093e \u092f\u093e \u0924\u093e\u0932\u0940 \u092c\u091c\u093e\u0928\u093e" : "Dance or clap to the rhythm", emoji: "\ud83c\udfc3", domains: ["kinesthetic", "creative"] },
        { label: isHindi ? "\u0927\u0921\u093c\u0915\u0928\u094b\u0902 \u0915\u0947 \u092a\u0948\u091f\u0930\u094d\u0928 \u0915\u094b \u0927\u094d\u092f\u093e\u0928 \u0938\u0947 \u0938\u0941\u0928\u0928\u093e" : "Listen to the pattern of beats", emoji: "\ud83e\udde9", domains: ["logical", "naturalist"] },
        { label: isHindi ? "\u0926\u094b\u0938\u094d\u0924\u094b\u0902 \u0915\u094b \u0936\u093e\u092e\u093f\u0932 \u0939\u094b\u0928\u0947 \u0915\u0947 \u0932\u093f\u090f \u092c\u0941\u0932\u093e\u0928\u093e" : "Call friends to join in", emoji: "\ud83e\udd1d", domains: ["social", "language"] },
        { label: isHindi ? "\u0906\u0901\u0916\u0947\u0902 \u092c\u0902\u0926 \u0915\u0930\u0915\u0947 \u0938\u0902\u0917\u0940\u0924 \u0915\u094b \u092e\u0939\u0938\u0942\u0938 \u0915\u0930\u0928\u093e" : "Close eyes and feel the music", emoji: "\ud83e\udd14", domains: ["intrapersonal"] },
      ]
    },
    {
      id: "q_discovery_6",
      question: isHindi ? "\u0906\u092a\u0915\u094b \u092c\u0917\u0940\u091a\u0947 \u092e\u0947\u0902 \u090f\u0915 \u092c\u0940\u092e\u093e\u0930 \u092a\u094c\u0927\u093e \u092e\u093f\u0932\u0924\u093e \u0939\u0948\u0964 \u0906\u092a \u0915\u094d\u092f\u093e \u0915\u0930\u0947\u0902\u0917\u0947?" : "You find a sick plant in the garden. What do you do?",
      type: 'choice',
      options: [
        { label: isHindi ? "\u092a\u0924\u094d\u0924\u093f\u092f\u094b\u0902 \u0915\u0940 \u091c\u093e\u0901\u091a \u0915\u0930\u0928\u093e \u0914\u0930 \u092e\u093f\u091f\u094d\u091f\u0940 \u0921\u093e\u0932\u0928\u093e" : "Inspect leaves and add soil", emoji: "\ud83c\udf31", domains: ["naturalist", "logical"] },
        { label: isHindi ? "\u090f\u0915 \u0921\u093e\u092f\u0930\u0940 \u092e\u0947\u0902 \u092a\u0924\u094d\u0924\u093f\u092f\u094b\u0902 \u0915\u093e \u091a\u093f\u0924\u094d\u0930 \u092c\u0928\u093e\u0928\u093e" : "Draw the leaves in a diary", emoji: "\ud83c\udfa8", domains: ["creative", "naturalist"] },
        { label: isHindi ? "\u0936\u093f\u0915\u094d\u0937\u0915 \u0938\u0947 \u0907\u0938\u0947 \u0938\u0941\u0932\u091d\u093e\u0928\u0947 \u092e\u0947\u0902 \u092e\u0926\u0926 \u092e\u093e\u0901\u0917\u0928\u093e" : "Ask a teacher to help solve it", emoji: "\ud83d\udde3\ufe0f", domains: ["language", "social"] },
        { label: isHindi ? "\u091a\u0941\u092a\u091a\u093e\u092a \u0938\u094b\u091a\u0928\u093e \u0915\u093f \u092f\u0939 \u0915\u0948\u0938\u0947 \u092c\u0922\u093c\u0924\u093e \u0939\u0948" : "Quietly wonder how it grows", emoji: "\ud83e\udd14", domains: ["intrapersonal"] },
      ]
    },
    {
      id: "q_discovery_7",
      question: isHindi ? "\u092e\u0927\u094d\u092f\u093e\u0939\u094d\u0928 \u092d\u094b\u091c\u0928 (\u0932\u0902\u091a \u092c\u094d\u0930\u0947\u0915) \u092e\u0947\u0902 \u090f\u0915 \u0938\u0939\u092a\u093e\u0920\u0940 \u0905\u0915\u0947\u0932\u093e \u092e\u0939\u0938\u0942\u0938 \u0915\u0930 \u0930\u0939\u093e \u0939\u0948\u0964 \u0906\u092a \u0915\u094d\u092f\u093e \u0915\u0930\u0947\u0902\u0917\u0947?" : "A classmate is feeling lonely at lunch break. What do you do?",
      type: 'choice',
      options: [
        { label: isHindi ? "\u091c\u093e\u0915\u0930 \u092c\u0948\u0920\u0928\u093e, \u092c\u093e\u0924 \u0915\u0930\u0928\u093e \u0914\u0930 \u091a\u0941\u091f\u0915\u0941\u0932\u0947 \u0938\u0941\u0928\u093e\u0928\u093e" : "Go sit, talk, and tell jokes", emoji: "\ud83d\udde3\ufe0f", domains: ["language", "social"] },
        { label: isHindi ? "\u0909\u0928\u094d\u0939\u0947\u0902 \u090f\u0915 \u0916\u0947\u0932 \u0916\u0947\u0932\u0928\u0947 \u0915\u0947 \u0932\u093f\u090f \u0906\u092e\u0902\u0924\u094d\u0930\u093f\u0924 \u0915\u0930\u0928\u093e" : "Invite them to a sports game", emoji: "\ud83c\udfc3", domains: ["kinesthetic", "social"] },
        { label: isHindi ? "\u0938\u094b\u091a\u0928\u093e \u0915\u093f \u0935\u0947 \u0915\u0948\u0938\u093e \u092e\u0939\u0938\u0942\u0938 \u0915\u0930 \u0930\u0939\u0947 \u0939\u0948\u0902" : "Think about how they feel", emoji: "\ud83e\udd14", domains: ["intrapersonal"] },
        { label: isHindi ? "\u0926\u094b \u0932\u094b\u0917\u094b\u0902 \u0915\u0947 \u0916\u0947\u0932\u0928\u0947 \u0915\u093e \u090f\u0915 \u0916\u0947\u0932 \u092c\u0928\u093e\u0928\u093e" : "Invent a two-person game", emoji: "\ud83c\udfa8", domains: ["creative", "social"] },
      ]
    },
    {
      id: "q_discovery_8",
      question: isHindi ? "\u091c\u092c \u0906\u092a \u0915\u093f\u0938\u0940 \u091a\u093f\u0924\u094d\u0930 \u092f\u093e \u092a\u094d\u0930\u094b\u091c\u0947\u0915\u094d\u091f \u092e\u0947\u0902 \u0915\u094b\u0908 \u0917\u0932\u0924\u0940 \u0915\u0930\u0924\u0947 \u0939\u0948\u0902, \u0924\u094b \u0906\u092a \u0915\u094d\u092f\u093e \u0915\u0930\u0924\u0947 \u0939\u0948\u0902?" : "When you make a mistake in a drawing or project, what do you do?",
      type: 'choice',
      options: [
        { label: isHindi ? "\u0936\u093e\u0902\u0924 \u0939\u094b\u0928\u093e \u0914\u0930 \u0907\u0938\u0947 \u0920\u0940\u0915 \u0915\u0930\u0928\u0947 \u0915\u0940 \u092f\u094b\u091c\u0928\u093e \u092c\u0928\u093e\u0928\u093e" : "Calm down and plan how to fix it", emoji: "\ud83e\udd14", domains: ["intrapersonal", "logical"] },
        { label: isHindi ? "\u090f\u0915 \u0928\u090f \u0935\u093f\u091a\u093e\u0930 \u0915\u0947 \u0938\u093e\u0925 \u092b\u093f\u0930 \u0938\u0947 \u0936\u0941\u0930\u0941\u0906\u0924 \u0915\u0930\u0928\u093e" : "Start over with a completely new idea", emoji: "\ud83c\udfa8", domains: ["creative"] },
        { label: isHindi ? "\u0915\u093f\u0938\u0940 \u0926\u094b\u0938\u094d\u0924 \u0938\u0947 \u0938\u0932\u093e\u0939 \u092e\u093e\u0901\u0917\u0928\u093e" : "Ask a friend for advice", emoji: "\ud83e\udd1d", domains: ["social", "language"] },
        { label: isHindi ? "\u0907\u0938\u0947 \u092b\u0947\u0902\u0915 \u0926\u0947\u0928\u093e \u0914\u0930 \u092c\u093e\u0939\u0930 \u091f\u0939\u0932\u0928\u0947 \u091a\u0932\u0947 \u091c\u093e\u0928\u093e" : "Throw it away and walk outside", emoji: "\ud83c\udfc3", domains: ["kinesthetic"] },
      ]
    },
  ];
}

export function getAdaptedDeepTasks(tasks, schoolYear, age, language) {
  const isHindi = language === 'Hindi';
  return tasks.map(t => {
    // Extract Hindi or English translations based on language
    const title = typeof t.title === 'object' && t.title ? (isHindi ? t.title.Hindi || t.title.English : t.title.English) : t.title;
    const prompt = typeof t.prompt === 'object' && t.prompt ? (isHindi ? t.prompt.Hindi || t.prompt.English : t.prompt.English) : t.prompt;
    
    let steps = t.steps;
    if (steps && typeof steps === 'object') {
      steps = isHindi ? steps.Hindi || steps.English : steps.English;
    }
    
    let shuffled = t.shuffled;
    if (shuffled && typeof shuffled === 'object') {
      shuffled = isHindi ? shuffled.Hindi || shuffled.English : shuffled.English;
    }
    
    let options = t.options;
    if (options && Array.isArray(options)) {
      options = options.map(o => {
        let label = o.label;
        if (label && typeof label === 'object') {
          label = isHindi ? label.Hindi || label.English : label.English;
        }
        return { ...o, label };
      });
    }
    
    let answer = t.answer;
    if (answer && typeof answer === 'object') {
      answer = isHindi ? answer.Hindi || answer.English : answer.English;
    }
    
    return { ...t, title, prompt, steps, shuffled, options, answer };
  });
}

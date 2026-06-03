// GOAT Assessment Questions
// Each question maps to a domain_component key scored 0-4.
// Supports complete English and Hindi translations for child-friendly, visual/pattern assessment.

export const DOMAINS = {
  kinesthetic:   { label: "Kinesthetic & Physical",     emoji: "🏃", color: "#0F6E56", light: "#E1F5EE" },
  creative:      { label: "Creative & Artistic",        emoji: "🎨", color: "#993556", light: "#FBEAF0" },
  logical:       { label: "Logical & Analytical",       emoji: "🧠", color: "#185FA5", light: "#E6F1FB" },
  spatial:       { label: "Spatial & Making",           emoji: "🔧", color: "#854F0B", light: "#FAEEDA" },
  social:        { label: "Social & Leadership",        emoji: "🤝", color: "#534AB7", light: "#EEEDFE" },
  language:      { label: "Language & Communication",   emoji: "💬", color: "#993C1D", light: "#FAECE7" },
  naturalist:    { label: "Naturalist & Environmental", emoji: "🌱", color: "#3B6D11", light: "#EAF3DE" },
  intrapersonal: { label: "Intrapersonal & Reflective", emoji: "🪞", color: "#5F5E5A", light: "#F1EFE8" },
};

export const DISCOVERY_QUESTIONS = [
  {
    id: "q_discovery_1",
    question: "Your teacher gives your group a difficult challenge. What do you naturally do first?",
    type: "choice",
    options: [
      { label: "Break the problem into smaller parts and look for patterns", emoji: "🧩", domains: ["logical"] },
      { label: "Think of a unique or unusual solution", emoji: "🎨", domains: ["creative"] },
      { label: "Explain ideas and help everyone understand", emoji: "🗣️", domains: ["language"] },
      { label: "Organize the group and assign tasks", emoji: "🤝", domains: ["social"] }
    ]
  },
  {
    id: "q_discovery_2",
    question: "You receive a box filled with cardboard, sticks, paper clips and rubber bands. What do you do first?",
    type: "choice",
    options: [
      { label: "Build something useful", emoji: "🔨", domains: ["spatial"] },
      { label: "Create something beautiful", emoji: "🎨", domains: ["creative"] },
      { label: "Sort everything and understand how it works", emoji: "🧩", domains: ["logical"] },
      { label: "Shake the box and feel the weight of the objects", emoji: "💃", domains: ["kinesthetic"] }
    ]
  },
  {
    id: "q_discovery_3",
    question: "You discover an unusual insect. What is your first reaction?",
    type: "choice",
    options: [
      { label: "Observe it carefully", emoji: "🦋", domains: ["naturalist"] },
      { label: "Draw it", emoji: "🎨", domains: ["creative"] },
      { label: "Reflect quietly on what its life is like in nature", emoji: "🤔", domains: ["intrapersonal"] },
      { label: "Tell others about it", emoji: "🗣️", domains: ["language"] }
    ]
  },
  {
    id: "q_discovery_4",
    question: "A friend feels left out. What do you naturally do?",
    type: "choice",
    options: [
      { label: "Invite them to join", emoji: "🤝", domains: ["social"] },
      { label: "Talk to them and listen", emoji: "🗣️", domains: ["language"] },
      { label: "Think quietly about how they feel", emoji: "🤔", domains: ["intrapersonal"] },
      { label: "Start a fun, active physical game together", emoji: "🏃", domains: ["kinesthetic"] }
    ]
  },
  {
    id: "q_discovery_5",
    question: "You get a brand-new puzzle. What happens first?",
    type: "choice",
    options: [
      { label: "Look for patterns", emoji: "🧩", domains: ["logical"] },
      { label: "Take it apart and understand the structure", emoji: "🔨", domains: ["spatial"] },
      { label: "Touch and move the pieces physically to see how they feel", emoji: "🏃", domains: ["kinesthetic"] },
      { label: "Turn it into a game with friends", emoji: "🤝", domains: ["social"] }
    ]
  },
  {
    id: "q_discovery_6",
    question: "Your school is holding a fair. Which role feels most natural?",
    type: "choice",
    options: [
      { label: "Designing decorations", emoji: "🎨", domains: ["creative"] },
      { label: "Managing teams", emoji: "🤝", domains: ["social"] },
      { label: "Presenting ideas", emoji: "🗣️", domains: ["language"] },
      { label: "Building displays and models", emoji: "🔨", domains: ["spatial"] }
    ]
  },
  {
    id: "q_discovery_7",
    question: "You have one free afternoon. What would you naturally choose?",
    type: "choice",
    options: [
      { label: "Explore outdoors in nature", emoji: "🦋", domains: ["naturalist"] },
      { label: "Build or create something", emoji: "🔨", domains: ["spatial"] },
      { label: "Solve puzzles", emoji: "🧩", domains: ["logical"] },
      { label: "Play active games", emoji: "🏃", domains: ["kinesthetic"] }
    ]
  },
  {
    id: "q_discovery_8",
    question: "You see something amazing happen. What do you do first?",
    type: "choice",
    options: [
      { label: "Explain it to others", emoji: "🗣️", domains: ["language"] },
      { label: "Compare it to plants and animals in nature", emoji: "🌱", domains: ["naturalist"] },
      { label: "Draw or create something inspired by it", emoji: "🎨", domains: ["creative"] },
      { label: "Reflect on it privately", emoji: "🤔", domains: ["intrapersonal"] }
    ]
  },
  {
    id: "q_discovery_9",
    question: "A game is not working properly. What do you naturally do?",
    type: "choice",
    options: [
      { label: "Check how the pieces connect to the natural environment", emoji: "🌱", domains: ["naturalist"] },
      { label: "Rebuild parts of it", emoji: "🔨", domains: ["spatial"] },
      { label: "Suggest a creative alternative", emoji: "🎨", domains: ["creative"] },
      { label: "Move and shake the game pieces physically to test them", emoji: "🏃", domains: ["kinesthetic"] }
    ]
  },
  {
    id: "q_discovery_10",
    question: "You are learning something new. What helps you most?",
    type: "choice",
    options: [
      { label: "Trying it physically", emoji: "🏃", domains: ["kinesthetic"] },
      { label: "Seeing how it works", emoji: "🔨", domains: ["spatial"] },
      { label: "Discussing it with others", emoji: "🗣️", domains: ["language"] },
      { label: "Thinking deeply about it alone", emoji: "🤔", domains: ["intrapersonal"] }
    ]
  },
  {
    id: "q_discovery_11",
    question: "Your team gets stuck. What do you naturally contribute?",
    type: "choice",
    options: [
      { label: "An observation of the natural surroundings", emoji: "🌱", domains: ["naturalist"] },
      { label: "A plan or a pattern solution", emoji: "🧩", domains: ["logical"] },
      { label: "Motivation and encouragement", emoji: "🤝", domains: ["social"] },
      { label: "A quiet moment of reflection", emoji: "🤔", domains: ["intrapersonal"] }
    ]
  },
  {
    id: "q_discovery_12",
    question: "A mystery appears in your neighborhood. What do you do first?",
    type: "choice",
    options: [
      { label: "Investigate clues", emoji: "🔍", domains: ["logical"] },
      { label: "Observe carefully", emoji: "🦋", domains: ["naturalist"] },
      { label: "Gather people and discuss", emoji: "🤝", domains: ["social"] },
      { label: "Think quietly on what it means", emoji: "🤔", domains: ["intrapersonal"] }
    ]
  }
];

export const DEEP_QUESTIONS = {
  kinesthetic: [
    { key: "kinesthetic_rhythm_accuracy", q: "When you hear music, how easily can you clap or tap along to the beat?", type: "scale", low: "Very hard", high: "Perfectly natural" },
    { key: "kinesthetic_movement_memory", q: "If someone shows you a dance move once, how quickly can you copy it?", type: "scale", low: "Need many tries", high: "Get it immediately" },
    { key: "kinesthetic_fine_motor", q: "How are you at tasks needing careful hand control - like threading a needle or drawing a straight line?", type: "scale", low: "Struggle a lot", high: "Very precise" },
    { key: "kinesthetic_body_coordination", q: "In sports or games, how well can you control your body to do what you want?", type: "scale", low: "Clumsy often", high: "Very coordinated" },
    { key: "kinesthetic_physical_endurance", q: "How long can you keep going during physical activity without wanting to stop?", type: "scale", low: "Get tired quickly", high: "Could go for hours" },
  ],
  creative: [
    { key: "creative_divergent_thinking", q: "If I give you a paper clip, how many different uses can you think of?", type: "scale", low: "1-2 ideas", high: "10+ ideas" },
    { key: "creative_visual_imagination", q: "When you close your eyes and imagine a scene, how vivid and detailed is it?", type: "scale", low: "Blurry / vague", high: "Crystal clear" },
    { key: "creative_originality", q: "Do your ideas usually feel different from what others think of?", type: "scale", low: "Similar to others", high: "Always unique" },
    { key: "creative_colour_sense", q: "When you look at colours together, do you notice if they look good or bad?", type: "scale", low: "Not really", high: "Immediately notice" },
    { key: "creative_pattern_creation", q: "If you have to decorate something, how naturally do patterns come to you?", type: "scale", low: "Hard to start", high: "Flows naturally" },
  ],
  logical: [
    { key: "logical_pattern_recognition", q: "2, 4, 8, 16 - what comes next? How easily do you spot number patterns?", type: "scale", low: "Take a long time", high: "See it instantly" },
    { key: "logical_number_reasoning", q: "How comfortable are you solving maths problems in your head?", type: "scale", low: "Uncomfortable", high: "Love it" },
    { key: "logical_sequence_logic", q: "If A happens, then B happens, so C must happen - this kind of thinking feels:", type: "scale", low: "Very confusing", high: "Very natural" },
    { key: "logical_spatial_logic", q: "If you fold a paper and cut a hole, can you picture what it looks like unfolded?", type: "scale", low: "No idea", high: "See it clearly" },
  ],
  spatial: [
    { key: "spatial_mental_rotation", q: "Can you picture objects rotating in your head - like a cube turning around?", type: "scale", low: "Very hard", high: "Easy and clear" },
    { key: "spatial_construction_sense", q: "When building something (LEGO, blocks, sticks), how naturally does it come?", type: "scale", low: "Frustrating", high: "Totally natural" },
    { key: "spatial_mechanical_intuition", q: "When you see a machine or tool, do you naturally understand how it works?", type: "scale", low: "No clue", high: "Usually figure it out" },
    { key: "spatial_design_thinking", q: "If you had to make something look better, do ideas come easily?", type: "scale", low: "Hard to start", high: "Many ideas fast" },
  ],
  social: [
    { key: "social_empathy_recognition", q: "Can you tell how someone is feeling just by looking at their face?", type: "scale", low: "Rarely", high: "Almost always" },
    { key: "social_peer_influence", q: "When you share your idea, do others usually listen and follow?", type: "scale", low: "Rarely", high: "Usually yes" },
    { key: "social_conflict_resolution", q: "When two friends argue, how naturally do you help solve it?", type: "scale", low: "Avoid it", high: "Step in naturally" },
    { key: "social_group_organising", q: "How comfortable are you organising people to do a task together?", type: "scale", low: "Very uncomfortable", high: "Enjoy it" },
  ],
  language: [
    { key: "language_verbal_fluency", q: "When you talk about something you like, do words come easily and quickly?", type: "scale", low: "Often stuck", high: "Flow very easily" },
    { key: "language_storytelling", q: "If you make up a story, how well does it have a beginning, middle, and end?", type: "scale", low: "All over the place", high: "Clear and gripping" },
    { key: "language_expression_clarity", q: "Can people usually understand exactly what you mean when you explain something?", type: "scale", low: "Often confused", high: "Always understand" },
    { key: "language_persuasion", q: "How often do you manage to change someone's mind with your words?", type: "scale", low: "Rarely", high: "Often" },
  ],
  naturalist: [
    { key: "naturalist_living_systems", q: "Do you notice details about plants, animals, or nature that others miss?", type: "scale", low: "Not really", high: "All the time" },
    { key: "naturalist_pattern_in_nature", q: "Can you see patterns in nature - like how leaves grow or clouds form?", type: "scale", low: "Never noticed", high: "Always see them" },
    { key: "naturalist_animal_empathy", q: "Do you naturally understand what an animal is feeling or needing?", type: "scale", low: "Not usually", high: "Very naturally" },
    { key: "naturalist_environment_awareness", q: "How aware are you of changes in your environment - weather, plants, seasons?", type: "scale", low: "Rarely notice", high: "Always aware" },
  ],
  intrapersonal: [
    { key: "intrapersonal_self_awareness", q: "How well do you understand why you feel certain emotions?", type: "scale", low: "Rarely understand", high: "Always know why" },
    { key: "intrapersonal_emotional_depth", q: "Do you feel things more deeply than most people around you seem to?", type: "scale", low: "Not really", high: "Much more deeply" },
    { key: "intrapersonal_resilience_signal", q: "When something goes wrong, how quickly do you find a way to keep going?", type: "scale", low: "Takes a long time", high: "Bounce back fast" },
    { key: "intrapersonal_reflective_thinking", q: "Do you often think carefully about your own actions and decisions?", type: "scale", low: "Rarely", high: "All the time" },
  ],
};

export const EQ_QUESTIONS = [
  { key: "eq_overall", q: "Overall, how well do you understand and manage your own feelings?", type: "scale", low: "Struggle a lot", high: "Very well" },
];

export const VISUALIZER_QUESTIONS = [
  { key: "visualizer_overall", q: "When you imagine something in your mind - a room, a face, a place - how clearly can you see it?", type: "scale", low: "Very fuzzy", high: "Like a photograph" },
];

export const ASSESSMENT_TASKS = [
  {
    key: "logical_pattern_matrix",
    type: "pattern_choice",
    domain: "logical",
    component: "pattern_recognition",
    title: {
      English: "The Wizard's Door Pyramid",
      Hindi: "जादूगर के दरवाजे का पिरामिड"
    },
    prompt: {
      English: "At the bottom of a stone tower, numbers are added together to open the lock. The bottom rows are 3 and 5, which add up to 8. Next to them are 5 and 9, which add up to 14. What number belongs at the very top of the pyramid? (3 + 5 = 8; 5 + 9 = 14; 8 + 14 = ?)",
      Hindi: "एक पत्थर के मीनार के नीचे, ताला खोलने के लिए संख्याओं को आपस में जोड़ा जाता है। सबसे नीचे की पंक्ति में 3 और 5 हैं, जो मिलकर 8 बनते हैं। उनके बगल में 5 और 9 हैं, जो मिलकर 14 बनते हैं। पिरामिड के सबसे ऊपर कौन सी संख्या आएगी? (3 + 5 = 8; 5 + 9 = 14; 8 + 14 = ?)"
    },
    sequence: ["3", "5", "9", "8", "14", "?"],
    options: ["18", "20", "22", "24"],
    answer: "22",
    metric: "correctness",
  },
  {
    key: "logical_riddle",
    type: "choice",
    domain: "logical",
    component: "sequence_logic",
    title: {
      English: "The Secret Cipher of Animals",
      Hindi: "जानवरों का गुप्त कोड"
    },
    prompt: {
      English: "A secret code matches animals to numbers based on their legs: Cat is 4, Spider is 8, Ant is 6. What number represents a Snake?",
      Hindi: "एक गुप्त कोड जानवरों के पैरों की संख्या के आधार पर उन्हें एक नंबर देता है: बिल्ली (Cat) 4 है, मकड़ी (Spider) 8 है, चींटी (Ant) 6 है। सांप (Snake) का नंबर क्या होगा?"
    },
    options: [
      {
        label: { English: "4", Hindi: "4" },
        value: 0
      },
      {
        label: { English: "0", Hindi: "0" },
        value: 4
      },
      {
        label: { English: "2", Hindi: "2" },
        value: 0
      },
      {
        label: { English: "6", Hindi: "6" },
        value: 0
      }
    ],
    metric: "judgement",
  },
  {
    key: "spatial_rotation",
    type: "pattern_choice",
    domain: "spatial",
    component: "mental_rotation",
    title: {
      English: "The Magic Clock Hand",
      Hindi: "जादुई घड़ी की सुई"
    },
    prompt: {
      English: "A glowing star on a clock moves around: First it points UP (12 o'clock), then RIGHT (3 o'clock), then DOWN (6 o'clock). Where will the star point next?",
      Hindi: "एक घड़ी पर चमकता हुआ सितारा घूमता है: पहले वह ऊपर (12 बजे) इशारा करता है, फिर दाएं (3 बजे), फिर नीचे (6 बजे)। इसके बाद सितारा किस दिशा में इशारा करेगा?"
    },
    sequence: ["↑", "→", "↓", "?"],
    options: ["↑", "→", "↓", "←"],
    answer: "←",
    metric: "correctness",
  },
  {
    key: "spatial_perspective",
    type: "choice",
    domain: "spatial",
    component: "mechanical_intuition",
    title: {
      English: "The Golden Key Shadow",
      Hindi: "चाबी की परछाई"
    },
    prompt: {
      English: "A 3D key shaped like a flat 'T' is held in front of a flashlight. If the flashlight shines directly from the LEFT side, what shape of shadow does the T-key make on the wall?",
      Hindi: "एक 'T' आकार की 3D चाबी को टॉर्च के सामने रखा गया है। यदि टॉर्च की रोशनी सीधे बाईं (LEFT) ओर से पड़ती है, तो दीवार पर चाबी की छाया का आकार कैसा दिखेगा?"
    },
    options: [
      { label: { English: "A long vertical rectangle", Hindi: "एक लंबी खड़ी पट्टी" }, value: 4 },
      { label: { English: "A perfect square", Hindi: "एक चौकोर वर्ग" }, value: 0 },
      { label: { English: "A cross shape", Hindi: "एक क्रॉस का आकार" }, value: 1 },
      { label: { English: "A round circle", Hindi: "एक गोल वृत्त" }, value: 0 }
    ],
    metric: "judgement",
  },
  {
    key: "visualizer_memory_grid",
    type: "memory_grid",
    domain: "creative",
    component: "visual_imagination",
    title: {
      English: "The Constellation Map",
      Hindi: "तारामंडल का नक्शा"
    },
    prompt: {
      English: "Look closely at the glowing stars in the magic night sky grid, and click them exactly as you remember them!",
      Hindi: "जादुई रात के आसमान के ग्रिड में चमकते सितारों को ध्यान से देखें, और ठीक वैसे ही उन पर क्लिक करें जैसे वे आपको याद हैं!"
    },
    gridSize: 9,
    highlights: [1, 3, 5, 7],
    revealMs: 2500,
    metric: "memory_span",
  },
  {
    key: "creative_uses",
    type: "idea_list",
    domain: "creative",
    component: "divergent_thinking",
    title: {
      English: "Sideways Gravity School",
      Hindi: "अनोखी सोच: तिरछा गुरुत्वाकर्षण"
    },
    prompt: {
      English: "Imagine that gravity suddenly starts working SIDEWAYS at your school instead of pulling you down! Write down at least 3 super funny or amazing things that would happen to you and your friends!",
      Hindi: "कल्पना कीजिए कि आपके स्कूल में गुरुत्वाकर्षण (gravity) नीचे खींचने के बजाय अचानक दाईं या बाईं ओर (SIDEWAYS) काम करने लगे! लिखें कि आपके और आपके दोस्तों के साथ कौन सी 3 सबसे मजेदार या अनोखी बातें होंगी!"
    },
    minIdeas: 3,
    metric: "fluency",
  },
  {
    key: "language_story_order",
    type: "order_steps",
    domain: "language",
    component: "storytelling",
    title: {
      English: "The Robot Escape Adventure",
      Hindi: "रोबोट से बचने का रोमांच"
    },
    prompt: {
      English: "Put these secret agent message pieces in the order that tells the exciting escape story!",
      Hindi: "इन जासूस संदेशों को सही क्रम में लगाएं ताकि रोमांचक फरारी की कहानी पूरी हो सके!"
    },
    steps: {
      English: [
        "We saw a giant iron gate guarded by two sleeping robots.",
        "I whispered the secret code word to open the gate.",
        "We ran through the dark jungle and found a hidden sailboat.",
        "We sailed away under the beautiful starry night sky."
      ],
      Hindi: [
        "हमने एक विशाल लोहे का दरवाजा देखा जिस पर दो सोते हुए रोबोट पहरा दे रहे थे।",
        "मैंने दरवाजा खोलने के लिए गुप्त कोड शब्द फुसफुसाया।",
        "हम अंधेरे जंगल में भागे और हमें एक छिपी हुई नाव मिली।",
        "हम सुंदर तारों वाले आसमान के नीचे नाव लेकर निकल गए।"
      ]
    },
    shuffled: {
      English: [
        "We ran through the dark jungle and found a hidden sailboat.",
        "We saw a giant iron gate guarded by two sleeping robots.",
        "We sailed away under the beautiful starry night sky.",
        "I whispered the secret code word to open the gate."
      ],
      Hindi: [
        "हम अंधेरे जंगल में भागे और हमें एक छिपी हुई नाव मिली।",
        "हमने एक विशाल लोहे का दरवाजा देखा जिस पर दो सोते हुए रोबोट पहरा दे रहे थे।",
        "हम सुंदर तारों वाले आसमान के नीचे नाव लेकर निकल गए।",
        "मैंने दरवाजा खोलने के लिए गुप्त कोड शब्द फुसफुसाया।"
      ]
    },
    metric: "sequence_accuracy",
  },
  {
    key: "language_analogy",
    type: "choice",
    domain: "language",
    component: "expression_clarity",
    title: {
      English: "The Secret Word Bridges",
      Hindi: "शब्दों का जादुई पुल"
    },
    prompt: {
      English: "Complete this word connection bridge: A FEATHER is to a BIRD as a SCALE is to...?",
      Hindi: "शब्दों का संबंध पूरा करें: एक पंख (FEATHER) चिड़िया (BIRD) के लिए है, तो एक शल्क (SCALE) किसके लिए है...?"
    },
    options: [
      { label: { English: "A Fish", Hindi: "एक मछली" }, value: 4 },
      { label: { English: "A Dog", Hindi: "एक कुत्ता" }, value: 0 },
      { label: { English: "A Tree", Hindi: "एक पेड़" }, value: 0 },
      { label: { English: "A River", Hindi: "एक नदी" }, value: 0 }
    ],
    metric: "judgement",
  },
  {
    key: "visual_reaction",
    type: "reaction",
    domain: "kinesthetic",
    component: "body_coordination",
    title: {
      English: "The Lightning Flash",
      Hindi: "बिजली की चमक"
    },
    prompt: {
      English: "Tap the center target as fast as a lightning bolt the exact millisecond it flashes happy gold!",
      Hindi: "जैसे ही बीच का गोला चमकीला सुनहरा (gold) रंग का हो, बिजली की तेजी से उस पर टैप करें!"
    },
    waitMs: 1200,
    metric: "reaction_time",
  },
  {
    key: "kinesthetic_motor_planning",
    type: "choice",
    domain: "kinesthetic",
    component: "body_coordination",
    title: {
      English: "The Treehouse Rope Bridge",
      Hindi: "रस्सी के पुल पर संतुलन"
    },
    prompt: {
      English: "You are crossing a high, wobbling rope bridge to reach a treehouse. A strong gust of wind suddenly blows from the right! What is the best way to balance your body so you don't slip?",
      Hindi: "आप पेड़ पर बने घर तक पहुँचने के लिए एक ऊँचे, हिलते हुए रस्सी के पुल को पार कर रहे हैं। अचानक दाईं ओर से तेज़ हवा का झोंका आता है! अपने शरीर को संतुलित करने का सबसे सुरक्षित तरीका क्या है ताकि आप फिसलें नहीं?"
    },
    options: [
      {
        label: { English: "Bend your knees slightly, spread your arms wide, and lean your weight slightly into the wind to the right", Hindi: "अपने घुटनों को थोड़ा मोड़ें, अपने दोनों हाथों को फैलाएं, और अपने वजन को थोड़ा दाईं ओर (हवा की तरफ) झुकाएं" },
        value: 4
      },
      {
        label: { English: "Stand completely straight and close your eyes", Hindi: "बिल्कुल सीधे खड़े हो जाएं और अपनी आँखें बंद कर लें" },
        value: 0
      },
      {
        label: { English: "Run as fast as you can to the other side", Hindi: "जितनी तेजी से हो सके दूसरी तरफ दौड़ें" },
        value: 1
      },
      {
        label: { English: "Sit down on the rope bridge and shout for help", Hindi: "रस्सी के पुल पर बैठ जाएं और मदद के लिए चिल्लाएं" },
        value: 2
      }
    ],
    metric: "judgement",
  },
  {
    key: "social_response",
    type: "choice",
    domain: "social",
    component: "empathy_recognition",
    title: {
      English: "The Lost Puppy Dilemma",
      Hindi: "खोए हुए पिल्ले का फैसला"
    },
    prompt: {
      English: "Your group of friends finds a cute lost puppy with a collar in the park. Two friends want to keep the puppy secretly in their house, but you know its owners must be worried. How do you lead your friends to do the right thing without making them angry?",
      Hindi: "आपके दोस्तों के समूह को पार्क में पट्टे वाला एक प्यारा खोया हुआ पिल्ला मिलता है। दो दोस्त पिल्ले को चुपके से अपने घर में रखना चाहते हैं, लेकिन आप जानते हैं कि उसके मालिक परेशान होंगे। आप अपने दोस्तों को बिना गुस्सा दिलाए सही काम करने के लिए कैसे मनाएंगे?"
    },
    options: [
      {
        label: { English: "Suggest calling the number on the collar together so you can all be heroes who saved and returned a lost pet", Hindi: "सुझाव दें कि सभी मिलकर पट्टे पर लिखे नंबर पर फोन करें ताकि आप सब उस खोए हुए पालतू जानवर को बचाने वाले हीरो बन सकें" },
        value: 4
      },
      {
        label: { English: "Fight with them and threaten to report them to the police", Hindi: "उनसे लड़ें और पुलिस में शिकायत करने की धमकी दें" },
        value: 0
      },
      {
        label: { English: "Walk away in silence and let them do whatever they want", Hindi: "चुपचाप चले जाएं और उन्हें जो करना है करने दें" },
        value: 1
      },
      {
        label: { English: "Take the puppy away from them by force and run", Hindi: "उनसे जबरदस्ती पिल्ला छीन लें और भाग जाएं" },
        value: 0
      }
    ],
    metric: "judgement",
  },
  {
    key: "social_conflict_resolution",
    type: "choice",
    domain: "social",
    component: "conflict_resolution",
    title: {
      English: "The Playground Game Dispute",
      Hindi: "खेल के मैदान का झगड़ा"
    },
    prompt: {
      English: "During a football match, two of your classmates start arguing loudly about whether the ball crossed the goal line. Everyone is shouting and the game has stopped. How do you resolve this conflict so everyone plays again happily?",
      Hindi: "एक फुटबॉल मैच के दौरान, आपके दो सहपाठी ज़ोर-ज़ोर से बहस करने लगते हैं कि गेंद गोल रेखा के पार गई या नहीं। सभी चिल्ला रहे हैं और खेल रुक गया है। आप इस झगड़े को कैसे सुलझाएंगे ताकि सब फिर से खुशी-खुशी खेल सकें?"
    },
    options: [
      {
        label: { English: "Suggest playing a quick penalty kick or flip a coin to decide, and remind them that having fun together is the main goal", Hindi: "एक त्वरित पेनल्टी किक लेने या सिक्का उछालकर फैसला करने का सुझाव दें, और उन्हें याद दिलाएं कि साथ में मज़ा करना ही मुख्य लक्ष्य है" },
        value: 4
      },
      {
        label: { English: "Shout louder than both of them to make them shut up", Hindi: "उन दोनों से भी ज़्यादा ज़ोर से चिल्लाएँ ताकि वे चुप हो जाएँ" },
        value: 0
      },
      {
        label: { English: "Take the football and walk home", Hindi: "फुटबॉल लेकर अपने घर चले जाएं" },
        value: 1
      },
      {
        label: { English: "Blame one classmate immediately to end the argument quickly", Hindi: "बहस को जल्दी खत्म करने के लिए तुरंत एक सहपाठी को दोषी ठहराएं" },
        value: 0
      }
    ],
    metric: "judgement",
  },
  {
    key: "naturalist_decomposer",
    type: "choice",
    domain: "naturalist",
    component: "living_systems",
    title: {
      English: "The Forest Soil Miracle",
      Hindi: "जंगल की मिट्टी का चमत्कार"
    },
    prompt: {
      English: "In a thick, green forest, giant dead leaves fall on the ground every day, but the forest floor stays clean and rich. Who are the hidden heroes cleaning the forest floor?",
      Hindi: "एक घने, हरे जंगल में, हर दिन विशाल सूखी पत्तियाँ ज़मीन पर गिरती हैं, लेकिन जंगल की ज़मीन साफ़ और उपजाऊ बनी रहती है। जंगल की ज़मीन को साफ़ करने वाले ये छिपे हुए हीरो कौन हैं?"
    },
    options: [
      { label: { English: "Tiny earthworms, mushrooms, and beetles (decomposers) turning leaves into soil", Hindi: "छोटे केंचुए, मशरूम, और भृंग (beetles) जो पत्तियों को उपजाऊ मिट्टी में बदलते हैं" }, value: 4 },
      { label: { English: "The forest wind blowing everything away", Hindi: "जंगल की हवा जो सब कुछ उड़ा ले जाती है" }, value: 0 },
      { label: { English: "The rain washing everything into rivers", Hindi: "बारिश जो सब कुछ नदियों में बहा ले जाती है" }, value: 0 },
      { label: { English: "Wild forest animals eating all the dry leaves", Hindi: "जंगली जानवर जो सूखी पत्तियाँ खा जाते हैं" }, value: 1 }
    ],
    metric: "classification",
  },
  {
    key: "naturalist_wind_disperse",
    type: "choice",
    domain: "naturalist",
    component: "living_systems",
    title: {
      English: "The Secret Butterfly Garden",
      Hindi: "तितलियों का जादुई बगीचा"
    },
    prompt: {
      English: "You want to attract colorful butterflies to live in your school garden. Which of these actions will help the butterflies the MOST?",
      Hindi: "आप अपने स्कूल के बगीचे में रंग-बिरंगी तितलियों को आकर्षित करना चाहते हैं। इनमें से कौन सा काम तितलियों की सबसे ज़्यादा मदद करेगा?"
    },
    options: [
      {
        label: { English: "Plant bright native flowering plants that have sweet nectar and keep fresh shallow water trays nearby", Hindi: "मीठे मकरंद वाले चमकदार स्थानीय फूलों के पौधे लगाएं और पास में उथले बर्तनों में ताजा पानी रखें" },
        value: 4
      },
      {
        label: { English: "Spray strong insect spray to keep other bugs away from the plants", Hindi: "पौधों से दूसरे कीड़ों को दूर रखने के लिए तेज़ कीटनाशक का छिड़काव करें" },
        value: 0
      },
      {
        label: { English: "Cover all the flowers with plastic sheets so they don't get dirty", Hindi: "सभी फूलों को प्लास्टिक की शीट से ढक दें ताकि वे गंदे न हों" },
        value: 0
      },
      {
        label: { English: "Catch butterflies from other parks and release them inside your garden", Hindi: "दूसरे पार्कों से तितलियों को पकड़ें और उन्हें अपने बगीचे में छोड़ दें" },
        value: 1
      }
    ],
    metric: "classification",
  },
  {
    key: "intrapersonal_reflection",
    type: "scale",
    domain: "intrapersonal",
    component: "reflective_thinking",
    title: {
      English: "The Brave Explorer Goal",
      Hindi: "साहसी खोजकर्ता का संकल्प"
    },
    prompt: {
      English: "When you face a challenge that is very hard for you, do you tell yourself that you can get better at it with practice?",
      Hindi: "जब आप किसी बहुत कठिन चुनौती का सामना करते हैं, तो क्या आप खुद से कहते हैं कि अभ्यास करने से आप इसमें बेहतर हो सकते हैं?"
    },
    low: { English: "Never, I get discouraged", Hindi: "कभी नहीं, मैं हिम्मत हार जाता हूँ" },
    high: { English: "Always, I love to learn!", Hindi: "हमेशा, मुझे सीखना पसंद है!" },
    metric: "self_reflection",
  },
  {
    key: "intrapersonal_frustration",
    type: "choice",
    domain: "intrapersonal",
    component: "resilience_signal",
    title: {
      English: "The Lost Kite Adventure",
      Hindi: "खोई हुई पतंग का हौसला"
    },
    prompt: {
      English: "You spent two days making a beautiful paper kite. On its very first flight, it gets stuck high in a thorny tree. You feel upset and want to cry. What is the most helpful thing to tell yourself?",
      Hindi: "आपने दो दिन लगाकर कागज की एक सुंदर पतंग बनाई। पहली ही उड़ान में, वह एक कांटेदार पेड़ पर ऊँचाई पर फंस जाती है। आप बहुत परेशान महसूस करते हैं और आपका रोने का मन करता है। ऐसे में खुद को समझाने के लिए सबसे मददगार बात क्या होगी?"
    },
    options: [
      {
        label: { English: "It is normal to feel sad, but crying won't get it down. Let me take a deep breath and plan to reach it with a long stick.", Hindi: "उदास महसूस होना सामान्य है, लेकिन रोने से पतंग नीचे नहीं आएगी। मैं एक गहरी सांस लेता हूं और एक लंबी छड़ी से उसे सुरक्षित निकालने की योजना बनाता हूं।" },
        value: 4
      },
      {
        label: { English: "I am terrible at flying kites. I will never make or fly one again.", Hindi: "मैं पतंग उड़ाने में बहुत बेकार हूं। मैं अब कभी पतंग नहीं बनाऊंगा और न ही उड़ाऊंगा।" },
        value: 0
      },
      {
        label: { English: "I will kick the tree as hard as I can until it shakes.", Hindi: "मैं पेड़ को इतनी जोर से लात मारूंगा जब तक कि वह हिलने न लगे।" },
        value: 0
      },
      {
        label: { English: "It was a bad kite anyway, I don't care.", Hindi: "वह पतंग वैसे भी खराब थी, मुझे कोई परवाह नहीं है।" },
        value: 1
      }
    ],
    metric: "judgement",
  }
];

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
      English: "The Project Deadline",
      Hindi: "The Project Deadline"
    },
    prompt: {
      English: "Your team has 10 minutes left to submit a project. The poster looks great, but one teammate is upset because the group forgot to include their drawing. The other teammates want to submit immediately to win. What do you do?",
      Hindi: "Your team has 10 minutes left to submit a project. The poster looks great, but one teammate is upset because the group forgot to include their drawing. The other teammates want to submit immediately to win. What do you do?"
    },
    options: [
      {
        label: { English: "Submit the project now to ensure the team wins, then promise the teammate to highlight their drawing during the presentation.", Hindi: "Submit the project now to ensure the team wins, then promise the teammate to highlight their drawing during the presentation." },
        value: 4
      },
      {
        label: { English: "Delay the submission to glue the drawing on, even if it means missing the absolute deadline, because team unity is more important.", Hindi: "Delay the submission to glue the drawing on, even if it means missing the absolute deadline, because team unity is more important." },
        value: 4
      },
      {
        label: { English: "Find a quick, creative compromise, like taping the drawing to the back of the poster as an 'Appendix' to save time.", Hindi: "Find a quick, creative compromise, like taping the drawing to the back of the poster as an 'Appendix' to save time." },
        value: 4
      },
      {
        label: { English: "Do nothing and let the other teammates decide.", Hindi: "Do nothing and let the other teammates decide." },
        value: 1
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
    key: "naturalist_weather_pattern",
    type: "choice",
    domain: "naturalist",
    component: "pattern_in_nature",
    title: {
      English: "The Rain Clouds",
      Hindi: "बारिश के बादल"
    },
    prompt: {
      English: "You are playing outdoors and notice the wind suddenly blowing cold, swallows flying low, and the sky turning dark grey. What is nature telling you?",
      Hindi: "आप बाहर खेल रहे हैं और अचानक ठंडी हवा चलने लगती है, चिड़ियाँ नीचे उड़ने लगती हैं, और आसमान गहरा भूरा हो जाता है। प्रकृति आपको क्या बता रही है?"
    },
    options: [
      { label: { English: "A heavy rain shower is coming very soon", Hindi: "बहुत जल्द तेज़ बारिश होने वाली है" }, value: 4 },
      { label: { English: "The sun is going to shine brighter", Hindi: "सूरज और तेज़ चमकने वाला है" }, value: 0 },
      { label: { English: "An earthquake is happening", Hindi: "भूकंप आ रहा है" }, value: 0 },
      { label: { English: "A cold winter night has started", Hindi: "ठंड की रात शुरू हो गई है" }, value: 1 }
    ],
    metric: "judgement",
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
      English: "The Stuck Kite",
      Hindi: "The Stuck Kite"
    },
    prompt: {
      English: "You spent two days making a beautiful paper kite, but on its first flight it gets stuck high in a thorny tree. You cannot reach it. What do you do?",
      Hindi: "You spent two days making a beautiful paper kite, but on its first flight it gets stuck high in a thorny tree. You cannot reach it. What do you do?"
    },
    options: [
      {
        label: { English: "Accept that it's gone for now, and start designing a new, improved paper kite using what you learned.", Hindi: "Accept that it's gone for now, and start designing a new, improved paper kite using what you learned." },
        value: 4
      },
      {
        label: { English: "Go find a helper or a long tool to try retrieving it, even if it might take a long time and rip the paper.", Hindi: "Go find a helper or a long tool to try retrieving it, even if it might take a long time and rip the paper." },
        value: 4
      },
      {
        label: { English: "Ask friends for ideas on how to build a simple pulley or tool to hook the string.", Hindi: "Ask friends for ideas on how to build a simple pulley or tool to hook the string." },
        value: 4
      },
      {
        label: { English: "Leave the park feeling angry and give up on flying kites altogether.", Hindi: "Leave the park feeling angry and give up on flying kites altogether." },
        value: 1
      }
    ],
    metric: "judgement",
  },
  {
    key: "deep_discovery_flow",
    type: "open_ended",
    domain: "intrapersonal",
    component: "self_awareness",
    title: {
      English: "Flow State Tracker",
      Hindi: "ध्यान केंद्रित करने वाली गतिविधियाँ"
    },
    prompt: {
      English: "Tell us about an activity (like building, drawing, reading, or playing) that makes you completely lose track of time. What are you doing, and what makes it so exciting?",
      Hindi: "हमें किसी ऐसी गतिविधि (जैसे कुछ बनाना, चित्र बनाना, पढ़ना, या खेलना) के बारे में बताएं जिसमें आप समय का ध्यान बिल्कुल भूल जाते हैं। आप क्या कर रहे होते हैं, और वह बात आपको इतनी रोमांचक क्यों लगती है?"
    },
    metric: "narrative_expression"
  },
  {
    key: "deep_discovery_pride",
    type: "open_ended",
    domain: "intrapersonal",
    component: "self_awareness",
    title: {
      English: "Your Proudest Moment",
      Hindi: "आपका सबसे गौरवपूर्ण क्षण"
    },
    prompt: {
      English: "What is one project, creation, or achievement that you are most proud of? Describe what you did and why it felt so special to you.",
      Hindi: "कोई एक प्रोजेक्ट, रचना, या उपलब्धि क्या है जिस पर आपको सबसे ज्यादा गर्व है? वर्णन करें कि आपने क्या किया और वह आपके लिए इतना विशेष क्यों था।"
    },
    metric: "narrative_expression"
  },
  {
    key: "deep_discovery_curiosity",
    type: "open_ended",
    domain: "intrapersonal",
    component: "reflective_thinking",
    title: {
      English: "The One-Year Learning Quest",
      Hindi: "एक साल का सीखने का सफर"
    },
    prompt: {
      English: "If you could spend one whole year learning about anything you want without any exams or grades, what topic or skill would you choose, and why?",
      Hindi: "यदि आप बिना किसी परीक्षा या ग्रेड के अपनी पसंद की किसी भी चीज़ को सीखने में एक पूरा वर्ष बिता सकते हैं, तो आप किस विषय या कौशल को चुनेंगे, और क्यों?"
    },
    metric: "narrative_expression"
  },
  {
    key: "deep_discovery_vision",
    type: "open_ended",
    domain: "social",
    component: "peer_influence",
    title: {
      English: "The Big Problem Solver",
      Hindi: "बड़ी समस्या का समाधान"
    },
    prompt: {
      English: "If you were given resources to solve one big problem in your school, community, or the world, what problem would you choose, and how would you start solving it?",
      Hindi: "यदि आपको अपने स्कूल, समुदाय या दुनिया में एक बड़ी समस्या को हल करने के लिए संसाधन दिए जाएं, तो आप कौन सी समस्या चुनेंगे, और आप इसे कैसे हल करना शुरू करेंगे?"
    },
    metric: "narrative_expression"
  }
];

function getComplexityLevel(schoolYear, age) {
  const sy = String(schoolYear || "").toLowerCase();
  if (sy.includes("class 4") || sy.includes("class 5") || sy.includes("class 6") || sy.includes("grade 4") || sy.includes("grade 5") || sy.includes("grade 6")) {
    return "PRIMARY";
  }
  if (sy.includes("class 7") || sy.includes("class 8") || sy.includes("grade 7") || sy.includes("grade 8")) {
    return "MIDDLE";
  }
  if (sy.includes("class 9") || sy.includes("class 10") || sy.includes("grade 9") || sy.includes("grade 10")) {
    return "SECONDARY";
  }
  if (sy.includes("class 11") || sy.includes("class 12") || sy.includes("grade 11") || sy.includes("grade 12")) {
    return "SENIOR";
  }
  const numericAge = Number(age);
  if (!isNaN(numericAge) && numericAge > 0) {
    if (numericAge <= 11) return "PRIMARY";
    if (numericAge <= 13) return "MIDDLE";
    if (numericAge <= 15) return "SECONDARY";
    return "SENIOR";
  }
  return "MIDDLE"; // Default fallback
}

export function getAdaptedDiscoveryQuestions(schoolYear, age, language) {
  const level = getComplexityLevel(schoolYear, age);
  const isHindi = language === "Hindi";

  return [
    {
      id: "q_discovery_1",
      question: {
        PRIMARY: isHindi
          ? "आपके पांच दोस्त खेल रहे हैं पर उन्हें नहीं पता क्या खेलना है। 🎮 आप पहले क्या करेंगे?"
          : "Five friends want to play but don't know what game to play. 🎮 What do you do first?",
        MIDDLE: isHindi
          ? "आपकी टीम किसी प्रोजेक्ट के विचार पर सहमत नहीं हो पा रही है। 💡 आप क्या करते हैं?"
          : "Your team cannot agree on a project idea. 💡 What do you do?",
        SECONDARY: isHindi
          ? "आप स्कूल में एक नया क्लब शुरू करना चाहते हैं। 🚀 आपका पहला कदम क्या है?"
          : "You want to start a new school club. 🚀 What is your first step?",
        SENIOR: isHindi
          ? "आपकी प्रोजेक्ट टीम समय सीमा (deadlines) को पूरा नहीं कर पा रही है। ⏳ आप इसे कैसे संभालेंगे?"
          : "Your project team is missing deadlines. ⏳ How would you handle it?"
      }[level],
      type: "choice",
      options: {
        PRIMARY: [
          { label: isHindi ? "खिलाड़ियों को गिनकर खिलौनों को बांटूंगा" : "Count the players and divide the toys", emoji: "🧩", domains: ["logical"] },
          { label: isHindi ? "एक नया खेल बनाने का चित्र बनाऊंगा" : "Draw a picture of a new game we can make", emoji: "🎨", domains: ["creative"] },
          { label: isHindi ? "एक खेल का सुझाव दूंगा और नियम समझाऊंगा" : "Suggest a game and explain the rules", emoji: "🗣️", domains: ["language"] },
          { label: isHindi ? "उन्हें दो टीमों में बांटकर शुरू करूंगा" : "Split them into two teams and get started", emoji: "🤝", domains: ["social"] }
        ],
        MIDDLE: [
          { label: isHindi ? "प्रत्येक विचार के फायदे और नुकसान की सूची बनाएं" : "List the pros and cons of each project idea", emoji: "🧩", domains: ["logical"] },
          { label: isHindi ? "दो विचारों को मिलाकर एक नया रचनात्मक विचार बनाएं" : "Combine two different ideas into a new creative one", emoji: "🎨", domains: ["creative"] },
          { label: isHindi ? "सभी विचारों का सारांश लिखकर चर्चा करें" : "Write a summary of all ideas to discuss with the team", emoji: "🗣️", domains: ["language"] },
          { label: isHindi ? "जल्दी निर्णय लेने के लिए वोट कराने का सुझाव दें" : "Propose a vote to decide quickly and move forward", emoji: "🤝", domains: ["social"] }
        ],
        SECONDARY: [
          { label: isHindi ? "गतिविधियों की सूची और एक विस्तृत समय-सारणी बनाएं" : "Create a detailed schedule and list of learning activities", emoji: "🧩", domains: ["logical"] },
          { label: isHindi ? "एक आकर्षक लोगो और क्लब की थीम डिजाइन करें" : "Design a stylish logo and branding theme for the club", emoji: "🎨", domains: ["creative"] },
          { label: isHindi ? "छात्रों को शामिल होने के लिए मनाने हेतु एक भाषण दें" : "Give an inspiring presentation to convince students to join", emoji: "🗣️", domains: ["language"] },
          { label: isHindi ? "काम बांटने के लिए एक नेतृत्व टीम तैयार करें" : "Recruit a core leadership team to share responsibilities", emoji: "🤝", domains: ["social"] }
        ],
        SENIOR: [
          { label: isHindi ? "समय-सीमा की समीक्षा करें, बाधाओं को पहचानें और कार्यों को फिर से सौंपें" : "Review the timeline, identify bottlenecks, and re-allocate tasks", emoji: "🧩", domains: ["logical"] },
          { label: isHindi ? "परियोजना को सरल बनाने के लिए एक रचनात्मक बदलाव का सुझाव दें" : "Pitch a creative pivot to simplify the project requirements", emoji: "🎨", domains: ["creative"] },
          { label: isHindi ? "विस्तृत स्थिति रिपोर्ट लिखें और समय बढ़ाने के लिए बातचीत करें" : "Write a detailed status report and negotiate a deadline extension", emoji: "🗣️", domains: ["language"] },
          { label: isHindi ? "बैठक आयोजित कर विवादों को सुलझाएं और टीम को प्रेरित करें" : "Facilitate a team meeting to resolve conflicts and motivate members", emoji: "🤝", domains: ["social"] }
        ]
      }[level]
    },
    {
      id: "q_discovery_2",
      question: {
        PRIMARY: isHindi
          ? "आपको कार्डबोर्ड, डंडियाँ और धागे का एक डिब्बा मिलता है। 📦 आप पहले क्या करेंगे?"
          : "You get a box of cardboard, sticks, and strings. 📦 What do you do first?",
        MIDDLE: isHindi
          ? "आप विज्ञान की कक्षा में एक नया मॉडल बना रहे हैं। 🔬 आप पहले क्या करते हैं?"
          : "You are designing a prototype in science class. 🔬 What do you do first?",
        SECONDARY: isHindi
          ? "आप स्कूल की प्रदर्शनी के लिए एक उत्पाद बनाना चाहते हैं। 🛍️ आप पहले क्या करते हैं?"
          : "You want to create a product for a school exhibition. 🛍️ What do you do first?",
        SENIOR: isHindi
          ? "आप एक नया स्टार्टअप उत्पाद विकसित कर रहे हैं। 💼 आपका पहला कदम क्या है?"
          : "You are developing a startup product. 💼 What is your first step?"
      }[level],
      type: "choice",
      options: {
        PRIMARY: [
          { label: isHindi ? "खिलौना घर या मीनार बनाऊंगा" : "Build a toy house or a tall tower", emoji: "🔨", domains: ["spatial"] },
          { label: isHindi ? "उसे सुंदर रंगों से सजाऊंगा" : "Decorate it with bright colors", emoji: "🎨", domains: ["creative"] },
          { label: isHindi ? "उन्हें आकार के हिसाब से अलग करूंगा" : "Sort them by size and shape", emoji: "🧩", domains: ["logical"] },
          { label: isHindi ? "डंडी को अपनी उंगली पर संतुलित करूंगा" : "Balance a stick on your finger", emoji: "💃", domains: ["kinesthetic"] }
        ],
        MIDDLE: [
          { label: isHindi ? "कार्डबोर्ड का उपयोग करके एक मॉडल बनाएं" : "Build a physical model using cardboard", emoji: "🔨", domains: ["spatial"] },
          { label: isHindi ? "उसका एक सुंदर, कलात्मक चित्र (sketch) बनाएं" : "Sketch a beautiful, artistic blueprint", emoji: "🎨", domains: ["creative"] },
          { label: isHindi ? "जांचें कि उसकी मशीनरी कैसे काम करती है" : "Analyze how the mechanics work step-by-step", emoji: "🧩", domains: ["logical"] },
          { label: isHindi ? "सामग्री को उठाकर देखें कि वह कितनी भारी और मजबूत है" : "Test how heavy and sturdy the materials feel physically", emoji: "💃", domains: ["kinesthetic"] }
        ],
        SECONDARY: [
          { label: isHindi ? "उस उपकरण का एक कार्यशील प्रोटोटाइप तैयार करें" : "Construct a working prototype of the device", emoji: "🔨", domains: ["spatial"] },
          { label: isHindi ? "एक आकर्षक ब्रांड लोगो और पैकेजिंग डिज़ाइन करें" : "Design a stylish brand logo and packaging", emoji: "🎨", domains: ["creative"] },
          { label: isHindi ? "लागत और बजट का हिसाब लगाएं" : "Calculate the material costs and budget", emoji: "🧩", domains: ["logical"] },
          { label: isHindi ? "ग्राहकों को दिखाएं कि उत्पाद कैसे काम करता है" : "Demonstrate the product's physical movement to users", emoji: "💃", domains: ["kinesthetic"] }
        ],
        SENIOR: [
          { label: isHindi ? "भौतिक/स्थानिक ब्लूप्रिंट और असेंबली प्रक्रिया तैयार करें" : "Engineer the physical/spatial blueprint and assembly process", emoji: "🔨", domains: ["spatial"] },
          { label: isHindi ? "सौंदर्य डिजाइन और रचनात्मक ब्रांडिंग का निर्देश दें" : "Direct the aesthetic design and creative branding strategy", emoji: "🎨", domains: ["creative"] },
          { label: isHindi ? "सिस्टम आर्किटेक्चर और डेटा मॉडल को अनुकूलित करें" : "Optimize the functional architecture and database layout", emoji: "🧩", domains: ["logical"] },
          { label: isHindi ? "उपयोगकर्ता अनुभव, सुविधा और शारीरिक संपर्क का परीक्षण करें" : "Test usability, ergonomic comfort, and physical interaction", emoji: "💃", domains: ["kinesthetic"] }
        ]
      }[level]
    },
    {
      id: "q_discovery_3",
      question: {
        PRIMARY: isHindi
          ? "आपको घास में एक सुंदर हरा कीड़ा मिलता है। 🐜 आप पहले क्या करेंगे?"
          : "You find a cool green bug in the grass. 🐜 What do you do first?",
        MIDDLE: isHindi
          ? "आपको स्कूल के मैदान में एक सुंदर पक्षी दिखाई देता है। 🦅 आप क्या करते हैं?"
          : "You notice a beautiful bird in the schoolyard. 🦅 What do you do?",
        SECONDARY: isHindi
          ? "आप प्रकृति की सैर (nature trail) पर हैं। 🌲 आपको सबसे ज्यादा क्या आकर्षित करता है?"
          : "You are on a nature trail. 🌲 What attracts you most?",
        SENIOR: isHindi
          ? "आप पर्यावरण संरक्षण का अध्ययन कर रहे हैं। 🌍 आपका ध्यान किस पर है?"
          : "You are studying environmental conservation. 🌍 What is your focus?"
      }[level],
      type: "choice",
      options: {
        PRIMARY: [
          { label: isHindi ? "देखूंगा कि वह कैसे चलता है और क्या खाता है" : "Watch it crawl and see what it eats", emoji: "🦋", domains: ["naturalist"] },
          { label: isHindi ? "अपनी कॉपी में उसका चित्र बनाऊंगा" : "Draw a picture of it in my notebook", emoji: "🎨", domains: ["creative"] },
          { label: isHindi ? "बिना छुए चुपचाप उसे देखता रहूंगा" : "Sit quietly and watch it without touching", emoji: "🤔", domains: ["intrapersonal"] },
          { label: isHindi ? "अपने दोस्तों को बुलाकर उसके बारे में बताऊंगा" : "Call my friends to tell them all about it", emoji: "🗣️", domains: ["language"] }
        ],
        MIDDLE: [
          { label: isHindi ? "उसकी प्रजाति और रहने की जगह पहचानने की कोशिश करें" : "Try to identify its species and habitat", emoji: "🦋", domains: ["naturalist"] },
          { label: isHindi ? "उस पर एक कविता लिखें या उसका चित्र बनाएं" : "Write a poem or sketch its feathers", emoji: "🎨", domains: ["creative"] },
          { label: isHindi ? "प्रकृति के उस शांत क्षण का आनंद लें" : "Enjoy the peaceful, quiet moment in nature", emoji: "🤔", domains: ["intrapersonal"] },
          { label: isHindi ? "अपने सहपाठी को उसके व्यवहार के बारे में समझाएं" : "Explain its behavior to your classmate", emoji: "🗣️", domains: ["language"] }
        ],
        SECONDARY: [
          { label: isHindi ? "यह अध्ययन करना कि स्थानीय पर्यावरण कैसे काम करता है" : "Studying how the local ecosystem functions", emoji: "🦋", domains: ["naturalist"] },
          { label: isHindi ? "सुंदर दृश्यों की तस्वीरें खींचना" : "Photographing the scenic nature views", emoji: "🎨", domains: ["creative"] },
          { label: isHindi ? "शांत जंगल में अपने लक्ष्यों के बारे में सोचना" : "Reflecting on your goals in the quiet woods", emoji: "🤔", domains: ["intrapersonal"] },
          { label: isHindi ? "समूह का मार्गदर्शन करना और रास्ते के बारे में बताना" : "Guiding the group and explaining the route details", emoji: "🗣️", domains: ["language"] }
        ],
        SENIOR: [
          { label: isHindi ? "मिट्टी की जैव विविधता और पौधों के अनुकूलन का विश्लेषण करना" : "Analyzing soil biodiversity and plant adaptations", emoji: "🦋", domains: ["naturalist"] },
          { label: isHindi ? "प्रकृति की सुंदरता पर एक वृत्तचित्र (documentary) बनाना" : "Creating a visual documentary about nature's ecosystem", emoji: "🎨", domains: ["creative"] },
          { label: isHindi ? "प्रकृति के प्रति मानवता के नैतिक संबंधों पर चिंतन करना" : "Reflecting on humanity's ethical relationship with nature", emoji: "🤔", domains: ["intrapersonal"] },
          { label: isHindi ? "स्थानीय अधिकारियों के समक्ष नीति प्रस्ताव प्रस्तुत करना" : "Presenting a policy proposal to local authorities", emoji: "🗣️", domains: ["language"] }
        ]
      }[level]
    },
    {
      id: "q_discovery_4",
      question: {
        PRIMARY: isHindi
          ? "एक नया सहपाठी उदास और अकेला बैठा है। 😔 आप पहले क्या करेंगे?"
          : "A new classmate looks sad and lonely. 😔 What do you do first?",
        MIDDLE: isHindi
          ? "एक सहपाठी को स्कूल में तालमेल बिठाने में परेशानी हो रही है। 🤝 आप क्या करते हैं?"
          : "A classmate is struggling to fit in at school. 🤝 What do you do?",
        SECONDARY: isHindi
          ? "आप स्कूल में सबको शामिल करने की भावना को बढ़ाना चाहते हैं। 🏫 आप क्या करते हैं?"
          : "You want to improve school community inclusion. 🏫 What do you do?",
        SENIOR: isHindi
          ? "आप सामुदायिक अलगाव की समस्या को दूर कर रहे हैं। 👥 आपका दृष्टिकोण क्या है?"
          : "You are addressing community isolation. 👥 What is your approach?"
      }[level],
      type: "choice",
      options: {
        PRIMARY: [
          { label: isHindi ? "उन्हें अपने दोस्तों के समूह में शामिल होने के लिए कहूंगा" : "Invite them to join your group of friends", emoji: "🤝", domains: ["social"] },
          { label: isHindi ? "नमस्ते कहूंगा और उनसे बातचीत शुरू करूंगा" : "Say hello and start a friendly chat", emoji: "🗣️", domains: ["language"] },
          { label: isHindi ? "चुपचाप सोचूंगा कि वे कैसा महसूस कर रहे होंगे" : "Wonder quietly how they are feeling inside", emoji: "🤔", domains: ["intrapersonal"] },
          { label: isHindi ? "उन्हें पकड़म-पकड़ाई या दौड़ने वाले खेल के लिए कहूंगा" : "Ask them to play tag or run with you", emoji: "🏃", domains: ["kinesthetic"] }
        ],
        MIDDLE: [
          { label: isHindi ? "उन्हें अलग-अलग क्लबों और अध्ययन समूहों से परिचित कराएं" : "Introduce them to different clubs and study groups", emoji: "🤝", domains: ["social"] },
          { label: isHindi ? "उन्हें सहज महसूस कराने के लिए एक अच्छी बातचीत करें" : "Have a warm conversation to make them feel welcome", emoji: "🗣️", domains: ["language"] },
          { label: isHindi ? "सोचें कि उनके स्थान पर होने पर कैसा महसूस होता है" : "Think about how it feels to be in their place", emoji: "🤔", domains: ["intrapersonal"] },
          { label: isHindi ? "उन्हें फुटबॉल या किसी खेल के मैच में खेलने के लिए आमंत्रित करें" : "Invite them to play in a football or sports match", emoji: "🏃", domains: ["kinesthetic"] }
        ],
        SECONDARY: [
          { label: isHindi ? "नए छात्रों के लिए एक स्वागत समिति बनाएं" : "Form a welcoming committee for new students", emoji: "🤝", domains: ["social"] },
          { label: isHindi ? "सभी का स्वागत करने पर एक लेख या पोस्ट लिखें" : "Write an article or post about welcoming everyone", emoji: "🗣️", domains: ["language"] },
          { label: isHindi ? "चिंतन करें कि आप अपने व्यवहार को और अधिक समावेशी कैसे बना सकते हैं" : "Reflect on how to make your own actions more inclusive", emoji: "🤔", domains: ["intrapersonal"] },
          { label: isHindi ? "एक दोस्ताना खेलकूद प्रतियोगिता (sports tournament) आयोजित करें" : "Organize a friendly sports tournament", emoji: "🏃", domains: ["kinesthetic"] }
        ],
        SENIOR: [
          { label: isHindi ? "सहकर्मी परामर्श नेटवर्क (peer mentorship network) स्थापित करना" : "Establishing a peer mentorship network", emoji: "🤝", domains: ["social"] },
          { label: isHindi ? "सहानुभूति और संचार पर एक प्रभावशाली भाषण लिखना" : "Writing a persuasive speech on empathy and communication", emoji: "🗣️", domains: ["language"] },
          { label: isHindi ? "पूर्वाग्रह और समावेश पर एक आत्म-चिंतन मार्गदर्शिका विकसित करना" : "Developing a self-reflection guide on bias and inclusion", emoji: "🤔", domains: ["intrapersonal"] },
          { label: isHindi ? "एक शारीरिक टीम-निर्माण गतिविधि या कार्यशाला का संचालन करना" : "Coaching a physical team-building activity or workshop", emoji: "🏃", domains: ["kinesthetic"] }
        ]
      }[level]
    },
    {
      id: "q_discovery_5",
      question: {
        PRIMARY: isHindi
          ? "आपका बनाया हुआ खिलौना मीनार गिर जाता है। 🧱 आप इसके बाद क्या करेंगे?"
          : "Your toy tower falls down. 🧱 What do you do next?",
        MIDDLE: isHindi
          ? "एक प्रतियोगिता में आपकी टीम का पुल का मॉडल ढह जाता है। 🌉 आप क्या करते हैं?"
          : "Your team's bridge model collapses in a contest. 🌉 What do you do?",
        SECONDARY: isHindi
          ? "आपका कोई सॉफ्टवेयर प्रोग्राम या उपकरण काम करना बंद कर देता है। 💻 आपकी क्या प्रतिक्रिया होती है?"
          : "Your software program or device stops working. 💻 What is your reaction?",
        SENIOR: isHindi
          ? "आपके नए स्टार्टअप उत्पाद का लॉन्च विफल हो जाता है। 📉 आप क्या करते हैं?"
          : "Your entrepreneurial venture's product launch fails. 📉 What do you do?"
      }[level],
      type: "choice",
      options: {
        PRIMARY: [
          { label: isHindi ? "सोचूंगा कि वह क्यों गिरा और उसका डिजाइन बदलूंगा" : "Think why it fell and change the design", emoji: "🧩", domains: ["logical"] },
          { label: isHindi ? "नीचे चौड़े ब्लॉक लगाकर उसे दोबारा बनाऊंगा" : "Build it again with wider blocks at the bottom", emoji: "🔨", domains: ["spatial"] },
          { label: isHindi ? "इस बार उसे और तेज़ी से बनाने की कोशिश करूंगा" : "Try to build it faster this time", emoji: "🏃", domains: ["kinesthetic"] },
          { label: isHindi ? "अपने दोस्त को साथ मिलकर बनाने के लिए कहूंगा" : "Ask a friend to build it with you", emoji: "🤝", domains: ["social"] }
        ],
        MIDDLE: [
          { label: isHindi ? "उन कमजोर हिस्सों का विश्लेषण करें जो विफल रहे" : "Analyze the stress points that failed", emoji: "🧩", domains: ["logical"] },
          { label: isHindi ? "ढांचे की मजबूती के लिए नए सिरे से डिजाइन बनाएं" : "Redesign the structural support layout", emoji: "🔨", domains: ["spatial"] },
          { label: isHindi ? "पूरी ऊर्जा के साथ तुरंत दोबारा बनाने का काम शुरू करें" : "Start rebuild work immediately with high energy", emoji: "🏃", domains: ["kinesthetic"] },
          { label: isHindi ? "दोबारा काम करने के लिए टीम के साथियों में काम बांटें" : "Coordinate the team to split the rebuild tasks", emoji: "🤝", domains: ["social"] }
        ],
        SECONDARY: [
          { label: isHindi ? "गलती ढूंढने के लिए कोड की कदम-दर-कदम जांच (debug) करें" : "Debug the code step-by-step to find the error", emoji: "🧩", domains: ["logical"] },
          { label: isHindi ? "उपकरण के भौतिक या इंटरफेस लेआउट को फिर से तैयार करें" : "Redesign the physical or interface layout", emoji: "🔨", domains: ["spatial"] },
          { label: isHindi ? "घटकों (components) को जल्दी से रीसेट या दोबारा जोड़ें" : "Quickly rebuild or reset the hardware components", emoji: "🏃", domains: ["kinesthetic"] },
          { label: isHindi ? "समाधान खोजने के लिए अपने समूह के साथ चर्चा करें" : "Consult with your group to brainstorm fixes", emoji: "🤝", domains: ["social"] }
        ],
        SENIOR: [
          { label: isHindi ? "विस्तृत डेटा विश्लेषण करें ताकि विफलता के कारणों का पता चले" : "Perform a root-cause data analysis on the failure", emoji: "🧩", domains: ["logical"] },
          { label: isHindi ? "उत्पाद की मुख्य वास्तुकला (architecture) और डिजाइन को फिर से तैयार करें" : "Re-engineer the core product architecture and design", emoji: "🔨", domains: ["spatial"] },
          { label: isHindi ? "परिचालन सुधार योजना (recovery plan) को तेजी से लागू करें" : "Execute the operational recovery plan quickly", emoji: "🏃", domains: ["kinesthetic"] },
          { label: isHindi ? "हितधारकों और टीम के सदस्यों को प्रेरित करें और काम में लगाएं" : "Re-align and motivate stakeholders and team members", emoji: "🤝", domains: ["social"] }
        ]
      }[level]
    },
    {
      id: "q_discovery_6",
      question: {
        PRIMARY: isHindi
          ? "आपके स्कूल में एक बड़ा मेला लग रहा है। 🎪 आपका पसंदीदा काम कौन सा होगा?"
          : "Your school is having a big fun fair. 🎪 What is your favorite job?",
        MIDDLE: isHindi
          ? "आपकी कक्षा स्कूल प्रदर्शनी की तैयारी कर रही है। 🎨 आप कौन सी भूमिका चुनते हैं?"
          : "Your class is preparing a school exhibition. 🎨 What role do you choose?",
        SECONDARY: isHindi
          ? "आप एक सामुदायिक कार्यक्रम का आयोजन कर रहे हैं। 📣 आपकी क्या भूमिका है?"
          : "You are organizing a community event. 📣 What is your role?",
        SENIOR: isHindi
          ? "आप एक नया मार्केटिंग अभियान शुरू कर रहे हैं। 🚀 आपका मुख्य ध्यान कहाँ है?"
          : "You are launching a marketing campaign. 🚀 Where do you focus?"
      }[level],
      type: "choice",
      options: {
        PRIMARY: [
          { label: isHindi ? "सुंदर पोस्टर और बोर्ड पेंट करना" : "Painting the posters and signs", emoji: "🎨", domains: ["creative"] },
          { label: isHindi ? "दुकान लगाने में अपने दोस्तों की मदद करना" : "Helping friends set up their stalls", emoji: "🤝", domains: ["social"] },
          { label: isHindi ? "लोगों को खेलने के लिए जोर-जोर से बुलाना" : "Calling out to invite people to play", emoji: "🗣️", domains: ["language"] },
          { label: isHindi ? "लकड़ी से खेल के बूथ (stalls) बनाना" : "Building the game booths out of wood", emoji: "🔨", domains: ["spatial"] }
        ],
        MIDDLE: [
          { label: isHindi ? "प्रदर्शनी की सजावट और विजुअल लेआउट का निर्देश देना" : "Directing the visual layout and decorations", emoji: "🎨", domains: ["creative"] },
          { label: isHindi ? "छात्रों की समन्वय टीम (coordination team) का प्रबंधन करना" : "Managing the student coordination team", emoji: "🤝", domains: ["social"] },
          { label: isHindi ? "प्रोजेक्ट के बारे में लिखना और प्रस्तुति देना" : "Writing and presenting the explanations", emoji: "🗣️", domains: ["language"] },
          { label: isHindi ? "प्रदर्शनी स्टैंड और मॉडल का निर्माण करना" : "Constructing the display stands and models", emoji: "🔨", domains: ["spatial"] }
        ],
        SECONDARY: [
          { label: isHindi ? "प्रचार वीडियो और ग्राफिक डिजाइन तैयार करना" : "Creating the promotional videos and graphic designs", emoji: "🎨", domains: ["creative"] },
          { label: isHindi ? "स्वयंसेवक टीमों और उनके समय का प्रबंधन करना" : "Directing volunteer teams and schedules", emoji: "🤝", domains: ["social"] },
          { label: isHindi ? "प्रायोजकों (sponsors) से बात करना और मंच का संचालन करना" : "Speaking to sponsors and hosting the stage", emoji: "🗣️", domains: ["language"] },
          { label: isHindi ? "मुख्य मंच और उपकरणों की भौतिक व्यवस्था करना" : "Setting up the physical stage and equipment", emoji: "🔨", domains: ["spatial"] }
        ],
        SENIOR: [
          { label: isHindi ? "रचनात्मक ब्रांडिंग और डिजाइन भाषा का निर्देशन करना" : "Directing the creative branding and design language", emoji: "🎨", domains: ["creative"] },
          { label: isHindi ? "ग्राहक संबंधों और टीम के संचालन का प्रबंधन करना" : "Managing client relationships and team operations", emoji: "🤝", domains: ["social"] },
          { label: isHindi ? "संचार रणनीति तैयार करना और विज्ञापन लेखन (copywriting) करना" : "Drafting the communications strategy and copywriting", emoji: "🗣️", domains: ["language"] },
          { label: isHindi ? "भौतिक बूथ स्पेस या यूजर इंटरफेस लेआउट डिजाइन करना" : "Designing the physical booth space or user interface layout", emoji: "🔨", domains: ["spatial"] }
        ]
      }[level]
    }
  ];
}

export function getAdaptedDeepTasks(tasks, schoolYear, age, language) {
  const level = getComplexityLevel(schoolYear, age);
  if (level === "MIDDLE") return tasks; // Middle uses standard content directly

  const isHindi = language === "Hindi";

  // Let's define Primary adaptations for core tasks:
  const primaryOverrides = {
    logical_pattern_matrix: {
      title: { English: "The Magic Lock", Hindi: "जादू की संख्या" },
      prompt: {
        English: "Add numbers to open the lock. The bottom row has 3 and 5 (= 8). Next are 5 and 9 (= 14). What belongs at the top? (3+5=8, 5+9=14, 8+14=?)",
        Hindi: "ताला खोलने के लिए संख्याओं को जोड़ें। सबसे नीचे 3 और 5 हैं, जो 8 बनते हैं। 5 और 9 मिलकर 14 बनते हैं। सबसे ऊपर क्या आएगा? (3+5=8, 5+9=14, 8+14=?)"
      }
    },
    logical_riddle: {
      title: { English: "The Leg Code", Hindi: "पैरों का खेल" },
      prompt: {
        English: "A cat is 4, a spider is 8, and an ant is 6. What number represents a snake? 🐍",
        Hindi: "बिल्ली 4 है, मकड़ी 8 है, चींटी 6 है। सांप का नंबर क्या होगा? 🐍"
      }
    },
    spatial_rotation: {
      prompt: {
        English: "A star pointer turns: first UP ↑, then RIGHT →, then DOWN ↓. Where will it point next?",
        Hindi: "तारे की सुई घूमती है: पहले ऊपर इशारा करती है ↑, फिर दाएं →, फिर नीचे ↓। आगे कहाँ इशारा करेगी?"
      }
    },
    spatial_perspective: {
      title: { English: "Shadow Match", Hindi: "परछाई का खेल" },
      prompt: {
        English: "A T-shaped toy has light shining from the LEFT. What shape of shadow does it make on the wall?",
        Hindi: "एक 'T' आकार के खिलौने पर बाईं (LEFT) ओर से टॉर्च की रोशनी पड़ने पर दीवार पर कैसी छाया बनेगी?"
      }
    },
    creative_uses: {
      prompt: {
        English: "Imagine gravity pulls you SIDEWAYS at school instead of down! 😮 Write 3 funny things that would happen!",
        Hindi: "सोचें कि आपके स्कूल में गुरुत्वाकर्षण नीचे के बजाय बगल में काम करने लगे! 😮 3 मजेदार चीजें लिखें जो आपके साथ होंगी!"
      }
    },
    language_story_order: {
      title: { English: "Story Order", Hindi: "कहानी जमाएं" },
      prompt: {
        English: "Put these secret agent message pieces in the correct order to tell the exciting escape story!",
        Hindi: "इन वाक्यों को सही क्रम में लगाएं ताकि एक मजेदार भागने की कहानी बन सके!"
      }
    },
    language_analogy: {
      title: { English: "Word Connection", Hindi: "शब्दों का मेल" },
      prompt: {
        English: "Complete this word connection: A FEATHER is to a BIRD as a SCALE is to...?",
        Hindi: "शब्दों का संबंध पूरा करें: एक पंख (FEATHER) चिड़िया (BIRD) के लिए है, तो एक शल्क (SCALE) किसके लिए है...?"
      }
    },
    kinesthetic_motor_planning: {
      title: { English: "The Rope Bridge", Hindi: "रस्सी का पुल" },
      prompt: {
        English: "You are on a wobbling rope bridge. Strong wind blows from the right! What is the best way to balance?",
        Hindi: "आप एक हिलते हुए रस्सी के पुल पर हैं। दाईं ओर से तेज हवा चलती है! सुरक्षित रहने के लिए आप क्या करेंगे?"
      },
      options: [
        { label: { English: "Bend knees, spread arms, and lean slightly right", Hindi: "घुटनों को मोड़ें, हाथ फैलाएं और थोड़ा दाईं ओर झुकें" }, value: 4 },
        { label: { English: "Stand straight and close eyes", Hindi: "बिल्कुल सीधे खड़े रहें और आंखें बंद करें" }, value: 0 },
        { label: { English: "Run fast to the other side", Hindi: "जितनी तेजी से हो सके दूसरी तरफ दौड़ें" }, value: 1 },
        { label: { English: "Sit down and shout for help", Hindi: "रस्सी के पुल पर बैठ जाएं और मदद के लिए चिल्लाएं" }, value: 2 }
      ]
    },
    social_response: {
      title: { English: "Helping a Teammate", Hindi: "साथी की मदद" },
      prompt: {
        English: "10 minutes left for a group project. A friend is upset because their drawing was left out. What do you do?",
        Hindi: "प्रोजेक्ट जमा करने में 10 मिनट बचे हैं। एक दोस्त रो रहा है क्योंकि उसका चित्र भूल गए। बाकी जमा करना चाहते हैं। आप क्या करेंगे?"
      },
      options: [
        { label: { English: "Submit now and highlight their drawing later", Hindi: "प्रोजेक्ट जमा कर दें, फिर प्रेजेंटेशन में दोस्त के चित्र की बात करें" }, value: 4 },
        { label: { English: "Delay to add the drawing because friendship matters most", Hindi: "देर हो जाए तो भी चित्र चिपकाएं क्योंकि दोस्त की खुशी जरूरी है" }, value: 4 },
        { label: { English: "Tape the drawing to the back quickly to save time", Hindi: "चित्र को पोस्टर के पीछे चिपका दें ताकि समय बच सके" }, value: 4 },
        { label: { English: "Do nothing and let others decide", Hindi: "चुप रहें और दूसरों को फैसला करने दें" }, value: 1 }
      ]
    },
    social_conflict_resolution: {
      title: { English: "Playground Argument", Hindi: "मैदान का झगड़ा" },
      prompt: {
        English: "Two friends argue about a football goal. The game stops. How do you help them play again?",
        Hindi: "फुटबॉल मैच में दो दोस्त गोल को लेकर झगड़ रहे हैं। खेल रुक गया है। आप झगड़ा कैसे सुलझाएंगे?"
      },
      options: [
        { label: { English: "Flip a coin to decide and continue having fun", Hindi: "सिक्का उछालकर फैसला करें और खेल जारी रखें" }, value: 4 },
        { label: { English: "Shout louder than them to make them stop", Hindi: "उन दोनों से भी ज़्यादा ज़ोर से चिल्लाएँ ताकि वे चुप हो जाएँ" }, value: 0 },
        { label: { English: "Take the ball and walk home", Hindi: "फुटबॉल लेकर अपने घर चले जाएं" }, value: 1 },
        { label: { English: "Blame one friend to end it quickly", Hindi: "बहस को जल्दी खत्म करने के लिए तुरंत एक सहपाठी को दोषी ठहराएं" }, value: 0 }
      ]
    },
    naturalist_weather_pattern: {
      prompt: {
        English: "Cold wind blows, birds fly low, and the sky turns dark grey. What is nature telling you?",
        Hindi: "अचानक ठंडी हवा चलने लगती है, पक्षी नीचे उड़ते हैं और आसमान काला हो जाता है। प्रकृति क्या बता रही है?"
      },
      options: [
        { label: { English: "Heavy rain is coming soon", Hindi: "बहुत जल्द तेज बारिश होने वाली है" }, value: 4 },
        { label: { English: "The sun will shine brighter", Hindi: "सूरज और तेज चमकेगा" }, value: 0 },
        { label: { English: "An earthquake is coming", Hindi: "भूकंप आने वाला है" }, value: 0 },
        { label: { English: "A cold winter night has started", Hindi: "ठंड की रात शुरू हो गई है" }, value: 1 }
      ]
    },
    naturalist_wind_disperse: {
      title: { English: "Butterfly Garden", Hindi: "तितलियों का बगीचा" },
      prompt: {
        English: "You want to attract butterflies to your garden. What is the best thing to do?",
        Hindi: "आप अपने बगीचे में सुंदर तितलियों को बुलाना चाहते हैं। कौन सा काम सबसे अच्छा होगा?"
      },
      options: [
        { label: { English: "Plant sweet flowers and keep water nearby", Hindi: "मीठे फूलों के पौधे लगाएं और उथले बर्तन में पानी रखें" }, value: 4 },
        { label: { English: "Spray insect spray", Hindi: "पौधों से दूसरे कीड़ों को दूर रखने के लिए तेज़ कीटनाशक का छिड़काव करें" }, value: 0 },
        { label: { English: "Cover flowers with plastic bags", Hindi: "सभी फूलों को प्लास्टिक की शीट से ढक दें" }, value: 0 },
        { label: { English: "Catch butterflies elsewhere and release them", Hindi: "दूसरे पार्कों से तितलियों को पकड़ें और उन्हें अपने बगीचे में छोड़ दें" }, value: 1 }
      ]
    },
    intrapersonal_reflection: {
      title: { English: "Hard Work", Hindi: "कठिन काम" },
      prompt: {
        English: "When something is hard, do you tell yourself you can do it with practice?",
        Hindi: "जब आप किसी बहुत कठिन चुनौती का सामना करते हैं, तो क्या आप खुद से कहते हैं कि अभ्यास करने से आप इसमें बेहतर हो सकते हैं?"
      },
      low: { English: "No, I get discouraged", Hindi: "नहीं, मैं हिम्मत हार जाता हूँ" },
      high: { English: "Yes, I love to learn!", Hindi: "हाँ, मुझे सीखना पसंद है!" }
    },
    intrapersonal_frustration: {
      title: { English: "The Stuck Kite", Hindi: "फंसी पतंग" },
      prompt: {
        English: "Your handmade kite gets stuck in a tree. You cannot reach it. What do you do?",
        Hindi: "आपकी बनाई पतंग पेड़ पर फंस गई है। आप वहां तक नहीं पहुंच सकते। आप क्या करेंगे?"
      },
      options: [
        { label: { English: "Accept it and design a new, better kite", Hindi: "मान लें कि वह गई, और नई पतंग बनाने की सोचें" }, value: 4 },
        { label: { English: "Find a long stick to try to get it down", Hindi: "एक लंबा डंडा ढूंढकर उसे निकालने की कोशिश करें" }, value: 4 },
        { label: { English: "Ask friends for ideas to build a hook tool", Hindi: "दोस्तों से कहें कि धागा खींचने की मशीन बनाएं" }, value: 4 },
        { label: { English: "Go home angry and give up entirely", Hindi: "गुस्सा होकर घर चले जाएं और पतंग उड़ाना छोड़ दें" }, value: 1 }
      ]
    },
    deep_discovery_flow: {
      prompt: {
        English: "Tell us about a game or drawing that makes you forget about lunchtime! 🎨 What are you doing and why is it so much fun?",
        Hindi: "हमें किसी ऐसे खेल या चित्रकारी के बारे में बताएं जिसमें आप दोपहर के खाने का समय भी भूल जाते हैं! 🎨 आप क्या कर रहे होते हैं और यह इतना मजेदार क्यों है?"
      }
    },
    deep_discovery_pride: {
      prompt: {
        English: "What is one thing you built or made that you love showing to everyone? 🌟 Describe what you did.",
        Hindi: "आपने कौन सी एक ऐसी चीज़ बनाई है जो आप सबको दिखाना चाहते हैं? 🌟 बताएं कि आपने उसे कैसे बनाया।"
      }
    },
    deep_discovery_curiosity: {
      prompt: {
        English: "If you could spend a whole day learning anything you want (like magic, space, or building robots), what would it be?",
        Hindi: "यदि आप अपनी पसंद की कोई भी चीज़ सीखने (जैसे जादू, अंतरिक्ष, या रोबोट बनाना) में एक पूरा दिन बिता सकते हैं, तो आप क्या चुनेंगे?"
      }
    },
    deep_discovery_vision: {
      prompt: {
        English: "If you had a magic wand to fix one big problem in your school or village, what would you fix first?",
        Hindi: "यदि आपके पास अपने स्कूल या गाँव की किसी एक बड़ी समस्या को ठीक करने के लिए एक जादुई छड़ी हो, तो आप पहले क्या ठीक करेंगे?"
      }
    }
  };

  // Secondary & Senior adaptations (elevating language and scenario complexity):
  const advancedOverrides = {
    logical_pattern_matrix: {
      title: { English: "The Numerical Matrix Crypt", Hindi: "संख्यात्मक मैट्रिक्स" },
      prompt: {
        English: "Analyze the sequence hierarchy in a numerical matrix where base inputs of 3 and 5 sum to 8, adjacent inputs 5 and 9 sum to 14, and mid-tier outputs sum to the apex. Calculate the missing value at the apex of the structure. (3 + 5 = 8; 5 + 9 = 14; 8 + 14 = ?)",
        Hindi: "संख्यात्मक मैट्रिक्स में अनुक्रम पदानुक्रम का विश्लेषण करें जहां 3 और 5 का योग 8 है, 5 और 9 का योग 14 है, और मध्य-स्तरीय योग शीर्ष की ओर बढ़ते हैं। शीर्ष पर अज्ञात मान की गणना करें। (3 + 5 = 8; 5 + 9 = 14; 8 + 14 = ?)"
      }
    },
    logical_riddle: {
      title: { English: "The Taxonomic Leg-Count Cipher", Hindi: "वर्गीकरण कोड" },
      prompt: {
        English: "An abstract cipher maps biological entities to indices based on their appendages: Feline represents 4, Arachnid represents 8, Formicidae represents 6. Determine the numerical value mapping to Serpentes.",
        Hindi: "एक अमूर्त सिफर जीवों को उनके अंगों के आधार पर अनुक्रमित करता है: बिल्ली (Feline) 4 को दर्शाती है, मकड़ी (Arachnid) 8 को, और चींटी (Formicidae) 6 को। सर्प (Serpentes) के लिए सही संख्या निर्धारित करें।"
      }
    },
    spatial_rotation: {
      prompt: {
        English: "A vector indicator on a coordinate system rotates sequentially: pointing 90 degrees (North), 0 degrees (East), then 270 degrees (South). Compute the next heading in the cycle.",
        Hindi: "एक समन्वय प्रणाली (coordinate system) में एक वेक्टर संकेतक क्रमिक रूप से घूमता है: पहले 90 डिग्री (उत्तर), फिर 0 डिग्री (पूर्व), और फिर 270 डिग्री (दक्षिण)। चक्र में अगले हेडिंग की गणना करें।"
      }
    },
    spatial_perspective: {
      title: { English: "Orthographic Projection Shadow", Hindi: "ऑर्थोग्राफिक प्रोजेक्शन शैडो" },
      prompt: {
        English: "A three-dimensional planar T-shaped structure is cast under a light source from the direct lateral left axis. What two-dimensional orthographic silhouette is projected onto the wall?",
        Hindi: "एक त्रि-आयामी (3D) समतलीय T-आकार की संरचना को बाईं ओर (lateral left) से प्रकाश स्रोत के नीचे रखा गया है। दीवार पर कौन सी द्वि-आयामी (2D) ऑर्थोग्राफिक परछाई दिखाई देगी?"
      }
    },
    creative_uses: {
      prompt: {
        English: "Hypothesize a scenario where gravity shifts to operate along the horizontal lateral axis rather than the vertical pull. Propose 3 distinct, highly divergent consequences of this physical anomaly on daily routines.",
        Hindi: "एक ऐसी स्थिति की परिकल्पना करें जहां गुरुत्वाकर्षण ऊर्ध्वाधर (vertical) खिंचाव के बजाय क्षैतिज (horizontal lateral) अक्ष पर काम करना शुरू कर देता है। दैनिक जीवन पर इस भौतिक विसंगति के 3 बिल्कुल अलग परिणामों का प्रस्ताव दें।"
      }
    },
    language_story_order: {
      title: { English: "Narrative Reconstruction Sequence", Hindi: "कथा पुनर्निर्माण क्रम" },
      prompt: {
        English: "Reconstruct the chronological order of these compound narrative segments to establish a coherent, logically flowing adventure sequence.",
        Hindi: "एक सुसंगत और तार्किक कहानी स्थापित करने के लिए इन मिश्रित कथा खंडों के कालानुक्रमिक (chronological) क्रम को पुनर्गठित करें।"
      }
    },
    language_analogy: {
      title: { English: "Semantic Analogy Bridge", Hindi: "सिमेंटिक सादृश्य पुल" },
      prompt: {
        English: "Determine the semantic correlation to complete the analogical bridge: FEATHER is to BIRD as SCALE is to...?",
        Hindi: "सादृश्य संबंध को पूरा करने के लिए सही अर्थपूर्ण शब्द का चयन करें: पंख (FEATHER) का जो संबंध पक्षी (BIRD) से है, वही शल्क (SCALE) का किससे है...?"
      }
    },
    kinesthetic_motor_planning: {
      title: { English: "Biomechanical Stabilization", Hindi: "बायोमैकेनिकल स्थिरता" },
      prompt: {
        English: "While traversing an unstable, high rope bridge, you encounter a sudden, high-velocity wind force from the right lateral axis. What physical stabilization strategy best maintains equilibrium?",
        Hindi: "एक अस्थिर, ऊंचे रस्सी के पुल को पार करते समय, आपको दाईं ओर से अचानक तेज गति से हवा के झोंके का सामना करना पड़ता है। संतुलन बनाए रखने के लिए सबसे प्रभावी शारीरिक स्थिरीकरण (stabilization) रणनीति क्या है?"
      },
      options: [
        { label: { English: "Lower your center of gravity by flexing knees, extend arms for counterbalance, and lean slightly into the wind", Hindi: "घुटनों को मोड़कर अपने गुरुत्वाकर्षण केंद्र को कम करें, संतुलन के लिए हाथ फैलाएं, और थोड़ा दाईं ओर (हवा की तरफ) झुकें" }, value: 4 },
        { label: { English: "Align body posture fully vertical, close eyes, and stiffen muscle groups", Hindi: "शरीर की मुद्रा को पूरी तरह से सीधा संरेखित करें, आंखें बंद करें और अपनी मांसपेशियों को कड़ा करें" }, value: 0 },
        { label: { English: "Increase linear velocity to minimize exposure time on the bridge", Hindi: "पुल पर समय कम करने के लिए जितनी जल्दी हो सके दौड़ें" }, value: 1 },
        { label: { English: "Decline posture to seated, minimizing wind profile, and signal for external assistance", Hindi: "हवा के प्रभाव को कम करने के लिए पुल पर बैठ जाएं और बाहरी सहायता का संकेत दें" }, value: 2 }
      ]
    },
    social_response: {
      title: { English: "Collaborative Milestone Conflict", Hindi: "सहयोगात्मक कार्य संघर्ष" },
      prompt: {
        English: "Your team faces an imminent 10-minute project submission deadline. The display is functional, but a teammate is distressed because their contributions were omitted. Other members insist on immediate submission. How do you resolve this?",
        Hindi: "आपकी टीम के पास प्रोजेक्ट जमा करने के लिए केवल 10 मिनट बचे हैं। प्रोजेक्ट तैयार है, लेकिन एक टीम का सदस्य परेशान है क्योंकि उसका काम शामिल नहीं किया गया है। अन्य सदस्य तुरंत जमा करने पर जोर दे रहे हैं। आप इसे कैसे हल करेंगे?"
      },
      options: [
        { label: { English: "Submit immediately to secure victory, promising to emphasize their role during the oral presentation", Hindi: "जीत सुनिश्चित करने के लिए तुरंत जमा करें, और मौखिक प्रस्तुति के दौरान उनकी भूमिका पर प्रकाश डालने का वादा करें" }, value: 4 },
        { label: { English: "Delay submission to integrate their contribution, prioritizing group cohesion over strict adherence to deadlines", Hindi: "उनके योगदान को शामिल करने के लिए जमा करने में देरी करें, समय सीमा के बजाय समूह एकता को प्राथमिकता दें" }, value: 4 },
        { label: { English: "Execute a rapid compromise, attaching the drawing to the reverse side as a visual appendix to satisfy both interests", Hindi: "एक त्वरित समझौता खोजें, चित्र को पोस्टर के पीछे 'परिशिष्ट' (Appendix) के रूप में चिपका दें ताकि समय बच सके" }, value: 4 },
        { label: { English: "Maintain neutrality and defer the final decision to the collective group vote", Hindi: "तटस्थ रहें और अंतिम निर्णय को सामूहिक समूह वोट पर छोड़ दें" }, value: 1 }
      ]
    },
    social_conflict_resolution: {
      title: { English: "Peer Dispute Resolution", Hindi: "सहकर्मी विवाद समाधान" },
      prompt: {
        English: "During a competitive activity, an intense dispute arises between two peers regarding whether a scoring event occurred. Tensions escalate and progress halts. How do you intervene?",
        Hindi: "एक प्रतिस्पर्धी गतिविधि के दौरान, दो सहपाठियों के बीच स्कोरिंग को लेकर तीव्र विवाद उत्पन्न हो जाता है। तनाव बढ़ता है और खेल रुक जाता है। आप कैसे हस्तक्षेप करेंगे?"
      },
      options: [
        { label: { English: "Implement a randomized determination (e.g. coin flip) to restore activity, emphasizing that mutual enjoyment supersedes the score", Hindi: "गतिविधि को फिर से शुरू करने के लिए एक यादृच्छिक तरीका (जैसे सिक्का उछालना) अपनाएं, और याद दिलाएं कि आपसी मज़ा जीत से बड़ा है" }, value: 4 },
        { label: { English: "Raise your vocal volume to command attention and demand compliance", Hindi: "उनका ध्यान आकर्षित करने के लिए अपनी आवाज़ उठाएं और शांत होने की मांग करें" }, value: 0 },
        { label: { English: "Withdraw from the group and remove the central equipment to end the activity", Hindi: "गतिविधि को समाप्त करने के लिए समूह से हट जाएं और खेल का मुख्य सामान अपने साथ ले जाएं" }, value: 1 },
        { label: { English: "Assign fault immediately to one individual to expedite resolution", Hindi: "विवाद को जल्दी सुलझाने के लिए तुरंत एक व्यक्ति को दोषी ठहराएं" }, value: 0 }
      ]
    },
    naturalist_weather_pattern: {
      prompt: {
        English: "You observe a sudden decrease in air temperature, low-altitude avian flight paths, and dense cumulonimbus cloud formations. What meteorological transition is indicated?",
        Hindi: "आप हवा के तापमान में अचानक गिरावट, पक्षियों की कम ऊंचाई पर उड़ान, और आसमान में घने बादलों के निर्माण को देखते हैं। यह कौन सा मौसमी परिवर्तन दर्शाता है?"
      },
      options: [
        { label: { English: "An imminent heavy precipitation event", Hindi: "बहुत जल्द होने वाली भारी वर्षा (precipitation)" }, value: 4 },
        { label: { English: "Increased solar radiation and clearing conditions", Hindi: "सौर विकिरण में वृद्धि और मौसम का साफ होना" }, value: 0 },
        { label: { English: "Seismic instability", Hindi: "भूकंपीय अस्थिरता" }, value: 0 },
        { label: { English: "Onset of a cold anticyclonic front", Hindi: "शीत हवा के फ्रंट (cold anticyclonic front) की शुरुआत" }, value: 1 }
      ]
    },
    naturalist_wind_disperse: {
      title: { English: "Ecological Restoration", Hindi: "पारिस्थितिकी बहाली" },
      prompt: {
        English: "You intend to optimize the local insect population in a micro-habitat. Which ecological intervention will support native lepidoptera (butterflies) the most?",
        Hindi: "आप एक छोटे बगीचे में स्थानीय कीटों की आबादी बढ़ाना चाहते हैं। कौन सा उपाय स्थानीय तितलियों (lepidoptera) की सबसे अधिक मदद करेगा?"
      },
      options: [
        { label: { English: "Cultivate native nectar-producing angiosperms and provide accessible hydration stations", Hindi: "मीठे मकरंद वाले चमकदार स्थानीय फूलों के पौधे लगाएं और पास में उथले बर्तनों में ताजा पानी रखें" }, value: 4 },
        { label: { English: "Apply synthetic chemical insecticides to eliminate competing arthropods", Hindi: "प्रतिस्पर्धी कीड़ों को समाप्त करने के लिए रासायनिक कीटनाशकों का छिड़काव करें" }, value: 0 },
        { label: { English: "Enclose the flora fully in protective polyethylene sheets to prevent contamination", Hindi: "प्रदूषण से बचाने के लिए पौधों को पूरी तरह से पॉलीथीन शीट से ढक दें" }, value: 0 },
        { label: { English: "Introduce non-native species captured from distant ecosystems", Hindi: "दूर के पारिस्थितिकी तंत्र (ecosystems) से पकड़ी गई गैर-स्थानीय प्रजातियों को शामिल करें" }, value: 1 }
      ]
    },
    intrapersonal_reflection: {
      title: { English: "Cognitive Agility & Growth", Hindi: "संज्ञानात्मक विकास" },
      prompt: {
        English: "When confronted with highly challenging cognitive tasks, do you maintain that your abilities in this domain are malleable and improve with systematic effort?",
        Hindi: "जब आपका सामना किसी कठिन चुनौती से होता है, तो क्या आप मानते हैं कि अभ्यास और योजनाबद्ध प्रयास के माध्यम से आपकी क्षमताएं विकसित हो सकती हैं?"
      },
      low: { English: "No, I believe my capacity is fixed and feel discouraged", Hindi: "नहीं, मेरा मानना है कि मेरी क्षमताएं निश्चित हैं और मैं हतोत्साहित महसूस करता हूँ" },
      high: { English: "Yes, I view challenges as opportunities for skill acquisition", Hindi: "हाँ, मैं चुनौतियों को नए कौशल सीखने के अवसर के रूप में देखता हूँ" }
    },
    intrapersonal_frustration: {
      title: { English: "Resilience Strategy", Hindi: "लचीलापन रणनीति" },
      prompt: {
        English: "You spent significant effort constructing a complex device, but on its initial test it becomes trapped in an inaccessible location. How do you respond?",
        Hindi: "आपने एक जटिल उपकरण के निर्माण में काफी समय बिताया, लेकिन परीक्षण के दौरान वह एक दुर्गम स्थान पर फंस गया। आपकी प्रतिक्रिया क्या होगी?"
      },
      options: [
        { label: { English: "Acknowledge the loss, analyze the design failures, and initiate construction of an optimized version", Hindi: "नुकसान को स्वीकार करें, डिजाइन की विफलताओं का विश्लेषण करें और एक बेहतर संस्करण का निर्माण शुरू करें" }, value: 4 },
        { label: { English: "Acquire specialized tools to attempt recovery, accepting the risk of physical damage to the device", Hindi: "उपकरण को निकालने के लिए विशेष उपकरणों की व्यवस्था करें, भले ही इसमें समय लगे और उपकरण क्षतिग्रस्त हो" }, value: 4 },
        { label: { English: "Collaborate with peers to engineer a mechanical extraction or pulley apparatus", Hindi: "उपकरण को निकालने के लिए एक सरल यांत्रिक चरखी (pulley) बनाने के लिए दोस्तों से चर्चा करें" }, value: 4 },
        { label: { English: "Abandon the project, experiencing frustration, and cease activities in this domain", Hindi: "क्रोधित होकर परियोजना को छोड़ दें और इस क्षेत्र में काम करना पूरी तरह बंद कर दें" }, value: 1 }
      ]
    },
    deep_discovery_flow: {
      prompt: {
        English: "Tell us about a complex project, design, or research activity that engages you so deeply that you completely lose track of time. Describe your operational focus.",
        Hindi: "हमें किसी ऐसे जटिल प्रोजेक्ट, डिजाइन, या शोध गतिविधि के बारे में बताएं जिसमें आप समय का ध्यान भूल जाते हैं। अपनी परिचालन एकाग्रता (operational focus) का वर्णन करें।"
      }
    },
    deep_discovery_pride: {
      prompt: {
        English: "Describe a complex creation, engineered solution, or milestone achievement that you are proud of. What specific problems did you solve?",
        Hindi: "अपनी किसी ऐसी जटिल रचना, इंजीनियरिंग समाधान या महत्वपूर्ण उपलब्धि का वर्णन करें जिस पर आपको गर्व है। आपने किन विशिष्ट समस्याओं का समाधान किया?"
      }
    },
    deep_discovery_curiosity: {
      prompt: {
        English: "If you could spend one year investigating a single scientific field, technology, or creative domain without academic constraints, what would it be and why?",
        Hindi: "यदि आप बिना किसी शैक्षणिक प्रतिबंध के एक पूरा वर्ष किसी एकल वैज्ञानिक क्षेत्र, तकनीक या रचनात्मक डोमेन की जांच करने में बिता सकते हैं, तो वह क्या होगा और क्यों?"
      }
    },
    deep_discovery_vision: {
      prompt: {
        English: "Identify a systemic challenge in your community, school, or industry. If you were granted resources, how would you design and implement a solution?",
        Hindi: "अपने स्कूल, समुदाय या उद्योग में एक प्रणालीगत चुनौती (systemic challenge) की पहचान करें। यदि आपको संसाधन दिए जाएं, तो आप समाधान कैसे तैयार और लागू करेंगे?"
      }
    }
  };

  const overrides = level === "PRIMARY" ? primaryOverrides : advancedOverrides;

  return tasks.map(task => {
    const override = overrides[task.key];
    if (!override) return task;

    const updated = { ...task };
    if (override.title) {
      updated.title = isHindi ? override.title.Hindi : override.title.English;
    }
    if (override.prompt) {
      updated.prompt = isHindi ? override.prompt.Hindi : override.prompt.English;
    }
    if (override.low) {
      updated.low = isHindi ? override.low.Hindi : override.low.English;
    }
    if (override.high) {
      updated.high = isHindi ? override.high.Hindi : override.high.English;
    }
    if (override.options && Array.isArray(updated.options)) {
      updated.options = updated.options.map((opt, idx) => {
        const oOverride = override.options[idx];
        if (!oOverride) return opt;
        return {
          ...opt,
          label: isHindi ? oOverride.label.Hindi : oOverride.label.English
        };
      });
    }
    return updated;
  });
}


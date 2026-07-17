import os
import json

def generate_bank():
    print("Generating GOAT V5 assessment bank...")
    bank = []

    # 1. DISCOVERY QUESTIONS (8 total, 1 per domain)
    # Options map to multiple domains simultaneously.
    discovery_questions = [
        {
            "key": "q_discovery_1",
            "type": "choice",
            "domain": "language",
            "component": "discovery",
            "title": {"English": "Free Afternoon", "Hindi": "खाली दोपहर"},
            "prompt": {
                "English": "You get one free afternoon. What sounds most fun?",
                "Hindi": "तुम्हें एक खाली दोपहर मिलती है। तुम सबसे ज़्यादा क्या करना चाहोगे?"
            },
            "options": [
                {"label": {"English": "Tell or write a story", "Hindi": "कहानी सुनाना या लिखना"}, "value": 0, "domains": ["language", "creative"]},
                {"label": {"English": "Solve a tricky puzzle", "Hindi": "एक कठिन पहेली हल करना"}, "value": 1, "domains": ["logical", "spatial"]},
                {"label": {"English": "Organize a group game", "Hindi": "एक सामूहिक खेल का आयोजन करना"}, "value": 2, "domains": ["social", "language"]},
                {"label": {"English": "Plan a personal goal", "Hindi": "एक व्यक्तिगत लक्ष्य की योजना बनाना"}, "value": 3, "domains": ["intrapersonal"]}
            ],
            "metric": "preference",
            "difficulty": "easy",
            "ai_interpretation_notes": "Measures initial interest leaning across language, creative, logical, spatial, social, and intrapersonal domains."
        },
        {
            "key": "q_discovery_2",
            "type": "choice",
            "domain": "creative",
            "component": "discovery",
            "title": {"English": "Box of Cardboard", "Hindi": "गत्ते का डिब्बा"},
            "prompt": {
                "English": "You receive a box of cardboard and sticks. What do you do?",
                "Hindi": "आपको गत्ते का एक डिब्बा और लकड़ियाँ मिलती हैं। आप क्या करेंगे?"
            },
            "options": [
                {"label": {"English": "Design an artistic toy castle", "Hindi": "एक कलात्मक खिलौना किला बनाना"}, "value": 0, "domains": ["creative", "spatial"]},
                {"label": {"English": "Build a model bridge", "Hindi": "एक मॉडल पुल का निर्माण करना"}, "value": 1, "domains": ["spatial", "logical"]},
                {"label": {"English": "Invite friends to build together", "Hindi": "दोस्तों को मिलकर बनाने के लिए बुलाना"}, "value": 2, "domains": ["social", "language"]},
                {"label": {"English": "Inspect the materials quietly", "Hindi": "सामग्री का शांति से निरीक्षण करना"}, "value": 3, "domains": ["intrapersonal"]}
            ],
            "metric": "preference",
            "difficulty": "easy",
            "ai_interpretation_notes": "Measures creative, spatial, logical, social, and intrapersonal preferences."
        },
        {
            "key": "q_discovery_3",
            "type": "choice",
            "domain": "logical",
            "component": "discovery",
            "title": {"English": "Strange Lights", "Hindi": "अजीब रोशनी"},
            "prompt": {
                "English": "You see a strange pattern of lights on a building. What do you do?",
                "Hindi": "आप किसी इमारत पर रोशनी का एक अजीब पैटर्न देखते हैं। आप क्या करेंगे?"
            },
            "options": [
                {"label": {"English": "Try to figure out the code", "Hindi": "कोड का पता लगाने की कोशिश करना"}, "value": 0, "domains": ["logical", "spatial"]},
                {"label": {"English": "Draw the pattern in a notebook", "Hindi": "नोटबुक में पैटर्न बनाना"}, "value": 1, "domains": ["creative", "spatial"]},
                {"label": {"English": "Explain it to a friend", "Hindi": "एक दोस्त को इसे समझाना"}, "value": 2, "domains": ["language", "social"]},
                {"label": {"English": "Sit and watch it quietly", "Hindi": " बैठकर चुपचाप इसे देखना"}, "value": 3, "domains": ["intrapersonal"]}
            ],
            "metric": "preference",
            "difficulty": "easy",
            "ai_interpretation_notes": "Measures logical, spatial, creative, language, social, and intrapersonal preferences."
        },
        {
            "key": "q_discovery_4",
            "type": "choice",
            "domain": "spatial",
            "component": "discovery",
            "title": {"English": "Playground Game", "Hindi": "मैदान का खेल"},
            "prompt": {
                "English": "If you could design a new playground game, what would it look like?",
                "Hindi": "यदि आप खेल के मैदान के लिए एक नया खेल बना सकें, तो वह कैसा दिखेगा?"
            },
            "options": [
                {"label": {"English": "A maze with hidden routes", "Hindi": "छिपे हुए रास्तों वाली भूलभुलैया"}, "value": 0, "domains": ["spatial", "logical"]},
                {"label": {"English": "A physical obstacle course", "Hindi": "एक शारीरिक बाधा दौड़ का रास्ता"}, "value": 1, "domains": ["kinesthetic", "spatial"]},
                {"label": {"English": "A team game with roles", "Hindi": "अलग-अलग भूमिकाओं वाला टीम खेल"}, "value": 2, "domains": ["social", "language"]},
                {"label": {"English": "A puzzle game for one person", "Hindi": "एक व्यक्ति के लिए एक पहेली खेल"}, "value": 3, "domains": ["intrapersonal"]}
            ],
            "metric": "preference",
            "difficulty": "easy",
            "ai_interpretation_notes": "Measures spatial, logical, kinesthetic, social, language, and intrapersonal preferences."
        },
        {
            "key": "q_discovery_5",
            "type": "choice",
            "domain": "kinesthetic",
            "component": "discovery",
            "title": {"English": "Fast Drumbeat", "Hindi": "तेज़ ढोल"},
            "prompt": {
                "English": "You hear a fast drumbeat. What is your reaction?",
                "Hindi": "आप एक तेज़ ढोल की आवाज़ सुनते हैं। आपकी क्या प्रतिक्रिया होगी?"
            },
            "options": [
                {"label": {"English": "Dance or clap to the rhythm", "Hindi": "ताल पर नाचना या ताली बजाना"}, "value": 0, "domains": ["kinesthetic", "creative"]},
                {"label": {"English": "Listen to the pattern of beats", "Hindi": "धड़कनों के पैटर्न को ध्यान से सुनना"}, "value": 1, "domains": ["logical", "naturalist"]},
                {"label": {"English": "Call friends to join in", "Hindi": "दोस्तों को शामिल होने के लिए बुलाना"}, "value": 2, "domains": ["social", "language"]},
                {"label": {"English": "Close eyes and feel the music", "Hindi": "आँखें बंद करके संगीत को महसूस करना"}, "value": 3, "domains": ["intrapersonal"]}
            ],
            "metric": "preference",
            "difficulty": "easy",
            "ai_interpretation_notes": "Measures kinesthetic, creative, logical, naturalist, social, language, and intrapersonal preferences."
        },
        {
            "key": "q_discovery_6",
            "type": "choice",
            "domain": "naturalist",
            "component": "discovery",
            "title": {"English": "Sick Plant", "Hindi": "बीमार पौधा"},
            "prompt": {
                "English": "You find a sick plant in the garden. What do you do?",
                "Hindi": "आपको बगीचे में एक बीमार पौधा मिलता है। आप क्या करेंगे?"
            },
            "options": [
                {"label": {"English": "Inspect leaves and add soil", "Hindi": "पत्तियों की जाँच करना और मिट्टी डालना"}, "value": 0, "domains": ["naturalist", "logical"]},
                {"label": {"English": "Draw the leaves in a diary", "Hindi": "एक डायरी में पत्तियों का चित्र बनाना"}, "value": 1, "domains": ["creative", "naturalist"]},
                {"label": {"English": "Ask a teacher to help solve it", "Hindi": "शिक्षक से इसे सुलझाने में मदद माँगना"}, "value": 2, "domains": ["language", "social"]},
                {"label": {"English": "Quietly wonder how it grows", "Hindi": "चुपचाप सोचना कि यह कैसे बढ़ता है"}, "value": 3, "domains": ["intrapersonal"]}
            ],
            "metric": "preference",
            "difficulty": "easy",
            "ai_interpretation_notes": "Measures naturalist, logical, creative, language, social, and intrapersonal preferences."
        },
        {
            "key": "q_discovery_7",
            "type": "choice",
            "domain": "social",
            "component": "discovery",
            "title": {"English": "Lonely Classmate", "Hindi": "अकेला सहपाठी"},
            "prompt": {
                "English": "A classmate is feeling lonely at lunch break. What do you do?",
                "Hindi": "मध्याह्न भोजन (लंच ब्रेक) में एक सहपाठी अकेला महसूस कर रहा है। आप क्या करेंगे?"
            },
            "options": [
                {"label": {"English": "Go sit, talk, and tell jokes", "Hindi": "जाकर बैठना, बात करना और चुटकुले सुनाना"}, "value": 0, "domains": ["language", "social"]},
                {"label": {"English": "Invite them to a sports game", "Hindi": "उन्हें एक खेल खेलने के लिए आमंत्रित करना"}, "value": 1, "domains": ["kinesthetic", "social"]},
                {"label": {"English": "Think about how they feel", "Hindi": "सोचना कि वे कैसा महसूस कर रहे हैं"}, "value": 2, "domains": ["intrapersonal"]},
                {"label": {"English": "Invent a two-person game", "Hindi": "दो लोगों के खेलने का एक खेल बनाना"}, "value": 3, "domains": ["creative", "social"]}
            ],
            "metric": "preference",
            "difficulty": "easy",
            "ai_interpretation_notes": "Measures language, social, kinesthetic, intrapersonal, and creative preferences."
        },
        {
            "key": "q_discovery_8",
            "type": "choice",
            "domain": "intrapersonal",
            "component": "discovery",
            "title": {"English": "Mistake Made", "Hindi": "गलती होने पर"},
            "prompt": {
                "English": "When you make a mistake in a drawing or project, what do you do?",
                "Hindi": "जब आप किसी चित्र या प्रोजेक्ट में कोई गलती करते हैं, तो आप क्या करते हैं?"
            },
            "options": [
                {"label": {"English": "Calm down and plan how to fix it", "Hindi": "शांत होना और इसे ठीक करने की योजना बनाना"}, "value": 0, "domains": ["intrapersonal", "logical"]},
                {"label": {"English": "Start over with a completely new idea", "Hindi": "एक नए विचार के साथ फिर से शुरुआत करना"}, "value": 1, "domains": ["creative"]},
                {"label": {"English": "Ask a friend for advice", "Hindi": "किसी दोस्त से सलाह माँगना"}, "value": 2, "domains": ["social", "language"]},
                {"label": {"English": "Throw it away and walk outside", "Hindi": "इसे फेंक देना और बाहर टहलने चले जाना"}, "value": 3, "domains": ["kinesthetic"]}
            ],
            "metric": "preference",
            "difficulty": "easy",
            "ai_interpretation_notes": "Measures intrapersonal, logical, creative, social, language, and kinesthetic preferences."
        },
        {
            "key": "q_discovery_9",
            "type": "choice",
            "domain": "kinesthetic",
            "component": "discovery",
            "title": {"English": "Teaching a New Skill", "Hindi": "नया कौशल सिखाना"},
            "prompt": {
                "English": "Your cousin has never played cricket before. They ask you how to bowl correctly. What do you do first?",
                "Hindi": "आपका चचेरा भाई कभी क्रिकेट नहीं खेला है। वह आपसे पूछता है कि गेंद सही तरह से कैसे फेंकें। आप सबसे पहले क्या करते हैं?"
            },
            "options": [
                {"label": {"English": "Pick up the ball and show them by bowling yourself", "Hindi": "गेंद उठाओ और खुद गेंद फेंककर दिखाओ"}, "value": 0, "domains": ["kinesthetic"]},
                {"label": {"English": "Draw the grip position and foot placement on paper", "Hindi": "कागज पर हाथ की पकड़ और पैरों की जगह का चित्र बनाओ"}, "value": 1, "domains": ["spatial", "logical"]},
                {"label": {"English": "Tell them the rules and explain what mistakes to avoid", "Hindi": "नियम बताओ और बताओ कि कौन सी गलतियाँ न करें"}, "value": 2, "domains": ["language", "logical"]},
                {"label": {"English": "Ask them to watch a video and figure it out themselves", "Hindi": "उनसे कहो कि वीडियो देखें और खुद समझें"}, "value": 3, "domains": ["intrapersonal"]}
            ],
            "metric": "preference",
            "difficulty": "easy",
            "ai_interpretation_notes": "Reveals whether the child's first instinct is physical demonstration — a strong marker of kinesthetic intelligence. Option 0 is diagnostic (not obviously the 'best' answer), making it resistant to social desirability bias."
        },
        {
            "key": "q_discovery_10",
            "type": "choice",
            "domain": "kinesthetic",
            "component": "discovery",
            "title": {"English": "The Stuck Kite", "Hindi": "फंसी हुई पतंग"},
            "prompt": {
                "English": "Your favourite kite gets stuck high in a neem tree. No adult is around. What is your first move?",
                "Hindi": "आपकी पसंदीदा पतंग ऊंचे नीम के पेड़ में फंस जाती है। आस-पास कोई बड़ा नहीं है। आप सबसे पहले क्या करेंगे?"
            },
            "options": [
                {"label": {"English": "Start climbing the tree or look for a long stick to reach it", "Hindi": "पेड़ पर चढ़ने की कोशिश करो या लंबी छड़ी खोजो"}, "value": 0, "domains": ["kinesthetic"]},
                {"label": {"English": "Figure out the angle of the string and tug it in a specific direction", "Hindi": "धागे का कोण समझो और उसे एक खास दिशा में खींचो"}, "value": 1, "domains": ["logical", "spatial"]},
                {"label": {"English": "Call out to friends nearby to help you plan a solution together", "Hindi": "पास के दोस्तों को बुलाओ और मिलकर हल सोचो"}, "value": 2, "domains": ["social"]},
                {"label": {"English": "Leave it and accept that the kite is gone, then go build a new one", "Hindi": "इसे छोड़ दो और मान लो पतंग गई, फिर नई पतंग बनाओ"}, "value": 3, "domains": ["intrapersonal", "creative"]}
            ],
            "metric": "preference",
            "difficulty": "easy",
            "ai_interpretation_notes": "The kinesthetic child's reflex is to physically engage with the problem (climb, reach, act). The scenario is culturally grounded and the options are genuinely distinct — no single answer reads as obviously correct to a child."
        }
    ]

    # Add Discovery Questions to bank
    for q in discovery_questions:
        bank.append(q)

    # 2. CORE DEEP ASSESSMENT QUESTIONS (16 total, 2 per domain)
    core_deep_questions = [
        # --- LANGUAGE & COMMUNICATION ---
        {
            "key": "language_race",
            "type": "order_steps",
            "domain": "language",
            "component": "core_deep",
            "title": {"English": "Story Order", "Hindi": "कहानी का क्रम"},
            "prompt": {
                "English": "Put these steps in the correct order to tell a story:",
                "Hindi": "कहानी बताने के लिए इन चरणों को सही क्रम में रखें:"
            },
            "steps": {
                "English": [
                    "We lined up at the starting line.",
                    "The whistle blew and we ran fast.",
                    "I crossed the finish line third.",
                    "We clapped and cheered for the winner."
                ],
                "Hindi": [
                    "हम शुरुआती रेखा पर खड़े हुए।",
                    "सीटी बजी और हम तेजी से दौड़े।",
                    "मैंने तीसरे स्थान पर फिनिश लाइन पार की।",
                    "हमने विजेता के लिए तालियाँ बजाईं।"
                ]
            },
            "shuffled": {
                "English": [
                    "We clapped and cheered for the winner.",
                    "We lined up at the starting line.",
                    "I crossed the finish line third.",
                    "The whistle blew and we ran fast."
                ],
                "Hindi": [
                    "हमने विजेता के लिए तालियाँ बजाईं।",
                    "हम शुरुआती रेखा पर खड़े हुए।",
                    "मैंने तीसरे स्थान पर फिनिश लाइन पार की।",
                    "सीटी बजी और हम तेजी से दौड़े।"
                ]
            },
            "metric": "sequence_accuracy",
            "difficulty": "easy",
            "ai_interpretation_notes": "Story building sequencing task."
        },
        {
            "key": "language_explain_game",
            "type": "choice",
            "domain": "language",
            "component": "core_deep",
            "title": {"English": "Teaching a Game", "Hindi": "खेल सिखाना"},
            "prompt": {
                "English": "You want to teach a new Class 1 student how to play your favorite playground game. What is the best way to explain it?",
                "Hindi": "आप पहली कक्षा के एक नए छात्र को अपना पसंदीदा खेल सिखाना चाहते हैं। इसे समझाने का सबसे अच्छा तरीका क्या है?"
            },
            "options": [
                {"label": {"English": "Show them the actions slowly and play a practice round together", "Hindi": "उन्हें धीरे-धीरे इशारों से समझाएं और साथ में एक अभ्यास खेल खेलें"}, "value": 4},
                {"label": {"English": "Read the full rulebook to them very quickly", "Hindi": "नियमों की पूरी किताब उन्हें बहुत तेजी से पढ़कर सुनाएं"}, "value": 1},
                {"label": {"English": "Tell them to watch other students play from far away", "Hindi": "उन्हें दूर से अन्य छात्रों को खेलते हुए देखने के लिए कहें"}, "value": 2},
                {"label": {"English": "Write down a list of rules and give it to them to read", "Hindi": "नियमों की एक सूची लिखकर उन्हें पढ़ने के लिए दे दें"}, "value": 0}
            ],
            "answer": "Show them the actions slowly and play a practice round together",
            "metric": "correctness",
            "difficulty": "easy",
            "ai_interpretation_notes": "Situational logic measuring empathetic communication."
        },
        # --- CREATIVE & ARTISTIC ---
        {
            "key": "creative_circles",
            "type": "idea_list",
            "domain": "creative",
            "component": "core_deep",
            "title": {"English": "Circles Challenge", "Hindi": "गोला चुनौती"},
            "prompt": {
                "English": "Imagine 3 empty circles. Write down 3 different and unique things you could draw by adding lines to these circles!",
                "Hindi": "3 खाली गोलों (circles) की कल्पना करें। कुछ लाइनें जोड़कर आप उनसे 3 अलग और अनोखी चीजें क्या बना सकते हैं, लिखें!"
            },
            "minIdeas": 3,
            "metric": "fluency",
            "difficulty": "adaptive",
            "ai_interpretation_notes": "Visual circle transformation test."
        },
        {
            "key": "creative_box_situational",
            "type": "choice",
            "domain": "creative",
            "component": "core_deep",
            "title": {"English": "Cardboard Box Use", "Hindi": "गत्ते के डिब्बे का उपयोग"},
            "prompt": {
                "English": "You find a large, empty cardboard box. What is the most creative way to use it?",
                "Hindi": "आपको एक बड़ा, खाली गत्ते का डिब्बा मिलता है। इसका उपयोग करने का सबसे रचनात्मक तरीका क्या है?"
            },
            "options": [
                {"label": {"English": "Turn it into a puppet theater with cut-out windows for a show", "Hindi": "इसे एक पपेट थियेटर (कटपुतली थियेटर) में बदलें और नाटक दिखाएं"}, "value": 4},
                {"label": {"English": "Use it to store old school notebooks neatly", "Hindi": "पुरानी स्कूल नोटबुक्स को रखने के लिए इसका उपयोग करें"}, "value": 2},
                {"label": {"English": "Flatten it and throw it in the dustbin", "Hindi": "इसे मोड़कर कचरे के डिब्बे में फेंक दें"}, "value": 1},
                {"label": {"English": "Keep it in the corner of the room empty", "Hindi": "कमरे के कोने में इसे खाली रख दें"}, "value": 0}
            ],
            "answer": "Turn it into a puppet theater with cut-out windows for a show",
            "metric": "correctness",
            "difficulty": "easy",
            "ai_interpretation_notes": "Situational creative divergent thinking."
        },
        # --- LOGICAL & ANALYTICAL ---
        {
            "key": "logical_lock",
            "type": "choice",
            "domain": "logical",
            "component": "core_deep",
            "title": {"English": "Number Lock", "Hindi": "संख्या का ताला"},
            "prompt": {
                "English": "A number pattern goes: 3, 6, 12, 24, ... What number comes next?",
                "Hindi": "एक संख्या पैटर्न इस प्रकार है: 3, 6, 12, 24, ... अगला नंबर क्या होगा?"
            },
            "options": [
                {"label": {"English": "30", "Hindi": "30"}, "value": 0},
                {"label": {"English": "48", "Hindi": "48"}, "value": 4},
                {"label": {"English": "36", "Hindi": "36"}, "value": 0},
                {"label": {"English": "40", "Hindi": "40"}, "value": 0}
            ],
            "answer": "48",
            "metric": "correctness",
            "difficulty": "easy",
            "ai_interpretation_notes": "Numerical progression pattern reasoning."
        },
        {
            "key": "logical_legs",
            "type": "choice",
            "domain": "logical",
            "component": "core_deep",
            "title": {"English": "Animal Legs", "Hindi": "जानवरों के पैर"},
            "prompt": {
                "English": "A duck has 2 legs, a dog has 4 legs, and a spider has 8 legs. Which of these fits the pattern of legs (2, 4, 8) increasing?",
                "Hindi": "एक बत्तख के 2 पैर होते हैं, एक कुत्ते के 4 पैर होते हैं, और एक मकड़ी के 8 पैर होते हैं। इनमें से कौन पैरों के बढ़ते हुए पैटर्न (2, 4, 8) में फिट बैठता है?"
            },
            "options": [
                {"label": {"English": "A sparrow (2 legs), a cat (4 legs), a crab (10 legs)", "Hindi": "एक गौरैया (2 पैर), एक बिल्ली (4 पैर), एक केकड़ा (10 पैर)"}, "value": 4},
                {"label": {"English": "A snake (0 legs), a monkey (2 legs), a horse (4 legs)", "Hindi": "एक सांप (0 पैर), एक बंदर (2 पैर), एक घोड़ा (4 पैर)"}, "value": 1},
                {"label": {"English": "A fish (0 legs), a bird (2 legs), a spider (8 legs)", "Hindi": "एक मछली (0 पैर), एक पक्षी (2 पैर), एक मकड़ी (8 पैर)"}, "value": 0},
                {"label": {"English": "A goat (4 legs), an ant (6 legs), a centipede (many legs)", "Hindi": "एक बकरी (4 पैर), एक चींटी (6 पैर), एक कनखजूरा (कई पैर)"}, "value": 2}
            ],
            "answer": "A sparrow (2 legs), a cat (4 legs), a crab (10 legs)",
            "metric": "correctness",
            "difficulty": "medium",
            "ai_interpretation_notes": "Pattern recognition and classification logic."
        },
        # --- SPATIAL & MAKING ---
        {
            "key": "spatial_shape_match",
            "type": "choice",
            "domain": "spatial",
            "component": "core_deep",
            "title": {"English": "Corner Blocks", "Hindi": "कोने के ब्लॉक"},
            "prompt": {
                "English": "You have a large solid cube with one corner block missing. Which single shape can fit perfectly into the empty corner to make the cube complete?",
                "Hindi": "आपके पास एक बड़ा ठोस घन (cube) है जिसका एक कोने का ब्लॉक गायब है। घन को पूरा करने के लिए खाली कोने में कौन सा आकार बिल्कुल सही फिट हो सकता है?"
            },
            "options": [
                {"label": {"English": "A small corner block matching the cutout size", "Hindi": "कटआउट आकार से मेल खाता हुआ एक छोटा कोना ब्लॉक"}, "value": 4},
                {"label": {"English": "A flat rectangular sheet", "Hindi": "एक सपाट आयताकार शीट"}, "value": 1},
                {"label": {"English": "A long cylindrical stick", "Hindi": "एक लंबी बेलनाकार छड़ी"}, "value": 0},
                {"label": {"English": "A round ball of the same height", "Hindi": "उसी ऊंचाई की एक गोल गेंद"}, "value": 2}
            ],
            "answer": "A small corner block matching the cutout size",
            "metric": "correctness",
            "difficulty": "easy",
            "ai_interpretation_notes": "Measures 3D spatial fitting and object completion visualization."
        },
        {
            "key": "spatial_clock",
            "type": "choice",
            "domain": "spatial",
            "component": "core_deep",
            "title": {"English": "Clock Rotation", "Hindi": "घड़ी का घूमना"},
            "prompt": {
                "English": "A clock hand points straight UP (at 12). If it rotates a quarter turn (90 degrees) clockwise, where does it point?",
                "Hindi": "एक घड़ी की सुई सीधे ऊपर (12 पर) इशारा करती है। यदि यह घड़ी की दिशा में एक चौथाई चक्कर (90 डिग्री) घूमती है, तो यह कहाँ इशारा करेगी?"
            },
            "options": [
                {"label": {"English": "Right (at 3)", "Hindi": "दाएँ (3 पर)"}, "value": 4},
                {"label": {"English": "Down (at 6)", "Hindi": "नीचे (6 पर)"}, "value": 1},
                {"label": {"English": "Left (at 9)", "Hindi": "बाएँ (9 पर)"}, "value": 0},
                {"label": {"English": "It stays at 12", "Hindi": "यह 12 पर ही रहती है"}, "value": 0}
            ],
            "answer": "Right (at 3)",
            "metric": "correctness",
            "difficulty": "easy",
            "ai_interpretation_notes": "Measures 2D rotation and orientation tracking."
        },
        # --- KINESTHETIC & PHYSICAL ---
        {
            "key": "visualizer_memory_grid",
            "type": "memory_grid",
            "domain": "spatial",
            "component": "core_deep",
            "title": {"English": "Step Memory", "Hindi": "कदम याद रखना"},
            "prompt": {
                "English": "Repeat the highlighted path of footsteps accurately. The speed, accuracy, and sequence of moves are checked.",
                "Hindi": "पदचिह्नों के हाइलाइट किए गए मार्ग को बिल्कुल सही दोहराएं। कदमों की गति, सटीकता और क्रम की जांच की जाती है।"
            },
            "gridSize": 3,
            "path": [0, 4, 8, 7],
            "metric": "spatial_navigation",
            "difficulty": "medium",
            "ai_interpretation_notes": "Measures sequence learning and motor-planning recall."
        },
        {
            "key": "kinesthetic_catch",
            "type": "choice",
            "domain": "kinesthetic",
            "component": "core_deep",
            "title": {"English": "Catching a Ball", "Hindi": "गेंद पकड़ना"},
            "prompt": {
                "English": "A friend throws a high ball toward you, but the wind is blowing it to your left. Where should you run to catch it?",
                "Hindi": "एक दोस्त आपकी ओर एक ऊंची गेंद फेंकता है, लेकिन हवा उसे आपकी बाईं ओर धकेल रही है। गेंद को पकड़ने के लिए आपको किस ओर दौड़ना चाहिए?"
            },
            "options": [
                {"label": {"English": "Run to your left side and slightly back", "Hindi": "अपनी बाईं ओर और थोड़ा पीछे की ओर दौड़ें"}, "value": 4},
                {"label": {"English": "Stand completely still in the center", "Hindi": "केंद्र में बिल्कुल स्थिर खड़े रहें"}, "value": 1},
                {"label": {"English": "Run to your right side and forward", "Hindi": "अपनी दाईं ओर और आगे की ओर दौड़ें"}, "value": 0},
                {"label": {"English": "Run directly forward toward your friend", "Hindi": "सीधे अपने दोस्त की ओर आगे दौड़ें"}, "value": 2}
            ],
            "answer": "Run to your left side and slightly back",
            "metric": "correctness",
            "difficulty": "easy",
            "ai_interpretation_notes": "Biomechanical coordinate reasoning and anticipation."
        },
        {
            "key": "kinesthetic_motor_planning",
            "type": "choice",
            "domain": "kinesthetic",
            "component": "core_deep",
            "title": {"English": "The Rope Bridge", "Hindi": "रस्सी का पुल"},
            "prompt": {
                "English": "You are on a wobbling rope bridge. Strong wind blows from the right! What is the best way to balance?",
                "Hindi": "आप एक हिलते हुए रस्सी के पुल पर हैं। दाईं ओर से तेज हवा चलती है! सुरक्षित रहने के लिए आप क्या करेंगे?"
            },
            "options": [
                {"label": {"English": "Bend knees, spread arms, and lean slightly right", "Hindi": "घुटनों को मोड़ें, हाथ फैलाएं और थोड़ा दाईं ओर झुकें"}, "value": 4},
                {"label": {"English": "Stand straight and close eyes", "Hindi": "बिल्कुल सीधे खड़े रहें और आंखें बंद करें"}, "value": 0},
                {"label": {"English": "Run fast to the other side", "Hindi": "जितनी तेजी से हो सके दूसरी तरफ दौड़ें"}, "value": 1},
                {"label": {"English": "Sit down and shout for help", "Hindi": "रस्सी के पुल पर बैठ जाएं और मदद के लिए चिल्लाएं"}, "value": 2}
            ],
            "answer": "Bend knees, spread arms, and lean slightly right",
            "metric": "correctness",
            "difficulty": "medium",
            "ai_interpretation_notes": "Motor planning and body stabilisation under dynamic conditions."
        },
        # --- NATURALIST & ENVIRONMENTAL ---
        {
            "key": "naturalist_weather",
            "type": "choice",
            "domain": "naturalist",
            "component": "core_deep",
            "title": {"English": "Nature Weather Sign", "Hindi": "प्रकृति के मौसम संकेत"},
            "prompt": {
                "English": "You notice that swallow birds are flying very low to the ground and ants are piling soil around their holes. What weather change is likely coming?",
                "Hindi": "आप देखते हैं कि गौरैया पक्षी जमीन के बहुत करीब उड़ रहे हैं और चींटियां अपने बिलों के आसपास मिट्टी का ढेर लगा रही हैं। मौसम में क्या बदलाव आने की संभावना है?"
            },
            "options": [
                {"label": {"English": "It is going to rain soon", "Hindi": "जल्द ही बारिश होने वाली है"}, "value": 4},
                {"label": {"English": "A hot dry wind is starting", "Hindi": "गर्म सूखी हवा चलने वाली है"}, "value": 1},
                {"label": {"English": "The weather will stay sunny and dry", "Hindi": "मौसम धूप वाला और शुष्क रहेगा"}, "value": 0},
                {"label": {"English": "It will start snowing", "Hindi": "बर्फबारी शुरू हो जाएगी"}, "value": 0}
            ],
            "answer": "It is going to rain soon",
            "metric": "correctness",
            "difficulty": "easy",
            "ai_interpretation_notes": "Measures environmental awareness and reading nature indicators."
        },
        {
            "key": "naturalist_plants",
            "type": "choice",
            "domain": "naturalist",
            "component": "core_deep",
            "title": {"English": "Spotting Leaf Spot", "Hindi": "पत्ती के धब्बे पहचानना"},
            "prompt": {
                "English": "Your tomato plant's lower leaves have dark circular spots with yellow rings. The top leaves look healthy. What should you do first to save it?",
                "Hindi": "आपके टमाटर के पौधे की निचली पत्तियों पर पीले घेरे के साथ गहरे रंग के गोल धब्बे हैं। ऊपर की पत्तियाँ स्वस्थ दिखती हैं। इसे बचाने के लिए आपको सबसे पहले क्या करना चाहिए?"
            },
            "options": [
                {"label": {"English": "Cut off the spotted lower leaves and water the roots, not the leaves", "Hindi": "धब्बेदार निचली पत्तियों को काट दें और पत्तियों पर नहीं बल्कि जड़ों में पानी दें"}, "value": 4},
                {"label": {"English": "Cut down the entire plant from the base", "Hindi": "पूरे पौधे को आधार से काट दें"}, "value": 1},
                {"label": {"English": "Pour extra water on all the green leaves", "Hindi": "सभी हरी पत्तियों पर अतिरिक्त पानी डालें"}, "value": 0},
                {"label": {"English": "Move it into a completely dark room", "Hindi": "इसे पूरी तरह से अंधेरे कमरे में ले जाएं"}, "value": 0}
            ],
            "answer": "Cut off the spotted lower leaves and water the roots, not the leaves",
            "metric": "correctness",
            "difficulty": "medium",
            "ai_interpretation_notes": "Practical botanical diagnostics and naturalist care reasoning."
        },
        # --- SOCIAL & LEADERSHIP ---
        {
            "key": "social_planning",
            "type": "choice",
            "domain": "social",
            "component": "core_deep",
            "title": {"English": "Cleaning Team", "Hindi": "सफाई टीम"},
            "prompt": {
                "English": "Your teacher asks your group of 4 students to clean the classroom. What is the best way to lead the work?",
                "Hindi": "आपकी शिक्षिका आपके 4 छात्रों के समूह को कक्षा साफ करने के लिए कहती हैं। काम का नेतृत्व करने का सबसे अच्छा तरीका क्या है?"
            },
            "options": [
                {"label": {"English": "Assign different tasks to each person based on what they like doing, and clean together", "Hindi": "प्रत्येक व्यक्ति को उनकी पसंद के आधार पर अलग-अलग काम सौंपें, और मिलकर सफाई करें"}, "value": 4},
                {"label": {"English": "Do all the cleaning yourself while the other 3 students watch", "Hindi": "बाकी 3 छात्रों के देखने के दौरान सारा सफाई कार्य स्वयं करें"}, "value": 1},
                {"label": {"English": "Tell the other 3 students to clean everything while you sit and supervise", "Hindi": "बाकी 3 छात्रों को सब कुछ साफ करने के लिए कहें जबकि आप बैठकर निगरानी करें"}, "value": 2},
                {"label": {"English": "Leave the classroom and hope the teacher cleans it instead", "Hindi": "कक्षा से बाहर चले जाएं और आशा करें कि शिक्षिका ही इसे साफ करेंगी"}, "value": 0}
            ],
            "answer": "Assign different tasks to each person based on what they like doing, and clean together",
            "metric": "correctness",
            "difficulty": "easy",
            "ai_interpretation_notes": "Situational task delegation and team coordination."
        },
        {
            "key": "social_conflict_resolution",
            "type": "choice",
            "domain": "social",
            "component": "core_deep",
            "title": {"English": "Playground Dispute", "Hindi": "मैदान का झगड़ा"},
            "prompt": {
                "English": "During a playground game, two friends are arguing loudly about who got out first. What is the best action to resolve this?",
                "Hindi": "खेल के मैदान में एक खेल के दौरान, दो दोस्त ज़ोर-ज़ोर से बहस कर रहे हैं कि पहले कौन आउट हुआ। इसे सुलझाने के लिए सबसे अच्छा कदम क्या है?"
            },
            "options": [
                {"label": {"English": "Suggest a quick toss or game-point rule to decide, then continue playing", "Hindi": "तय करने के लिए एक त्वरित टॉस या गेम-पॉइंट नियम का सुझाव देंगे, फिर खेल जारी रखेंगे"}, "value": 4},
                {"label": {"English": "Take the bat away and stop the game for everyone", "Hindi": "बल्ला छीन लेंगे और सभी के लिए खेल बंद कर देंगे"}, "value": 1},
                {"label": {"English": "Support the friend you like more and ignore the other", "Hindi": "अपने पसंदीदा दोस्त का समर्थन करेंगे और दूसरे की अनदेखी करेंगे"}, "value": 2},
                {"label": {"English": "Shout at both of them to go back to class", "Hindi": "दोनों पर चिल्लाकर उन्हें वापस कक्षा में जाने के लिए कहेंगे"}, "value": 0}
            ],
            "answer": "Suggest a quick toss or game-point rule to decide, then continue playing",
            "metric": "correctness",
            "difficulty": "easy",
            "ai_interpretation_notes": "Measures conflict resolution and democratic playground mediation."
        },
        # --- INTRAPERSONAL & REFLECTIVE ---
        {
            "key": "intrapersonal_goals",
            "type": "choice",
            "domain": "intrapersonal",
            "component": "core_deep",
            "title": {"English": "Learning a Skill", "Hindi": "कौशल सीखना"},
            "prompt": {
                "English": "You want to learn a difficult new skill, like sketching or a sport, in one month. What is the best way to practice?",
                "Hindi": "आप एक महीने में स्केचिंग या कोई खेल जैसा कठिन नया कौशल सीखना चाहते हैं। अभ्यास करने का सबसे अच्छा तरीका क्या है?"
            },
            "options": [
                {"label": {"English": "Practice for 15 minutes every single day and track your progress", "Hindi": "हर दिन 15 मिनट अभ्यास करें और अपनी प्रगति को ट्रैक करें"}, "value": 4},
                {"label": {"English": "Practice for 5 hours on the last day of the month only", "Hindi": "महीने के केवल अंतिम दिन 5 घंटे अभ्यास करें"}, "value": 1},
                {"label": {"English": "Only practice when you feel very happy or excited", "Hindi": "केवल तभी अभ्यास करें जब आप बहुत खुश या उत्साहित महसूस करें"}, "value": 2},
                {"label": {"English": "Wait for someone to force you to practice", "Hindi": "किसी के द्वारा अभ्यास के लिए मजबूर करने का इंतजार करें"}, "value": 0}
            ],
            "answer": "Practice for 15 minutes every single day and track your progress",
            "metric": "correctness",
            "difficulty": "easy",
            "ai_interpretation_notes": "Self-regulation and systematic planning logic."
        },
        {
            "key": "intrapersonal_reflection",
            "type": "choice",
            "domain": "intrapersonal",
            "component": "core_deep",
            "title": {"English": "Unsolved Puzzle", "Hindi": "अनसुलझी पहेली"},
            "prompt": {
                "English": "You fail to solve a very hard puzzle after trying for a long time. What is your thought?",
                "Hindi": "लंबे समय तक कोशिश करने के बाद भी आप एक बहुत कठिन पहेली को हल करने में विफल रहते हैं। आपका विचार क्या है?"
            },
            "options": [
                {"label": {"English": "This is a good challenge, let me look at it differently and try again", "Hindi": "यह एक अच्छी चुनौती है, मुझे इसे अलग तरीके से देखना चाहिए और फिर से प्रयास करना चाहिए"}, "value": 4},
                {"label": {"English": "I am not smart enough to solve puzzles", "Hindi": "मैं पहेलियाँ हल करने के लिए पर्याप्त स्मार्ट नहीं हूँ"}, "value": 1},
                {"label": {"English": "This puzzle has a wrong question and is broken", "Hindi": "यह पहेली गलत प्रश्न है और खराब है"}, "value": 2},
                {"label": {"English": "I will never try a puzzle again", "Hindi": "मैं फिर कभी पहेली का प्रयास नहीं करूँगा"}, "value": 0}
            ],
            "answer": "This is a good challenge, let me look at it differently and try again",
            "metric": "correctness",
            "difficulty": "easy",
            "ai_interpretation_notes": "Growth mindset and cognitive resilience indicator."
        }
    ]

    # Add Core Deep questions to bank
    for q in core_deep_questions:
        bank.append(q)

    # 3. REFLECTION QUESTIONS (4 total, open-ended)
    reflection_questions = [
        {
            "key": "reflection_pride",
            "type": "open_ended",
            "domain": "intrapersonal",
            "component": "reflection",
            "title": {"English": "Proudest Achievement", "Hindi": "गर्व की उपलब्धि"},
            "prompt": {
                "English": "What achievement or moment in your life are you most proud of?",
                "Hindi": "आपके जीवन की कौन सी उपलब्धि या क्षण ऐसा है जिस पर आपको सबसे अधिक गर्व है?"
            },
            "metric": "narrative_expression",
            "difficulty": "easy",
            "ai_interpretation_notes": "Exposes core values, pride drivers, and self-awareness."
        },
        {
            "key": "reflection_flow",
            "type": "open_ended",
            "domain": "intrapersonal",
            "component": "reflection",
            "title": {"English": "Forget Time", "Hindi": "समय भूल जाना"},
            "prompt": {
                "English": "What activity or hobby makes you completely forget about time?",
                "Hindi": "कौन सी गतिविधि या शौक ऐसा है जो आपको समय का अहसास पूरी तरह से भुला देता है?"
            },
            "metric": "narrative_expression",
            "difficulty": "easy",
            "ai_interpretation_notes": "Measures spontaneous flow state and deep intrinsic interest patterns."
        },
        {
            "key": "reflection_learning",
            "type": "open_ended",
            "domain": "intrapersonal",
            "component": "reflection",
            "title": {"English": "Want to Learn", "Hindi": "सीखने की इच्छा"},
            "prompt": {
                "English": "What is one new thing you would love to learn how to do this year?",
                "Hindi": "ऐसी कौन सी एक नई चीज़ है जिसे आप इस साल सीखना पसंद करेंगे?"
            },
            "metric": "narrative_expression",
            "difficulty": "easy",
            "ai_interpretation_notes": "Measures child's curiosities and proactive growth mindset targets."
        },
        {
            "key": "reflection_community",
            "type": "open_ended",
            "domain": "social",
            "component": "reflection",
            "title": {"English": "School Improvement", "Hindi": "स्कूल सुधार"},
            "prompt": {
                "English": "If you could improve one thing in your school or community, what would it be?",
                "Hindi": "यदि आप अपने स्कूल या समुदाय में कोई एक चीज़ सुधार सकें, तो वह क्या होगी?"
            },
            "metric": "narrative_expression",
            "difficulty": "easy",
            "ai_interpretation_notes": "Exposes empathy, civic values, and social/leadership problem-solving leanings."
        }
    ]

    # Add Reflection Questions to bank
    for q in reflection_questions:
        bank.append(q)

    # 4. ADAPTIVE ASSESSMENT BANK (16 total, 2 per domain)
    adaptive_questions = [
        # --- LANGUAGE & COMMUNICATION ---
        {
            "key": "adaptive_language_story",
            "type": "choice",
            "domain": "language",
            "component": "adaptive",
            "title": {"English": "Monkey Copy", "Hindi": "नकलची बंदर"},
            "prompt": {
                "English": "A merchant sells hats. Monkeys steal them and climb a tree. The merchant throws his own hat down in frustration, and all the monkeys throw their hats down too. Why did the monkeys copy him?",
                "Hindi": "एक व्यापारी टोपियां बेचता है। बंदर उन्हें चुराकर पेड़ पर चढ़ जाते हैं। व्यापारी हताशा में अपनी टोपी नीचे फेंकता है, और सभी बंदर भी अपनी-अपनी टोपियां नीचे फेंक देते हैं। बंदरों ने उसकी नकल क्यों की?"
            },
            "options": [
                {"label": {"English": "Monkeys naturally copy the actions they see around them", "Hindi": "बंदर स्वाभाविक रूप से अपने आस-पास दिखने वाले कामों की नकल करते हैं"}, "value": 4},
                {"label": {"English": "The monkeys were angry and wanted to attack the merchant", "Hindi": "बंदर गुस्से में थे और व्यापारी पर हमला करना चाहते थे"}, "value": 2},
                {"label": {"English": "The merchant had trained these monkeys in a circus before", "Hindi": "व्यापारी ने इन बंदरों को पहले एक सर्कस में प्रशिक्षित किया था"}, "value": 1},
                {"label": {"English": "The hats were too hot and heavy to keep on their heads", "Hindi": "टोपियां सिर पर रखने के लिए बहुत गर्म और भारी थीं"}, "value": 0}
            ],
            "answer": "Monkeys naturally copy the actions they see around them",
            "metric": "comprehension",
            "difficulty": "hard",
            "ai_interpretation_notes": "Measures deep story comprehension and narrative deduction."
        },
        {
            "key": "adaptive_language_teach",
            "type": "choice",
            "domain": "language",
            "component": "adaptive",
            "title": {"English": "Explain Multiplication", "Hindi": "गुणा समझाना"},
            "prompt": {
                "English": "You are teaching a classmate how to multiply numbers. They make the same mistake twice. What is the most helpful way to guide them?",
                "Hindi": "आप अपने एक सहपाठी को गुणा करना सिखा रहे हैं। वे दो बार एक ही गलती करते हैं। उनका मार्गदर्शन करने का सबसे उपयोगी तरीका क्या है?"
            },
            "options": [
                {"label": {"English": "Use small stones to show the groupings visually", "Hindi": "समूह को स्पष्ट रूप से दिखाने के लिए छोटे पत्थरों का उपयोग करेंगे"}, "value": 4},
                {"label": {"English": "Tell them to read the math textbook rules again", "Hindi": "उन्हें गणित की पाठ्यपुस्तक के नियमों को फिर से पढ़ने के लिए कहेंगे"}, "value": 2},
                {"label": {"English": "Speak louder so they hear your instructions clearly", "Hindi": "जोर से बोलेंगे ताकि वे आपके निर्देशों को स्पष्ट रूप से सुन सकें"}, "value": 1},
                {"label": {"English": "Write down the correct answers for them to copy", "Hindi": "उनके लिए सही उत्तर लिख देंगे ताकि वे उसकी नकल कर सकें"}, "value": 0}
            ],
            "answer": "Use small stones to show the groupings visually",
            "metric": "explanation_clarity",
            "difficulty": "hard",
            "ai_interpretation_notes": "Measures teaching challenge explanation ability."
        },
        # --- CREATIVE & ARTISTIC ---
        {
            "key": "adaptive_creative_transform",
            "type": "choice",
            "domain": "creative",
            "component": "adaptive",
            "title": {"English": "Plastic Bottle Invention", "Hindi": "प्लास्टिक की बोतल का आविष्कार"},
            "prompt": {
                "English": "You have a plastic bottle, a straw, and a rubber band. What unique invention do you design?",
                "Hindi": "आपके पास एक प्लास्टिक की बोतल, एक स्ट्रॉ और एक रबर बैंड है। आप किस अनोखे आविष्कार का डिज़ाइन तैयार करेंगे?"
            },
            "options": [
                {"label": {"English": "A mini wind-up boat that runs in water", "Hindi": "एक मिनी वाइंड-अप नाव जो पानी में चलती है"}, "value": 4},
                {"label": {"English": "A simple pencil stand to keep pens on the table", "Hindi": "मेज पर पेन रखने के लिए एक साधारण पेंसिल स्टैंड"}, "value": 2},
                {"label": {"English": "A trash bottle to keep used straws in", "Hindi": "उपयोग की गई स्ट्रॉ को रखने के लिए एक कचरे की बोतल"}, "value": 1},
                {"label": {"English": "A standard drinking bottle to hold water", "Hindi": "पानी भरने के लिए एक साधारण बोतल"}, "value": 0}
            ],
            "answer": "A mini wind-up boat that runs in water",
            "metric": "originality",
            "difficulty": "hard",
            "ai_interpretation_notes": "Object transformation and inventive thinking."
        },
        {
            "key": "adaptive_creative_design",
            "type": "choice",
            "domain": "creative",
            "component": "adaptive",
            "title": {"English": "School Mascot Theme", "Hindi": "स्कूल मस्कट थीम"},
            "prompt": {
                "English": "Your school needs a mascot. You want to represent unity and energy. What do you design?",
                "Hindi": "आपके स्कूल को एक शुभंकर (mascot) की आवश्यकता है। आप एकता और ऊर्जा का प्रतिनिधित्व करना चाहते हैं। आप क्या डिज़ाइन करेंगे?"
            },
            "options": [
                {"label": {"English": "A glowing multi-colored wheel made of handprints", "Hindi": "हाथ के निशानों से बना एक चमकता हुआ बहुरंगी पहिया"}, "value": 4},
                {"label": {"English": "A simple picture of the school main gate and building", "Hindi": "स्कूल के मुख्य गेट और इमारत का एक साधारण चित्र"}, "value": 2},
                {"label": {"English": "A standard shield with school letters", "Hindi": "स्कूल के अक्षरों वाला एक मानक शील्ड"}, "value": 1},
                {"label": {"English": "A plain brown square board", "Hindi": "एक साधारण भूरा चौकोर बोर्ड"}, "value": 0}
            ],
            "answer": "A glowing multi-colored wheel made of handprints",
            "metric": "design_expression",
            "difficulty": "hard",
            "ai_interpretation_notes": "Creative symbolism and visual design challenge."
        },
        # --- LOGICAL & ANALYTICAL ---
        {
            "key": "adaptive_logical_reasoning",
            "type": "choice",
            "domain": "logical",
            "component": "adaptive",
            "title": {"English": "Weight Order", "Hindi": "वजन का क्रम"},
            "prompt": {
                "English": "Box A is heavier than Box B. Box B is heavier than Box C. Box D is heavier than Box A. Which box is the heaviest?",
                "Hindi": "बक्सा A, बक्से B से भारी है। बक्सा B, बक्से C से भारी है। बक्सा D, बक्से A से भारी है। सबसे भारी बक्सा कौन सा है?"
            },
            "options": [
                {"label": {"English": "Box D", "Hindi": "बक्सा D"}, "value": 4},
                {"label": {"English": "Box A", "Hindi": "बक्सा A"}, "value": 0},
                {"label": {"English": "Box B", "Hindi": "बक्सा B"}, "value": 0},
                {"label": {"English": "Box C", "Hindi": "बक्सा C"}, "value": 0}
            ],
            "answer": "Box D",
            "metric": "deductive_reasoning",
            "difficulty": "hard",
            "ai_interpretation_notes": "Multi-step logical deduction."
        },
        {
            "key": "adaptive_logical_problem",
            "type": "choice",
            "domain": "logical",
            "component": "adaptive",
            "title": {"English": "Library Book Share", "Hindi": "लाइब्रेरी किताबों का बंटवारा"},
            "prompt": {
                "English": "Your school has 10 new library books. Class A has 30 kids. Class B has 15 kids. How should the books be shared fairly?",
                "Hindi": "आपके स्कूल में 10 नई लाइब्रेरी पुस्तकें हैं। कक्षा A में 30 बच्चे हैं। कक्षा B में 15 बच्चे हैं। पुस्तकों को निष्पक्ष रूप से कैसे साझा किया जाना चाहिए?"
            },
            "options": [
                {"label": {"English": "Class A gets 7 books, Class B gets 3 books (by student ratio)", "Hindi": "कक्षा A को 7 पुस्तकें मिलें, कक्षा B को 3 पुस्तकें मिलें (छात्रों के अनुपात में)"}, "value": 4},
                {"label": {"English": "Give 5 books to each class", "Hindi": "प्रत्येक कक्षा को 5 पुस्तकें दें"}, "value": 2},
                {"label": {"English": "Give all 10 books to Class A because it is larger", "Hindi": "बड़ी होने के कारण सभी 10 पुस्तकें कक्षा A को दे दें"}, "value": 1},
                {"label": {"English": "Keep all books in the principal's room unused", "Hindi": "सभी किताबों को प्रधानाचार्य के कमरे में बिना इस्तेमाल के रखें"}, "value": 0}
            ],
            "answer": "Class A gets 7 books, Class B gets 3 books (by student ratio)",
            "metric": "problem_solving",
            "difficulty": "hard",
            "ai_interpretation_notes": "Practical proportional reasoning."
        },
        # --- SPATIAL & MAKING ---
        {
            "key": "adaptive_spatial_construction",
            "type": "choice",
            "domain": "spatial",
            "component": "adaptive",
            "title": {"English": "Stable Tower Base", "Hindi": "स्थिर टावर का आधार"},
            "prompt": {
                "English": "You are building a tall tower with wooden blocks. Which shape is best for the base to make it very stable and prevent it from falling?",
                "Hindi": "आप लकड़ी के ब्लॉकों से एक ऊँचा टावर बना रहे हैं। इसे बहुत स्थिर बनाने और गिरने से रोकने के लिए आधार के लिए कौन सा आकार सबसे अच्छा है?"
            },
            "options": [
                {"label": {"English": "A wide solid pyramid block", "Hindi": "एक चौड़ा ठोस पिरामिड ब्लॉक"}, "value": 4},
                {"label": {"English": "A tall thin cylinder block", "Hindi": "एक लंबा पतला बेलनाकार ब्लॉक"}, "value": 2},
                {"label": {"English": "An upside-down cone shape", "Hindi": "एक उलटा शंक्वाकार आकार"}, "value": 1},
                {"label": {"English": "A narrow flat stick block", "Hindi": "एक संकीर्ण फ्लैट छड़ी ब्लॉक"}, "value": 0}
            ],
            "answer": "A wide solid pyramid block",
            "metric": "structural_reasoning",
            "difficulty": "hard",
            "ai_interpretation_notes": "Visual construction stability logic."
        },
        {
            "key": "adaptive_spatial_reasoning",
            "type": "choice",
            "domain": "spatial",
            "component": "adaptive",
            "title": {"English": "Paper Punch Holes", "Hindi": "कागज में छेद"},
            "prompt": {
                "English": "Imagine folding a flat square piece of paper in half, then punching one single hole through the middle. When you unfold the paper flat, how many holes will there be?",
                "Hindi": "कल्पना करें कि कागज के एक वर्गाकार टुकड़े को आधा मोड़ा जाता है, और फिर बीच में एक छेद किया जाता है। जब आप कागज को खोलेंगे, तो उसमें कितने छेद होंगे?"
            },
            "options": [
                {"label": {"English": "2 holes", "Hindi": "2 छेद"}, "value": 4},
                {"label": {"English": "1 hole", "Hindi": "1 छेद"}, "value": 1},
                {"label": {"English": "3 holes", "Hindi": "3 छेद"}, "value": 0},
                {"label": {"English": "4 holes", "Hindi": "4 छेद"}, "value": 0}
            ],
            "answer": "2 holes",
            "metric": "spatial_reasoning",
            "difficulty": "hard",
            "ai_interpretation_notes": "Measures spatial folding visualization."
        },
        # --- KINESTHETIC & PHYSICAL ---
        {
            "key": "adaptive_kinesthetic_strategy",
            "type": "choice",
            "domain": "kinesthetic",
            "component": "adaptive",
            "title": {"English": "Escape Tag Defenders", "Hindi": "बचाव रणनीति"},
            "prompt": {
                "English": "In a game of tag, three defenders are blocking you in the center. What is the best strategy to escape?",
                "Hindi": "पकड़म-पकड़ाई के खेल में, तीन रक्षक बीच में आपका रास्ता रोक रहे हैं। बचने की सबसे अच्छी रणनीति क्या है?"
            },
            "options": [
                {"label": {"English": "Run sideways to draw them, then pivot and sprint past their gap", "Hindi": "उन्हें एक तरफ खींचने के लिए बगल में दौड़ें, फिर मुड़कर उनके बीच की खाली जगह से निकल जाएं"}, "value": 4},
                {"label": {"English": "Run directly into the middle defender as fast as you can", "Hindi": "जितनी तेजी से हो सके सीधे बीच वाले रक्षक की ओर दौड़ें"}, "value": 2},
                {"label": {"English": "Stop running and wait to be tagged easily", "Hindi": "दौड़ना बंद करें और आसानी से पकड़े जाने का इंतजार करें"}, "value": 1},
                {"label": {"English": "Shout at them to move away from your path", "Hindi": "उन्हें अपने रास्ते से हटने के लिए चिल्लाएं"}, "value": 0}
            ],
            "answer": "Run sideways to draw them, then pivot and sprint past their gap",
            "metric": "movement_strategy",
            "difficulty": "hard",
            "ai_interpretation_notes": "Physical route and speed adjustment strategy planning."
        },
        {
            "key": "adaptive_kinesthetic_learning",
            "type": "choice",
            "domain": "kinesthetic",
            "component": "adaptive",
            "title": {"English": "Bicycle Trick", "Hindi": "साइकिल की ट्रिक"},
            "prompt": {
                "English": "You are trying to learn a new bicycle trick. You keep losing balance. What is the best way to master it?",
                "Hindi": "आप साइकिल की एक नई ट्रिक सीखने की कोशिश कर रहे हैं। आप बार-बार संतुलन खो देते हैं। इसमें महारत हासिल करने का सबसे अच्छा तरीका क्या है?"
            },
            "options": [
                {"label": {"English": "Practice the balance step-by-step slowly near a wall first", "Hindi": "पहले दीवार के पास धीरे-धीरे संतुलन का अभ्यास कदम-दर-कदम करें"}, "value": 4},
                {"label": {"English": "Ride as fast as possible down a steep hill to get momentum", "Hindi": "गति प्राप्त करने के लिए किसी ढलान वाली पहाड़ी से जितनी जल्दी हो सके उतनी तेजी से उतरें"}, "value": 2},
                {"label": {"English": "Try it only once a week to let your legs rest", "Hindi": "सप्ताह में केवल एक बार इसका प्रयास करें ताकि आपके पैरों को आराम मिले"}, "value": 1},
                {"label": {"English": "Give up immediately and ride normally", "Hindi": "तुरंत हार मान लें और सामान्य रूप से साइकिल चलाएं"}, "value": 0}
            ],
            "answer": "Practice the balance step-by-step slowly near a wall first",
            "metric": "sports_learning",
            "difficulty": "hard",
            "ai_interpretation_notes": "Measures physical safety and skill breakdown awareness."
        },
        # --- NATURALIST & ENVIRONMENTAL ---
        {
            "key": "adaptive_naturalist_observation",
            "type": "choice",
            "domain": "naturalist",
            "component": "adaptive",
            "title": {"English": "Green Lake Change", "Hindi": "झील का हरा होना"},
            "prompt": {
                "English": "You notice that a small lake in your village has turned green and fish are gasping for air at the surface. What is the most likely reason?",
                "Hindi": "आप देखते हैं कि आपके गाँव की एक छोटी सी झील हरी हो गई है और मछलियाँ सतह पर हवा के लिए तड़प रही हैं। इसका सबसे संभावित कारण क्या है?"
            },
            "options": [
                {"label": {"English": "Fertilizers or waste flowed into the water, causing overgrown algae", "Hindi": "खाद या कचरा पानी में बह गया, जिससे शैवाल (algae) बहुत ज़्यादा बढ़ गए"}, "value": 4},
                {"label": {"English": "The water has become too cold for the fish to swim", "Hindi": "पानी मछलियों के तैरने के लिए बहुत ठंडा हो गया है"}, "value": 2},
                {"label": {"English": "The fish are playing a jumping game at the surface", "Hindi": "मछलियां सतह पर कूदने का खेल खेल रही हैं"}, "value": 1},
                {"label": {"English": "Rainwater has made the lake clean and fresh", "Hindi": "बारिश के पानी ने झील को साफ और ताजा बना दिया है"}, "value": 0}
            ],
            "answer": "Fertilizers or waste flowed into the water, causing overgrown algae",
            "metric": "ecosystem_understanding",
            "difficulty": "hard",
            "ai_interpretation_notes": "Ecosystem observation and cause-effect reasoning."
        },
        {
            "key": "adaptive_naturalist_problem",
            "type": "choice",
            "domain": "naturalist",
            "component": "adaptive",
            "title": {"English": "Dry Summer Water", "Hindi": "गर्मियों में पानी की कमी"},
            "prompt": {
                "English": "Your village is running out of clean drinking water in summer. What is the best environmental solution?",
                "Hindi": "गर्मी के दिनों में आपके गाँव में पीने के साफ पानी की कमी हो रही है। पर्यावरण के अनुकूल सबसे अच्छा समाधान क्या है?"
            },
            "options": [
                {"label": {"English": "Build rainwater harvesting filters in houses to save rain", "Hindi": "बारिश के पानी को बचाने के लिए घरों में वर्षा जल संचयन (rainwater harvesting) फिल्टर लगाएं"}, "value": 4},
                {"label": {"English": "Buy plastic bottled water from the city every day", "Hindi": "हर दिन शहर से प्लास्टिक की बोतलों में बंद पानी खरीदें"}, "value": 2},
                {"label": {"English": "Dig the local pond much deeper during active rainy days", "Hindi": "बारिश के दिनों में स्थानीय तालाब को और अधिक गहरा खोदें"}, "value": 3},
                {"label": {"English": "Use less water for drinking to save it", "Hindi": "पानी बचाने के लिए पीने के लिए कम पानी का उपयोग करें"}, "value": 0}
            ],
            "answer": "Build rainwater harvesting filters in houses to save rain",
            "metric": "environmental_problem_solving",
            "difficulty": "hard",
            "ai_interpretation_notes": "Practical water-scarcity environmental reasoning."
        },
        # --- SOCIAL & LEADERSHIP ---
        {
            "key": "adaptive_social_conflict",
            "type": "choice",
            "domain": "social",
            "component": "adaptive",
            "title": {"English": "Role Dispute", "Hindi": "भूमिका का विवाद"},
            "prompt": {
                "English": "Two members of your school group want to do the same task and are arguing. How do you lead them?",
                "Hindi": "आपके स्कूल समूह के दो सदस्य एक ही काम करना चाहते हैं और बहस कर रहे हैं। आप उनका नेतृत्व कैसे करेंगे?"
            },
            "options": [
                {"label": {"English": "Split the task into two sub-tasks so both can contribute", "Hindi": "कार्य को दो उप-कार्यों (sub-tasks) में विभाजित करें ताकि दोनों योगदान दे सकें"}, "value": 4},
                {"label": {"English": "Do the task yourself and ignore their arguments", "Hindi": "कार्य स्वयं करें और उनकी बहस की उपेक्षा करें"}, "value": 2},
                {"label": {"English": "Choose the older student to do the task and ignore the younger one", "Hindi": "कार्य करने के लिए बड़े छात्र को चुनें और छोटे वाले की उपेक्षा करें"}, "value": 1},
                {"label": {"English": "Tell them both to leave the school group immediately", "Hindi": "उन दोनों को तुरंत स्कूल समूह छोड़ने के लिए कहें"}, "value": 0}
            ],
            "answer": "Split the task into two sub-tasks so both can contribute",
            "metric": "team_conflict",
            "difficulty": "hard",
            "ai_interpretation_notes": "Measures dispute resolution and cooperative leadership."
        },
        {
            "key": "adaptive_social_planning",
            "type": "choice",
            "domain": "social",
            "component": "adaptive",
            "title": {"English": "Animal Shelter Drive", "Hindi": "पशु आश्रय अभियान"},
            "prompt": {
                "English": "Your school wants to raise money to help a local animal shelter. What is the best way to organize it?",
                "Hindi": "आपका स्कूल स्थानीय पशु आश्रय की मदद के लिए पैसे जुटाना चाहता है। इसे व्यवस्थित करने का सबसे अच्छा तरीका क्या है?"
            },
            "options": [
                {"label": {"English": "Create student teams for advertising, collection, and event planning", "Hindi": "विज्ञापन, संग्रह और कार्यक्रम योजना के लिए छात्रों की टीमें बनाएं"}, "value": 4},
                {"label": {"English": "Ask the school principal to pay all the money directly", "Hindi": "स्कूल के प्रधानाचार्य से सारा पैसा सीधे देने के लिए कहें"}, "value": 2},
                {"label": {"English": "Stand at the school gate and shout for donations from passengers", "Hindi": "स्कूल के गेट पर खड़े होकर आने-जाने वालों से दान के लिए चिल्लाएं"}, "value": 1},
                {"label": {"English": "Do nothing and hope someone else helps them", "Hindi": "कुछ न करें और आशा करें कि कोई और उनकी मदद करेगा"}, "value": 0}
            ],
            "answer": "Create student teams for advertising, collection, and event planning",
            "metric": "group_planning",
            "difficulty": "hard",
            "ai_interpretation_notes": "Measures task organization and community leadership."
        },
        # --- INTRAPERSONAL & REFLECTIVE ---
        {
            "key": "adaptive_intrapersonal_reflection",
            "type": "choice",
            "domain": "intrapersonal",
            "component": "adaptive",
            "title": {"English": "Competition Failure", "Hindi": "प्रतियोगिता में असफलता"},
            "prompt": {
                "English": "You lost a school competition that you practiced very hard for. What is your reaction?",
                "Hindi": "आप एक स्कूल प्रतियोगिता हार गए जिसके लिए आपने बहुत मेहनत की थी। आपकी क्या प्रतिक्रिया होगी?"
            },
            "options": [
                {"label": {"English": "Think about where you can improve and ask for feedback", "Hindi": "सोचें कि आप कहाँ सुधार कर सकते हैं और प्रतिक्रिया (feedback) मांगें"}, "value": 4},
                {"label": {"English": "Decide that the competition was unfair and biased", "Hindi": "निर्णय लें कि प्रतियोगिता अनुचित और पक्षपाती थी"}, "value": 2},
                {"label": {"English": "Feel sad and decide to never enter any competition again", "Hindi": "दुखी महसूस करें और फिर कभी किसी प्रतियोगिता में भाग न लेने का निर्णय लें"}, "value": 1},
                {"label": {"English": "Blame the judges for your loss", "Hindi": "अपनी हार के लिए जजों को दोष दें"}, "value": 0}
            ],
            "answer": "Think about where you can improve and ask for feedback",
            "metric": "resilience",
            "difficulty": "hard",
            "ai_interpretation_notes": "Growth mindset and feedback resilience."
        },
        {
            "key": "adaptive_intrapersonal_goals",
            "type": "choice",
            "domain": "intrapersonal",
            "component": "adaptive",
            "title": {"English": "Improving Grades", "Hindi": "ग्रेड में सुधार"},
            "prompt": {
                "English": "You want to improve your school grades this term. What is the most effective approach?",
                "Hindi": "आप इस सत्र में अपने स्कूल के ग्रेड में सुधार करना चाहते हैं। सबसे प्रभावी तरीका क्या है?"
            },
            "options": [
                {"label": {"English": "Write weekly study goals, track hours, and solve practice questions", "Hindi": "साप्ताहिक अध्ययन लक्ष्य लिखें, घंटों को ट्रैक करें, और अभ्यास प्रश्नों को हल करें"}, "value": 4},
                {"label": {"English": "Promise yourself to study harder without a clear plan", "Hindi": "बिना किसी स्पष्ट योजना के अधिक मेहनत से अध्ययन करने का स्वयं से वादा करें"}, "value": 2},
                {"label": {"English": "Study only the night before the final exams", "Hindi": "केवल अंतिम परीक्षा से ठीक एक रात पहले अध्ययन करें"}, "value": 1},
                {"label": {"English": "Wish for good luck and hope for the best", "Hindi": "अच्छे भाग्य की कामना करें और सर्वोत्तम की आशा करें"}, "value": 0}
            ],
            "answer": "Write weekly study goals, track hours, and solve practice questions",
            "metric": "goal_planning",
            "difficulty": "hard",
            "ai_interpretation_notes": "Goal structuring and self-monitoring logic."
        }
    ]

    # Add Adaptive Questions to bank
    for q in adaptive_questions:
        bank.append(q)

    # Write bank to JSON
    bank_dir = os.path.join(os.path.dirname(__file__), "question_bank")
    os.makedirs(bank_dir, exist_ok=True)
    bank_path = os.path.join(bank_dir, "extended_bank.json")
    
    with open(bank_path, "w", encoding="utf-8") as f:
        json.dump(bank, f, ensure_ascii=False, indent=2)
        
    print(f"Successfully generated {len(bank)} items in {bank_path}.")

if __name__ == "__main__":
    generate_bank()

import os
import json

def generate_bank():
    print("Generating GOAT V4 assessment bank...")
    bank = []

    # -------------------------------------------------------------
    # SECTION 1: DISCOVERY PHASE (16 questions, balanced domains)
    # -------------------------------------------------------------
    discovery_questions = [
        {
            "id": "1",
            "en_q": "You get one free afternoon. What would you most like to do?",
            "hi_q": "तुम्हें एक खाली दोपहर मिलती है। तुम सबसे ज़्यादा क्या करना चाहोगे?",
            "options": [
                {"en": "Tell or write a story", "hi": "कहानी सुनाना या लिखना", "domain": "language"},
                {"en": "Draw, paint, or sketch", "hi": "चित्र बनाना, रंग भरना या स्केच बनाना", "domain": "creative"},
                {"en": "Solve a tricky math puzzle", "hi": "गणित की पहेली हल करना", "domain": "logical"},
                {"en": "Build a cardboard model", "hi": "गत्ते का मॉडल बनाना", "domain": "spatial"}
            ]
        },
        {
            "id": "2",
            "en_q": "If you could join a school club, which one would you choose?",
            "hi_q": "यदि तुम किसी स्कूल क्लब में शामिल हो सकते, तो तुम किसे चुनते?",
            "options": [
                {"en": "Running and sports club", "hi": "दौड़-भाग और खेल क्लब", "domain": "kinesthetic"},
                {"en": "Plant and garden care club", "hi": "पौधों और बगीचे की देखभाल क्लब", "domain": "naturalist"},
                {"en": "Group game and planning club", "hi": "समूह खेल और योजना क्लब", "domain": "social"},
                {"en": "Quiet reading and thinking club", "hi": "शांत पढ़ने और सोचने का क्लब", "domain": "intrapersonal"}
            ]
        },
        {
            "id": "3",
            "en_q": "Your teacher asks you to help with a task. What sounds most fun?",
            "hi_q": "तुम्हारी शिक्षिका तुम्हें किसी काम में मदद करने के लिए कहती हैं। तुम्हें क्या करने में सबसे ज़्यादा मज़ा आएगा?",
            "options": [
                {"en": "Write a classroom newsletter", "hi": "कक्षा का समाचार पत्र लिखना", "domain": "language"},
                {"en": "Decorate the classroom walls", "hi": "कक्षा की दीवारों को सजाना", "domain": "creative"},
                {"en": "Count and organize school books", "hi": "स्कूल की किताबों को गिनना और व्यवस्थित करना", "domain": "logical"},
                {"en": "Fix a broken pencil sharpener", "hi": "टूटे हुए पेंसिल शार्पनर को ठीक करना", "domain": "spatial"}
            ]
        },
        {
            "id": "4",
            "en_q": "What is your favorite way to spend a rainy day?",
            "hi_q": "बारिश के दिन समय बिताने का तुम्हारा पसंदीदा तरीका क्या है?",
            "options": [
                {"en": "Practice indoor dance or exercises", "hi": "घर के अंदर नृत्य या व्यायाम का अभ्यास करना", "domain": "kinesthetic"},
                {"en": "Watch rain fall and look for birds", "hi": "बारिश गिरते देखना और पक्षियों को खोजना", "domain": "naturalist"},
                {"en": "Play board games with friends", "hi": "दोस्तों के साथ बोर्ड गेम खेलना", "domain": "social"},
                {"en": "Write in a secret diary", "hi": "एक गुप्त डायरी में लिखना", "domain": "intrapersonal"}
            ]
        },
        {
            "id": "5",
            "en_q": "If you could invent a new machine, what would it do?",
            "hi_q": "यदि तुम एक नई मशीन का आविष्कार कर सकते, तो वह क्या करती?",
            "options": [
                {"en": "Translate any language", "hi": "किसी भी भाषा का अनुवाद करना", "domain": "language"},
                {"en": "Make beautiful color patterns", "hi": "सुंदर रंगीन पैटर्न बनाना", "domain": "creative"},
                {"en": "Sort items by size and weight", "hi": "वस्तुओं को आकार और वजन के अनुसार छांटना", "domain": "logical"},
                {"en": "Build toy houses automatically", "hi": "खिलौना घर अपने आप बनाना", "domain": "spatial"}
            ]
        },
        {
            "id": "6",
            "en_q": "You are visiting a big park. What do you do first?",
            "hi_q": "तुम एक बड़े पार्क में जा रहे हो। तुम सबसे पहले क्या करते हो?",
            "options": [
                {"en": "Climb a tree or race around", "hi": "पेड़ पर चढ़ना या दौड़ लगाना", "domain": "kinesthetic"},
                {"en": "Collect colorful leaves and stones", "hi": "रंगीन पत्तियां और पत्थर इकट्ठा करना", "domain": "naturalist"},
                {"en": "Meet new friends and play tag", "hi": "नए दोस्तों से मिलना और पकड़म-पकड़ाई खेलना", "domain": "social"},
                {"en": "Sit under a tree and think", "hi": "पेड़ के नीचे बैठना और सोचना", "domain": "intrapersonal"}
            ]
        },
        {
            "id": "7",
            "en_q": "What kind of book would you pick from the library?",
            "hi_q": "तुम पुस्तकालय से किस तरह की किताब चुनोगे?",
            "options": [
                {"en": "A book of fun stories", "hi": "मजेदार कहानियों की किताब", "domain": "language"},
                {"en": "A book of art ideas and drawing", "hi": "कला के विचारों और ड्राइंग की किताब", "domain": "creative"},
                {"en": "A book of riddles and brain teasers", "hi": "पहेलियों और दिमाग के खेलों की किताब", "domain": "logical"},
                {"en": "A book on how buildings are made", "hi": "इमारतें कैसे बनती हैं, इस पर किताब", "domain": "spatial"}
            ]
        },
        {
            "id": "8",
            "en_q": "If you could watch any show, what would it be about?",
            "hi_q": "यदि तुम कोई शो देख सकते, तो वह किसके बारे में होता?",
            "options": [
                {"en": "High-energy sports or stunts", "hi": "ऊर्जा से भरपूर खेल या स्टंट", "domain": "kinesthetic"},
                {"en": "Animals living in the forest", "hi": "जंगल में रहने वाले जानवर", "domain": "naturalist"},
                {"en": "How teams work together to win", "hi": "जीतने के लिए टीमें मिलकर कैसे काम करती हैं", "domain": "social"},
                {"en": "A person's quiet journey to success", "hi": "सफलता के लिए किसी व्यक्ति की शांत यात्रा", "domain": "intrapersonal"}
            ]
        },
        {
            "id": "9",
            "en_q": "What is your favorite school subject activity?",
            "hi_q": "तुम्हारी पसंदीदा स्कूल विषय गतिविधि कौन सी है?",
            "options": [
                {"en": "Giving a speech or reading aloud", "hi": "भाषण देना या ज़ोर से पढ़ना", "domain": "language"},
                {"en": "Painting or making paper crafts", "hi": "पेंटिंग करना या कागज़ के शिल्प बनाना", "domain": "creative"},
                {"en": "Solving math logic questions", "hi": "गणित के तर्क वाले प्रश्नों को हल करना", "domain": "logical"},
                {"en": "Drawing maps or 3D boxes", "hi": "नक्शे या 3D बक्से बनाना", "domain": "spatial"}
            ]
        },
        {
            "id": "10",
            "en_q": "Which of these gifts would you like to receive?",
            "hi_q": "तुम इनमें से कौन सा उपहार प्राप्त करना चाहोगे?",
            "options": [
                {"en": "A football or skipping rope", "hi": "एक फुटबॉल या कूदने वाली रस्सी", "domain": "kinesthetic"},
                {"en": "A small plant or pet fish", "hi": "एक छोटा पौधा या पालतू मछली", "domain": "naturalist"},
                {"en": "A multiplayer board game", "hi": "कई खिलाड़ियों वाला बोर्ड गेम", "domain": "social"},
                {"en": "A notebook with a lock", "hi": "ताले वाली एक नोटबुक", "domain": "intrapersonal"}
            ]
        },
        {
            "id": "11",
            "en_q": "When working on a team project, what is your role?",
            "hi_q": "जब आप एक टीम प्रोजेक्ट पर काम करते हैं, तो आपकी भूमिका क्या होती है?",
            "options": [
                {"en": "Writing down and presenting the ideas", "hi": "विचारों को लिखना और प्रस्तुत करना", "domain": "language"},
                {"en": "Designing unique logos and colors", "hi": "अनोखे लोगो और रंग डिजाइन करना", "domain": "creative"},
                {"en": "Checking facts and finding errors", "hi": "तथ्यों की जांच करना और गलतियां खोजना", "domain": "logical"},
                {"en": "Assembling the project board", "hi": "प्रोजेक्ट बोर्ड को जोड़ना", "domain": "spatial"}
            ]
        },
        {
            "id": "12",
            "en_q": "What would you like to learn in a workshop?",
            "hi_q": "तुम एक कार्यशाला में क्या सीखना चाहोगे?",
            "options": [
                {"en": "Karate blocks or gymnastics moves", "hi": "कराटे ब्लॉक या जिम्नास्टिक मूव्स", "domain": "kinesthetic"},
                {"en": "Identifying birds and insects", "hi": "पक्षियों और कीड़ों की पहचान करना", "domain": "naturalist"},
                {"en": "Leading groups and solving disputes", "hi": "समूहों का नेतृत्व करना और विवादों को सुलझाना", "domain": "social"},
                {"en": "Setting goals and planning time", "hi": "लक्ष्य निर्धारित करना और समय की योजना बनाना", "domain": "intrapersonal"}
            ]
        },
        {
            "id": "13",
            "en_q": "You see an empty box in the classroom. What do you think?",
            "hi_q": "तुम कक्षा में एक खाली डिब्बा देखते हो। तुम क्या सोचते हो?",
            "options": [
                {"en": "Let's write stories to put inside", "hi": "चलो इसके अंदर रखने के लिए कहानियां लिखते हैं", "domain": "language"},
                {"en": "Let's paint it with bright colors", "hi": "चलो इसे चमकीले रंगों से पेंट करते हैं", "domain": "creative"},
                {"en": "Let's see how many books it can hold", "hi": "चलो देखते हैं कि इसमें कितनी किताबें आ सकती हैं", "domain": "logical"},
                {"en": "Let's build a toy castle with it", "hi": "चलो इससे एक खिलौना किला बनाते हैं", "domain": "spatial"}
            ]
        },
        {
            "id": "14",
            "en_q": "You hear music playing. What do you naturally do?",
            "hi_q": "तुम संगीत बजता हुआ सुनते हो। तुम स्वाभाविक रूप से क्या करते हो?",
            "options": [
                {"en": "Start dancing or tapping your feet", "hi": "नाचना या पैर थपथपाना शुरू करना", "domain": "kinesthetic"},
                {"en": "Listen to find sounds like birds or rain", "hi": "पक्षी या बारिश जैसी आवाजें खोजना", "domain": "naturalist"},
                {"en": "Sing along with a group of friends", "hi": "दोस्तों के समूह के साथ मिलकर गाना", "domain": "social"},
                {"en": "Close your eyes and enjoy it quietly", "hi": "अपनी आँखें बंद करना और शांति से इसका आनंद लेना", "domain": "intrapersonal"}
            ]
        },
        {
            "id": "15",
            "en_q": "If you had a magic wand, what would you make?",
            "hi_q": "यदि तुम्हारे पास एक जादुई छड़ी होती, तो तुम क्या बनाते?",
            "options": [
                {"en": "A book that writes itself", "hi": "एक किताब जो अपने आप लिखती है", "domain": "language"},
                {"en": "A picture that changes colors", "hi": "एक चित्र जो रंग बदलता है", "domain": "creative"},
                {"en": "A puzzle that never ends", "hi": "एक पहेली जो कभी खत्म नहीं होती", "domain": "logical"},
                {"en": "A bridge that opens and closes", "hi": "एक पुल जो खुलता और बंद होता है", "domain": "spatial"}
            ]
        },
        {
            "id": "16",
            "en_q": "What is the most exciting thing to do at a village fair?",
            "hi_q": "गांव के मेले में करने के लिए सबसे रोमांचक काम क्या है?",
            "options": [
                {"en": "Ride the giant wheel or run around", "hi": "विशाल झूले की सवारी करना या चारों ओर दौड़ना", "domain": "kinesthetic"},
                {"en": "Look at the cows, goats, and birds", "hi": "गायों, बकरियों और पक्षियों को देखना", "domain": "naturalist"},
                {"en": "Help run a game stall for kids", "hi": "बच्चों के लिए गेम स्टॉल चलाने में मदद करना", "domain": "social"},
                {"en": "Find a quiet corner to watch the crowd", "hi": "भीड़ को देखने के लिए एक शांत कोना खोजना", "domain": "intrapersonal"}
            ]
        }
    ]

    for d in discovery_questions:
        opts = []
        for idx, o in enumerate(d["options"]):
            opts.append({
                "label": {"English": o["en"], "Hindi": o["hi"]},
                "value": idx,  # Frontend sends index directly
                "mapping": {o["domain"]: 4},
                "riasec": "Social" # Fallback static value
            })
        bank.append({
            "key": f"q_discovery_{d['id']}",
            "type": "choice",
            "domain": d["options"][0]["domain"], # compatibility key
            "component": "discovery_preference",
            "title": {"English": f"Discovery Question {d['id']}", "Hindi": f"खोज प्रश्न {d['id']}"},
            "prompt": {"English": d["en_q"], "Hindi": d["hi_q"]},
            "options": opts,
            "metric": "preference",
            "difficulty": "easy",
            "ai_interpretation_notes": "Discovery preference measuring spontaneous alignment."
        })

    # -------------------------------------------------------------
    # SECTION 2: DEEP ASSESSMENT PHASE (32 puzzles, 4 per domain)
    # -------------------------------------------------------------
    deep_puzzles = [
        # --- LANGUAGE & COMMUNICATION ---
        {
            "key": "language_race",
            "type": "order_steps",
            "domain": "language",
            "component": "performance_1",
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
            "key": "language_pic_interpret",
            "type": "choice",
            "domain": "language",
            "component": "performance_2",
            "title": {"English": "Picture Clues", "Hindi": "चित्र के सुराग"},
            "prompt": {
                "English": "A dog is barking at a cat stuck in a tall tree. A boy runs, gets a wooden ladder, and helps the cat climb down. What is this picture showing?",
                "Hindi": "एक कुत्ता पेड़ पर फंसी बिल्ली पर भौंक रहा है। एक लड़का लकड़ी की सीढ़ी लाता है और बिल्ली को नीचे उतारने में मदद करता है। यह चित्र क्या दिखाता है?"
            },
            "options": [
                {"label": {"English": "A boy helping an animal in trouble", "Hindi": "एक लड़का मुसीबत में फंसे जानवर की मदद कर रहा है"}, "value": 4},
                {"label": {"English": "A cat playing on a tree branch", "Hindi": "एक बिल्ली पेड़ की शाखा पर खेल रही है"}, "value": 1},
                {"label": {"English": "A dog chasing a boy with a ladder", "Hindi": "एक कुत्ता सीढ़ी वाले लड़के का पीछा कर रहा है"}, "value": 2},
                {"label": {"English": "A boy building a wooden ladder", "Hindi": "एक लड़का लकड़ी की सीढ़ी बना रहा है"}, "value": 0}
            ],
            "answer": "A boy helping an animal in trouble",
            "metric": "correctness",
            "difficulty": "easy",
            "ai_interpretation_notes": "Picture interpretation and comprehension task."
        },
        {
            "key": "language_explain_game",
            "type": "choice",
            "domain": "language",
            "component": "situational",
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
        {
            "key": "language_story_words",
            "type": "open_ended",
            "domain": "language",
            "component": "open_response",
            "title": {"English": "Three Words Story", "Hindi": "तीन शब्दों की कहानी"},
            "prompt": {
                "English": "Use these 3 words to write a short, fun story: dog, box, balloon.",
                "Hindi": "इन 3 शब्दों का उपयोग करके एक छोटी और मजेदार कहानी लिखें: कुत्ता (dog), डिब्बा (box), गुब्बारा (balloon)।"
            },
            "metric": "narrative_expression",
            "difficulty": "adaptive",
            "ai_interpretation_notes": "Measures story fluency, word usage, and imagination."
        },

        # --- CREATIVE & ARTISTIC ---
        {
            "key": "creative_circles",
            "type": "idea_list",
            "domain": "creative",
            "component": "performance_1",
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
            "key": "creative_cloud",
            "type": "idea_list",
            "domain": "creative",
            "component": "performance_2",
            "title": {"English": "Teacup Cloud", "Hindi": "कप जैसा बादल"},
            "prompt": {
                "English": "You see a cloud shaped like a giant teacup. Write down 3 unusual or magical things that could pour out of it!",
                "Hindi": "आप एक बड़े चाय के कप के आकार का बादल देखते हैं। कल्पना करें और 3 अनोखी या जादुई चीजें लिखें जो इसमें से गिर सकती हैं!"
            },
            "minIdeas": 3,
            "metric": "fluency",
            "difficulty": "adaptive",
            "ai_interpretation_notes": "Divergent thinking and semantic flexibility."
        },
        {
            "key": "creative_box_situational",
            "type": "choice",
            "domain": "creative",
            "component": "situational",
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
        {
            "key": "creative_toy_invent",
            "type": "open_ended",
            "domain": "creative",
            "component": "open_response",
            "title": {"English": "Invent a Toy", "Hindi": "एक खिलौना बनाएं"},
            "prompt": {
                "English": "Describe an entirely new toy you would invent. What does it look like and how do children play with it?",
                "Hindi": "एक बिल्कुल नए खिलौने के बारे में बताएं जिसे आप बनाना चाहते हैं। वह कैसा दिखता है और बच्चे उससे कैसे खेलते हैं?"
            },
            "metric": "narrative_expression",
            "difficulty": "adaptive",
            "ai_interpretation_notes": "Measures product concept fluency and visual imagination."
        },

        # --- LOGICAL & ANALYTICAL ---
        {
            "key": "logical_lock",
            "type": "choice",
            "domain": "logical",
            "component": "performance_1",
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
            "difficulty": "medium",
            "ai_interpretation_notes": "Logical sequencing correctness."
        },
        {
            "key": "logical_legs",
            "type": "choice",
            "domain": "logical",
            "component": "performance_2",
            "title": {"English": "Animal Leg Riddle", "Hindi": "जानवरों के पैरों की पहेली"},
            "prompt": {
                "English": "A logic game matches animals to numbers: Cat is 4, Spider is 8, Ant is 6. What represents a Snake?",
                "Hindi": "एक तर्क खेल में बिल्ली (Cat) 4 है, मकड़ी (Spider) 8 है, चींटी (Ant) 6 है। सांप (Snake) का नंबर क्या होगा?"
            },
            "options": [
                {"label": {"English": "4", "Hindi": "4"}, "value": 0},
                {"label": {"English": "0", "Hindi": "0"}, "value": 4},
                {"label": {"English": "2", "Hindi": "2"}, "value": 0},
                {"label": {"English": "6", "Hindi": "6"}, "value": 0}
            ],
            "answer": "0",
            "metric": "correctness",
            "difficulty": "medium",
            "ai_interpretation_notes": "Visual inductive classification reasoning."
        },
        {
            "key": "logical_bottles_situational",
            "type": "choice",
            "domain": "logical",
            "component": "situational",
            "title": {"English": "Lost Bottles", "Hindi": "खोई हुई बोतलें"},
            "prompt": {
                "English": "Students at school keep losing their water bottles on the playground. What is the most effective way to solve this?",
                "Hindi": "स्कूल के मैदान में छात्र अपनी पानी की बोतलें भूल जाते हैं। इसे हल करने का सबसे कारगर तरीका क्या है?"
            },
            "options": [
                {"label": {"English": "Make a designated wooden bottle stand near the playground entrance", "Hindi": "खेल के मैदान के प्रवेश द्वार के पास एक लकड़ी का बोतल स्टैंड बनाएं"}, "value": 4},
                {"label": {"English": "Tell children to stop drinking water during school hours", "Hindi": "बच्चों से कहें कि वे स्कूल के समय पानी पीना बंद कर दें"}, "value": 1},
                {"label": {"English": "Fine students who lose their bottles", "Hindi": "बोतल खोने वाले छात्रों पर जुर्माना लगाएं"}, "value": 2},
                {"label": {"English": "Do nothing and let parents buy new bottles", "Hindi": "कुछ न करें और माता-पिता को नई बोतलें खरीदने दें"}, "value": 0}
            ],
            "answer": "Make a designated wooden bottle stand near the playground entrance",
            "metric": "correctness",
            "difficulty": "easy",
            "ai_interpretation_notes": "Measures practical logic and systematic problem solving."
        },
        {
            "key": "logical_queue_solution",
            "type": "open_ended",
            "domain": "logical",
            "component": "open_response",
            "title": {"English": "Water Tap Queue", "Hindi": "पानी की कतार"},
            "prompt": {
                "English": "During lunch break, there is a very long, messy queue at the school water tap. How would you solve this problem so everyone gets water quickly?",
                "Hindi": "लंच ब्रेक के दौरान स्कूल के नल पर पानी के लिए बहुत लंबी और अस्त-व्यस्त कतार लग जाती है। आप इस समस्या को कैसे हल करेंगे ताकि सभी को जल्दी पानी मिल सके?"
            },
            "metric": "narrative_expression",
            "difficulty": "adaptive",
            "ai_interpretation_notes": "Measures structural planning and systematic logical thinking."
        },

        # --- SPATIAL & MAKING ---
        {
            "key": "spatial_shape_match",
            "type": "choice",
            "domain": "spatial",
            "component": "performance_1",
            "title": {"English": "Missing Corner Piece", "Hindi": "गायब कोना"},
            "prompt": {
                "English": "A square wooden board is missing a L-shaped corner piece. Which piece will fit perfectly to make it a square again?",
                "Hindi": "एक चौकोर लकड़ी के बोर्ड में एक L-आकार का कोना गायब है। इसे फिर से पूरा वर्ग बनाने के लिए कौन सा टुकड़ा बिल्कुल फिट होगा?"
            },
            "options": [
                {"label": {"English": "A small L-shaped block matching the size of the corner", "Hindi": "एक छोटा L-आकार का ब्लॉक जो कोने के आकार का हो"}, "value": 4},
                {"label": {"English": "A long straight thin block", "Hindi": "एक लंबा सीधा पतला ब्लॉक"}, "value": 0},
                {"label": {"English": "A round circle block", "Hindi": "एक गोल वृत्त ब्लॉक"}, "value": 0},
                {"label": {"English": "A large triangle block", "Hindi": "एक बड़ा त्रिकोण ब्लॉक"}, "value": 0}
            ],
            "answer": "A small L-shaped block matching the size of the corner",
            "metric": "correctness",
            "difficulty": "easy",
            "ai_interpretation_notes": "Mental geometry and spatial matching."
        },
        {
            "key": "spatial_clock",
            "type": "choice",
            "domain": "spatial",
            "component": "performance_2",
            "title": {"English": "Clock Hand Rotation", "Hindi": "सुई का घूमना"},
            "prompt": {
                "English": "A pointer moves: first UP, then RIGHT, then DOWN. Where will it point next?",
                "Hindi": "एक सुई घूमती है: पहले ऊपर, फिर दाएं, फिर नीचे। इसके बाद यह किस दिशा में होगी?"
            },
            "options": [
                {"label": {"English": "UP", "Hindi": "ऊपर"}, "value": 0},
                {"label": {"English": "RIGHT", "Hindi": "दाएं"}, "value": 0},
                {"label": {"English": "DOWN", "Hindi": "नीचे"}, "value": 0},
                {"label": {"English": "LEFT", "Hindi": "बाएं"}, "value": 4}
            ],
            "answer": "LEFT",
            "metric": "correctness",
            "difficulty": "easy",
            "ai_interpretation_notes": "Mental rotation tracking."
        },
        {
            "key": "spatial_room_situational",
            "type": "choice",
            "domain": "spatial",
            "component": "situational",
            "title": {"English": "Small Room Plan", "Hindi": "छोटे कमरे की योजना"},
            "prompt": {
                "English": "You have a very small room and need to fit a bed, a desk, and a bookshelf. How should you arrange them?",
                "Hindi": "आपके पास एक बहुत छोटा कमरा है और उसमें एक बिस्तर, एक मेज और एक बुकशेल्फ़ रखना है। आपको उन्हें कैसे व्यवस्थित करना चाहिए?"
            },
            "options": [
                {"label": {"English": "Place the bed along the wall and place the desk under a high bookshelf", "Hindi": "बिस्तर को दीवार के साथ लगाएं और मेज को ऊंचे बुकशेल्फ़ के नीचे रखें"}, "value": 4},
                {"label": {"English": "Put the bed in the middle of the room so no other furniture fits", "Hindi": "बिस्तर को कमरे के बीच में रखें ताकि कोई अन्य फर्नीचर फिट न हो सके"}, "value": 1},
                {"label": {"English": "Leave the desk outside the room on the corridor", "Hindi": "मेज को कमरे के बाहर कॉरिडोर में छोड़ दें"}, "value": 2},
                {"label": {"English": "Stack the bed on top of the desk directly", "Hindi": "बिस्तर को सीधे मेज के ऊपर रख दें"}, "value": 0}
            ],
            "answer": "Place the bed along the wall and place the desk under a high bookshelf",
            "metric": "correctness",
            "difficulty": "easy",
            "ai_interpretation_notes": "Measures 3D spatial arranging and structural design logic."
        },
        {
            "key": "spatial_treehouse_design",
            "type": "open_ended",
            "domain": "spatial",
            "component": "open_response",
            "title": {"English": "Treehouse Design", "Hindi": "ट्रीहाउस डिजाइन"},
            "prompt": {
                "English": "You want to design a strong wooden treehouse. Describe what shape it will be, and how you will secure it to the tree so it does not fall.",
                "Hindi": "आप एक मजबूत लकड़ी का ट्रीहाउस (पेड़ पर घर) बनाना चाहते हैं। बताएं कि इसका आकार कैसा होगा, और आप इसे पेड़ से कैसे सुरक्षित बांधेंगे ताकि यह गिरे नहीं।"
            },
            "metric": "narrative_expression",
            "difficulty": "adaptive",
            "ai_interpretation_notes": "Measures 3D visualization, physical balance, and construction reasoning."
        },

        # --- KINESTHETIC & PHYSICAL ---
        {
            "key": "visualizer_memory_grid",
            "type": "memory_grid",
            "domain": "kinesthetic",
            "component": "performance_1",
            "title": {"English": "Flashing Stars", "Hindi": "चमकते सितारे"},
            "prompt": {
                "English": "Watch the flashing pattern on the grid, then tap the same squares in order.",
                "Hindi": "ग्रिड पर चमकते पैटर्न को देखें, फिर उसी क्रम में उन खानों को छुएं।"
            },
            "gridSize": 9,
            "highlights": [0, 2, 6, 8],
            "revealMs": 2000,
            "metric": "memory_span",
            "difficulty": "medium",
            "ai_interpretation_notes": "Motor sequencing and spatial visual working memory."
        },
        {
            "key": "kinesthetic_catch",
            "type": "choice",
            "domain": "kinesthetic",
            "component": "performance_2",
            "title": {"English": "Catching a Ball", "Hindi": "गेंद पकड़ना"},
            "prompt": {
                "English": "A high leather ball is falling fast toward you. What is the safest way to catch it without hurting your hands?",
                "Hindi": "एक ऊंची चमड़े की गेंद आपकी ओर तेजी से गिर रही है। हाथों को चोट पहुंचाए बिना इसे पकड़ने का सबसे सुरक्षित तरीका क्या है?"
            },
            "options": [
                {"label": {"English": "Cup your hands together and pull them back slightly as you catch the ball", "Hindi": "दोनों हाथों को एक साथ कप के आकार में लाएं और गेंद पकड़ते समय उन्हें थोड़ा पीछे खींचें"}, "value": 4},
                {"label": {"English": "Keep your hands stiff and straight and block the ball", "Hindi": "हाथों को सीधा और सख्त रखें और गेंद को रोकें"}, "value": 1},
                {"label": {"English": "Try to catch it with only one hand stretched out high", "Hindi": "केवल एक हाथ को ऊपर फैलाकर इसे पकड़ने का प्रयास करें"}, "value": 2},
                {"label": {"English": "Close your eyes and let the ball hit your chest", "Hindi": "अपनी आंखें बंद करें और गेंद को अपनी छाती से टकराने दें"}, "value": 0}
            ],
            "answer": "Cup your hands together and pull them back slightly as you catch the ball",
            "metric": "correctness",
            "difficulty": "easy",
            "ai_interpretation_notes": "Biomechanical coordination and impact absorption logic."
        },
        {
            "key": "kinesthetic_team_losing",
            "type": "choice",
            "domain": "kinesthetic",
            "component": "situational",
            "title": {"English": "Tired Teammate", "Hindi": "थका हुआ साथी"},
            "prompt": {
                "English": "During a match, your teammate is running very slowly because they are tired. What do you do?",
                "Hindi": "एक मैच के दौरान, आपका साथी खिलाड़ी थक जाने के कारण बहुत धीरे दौड़ रहा है। आप क्या करेंगे?"
            },
            "options": [
                {"label": {"English": "Pass the ball to another open player and adjust your running path to support them", "Hindi": "गेंद को दूसरे खाली खिलाड़ी को पास करें और उनकी मदद के लिए अपने दौड़ने का रास्ता बदलें"}, "value": 4},
                {"label": {"English": "Shout at them to run faster and get angry", "Hindi": "उन पर तेजी से दौड़ने के लिए चिल्लाएं और गुस्सा करें"}, "value": 1},
                {"label": {"English": "Stop running yourself and watch the match", "Hindi": "खुद दौड़ना बंद कर दें और मैच देखें"}, "value": 2},
                {"label": {"English": "Ask the referee to stop the match immediately", "Hindi": "रेफरी से मैच को तुरंत रोकने के लिए कहें"}, "value": 0}
            ],
            "answer": "Pass the ball to another open player and adjust your running path to support them",
            "metric": "correctness",
            "difficulty": "easy",
            "ai_interpretation_notes": "Situational physical play tactics and sportsmanship."
        },
        {
            "key": "kinesthetic_learn_sport",
            "type": "open_ended",
            "domain": "kinesthetic",
            "component": "open_response",
            "title": {"English": "Learn a Sport", "Hindi": "नया खेल सीखना"},
            "prompt": {
                "English": "Imagine a new physical game or sport you have never played before. Describe step-by-step how you would practice to learn and master it.",
                "Hindi": "कल्पना कीजिए कि एक नया खेल या स्पोर्ट्स है जिसे आपने पहले कभी नहीं खेला है। इसे सीखने और माहिर होने के लिए आप कदम-दर-कदम कैसे अभ्यास करेंगे, लिखें।"
            },
            "metric": "narrative_expression",
            "difficulty": "adaptive",
            "ai_interpretation_notes": "Measures physical learning planning, muscle memory awareness, and motor regulation."
        },

        # --- NATURALIST & ENVIRONMENTAL ---
        {
            "key": "naturalist_weather",
            "type": "choice",
            "domain": "naturalist",
            "component": "performance_1",
            "title": {"English": "Rain Signs", "Hindi": "बारिश के संकेत"},
            "prompt": {
                "English": "You notice that the wind is blowing very cold, dark clouds are covering the sun, and swallow birds are flying low to the ground. What is most likely to happen next?",
                "Hindi": "आप देखते हैं कि हवा बहुत ठंडी चल रही है, काले बादल सूरज को ढक रहे हैं, और पक्षी जमीन के बहुत करीब उड़ रहे हैं। इसके बाद क्या होने की सबसे अधिक संभावना है?"
            },
            "options": [
                {"label": {"English": "It will rain heavily soon", "Hindi": "जल्द ही भारी बारिश होगी"}, "value": 4},
                {"label": {"English": "It will become a very hot and sunny day", "Hindi": "बहुत गर्म और धूप वाला दिन हो जाएगा"}, "value": 1},
                {"label": {"English": "A sandstorm will clear all the clouds", "Hindi": "धूल भरी आंधी सभी बादलों को साफ कर देगी"}, "value": 2},
                {"label": {"English": "Nothing will change", "Hindi": "कुछ नहीं बदलेगा"}, "value": 0}
            ],
            "answer": "It will rain heavily soon",
            "metric": "correctness",
            "difficulty": "easy",
            "ai_interpretation_notes": "Nature pattern deduction."
        },
        {
            "key": "naturalist_plants",
            "type": "choice",
            "domain": "naturalist",
            "component": "performance_2",
            "title": {"English": "Dry Plant Care", "Hindi": "सूखे पौधे की देखभाल"},
            "prompt": {
                "English": "Two identical green potted plants are placed in different spots. Plant A has dry soil and drooping yellow leaves. Plant B has moist soil and bright green leaves. What does Plant A need?",
                "Hindi": "दो समान गमले वाले पौधे अलग स्थानों पर रखे हैं। पौधे A की मिट्टी सूखी और पत्तियां पीली हैं। पौधे B की मिट्टी नम और पत्तियां हरी हैं। पौधे A को क्या चाहिए?"
            },
            "options": [
                {"label": {"English": "Water and a moderate amount of sunlight", "Hindi": "पानी और मध्यम मात्रा में धूप"}, "value": 4},
                {"label": {"English": "More dry fertilizer only", "Hindi": "केवल अधिक सूखा उर्वरक"}, "value": 1},
                {"label": {"English": "Moving to a dark closed cupboard", "Hindi": "अंधेरे बंद अलमारी में ले जाना"}, "value": 2},
                {"label": {"English": "Plucking all its yellow leaves off", "Hindi": "उसकी सभी पीली पत्तियों को तोड़ देना"}, "value": 0}
            ],
            "answer": "Water and a moderate amount of sunlight",
            "metric": "correctness",
            "difficulty": "easy",
            "ai_interpretation_notes": "Living systems observation and care diagnosis."
        },
        {
            "key": "naturalist_sick_plant",
            "type": "choice",
            "domain": "naturalist",
            "component": "situational",
            "title": {"English": "Sick Classroom Plant", "Hindi": "बीमार पौधा"},
            "prompt": {
                "English": "A vegetable plant in the school garden is looking sick with small insects on its stems. What is the best organic action to take?",
                "Hindi": "स्कूल के बगीचे में एक सब्जी का पौधा बीमार दिख रहा है और उसके तनों पर छोटे कीड़े लगे हैं। सबसे अच्छा जैविक (organic) कदम क्या होगा?"
            },
            "options": [
                {"label": {"English": "Spray it gently with mild neem-soap water and remove the pests", "Hindi": "नीम और साबुन के हल्के पानी का छिड़काव करें और कीड़ों को हटा दें"}, "value": 4},
                {"label": {"English": "Cut the entire plant from the roots and throw it away", "Hindi": "पूरे पौधे को जड़ से काटकर फेंक दें"}, "value": 1},
                {"label": {"English": "Pour strong chemical insect killer on the soil", "Hindi": "मिट्टी पर तेज रासायनिक कीटनाशक डालें"}, "value": 2},
                {"label": {"English": "Do nothing and let the insects eat it", "Hindi": "कुछ न करें और कीड़ों को उसे खाने दें"}, "value": 0}
            ],
            "answer": "Spray it gently with mild neem-soap water and remove the pests",
            "metric": "correctness",
            "difficulty": "easy",
            "ai_interpretation_notes": "Measures naturalist diagnostic action and environmental care."
        },
        {
            "key": "naturalist_notice_nature",
            "type": "open_ended",
            "domain": "naturalist",
            "component": "open_response",
            "title": {"English": "Notice Nature", "Hindi": "प्रकृति में ध्यान देना"},
            "prompt": {
                "English": "Describe something interesting you noticed recently about an animal, bird, insect, or plant in nature. What did you observe?",
                "Hindi": "प्रकृति में किसी जानवर, पक्षी, कीड़े या पौधे के बारे में कुछ दिलचस्प बताएं जो आपने हाल ही में देखा हो। आपने क्या नोटिस किया?"
            },
            "metric": "narrative_expression",
            "difficulty": "adaptive",
            "ai_interpretation_notes": "Measures naturalist sensory observation details and curiosity."
        },

        # --- SOCIAL & LEADERSHIP ---
        {
            "key": "social_planning",
            "type": "choice",
            "domain": "social",
            "component": "performance_1",
            "title": {"English": "Quick Cleanup Plan", "Hindi": "त्वरित सफाई योजना"},
            "prompt": {
                "English": "Your group needs to clean the classroom, make banners, and arrange chairs in 10 minutes. How do you plan to finish?",
                "Hindi": "आपके ग्रुप को 10 मिनट में कक्षा की सफाई करनी है, बैनर बनाने हैं और कुर्सियां व्यवस्थित करनी हैं। आप इसे कैसे पूरा करेंगे?"
            },
            "options": [
                {"label": {"English": "Assign different tasks to small teams based on what they like and do well", "Hindi": "छोटे समूहों को उनकी पसंद और ताकत के अनुसार अलग-अलग काम सौंपेंगे"}, "value": 4},
                {"label": {"English": "Try to do all tasks yourself while everyone else watches", "Hindi": "सभी काम खुद करने की कोशिश करेंगे जबकि बाकी सब देखते रहेंगे"}, "value": 1},
                {"label": {"English": "Let everyone do whatever they want without any plan", "Hindi": "बिना किसी योजना के सभी को जो मन करे करने देंगे"}, "value": 2},
                {"label": {"English": "Wait for the teacher to come and tell you what to do", "Hindi": "शिक्षिका के आने और बताने का इंतजार करेंगे"}, "value": 0}
            ],
            "answer": "Assign different tasks to small teams based on what they like and do well",
            "metric": "correctness",
            "difficulty": "easy",
            "ai_interpretation_notes": "Group task organization and delegation."
        },
        {
            "key": "social_decision",
            "type": "choice",
            "domain": "social",
            "component": "performance_2",
            "title": {"English": "Getting Lost", "Hindi": "रास्ता भटकना"},
            "prompt": {
                "English": "Your group takes a wrong turn during a school walk in a park. Some students start crying. What is your first action?",
                "Hindi": "पार्क में स्कूल की सैर के दौरान आपका ग्रुप गलत रास्ते पर चला जाता है। कुछ बच्चे रोने लगते हैं। आपका पहला कदम क्या होगा?"
            },
            "options": [
                {"label": {"English": "Calm everyone down, ask them to stay together, and look for a familiar path or call the teacher", "Hindi": "सभी को शांत करेंगे, एक साथ रहने को कहेंगे और किसी परिचित रास्ते की तलाश करेंगे या शिक्षिका को बुलाएंगे"}, "value": 4},
                {"label": {"English": "Start crying yourself so others know it is serious", "Hindi": "खुद भी रोना शुरू कर देंगे ताकि दूसरों को पता चले कि यह गंभीर है"}, "value": 1},
                {"label": {"English": "Run away quickly to find the path alone", "Hindi": "अकेले रास्ते की तलाश में तेजी से भाग जाएंगे"}, "value": 2},
                {"label": {"English": "Sit down on the ground and do nothing", "Hindi": "जमीन पर बैठ जाएंगे और कुछ नहीं करेंगे"}, "value": 0}
            ],
            "answer": "Calm everyone down, ask them to stay together, and look for a familiar path or call the teacher",
            "metric": "correctness",
            "difficulty": "easy",
            "ai_interpretation_notes": "Situational peer reassurance and group control."
        },
        {
            "key": "social_conflict_resolution",
            "type": "choice",
            "domain": "social",
            "component": "situational",
            "title": {"English": "Batting Argument", "Hindi": "बल्लेबाजी पर विवाद"},
            "prompt": {
                "English": "Two friends are arguing loudly on the playground about whose turn it is to bat. How would you solve this dispute fairly?",
                "Hindi": "खेल के मैदान में दो दोस्त आपस में इस बात पर बहस कर रहे हैं कि बल्लेबाजी की किसकी बारी है। आप इस विवाद को निष्पक्ष रूप से कैसे सुलझाएंगे?"
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
        {
            "key": "social_helped_others",
            "type": "open_ended",
            "domain": "social",
            "component": "open_response",
            "title": {"English": "Helping a Friend", "Hindi": "दोस्त की मदद"},
            "prompt": {
                "English": "Describe a time when you helped others solve a problem or settle an argument. What was the problem and what did you do?",
                "Hindi": "कोई ऐसा समय बताएं जब आपने दूसरों को किसी समस्या को हल करने या किसी बहस को सुलझाने में मदद की हो। समस्या क्या थी और आपने क्या किया?"
            },
            "metric": "narrative_expression",
            "difficulty": "adaptive",
            "ai_interpretation_notes": "Measures interpersonal empathy, helpful initiative, and relational intelligence."
        },

        # --- INTRAPERSONAL & REFLECTIVE ---
        {
            "key": "intrapersonal_goals",
            "type": "choice",
            "domain": "intrapersonal",
            "component": "performance_1",
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
            "component": "performance_2",
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
        },
        {
            "key": "intrapersonal_frustration",
            "type": "choice",
            "domain": "intrapersonal",
            "component": "situational",
            "title": {"English": "Stuck Kite", "Hindi": "फंसी पतंग"},
            "prompt": {
                "English": "You spent an hour making a paper kite, but it immediately gets stuck in a tall thorny tree and tears. What do you do?",
                "Hindi": "आपने कागज़ का पतंग बनाने में एक घंटा लगाया, लेकिन वह तुरंत एक बड़े कांटेदार पेड़ में फंसकर फट जाती है। आप क्या करेंगे?"
            },
            "options": [
                {"label": {"English": "Acknowledge the mistake, clean up, and build a stronger version using what you learned", "Hindi": "गलती को स्वीकार करें, सफाई करें, और सीखी हुई बातों का उपयोग करके एक मजबूत पतंग बनाएं"}, "value": 4},
                {"label": {"English": "Get angry and scream at the tree", "Hindi": "गुस्सा हो जाएं और पेड़ पर चिल्लाएं"}, "value": 1},
                {"label": {"English": "Ask your friend to climb the thorny tree even if it is dangerous", "Hindi": "खतरनाक होने पर भी अपने दोस्त से उस कांटेदार पेड़ पर चढ़ने के लिए कहें"}, "value": 2},
                {"label": {"English": "Throw all your remaining paper sheets in the mud", "Hindi": "अपने बचे हुए सभी कागज़ के टुकड़ों को कीचड़ में फेंक दें"}, "value": 0}
            ],
            "answer": "Acknowledge the mistake, clean up, and build a stronger version using what you learned",
            "metric": "correctness",
            "difficulty": "easy",
            "ai_interpretation_notes": "Measures emotional regulation and resilience under disappointment."
        },
        {
            "key": "intrapersonal_difficult_moment",
            "type": "open_ended",
            "domain": "intrapersonal",
            "component": "open_response",
            "title": {"English": "Difficult Moment", "Hindi": "कठिन समय"},
            "prompt": {
                "English": "Describe a difficult situation you faced at school or home, how you felt, and what you learned from it.",
                "Hindi": "स्कूल या घर पर सामना की गई किसी कठिन परिस्थिति के बारे में बताएं, आपको कैसा लगा, और आपने उससे क्या सीखा।"
            },
            "metric": "narrative_expression",
            "difficulty": "adaptive",
            "ai_interpretation_notes": "Measures self-reflection depth, emotional awareness, and resilience learning."
        }
    ]

    for p in deep_puzzles:
        bank.append(p)

    # Write bank to JSON
    bank_dir = os.path.join(os.path.dirname(__file__), "question_bank")
    os.makedirs(bank_dir, exist_ok=True)
    bank_path = os.path.join(bank_dir, "extended_bank.json")
    
    with open(bank_path, "w", encoding="utf-8") as f:
        json.dump(bank, f, ensure_ascii=False, indent=2)
        
    print(f"Successfully generated {len(bank)} items in {bank_path}.")

if __name__ == "__main__":
    generate_bank()

import os
import json

def generate_bank():
    print("Generating extended 103-question assessment bank...")
    bank = []

    # -------------------------------------------------------------
    # SECTION 1: DISCOVERY PHASE (6 questions)
    # -------------------------------------------------------------
    discovery_data = [
        {
            "id": "1",
            "en_q": "Your teacher gives your group a difficult challenge. What do you naturally do first?",
            "hi_q": "आपकी शिक्षिका आपके समूह को एक कठिन चुनौती देती हैं। आप स्वाभाविक रूप से सबसे पहले क्या करते हैं?",
            "options": [
                {"en": "Break the problem into smaller parts and look for patterns", "hi": "समस्या को छोटे भागों में बांटें और पैटर्न खोजें", "domain": "logical", "riasec": "Investigative"},
                {"en": "Think of a unique or unusual solution", "hi": "एक अनोखा या असामान्य समाधान सोचें", "domain": "creative", "riasec": "Artistic"},
                {"en": "Explain ideas and help everyone understand", "hi": "विचारों को समझाएं और सभी को समझने में मदद करें", "domain": "language", "riasec": "Social"},
                {"en": "Organize the group and assign tasks", "hi": "समूह को व्यवस्थित करें और काम सौंपें", "domain": "social", "riasec": "Enterprising"}
            ]
        },
        {
            "id": "2",
            "en_q": "You receive a box filled with cardboard, sticks, paper clips and rubber bands. What do you do first?",
            "hi_q": "आपको कार्डबोर्ड, डंडे, पेपर क्लिप और रबर बैंड से भरा एक डिब्बा मिलता है। आप सबसे पहले क्या करते हैं?",
            "options": [
                {"en": "Build something useful", "hi": "कुछ उपयोगी बनाएं", "domain": "spatial", "riasec": "Realistic"},
                {"en": "Create something beautiful", "hi": "कुछ सुंदर बनाएं", "domain": "creative", "riasec": "Artistic"},
                {"en": "Sort everything and understand how it works", "hi": "सब कुछ अलग करें और समझें कि यह कैसे काम करता है", "domain": "logical", "riasec": "Investigative"},
                {"en": "Shake the box and feel the weight of the objects", "hi": "डिब्बे को हिलाएं और वस्तुओं के वजन को महसूस करें", "domain": "kinesthetic", "riasec": "Realistic"}
            ]
        },
        {
            "id": "3",
            "en_q": "You discover an unusual insect in the school garden. What is your first reaction?",
            "hi_q": "आपको स्कूल के बगीचे में एक अनोखा कीड़ा मिलता है। आपकी पहली प्रतिक्रिया क्या होती है?",
            "options": [
                {"en": "Observe it carefully and watch where it goes", "hi": "इसे ध्यान से देखें और देखें कि यह कहाँ जाता है", "domain": "naturalist", "riasec": "Investigative"},
                {"en": "Draw a sketch of it in your notebook", "hi": "अपनी कॉपी में इसका एक चित्र बनाएं", "domain": "creative", "riasec": "Artistic"},
                {"en": "Reflect quietly on what its life is like", "hi": "चुपचाप विचार करें कि इसका जीवन कैसा है", "domain": "intrapersonal", "riasec": "Investigative"},
                {"en": "Run to tell your classmates about it", "hi": "अपने सहपाठियों को इसके बारे में बताने के लिए दौड़ें", "domain": "language", "riasec": "Social"}
            ]
        },
        {
            "id": "4",
            "en_q": "A friend feels left out during lunch break. What do you naturally do?",
            "hi_q": "लंच ब्रेक के दौरान एक दोस्त अकेला महसूस कर रहा है। आप स्वाभाविक रूप से क्या करते हैं?",
            "options": [
                {"en": "Invite them to join your group", "hi": "उन्हें अपने समूह में शामिल होने के लिए आमंत्रित करें", "domain": "social", "riasec": "Social"},
                {"en": "Sit with them and chat kindly", "hi": "उनके साथ बैठें और प्यार से बात करें", "domain": "language", "riasec": "Social"},
                {"en": "Think quietly about how they might be feeling", "hi": "चुपचाप सोचें कि वे कैसा महसूस कर रहे होंगे", "domain": "intrapersonal", "riasec": "Investigative"},
                {"en": "Start an active game to cheer everyone up", "hi": "सभी का मनोरंजन करने के लिए एक दौड़-भाग वाला खेल शुरू करें", "domain": "kinesthetic", "riasec": "Realistic"}
            ]
        },
        {
            "id": "5",
            "en_q": "You get a brand-new board game. What happens first?",
            "hi_q": "आपको एक बिल्कुल नया बोर्ड गेम मिलता है। सबसे पहले क्या होता है?",
            "options": [
                {"en": "Look for patterns and strategize to win", "hi": "पैटर्न खोजें और जीतने की रणनीति बनाएं", "domain": "logical", "riasec": "Investigative"},
                {"en": "Examine the board pieces and setup structure", "hi": "बोर्ड के टुकड़ों और सेटअप की संरचना की जांच करें", "domain": "spatial", "riasec": "Realistic"},
                {"en": "Touch and move the pieces physically to feel them", "hi": "गोटियों को छूकर और हिलाकर देखें", "domain": "kinesthetic", "riasec": "Realistic"},
                {"en": "Explain rules and play together with friends", "hi": "नियम समझाएं और दोस्तों के साथ मिलकर खेलें", "domain": "social", "riasec": "Social"}
            ]
        },
        {
            "id": "6",
            "en_q": "Your school is holding a fair. Which role feels most natural?",
            "hi_q": "आपका स्कूल एक मेला आयोजित कर रहा है। कौन सी भूमिका सबसे स्वाभाविक लगती है?",
            "options": [
                {"en": "Designing banners and decorations", "hi": "बैनर और सजावट डिजाइन करना", "domain": "creative", "riasec": "Artistic"},
                {"en": "Managing teams and coordinating stall duties", "hi": "टीमों का प्रबंधन करना और स्टॉल के कामों का तालमेल बिठाना", "domain": "social", "riasec": "Enterprising"},
                {"en": "Speaking on stage and welcoming guests", "hi": "मंच पर बोलना और मेहमानों का स्वागत करना", "domain": "language", "riasec": "Social"},
                {"en": "Building display racks and game booths", "hi": "डिस्प्ले रैक और गेम बूथ बनाना", "domain": "spatial", "riasec": "Realistic"}
            ]
        }
    ]

    for d in discovery_data:
        opts = []
        for idx, o in enumerate(d["options"]):
            opts.append({
                "label": {"English": o["en"], "Hindi": o["hi"]},
                "value": 4 - idx,
                "mapping": {o["domain"]: 4},
                "riasec": o["riasec"]
            })
        bank.append({
            "key": f"q_discovery_{d['id']}",
            "type": "choice",
            "domain": d["options"][0]["domain"],
            "component": "discovery_preference",
            "title": {"English": f"Discovery Question {d['id']}", "Hindi": f"खोज प्रश्न {d['id']}"},
            "prompt": {"English": d["en_q"], "Hindi": d["hi_q"]},
            "options": opts,
            "metric": "preference",
            "difficulty": "easy",
            "ai_interpretation_notes": "Discovery phase preference test measuring natural domain alignment."
        })

    # -------------------------------------------------------------
    # SECTION 2: RIASEC CAREER ASSESSMENT (18 questions - 3 per dimension)
    # -------------------------------------------------------------
    riasec_defs = [
        # R - Realistic
        ("r", 1, "spatial", "Realistic", 
         "Do you like building things from wood, cardboard, or plastic blocks?", 
         "क्या आपको लकड़ी, गत्ते या प्लास्टिक ब्लॉक से चीजें बनाना पसंद है?"),
        ("r", 2, "spatial", "Realistic", 
         "Do you enjoy fixing broken things like toys, cycles, or pencil sharpeners?", 
         "क्या आपको खिलौने, साइकिल या पेंसिल शार्पनर जैसी टूटी हुई चीजें ठीक करना पसंद है?"),
        ("r", 3, "spatial", "Realistic", 
         "Do you like spending time gardening, planting seeds, or feeding animals?", 
         "क्या आपको बागवानी करना, बीज बोना या जानवरों को खाना खिलाना पसंद है?"),
        # I - Investigative
        ("i", 1, "logical", "Investigative", 
         "Do you like solving math riddles and number puzzles?", 
         "क्या आपको गणित की पहेलियां और संख्या पहेलियां हल करना पसंद है?"),
        ("i", 2, "logical", "Investigative", 
         "Do you enjoy learning how machines, magnets, or electricity work?", 
         "क्या आपको यह सीखना पसंद है कि मशीनें, चुंबकीय शक्ति या बिजली कैसे काम करती है?"),
        ("i", 3, "logical", "Investigative", 
         "Do you like looking at maps, stars, or reading science facts?", 
         "क्या आपको नक्शे, तारे देखना या विज्ञान के तथ्य पढ़ना पसंद है?"),
        # A - Artistic
        ("a", 1, "creative", "Artistic", 
         "Do you like drawing, painting, or sketching cartoons and scenes?", 
         "क्या आपको चित्र बनाना, पेंटिंग करना या कार्टून और दृश्य बनाना पसंद है?"),
        ("a", 2, "creative", "Artistic", 
         "Do you enjoy writing stories, poems, or creating plays?", 
         "क्या आपको कहानियां, कविताएं लिखना या नाटक बनाना पसंद है?"),
        ("a", 3, "creative", "Artistic", 
         "Do you like singing, humming, playing a musical instrument, or dancing?", 
         "क्या आपको गाना, गुनगुनाना, वाद्य यंत्र बजाना या नृत्य करना पसंद है?"),
        # S - Social
        ("s", 1, "social", "Social", 
         "Do you like teaching your classmates or younger children how to do something?", 
         "क्या आपको अपने सहपाठियों या छोटे बच्चों को कुछ सिखाना पसंद है?"),
        ("s", 2, "social", "Social", 
         "Do you enjoy helping a friend when they are upset or having trouble?", 
         "क्या आपको किसी दोस्त की मदद करना पसंद है जब वे परेशान हों या मुश्किल में हों?"),
        ("s", 3, "social", "Social", 
         "Do you like playing team games where everyone works together?", 
         "क्या आपको ऐसे टीम खेल खेलना पसंद है जहाँ सभी मिलकर काम करते हैं?"),
        # E - Enterprising
        ("e", 1, "social", "Enterprising", 
         "Do you like organizing group games or leading teams in school?", 
         "क्या आपको स्कूल में समूह खेल आयोजित करना या टीमों का नेतृत्व करना पसंद है?"),
        ("e", 2, "social", "Enterprising", 
         "Do you enjoy speaking in front of the class, presenting ideas, or debating?", 
         "क्या आपको कक्षा के सामने बोलना, विचार प्रस्तुत करना या वाद-विवाद करना पसंद है?"),
        ("e", 3, "social", "Enterprising", 
         "Do you like planning how to sell things or set up school fair stalls?", 
         "क्या आपको चीजें बेचना या स्कूल मेले के स्टॉल लगाने की योजना बनाना पसंद है?"),
        # C - Conventional
        ("c", 1, "logical", "Conventional", 
         "Do you like sorting and organizing your books, pencils, and workspace neatly?", 
         "क्या आपको अपनी किताबें, पेंसिल और काम करने की जगह को साफ-सुथरा रखना पसंद है?"),
        ("c", 2, "logical", "Conventional", 
         "Do you enjoy keeping a daily checklist or daily schedule for your tasks?", 
         "क्या आपको अपने कार्यों के लिए दैनिक चेकलिस्ट या दैनिक कार्यक्रम रखना पसंद है?"),
        ("c", 3, "logical", "Conventional", 
         "Do you like following clear rules and step-by-step instructions in games?", 
         "क्या आपको खेलों में स्पष्ट नियमों और कदम-दर-कदम निर्देशों का पालन करना पसंद है?")
    ]

    for dim_key, num, domain, dim_name, en_q, hi_q in riasec_defs:
        bank.append({
            "key": f"riasec_{dim_key}_{num}",
            "type": "choice",
            "domain": domain,
            "component": "discovery_preference",
            "title": {"English": f"{dim_name} preference {num}", "Hindi": f"{dim_name} preference {num}"},
            "prompt": {"English": en_q, "Hindi": hi_q},
            "options": [
                {"label": {"English": "Yes, I would love to do this regularly.", "Hindi": "हाँ, मुझे यह नियमित रूप से करना बहुत पसंद आएगा।"}, "value": 4, "mapping": {domain: 4}, "riasec": dim_name},
                {"label": {"English": "Yes, I would try it occasionally.", "Hindi": "हाँ, मैं कभी-कभी इसे आजमाना चाहूंगा।"}, "value": 2, "mapping": {domain: 2}, "riasec": dim_name},
                {"label": {"English": "I don't mind it, but it's not my first choice.", "Hindi": "मुझे कोई आपत्ति नहीं है, लेकिन यह मेरी पहली पसंद नहीं है।"}, "value": 1, "mapping": {domain: 1}, "riasec": dim_name},
                {"label": {"English": "No, I would avoid it.", "Hindi": "नहीं, मैं इससे बचना चाहूंगा।"}, "value": 0, "mapping": {domain: 0}, "riasec": dim_name}
            ],
            "metric": "riasec_score",
            "difficulty": "easy",
            "ai_interpretation_notes": f"Behavior-based preference question directly targeting {dim_name} career dimension."
        })

    # -------------------------------------------------------------
    # SECTION 3: BEHAVIORAL SCENARIOS (40 questions - 5 per domain/trait)
    # -------------------------------------------------------------
    
    # 3.1 Curiosity (5 items)
    curiosity_scenarios = [
        ("1", "The Mystery Box", "A sealed box with no label is left on your desk. What is your first reaction?",
         "रहस्यमयी डिब्बा: आपके डेस्क पर बिना नाम का एक बंद डिब्बा रखा है। आपकी पहली प्रतिक्रिया क्या होगी?"),
        ("2", "The Hidden Library Door", "You notice a tiny door hidden behind a bookshelf in the library. What do you do?",
         "पुस्तकालय का छिपा हुआ दरवाजा: आप पुस्तकालय में एक अलमारी के पीछे एक छोटा सा छिपा हुआ दरवाजा देखते हैं। आप क्या करेंगे?"),
        ("3", "The Strange humming sound", "You hear a soft, strange buzzing sound behind the school wall. How do you respond?",
         "अजीब भनभनाहट: आप स्कूल की दीवार के पीछे से एक हल्की, अजीब भनभनाहट सुनते हैं। आप क्या प्रतिक्रिया देंगे?"),
        ("4", "The Glowing Plant", "You find a leaf in the park that glows slightly in the dark. What is your first action?",
         "चमकता हुआ पौधा: आपको पार्क में एक पत्ता मिलता है जो अंधेरे में थोड़ा चमकता है। आपका पहला कदम क्या होगा?"),
        ("5", "The New Game", "A friend brings a board game with no instruction booklet. How do you react?",
         "नया खेल: एक दोस्त बिना नियमों की पुस्तिका वाला बोर्ड गेम लाता है। आप क्या करेंगे?")
    ]
    for num, title, en_q, hi_q in curiosity_scenarios:
        bank.append({
            "key": f"curiosity_{num}",
            "type": "choice",
            "domain": "intrapersonal",
            "component": "reflective_thinking",
            "title": {"English": title, "Hindi": title},
            "prompt": {"English": en_q, "Hindi": hi_q},
            "options": [
                {"label": {"English": "Examine it closely and try to understand how it works.", "Hindi": "बारीकी से जांच करें और समझें कि यह कैसे काम करता है।"}, "value": 4, "mapping": {"intrapersonal": 4}, "riasec": "Investigative"},
                {"label": {"English": "Ask the teacher or search online to learn more.", "Hindi": "शिक्षक से पूछें या अधिक जानने के लिए ऑनलाइन खोजें।"}, "value": 3, "mapping": {"language": 4}, "riasec": "Conventional"},
                {"label": {"English": "Touch and move switches gently to see what happens.", "Hindi": "यह देखने के लिए कि क्या होता है, स्विचों को धीरे से छुएं और हिलाएं।"}, "value": 2, "mapping": {"spatial": 4}, "riasec": "Realistic"},
                {"label": {"English": "Leave it alone to avoid making a mistake.", "Hindi": "गलती से बचने के लिए इसे अकेला छोड़ दें।"}, "value": 1, "mapping": {"intrapersonal": 1}, "riasec": "Conventional"}
            ],
            "metric": "curiosity_level",
            "difficulty": "medium",
            "ai_interpretation_notes": "Measures curiosity and active exploration preference."
        })

    # 3.2 Motivation (5 items)
    motivation_scenarios = [
        ("1", "Choosing a School Project", "When picking a project to work on, what matters most to you?",
         "स्कूल प्रोजेक्ट चुनना: काम करने के लिए एक प्रोजेक्ट चुनते समय आपके लिए सबसे महत्वपूर्ण क्या है?"),
        ("2", "Learning a Hard Skill", "When trying to learn a new, difficult skill (like drawing or a sport), what drives you?",
         "कठिन कौशल सीखना: जब आप एक नया, कठिन कौशल (जैसे ड्राइंग या खेल) सीखने की कोशिश कर रहे होते हैं, तो आपको क्या प्रेरित करता है?"),
        ("3", "Group Work Contribution", "When working in a group, what gives you the most satisfaction?",
         "समूह कार्य में योगदान: समूह में काम करते समय आपको सबसे अधिक संतुष्टि किससे मिलती है?"),
        ("4", "Sports Day Goal", "If you participate in Sports Day, what is your main aim?",
         "खेल दिवस का लक्ष्य: यदि आप खेल दिवस में भाग लेते हैं, तो आपका मुख्य लक्ष्य क्या है?"),
        ("5", "Drawing a Picture", "When you paint or draw a picture in your free time, what is your main purpose?",
         "चित्र बनाना: जब आप खाली समय में चित्र बनाते हैं, तो आपका मुख्य उद्देश्य क्या होता है?")
    ]
    for num, title, en_q, hi_q in motivation_scenarios:
        bank.append({
            "key": f"motivation_{num}",
            "type": "choice",
            "domain": "intrapersonal",
            "component": "self_awareness",
            "title": {"English": title, "Hindi": title},
            "prompt": {"English": en_q, "Hindi": hi_q},
            "options": [
                {"label": {"English": "Learning a new skill that I haven't mastered yet.", "Hindi": "एक नया कौशल सीखना जिसमें मैंने अभी तक महारत हासिल नहीं की है।"}, "value": 4, "mapping": {"intrapersonal": 4}, "riasec": "Investigative"},
                {"label": {"English": "Helping my classmates or solving a community problem.", "Hindi": "अपने सहपाठियों की मदद करना या किसी सामुदायिक समस्या को हल करना।"}, "value": 3, "mapping": {"social": 4}, "riasec": "Social"},
                {"label": {"English": "Creating something unique and beautiful that others will enjoy.", "Hindi": "कुछ अनोखा और सुंदर बनाना जिसका दूसरे आनंद ले सकें।"}, "value": 2, "mapping": {"creative": 4}, "riasec": "Artistic"},
                {"label": {"English": "Doing better than others or winning a reward.", "Hindi": "दूसरों से बेहतर करना या इनाम जीतना।"}, "value": 1, "mapping": {"social": 2}, "riasec": "Enterprising"}
            ],
            "metric": "motivation_drivers",
            "difficulty": "medium",
            "ai_interpretation_notes": "Identifies primary motivational drivers."
        })

    # 3.3 Learning Style (5 items)
    learning_scenarios = [
        ("1", "Learning Board Game", "You need to learn a new board game. How do you prefer to start?",
         "नया खेल सीखना: आपको एक नया बोर्ड गेम सीखना है। आप कैसे शुरू करना पसंद करते हैं?"),
        ("2", "Learning a Recipe", "You want to learn how to cook a simple snack. What is best for you?",
         "पकाने की विधि सीखना: आप एक साधारण स्नैक बनाना सीखना चाहते हैं। आपके लिए क्या सबसे अच्छा है?"),
        ("3", "Learning a Dance Step", "You need to learn a new dance move or physical exercise. How do you learn best?",
         "नृत्य कदम सीखना: आपको एक नया नृत्य कदम या शारीरिक व्यायाम सीखना है। आप सबसे अच्छे तरीके से कैसे सीखते हैं?"),
        ("4", "Finding a New Route", "You need to find a way to a new shop in your neighborhood. What do you do?",
         "नया रास्ता खोजना: आपको अपने पड़ोस में एक नई दुकान का रास्ता खोजना है। आप क्या करेंगे?"),
        ("5", "Understanding a Machine", "You want to understand how a mechanical toy works. What do you prefer?",
         "मशीन को समझना: आप यह समझना चाहते हैं कि एक यांत्रिक खिलौना कैसे काम करता है। आप क्या पसंद करते हैं?")
    ]
    for num, title, en_q, hi_q in learning_scenarios:
        bank.append({
            "key": f"learning_style_{num}",
            "type": "choice",
            "domain": "intrapersonal",
            "component": "reflective_thinking",
            "title": {"English": title, "Hindi": title},
            "prompt": {"English": en_q, "Hindi": hi_q},
            "options": [
                {"label": {"English": "Read a booklet, rules sheet, or written guide quietly.", "Hindi": "शांति से एक नियम पुस्तिका या लिखित गाइड पढ़ें।"}, "value": 4, "mapping": {"logical": 4}, "learning_style": "Reading/Writing"},
                {"label": {"English": "Look at pictures, maps, diagrams, or watch a video demo.", "Hindi": "चित्र, नक्शे, चित्रलेख देखें या एक वीडियो प्रदर्शन देखें।"}, "value": 3, "mapping": {"spatial": 4}, "learning_style": "Visual"},
                {"label": {"English": "Listen to a friend explain the instructions to me verbally.", "Hindi": "एक दोस्त को मौखिक रूप से मुझे निर्देश समझाते हुए सुनें।"}, "value": 2, "mapping": {"language": 4}, "learning_style": "Auditory"},
                {"label": {"English": "Start playing or trying immediately and learn as I go.", "Hindi": "तुरंत खेलना या प्रयास करना शुरू करें और आगे बढ़ते हुए सीखें।"}, "value": 1, "mapping": {"kinesthetic": 4}, "learning_style": "Kinesthetic"}
            ],
            "metric": "learning_style",
            "difficulty": "easy",
            "ai_interpretation_notes": "Identifies cognitive processing and learning preference."
        })

    # 3.4 Resilience (5 items)
    resilience_scenarios = [
        ("1", "The Broken Clay Castle", "You spent an hour building a clay castle, but a classmate accidentally trips and crushes it. What do you do?",
         "टूटा हुआ किला: आपने मिट्टी का किला बनाने में एक घंटा लगाया, लेकिन एक सहपाठी गलती से फिसल कर उसे तोड़ देता है। आप क्या करेंगे?"),
        ("2", "Failing a Game Level", "You fail to cross a level in a strategy puzzle game after trying for 15 minutes. How do you respond?",
         "खेल का स्तर: आप 15 मिनट की कोशिश के बाद एक रणनीति पहेली खेल में एक स्तर को पार करने में विफल रहते हैं। आप क्या प्रतिक्रिया देंगे?"),
        ("3", "The Lost Notebook", "You lose your school notebook containing your drawing work. What is your reaction?",
         "खोई हुई कॉपी: आप अपनी कॉपी खो देते हैं जिसमें आपकी ड्राइंग का काम था। आपकी प्रतिक्रिया क्या होगी?"),
        ("4", "Rain Cancels Play", "It starts raining heavily, canceling your planned outdoor games. How do you react?",
         "बारिश से खेल रद्द: भारी बारिश शुरू हो जाती है, जिससे आपकी नियोजित बाहरी खेल गतिविधियाँ रद्द हो जाती हैं। आप क्या करेंगे?"),
        ("5", "Mistake in Art Project", "You make a mistake in a drawing and smudge the colors. What is your next step?",
         "कला में गलती: आप एक ड्राइंग में गलती करते हैं और रंग फैल जाता है। आपका अगला कदम क्या होगा?")
    ]
    for num, title, en_q, hi_q in resilience_scenarios:
        key = "social_sandcastle" if num == "1" else f"resilience_{num}"
        bank.append({
            "key": key,
            "type": "choice",
            "domain": "intrapersonal",
            "component": "resilience_signal",
            "title": {"English": title, "Hindi": title},
            "prompt": {"English": en_q, "Hindi": hi_q},
            "options": [
                {"label": {"English": "Acknowledge it, clean the area, and plan a better version using what you learned.", "Hindi": "इसे स्वीकार करें, जगह साफ करें और सीखी हुई बातों का उपयोग करके एक बेहतर संस्करण की योजना बनाएं।"}, "value": 4, "mapping": {"intrapersonal": 4}, "riasec": "Investigative"},
                {"label": {"English": "Try to fix it gently using available tools or helpers.", "Hindi": "उपलब्ध उपकरणों या सहायकों की मदद से इसे धीरे से ठीक करने का प्रयास करें।"}, "value": 4, "mapping": {"social": 3}, "riasec": "Social"},
                {"label": {"English": "Collaborate with friends to find a fun alternative activity indoors.", "Hindi": "घर के अंदर एक मजेदार वैकल्पिक गतिविधि खोजने के लिए दोस्तों के साथ मिलकर काम करें।"}, "value": 3, "mapping": {"logical": 4}, "riasec": "Realistic"},
                {"label": {"English": "Feel angry, drop the activity completely, and walk away.", "Hindi": "गुस्सा महसूस करें, गतिविधि को पूरी तरह से छोड़ दें और चले जाएं।"}, "value": 1, "mapping": {"intrapersonal": 1}, "riasec": "Conventional"}
            ],
            "metric": "grit_resilience",
            "difficulty": "medium",
            "ai_interpretation_notes": "Measures coping strategies and persistence."
        })

    # 3.5 Social / Empathy (5 items)
    social_scenarios = [
        ("1", "The Upset Classmate", "A classmate is quiet and crying silently at the edge of the classroom. What do you do?",
         "उदास सहपाठी: एक सहपाठी शांत है और कक्षा के कोने में चुपचाप रो रहा है। आप क्या करेंगे?"),
        ("2", "The Left-Out Friend", "A friend wants to join a group game but other players say the team is already full. How do you respond?",
         "अकेला दोस्त: एक दोस्त समूह के खेल में शामिल होना चाहता है लेकिन अन्य खिलाड़ी कहते हैं कि टीम पहले से ही भरी हुई है। आप क्या प्रतिक्रिया देंगे?"),
        ("3", "Group Project Dispute", "During a class group activity, two friends start arguing loudly about a drawing layout. What do you do?",
         "समूह परियोजना विवाद: कक्षा की एक समूह गतिविधि के दौरान, दो दोस्त एक चित्र के लेआउट को लेकर आपस में बहस करने लगते हैं। आप क्या करेंगे?"),
        ("4", "Sharing Lunch", "A classmate forgets their lunch box and sits alone during lunch break. What is your action?",
         "दोपहर का भोजन साझा करना: एक सहपाठी अपना टिफिन बॉक्स भूल जाता है और लंच ब्रेक के दौरान अकेला बैठता है। आपका कदम क्या होगा?"),
        ("5", "The New Student", "A new student joins your class today. They look nervous and do not know anyone. What do you do?",
         "नया छात्र: आज आपकी कक्षा में एक नया छात्र आया है। वे घबराए हुए दिखते हैं और किसी को नहीं जानते। आप क्या करेंगे?")
    ]
    for num, title, en_q, hi_q in social_scenarios:
        key = "social_conflict_resolution" if num == "3" else f"social_intel_{num}"
        bank.append({
            "key": key,
            "type": "choice",
            "domain": "social",
            "component": "empathy_recognition",
            "title": {"English": title, "Hindi": title},
            "prompt": {"English": en_q, "Hindi": hi_q},
            "options": [
                {"label": {"English": "Approach them gently, speak kindly, and check how to help.", "Hindi": "उनके पास धीरे से जाएं, प्यार से बात करें और देखें कि कैसे मदद की जा सकती है।"}, "value": 4, "mapping": {"social": 4}, "riasec": "Social"},
                {"label": {"English": "Invite them to join immediately or share my spot with them.", "Hindi": "उन्हें तुरंत शामिल होने के लिए आमंत्रित करें या उनके साथ अपनी जगह साझा करें।"}, "value": 4, "mapping": {"social": 3}, "riasec": "Social"},
                {"label": {"English": "Suggest a fair compromise or try to calm both sides down.", "Hindi": "एक निष्पक्ष समझौता सुझाएं या दोनों पक्षों को शांत करने का प्रयास करें।"}, "value": 3, "mapping": {"intrapersonal": 3}, "riasec": "Investigative"},
                {"label": {"English": "Keep playing with my friends and let them resolve it themselves.", "Hindi": "अपने दोस्तों के साथ खेलते रहें और उन्हें खुद इसे सुलझाने दें।"}, "value": 1, "mapping": {"social": 1}, "riasec": "Conventional"}
            ],
            "metric": "social_intelligence",
            "difficulty": "medium",
            "ai_interpretation_notes": "Measures prosocial empathy and conflict resolution strategies."
        })

    # 3.6 Leadership (5 items)
    leadership_scenarios = [
        ("1", "The Lost Group Route", "During a school field trip in a forest, your group takes a wrong turn and gets lost. How do you lead?",
         "खोया हुआ रास्ता: जंगल में एक स्कूल फील्ड ट्रिप के दौरान, आपका समूह गलत मोड़ ले लेता है और रास्ता भटक जाता है। आप कैसे नेतृत्व करेंगे?"),
        ("2", "Classroom Cleanup Stall", "Your teacher asks your class to clean and paint the school garden stall. How do you coordinate?",
         "कक्षा की सफाई: आपकी शिक्षिका आपकी कक्षा को स्कूल के बगीचे के स्टॉल को साफ और पेंट करने के लिए कहती हैं। आप तालमेल कैसे बिठाएंगे?"),
        ("3", "The Group Drama Play", "Your group is preparing a small drama act, but members are arguing about roles. What do you do?",
         "समूह नाटक: आपका समूह एक छोटे नाटक की तैयारी कर रहा है, लेकिन सदस्य भूमिकाओं को लेकर बहस कर रहे हैं। आप क्या करेंगे?"),
        ("4", "Group Project Deadline", "Your group project has 10 minutes left for submission, but a chart sheet is still unfinished. How do you act?",
         "परियोजना की समय सीमा: आपके समूह प्रोजेक्ट को जमा करने में 10 मिनट बचे हैं, लेकिन एक चार्ट शीट अभी भी अधूरी है। आप क्या करेंगे?"),
        ("5", "Setting Up Sports Team", "You need to select classmates to form a team for a sports match. How do you choose?",
         "खेल टीम बनाना: आपको एक खेल मैच के लिए टीम बनाने के लिए सहपाठियों का चयन करना है। आप कैसे चुनाव करेंगे?")
    ]
    for num, title, en_q, hi_q in leadership_scenarios:
        bank.append({
            "key": f"leadership_{num}",
            "type": "choice",
            "domain": "social",
            "component": "peer_influence",
            "title": {"English": title, "Hindi": title},
            "prompt": {"English": en_q, "Hindi": hi_q},
            "options": [
                {"label": {"English": "Propose a quick democratic vote to decide the next action immediately.", "Hindi": "तुरंत अगला कदम तय करने के लिए एक त्वरित लोकतांत्रिक वोट का प्रस्ताव रखें।"}, "value": 4, "mapping": {"social": 4}, "leadership_style": "Democratic"},
                {"label": {"English": "Delegate tasks to each member based on their strengths to work faster.", "Hindi": "तेजी से काम करने के लिए प्रत्येक सदस्य को उनकी ताकत के आधार पर काम सौंपें।"}, "value": 4, "mapping": {"social": 3}, "leadership_style": "Delegative"},
                {"label": {"English": "Make the decision myself, explain why, and lead the team forward.", "Hindi": "निर्णय स्वयं लें, समझाएं कि क्यों, और टीम को आगे बढ़ाएं।"}, "value": 3, "mapping": {"social": 2}, "leadership_style": "Authoritative"},
                {"label": {"English": "Sit back and wait until the group naturally reaches a consensus.", "Hindi": "आराम से बैठें और तब तक प्रतीक्षा करें जब तक कि समूह स्वाभाविक रूप से आम सहमति पर न पहुंच जाए।"}, "value": 1, "mapping": {"social": 1}, "leadership_style": "Laissez-faire"}
            ],
            "metric": "leadership_style",
            "difficulty": "medium",
            "ai_interpretation_notes": "Identifies preferred situational leadership style."
        })

    # 3.7 Entrepreneurial (5 items)
    entrepreneurial_scenarios = [
        ("1", "Canteen Long Queues", "You notice students wait in a long, slow queue every day to buy notebooks at the book shop. What do you think?",
         "कैंटीन की लंबी कतारें: आप देखते हैं कि छात्र किताबों की दुकान पर नोटबुक खरीदने के लिए हर दिन एक लंबी, धीमी कतार में खड़े रहते हैं। आप क्या सोचते हैं?"),
        ("2", "The School Shop Stall", "Your class is allowed to run a game stall at the school fair to raise funds. What do you do?",
         "school की दुकान का स्टॉल: आपकी कक्षा को धन जुटाने के लिए स्कूल मेले में एक गेम स्टॉल चलाने की अनुमति दी गई है। आप क्या करेंगे?"),
        ("3", "Origami Toy Crafts", "Many classmates want paper toy animals, but they do not know how to fold them. How do you solve this?",
         "ओरिगेमी खिलौने: कई सहपाठी कागज के खिलौने वाले जानवर चाहते हैं, लेकिन वे उन्हें मोड़ना नहीं जानते। आप इसका समाधान कैसे करेंगे?"),
        ("4", "The Classroom Newspaper", "You want to share news and stories about your class with the school. How do you start?",
         "कक्षा का समाचार पत्र: आप स्कूल के साथ अपनी कक्षा के समाचार और कहानियां साझा करना चाहते हैं। आप कैसे शुरुआत करेंगे?"),
        ("5", "Used Book Exchange", "You notice many students have old storybooks they have read and don't need anymore. What do you do?",
         "पुरानी पुस्तकों का आदान-प्रदान: आप देखते हैं कि कई छात्रों के पास पुरानी कहानियों की किताबें हैं जिन्हें वे पढ़ चुके हैं और अब उनकी आवश्यकता नहीं है। आप क्या करेंगे?")
    ]
    for num, title, en_q, hi_q in entrepreneurial_scenarios:
        bank.append({
            "key": f"entrepreneurial_{num}",
            "type": "choice",
            "domain": "social",
            "component": "group_organising",
            "title": {"English": title, "Hindi": title},
            "prompt": {"English": en_q, "Hindi": hi_q},
            "options": [
                {"label": {"English": "Organize a small system with friends to pre-order or deliver items for a small fee.", "Hindi": "छोटे से शुल्क पर वस्तुओं को प्री-ऑर्डर या डिलीवर करने के लिए दोस्तों के साथ एक छोटी व्यवस्था बनाएं।"}, "value": 4, "mapping": {"social": 4, "logical": 3}, "riasec": "Enterprising"},
                {"label": {"English": "Design a faster queue process or token system and suggest it to the shop owner.", "Hindi": "एक तेज़ कतार प्रक्रिया या टोकन प्रणाली डिज़ाइन करें और दुकान के मालिक को इसका सुझाव दें।"}, "value": 4, "mapping": {"logical": 4}, "riasec": "Investigative"},
                {"label": {"English": "Teach a few close friends how to do it and share the activity.", "Hindi": "कुछ करीबी दोस्तों को इसे करना सिखाएं और गतिविधि साझा करें।"}, "value": 2, "mapping": {"spatial": 3}, "riasec": "Realistic"},
                {"label": {"English": "Do nothing since it is not my responsibility.", "Hindi": "कुछ न करें क्योंकि यह मेरी ज़िम्मेदारी नहीं है।"}, "value": 1, "mapping": {"intrapersonal": 1}, "riasec": "Conventional"}
            ],
            "metric": "entrepreneurial_mindset",
            "difficulty": "medium",
            "ai_interpretation_notes": "Measures opportunity recognition, initiative, and resourcefulness."
        })

    # 3.8 Intrapersonal / Self-regulation (5 items)
    intrapersonal_scenarios = [
        ("1", "Frustration in Drawing", "You feel frustrated because your drawing is not turning out as good as you expected. How do you handle it?",
         "चित्र बनाने में निराशा: आप निराश महसूस करते हैं क्योंकि आपका चित्र वैसा नहीं बन रहा है जैसा आपने उम्मीद की थी। आप इसे कैसे संभालेंगे?"),
        ("2", "Anger in Teamwork", "A classmate in your project group ignores your idea, and you feel very angry. What do you do?",
         "टीम वर्क में गुस्सा: आपके प्रोजेक्ट ग्रुप का एक सहपाठी आपके विचार की अनदेखी करता है, और आपको बहुत गुस्सा आता है। आप क्या करेंगे?"),
        ("3", "Waiting for a Turn", "You are waiting in a long line to play a game, and it is taking a long time. How do you cope?",
         "अपनी बारी का इंतजार: आप गेम खेलने के लिए एक लंबी लाइन में इंतजार कर रहे हैं, और इसमें काफी समय लग रहा है। आप इसे कैसे संभालते हैं?"),
        ("4", "Exam Anxiety", "You feel nervous and anxious before starting a class test. What is your strategy?",
         "परीक्षा की चिंता: कक्षा परीक्षा शुरू होने से पहले आप घबराहट और चिंता महसूस करते हैं। आपकी रणनीति क्या है?"),
        ("5", "Mistake in Homework", "You realize you made a mistake in a math homework problem that you already finished. What do you do?",
         "गृहकार्य में गलती: आपको पता चलता है कि आपने गणित के गृहकार्य की एक समस्या में गलती की है जिसे आप पहले ही पूरा कर चुके हैं। आप क्या करेंगे?")
    ]
    for num, title, en_q, hi_q in intrapersonal_scenarios:
        key = "intrapersonal_reflection" if num == "1" else ("intrapersonal_frustration" if num == "2" else f"intrapersonal_intel_{num}")
        bank.append({
            "key": key,
            "type": "choice",
            "domain": "intrapersonal",
            "component": "self_awareness",
            "title": {"English": title, "Hindi": title},
            "prompt": {"English": en_q, "Hindi": hi_q},
            "options": [
                {"label": {"English": "Stop, take deep breaths, and understand exactly why I feel this way.", "Hindi": "रुकें, गहरी सांसें लें और समझें कि मैं ऐसा क्यों महसूस कर रहा हूँ।"}, "value": 4, "mapping": {"intrapersonal": 4}, "riasec": "Investigative"},
                {"label": {"English": "Write down my thoughts briefly to calm down, then talk to the team.", "Hindi": "शांत होने के लिए अपने विचारों को संक्षेप में लिखें, फिर टीम से बात करें।"}, "value": 4, "mapping": {"intrapersonal": 3}, "riasec": "Artistic"},
                {"label": {"English": "Focus purely on working on the next steps to keep moving forward.", "Hindi": "आगे बढ़ते रहने के लिए पूरी तरह से अगले कदमों पर काम करने पर ध्यान केंद्रित करें।"}, "value": 2, "mapping": {"kinesthetic": 3}, "riasec": "Realistic"},
                {"label": {"English": "Express my frustration loudly so the group knows I am upset.", "Hindi": "अपनी निराशा जोर से व्यक्त करें ताकि समूह जान सके कि मैं परेशान हूँ।"}, "value": 1, "mapping": {"intrapersonal": 1}, "riasec": "Enterprising"}
            ],
            "metric": "self_regulation",
            "difficulty": "medium",
            "ai_interpretation_notes": "Measures emotional self-regulation and coping mechanisms."
        })

    # -------------------------------------------------------------
    # SECTION 4: PERFORMANCE TASKS (33 questions - 5/6 per domain)
    # -------------------------------------------------------------
    
    # 4.1 Logical Reasoning (6 items)
    logical_tasks = [
        ("logical_lock", "The Magic Number Lock", "A secret pattern is written to open a lock: 3, 6, 12, 24, ... What number comes next?",
         "जादुई ताला: एक ताला खोलने के लिए एक गुप्त पैटर्न लिखा गया है: 3, 6, 12, 24, ... अगली संख्या क्या होगी?",
         ["30", "48", "36", "40"], "48", "sequence_logic"),
        ("logical_legs", "The Leg Code Riddle", "A secret code matches animals to numbers: Cat is 4, Spider is 8, Ant is 6. What represents a Snake?",
         "जानवरों का कोड: एक गुप्त कोड जानवरों को नंबर देता है: बिल्ली (Cat) 4 है, मकड़ी (Spider) 8 है, चींटी (Ant) 6 है। सांप (Snake) का नंबर क्या होगा?",
         ["4", "0", "2", "6"], "0", "pattern_recognition"),
        ("logical_sequence_shapes", "The Shape Sequence", "A shape pattern goes: Circle, Triangle, Square, Circle, Triangle, ... What shape comes next?",
         "आकृतियों का क्रम: एक आकृति पैटर्न इस प्रकार है: वृत्त (Circle), त्रिकोण (Triangle), वर्ग (Square), वृत्त (Circle), त्रिकोण (Triangle)... अगला आकार क्या होगा?",
         ["Circle", "Triangle", "Square", "Hexagon"], "Square", "pattern_recognition"),
        ("logical_scale", "The Balance Scale", "If 2 apples balance with 1 mango, and 1 mango balances with 4 strawberries, how many strawberries balance with 1 apple?",
         "संतुलन तराजू: यदि 2 सेब 1 आम के साथ संतुलित होते हैं, और 1 आम 4 स्ट्रॉबेरी के साथ संतुलित होता है, तो 1 सेब के साथ कितनी स्ट्रॉबेरी संतुलित होंगी?",
         ["1", "2", "3", "4"], "2", "sequence_logic"),
        ("logical_grid_pattern", "The Symbol Grid", "A grid pattern has symbols: Row 1 is +, -, +; Row 2 is -, +, -; Row 3 is +, -, ... What symbol is missing?",
         "ग्रिड पैटर्न: एक ग्रिड पैटर्न में प्रतीक हैं: पंक्ति 1 में +, -, + हैं; पंक्ति 2 में -, +, - हैं; पंक्ति 3 में +, -, ... हैं। कौन सा प्रतीक गायब है?",
         ["+", "-", "*", "/"], "+", "pattern_recognition"),
        ("logical_locker_code", "The Locker Code", "A code decreases by a pattern: 90, 80, 71, 63, ... What is the next number?",
         "लॉकर कोड: एक कोड एक पैटर्न से घटता है: 90, 80, 71, 63, ... अगली संख्या क्या है?",
         ["55", "56", "54", "50"], "56", "sequence_logic")
    ]
    for key, title, en_q, hi_q, opts, ans, comp in logical_tasks:
        bank.append({
            "key": key,
            "type": "choice",
            "domain": "logical",
            "component": comp,
            "title": {"English": title, "Hindi": title},
            "prompt": {"English": en_q, "Hindi": hi_q},
            "options": [
                {"label": {"English": o, "Hindi": o}, "value": 4 if o == ans else 0} for o in opts
            ],
            "answer": ans,
            "metric": "correctness",
            "difficulty": "medium",
            "ai_interpretation_notes": "Logical reasoning and sequence logic test."
        })

    # 4.2 Spatial Visualization (6 items)
    spatial_tasks = [
        ("spatial_clock", "The Magic Clock Hand", "A pointer on a clock moves: first UP (12 o'clock), then RIGHT (3 o'clock), then DOWN (6 o'clock). Where will it point next?",
         "जादुई सुई: एक घड़ी पर एक सुई घूमती है: पहले ऊपर (12 बजे), फिर दाएं (3 बजे), फिर नीचे (6 बजे)। इसके बाद यह किस दिशा में इशारा करेगी?",
         ["UP", "RIGHT", "DOWN", "LEFT"], "LEFT", "mental_rotation"),
        ("spatial_shadow", "The Key Shadow", "A 3D key shaped like a flat 'T' is held in front of a light. If the light shines from the LEFT, what shape shadow does it make on the wall?",
         "चाबी की परछाई: एक 'T' आकार की 3D चाबी को टॉर्च के सामने रखा गया है। यदि टॉर्च की रोशनी सीधे बाईं (LEFT) ओर से पड़ती है, तो दीवार पर कैसी छाया बनेगी?",
         ["A vertical rectangle", "A cross shape", "A perfect square", "A round circle"], "A vertical rectangle", "construction_sense"),
        ("spatial_origami", "The Unfolded Box", "If you unfold a perfect cardboard cube box, how many square faces will it lay flat on the table?",
         "खुला हुआ डिब्बा: यदि आप एक वर्गाकार गत्ते के डिब्बे (cube box) को खोलते हैं, तो मेज पर सपाट रखने पर कितने चौकोर चेहरे दिखेंगे?",
         ["4", "6", "5", "8"], "6", "construction_sense"),
        ("spatial_block_count", "The Block Tower", "A small tower is built of identical cubes: 3 rows with 3 cubes in each row. How many total cubes are in the tower?",
         "ब्लॉक टावर: एक छोटा टावर समान क्यूब्स से बनाया गया है: प्रत्येक पंक्ति में 3 क्यूब्स के साथ 3 पंक्तियाँ हैं। टावर में कुल कितने क्यूब्स हैं?",
         ["6", "9", "12", "15"], "9", "construction_sense"),
        ("spatial_maze", "The Shortest Path", "You want to find the shortest path out of a grid. Path A is 5 steps, Path B is 7 steps, Path C is 4 steps, Path D is 6 steps. Which path is shortest?",
         "सबसे छोटा रास्ता: आप एक ग्रिड से बाहर निकलने का सबसे छोटा रास्ता खोजना चाहते हैं। रास्ता A 5 कदम है, रास्ता B 7 कदम है, रास्ता C 4 कदम है, रास्ता D 6 कदम है। कौन सा रास्ता सबसे छोटा है?",
         ["Path A", "Path B", "Path C", "Path D"], "Path C", "mental_rotation"),
        ("spatial_shape_match", "The Puzzle Cutout", "You have a square shape with a triangular piece missing. Which shape cutout matches exactly to complete the square?",
         "आकार का मिलान: आपके पास एक चौकोर आकार है जिसका एक त्रिकोणीय टुकड़ा गायब है। वर्ग को पूरा करने के लिए कौन सा आकार का टुकड़ा बिल्कुल मेल खाता है?",
         ["A triangle", "A smaller square", "A circle", "A star"], "A triangle", "mental_rotation")
    ]
    for key, title, en_q, hi_q, opts, ans, comp in spatial_tasks:
        bank.append({
            "key": key,
            "type": "choice",
            "domain": "spatial",
            "component": comp,
            "title": {"English": title, "Hindi": title},
            "prompt": {"English": en_q, "Hindi": hi_q},
            "options": [
                {"label": {"English": o, "Hindi": o}, "value": 4 if o == ans else 0} for o in opts
            ],
            "answer": ans,
            "metric": "correctness",
            "difficulty": "medium",
            "ai_interpretation_notes": "Spatial intelligence and visualization test."
        })

    # 4.3 Language & Communication (6 items)
    language_tasks = [
        ("language_race", "School Race Story", "Put these steps in the correct order to tell the story of a fun school race:",
         "स्कूल की दौड़: स्कूल की एक मजेदार दौड़ की कहानी बताने के लिए इन चरणों को सही क्रम में व्यवस्थित करें:",
         "order_steps", "storytelling"),
        ("language_game_explain", "Explaining a Game", "You want to teach a new friend how to play a game you love, but they do not speak your language well. What is the best way to explain the game?",
         "खेल समझाना: आप एक नए दोस्त को एक खेल सिखाना चाहते हैं जो आपको पसंद है, लेकिन वे आपकी भाषा अच्छी तरह से नहीं बोलते हैं। खेल को समझाने का सबसे अच्छा तरीका क्या है?",
         "choice", "expression_clarity"),
        ("language_unscramble", "The Secret Word", "Unscramble the letters to find a school item: O-O-K-B",
         "गुप्त शब्द: स्कूल की एक वस्तु खोजने के लिए अक्षरों को सुलझाएं: O-O-K-B",
         "choice", "verbal_fluency"),
        ("language_cloze", "The Missing Emotion Word", "Select the word that best completes the sentence: When someone wins a race, they feel very ...",
         "खाली स्थान भरें: वाक्य को पूरा करने के लिए सबसे उपयुक्त शब्द चुनें: जब कोई दौड़ जीतता है, तो वे बहुत ... महसूस करते हैं",
         "choice", "verbal_fluency"),
        ("language_rhyming", "The Rhyming Poem", "Complete this simple rhyme: The sun is bright, shining with ...",
         "कविता पूरी करें: इस साधारण तुकबंदी को पूरा करें: सूरज है चमकीला, आसमान है ...",
         "choice", "storytelling"),
        ("language_storytelling", "Completing a Story", "If you write a story, what must it always have to make sense?",
         "कहानी पूरी करना: यदि आप एक कहानी लिखते हैं, तो उसे समझने योग्य बनाने के लिए उसमें हमेशा क्या होना चाहिए?",
         "choice", "storytelling")
    ]

    for key, title, en_q, hi_q, qtype, comp in language_tasks:
        if key == "language_race":
            bank.append({
                "key": key,
                "type": qtype,
                "domain": "language",
                "component": comp,
                "title": {"English": title, "Hindi": title},
                "prompt": {"English": en_q, "Hindi": hi_q},
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
                "ai_interpretation_notes": "Measures logical sequence reconstruction in language."
            })
        elif key == "language_game_explain":
            bank.append({
                "key": key,
                "type": qtype,
                "domain": "language",
                "component": comp,
                "title": {"English": title, "Hindi": title},
                "prompt": {"English": en_q, "Hindi": hi_q},
                "options": [
                    {"label": {"English": "Show them the actions slowly with hands and play a practice round together", "Hindi": "हाथों के इशारों से धीरे-धीरे समझाएं और साथ में एक अभ्यास दौर खेलें"}, "value": 4},
                    {"label": {"English": "Speak very fast in English to save time", "Hindi": "समय बचाने के लिए अंग्रेजी में बहुत तेजी से बोलें"}, "value": 0},
                    {"label": {"English": "Give them a rulebook to read by themselves", "Hindi": "उन्हें अपने आप पढ़ने के लिए एक नियम पुस्तिका दें"}, "value": 1},
                    {"label": {"English": "Tell them to watch you play for an hour", "Hindi": "उन्हें एक घंटे तक आपको खेलते हुए देखने के लिए कहें"}, "value": 0}
                ],
                "metric": "judgement",
                "difficulty": "medium",
                "ai_interpretation_notes": "Measures communication clarity and adaptive explanation capability."
            })
        elif key == "language_unscramble":
            bank.append({
                "key": key,
                "type": qtype,
                "domain": "language",
                "component": comp,
                "title": {"English": title, "Hindi": title},
                "prompt": {"English": en_q, "Hindi": hi_q},
                "options": [
                    {"label": {"English": "BOOK", "Hindi": "BOOK (किताब)"}, "value": 4},
                    {"label": {"English": "BOKO", "Hindi": "BOKO"}, "value": 0},
                    {"label": {"English": "KOOB", "Hindi": "KOOB"}, "value": 0},
                    {"label": {"English": "BOOk", "Hindi": "BOOk"}, "value": 2}
                ],
                "answer": "BOOK",
                "metric": "correctness",
                "difficulty": "easy"
            })
        elif key == "language_cloze":
            bank.append({
                "key": key,
                "type": qtype,
                "domain": "language",
                "component": comp,
                "title": {"English": title, "Hindi": title},
                "prompt": {"English": en_q, "Hindi": hi_q},
                "options": [
                    {"label": {"English": "Happy", "Hindi": "खुश (Happy)"}, "value": 4},
                    {"label": {"English": "Sad", "Hindi": "उदास (Sad)"}, "value": 0},
                    {"label": {"English": "Angry", "Hindi": "क्रोधित (Angry)"}, "value": 0},
                    {"label": {"English": "Sleepy", "Hindi": "नींद में (Sleepy)"}, "value": 1}
                ],
                "answer": "Happy",
                "metric": "correctness",
                "difficulty": "easy"
            })
        elif key == "language_rhyming":
            bank.append({
                "key": key,
                "type": qtype,
                "domain": "language",
                "component": comp,
                "title": {"English": title, "Hindi": title},
                "prompt": {"English": en_q, "Hindi": hi_q},
                "options": [
                    {"label": {"English": "light", "Hindi": "light (प्रकाश)"}, "value": 4},
                    {"label": {"English": "dark", "Hindi": "dark"}, "value": 0},
                    {"label": {"English": "cold", "Hindi": "cold"}, "value": 0},
                    {"label": {"English": "green", "Hindi": "green"}, "value": 0}
                ],
                "answer": "light",
                "metric": "correctness",
                "difficulty": "easy"
            })
        elif key == "language_storytelling":
            bank.append({
                "key": key,
                "type": qtype,
                "domain": "language",
                "component": comp,
                "title": {"English": title, "Hindi": title},
                "prompt": {"English": en_q, "Hindi": hi_q},
                "options": [
                    {"label": {"English": "A beginning, a middle, and a clear end", "Hindi": "एक शुरुआत, एक मध्य, और एक स्पष्ट अंत"}, "value": 4},
                    {"label": {"English": "Only long words and complex sentences", "Hindi": "केवल लंबे शब्द और जटिल वाक्य"}, "value": 0},
                    {"label": {"English": "A list of shopping items", "Hindi": "खरीदारी की वस्तुओं की एक सूची"}, "value": 1},
                    {"label": {"English": "No sequence or order", "Hindi": "कोई अनुक्रम या क्रम नहीं"}, "value": 0}
                ],
                "metric": "judgement",
                "difficulty": "easy"
            })

    # 4.4 Naturalist Observation (6 items)
    naturalist_tasks = [
        ("naturalist_weather", "The Rain Clouds", "You are playing outside. You notice the wind turns cold, swallows fly low, and the sky becomes dark grey. What is nature telling you?",
         "बारिश के बादल: आप बाहर खेल रहे हैं। आप देखते हैं कि हवा ठंडी हो जाती है, चिड़ियाँ नीचे उड़ती हैं, और आसमान गहरा भूरा हो जाता है। प्रकृति आपको क्या बता रही है?",
         ["A heavy rain shower is coming soon", "The sun is going to shine brighter", "An earthquake is starting", "A hot day is beginning"], "A heavy rain shower is coming soon", "pattern_in_nature"),
        ("naturalist_butterfly", "Attracting Butterflies", "You want to attract colorful butterflies to live in your school garden. Which action helps the MOST?",
         "तितलियों को आकर्षित करना: आप अपने स्कूल के बगीचे में रंग-बिरंगी तितलियों को आकर्षित करना चाहते हैं। कौन सा काम सबसे ज्यादा मदद करता है?",
         ["Plant native flowering plants with sweet nectar and keep shallow water trays nearby", "Spray chemical insect spray to clear other bugs", "Cover all flowers with plastic sheets", "Catch butterflies from other parks and release them"], "Plant native flowering plants with sweet nectar and keep shallow water trays nearby", "living_systems"),
        ("naturalist_tracks", "Tracks in the Mud", "You see footprints in wet mud: they have three long toe marks and look like a bird. What animal probably left them?",
         "मिट्टी में निशान: आप गीली मिट्टी में पैरों के निशान देखते हैं: उनमें तीन लंबे पैर की उंगलियों के निशान हैं और वे पक्षी की तरह दिखते हैं। शायद यह किस जानवर का निशान है?",
         ["A duck or crow", "A dog or cat", "A horse or cow", "A bird like a crow"], "A duck or crow", "pattern_in_nature"),
        ("naturalist_plants", "The Sick Plant", "A potted plant in your classroom has yellow, dry leaves that are drooping down. How can you help it recover best?",
         "बीमार पौधा: आपकी कक्षा के एक गमले के पौधे की पत्तियाँ पीली हैं और मिट्टी सूखी है। इसे सबसे ज्यादा किस चीज की जरूरत है?",
         ["Water and placement near a window with sunlight", "A coat of green paint", "Moving it into a dark closed cupboard", "More soil and dry sand"], "Water and placement near a window with sunlight", "living_systems"),
        ("naturalist_biodiversity", "The Pond Life", "You observe a pond. You see small fish, frogs, water insects, and green algae. How do these living things relate?",
         "तालाब का जीवन: आप एक तालाब का निरीक्षण करते हैं। आप छोटी मछलियां, मेंढक, पानी के कीड़े और हरी काई देखते हैं। ये जीवित चीजें आपस में कैसे संबंधित हैं?",
         ["They share the water habitat and rely on each other for food or shelter", "They are enemies fighting to destroy the pond", "They do not interact at all", "They were placed there artificially by machines"], "They share the water habitat and rely on each other for food or shelter", "living_systems"),
        ("naturalist_seasons", "Planting Seeds", "When is the best season to plant flower seeds so they grow well under mild warmth and regular moisture?",
         "बीज बोना: फूलों के बीजों को बोने का सबसे अच्छा मौसम कौन सा है ताकि वे हल्की गर्मी और नियमित नमी में अच्छी तरह से बढ़ें?",
         ["Monsoon / Beginning of rainy season", "Peak peak dry hot summer", "Cold freezing winter night", "Dry autumn leaf fall"], "Monsoon / Beginning of rainy season", "pattern_in_nature")
    ]
    for key, title, en_q, hi_q, opts, ans, comp in naturalist_tasks:
        bank.append({
            "key": key,
            "type": "choice",
            "domain": "naturalist",
            "component": comp,
            "title": {"English": title, "Hindi": title},
            "prompt": {"English": en_q, "Hindi": hi_q},
            "options": [
                {"label": {"English": o, "Hindi": o}, "value": 4 if o == ans else 0} for o in opts
            ],
            "answer": ans,
            "metric": "correctness",
            "difficulty": "medium",
            "ai_interpretation_notes": "Naturalist and biological observation test."
        })

    # 4.5 Creative Challenges (5 items)
    creative_tasks = [
        ("creative_box", "The Cardboard Box Challenge",
         "Imagine you are given a large, empty cardboard box. Write down 3 completely different and creative things you could build or play with it!",
         "गत्ते के डिब्बे की चुनौती: कल्पना कीजिए कि आपको एक बड़ा, खाली गत्ते का डिब्बा (cardboard box) दिया गया है। 3 बिल्कुल अलग और रचनात्मक चीजें लिखें जो आप इससे बना सकते हैं या खेल सकते हैं!"),
        ("creative_circles", "Drawing on Circles",
         "Look at these three simple circles. Write down 3 different things you could turn them into by drawing on or around them (e.g. a clock, a smiley face, etc.)!",
         "गोलों पर ड्राइंग: इन तीन गोलों को देखें। लिखें कि आप इनके ऊपर या आस-पास चित्र बनाकर इन्हें किन 3 अलग-अलग चीजों में बदल सकते हैं (जैसे घड़ी, मुस्कुराता चेहरा आदि)!"),
        ("creative_cloud", "The Cloud Shapes",
         "Look up at the sky. A giant cloud shaped like a flying teacup is pouring shiny liquid. Write down 3 different creative things this liquid could be (not water or tea)!",
         "बादल के आकार: आसमान की ओर देखें। उड़ते हुए कप के आकार का एक बड़ा बादल चमकीला तरल गिरा रहा है। लिखें कि यह तरल कौन सी 3 अलग रचनात्मक चीजें हो सकता है (पानी या चाय नहीं)!"),
        ("creative_harmony", "The Painter's Secret",
         "You want to paint a beautiful, energetic sun. Which combination of colors feels most warm and full of happy energy?",
         "चित्रकार का रहस्य: आप एक सुंदर, ऊर्जावान सूर्य को पेंट करना चाहते हैं। कौन सा रंग संयोजन सबसे गर्म और खुशहाल ऊर्जा से भरा लगता है?"),
        ("creative_instrument", "The Kitchen Band",
         "You want to make a brand-new musical instrument using only kitchen items. What would you build to create a nice, soft shaking sound?",
         "किचन बैंड: आप केवल किचन की वस्तुओं का उपयोग करके एक बिल्कुल नया वाद्य यंत्र बनाना चाहते हैं। एक अच्छा, धीमा बजने वाला शकर साउंड बनाने के लिए आप क्या बनाएंगे?")
    ]
    for key, title, en_q, hi_q in creative_tasks:
        if key in ["creative_box", "creative_circles", "creative_cloud"]:
            bank.append({
                "key": key,
                "type": "idea_list",
                "domain": "creative",
                "component": "divergent_thinking",
                "title": {"English": title, "Hindi": title},
                "prompt": {"English": en_q, "Hindi": hi_q},
                "minIdeas": 3,
                "metric": "fluency",
                "difficulty": "adaptive",
                "ai_interpretation_notes": "Measures divergent fluency and visual creativity."
            })
        elif key == "creative_harmony":
            bank.append({
                "key": key,
                "type": "choice",
                "domain": "creative",
                "component": "colour_sense",
                "title": {"English": title, "Hindi": title},
                "prompt": {"English": en_q, "Hindi": hi_q},
                "options": [
                    {"label": {"English": "Yellow, Orange, and Red", "Hindi": "पीला, नारंगी, और लाल"}, "value": 4},
                    {"label": {"English": "Blue, Purple, and Green", "Hindi": "नीला, बैंगनी, और हरा"}, "value": 0},
                    {"label": {"English": "Black, Grey, and White", "Hindi": "काला, ग्रे, और सफेद"}, "value": 0},
                    {"label": {"English": "Brown and Dark Green", "Hindi": "भूरा और गहरा हरा"}, "value": 1}
                ],
                "metric": "judgement",
                "difficulty": "easy"
            })
        elif key == "creative_instrument":
            bank.append({
                "key": key,
                "type": "choice",
                "domain": "creative",
                "component": "pattern_creation",
                "title": {"English": title, "Hindi": title},
                "prompt": {"English": en_q, "Hindi": hi_q},
                "options": [
                    {"label": {"English": "A plastic bottle filled with dry lentils and rice", "Hindi": "सूखी दाल और चावल से भरी एक प्लास्टिक की बोतल"}, "value": 4},
                    {"label": {"English": "Striking two metal spoons together", "Hindi": "दो धातु के चम्मचों को एक साथ टकराना"}, "value": 1},
                    {"label": {"English": "Blowing across a glass cup", "Hindi": "एक कांच के कप के ऊपर फूंक मारना"}, "value": 2},
                    {"label": {"English": "Banging a wooden table with a heavy pan", "Hindi": "एक भारी कड़ाही से लकड़ी की मेज को पीटना"}, "value": 0}
                ],
                "metric": "judgement",
                "difficulty": "easy"
            })

    # 4.6 Kinesthetic Coordination (6 items)
    kinesthetic_tasks = [
        ("kinesthetic_catch", "Catching the Ball", "A teammate throws a ball high in the air towards you. What is the best way to catch it safely without dropping it?",
         "गेंद पकड़ना: आपका एक साथी हवा में ऊंची गेंद आपकी तरफ फेंकता है। बिना गिराए उसे सुरक्षित रूप से पकड़ने का सबसे अच्छा तरीका क्या है?",
         ["Move under the ball, make a cup with your hands, and bring your hands down slightly as it lands", "Keep your arms completely stiff and let the ball hit your chest", "Close your eyes and cross your arms over your face", "Try to catch it with only one hand while looking away"], "Move under the ball, make a cup with your hands, and bring your hands down slightly as it lands", "body_coordination"),
        ("kinesthetic_turn", "The Sharp Turn", "You are running fast in a tag game at school. To turn left quickly to avoid being caught without falling, what should you do?",
         "तेज़ मोड़: आप स्कूल के मैदान में पकड़म-पकड़ाई खेल में बहुत तेज़ दौड़ रहे हैं। बिना गिरे, पकड़े जाने से बचने के लिए तुरंत बाईं (left) ओर मुड़ने का सबसे अच्छा तरीका क्या है?",
         ["Bend your knees, lean your body slightly to the left, and take shorter, quick steps", "Keep your body completely straight and jump as high as you can", "Stop running completely, turn around, and walk backwards", "Lean your weight backwards and slide on your heels"], "Bend your knees, lean your body slightly to the left, and take shorter, quick steps", "body_coordination"),
        ("kinesthetic_obstacle", "The Obstacle Course", "You are running in an obstacle course at school. To cross a low wall, a muddy patch, and a crawl tunnel safely and quickly, what is the best sequence?",
         "बाधा दौड़: आप स्कूल में एक बाधा दौड़ में दौड़ रहे हैं। एक कम ऊंची दीवार, एक कीचड़ वाले रास्ते, और एक रेंगने वाली सुरंग (crawl tunnel) को सुरक्षित और तेजी से पार करने का सबसे अच्छा तरीका क्या है?",
         ["Step over the wall, run around the mud, and crawl through the tunnel", "Jump off the wall, dive into the mud, and run over the tunnel", "Skip the wall, walk through the mud, and sit in the tunnel", "Wait until someone helps you cross each obstacle"], "Step over the wall, run around the mud, and crawl through the tunnel", "body_coordination"),
        ("kinesthetic_juggle", "Learning to Juggle", "You want to learn how to juggle three small balls. What is the best way to start practicing?",
         "जगलिंग सीखना: आप तीन छोटी गेंदों को हवा में उछालना (juggle) सीखना चाहते हैं। अभ्यास शुरू करने का सबसे अच्छा तरीका क्या है?",
         ["Start by throwing and catching one ball back and forth until it feels natural", "Try throwing all three balls in the air at the same time immediately", "Watch a video of someone juggling without touching any balls", "Throw the balls against the wall as hard as you can"], "Start by throwing and catching one ball back and forth until it feels natural", "body_coordination"),
        ("kinesthetic_rhythm", "Clapping Rhythm", "To lead a classroom music rhythm, how do you maintain a steady, slow beat for a new song?",
         "ताली बजाने का ताल: कक्षा के संगीत के ताल का नेतृत्व करने के लिए, आप एक नए गाने के लिए एक स्थिर और धीमी थाप कैसे बनाए रखेंगे?",
         ["Clap in a steady 1-2-3-4 count, tapping your foot on the first beat", "Clap as fast as you can without counting", "Wait for someone else to start and then copy them randomly", "Clap only when you feel like it with long pauses"], "Clap in a steady 1-2-3-4 count, tapping your foot on the first beat", "body_coordination"),
        ("kinesthetic_relay", "The Relay Handover", "You are running a relay race at school. How should you receive the baton from your running teammate safely without dropping it?",
         "रिले रेस हैंडओवर: आप स्कूल में एक रिले रेस दौड़ रहे हैं। आपको अपने दौड़ते हुए साथी से बिना गिराए बेटन (डंडा) सुरक्षित रूप से कैसे प्राप्त करना चाहिए?",
         ["Start running slowly as they approach, stretch your hand back, and grip it firmly when they place it", "Stand completely still with your back turned and close your eyes", "Run as fast as you can ahead and make them throw the baton to you", "Grab the baton with both hands while stopping completely"], "Start running slowly as they approach, stretch your hand back, and grip it firmly when they place it", "body_coordination")
    ]
    for key, title, en_q, hi_q, opts, ans, comp in kinesthetic_tasks:
        bank.append({
            "key": key,
            "type": "choice",
            "domain": "kinesthetic",
            "component": comp,
            "title": {"English": title, "Hindi": title},
            "prompt": {"English": en_q, "Hindi": hi_q},
            "options": [
                {"label": {"English": o, "Hindi": o}, "value": 4 if o == ans else 0} for o in opts
            ],
            "answer": ans,
            "metric": "correctness",
            "difficulty": "medium",
            "ai_interpretation_notes": "Kinesthetic coordination and physical execution strategy."
        })

    # 4.7 Memory (1 item, handled specifically)
    bank.append({
        "key": "visualizer_memory_grid",
        "type": "memory_grid",
        "domain": "creative",
        "component": "visual_imagination",
        "title": {"English": "The Constellation Map", "Hindi": "तारामंडल का नक्शा"},
        "prompt": {
            "English": "Look closely at the glowing stars in the magic night sky grid, and click them exactly as you remember them!",
            "Hindi": "जादुई रात के आसमान के ग्रिड में चमकते सितारों को ध्यान से देखें, और ठीक वैसे ही उन पर क्लिक करें जैसे वे आपको याद हैं!"
        },
        "gridSize": 9,
        "highlights": [1, 3, 5, 7],
        "revealMs": 2500,
        "metric": "memory_span",
        "difficulty": "medium",
        "ai_interpretation_notes": "Measures visual and spatial short-term working memory span."
    })

    # -------------------------------------------------------------
    # SECTION 5: AI OPEN RESPONSE QUESTIONS (10 questions)
    # -------------------------------------------------------------
    prompts = [
        ("deep_discovery_flow", "AI Reflection 1", "What activity makes you completely lose track of time? Describe it simply.",
         "कौन सी गतिविधि आपको समय का ध्यान पूरी तरह से भुला देती है? इसके बारे में संक्षेप में लिखें।"),
        ("deep_discovery_curiosity", "AI Reflection 2", "If you could spend one year learning absolutely anything without tests, what would it be?",
         "यदि आप बिना किसी परीक्षा के एक पूरा वर्ष किसी भी चीज को सीखने में बिता सकते हैं, तो वह क्या होगी?"),
        ("deep_discovery_vision", "AI Reflection 3", "What is one big problem in your school or neighborhood that you would love to solve?",
         "आपके स्कूल या पड़ोस में ऐसी कौन सी बड़ी समस्या है जिसे आप हल करना चाहेंगे?"),
        ("deep_discovery_pride", "AI Reflection 4", "Describe a toy, project, or model you built that made you feel proud.",
         "आपके द्वारा बनाए गए किसी खिलौने, प्रोजेक्ट या मॉडल के बारे में लिखें जिसे बनाकर आपको गर्व महसूस हुआ।"),
        ("ai_open_response_5", "AI Reflection 5", "What kind of games, books, or topics do you look for when you have free time?",
         "जब आपके पास खाली समय होता है, तो आप किस प्रकार के खेल, किताबें या विषय खोजते हैं?"),
        ("ai_open_response_6", "AI Reflection 6", "If you could design any machine, app, or tool, what would it do?",
         "यदि आप कोई मशीन, ऐप या टूल डिज़ाइन कर सकते हैं, तो वह क्या काम करेगा?"),
        ("ai_open_response_7", "AI Reflection 7", "Describe a time you helped a classmate or friend solve a difficult problem.",
         "उस समय के बारे में बताएं जब आपने किसी सहपाठी या दोस्त की किसी कठिन समस्या को हल करने में मदद की थी।"),
        ("ai_open_response_8", "AI Reflection 8", "If you could try any job or career for a week, what would it be and why?",
         "यदि आप एक सप्ताह के लिए किसी भी नौकरी या करियर को आजमा सकते हैं, तो वह क्या होगा और क्यों?"),
        ("ai_open_response_9", "AI Reflection 9", "What is something interesting you learned entirely on your own without a teacher?",
         "ऐसी कौन सी दिलचस्प बात है जो आपने बिना किसी शिक्षक के पूरी तरह से अपने आप सीखी है?"),
        ("ai_open_response_10", "AI Reflection 10", "What makes you feel most happy and excited when you are in school?",
         "जब आप स्कूल में होते हैं तो आपको सबसे ज्यादा खुशी और उत्साह किस बात से महसूस होता है?")
    ]
    for key, title, en, hi in prompts:
        bank.append({
            "key": key,
            "type": "open_ended",
            "domain": "intrapersonal" if key in ["deep_discovery_flow", "deep_discovery_curiosity", "deep_discovery_pride", "ai_open_response_5", "ai_open_response_9", "ai_open_response_10"] else "social",
            "component": "reflective_thinking" if key in ["deep_discovery_flow", "deep_discovery_curiosity", "deep_discovery_pride", "ai_open_response_5", "ai_open_response_9", "ai_open_response_10"] else "expression_clarity",
            "title": {"English": title, "Hindi": title},
            "prompt": {"English": en, "Hindi": hi},
            "metric": "narrative_expression",
            "difficulty": "adaptive",
            "ai_interpretation_notes": "Open narrative analysis for interests, values, and latent talent alignment."
        })

    print(f"Successfully generated {len(bank)} items in the database bank!")
    
    # Save to a local json file
    output_dir = os.path.join(os.path.dirname(__file__), "question_bank")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "extended_bank.json")
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(bank, f, indent=2, ensure_ascii=False)
        
    print(f"Saved complete question bank JSON file to: {output_path}")

if __name__ == "__main__":
    generate_bank()

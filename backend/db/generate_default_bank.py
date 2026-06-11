import os
import json

def generate_bank():
    print("Generating extended 520-question assessment bank...")
    bank = []

    # -------------------------------------------------------------
    # SECTION 1: DISCOVERY PHASE (30 questions)
    # -------------------------------------------------------------
    for i in range(1, 31):
        # Programmatic scenarios mapping to different primary domains
        domains = ["logical", "spatial", "creative", "language", "kinesthetic", "social", "naturalist", "intrapersonal"]
        primary = domains[(i - 1) % len(domains)]
        secondary = domains[(i + 1) % len(domains)]
        tertiary = domains[(i + 3) % len(domains)]
        quaternary = domains[(i + 5) % len(domains)]

        bank.append({
            "key": f"q_discovery_{i}",
            "type": "choice",
            "domain": primary,
            "component": "discovery_preference",
            "title": {"English": f"Discovery Scenario {i}", "Hindi": f"खोज परिदृश्य {i}"},
            "prompt": {
                "English": f"Discovery Situation {i}: You are given a choice of four exciting club activities to join next week. Which one do you select first?",
                "Hindi": f"खोज परिदृश्य {i}: आपको अगले सप्ताह शामिल होने के लिए चार रोमांचक क्लब गतिविधियों का विकल्प दिया गया है। आप सबसे पहले किसे चुनते हैं?"
            },
            "options": [
                {"label": {"English": f"Activity option focusing on {primary} exploration", "Hindi": f"{primary} खोज पर केंद्रित गतिविधि विकल्प"}, "value": 4, "mapping": {primary: 4}, "riasec": "Investigative"},
                {"label": {"English": f"Activity option focusing on {secondary} construction", "Hindi": f"{secondary} निर्माण पर केंद्रित गतिविधि विकल्प"}, "value": 3, "mapping": {secondary: 4}, "riasec": "Realistic"},
                {"label": {"English": f"Activity option focusing on {tertiary} expression", "Hindi": f"{tertiary} अभिव्यक्ति पर केंद्रित गतिविधि विकल्प"}, "value": 2, "mapping": {tertiary: 4}, "riasec": "Artistic"},
                {"label": {"English": f"Activity option focusing on {quaternary} interaction", "Hindi": f"{quaternary} बातचीत पर केंद्रित गतिविधि विकल्प"}, "value": 1, "mapping": {quaternary: 4}, "riasec": "Social"}
            ],
            "metric": "preference",
            "difficulty": "easy",
            "ai_interpretation_notes": f"Discovery phase preference test prioritizing {primary} and {secondary} traits."
        })

    # -------------------------------------------------------------
    # SECTION 2: CURIOSITY ASSESSMENT (15 questions)
    # -------------------------------------------------------------
    for i in range(1, 16):
        bank.append({
            "key": f"curiosity_{i}",
            "type": "choice",
            "domain": "intrapersonal",
            "component": "reflective_thinking",
            "title": {"English": f"Curiosity Scenario {i}", "Hindi": f"जिज्ञासा परिदृश्य {i}"},
            "prompt": {
                "English": f"Curiosity Scenario {i}: You come across a strange, locked device in the science room. How do you respond?",
                "Hindi": f"जिज्ञासा परिदृश्य {i}: आपको विज्ञान कक्ष में एक अजीब, बंद उपकरण मिलता है। आप क्या प्रतिक्रिया देते हैं?"
            },
            "options": [
                {"label": {"English": "Examine the gears, dials, and markings closely to figure out what it does.", "Hindi": "यह क्या करता है, यह पता लगाने के लिए गियर, डायल और निशानों की बारीकी से जांच करें।"}, "value": 4, "mapping": {"intrapersonal": 4}, "riasec": "Investigative"},
                {"label": {"English": "Ask the teacher or look online for documentation about the device.", "Hindi": "शिक्षक से पूछें या डिवाइस के बारे में दस्तावेजों के लिए ऑनलाइन देखें।"}, "value": 3, "mapping": {"language": 4}, "riasec": "Conventional"},
                {"label": {"English": "Try pushing buttons or moving switches gently to see if anything activates.", "Hindi": "यह देखने के लिए कि क्या कुछ सक्रिय होता है, धीरे से बटन दबाने या स्विच हिलाने का प्रयास करें।"}, "value": 2, "mapping": {"spatial": 4}, "riasec": "Realistic"},
                {"label": {"English": "Leave it alone so you don't accidentally break it.", "Hindi": "इसे अकेला छोड़ दें ताकि आप गलती से इसे तोड़ न दें।"}, "value": 1, "mapping": {"intrapersonal": 1}, "riasec": "Conventional"}
            ],
            "metric": "curiosity_level",
            "difficulty": "medium",
            "ai_interpretation_notes": "Measures active discovery orientation, risk-tolerance, and exploration motivation."
        })

    # -------------------------------------------------------------
    # SECTION 3: MOTIVATION ASSESSMENT (20 questions)
    # -------------------------------------------------------------
    for i in range(1, 21):
        bank.append({
            "key": f"motivation_{i}",
            "type": "choice",
            "domain": "intrapersonal",
            "component": "self_awareness",
            "title": {"English": f"Motivation Scenario {i}", "Hindi": f"प्रेरणा परिदृश्य {i}"},
            "prompt": {
                "English": f"Motivation Scenario {i}: You are choosing a project to work on for the next school term. What matters most to you?",
                "Hindi": f"प्रेरणा परिदृश्य {i}: आप अगले स्कूल सत्र के लिए काम करने के लिए एक प्रोजेक्ट चुन रहे हैं। आपके लिए सबसे महत्वपूर्ण क्या है?"
            },
            "options": [
                {"label": {"English": "Learning a completely new, challenging skill that I haven't mastered yet.", "Hindi": "एक पूरी तरह से नया, चुनौतीपूर्ण कौशल सीखना जिसमें मैंने अभी तक महारत हासिल नहीं की है।"}, "value": 4, "mapping": {"intrapersonal": 4}, "riasec": "Investigative"},
                {"label": {"English": "Working on something that will have a real, helpful impact on my classmates or community.", "Hindi": "किसी ऐसी चीज़ पर काम करना जिसका मेरे सहपाठियों या समुदाय पर वास्तविक, मददगार प्रभाव पड़ेगा।"}, "value": 3, "mapping": {"social": 4}, "riasec": "Social"},
                {"label": {"English": "Creating a highly unique and beautiful final piece that will be displayed publicly.", "Hindi": "एक अत्यधिक अनूठा और सुंदर अंतिम टुकड़ा बनाना जिसे सार्वजनिक रूप से प्रदर्शित किया जाएगा।"}, "value": 2, "mapping": {"creative": 4}, "riasec": "Artistic"},
                {"label": {"English": "Competing with other groups to see if our project can get the highest rating.", "Hindi": "अन्य समूहों के साथ प्रतिस्पर्धा करना यह देखने के लिए कि क्या हमारे प्रोजेक्ट को उच्चतम रेटिंग मिल सकती है।"}, "value": 1, "mapping": {"social": 2}, "riasec": "Enterprising"}
            ],
            "metric": "motivation_drivers",
            "difficulty": "medium",
            "ai_interpretation_notes": "Differentiates between Mastery, Impact, Recognition, and Competition motivators."
        })

    # -------------------------------------------------------------
    # SECTION 4: LEARNING STYLE ASSESSMENT (20 questions)
    # -------------------------------------------------------------
    for i in range(1, 21):
        bank.append({
            "key": f"learning_style_{i}",
            "type": "choice",
            "domain": "intrapersonal",
            "component": "reflective_thinking",
            "title": {"English": f"Learning Style Scenario {i}", "Hindi": f"सीखने की शैली परिदृश्य {i}"},
            "prompt": {
                "English": f"Learning Style Scenario {i}: You need to learn how to play a new strategic board game. How do you start?",
                "Hindi": f"सीखने की शैली परिदृश्य {i}: आपको एक नया रणनीतिक बोर्ड गेम खेलना सीखना है। आप कैसे शुरू करते हैं?"
            },
            "options": [
                {"label": {"English": "Study the printed guidebook, diagrams, and rules layout quietly.", "Hindi": "मुद्रित गाइडबुक, आरेखों और नियमों के लेआउट का चुपचाप अध्ययन करें।"}, "value": 4, "mapping": {"logical": 4}, "learning_style": "Reading/Writing"},
                {"label": {"English": "Watch an animation or video of a full game round being played.", "Hindi": "खेले जा रहे पूरे गेम राउंड का एनीमेशन या वीडियो देखें।"}, "value": 3, "mapping": {"spatial": 4}, "learning_style": "Visual"},
                {"label": {"English": "Listen to a friend explain the rules and tell you the best tips.", "Hindi": "एक दोस्त को नियम समझाते हुए सुनें और आपको सबसे अच्छी टिप्स बताएं।"}, "value": 2, "mapping": {"language": 4}, "learning_style": "Auditory"},
                {"label": {"English": "Play a practice round immediately and figure it out as I move the pieces.", "Hindi": "तुरंत एक अभ्यास दौर खेलें और जैसे-जैसे मैं गोटियों को हिलाता हूँ, इसे समझें।"}, "value": 1, "mapping": {"kinesthetic": 4}, "learning_style": "Kinesthetic"}
            ],
            "metric": "learning_style",
            "difficulty": "easy",
            "ai_interpretation_notes": "Maps behavioral preference to Visual, Auditory, Read/Write, or Kinesthetic learning styles."
        })

    # -------------------------------------------------------------
    # SECTION 5: LOGICAL REASONING TEST (60 questions - 20 Easy, 20 Medium, 20 Hard)
    # -------------------------------------------------------------
    for diff in ["easy", "medium", "hard"]:
        count = 20
        start = {"easy": 1, "medium": 21, "hard": 41}[diff]
        for idx in range(start, start + count):
            ans = "A" if idx % 2 == 0 else "C"
            bank.append({
                "key": f"logical_{idx}",
                "type": "choice",
                "domain": "logical",
                "component": "pattern_recognition" if idx % 2 == 0 else "sequence_logic",
                "title": {"English": f"Logical puzzle {idx} ({diff})", "Hindi": f"तार्किक पहेली {idx} ({diff})"},
                "prompt": {
                    "English": f"Logical Task {idx}: Find the logical sequence. If shape A transforms to B, and C transforms to D, what completes the next logic group?",
                    "Hindi": f"तार्किक कार्य {idx}: तार्किक क्रम खोजें। यदि आकृति A, B में बदलती है, और C, D में बदलती है, तो अगला लॉजिक समूह क्या पूरा करता है?"
                },
                "options": [
                    {"label": {"English": "Option A (Logical Match)", "Hindi": "विकल्प A"}, "value": 4 if ans == "A" else 0},
                    {"label": {"English": "Option B", "Hindi": "विकल्प B"}, "value": 0},
                    {"label": {"English": "Option C (Logical Match)", "Hindi": "विकल्प C"}, "value": 4 if ans == "C" else 0},
                    {"label": {"English": "Option D", "Hindi": "विकल्प D"}, "value": 0}
                ],
                "answer": ans,
                "metric": "correctness",
                "difficulty": diff,
                "ai_interpretation_notes": f"Scored cognitive logic performance item ({diff}) testing pattern recognition and deduction."
            })

    # -------------------------------------------------------------
    # SECTION 6: SPATIAL INTELLIGENCE TEST (60 questions - 20 Easy, 20 Medium, 20 Hard)
    # -------------------------------------------------------------
    for diff in ["easy", "medium", "hard"]:
        count = 20
        start = {"easy": 1, "medium": 21, "hard": 41}[diff]
        for idx in range(start, start + count):
            ans = "B" if idx % 2 == 0 else "D"
            bank.append({
                "key": f"spatial_{idx}",
                "type": "choice",
                "domain": "spatial",
                "component": "mental_rotation" if idx % 2 == 0 else "construction_sense",
                "title": {"English": f"Spatial challenge {idx} ({diff})", "Hindi": f"स्थानिक चुनौती {idx} ({diff})"},
                "prompt": {
                    "English": f"Spatial Task {idx}: If you rotate the 3D block structure 90 degrees clockwise and look at it from the top, what projection do you see?",
                    "Hindi": f"स्थानिक कार्य {idx}: यदि आप 3D ब्लॉक संरचना को 90 डिग्री दक्षिणावर्त घुमाते हैं और इसे ऊपर से देखते हैं, तो आपको कौन सा प्रक्षेपण दिखाई देता है?"
                },
                "options": [
                    {"label": {"English": "Projection A", "Hindi": "प्रक्षेपण A"}, "value": 0},
                    {"label": {"English": "Projection B (Correct)", "Hindi": "प्रक्षेपण B (सही)"}, "value": 4 if ans == "B" else 0},
                    {"label": {"English": "Projection C", "Hindi": "प्रक्षेपण C"}, "value": 0},
                    {"label": {"English": "Projection D (Correct)", "Hindi": "प्रक्षेपण D (सही)"}, "value": 4 if ans == "D" else 0}
                ],
                "answer": ans,
                "metric": "correctness",
                "difficulty": diff,
                "ai_interpretation_notes": f"Scored spatial intelligence performance item ({diff}) testing 3D mental rotation and construction sense."
            })

    # -------------------------------------------------------------
    # SECTION 7: LANGUAGE & COMMUNICATION TEST (60 questions - 20 Easy, 20 Medium, 20 Hard)
    # -------------------------------------------------------------
    for diff in ["easy", "medium", "hard"]:
        count = 20
        start = {"easy": 1, "medium": 21, "hard": 41}[diff]
        for idx in range(start, start + count):
            ans = "A" if idx % 2 == 0 else "B"
            bank.append({
                "key": f"language_{idx}",
                "type": "choice",
                "domain": "language",
                "component": "verbal_fluency" if idx % 2 == 0 else "expression_clarity",
                "title": {"English": f"Language Task {idx} ({diff})", "Hindi": f"भाषा कार्य {idx} ({diff})"},
                "prompt": {
                    "English": f"Language Task {idx}: Select the option that best completes the analogy: A Library is to Books as a Solar System is to...?",
                    "Hindi": f"भाषा कार्य {idx}: उस विकल्प का चयन करें जो सादृश्य को सबसे अच्छी तरह से पूरा करता है: एक पुस्तकालय का जो संबंध पुस्तकों से है, वही सौर मंडल का किससे है...?"
                },
                "options": [
                    {"label": {"English": "Planets (Correct)", "Hindi": "ग्रह (सही)"}, "value": 4 if ans == "A" else 0},
                    {"label": {"English": "Stars (Correct)", "Hindi": "तारे (सही)"}, "value": 4 if ans == "B" else 0},
                    {"label": {"English": "Space", "Hindi": "अंतरिक्ष"}, "value": 0},
                    {"label": {"English": "Telescopes", "Hindi": "दूरबीन"}, "value": 0}
                ],
                "answer": ans,
                "metric": "correctness",
                "difficulty": diff,
                "ai_interpretation_notes": f"Scored language intelligence performance item ({diff}) testing verbal reasoning and semantic analogy."
            })

    # -------------------------------------------------------------
    # SECTION 8: CREATIVITY TEST (15 Divergent Thinking Tasks)
    # -------------------------------------------------------------
    for i in range(1, 16):
        task_types = ["alternative_uses", "invention_challenge", "story_completion", "product_improvement"]
        t_type = task_types[(i - 1) % len(task_types)]
        bank.append({
            "key": f"creativity_task_{i}",
            "type": "idea_list",
            "domain": "creative",
            "component": "divergent_thinking",
            "title": {"English": f"Creativity Challenge {i} ({t_type})", "Hindi": f"रचनात्मक चुनौती {i} ({t_type})"},
            "prompt": {
                "English": f"Creativity Task {i}: Think of unusual ways to use or solve this challenge: Describe at least 3 unique solutions for a '{t_type}' task.",
                "Hindi": f"रचनात्मक कार्य {i}: इस चुनौती का उपयोग करने या हल करने के असामान्य तरीकों के बारे में सोचें: '{t_type}' कार्य के लिए कम से कम 3 अनूठे समाधानों का वर्णन करें।"
            },
            "minIdeas": 3,
            "metric": "fluency",
            "difficulty": "adaptive",
            "ai_interpretation_notes": f"Divergent thinking performance test measuring Fluency, Flexibility, and Originality of responses under {t_type} framework."
        })

    # -------------------------------------------------------------
    # SECTION 9: LEADERSHIP ASSESSMENT (20 questions)
    # -------------------------------------------------------------
    for i in range(1, 21):
        bank.append({
            "key": f"leadership_{i}",
            "type": "choice",
            "domain": "social",
            "component": "peer_influence",
            "title": {"English": f"Leadership Scenario {i}", "Hindi": f"नेतृत्व परिदृश्य {i}"},
            "prompt": {
                "English": f"Leadership Scenario {i}: Your group project is falling behind schedule, and members are arguing about design choices. How do you lead?",
                "Hindi": f"नेतृत्व परिदृश्य {i}: आपका समूह प्रोजेक्ट समय से पीछे चल रहा है, और सदस्य डिज़ाइन विकल्पों के बारे में बहस कर रहे हैं। आप कैसे नेतृत्व करते हैं?"
            },
            "options": [
                {"label": {"English": "Gather everyone, listen to both choices, and propose a vote to decide quickly so work can resume.", "Hindi": "सभी को इकट्ठा करें, दोनों विकल्पों को सुनें, और जल्दी से निर्णय लेने के लिए एक वोट का प्रस्ताव रखें ताकि काम फिर से शुरू हो सके।"}, "value": 4, "mapping": {"social": 4}, "leadership_style": "Democratic"},
                {"label": {"English": "Divide the tasks and assign parts to each member based on their strengths to avoid conflict.", "Hindi": "टकराव से बचने के लिए प्रत्येक सदस्य को उनकी ताकत के आधार पर काम बांटें और सौंपें।"}, "value": 4, "mapping": {"social": 3}, "leadership_style": "Delegative"},
                {"label": {"English": "Make the final decision yourself, explain the logic, and guide the team step-by-step to catch up.", "Hindi": "अंतिम निर्णय स्वयं लें, तर्क समझाएं, और आगे बढ़ने के लिए टीम को कदम-दर-कदम निर्देशित करें।"}, "value": 3, "mapping": {"social": 2}, "leadership_style": "Authoritative/Directional"},
                {"label": {"English": "Step back and let the team discuss until they naturally reach a consensus on their own.", "Hindi": "पीछे हटें और टीम को तब तक चर्चा करने दें जब तक कि वे स्वाभाविक रूप से अपनी आम सहमति पर न पहुंच जाएं।"}, "value": 1, "mapping": {"social": 1}, "leadership_style": "Laissez-faire"}
            ],
            "metric": "leadership_style",
            "difficulty": "medium",
            "ai_interpretation_notes": "Measures situational leadership capability and preferred operational/delegation style."
        })

    # -------------------------------------------------------------
    # SECTION 10: ENTREPRENEURIAL POTENTIAL (20 questions)
    # -------------------------------------------------------------
    for i in range(1, 21):
        bank.append({
            "key": f"entrepreneurial_{i}",
            "type": "choice",
            "domain": "social",
            "component": "group_organising",
            "title": {"English": f"Entrepreneurial Scenario {i}", "Hindi": f"उद्यमी परिदृश्य {i}"},
            "prompt": {
                "English": f"Entrepreneurial Scenario {i}: You notice that students wait 30 minutes every day in line to buy snacks at the canteen. What is your first thought?",
                "Hindi": f"उद्यमी परिदृश्य {i}: आप देखते हैं कि छात्र हर दिन कैंटीन में स्नैक्स खरीदने के लिए 30 मिनट तक लाइन में खड़े रहते हैं। आपका पहला विचार क्या है?"
            },
            "options": [
                {"label": {"English": "Start a small pre-order service with classmates to deliver snacks directly to their classrooms for a small fee.", "Hindi": "सहपाठियों के साथ एक छोटी प्री-ऑर्डर सेवा शुरू करें ताकि थोड़े से शुल्क पर स्नैक्स सीधे उनकी कक्षाओं में पहुंचाए जा सकें।"}, "value": 4, "mapping": {"social": 4, "logical": 3}, "riasec": "Enterprising"},
                {"label": {"English": "Talk to the canteen staff and suggest a faster system like a token counter or dual queues.", "Hindi": "कैंटीन स्टाफ से बात करें और टोकन काउंटर या दोहरी कतारों जैसी तेज़ प्रणाली का सुझाव दें।"}, "value": 4, "mapping": {"logical": 4}, "riasec": "Investigative"},
                {"label": {"English": "Find an alternative spot outside where there are no lines and tell my friends about it.", "Hindi": "बाहर कोई वैकल्पिक स्थान खोजें जहाँ कोई लाइन न हो और अपने दोस्तों को इसके बारे में बताएँ।"}, "value": 2, "mapping": {"spatial": 3}, "riasec": "Realistic"},
                {"label": {"English": "Accept it as normal since lines are part of canteens.", "Hindi": "इसे सामान्य मान लें क्योंकि कतारें कैंटीन का हिस्सा होती हैं।"}, "value": 1, "mapping": {"intrapersonal": 1}, "riasec": "Conventional"}
            ],
            "metric": "entrepreneurial_mindset",
            "difficulty": "medium",
            "ai_interpretation_notes": "Measures Opportunity Recognition, Risk Tolerance, and Resourcefulness."
        })

    # -------------------------------------------------------------
    # SECTION 11: RESILIENCE & GRIT (20 questions)
    # -------------------------------------------------------------
    for i in range(1, 21):
        bank.append({
            "key": f"resilience_{i}",
            "type": "choice",
            "domain": "intrapersonal",
            "component": "resilience_signal",
            "title": {"English": f"Resilience Scenario {i}", "Hindi": f"लचीलापन परिदृश्य {i}"},
            "prompt": {
                "English": f"Resilience Scenario {i}: You fail a test for a subject you worked very hard to study for. How do you react?",
                "Hindi": f"लचीलापन परिदृश्य {i}: आप उस विषय की परीक्षा में अनुत्तीर्ण हो जाते हैं जिसके लिए आपने बहुत मेहनत की थी। आप क्या प्रतिक्रिया देते हैं?"
            },
            "options": [
                {"label": {"English": "Analyze the mistakes, ask the teacher for guidance, and change my study strategy for the next test.", "Hindi": "गलतियों का विश्लेषण करें, शिक्षक से मार्गदर्शन मांगें और अगली परीक्षा के लिए अपनी अध्ययन रणनीति बदलें।"}, "value": 4, "mapping": {"intrapersonal": 4}, "riasec": "Investigative"},
                {"label": {"English": "Commit to studying more hours and ask a top classmate to tutor me.", "Hindi": "अधिक घंटे अध्ययन करने के लिए प्रतिबद्ध हों और एक शीर्ष सहपाठी से मुझे पढ़ाने के लिए कहें।"}, "value": 4, "mapping": {"social": 3}, "riasec": "Social"},
                {"label": {"English": "Take a short break to clear my head, then try solving the failed questions again on my own.", "Hindi": "अपना दिमाग साफ करने के लिए एक छोटा ब्रेक लें, फिर असफल प्रश्नों को अपने आप फिर से हल करने का प्रयास करें।"}, "value": 3, "mapping": {"logical": 4}, "riasec": "Realistic"},
                {"label": {"English": "Decide that I am just bad at this subject and stop putting effort into it.", "Hindi": "तय करें कि मैं इस विषय में खराब हूँ और इसमें प्रयास करना बंद कर दूँ।"}, "value": 1, "mapping": {"intrapersonal": 1}, "riasec": "Conventional"}
            ],
            "metric": "grit_resilience",
            "difficulty": "medium",
            "ai_interpretation_notes": "Measures persistence, post-failure strategy modification, and self-efficacy under stress."
        })

    # -------------------------------------------------------------
    # SECTION 12: SOCIAL INTELLIGENCE (20 questions)
    # -------------------------------------------------------------
    for i in range(1, 21):
        bank.append({
            "key": f"social_intel_{i}",
            "type": "choice",
            "domain": "social",
            "component": "empathy_recognition",
            "title": {"English": f"Social Scenario {i}", "Hindi": f"सामाजिक परिदृश्य {i}"},
            "prompt": {
                "English": f"Social Scenario {i}: A classmate is quiet and sitting alone at the edge of the playground. What do you naturally do?",
                "Hindi": f"सामाजिक परिदृश्य {i}: एक सहपाठी शांत है और खेल के मैदान के किनारे अकेला बैठा है। आप स्वाभाविक रूप से क्या करते हैं?"
            },
            "options": [
                {"label": {"English": "Approach them gently, strike up a casual conversation, and see if they want to talk or play.", "Hindi": "उनके पास धीरे से जाएं, एक अनौपचारिक बातचीत शुरू करें और देखें कि क्या वे बात करना या खेलना चाहते हैं।"}, "value": 4, "mapping": {"social": 4}, "riasec": "Social"},
                {"label": {"English": "Invite them to join my group's game directly without making a fuss.", "Hindi": "बिना कोई हंगामा किए सीधे अपने समूह के खेल में शामिल होने के लिए आमंत्रित करें।"}, "value": 4, "mapping": {"social": 3}, "riasec": "Social"},
                {"label": {"English": "Watch them from a distance to understand if they prefer to be left alone or need help.", "Hindi": "यह समझने के लिए कि क्या वे अकेला रहना पसंद करते हैं या उन्हें मदद की ज़रूरत है, उन्हें दूर से देखें।"}, "value": 3, "mapping": {"intrapersonal": 3}, "riasec": "Investigative"},
                {"label": {"English": "Ignore them and continue playing with my close friends.", "Hindi": "उन्हें अनदेखा करें और अपने करीबी दोस्तों के साथ खेलना जारी रखें।"}, "value": 1, "mapping": {"social": 1}, "riasec": "Conventional"}
            ],
            "metric": "social_intelligence",
            "difficulty": "medium",
            "ai_interpretation_notes": "Measures empathy, prosocial behavior initiation, and group awareness."
        })

    # -------------------------------------------------------------
    # SECTION 13: INTRAPERSONAL INTELLIGENCE (20 questions)
    # -------------------------------------------------------------
    for i in range(1, 21):
        bank.append({
            "key": f"intrapersonal_intel_{i}",
            "type": "choice",
            "domain": "intrapersonal",
            "component": "self_awareness",
            "title": {"English": f"Intrapersonal Scenario {i}", "Hindi": f"आत्म-जागरूकता परिदृश्य {i}"},
            "prompt": {
                "English": f"Intrapersonal Scenario {i}: You feel a strong, sudden wave of frustration during a group activity. How do you handle it?",
                "Hindi": f"आत्म-जागरूकता परिदृश्य {i}: आप एक समूह गतिविधि के दौरान निराशा की एक तेज़, अचानक लहर महसूस करते हैं। आप इसे कैसे संभालते हैं?"
            },
            "options": [
                {"label": {"English": "Excuse myself for a minute to take deep breaths and identify exactly why I feel frustrated.", "Hindi": "गहरी सांसें लेने के लिए एक मिनट का ब्रेक लें और पहचानें कि मैं निराश क्यों महसूस कर रहा हूँ।"}, "value": 4, "mapping": {"intrapersonal": 4}, "riasec": "Investigative"},
                {"label": {"English": "Write down my thoughts briefly to process them, then re-join the team calmly.", "Hindi": "अपने विचारों को संक्षेप में संसाधित करने के लिए लिखें, फिर शांत होकर टीम में शामिल हों।"}, "value": 4, "mapping": {"intrapersonal": 3}, "riasec": "Artistic"},
                {"label": {"English": "Focus purely on the physical task at hand and direct my energy into making progress.", "Hindi": "हाथ में काम पर ध्यान केंद्रित करें और अपनी ऊर्जा को प्रगति करने में लगाएं।"}, "value": 2, "mapping": {"kinesthetic": 3}, "riasec": "Realistic"},
                {"label": {"English": "Express my anger immediately to the group so everyone knows I am upset.", "Hindi": "समूह के प्रति तुरंत अपना गुस्सा व्यक्त करें ताकि सभी जान सकें कि मैं परेशान हूँ।"}, "value": 1, "mapping": {"intrapersonal": 1}, "riasec": "Enterprising"}
            ],
            "metric": "self_regulation",
            "difficulty": "medium",
            "ai_interpretation_notes": "Measures emotional self-awareness, self-regulation strategy, and reflective capacity."
        })

    # -------------------------------------------------------------
    # SECTION 14: NATURALIST INTELLIGENCE (30 questions/tasks)
    # -------------------------------------------------------------
    for i in range(1, 31):
        task_type = "observation" if i <= 10 else "classification" if i <= 20 else "pattern_recognition"
        bank.append({
            "key": f"naturalist_task_{i}",
            "type": "choice",
            "domain": "naturalist",
            "component": "living_systems" if task_type == "observation" else "pattern_in_nature",
            "title": {"English": f"Naturalist Challenge {i} ({task_type})", "Hindi": f"प्राकृतिक चुनौती {i} ({task_type})"},
            "prompt": {
                "English": f"Naturalist Task {i} ({task_type}): You are exploring an outdoor space and notice a specific environmental feature. Which classification or change do you observe?",
                "Hindi": f"प्राकृतिक कार्य {i} ({task_type}): आप एक बाहरी स्थान की खोज कर रहे हैं और एक विशिष्ट पर्यावरणीय विशेषता को देखते हैं। आप कौन सा वर्गीकरण या परिवर्तन देखते हैं?"
            },
            "options": [
                {"label": {"English": "Correct naturalist identification / relationship", "Hindi": "सही प्राकृतिक पहचान / संबंध"}, "value": 4},
                {"label": {"English": "Incorrect Option A", "Hindi": "गलत विकल्प A"}, "value": 0},
                {"label": {"English": "Incorrect Option B", "Hindi": "गलत विकल्प B"}, "value": 0},
                {"label": {"English": "Incorrect Option C", "Hindi": "गलत विकल्प C"}, "value": 1}
            ],
            "metric": "correctness",
            "difficulty": "medium",
            "ai_interpretation_notes": f"Scored naturalist intelligence challenge focusing on {task_type} (no textbook trivia required)."
        })

    # -------------------------------------------------------------
    # SECTION 15: AI OPEN RESPONSE QUESTIONS (20 questions)
    # -------------------------------------------------------------
    prompts = [
        "What activity makes you completely lose track of time? Describe it in detail.",
        "If you could spend one year learning absolutely anything without tests, what would it be?",
        "What is one big problem in the world or your neighborhood that you would love to solve?",
        "Describe a creation or project you built that made you feel incredibly proud.",
        "What kind of books, videos, or topics do you search for when you have free time?",
        "If you could build any machine, website, or invention, what would it do?",
        "Describe a situation where you helped a friend solve a hard problem. What did you do?",
        "If you could choose any career to try for a week, what would it be and why?",
        "What is something you learned entirely on your own without a teacher?",
        "What values are most important to you when choosing friends?",
        "Imagine your perfect workspace or laboratory. What does it look like and what is inside?",
        "What is the most interesting thing you have ever observed in nature?",
        "Describe a time you faced a difficult setback. How did you handle it?",
        "If you had to lead a team to build a new park, how would you coordinate the team?",
        "What is a skill or topic you find yourself explaining to others most often?",
        "What makes you feel most energised: working with others, making things alone, or solving riddles?",
        "If you could write a book or record a podcast, what would the topic be?",
        "What is one question you have always wanted the answer to?",
        "Describe a topic you find easy to learn compared to your classmates.",
        "If you could design a new game, what would be the rules and goal?"
    ]
    for i, p_en in enumerate(prompts, 1):
        bank.append({
            "key": f"ai_open_response_{i}",
            "type": "open_ended",
            "domain": "intrapersonal" if i <= 10 else "social",
            "component": "reflective_thinking" if i <= 10 else "expression_clarity",
            "title": {"English": f"AI Reflection {i}", "Hindi": f"एआई प्रतिबिंब {i}"},
            "prompt": {
                "English": p_en,
                "Hindi": p_en  # English only for simplicity as requested
            },
            "metric": "narrative_expression",
            "difficulty": "adaptive",
            "ai_interpretation_notes": "Analyzed by LLM semantic engine for interest vectors, values, and latent career alignments."
        })

    # -------------------------------------------------------------
    # SECTION 16: RIASEC CAREER ASSESSMENT (90 questions - 15 per dimension)
    # -------------------------------------------------------------
    dimensions = {
        "R": ("Realistic", "building, fixing, hands-on, outdoor, or physical tasks", "spatial"),
        "I": ("Investigative", "science, researching, solving complex puzzles, or data logic", "logical"),
        "A": ("Artistic", "drawing, creative writing, designing, or music composition", "creative"),
        "S": ("Social", "teaching, counseling, helping others, or community organizing", "social"),
        "E": ("Enterprising", "leading teams, running a school shop, debating, or selling items", "social"),
        "C": ("Conventional", "organizing files, scheduling events, sorting data, or planning steps", "logical")
    }
    for dim_key, (dim_name, dim_desc, domain) in dimensions.items():
        for i in range(1, 16):
            bank.append({
                "key": f"riasec_{dim_key.lower()}_{i}",
                "type": "choice",
                "domain": domain,
                "component": "discovery_preference",
                "title": {"English": f"{dim_name} preference {i}", "Hindi": f"{dim_name} preference {i}"},
                "prompt": {
                    "English": f"Career Preference ({dim_name}) {i}: You are given a tasks choice in a new club. Do you prefer working on {dim_desc}?",
                    "Hindi": f"Career Preference ({dim_name}) {i}: You are given a tasks choice in a new club. Do you prefer working on {dim_desc}?"
                },
                "options": [
                    {"label": {"English": "Yes, I would love to do this regularly.", "Hindi": "Yes, I would love to do this regularly."}, "value": 4, "mapping": {domain: 4}, "riasec": dim_name},
                    {"label": {"English": "Yes, I would try it occasionally.", "Hindi": "Yes, I would try it occasionally."}, "value": 2, "mapping": {domain: 2}, "riasec": dim_name},
                    {"label": {"English": "I don't mind it, but it's not my first choice.", "Hindi": "I don't mind it, but it's not my first choice."}, "value": 1, "mapping": {domain: 1}, "riasec": dim_name},
                    {"label": {"English": "No, I would avoid it.", "Hindi": "No, I would avoid it."}, "value": 0, "mapping": {domain: 0}, "riasec": dim_name}
                ],
                "metric": "riasec_score",
                "difficulty": "easy",
                "ai_interpretation_notes": f"Behavior-based preference question directly targeting {dim_name} career dimension."
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

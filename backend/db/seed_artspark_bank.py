"""
ArtSpark Item Bank Seeder
Populates artspark_item_bank with 72 curated psychometric items.
Run from project root: python backend/db/seed_artspark_bank.py
"""

import os
import sys
import json
import uuid
import sqlite3

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(SCRIPT_DIR)
DB_PATH     = os.path.join(SCRIPT_DIR, "goat.db")
sys.path.insert(0, BACKEND_DIR)

ITEMS = [
    # (domain, tier, difficulty, q_type, prompt, options_json, correct_key, explanation, tags_json)

    # ── VISUAL ART ────────────────────────────────────────────────────────────
    ("visual_art","easy",-1.2,"image_choice",
     "Which colour feels warm and energetic?",
     json.dumps([{"key":"A","label":"Blue 🔵"},{"key":"B","label":"Red 🔴"},{"key":"C","label":"Grey ⬜"},{"key":"D","label":"Black ⬛"}]),
     "B","Warm colours (red, orange, yellow) feel energetic and exciting.",
     json.dumps(["colour_theory","observation"])),

    ("visual_art","easy",-1.0,"image_choice",
     "A painting made with tiny dots of colour is called:",
     json.dumps([{"key":"A","label":"Cubism"},{"key":"B","label":"Pointillism"},{"key":"C","label":"Surrealism"},{"key":"D","label":"Realism"}]),
     "B","Pointillism uses small dots; Georges Seurat was a famous pointillist.",
     json.dumps(["art_history","technique"])),

    ("visual_art","medium",-0.2,"likert",
     "When you look at a picture, you notice small details that others usually miss.",
     json.dumps(["Never","Rarely","Sometimes","Often","Always"]),
     None,"Self-report: visual sensitivity and observation depth.",
     json.dumps(["observation","visual_acuity"])),

    ("visual_art","medium",0.3,"image_choice",
     "Which principle creates a sense of movement in a static artwork?",
     json.dumps([{"key":"A","label":"Symmetry"},{"key":"B","label":"Repetition of diagonal lines"},{"key":"C","label":"Flat colour blocks"},{"key":"D","label":"Heavy outline only"}]),
     "B","Diagonal lines and repeating patterns imply motion.",
     json.dumps(["composition","visual_rhythm"])),

    ("visual_art","hard",0.8,"open_text",
     "You have only three colours: red, blue, and white. Describe a scene you would paint and explain how you would mix them to create depth.",
     None,None,"Evaluates creative constraint handling, colour mixing knowledge, and narrative painting intent.",
     json.dumps(["colour_mixing","creative_constraint","depth"])),

    ("visual_art","hard",1.1,"sequence",
     "Put these steps of making a linocut print in the correct order:",
     json.dumps(["Ink the block","Cut the design into lino","Press paper onto block","Sketch design on lino","Peel paper to reveal print"]),
     json.dumps(["Sketch design on lino","Cut the design into lino","Ink the block","Press paper onto block","Peel paper to reveal print"]),
     "Correct process for relief printing.",
     json.dumps(["printmaking","process_knowledge"])),

    ("visual_art","expert",1.6,"open_text",
     "A photographer and a painter both make a portrait of the same person. Explain what each can express that the other cannot — and what both share.",
     None,None,"Expert-level comparative analysis of media, expression, and artistic intent.",
     json.dumps(["media_comparison","critical_analysis","artistic_intent"])),

    ("visual_art","expert",1.8,"image_choice",
     "Negative space in visual art refers to:",
     json.dumps([{"key":"A","label":"Background colours only"},{"key":"B","label":"Empty areas around and between subjects"},{"key":"C","label":"Shadows cast by objects"},{"key":"D","label":"Areas painted last"}]),
     "B","Negative space defines figure-ground relationships and shapes meaning.",
     json.dumps(["composition","negative_space","advanced"])),

    # ── MUSIC ─────────────────────────────────────────────────────────────────
    ("music","easy",-1.3,"image_choice",
     "How many beats are in a 4/4 bar?",
     json.dumps([{"key":"A","label":"2"},{"key":"B","label":"3"},{"key":"C","label":"4"},{"key":"D","label":"8"}]),
     "C","4/4 time means four quarter-note beats per measure.",
     json.dumps(["rhythm","time_signature","basics"])),

    ("music","easy",-0.9,"image_choice",
     "Which instrument makes sound by vibrating strings?",
     json.dumps([{"key":"A","label":"Flute"},{"key":"B","label":"Tabla"},{"key":"C","label":"Sitar"},{"key":"D","label":"Harmonium"}]),
     "C","Sitar is a plucked string instrument.",
     json.dumps(["instrument_families","acoustics"])),

    ("music","medium",-0.3,"likert",
     "When you hear a song, you can tap along to the beat without losing track.",
     json.dumps(["Never","Rarely","Sometimes","Often","Always"]),
     None,"Self-report: internal pulse and rhythmic sensitivity.",
     json.dumps(["rhythm","internal_pulse"])),

    ("music","medium",0.2,"image_choice",
     "A melody that moves by step (e.g., C-D-E) is called:",
     json.dumps([{"key":"A","label":"Conjunct motion"},{"key":"B","label":"Disjunct motion"},{"key":"C","label":"Chromatic motion"},{"key":"D","label":"Retrograde motion"}]),
     "A","Conjunct = stepwise; disjunct = leaps.",
     json.dumps(["melody","motion","music_theory"])),

    ("music","hard",0.9,"open_text",
     "You are composing a short piece to express sadness without using any words. What musical elements would you use and why?",
     None,None,"Evaluates understanding of expressive musical devices.",
     json.dumps(["composition","expression","musical_elements"])),

    ("music","hard",1.2,"sequence",
     "Order these from the slowest to fastest Italian tempo marking:",
     json.dumps(["Allegro","Largo","Andante","Presto","Moderato"]),
     json.dumps(["Largo","Andante","Moderato","Allegro","Presto"]),
     "Standard Italian tempo order.",
     json.dumps(["tempo","italian_terms","notation"])),

    ("music","expert",1.7,"image_choice",
     "Syncopation in rhythm means:",
     json.dumps([{"key":"A","label":"Playing exactly on the beat"},{"key":"B","label":"Accenting off-beats or weak beats"},{"key":"C","label":"Gradual increase in tempo"},{"key":"D","label":"Using only one note value"}]),
     "B","Syncopation shifts emphasis to weak beats.",
     json.dumps(["rhythm","syncopation","advanced"])),

    ("music","expert",1.9,"open_text",
     "Explain how a composer can use silence (rests) as powerfully as sound. Give a specific musical example or situation.",
     None,None,"Expert: understanding rest as expressive device.",
     json.dumps(["silence","expression","advanced_composition"])),

    # ── STORYTELLING ──────────────────────────────────────────────────────────
    ("storytelling","easy",-1.4,"image_choice",
     "Which word describes the main character who drives the story forward?",
     json.dumps([{"key":"A","label":"Narrator"},{"key":"B","label":"Protagonist"},{"key":"C","label":"Antagonist"},{"key":"D","label":"Setting"}]),
     "B","The protagonist is the central character the story follows.",
     json.dumps(["narrative_elements","character"])),

    ("storytelling","easy",-0.8,"image_choice",
     "A story that teaches a moral lesson using animals as characters is called a:",
     json.dumps([{"key":"A","label":"Biography"},{"key":"B","label":"Fable"},{"key":"C","label":"Fantasy"},{"key":"D","label":"Myth"}]),
     "B","Fables use animal characters to convey morals.",
     json.dumps(["genre","narrative_forms"])),

    ("storytelling","medium",-0.1,"likert",
     "When you make up a story, you can picture the scenes clearly in your head as if watching a film.",
     json.dumps(["Never","Rarely","Sometimes","Often","Always"]),
     None,"Visualisation ability as a predictor of narrative richness.",
     json.dumps(["visualisation","narrative_imagination"])),

    ("storytelling","medium",0.4,"open_text",
     "A character wakes up to discover everyone has forgotten how to laugh. Write the first two sentences of this story.",
     None,None,"Tests narrative hook quality, world-building instinct, and voice.",
     json.dumps(["story_opening","hook","voice"])),

    ("storytelling","hard",0.7,"image_choice",
     "Which technique reveals a character's personality through their actions rather than descriptions?",
     json.dumps([{"key":"A","label":"Exposition"},{"key":"B","label":"Show don't tell"},{"key":"C","label":"Flashback"},{"key":"D","label":"Foreshadowing"}]),
     "B","Show don't tell demonstrates character through behaviour.",
     json.dumps(["craft","narrative_technique"])),

    ("storytelling","hard",1.3,"open_text",
     "Rewrite this sentence to 'show' instead of 'tell': 'She was very nervous before the performance.'",
     None,None,"Practical craft application of show-don't-tell.",
     json.dumps(["show_dont_tell","craft","revision"])),

    ("storytelling","expert",1.6,"open_text",
     "An unreliable narrator tells a story differently from what actually happened. Why might a writer choose this technique and what effect does it create?",
     None,None,"Expert-level narrative craft and reader experience analysis.",
     json.dumps(["unreliable_narrator","narrative_craft","reader_effect"])),

    ("storytelling","expert",1.8,"image_choice",
     "In media res refers to:",
     json.dumps([{"key":"A","label":"Starting at the very beginning"},{"key":"B","label":"Beginning in the middle of the action"},{"key":"C","label":"Ending with a moral"},{"key":"D","label":"Telling the story backwards"}]),
     "B","In media res drops the reader into ongoing action.",
     json.dumps(["narrative_structure","literary_device","advanced"])),

    # ── DRAMA ─────────────────────────────────────────────────────────────────
    ("drama","easy",-1.3,"image_choice",
     "When an actor speaks thoughts aloud that other characters cannot hear, this is called a:",
     json.dumps([{"key":"A","label":"Dialogue"},{"key":"B","label":"Soliloquy"},{"key":"C","label":"Aside"},{"key":"D","label":"Monologue"}]),
     "B","A soliloquy is an internal thought spoken aloud, unheard by other characters.",
     json.dumps(["dramatic_technique","acting_terms"])),

    ("drama","easy",-0.7,"image_choice",
     "Stage directions marked 'stage left' mean the actor should move to their:",
     json.dumps([{"key":"A","label":"Left from audience view"},{"key":"B","label":"Right from audience view"},{"key":"C","label":"Back of the stage"},{"key":"D","label":"Front of the stage"}]),
     "B","Stage left is the actor's left — the audience's right.",
     json.dumps(["staging","theatre_vocabulary"])),

    ("drama","medium",-0.2,"likert",
     "You can change your voice, posture, and movement to convincingly become a completely different person.",
     json.dumps(["Never","Rarely","Sometimes","Often","Always"]),
     None,"Physical and vocal transformation ability.",
     json.dumps(["physicality","transformation","characterisation"])),

    ("drama","medium",0.3,"open_text",
     "You must play a character happy on the outside but hiding deep sadness. List five physical actions showing both emotions at once.",
     None,None,"Tests layered physical characterisation and emotional nuance.",
     json.dumps(["physical_characterisation","subtext","layered_emotion"])),

    ("drama","hard",0.9,"image_choice",
     "Stanislavski's 'magic if' technique asks actors to:",
     json.dumps([{"key":"A","label":"Memorise lines perfectly"},{"key":"B","label":"Ask: what would I do IF I were this character?"},{"key":"C","label":"Focus only on physical movement"},{"key":"D","label":"Improvise without preparation"}]),
     "B","The 'magic if' sparks imaginative identification with the character.",
     json.dumps(["acting_method","stanislavski","characterisation"])),

    ("drama","hard",1.2,"open_text",
     "You have 30 seconds of silence at the start of a play. As a director, what might happen and why?",
     None,None,"Directorial thinking: tension, atmosphere, audience contract.",
     json.dumps(["direction","theatrical_tension","atmosphere"])),

    ("drama","expert",1.5,"open_text",
     "Explain the difference between Brechtian theatre and Stanislavski's method. Which would you use for a play about climate change and why?",
     None,None,"Expert comparative drama theory with applied critical judgment.",
     json.dumps(["drama_theory","brecht","stanislavski","critical_thinking"])),

    ("drama","expert",1.9,"image_choice",
     "Catharsis in Aristotle's definition of tragedy means:",
     json.dumps([{"key":"A","label":"Resolution of all plot conflicts"},{"key":"B","label":"Emotional purging felt by the audience"},{"key":"C","label":"The protagonist achieving their goal"},{"key":"D","label":"Return to the original setting"}]),
     "B","Catharsis: emotional cleansing through witnessing tragedy.",
     json.dumps(["aristotle","dramatic_theory","tragedy"])),

    # ── DANCE & MOVEMENT ──────────────────────────────────────────────────────
    ("dance_movement","easy",-1.5,"image_choice",
     "Moving your body in time with music means you have good:",
     json.dumps([{"key":"A","label":"Flexibility"},{"key":"B","label":"Rhythm"},{"key":"C","label":"Balance"},{"key":"D","label":"Strength"}]),
     "B","Moving in time with music is fundamentally a rhythmic skill.",
     json.dumps(["rhythm","timing","basics"])),

    ("dance_movement","easy",-0.9,"image_choice",
     "In Bharatanatyam, the hand gestures used to tell stories are called:",
     json.dumps([{"key":"A","label":"Mudras"},{"key":"B","label":"Taals"},{"key":"C","label":"Ragas"},{"key":"D","label":"Avartans"}]),
     "A","Mudras (hasta mudras) are codified hand gestures in Indian classical dance.",
     json.dumps(["indian_dance","gesture","vocabulary"])),

    ("dance_movement","medium",-0.1,"likert",
     "When you hear music, you feel a natural urge to move your body without having to think about it.",
     json.dumps(["Never","Rarely","Sometimes","Often","Always"]),
     None,"Kinesthetic response to musical stimulus.",
     json.dumps(["kinesthetic","embodied_rhythm"])),

    ("dance_movement","medium",0.4,"open_text",
     "Describe a sequence of 5 movements expressing a storm — from distant rumble to lightning strike to calm.",
     None,None,"Spatial imagination, dynamic range, narrative movement.",
     json.dumps(["choreography","dynamics","spatial_awareness","narrative_movement"])),

    ("dance_movement","hard",0.8,"image_choice",
     "The Laban Movement Analysis term for movement that is sudden, strong, and direct is:",
     json.dumps([{"key":"A","label":"Float (sustained, light, indirect)"},{"key":"B","label":"Punch (sudden, strong, direct)"},{"key":"C","label":"Flick (sudden, light, indirect)"},{"key":"D","label":"Glide (sustained, light, direct)"}]),
     "B","Laban's Effort Actions classify movement by time, weight, space, and flow.",
     json.dumps(["laban","effort_actions","movement_analysis"])),

    ("dance_movement","hard",1.1,"open_text",
     "A dancer who uses a wheelchair wants to perform a piece about freedom. How would you choreograph this?",
     None,None,"Inclusive choreography and thematic expression.",
     json.dumps(["inclusive_dance","choreography","thematic_expression"])),

    ("dance_movement","expert",1.7,"open_text",
     "How does repetition in choreography function differently from repetition in music? How can a choreographer use this difference intentionally?",
     None,None,"Advanced cross-art form analysis of structural devices.",
     json.dumps(["choreography_theory","repetition","cross_art","advanced"])),

    ("dance_movement","expert",1.9,"image_choice",
     "In contact improvisation, the central principle is:",
     json.dumps([{"key":"A","label":"Following pre-set choreography"},{"key":"B","label":"Shared weight and responsive movement between two dancers"},{"key":"C","label":"Competing for technical skill"},{"key":"D","label":"Mirroring the lead dancer exactly"}]),
     "B","Contact improv is about listening, weight-sharing, and spontaneous co-creation.",
     json.dumps(["contact_improvisation","collaboration","advanced"])),

    # ── CRAFT & DESIGN ────────────────────────────────────────────────────────
    ("craft_design","easy",-1.4,"image_choice",
     "Which material would you choose to make something waterproof?",
     json.dumps([{"key":"A","label":"Paper"},{"key":"B","label":"Fabric"},{"key":"C","label":"Plastic or waxed cloth"},{"key":"D","label":"Cardboard"}]),
     "C","Plastic and waxed materials resist water penetration.",
     json.dumps(["materials","properties","selection"])),

    ("craft_design","easy",-0.8,"image_choice",
     "The word 'ergonomic' in design means:",
     json.dumps([{"key":"A","label":"Looks beautiful"},{"key":"B","label":"Designed to fit how humans use it comfortably"},{"key":"C","label":"Made from natural materials"},{"key":"D","label":"Very expensive to produce"}]),
     "B","Ergonomics designs products that fit natural human use.",
     json.dumps(["design_vocabulary","ergonomics","user_centred"])),

    ("craft_design","medium",-0.2,"likert",
     "When you see a broken or old object, you imagine creative new uses for it rather than throwing it away.",
     json.dumps(["Never","Rarely","Sometimes","Often","Always"]),
     None,"Upcycling instinct and material reimagination.",
     json.dumps(["upcycling","creative_reuse","divergent_thinking"])),

    ("craft_design","medium",0.3,"open_text",
     "Design a bag for a mountain climber. List three most important features and the materials for each — explain your reasoning.",
     None,None,"Design thinking: user needs, material properties, function-form balance.",
     json.dumps(["design_thinking","user_needs","materials"])),

    ("craft_design","hard",0.7,"image_choice",
     "In design thinking, the 'Empathise' stage means:",
     json.dumps([{"key":"A","label":"Building a prototype quickly"},{"key":"B","label":"Understanding the user's real needs, feelings, and context"},{"key":"C","label":"Testing the final product"},{"key":"D","label":"Generating 100 ideas without judgement"}]),
     "B","Empathy means deeply understanding people before jumping to solutions.",
     json.dumps(["design_thinking","empathy","human_centred"])),

    ("craft_design","hard",1.2,"open_text",
     "You have 10 minutes, a sheet of newspaper, and tape. Describe the strongest bridge structure across 30cm gap — explain the structural principle.",
     None,None,"Structural reasoning, rapid prototyping, constraint creativity.",
     json.dumps(["structures","materials","constraint_design","engineering_thinking"])),

    ("craft_design","expert",1.6,"open_text",
     "Explain the tension between aesthetic beauty and functional efficiency in product design. Give an example where a designer had to compromise.",
     None,None,"Expert design philosophy: form vs function debate.",
     json.dumps(["design_philosophy","aesthetics","function","critical_analysis"])),

    ("craft_design","expert",1.8,"image_choice",
     "Biomimicry in design means:",
     json.dumps([{"key":"A","label":"Making products that look like animals"},{"key":"B","label":"Designing solutions inspired by patterns in nature"},{"key":"C","label":"Using only biodegradable materials"},{"key":"D","label":"Copying existing designs from history"}]),
     "B","Biomimicry draws from nature's strategies (e.g., Velcro from burrs).",
     json.dumps(["biomimicry","innovation","nature_inspired","advanced"])),
]


def seed_sqlite(db_path):
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS artspark_item_bank (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            item_uuid   TEXT UNIQUE NOT NULL,
            domain      TEXT NOT NULL,
            tier        TEXT NOT NULL,
            difficulty  REAL NOT NULL DEFAULT 0.0,
            q_type      TEXT NOT NULL,
            prompt      TEXT NOT NULL,
            options     TEXT,
            correct_key TEXT,
            explanation TEXT,
            tags        TEXT,
            language    TEXT DEFAULT 'en',
            active      INTEGER DEFAULT 1,
            created_at  TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.commit()
    inserted = skipped = 0
    for (domain, tier, difficulty, q_type, prompt, options, correct_key, explanation, tags) in ITEMS:
        try:
            conn.execute(
                "INSERT INTO artspark_item_bank (item_uuid,domain,tier,difficulty,q_type,prompt,options,correct_key,explanation,tags) VALUES (?,?,?,?,?,?,?,?,?,?)",
                (str(uuid.uuid4()), domain, tier, difficulty, q_type, prompt, options, correct_key, explanation, tags)
            )
            inserted += 1
        except sqlite3.IntegrityError:
            skipped += 1
    conn.commit()
    conn.close()
    print(f"[ArtSpark Seed] SQLite: {inserted} inserted, {skipped} skipped.")


def seed_supabase():
    try:
        from dotenv import load_dotenv
        load_dotenv(os.path.join(BACKEND_DIR, ".env"))
        from supabase import create_client
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        if not url or not key:
            print("[ArtSpark Seed] No Supabase env vars — skipping.")
            return
        sb = create_client(url, key)
        rows = [
            {"item_uuid": str(uuid.uuid4()), "domain": d, "tier": t, "difficulty": diff,
             "q_type": qt, "prompt": p, "options": o, "correct_key": ck,
             "explanation": ex, "tags": tg, "language": "en", "active": 1}
            for (d, t, diff, qt, p, o, ck, ex, tg) in ITEMS
        ]
        sb.table("artspark_item_bank").upsert(rows, on_conflict="item_uuid").execute()
        print(f"[ArtSpark Seed] Supabase: {len(rows)} rows upserted.")
    except Exception as e:
        print(f"[ArtSpark Seed] Supabase error: {e}")


if __name__ == "__main__":
    print(f"[ArtSpark Seed] Seeding {len(ITEMS)} items...")
    seed_sqlite(DB_PATH)
    seed_supabase()
    print("[ArtSpark Seed] Done.")

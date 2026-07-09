import math
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing, Rect

# Premium Style Palette
primary_color = colors.HexColor("#5B4CF0")    # Indigo
secondary_color = colors.HexColor("#00B8A9")  # Teal
text_color = colors.HexColor("#2D3436")       # Dark Charcoal
light_bg = colors.HexColor("#F8F9FA")         # Light Grey
border_color = colors.HexColor("#E2E8F0")     # Light Border
accent_gold = colors.HexColor("#F7B731")      # Gold

# Default Sample Stylesheet
styles = getSampleStyleSheet()

# Typography Styles
title_style = ParagraphStyle(
    'CoverTitle',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=24,
    leading=30,
    textColor=primary_color,
    spaceAfter=15,
    alignment=1  # Center
)

h1_style = ParagraphStyle(
    'Header1',
    parent=styles['Heading1'],
    fontName='Helvetica-Bold',
    fontSize=18,
    leading=22,
    textColor=primary_color,
    spaceBefore=5,
    spaceAfter=10,
    keepWithNext=True
)

h2_style = ParagraphStyle(
    'Header2',
    parent=styles['Heading2'],
    fontName='Helvetica-Bold',
    fontSize=12,
    leading=15,
    textColor=primary_color,
    spaceBefore=10,
    spaceAfter=6,
    keepWithNext=True
)

body_style = ParagraphStyle(
    'ReportBody',
    parent=styles['BodyText'],
    fontName='Helvetica',
    fontSize=9.5,
    leading=14,
    textColor=text_color,
    spaceAfter=10
)

italic_style = ParagraphStyle(
    'ReportItalic',
    parent=body_style,
    fontName='Helvetica-Oblique',
    textColor=colors.HexColor("#4A4A4A")
)

section_header_style = ParagraphStyle(
    'SectionHeader',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=8.5,
    leading=10,
    textColor=secondary_color,
    spaceAfter=4,
    textTransform='uppercase'
)

table_cell_style = ParagraphStyle(
    'TableCell',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=9,
    leading=11,
    textColor=text_color
)

table_header_style = ParagraphStyle(
    'TableHeader',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=9,
    leading=11,
    textColor=colors.white
)

card_label_style = ParagraphStyle(
    'CardLabel',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=9.5,
    leading=12,
    textColor=primary_color
)

card_body_style = ParagraphStyle(
    'CardBody',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=8.5,
    leading=12,
    textColor=text_color
)

# Static Data Maps
DOMAINS_MAP = {
    "kinesthetic": "Kinesthetic & Physical",
    "creative": "Creative & Artistic",
    "logical": "Logical & Analytical",
    "spatial": "Spatial & Making",
    "social": "Social & Leadership",
    "language": "Language & Communication",
    "naturalist": "Naturalist & Environmental",
    "intrapersonal": "Intrapersonal & Reflective"
}

DOMAIN_COLORS = {
    "kinesthetic": colors.HexColor("#FF7675"),
    "creative": colors.HexColor("#6C5CE7"),
    "logical": colors.HexColor("#0984E3"),
    "spatial": colors.HexColor("#FD9644"),
    "social": colors.HexColor("#00B894"),
    "language": colors.HexColor("#D63031"),
    "naturalist": colors.HexColor("#26DE81"),
    "intrapersonal": colors.HexColor("#A55EEA")
}

PERSONAS = {
    "creative": {
        "title": "THE CREATOR",
        "emoji": "🎨",
        "desc": "This child enjoys generating original ideas, imagining possibilities, and expressing thoughts through visual and artistic mediums.",
        "strengths": ["Vivid Imagination", "Divergent Thinking", "Original Expression"],
        "growth": ["Structured Completion", "Attention to Rote Rules"]
    },
    "spatial": {
        "title": "THE BUILDER",
        "emoji": "🔧",
        "desc": "This child thinks in three dimensions, loves constructing physical or mental models, and naturally understands design structures.",
        "strengths": ["3D Visualization", "Structural Logic", "Spatial Transformation"],
        "growth": ["Verbalizing Concepts", "Patience with Abstract Theory"]
    },
    "logical": {
        "title": "THE THINKER",
        "emoji": "🧠",
        "desc": "This child is highly analytical, naturally notices logical patterns, loves solving puzzles, and thrives on structured reasoning.",
        "strengths": ["Pattern Recognition", "Reasoning & Logic", "Systematic Problem-Solving"],
        "growth": ["Handling Vague Goals", "Accepting Open-Ended Ambiguity"]
    },
    "social": {
        "title": "THE LEADER",
        "emoji": "🤝",
        "desc": "This child possesses natural social intelligence, easily connects with others, coordinates collaborative activities, and guides groups.",
        "strengths": ["Empathy & Influence", "Group Organization", "Collaborative Coordination"],
        "growth": ["Delegating Tasks", "Sustaining Quiet Focus"]
    },
    "language": {
        "title": "THE COMMUNICATOR",
        "emoji": "💬",
        "desc": "This child has a natural affinity for words, excels in verbal storytelling, expresses ideas with high clarity, and loves debate.",
        "strengths": ["Verbal Fluency", "Narrative Structure", "Persuasive Explanation"],
        "growth": ["Listening Without Interrupting", "Silent Individual Practice"]
    },
    "naturalist": {
        "title": "THE OBSERVER",
        "emoji": "🌱",
        "desc": "This child has unusual detail-awareness in nature, notices micro-patterns in ecosystems, and loves classifying biological details.",
        "strengths": ["Sensory Observation", "Taxonomic Classification", "Environmental Empathy"],
        "growth": ["Abstract Symbolic Tasks", "Prolonged Desk-Bound Study"]
    },
    "kinesthetic": {
        "title": "THE EXPLORER",
        "emoji": "🏃",
        "desc": "This child learns best through physical doing, movement, and hands-on trial-and-error, demonstrating great fine-motor control.",
        "strengths": ["Fine-Motor Precision", "Coordination & Agility", "Kinesthetic Intuition"],
        "growth": ["Passive Auditory Learning", "Prolonged Sitting Work"]
    },
    "intrapersonal": {
        "title": "THE RESEARCHER",
        "emoji": "🧘",
        "desc": "This child exhibits deep self-awareness, prefers reflecting in quiet spaces, understands personal motivations, and sets thoughtful goals.",
        "strengths": ["Emotional Reflexivity", "Independent Planning", "Goal-Oriented Perseverance"],
        "growth": ["Highly Competitive Groups", "Spontaneous Public Speaking"]
    }
}

parentGuides = {
    "creative": {
        "behaviors": ["Imagines highly unusual possibilities", "Enjoys open-ended tasks and abstract games", "Prefers visual creation over pure memorization"],
        "motivators": "Original expression, visual challenges, autonomy in choices",
        "styles": "Divergent and visual-first",
        "challenges": "Can easily become bored by highly repetitive or rigid work",
        "support": ["Provide diverse physical and digital design materials", "Allow space for experimentation without immediate grading"]
    },
    "spatial": {
        "behaviors": ["Likes physical construction and model-building", "Enjoys visualizing shapes and three-dimensional blocks", "Notices minute structural details in drawings"],
        "motivators": "Building, assembling, transforming structures, design tasks",
        "styles": "Three-dimensional and hands-on",
        "challenges": "May sometimes struggle to explain spatial concepts in written text",
        "support": ["Encourage model building and tinkering workshops", "Use visual diagrams and physical models for academic study"]
    },
    "logical": {
        "behaviors": ["Enjoys solving complex riddles and puzzles", "Notices mathematical patterns spontaneously", "Structures thoughts sequentially and logically"],
        "motivators": "Systematic patterns, numerical puzzles, clear cause-and-effect rules",
        "styles": "Analytical, sequence-based",
        "challenges": "May get frustrated by vague directions or emotional debates",
        "support": ["Provide math puzzles and logic-based board games", "Structure daily tasks with clear sequences and logical rules"]
    },
    "social": {
        "behaviors": ["Naturally organizes peers and group activities", "Shows high empathy and notices others' emotions", "Takes active initiative in coordinating events"],
        "motivators": "Collaborative projects, peer coordination, group problem-solving",
        "styles": "Interpersonal, leadership-driven",
        "challenges": "May dominate discussions or take on too much responsibility",
        "support": ["Provide leadership opportunities with guidance on delegation", "Encourage group games that require active listening and compromise"]
    },
    "language": {
        "behaviors": ["Expresses thoughts with high verbal clarity", "Enjoys telling stories and describing scenarios", "Has an extensive vocabulary and notices wordplay"],
        "motivators": "Debate, verbal explanation, storytelling, theater performance",
        "styles": "Verbal-auditory, narrative-driven",
        "challenges": "May talk excessively or struggle with silent, individual tasks",
        "support": ["Encourage storytelling, theater, or writing workshops", "Discuss complex topics together to challenge verbal expression"]
    },
    "naturalist": {
        "behaviors": ["Notices details in plants, animals, and ecosystems", "Loves sorting, classifying, and organizing collections", "Shows deep empathy and interest in the natural world"],
        "motivators": "Outdoor observations, wildlife exploration, environmental projects",
        "styles": "Environmental-observational",
        "challenges": "May get restless in closed, sedentary indoor spaces",
        "support": ["Provide opportunities for regular nature exploration", "Use outdoor settings and animal themes for academic concepts"]
    },
    "kinesthetic": {
        "behaviors": ["Demonstrates exceptional coordination and motor speed", "Learns concepts best by physically doing or moving", "Has strong fine-motor skills and tactile intuition"],
        "motivators": "Physical movement, sports, hands-on construction, active games",
        "styles": "Tactile-physical, experimental",
        "challenges": "Needs regular physical breaks; may fidget in quiet lectures",
        "support": ["Integrate physical movement and breaks into study routines", "Encourage sports, dance, or hands-on crafting workshops"]
    },
    "intrapersonal": {
        "behaviors": ["Shows deep reflection and self-awareness of feelings", "Sets thoughtful personal goals and plans ahead", "Thrives when working independently on projects"],
        "motivators": "Solo hobbies, personal reflection, self-directed goals",
        "styles": "Reflective, self-guided",
        "challenges": "May withdraw during highly competitive or chaotic group work",
        "support": ["Provide quiet spaces for reflection and independent projects", "Encourage journaling or writing to process thoughts and emotions"]
    }
}

pathways_dict = {
    "creative": {
        "title": "Creative Arts & Visual Storytelling",
        "desc": "Visual expression, digital sketching, and storytelling workshops. Recommended: Project WHY Art Club, clay modelling, and design thinking modules."
    },
    "spatial": {
        "title": "Mechanical Design & 3D Prototyping",
        "desc": "Model building, LEGO engineering, origami, and basic architectural drafting. Recommended: Maker Space tinkering and hands-on physics toys."
    },
    "logical": {
        "title": "Math Olympiad & Coding Logic",
        "desc": "Scratch programming, chess, pattern recognition exercises, and basic algorithms. Recommended: Logic puzzles and computer science basics."
    },
    "social": {
        "title": "Community Leadership & Public Speaking",
        "desc": "Peer tutoring, student council, debate club, and team sports. Recommended: Team building workshops and local volunteering."
    },
    "language": {
        "title": "Creative Writing & Debate",
        "desc": "Story writing, speech competitions, spelling bees, and library reading clubs. Recommended: Theatre arts and presentation skills."
    },
    "naturalist": {
        "title": "Environmental Science & Eco-Clubs",
        "desc": "Plant care, bird watching, nature mapping, and ecology clubs. Recommended: Science lab experiments and gardening programs."
    },
    "kinesthetic": {
        "title": "Sports, Dance & Theatre",
        "desc": "Athletics, classical/modern dance, gymnastics, and physical theatre. Recommended: Martial arts and fine-motor craft work."
    },
    "intrapersonal": {
        "title": "Reflective Journalism & Goal Setting",
        "desc": "Diary writing, mindfulness, solo research projects, and goal tracking. Recommended: Self-paced online learning and reading programs."
    }
}

def draw_bar(rating, max_rating=5, width=120, height=8):
    d = Drawing(width, height)
    # Background bar
    d.add(Rect(0, 0, width, height, fillColor=colors.HexColor("#E2E8F0"), strokeColor=None))
    # Foreground filled bar
    fill_width = (rating / float(max_rating)) * width if rating else 0
    if fill_width > 0:
        d.add(Rect(0, 0, fill_width, height, fillColor=colors.HexColor("#00B8A9"), strokeColor=None))
    return d

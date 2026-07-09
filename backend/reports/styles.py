import math
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing, Rect

# Premium Psychometric Color Palette (Minimal & Grayscale-safe)
primary_color = colors.HexColor("#4F46E5")    # TINS Indigo
secondary_color = colors.HexColor("#0D9488")  # TINS Teal
text_color = colors.HexColor("#1E293B")       # Dark Charcoal
slate_label = colors.HexColor("#64748B")      # Muted Slate
light_bg = colors.HexColor("#F8FAFC")         # Neutral Light Grey
border_color = colors.HexColor("#E2E8F0")     # Soft Border
accent_gold = colors.HexColor("#D97706")      # Amber/Gold

# Default Sample Stylesheet
styles = getSampleStyleSheet()

# Typography Styles
title_style = ParagraphStyle(
    'CoverTitle',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=24,
    leading=30,
    textColor=text_color,
    spaceAfter=15,
    alignment=1  # Center
)

h1_style = ParagraphStyle(
    'Header1',
    parent=styles['Heading1'],
    fontName='Helvetica-Bold',
    fontSize=18,
    leading=22,
    textColor=text_color,
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
    textColor=slate_label
)

section_header_style = ParagraphStyle(
    'SectionHeader',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=8.5,
    leading=10,
    textColor=primary_color,
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
    "kinesthetic": colors.HexColor("#EF4444"), # Red-500
    "creative": colors.HexColor("#6366F1"),    # Indigo-500
    "logical": colors.HexColor("#3B82F6"),     # Blue-500
    "spatial": colors.HexColor("#F59E0B"),     # Amber-500
    "social": colors.HexColor("#10B981"),      # Emerald-500
    "language": colors.HexColor("#EC4899"),    # Pink-500
    "naturalist": colors.HexColor("#22C55E"),  # Green-500
    "intrapersonal": colors.HexColor("#8B5CF6") # Violet-500
}

PERSONAS = {
    "creative": {
        "title": "THE CREATOR",
        "emoji": "🎨",
        "desc": "Generates highly original and divergent pathways, visualizing abstract ideas and mapping spatial patterns with high fluid intelligence.",
        "strengths": ["Original Thinking", "Divergent Ideation", "Visual Pattern Reasoning"],
        "growth": ["Structured Implementation", "Attention to Repetitive Protocols"]
    },
    "spatial": {
        "title": "THE BUILDER",
        "emoji": "🔧",
        "desc": "Thinks natively in three dimensions, excelling at mental rotation, structural assemblies, and modeling mechanical relationships.",
        "strengths": ["3D Mental Rotation", "Structural Assembly", "Spatial Logic Modeling"],
        "growth": ["Verbal Translation of Spatial Concepts", "Sedentary Abstract Lectures"]
    },
    "logical": {
        "title": "THE THINKER",
        "emoji": "🧠",
        "desc": "Excels in systematic logical deductions, pattern classification, rule inference, and breaking down complex problems.",
        "strengths": ["Rule Induction", "Logical Pattern Extraction", "Systematic Problem Breakdown"],
        "growth": ["Ambiguous Creative Goals", "Non-linear Dynamic Situations"]
    },
    "social": {
        "title": "THE LEADER",
        "emoji": "🤝",
        "desc": "Exhibits strong interpersonal cues, coordinating peer groups, mediating collaborations, and guiding group problem-solving.",
        "strengths": ["Interpersonal Insight", "Peer Group Coordination", "Mediated Collaboration"],
        "growth": ["Sustained Isolation Tasks", "Detailed Individual Research"]
    },
    "language": {
        "title": "THE COMMUNICATOR",
        "emoji": "💬",
        "desc": "Demonstrates high verbal fluency, rich semantic structures, narrative articulation, and persuasive conceptual explanations.",
        "strengths": ["Semantic Precision", "Narrative Articulation", "Conceptual Explanations"],
        "growth": ["Visual-Spatial Map Translation", "Prolonged Silent Data Entry"]
    },
    "naturalist": {
        "title": "THE OBSERVER",
        "emoji": "🌱",
        "desc": "Demonstrates high visual categorization, detail discrimination in environmental structures, and eco-system mapping.",
        "strengths": ["Micro-Detail Discrimination", "Structural Categorization", "Ecosystem Pattern Matching"],
        "growth": ["Highly Abstract Decontextualized Systems", "Sedentary Indoor Workspaces"]
    },
    "kinesthetic": {
        "title": "THE EXPLORER",
        "emoji": "🏃",
        "desc": "Learns best through sensory-motor feedback loop integration, demonstrating excellent motor speed and fine-motor control.",
        "strengths": ["Fine-Motor Coordination", "Proprioceptive Feedback Loop", "Dynamic Physical Manipulation"],
        "growth": ["Passive Auditory Lectures", "Prolonged Text-Based Memorization"]
    },
    "intrapersonal": {
        "title": "THE RESEARCHER",
        "emoji": "🧘",
        "desc": "Possesses deep self-reflective capacities, excels in individual goal setting, and demonstrates high task-persistence.",
        "strengths": ["Task-Persistence", "Metacognitive Self-Reflection", "Self-Guided Strategy Plan"],
        "growth": ["High-Competition Public Spaces", "Spontaneous Collaborative Ideation"]
    }
}

parentGuides = {
    "creative": {
        "behaviors": ["Explores unconventional puzzle designs", "Prefers open-ended sandbox settings", "Shows high fluid visualization style"],
        "motivators": "Novelty in choices, design autonomy, open-ended problem exploration",
        "styles": "Visual, exploratory, non-linear",
        "challenges": "May lose engagement if constrained by rigid task repetition",
        "support": ["Provide design tools and creative platforms", "Acknowledge original approaches rather than standardized solutions"]
    },
    "spatial": {
        "behaviors": ["Enjoys assembling mechanical models", "Exhibits rapid mental rotation of shapes", "Intuitively understands structural blueprints"],
        "motivators": "3D construction, material tinkering, visualization challenges",
        "styles": "Hands-on, spatial-tactile",
        "challenges": "May struggle to express spatial reasoning in purely verbal terms",
        "support": ["Provide 3D puzzles, engineering toys, and architectural grids", "Encourage drawing visual schemas to outline logical problems"]
    },
    "logical": {
        "behaviors": ["Deducts abstract patterns and rules", "Enjoys math puzzles and sequential logic", "Categorizes collections systematically"],
        "motivators": "Algorithmic rules, pattern decoding, clear causal systems",
        "styles": "Sequential, inductive, logic-driven",
        "challenges": "May feel uncomfortable with vague prompts lacking definite parameters",
        "support": ["Introduce coding logic, strategy games, and pattern puzzles", "Provide clear step-by-step frameworks for multi-phase tasks"]
    },
    "social": {
        "behaviors": ["Assumes active leadership in peer workshops", "Senses peer emotions and mediates disagreements", "Thrives in group challenge modules"],
        "motivators": "Team collaboration, group problem solving, interactive feedback",
        "styles": "Collaborative, group-centric",
        "challenges": "May experience fatigue or low focus in prolonged individual tasks",
        "support": ["Structure team-based challenges and community service", "Encourage group reflections and shared project goals"]
    },
    "language": {
        "behaviors": ["Articulates arguments with semantic rich vocabulary", "Enjoys narrative writing and conceptual debate", "Comprehends complex textual instructions rapidly"],
        "motivators": "Verbal debate, narrative drafting, vocabulary games",
        "styles": "Verbal-conceptual, story-driven",
        "challenges": "May become restless in tasks lacking opportunities for verbal dialogue",
        "support": ["Provide reading clubs, writing projects, and public speaking", "Engage in conceptual discussions to expand logic parameters"]
    },
    "naturalist": {
        "behaviors": ["Observes environmental shifts in plant/animal life", "Categorizes visual elements by detailed patterns", "Enjoys outdoor learning modules"],
        "motivators": "Environmental observation, taxonomic sorting, hands-on outdoors",
        "styles": "Ecosystem-based, categorization-driven",
        "challenges": "May experience difficulty focusing in sterile, closed rooms",
        "support": ["Encourage gardening, bird watching, and nature collections", "Use environmental science themes for classroom learning"]
    },
    "kinesthetic": {
        "behaviors": ["Exhibits high manual dexterity and speed", "Prefers kinetic activities over desk tasks", "Learns through tactile trial-and-error"],
        "motivators": "Kinetic movement, athletic challenges, manual crafts",
        "styles": "Tactual-motor, trial-and-error",
        "challenges": "May require periodic active breaks to maintain attention",
        "support": ["Provide hands-on craft projects and kinetic breaks", "Integrate active physical gestures into study routines"]
    },
    "intrapersonal": {
        "behaviors": ["Sets individual study goals and monitors progress", "Reflects quietly on personal achievements", "Demonstrates sustained individual task-persistence"],
        "motivators": "Independent goals, self-paced challenges, quiet study spaces",
        "styles": "Self-directed, reflective",
        "challenges": "May feel overwhelmed in highly competitive or chaotic groups",
        "support": ["Designate quiet individual work corners and study blocks", "Teach self-tracking tools for personal goals and plans"]
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
    # Background bar (soft gray)
    d.add(Rect(0, 0, width, height, fillColor=colors.HexColor("#F1F5F9"), strokeColor=None))
    # Foreground filled bar (indigo)
    fill_width = (rating / float(max_rating)) * width if rating else 0
    if fill_width > 0:
        d.add(Rect(0, 0, fill_width, height, fillColor=primary_color, strokeColor=None))
    return d

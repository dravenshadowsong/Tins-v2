from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle

def build_page(story, data, styles):
    section_header_style = styles.section_header_style
    h1_style = styles.h1_style
    body_style = styles.body_style
    card_body_style = styles.card_body_style
    border_color = styles.border_color
    light_bg = styles.light_bg
    table_cell_style = styles.table_cell_style
    primary_color = styles.primary_color

    primary_domain = data["primary_domain"]
    primary_label = styles.DOMAINS_MAP.get(primary_domain, primary_domain)
    child = data.get("child") or {}
    
    # Domain specific chronological roadmap configs
    roadmap_configs = {
        "creative": [
            ("30 DAYS (ACTIVATION)", "Establish creative sandbox familiarity.", "15 mins of daily block building or visual sketching without rules.", "Autonomy and confidence in shape design construction.", "Independently initiates visual design play twice a week."),
            ("90 DAYS (COLLABORATION)", "Channelize original ideas into peer group tasks.", "Collaborative building workshops with center mentors or neighborhood peers.", "Turn-taking, role coordination, and sharing design toolsets.", "Mentor logs positive cooperation markers in group sheets."),
            ("6 MONTHS (CHALLENGE)", "Resolve complex multi-step spatial problems.", "Attempts advanced clay modeling, geometry grids, or spatial block puzzles.", "Planning strategy and patience to minimize trial-and-error clicks.", "Completes advanced rotation puzzles with low error logs."),
            ("12 MONTHS (REVIEW)", "Advanced portfolio showcase and profile reassessment.", "Compile physical models/sketchbooks and conduct a TINS re-assessment.", "Metacognitive self-reflection and tracing developmental logical stability.", "Maintains or stabilizes high TSI index on second assessment.")
        ],
        "logical": [
            ("30 DAYS (ACTIVATION)", "Build comfort with structured sequential logic.", "Solve 3-5 pattern deduction grids or sequence puzzles daily.", "Rule induction, sequential reasoning, and systematic logic parameters.", "Completes pattern puzzles with uniform, steady pacing logs."),
            ("90 DAYS (COLLABORATION)", "Apply systematic reasoning in peer game groups.", "Join chess meetups, logic board game groups, or group coding blocks.", "Algorithmic thinking, group strategy checks, and peer feedback loops.", "Participates in team logic matches without becoming frustrated."),
            ("6 MONTHS (CHALLENGE)", "Solve multi-phase algorithmic challenges.", "Attempt basic Scratch coding or advanced strategy game puzzles.", "Formulating personal logic plans and debugging execution steps.", "Independently writes simple conditional script blocks."),
            ("12 MONTHS (REVIEW)", "Portfolio logic check and second assessment session.", "Showcase visual programs/chess logs and re-assess TINS profile.", "Tracing logic stability and pattern comprehension milestones.", "Stabilized or improved TSI score on second logic session.")
        ],
        "spatial": [
            ("30 DAYS (ACTIVATION)", "Strengthen mental rotation and 3D visualization.", "15 mins of daily mental rotation matching or building blocks.", "Spatial layout visualization and mechanical intuition.", "Assembles a multi-shape block model independently."),
            ("90 DAYS (COLLABORATION)", "Collaborate on complex structural model builds.", "Team LEGO construction builds or collaborative physical modeling.", "Visual-spatial cooperation and communicating design layout steps.", "Directs or coordinates a model build block with peers."),
            ("6 MONTHS (CHALLENGE)", "Navigate detailed engineering blueprints.", "Assemble advanced origami models, wood puzzle kits, or drafting grids.", "Patience, structural logic, and visual diagram translation.", "Assembles detailed mechanical model from diagram guidelines."),
            ("12 MONTHS (REVIEW)", "Mechanical portfolio showcase and re-assessment.", "Exhibit structural creations and complete a TINS follow-up assessment.", "Metacognitive reflection on mechanical and spatial design growth.", "Maintains high TSI index on secondary spatial task session.")
        ],
        "social": [
            ("30 DAYS (ACTIVATION)", "Develop peer coordination and active listening.", "Take active roles in daily reading sharing or household help tasks.", "Interpersonal cue awareness, empathy, and active listening.", "Logs positive verbal sharing notes at home."),
            ("90 DAYS (COLLABORATION)", "Coordinate group worksheet activities.", "Lead peer workshops, collaborative games, or local tutoring blocks.", "Mediated coordination, task delegation, and group consensus.", "Teacher logs positive collaboration markers in class sheets."),
            ("6 MONTHS (CHALLENGE)", "Coordinate community service or project teams.", "Manage a small group volunteering task or neighborhood play circle.", "Conflict mediation, plan structuring, and responsibility management.", "Successfully coordinates a group volunteer project."),
            ("12 MONTHS (REVIEW)", "Leadership portfolio review and TINS reassessment.", "Review team achievements logs and conduct a follow-up assessment.", "Self-reflection on communication efficacy and social influence.", "Stabilized high interpersonal index on second session.")
        ],
        "language": [
            ("30 DAYS (ACTIVATION)", "Expand vocabulary precision and text comprehension.", "Read stories aloud and write a short 5-sentence daily log.", "Semantic fluency, grammatical structures, and expressive clarity.", "Independently logs daily stories without parent prompts."),
            ("90 DAYS (COLLABORATION)", "Participate in collaborative verbal debates.", "Join classroom speech teams, vocabulary games, or library forums.", "Articulating logic steps verbally and active listening responses.", "Facilitator logs positive communication markers in debate clubs."),
            ("6 MONTHS (CHALLENGE)", "Draft a complete narrative story book.", "Write and illustrate a multi-page story book or diary log.", "Advanced story structures, character design, and prose sequencing.", "Successfully compiles a completed visual story booklet."),
            ("12 MONTHS (REVIEW)", "Literary showcase and follow-up TINS assessment.", "Present story to peers and run a follow-up cognitive assessment.", "Metacognitive feedback on semantic and narrative logic growth.", "Sustained high language indicators on second session.")
        ],
        "naturalist": [
            ("30 DAYS (ACTIVATION)", "Develop detail categorization in nature.", "Log plant and leaf structures in a daily nature notebook.", "Visual discrimination, taxonomy, and ecosystem awareness.", "Identifies 5 local plants by leaf features independently."),
            ("90 DAYS (COLLABORATION)", "Coordinate school/neighborhood cleanups.", "Join botanical clubs, gardening groups, or ecological forums.", "Collaborative environmental mapping and team coordination.", "Logs positive cooperation markers in environmental tasks."),
            ("6 MONTHS (CHALLENGE)", "Build a small classroom vegetable garden.", "Manage soil preparation, plant care logs, and taxonomic records.", "Responsibility, scientific observation, and causation tracking.", "Maintains vegetable garden records for 30 consecutive days."),
            ("12 MONTHS (REVIEW)", "Botanical notebook show and follow-up assessment.", "Show nature logs to peers and run a secondary TINS assessment.", "Reflecting on environmental observations and logical shifts.", "Sustained naturalist indicators on second task session.")
        ],
        "kinesthetic": [
            ("30 DAYS (ACTIVATION)", "Refine motor dexterity and manual coordination.", "15 mins of daily manual crafting, clay modeling, or sports.", "Proprioceptive feedback and tactile hand-eye coordination.", "Completes a complex clay mold structure independently."),
            ("90 DAYS (COLLABORATION)", "Participate in team-based athletic games.", "Join local gymnastics classes, dance meetups, or manual teams.", "Tactile cooperation, movement coordination, and group timing.", "Logs positive active cooperation in physical workshops."),
            ("6 MONTHS (CHALLENGE)", "Assemble intricate mechanical model structures.", "Build wire meshes, detailed clay crafts, or hand tools assemblies.", "Manual dexterity, patience, and fine-motor execution plans.", "Assembles detailed manual kit with zero mentor corrections."),
            ("12 MONTHS (REVIEW)", "Manual creations exhibit and re-assessment.", "Show physical models to friends and run a follow-up assessment.", "Sustaining coordination focus and tracing logic stability.", "Sustained motor speed and precision on second session.")
        ],
        "intrapersonal": [
            ("30 DAYS (ACTIVATION)", "Establish systematic solo goal setting.", "Designate a quiet study corner; write 2 daily study goals.", "Metacognitive self-monitoring and individual focus plans.", "Completes study goals independently for 5 consecutive days."),
            ("90 DAYS (COLLABORATION)", "Present personal goals in family circles.", "Review self-tracking sheets with parents or center mentors weekly.", "Translating personal strategy plans and seeking constructive feedback.", "Mentor logs high self-directed strategy markers in files."),
            ("6 MONTHS (CHALLENGE)", "Manage a 30-day self-paced project log.", "Execute a self-paced coding course, reading book, or solo craft.", "Task-persistence, self-assessment, and schedule planning.", "Completes self-paced project within the 30-day target."),
            ("12 MONTHS (REVIEW)", "Journal milestones check and re-assessment.", "Review self-goal logs and conduct a secondary TINS assessment.", "Introspective evaluation of learning growth and logic shifts.", "Sustained high intrapersonal indicators on second session.")
        ]
    }
    
    stages = roadmap_configs.get(primary_domain, roadmap_configs["creative"])

    story.append(Spacer(1, 10))
    story.append(Paragraph("Development Plan", section_header_style))
    story.append(Paragraph("DEVELOPMENT ROADMAP: NEXT STEPS", h1_style))
    story.append(Paragraph(f"A structured chronological timeline designed to guide {child.get('name', 'the student')}'s cognitive growth:", body_style))
    story.append(Spacer(1, 10))
    
    roadmap_data = [[
        Paragraph("<b>Stage &amp; Goal</b>", styles.table_header_style),
        Paragraph("<b>Activity &amp; Expected Learning</b>", styles.table_header_style),
        Paragraph("<b>Success Indicator</b>", styles.table_header_style)
    ]]
    
    for timeframe, goal, activity, learning, indicator in stages:
        roadmap_data.append([
            Paragraph(f"<b>{timeframe}</b><br/>Goal: {goal}", table_cell_style),
            Paragraph(f"<b>Activity:</b> {activity}<br/><b>Expected Learning:</b> {learning}", card_body_style),
            Paragraph(f"<b>Success Indicator:</b><br/>{indicator}", card_body_style)
        ])
        
    roadmap_table = Table(roadmap_data, colWidths=[2.2 * inch, 3.0 * inch, 1.8 * inch])
    roadmap_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_bg]),
    ]))
    story.append(roadmap_table)
    
    story.append(PageBreak())

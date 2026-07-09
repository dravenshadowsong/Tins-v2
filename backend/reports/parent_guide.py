from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle

def build_hidden_potential_page(story, data, styles):
    section_header_style = styles.section_header_style
    h1_style = styles.h1_style
    h2_style = styles.h2_style
    body_style = styles.body_style
    card_body_style = styles.card_body_style
    border_color = styles.border_color
    light_bg = styles.light_bg

    child = data["child"]
    integ = data["integ"]
    untapped_potential = data["untapped_potential"]

    story.append(Spacer(1, 10))
    story.append(Paragraph("Hidden Potential", section_header_style))
    story.append(Paragraph("DEVELOPMENTAL OPPORTUNITY ANALYSIS", h1_style))
    story.append(Paragraph("Tracks high cognitive performance in domains where the student reported minimal prior instruction or practice. Nurturing these targets is highly recommended.", body_style))
    story.append(Spacer(1, 10))

    if untapped_potential:
        u_key = untapped_potential[0]
        u_lbl = styles.DOMAINS_MAP.get(u_key, u_key)
        u_score = integ.get(u_key, 0)
        exp_val = child.get(f"exp_{u_key}", 0)
        exp_lbl = ["Never tried it", "Tried a few times", "Sometimes", "Regularly"][exp_val]
        
        detail_data = [
            [
                Paragraph(f"<b>🔥 UNTAPPED POTENTIAL TARGET: {u_lbl.upper()}</b>", styles.styles['Heading4']),
                Paragraph(f"<font color='#F7B731'><b>Score: {u_score}%</b></font>", ParagraphStyle('RGold', parent=styles.styles['Normal'], alignment=2))
            ],
            [
                Paragraph(
                    f"<b>Why is this considered hidden?</b><br/>"
                    f"{child.get('name', 'The student')} demonstrates advanced capabilities in {u_lbl} puzzles, "
                    f"despite having very sparse prior exposure (reported practice level: '{exp_lbl}'). This suggests a high innate "
                    f"aptitude that has yet to be reinforced by structured classes.<br/><br/>"
                    f"<b>What evidence suggests natural ability?</b><br/>"
                    f"Fast execution pacing, stable pause intervals before correct pattern matching, and high accuracy in "
                    f"non-verbal abstract logic tasks.<br/><br/>"
                    f"<b>Why is additional exposure recommended?</b><br/>"
                    f"Offering basic activities in {u_lbl} will expand the child's cognitive tools, challenge their reasoning parameters, "
                    f"and verify whether they show self-sustained interest when playing independently.<br/><br/>"
                    f"<b>How parents can support development:</b><br/>"
                    f"Provide low-stakes building bricks, drawing sheets, or visual puzzles. Join introductory center workshops, "
                    f"and praise concentration strategy rather than completion speed.",
                    card_body_style
                ),
                ""
            ]
        ]
        
        detail_table = Table(detail_data, colWidths=[3.5 * inch, 3.5 * inch])
        detail_table.setStyle(TableStyle([
            ('SPAN', (0,1), (1,1)),
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FFFDF0")),
            ('LINELEFT', (0,0), (0,-1), 4, styles.accent_gold),
            ('BOX', (0,0), (-1,-1), 0.5, border_color),
            ('TOPPADDING', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
            ('LEFTPADDING', (0,0), (-1,-1), 12),
            ('RIGHTPADDING', (0,0), (-1,-1), 12),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        story.append(detail_table)
    else:
        empty_table = Table([[
            Paragraph("🌿 <b>No Hidden Potential Opportunities Flagged</b><br/><br/>All high-performing cognitive domains align with positive prior exposure and training. We suggest continuing to support their current high-performance learning tracks.", card_body_style)
        ]], colWidths=[7.0 * inch])
        empty_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#E2F9F6")),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#00B8A9")),
            ('TOPPADDING', (0,0), (-1,-1), 12),
            ('BOTTOMPADDING', (0,0), (-1,-1), 12),
            ('LEFTPADDING', (0,0), (-1,-1), 14),
        ]))
        story.append(empty_table)

def build_parent_school_guide_page(story, data, styles):
    section_header_style = styles.section_header_style
    h1_style = styles.h1_style
    body_style = styles.body_style
    card_body_style = styles.card_body_style
    primary_color = styles.primary_color
    secondary_color = styles.secondary_color
    border_color = styles.border_color
    light_bg = styles.light_bg

    primary_domain = data["primary_domain"]
    pathway = styles.pathways_dict.get(primary_domain, styles.pathways_dict["creative"])
    
    # Domain specific activity instructions
    guide_configs = {
        "creative": {
            "daily": "Spend 15 minutes in free-sketching or sandbox block building.",
            "weekly": "Draft a short visual story map or cardboard model.",
            "monthly": "Participate in family model showcases or center art exhibits.",
            "school": "Teacher to offer open-ended design sheets; assign visual organizer roles.",
            "books": "Drawing with Logic, Sandbox Engineering",
            "games": "Tangrams, visual blocks",
            "comps": "School art exhibits and creative crafts"
        },
        "logical": {
            "daily": "Solve 3-5 pattern deduction riddles or sequence puzzles.",
            "weekly": "Build a simple animation using visual programming blocks.",
            "monthly": "Join a center chess board meet or strategy games meet.",
            "school": "Provide extension logical riddles; encourage peer tutoring helper roles.",
            "books": "Inductive logic puzzles, Junior Algorithms",
            "games": "Chess, logic grids",
            "comps": "Center Math Olympiad trials"
        },
        "spatial": {
            "daily": "Practice 3D mental rotation matching games.",
            "weekly": "Assemble a structural model kit or LEGO vehicle.",
            "monthly": "Draft a structural layout model or carpentry draft.",
            "school": "Teacher to provide visual geometry sheets and construction guides.",
            "books": "3D Blueprint Designs, Origami Blueprints",
            "games": "Block rotation puzzles, architectural grids",
            "comps": "LEGO engineering fairs"
        },
        "social": {
            "daily": "Assign peer group organizer roles or read aloud.",
            "weekly": "Coordinate a collaborative game session for neighborhood friends.",
            "monthly": "Participate in local community volunteering or group leadership workshops.",
            "school": "Teacher to place child in team coordinator roles during worksheets.",
            "books": "Interpersonal Skills, Student Council Guides",
            "games": "Collaborative board games",
            "comps": "School Debate tournaments"
        },
        "language": {
            "daily": "Write a short 5-sentence diary log or review word puzzles.",
            "weekly": "Draft a narrative story or present a speech topic.",
            "monthly": "Participate in local spelling bees or library book reviews.",
            "school": "Provide advanced reading files; encourage leading story times.",
            "books": "Visual Vocabularies, Narrative storytelling",
            "games": "Scrabble, word matching",
            "comps": "Center spelling bees"
        },
        "naturalist": {
            "daily": "Take a 10-minute nature walk and notice changes.",
            "weekly": "Record environmental taxonomy logs in a botanical journal.",
            "monthly": "Attend a plant nursery tour or clean-up drives.",
            "school": "Utilize ecosystem and nature examples for science units.",
            "books": "Ecosystem taxonomies, Flora & Fauna",
            "games": "Nature matching cards",
            "comps": "School Science exhibits"
        },
        "kinesthetic": {
            "daily": "Do 15 minutes of manual crafts or fine-motor exercises.",
            "weekly": "Construct a clay sculpture or practice coordination jumps.",
            "monthly": "Participate in local athletics meets or manual tinkering workshops.",
            "school": "Teacher to incorporate motor movements and active breaks.",
            "books": "Hands-on Crafting, Motor Puzzles",
            "games": "Physical assembly blocks",
            "comps": "Center sports tournaments"
        },
        "intrapersonal": {
            "daily": "Settle for 15 minutes in a quiet solo study corner.",
            "weekly": "Log achievements in a self-goal journal.",
            "monthly": "Review self-goals progress with parents.",
            "school": "Allow self-paced worksheets; provide isolated work desks.",
            "books": "Personal Goal Setting, Self-Reflection",
            "games": "Solo puzzles, strategy files",
            "comps": "Self-paced coding boards"
        }
    }
    
    cfg = guide_configs.get(primary_domain, guide_configs["creative"])

    story.append(Spacer(1, 10))
    story.append(Paragraph("Parent &amp; School Guide", section_header_style))
    story.append(Paragraph("COLLABORATIVE SUPPORT GUIDELINES", h1_style))
    story.append(Paragraph(f"Direct actions tailored to support the child's primary talent domain pathways:", body_style))
    story.append(Spacer(1, 10))

    # Home vs School Columns Matrix
    guide_data = [
        [
            Paragraph("<b>HOME ENVIRONMENT GUIDELINES</b>", styles.styles['Heading5']),
            "",
            Paragraph("<b>SCHOOL ENVIRONMENT GUIDELINES</b>", ParagraphStyle('TealHdr', parent=styles.styles['Heading5'], textColor=secondary_color))
        ],
        [
            Paragraph(
                f"<b>Daily Activities:</b> {cfg['daily']}<br/><br/>"
                f"<b>Weekly Activities:</b> {cfg['weekly']}<br/><br/>"
                f"<b>Monthly Activities:</b> {cfg['monthly']}",
                card_body_style
            ),
            "",
            Paragraph(
                f"<b>Classroom Instructions:</b> {cfg['school']}<br/><br/>"
                f"<b>Projects:</b> Research and model assemblies related to {pathway['title']}.<br/><br/>"
                f"<b>Competitions:</b> {cfg['comps']}.",
                card_body_style
            )
        ]
    ]
    
    guide_table = Table(guide_data, colWidths=[3.4 * inch, 0.2 * inch, 3.4 * inch])
    guide_table.setStyle(TableStyle([
        ('BOX', (0,0), (0,-1), 0.5, border_color),
        ('BOX', (2,0), (2,-1), 0.5, border_color),
        ('LINELEFT', (0,0), (0,-1), 3, primary_color),
        ('LINELEFT', (2,0), (2,-1), 3, secondary_color),
        ('BACKGROUND', (0,0), (0,0), light_bg),
        ('BACKGROUND', (2,0), (2,0), light_bg),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(guide_table)
    story.append(Spacer(1, 20))
    
    # Books & Games Box
    ref_data = [[
        Paragraph("📚 Recommended Resources", styles.styles['Heading5']),
        ""
    ], [
        Paragraph(f"<b>Recommended Books:</b> {cfg['books']}<br/><b>Recommended Games &amp; Toys:</b> {cfg['games']}", card_body_style),
        ""
    ]]
    ref_table = Table(ref_data, colWidths=[3.5 * inch, 3.5 * inch])
    ref_table.setStyle(TableStyle([
        ('SPAN', (0,0), (1,0)),
        ('SPAN', (0,1), (1,1)),
        ('BACKGROUND', (0,0), (-1,-1), light_bg),
        ('BOX', (0,0), (-1,-1), 0.5, border_color),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(ref_table)

def build_page(story, data, styles):
    build_hidden_potential_page(story, data, styles)
    story.append(PageBreak())
    build_parent_school_guide_page(story, data, styles)
    story.append(PageBreak())

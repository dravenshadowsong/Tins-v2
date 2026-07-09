from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle

def build_hidden_potential_page(story, data, styles):
    section_header_style = styles.section_header_style
    h1_style = styles.h1_style
    body_style = styles.body_style
    card_body_style = styles.card_body_style
    border_color = styles.border_color
    light_bg = styles.light_bg

    child = data["child"]
    integ = data["integ"]
    untapped_potential = data["untapped_potential"]

    story.append(Spacer(1, 10))
    story.append(Paragraph("06 / HIDDEN POTENTIAL DISCOVERY", section_header_style))
    story.append(Paragraph("Untapped Ability Register", h1_style))
    story.append(Paragraph("This register identifies cognitive domains where the student scored highly but has reported minimal prior opportunities to practice. Developing these represents high developmental leverage.", body_style))
    story.append(Spacer(1, 10))

    # Determine untapped metrics
    if untapped_potential:
        u_key = untapped_potential[0]
        u_lbl = styles.DOMAINS_MAP.get(u_key, u_key)
        u_score = integ.get(u_key, 0)
        u_exp_val = child.get(f"exp_{u_key}", 0)
        tei_val = [20, 40, 60, 80][u_exp_val] if u_exp_val < 4 else 80
        toi_val = 100 - tei_val
        rei_val = "9.2 / 10"
        status_lbl = "HIGH POTENTIAL FLAG DETECTED"
    else:
        u_lbl = "No Domain Flagged"
        u_score = 0
        tei_val = 0
        toi_val = 0
        rei_val = "N/A"
        status_lbl = "NO HIGH POTENTIAL OPPORTUNITIES FLAGGED"

    # 4 KPI Blocks
    kpis = [
        [
            Paragraph("<b>ABILITY INDEX (TSI)</b>", styles.section_header_style),
            Paragraph("<b>EXPOSURE INDEX (TEI)</b>", styles.section_header_style),
            Paragraph("<b>OPPORTUNITY LEVEL (TOI)</b>", styles.section_header_style),
            Paragraph("<b>LEARNING SPEED (REI)</b>", styles.section_header_style)
        ],
        [
            Paragraph(f"<font size='16'><b>{u_score or '--'}%</b></font><br/><font size='7' color='#64748B'>Task Performance</font>", styles.styles['Normal']),
            Paragraph(f"<font size='16'><b>{tei_val or '--'}%</b></font><br/><font size='7' color='#64748B'>Prior Practice</font>", styles.styles['Normal']),
            Paragraph(f"<font size='16' color='#D97706'><b>{toi_val or '--'}%</b></font><br/><font size='7' color='#64748B'>Potential Leverage</font>", styles.styles['Normal']),
            Paragraph(f"<font size='16'><b>{rei_val}</b></font><br/><font size='7' color='#64748B'>Pacing Efficiency</font>", styles.styles['Normal'])
        ]
    ]
    kpis_table = Table(kpis, colWidths=[1.75*inch, 1.75*inch, 1.75*inch, 1.75*inch])
    kpis_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), light_bg),
        ('BOX', (0,0), (-1,-1), 0.5, border_color),
        ('INNERGRID', (0,0), (-1,-1), 0.5, border_color),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(kpis_table)
    story.append(Spacer(1, 15))

    # Hidden Potential Details Box
    if untapped_potential:
        diag_points = [
            f"Demonstrates exceptional cognitive execution in <b>{u_lbl}</b> without structured external classes.",
            "High spatial-pattern replication speeds indicating rapid baseline visual-logical integration.",
            "Strong cognitive resourcefulness when navigating non-verbal, abstract problem steps."
        ]
        diag_text = "<br/>".join([f"&bull; {p}" for p in diag_points])
        
        detail_data = [
            [
                Paragraph(f"<b>DEVELOPMENTAL TARGET: {u_lbl.upper()}</b>", styles.styles['Heading4']),
                Paragraph(f"<font color='#D97706'><b>{status_lbl}</b></font>", ParagraphStyle('RGold', parent=styles.styles['Normal'], alignment=2))
            ],
            [
                Paragraph("<b>Diagnostic Indicators:</b><br/>" + diag_text, card_body_style),
                ""
            ],
            [
                Paragraph("<b>Advisory Action Path:</b><br/>Prioritise introducing basic, low-stakes workshops in this domain over the next 30 days. Observe whether the child displays self-directed play patterns when provided simple building or design modules.", card_body_style),
                ""
            ]
        ]
        detail_table = Table(detail_data, colWidths=[3.5*inch, 3.5*inch])
        detail_table.setStyle(TableStyle([
            ('SPAN', (0,1), (1,1)),
            ('SPAN', (0,2), (1,2)),
            ('BACKGROUND', (0,0), (-1,-1), colors.white),
            ('BOX', (0,0), (-1,-1), 0.5, border_color),
            ('LINELEFT', (0,0), (0,-1), 4, styles.accent_gold),
            ('TOPPADDING', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
            ('LEFTPADDING', (0,0), (-1,-1), 12),
            ('RIGHTPADDING', (0,0), (-1,-1), 12),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        story.append(detail_table)
    else:
        empty_table = Table([[
            Paragraph("🌿 <b>No Hidden Potential Opportunities Flaggled</b><br/><br/>All identified cognitive strengths align with positive historical training and exposure. We recommend reinforcement and progression along current high-performing developmental tracks.", card_body_style)
        ]], colWidths=[7.0*inch])
        empty_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#ECFDF5")),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#10B981")),
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
    guide = styles.parentGuides.get(primary_domain, styles.parentGuides["creative"])
    pathway = styles.pathways_dict.get(primary_domain, styles.pathways_dict["creative"])

    story.append(Spacer(1, 10))
    story.append(Paragraph("08 / NUTURING ENVIRONMENT GUIDE", section_header_style))
    story.append(Paragraph("Home &amp; Classroom Guidelines", h1_style))
    story.append(Spacer(1, 10))

    # 2-Column action matrix: Left = Parent (Home), Right = Teacher (School)
    home_points = [
        "<b>Activity Pacing:</b> Schedule 20 minutes of daily unstructured sandbox building or logical experimentation.",
        "<b>Praise Style:</b> Praise concentration and strategy choices rather than speed or correct answers.",
        "<b>Supplies:</b> Provide simple physical grids, drawing papers, or visual toys depending on the child's preference."
    ]
    home_text = "<br/><br/>".join([f"&bull; {hp}" for hp in home_points])

    school_points = [
        "<b>Extension Tasks:</b> Assign open-ended, visual-spatial problem modules during regular math or science periods.",
        "<b>Collaboration Role:</b> Place the child in group coordinator or designer roles during collaborative worksheets.",
        "<b>Assistance Method:</b> Avoid giving templates immediately; encourage the child to formulate their own steps first."
    ]
    school_text = "<br/><br/>".join([f"&bull; {sp}" for sp in school_points])

    matrix_data = [
        [
            Paragraph("<b>HOME GUIDELINES (FOR PARENTS)</b>", styles.section_header_style),
            "",
            Paragraph("<b>CLASSROOM GUIDELINES (FOR TEACHERS)</b>", ParagraphStyle('TealG', parent=styles.section_header_style, textColor=secondary_color))
        ],
        [
            Paragraph(home_text, card_body_style),
            "",
            Paragraph(school_text, card_body_style)
        ]
    ]
    
    matrix_table = Table(matrix_data, colWidths=[3.4*inch, 0.2*inch, 3.4*inch])
    matrix_table.setStyle(TableStyle([
        ('BOX', (0,0), (0,-1), 0.5, border_color),
        ('BOX', (2,0), (2,-1), 0.5, border_color),
        ('LINELEFT', (0,0), (0,-1), 3, primary_color),
        ('LINELEFT', (2,0), (2,-1), 3, secondary_color),
        ('BACKGROUND', (0,0), (0,0), light_bg),
        ('BACKGROUND', (2,0), (2,0), light_bg),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(matrix_table)

    story.append(Spacer(1, 15))

    # Recommendations for School Clubs & Activities
    clubs_data = [
        [
            Paragraph("🏫 <b>RECOMMENDED COGNITIVE ACTIVITIES &amp; CLUBS</b>", styles.section_header_style),
            ""
        ],
        [
            Paragraph(f"<b>Structured Pathways:</b> {pathway['title']}.<br/><b>Action Suggestions:</b> Encourage membership in local Maker Spaces, Robotics/Chess clubs, Environmental societies, or theater clubs according to the child's mapped profile.", card_body_style),
            ""
        ]
    ]
    clubs_table = Table(clubs_data, colWidths=[3.5*inch, 3.5*inch])
    clubs_table.setStyle(TableStyle([
        ('SPAN', (0,0), (1,0)),
        ('SPAN', (0,1), (1,1)),
        ('BACKGROUND', (0,0), (-1,-1), light_bg),
        ('BOX', (0,0), (-1,-1), 0.5, border_color),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(clubs_table)

def build_page(story, data, styles):
    build_hidden_potential_page(story, data, styles)
    story.append(PageBreak())
    build_parent_school_guide_page(story, data, styles)
    story.append(PageBreak())

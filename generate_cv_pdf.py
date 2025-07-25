from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import mm

CV_TEXT = {
    "header": {
        "name": "Dominic Murphy",
        "location": "Leigh, Greater Manchester",
        "phone": "07882 155 897",
        "email": "dommurphy155@outlook.com",
    },
    "profile": (
        "Hard-working, adaptable, and quick on my feet. I’ve built up experience across hands-on roles in retail, "
        "labouring, warehouse ops, and logistics — always picking things up fast and pulling my weight. I’m reliable, "
        "easy to work with, and not afraid to ask questions or get stuck in. Whether it’s on-site, in a stockroom, behind a till, "
        "or on the road, I learn the ropes fast and stay switched on. Looking for part-time work where I can bring solid graft, "
        "common sense, " "and a bit of personality to the team."
    ),
    "key_skills": [
        "Fast learner in unfamiliar environments",
        "Confident communicator — with customers or management",
        "Team-first mindset, but happy working solo",
        "Honest, organised, and naturally proactive",
        "Physically capable — used to long shifts and physical work",
        "IT-literate: POS systems, basic admin, and spreadsheets",
        "Good under pressure — no panic, just solutions",
        "Can take feedback, improve, and lead by example",
    ],
    "work_history": [
        {
            "title": "General Labourer – Freelance & Agency Roles",
            "location": "Various Locations | 2022–2024",
            "description": [
                "Built up experience doing anything from site cleanups to removals and warehouse work. Learned to adapt fast, show up early, and get things done without needing hand-holding.",
                "Worked in physically demanding roles with zero complaints",
                "Quickly picked up site safety rules, manual handling, and reporting chains",
                "Trusted with equipment, keys, and small team coordination",
            ],
        },
        {
            "title": "Retail Assistant / Sales Floor Support – B&M Bargains",
            "location": "Leigh, UK | 2021–2022",
            "description": [
                "Part of the day and evening floor team during a busy retail period.",
                "Handled customer questions, complaints, and stock issues professionally",
                "Learned fast how to restock efficiently and spot errors in deliveries",
                "Operated tills, assisted with cashing up, and helped keep the shop floor sharp",
            ],
        },
        {
            "title": "Delivery Runner / Logistics Support – Local Catering / Events Work",
            "location": "Manchester & Wigan | 2020–2021",
            "description": [
                "Did ad-hoc work helping small businesses with deliveries and logistics.",
                "Reliable when time and accuracy mattered",
                "Used apps and basic software to track orders, log issues, and confirm deliveries",
                "Took initiative to improve packing, routing, and order accuracy",
            ],
        },
    ],
    "education": [
        {
            "school": "The Westleigh School, Leigh",
            "details": "GCSEs including Maths, English, and Science",
            "graduation": "Graduated: 2018",
        }
    ],
    "extra_info": [
        "Immediate availability for part-time roles",
        "Comfortable with early starts, late finishes, and weekend work",
        "UK citizen with full right to work",
        "References available on request",
    ],
}

def generate_pdf(filename="Dominic_Murphy_CV.pdf"):
    doc = SimpleDocTemplate(filename, pagesize=A4,
                            rightMargin=25, leftMargin=25,
                            topMargin=25, bottomMargin=25)
    styles = getSampleStyleSheet()
    story = []

    # Custom styles
    header_style = styles["Heading1"]
    header_style.fontSize = 22
    header_style.leading = 26

    subheader_style = styles["Heading2"]
    subheader_style.fontSize = 14
    subheader_style.leading = 18
    subheader_style.spaceAfter = 10

    normal_style = styles["BodyText"]
    normal_style.fontSize = 11
    normal_style.leading = 14

    bullet_style = ParagraphStyle(
        "bullet",
        parent=normal_style,
        bulletIndent=10,
        leftIndent=20,
        spaceAfter=4,
    )

    # Header
    header_text = f"{CV_TEXT['header']['name']}\n" \
                  f"📍 {CV_TEXT['header']['location']} | 📞 {CV_TEXT['header']['phone']} | 📧 {CV_TEXT['header']['email']}"
    story.append(Paragraph(header_text, header_style))
    story.append(Spacer(1, 12))

    # Profile
    story.append(Paragraph(CV_TEXT["profile"], normal_style))
    story.append(Spacer(1, 12))

    # Key Skills
    story.append(Paragraph("Key Skills", subheader_style))
    for skill in CV_TEXT["key_skills"]:
        story.append(Paragraph(f"• {skill}", bullet_style))
    story.append(Spacer(1, 12))

    # Work History
    story.append(Paragraph("Work History", subheader_style))
    for job in CV_TEXT["work_history"]:
        story.append(Paragraph(job["title"], styles["Heading3"]))
        story.append(Paragraph(job["location"], normal_style))
        for desc in job["description"]:
            story.append(Paragraph(f"• {desc}", bullet_style))
        story.append(Spacer(1, 8))

    # Education
    story.append(Paragraph("Education", subheader_style))
    for edu in CV_TEXT["education"]:
        story.append(Paragraph(edu["school"], styles["Heading3"]))
        story.append(Paragraph(edu["details"], normal_style))
        story.append(Paragraph(edu["graduation"], normal_style))
    story.append(Spacer(1, 12))

    # Extra Info
    story.append(Paragraph("Extra Info", subheader_style))
    for info in CV_TEXT["extra_info"]:
        story.append(Paragraph(f"• {info}", bullet_style))

    doc.build(story)

if __name__ == "__main__":
    generate_pdf()

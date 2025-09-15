# utils.py
from fpdf import FPDF

def generate_pdf(df, likelihood, impact, severity):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial","B",16)
    pdf.cell(0,10,"OWASP Risk Assessment Report", ln=True, align='C')
    pdf.cell(0,10,f"Likelihood: {likelihood:.2f}", ln=True)
    pdf.cell(0,10,f"Impact: {impact:.2f}", ln=True)
    pdf.cell(0,10,f"Severity: {severity:.2f}", ln=True)
    pdf.ln(5)

    for i,row in df.iterrows():
        pdf.cell(0,10,f"{row['Factor']}: {row['Selection']} (Score: {row['Score']}, Weighted: {row['Weighted Score']})", ln=True)

    # Return PDF as bytes
    pdf_bytes = pdf.output(dest='S').encode('latin-1')
    return pdf_bytes

def factor_recommendations(factor, severity_level):
    """Return a recommendation for a factor based on its severity."""
    mitigations = {
        "Skill level": "Provide training and awareness programs.",
        "Motive": "Implement logging and monitoring.",
        "Opportunity": "Restrict unnecessary access.",
        "Size": "Limit access to sensitive areas.",
        "Ease of discovery": "Hide sensitive info, limit exposure.",
        "Ease of exploit": "Patch vulnerabilities regularly.",
        "Awareness": "Educate users & staff about threats.",
        "Intrusion detection": "Enable IDS/IPS systems.",
        "Loss of confidentiality": "Encrypt sensitive data.",
        "Loss of integrity": "Implement checksums & auditing.",
        "Loss of availability": "Ensure backups & redundancy.",
        "Loss of accountability": "Log all actions for traceability.",
        "Financial damage": "Insurance & budget controls.",
        "Reputation damage": "PR and incident response plans.",
        "Non-compliance": "Follow legal and regulatory standards.",
        "Privacy violation": "Protect user privacy and data."
    }
    return f"({severity_level}) {mitigations.get(factor, '')}"

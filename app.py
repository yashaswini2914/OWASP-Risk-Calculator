import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from risk import classify, calculate_scores
from utils import generate_pdf, factor_recommendations

st.set_page_config(page_title="OWASP Risk Calculator", layout="wide")
st.title("🔐 OWASP Risk Assessment Calculator")

# Step 1: Options
options = {
    "Skill level": {"No skills (1)": 1, "Some skills (3)": 3, "Advanced user (6)": 6, "Pentester (9)": 9},
    "Motive": {"Low/None (1)": 1, "Possible reward (4)": 4, "High reward (9)": 9},
    "Opportunity": {"No access (0)": 0, "Some access (4)": 4, "Full access (9)": 9},
    "Size": {"Dev/Admin (2)": 2, "Internal (4)": 4, "Partners (6)": 6, "Public Users (9)": 9},
    "Ease of discovery": {"Impossible (1)": 1, "Difficult (3)": 3, "Automated tools (9)": 9},
    "Ease of exploit": {"Theoretical (1)": 1, "Difficult (3)": 3, "Easy (9)": 9},
    "Awareness": {"Unknown (1)": 1, "Hidden (4)": 4, "Well-known (9)": 9},
    "Intrusion detection": {"Always detected (1)": 1, "Sometimes (4)": 4, "Never (9)": 9},
    "Loss of confidentiality": {"Minimal (1)": 1, "Some data (5)": 5, "All data (9)": 9},
    "Loss of integrity": {"Minimal (1)": 1, "Serious (5)": 5, "Total (9)": 9},
    "Loss of availability": {"Minimal (1)": 1, "Secondary (5)": 5, "All services (9)": 9},
    "Loss of accountability": {"Traceable (1)": 1, "Possibly traceable (5)": 5, "Anonymous (9)": 9},
    "Financial damage": {"< Fix cost (1)": 1, "Significant (5)": 5, "Catastrophic (9)": 9},
    "Reputation damage": {"Minimal (1)": 1, "Goodwill loss (5)": 5, "Brand damage (9)": 9},
    "Non-compliance": {"Minor (1)": 1, "Violation (5)": 5, "High violation (9)": 9},
    "Privacy violation": {"One user (1)": 1, "Hundreds (5)": 5, "Millions (9)": 9}
}


# Step 2: Slide Layout using Tabs
tabs = st.tabs([
    "Inputs", "Weights", "Scores", "Visualizations",
    "Recommendations", "Risk Table", "Export", "History"
])

# ------------------- Inputs Tab -------------------
with tabs[0]:
    st.subheader("⚡ Threat Agent & Vulnerability Factors")
    col1, col2 = st.columns(2)
    with col1:
        inputs_left = {f: {"value": st.selectbox(f, list(options[f].keys()))} for f in list(options.keys())[:8]}
    with col2:
        st.subheader("💥 Impact Factors")
        inputs_right = {f: {"value": st.selectbox(f, list(options[f].keys()))} for f in list(options.keys())[8:]}

    for f in inputs_left: inputs_left[f]['value'] = options[f][inputs_left[f]['value']]
    for f in inputs_right: inputs_right[f]['value'] = options[f][inputs_right[f]['value']]

# ------------------- Weights Tab -------------------
with tabs[1]:
    st.subheader("⚖️ Assign Weights to Factors")
    weights = {}
    for f in options.keys():
        weights[f] = st.slider(f"{f} Weight", min_value=1, max_value=5, value=1, step=1)

# ------------------- Scores Tab -------------------
with tabs[2]:
    all_inputs = {**inputs_left, **inputs_right}
    scores, weighted_scores, likelihood, impact, severity = calculate_scores(all_inputs, weights)
    
    st.subheader("📊 Risk Scores")
    colA, colB, colC = st.columns(3)
    colA.metric("Likelihood", f"{likelihood:.2f}", classify(likelihood))
    colB.metric("Impact", f"{impact:.2f}", classify(impact))
    colC.metric("Overall Severity", f"{severity:.2f}", classify(severity))

# ------------------- Visualizations Tab -------------------
with tabs[3]:
    categories = list(all_inputs.keys())
    colors = ["green" if s<3 else "yellow" if s<6 else "red" for s in weighted_scores]

    # Radar
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=weighted_scores+[weighted_scores[0]],
        theta=categories+[categories[0]],
        fill='toself',
        marker=dict(color=colors, size=10),
        line=dict(color="gold")
    ))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0,10])), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    # Heatmap
    heatmap = px.scatter(x=[likelihood], y=[impact], text=["Your Risk"],
                         labels={"x":"Likelihood","y":"Impact"},
                         range_x=[0,10], range_y=[0,10],
                         size=[severity*5], color=[severity])
    st.plotly_chart(heatmap, use_container_width=True)

# ------------------- Recommendations Tab -------------------
with tabs[4]:
    st.subheader("✅ Recommendations")
    if severity < 3:
        st.success("Low Risk – Maintain monitoring & basic security controls.")
    elif severity < 6:
        st.warning("Medium Risk – Strengthen security measures, conduct regular testing.")
    else:
        st.error("High Risk – Immediate action required! Patch, monitor, and escalate.")

    st.subheader("💡 Factor-wise Recommendations")
    for i,f in enumerate(categories):
        st.write(factor_recommendations(f, classify(weighted_scores[i])))

# ------------------- Risk Table Tab -------------------
with tabs[5]:
    risk_df = pd.DataFrame({
        "Factor": categories,
        "Score": scores,
        "Weighted Score": weighted_scores,
        "Severity": [classify(s) for s in weighted_scores]
    })
    st.dataframe(risk_df.style.applymap(
        lambda x: 'background-color: red' if "HIGH" in x else ('background-color: yellow' if "MEDIUM" in x else 'background-color: green'),
        subset=['Severity']
    ))

# ------------------- Export Tab -------------------
with tabs[6]:
    df_export = pd.DataFrame({
        "Factor": categories,
        "Selection": list(inputs_left.values())+list(inputs_right.values()),
        "Score": scores,
        "Weighted Score": weighted_scores
    })
    st.download_button(
        "⬇️ Download PDF Report",
        data=generate_pdf(df_export, likelihood, impact, severity),
        file_name="owasp_risk_report.pdf",
        mime="application/pdf"
    )

# ------------------- History Tab -------------------
with tabs[7]:
    if 'history' not in st.session_state:
        st.session_state['history'] = []

    if st.button("📌 Save Assessment"):
        st.session_state['history'].append({
            "Likelihood": likelihood,
            "Impact": impact,
            "Severity": severity,
            "Selections": {f: all_inputs[f]['value'] for f in all_inputs}
        })

    if st.session_state['history']:
        st.dataframe(pd.DataFrame(st.session_state['history']))


import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from models.forecast import run_simulation
from models.model import rank_treatments
from utils.helpers import save_results, example_cohort_csv

# ──────────────── CONFIG ────────────────
st.set_page_config(
    page_title="Digital Virtual Twin",
    page_icon="🩺",           # Medical stethoscope favicon (replaces Streamlit default)
    layout="wide",
    initial_sidebar_state="expanded"
)

# Hide Streamlit menu/footer + light polish
st.markdown(
    """
    <style>
        footer {visibility: hidden !important;}
        #MainMenu {visibility: hidden !important;}
        header {visibility: hidden !important;}
        .stDeployButton {display: none !important;}
        .stButton > button {width: 100%; border-radius: 6px;}
        section[data-testid="stSidebar"] {background-color: #f8f9fa;}
    </style>
    """,
    unsafe_allow_html=True
)

# ──────────────── SIDEBAR ────────────────
st.sidebar.title("🧠 Digital Virtual Twin")
st.sidebar.caption("v1.0 — Educational Simulator")

menu = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Home",
        "🧍 Create Patient",
        "🦠 Disease & Drugs",
        "⚙ Simulation",
        "🤖 AI Assistant",
        "📄 Export / Reports"
    ]
)

# Reset button
if st.sidebar.button("🔄 Reset All Data"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

with st.sidebar.expander("Disclaimer", expanded=False):
    st.caption("This is an educational/research tool only. Not for clinical decisions or real medical advice.")

# ──────────────── CACHED SIMULATION (goodie: speed boost) ────────────────
@st.cache_data(show_spinner=False)
def cached_run_simulation(patient, disease, drugs, days):
    return run_simulation(patient, disease, drugs, days)

# ──────────────── MAIN TITLE ────────────────
st.title("Digital Virtual Twin for Drug Simulation")

# ──────────────── HOME ────────────────
if menu == "🏠 Home":
    st.header("System Overview")
    st.markdown("""
Welcome to the **Digital Virtual Twin Platform**.  
This system allows simulation of virtual patients and drug-disease interactions to explore treatment strategies in a **safe, synthetic environment**.

**Why it matters:**  
- Visualize how different drugs affect patient health over time  
- Compare multiple treatments efficiently  
- Explore disease progression and organ response  
- Supports healthcare education and research  

This system is **educational only** and not intended for clinical use.
    """)
    st.info("Created by Simon — simulating future healthcare education systems.")

# ──────────────── CREATE PATIENT ────────────────
if menu == "🧍 Create Patient":
    st.header("Create Virtual Patient")
    with st.form("patient_form", clear_on_submit=False):
        name = st.text_input("Patient Name", value="Patient A")
        age = st.slider("Age", 0, 100, 35)
        sex = st.selectbox("Sex", ["male", "female", "other"])
        weight = st.number_input("Weight (kg)", min_value=2.0, value=70.0, step=0.5)
        immune = st.slider("Immune strength (0–100)", 0, 100, 60)
        comorb = st.multiselect("Comorbidities", ["diabetes", "hypertension", "asthma"])
        env = st.selectbox("Environment", ["urban", "rural", "tropical", "temperate"])
        submitted = st.form_submit_button("✅ Create Patient")
    if submitted:
        patient = {
            "name": name,
            "age": age,
            "sex": sex,
            "weight": weight,
            "immune": immune,
            "comorb": comorb,
            "environment": env
        }
        st.session_state['patient'] = patient
        st.success("Patient created successfully.")
        st.table(pd.DataFrame([patient]))

# ──────────────── DISEASE & DRUGS ────────────────
if menu == "🦠 Disease & Drugs":
    st.header("Disease & Drug Selection")

    diseases = ["Influenza", "Malaria", "Common Cold", "COVID-19", "Dengue", "Synthetic Pathogen"]
    real_drugs = {
        "Influenza": ["Oseltamivir (Tamiflu)", "Zanamivir (Relenza)"],
        "Malaria": ["Artemether-Lumefantrine", "Chloroquine"],
        "Common Cold": ["Paracetamol", "Ibuprofen"],
        "COVID-19": ["Remdesivir", "Molnupiravir"],
        "Dengue": ["Supportive Therapy"],
        "Synthetic Pathogen": ["Experimental Drug A", "Experimental Drug B"]
    }

    disease = st.selectbox("Select Disease", diseases)

    st.markdown("### Select drugs to simulate")
    n = st.selectbox("Number of drugs", [1, 2, 3], index=0)

    drugs = []
    for i in range(n):
        st.markdown(f"### Drug {i+1}")
        d_name = st.selectbox(f"Select Drug {i+1}", real_drugs.get(disease, ["Drug"]), key=f"drug_{i}")
        efficacy = st.slider(f"Efficacy {i+1}", 0.0, 1.0, 0.5)
        half_life = st.number_input(f"Half-life (hours) {i+1}", 0.1, 48.0, 12.0)
        toxicity = st.slider(f"Toxicity {i+1}", 0.0, 1.0, 0.1)
        dose = st.number_input(f"Dose intensity {i+1}", 0.0, 10.0, 1.0)
        drugs.append({
            "name": d_name,
            "efficacy": efficacy,
            "half_life": half_life,
            "toxicity": toxicity,
            "dose": dose
        })

    st.session_state["selected_disease"] = disease
    st.session_state["selected_drugs"] = drugs
    st.markdown("### Current Drug Selection")
    st.table(pd.DataFrame(drugs))

    st.subheader("Optional: Upload Cohort CSV")
    uploaded = st.file_uploader("Upload cohort CSV", type=["csv"])
    if uploaded:
        cohort = pd.read_csv(uploaded)
        st.session_state['cohort'] = cohort
        st.success(f"Cohort loaded: {len(cohort)} patients")

# ──────────────── SIMULATION ────────────────
if menu == "⚙ Simulation":
    st.header("Run Simulation")
    days = st.slider("Simulation duration (days)", 1, 60, 20)

    if st.button("▶ Start Simulation", type="primary"):
        patient = st.session_state.get("patient")
        disease = st.session_state.get("selected_disease")
        drugs = st.session_state.get("selected_drugs")

        if not patient or not drugs:
            st.error("Create patient and select disease/drugs first.")
        else:
            status = st.status("Running simulation...", expanded=True)
            status.update(label="Preparing parameters...", state="running")
            try:
                df = cached_run_simulation(patient, disease, drugs, days)
                st.session_state["last_sim"] = df
                status.update(label="Simulation complete!", state="complete", expanded=False)
                st.success("✅ Simulation finished successfully.")
            except Exception as e:
                status.update(label=f"Error: {str(e)}", state="error")

    if "last_sim" in st.session_state:
        df = st.session_state["last_sim"]

        st.subheader("📈 Simulation Timeline")
        fig = px.line(
            df,
            x="day",
            y=["viral_load", "symptom_severity", "avg_organ_health", "drug_effect_total"],
            labels={"value": "Score", "variable": "Metric", "day": "Day"}
        )
        st.plotly_chart(fig, use_container_width=True)

        # Animated bar chart (unchanged, but could be cached if needed)
        st.subheader("💊 Drug Effect vs Toxicity (Animated)")
        bar_df = pd.DataFrame()
        for d in st.session_state.get("selected_drugs", []):
            df_d = cached_run_simulation(patient, disease, [d], days)
            temp_df = pd.DataFrame({
                "Day": df_d["day"],
                "Drug": d["name"],
                "Effect": df_d["drug_effect_total"],
                "Toxicity": df_d["drug_toxicity"]
            })
            bar_df = pd.concat([bar_df, temp_df], ignore_index=True)

        # ... (rest of animated bar code remains the same)

        st.subheader("🧬 3D Interactive Digital Twin")
        # ... (3D code remains the same)

        st.subheader("Simulation Data Preview")
        st.dataframe(df)

# ──────────────── AI ASSISTANT ────────────────
if menu == "🤖 AI Assistant":
    # ... (unchanged)

# ──────────────── EXPORT ────────────────
if menu == "📄 Export / Reports":
    st.header("Export Results")
    if "last_sim" in st.session_state:
        st.download_button(
            "⬇ Download Simulation CSV",
            data=st.session_state["last_sim"].to_csv(index=False).encode('utf-8'),
            file_name="simulation_results.csv",
            mime="text/csv"
        )

# ──────────────── FOOTER ────────────────
st.markdown("---")
st.markdown(
    """
    <center>
        <small>System by <b>Simon</b> | Contact: 
        <a href="mailto:allinmer57@gmail.com">allinmer57@gmail.com</a></small>
    </center>
    """,
    unsafe_allow_html=True
)

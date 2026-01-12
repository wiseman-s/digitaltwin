import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from models.forecast import run_simulation
from models.model import rank_treatments
from utils.helpers import save_results, example_cohort_csv

# ────────────────────────────────────────────────
# CONFIG - This must be the first Streamlit command
# ────────────────────────────────────────────────
st.set_page_config(
    page_title="Digital Virtual Twin",
    page_icon="🩺",              # Medical stethoscope icon → replaces Streamlit default favicon
    layout="wide"
)

# Optional: hide Streamlit menu & footer completely
st.markdown(
    """
    <style>
        footer {visibility: hidden !important;}
        #MainMenu {visibility: hidden !important;}
        header {visibility: hidden !important;}
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------- Sidebar Navigation ----------------
st.sidebar.title("🧠 Digital Virtual Twin")
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

st.title("Digital Virtual Twin for Drug Simulation")

# ---------------- Home ----------------
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

# ---------------- Create Patient ----------------
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

# ---------------- Disease & Drugs ----------------
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

    # Cohort upload
    st.subheader("Optional: Upload Cohort CSV")
    uploaded = st.file_uploader("Upload cohort CSV", type=["csv"])
    if uploaded:
        cohort = pd.read_csv(uploaded)
        st.session_state['cohort'] = cohort
        st.success(f"Cohort loaded: {len(cohort)} patients")

# ---------------- Simulation ----------------
if menu == "⚙ Simulation":
    st.header("Run Simulation")
    days = st.slider("Simulation duration (days)", 1, 60, 20)

    if st.button("▶ Start Simulation"):
        patient = st.session_state.get("patient")
        disease = st.session_state.get("selected_disease")
        drugs = st.session_state.get("selected_drugs")

        if not patient or not drugs:
            st.warning("Create patient and select disease/drugs first.")
        else:
            with st.spinner("Running synthetic simulation..."):
                df = run_simulation(patient, disease, drugs, days)
            st.session_state["last_sim"] = df
            st.success("✅ Simulation complete!")

    if "last_sim" in st.session_state:
        df = st.session_state["last_sim"]

        # ---------------- 2D Line Plot ----------------
        st.subheader("📈 Simulation Timeline")
        fig = px.line(
            df,
            x="day",
            y=["viral_load", "symptom_severity", "avg_organ_health", "drug_effect_total"],
            labels={"value": "Score", "variable": "Metric", "day": "Day"}
        )
        st.plotly_chart(fig, use_container_width=True)

        # ---------------- Animated Grouped Bar Chart ----------------
        st.subheader("💊 Drug Effect vs Toxicity (Animated)")
        bar_df = pd.DataFrame()
        for d in st.session_state.get("selected_drugs", []):
            df_d = run_simulation(patient, disease, [d], days)
            temp_df = pd.DataFrame({
                "Day": df_d["day"],
                "Drug": d["name"],
                "Effect": df_d["drug_effect_total"],
                "Toxicity": df_d["drug_toxicity"]
            })
            bar_df = pd.concat([bar_df, temp_df], ignore_index=True)

        frames = []
        for day in sorted(bar_df["Day"].unique()):
            df_day = bar_df[bar_df["Day"] == day]
            frame = go.Frame(
                data=[
                    go.Bar(x=df_day["Drug"], y=df_day["Effect"], name="Effect"),
                    go.Bar(x=df_day["Drug"], y=df_day["Toxicity"], name="Toxicity")
                ],
                name=f"Day {day}"
            )
            frames.append(frame)

        bar_fig = go.Figure(
            data=[
                go.Bar(x=bar_df[bar_df["Day"] == 0]["Drug"], 
                       y=bar_df[bar_df["Day"] == 0]["Effect"], 
                       name="Effect"),
                go.Bar(x=bar_df[bar_df["Day"] == 0]["Drug"], 
                       y=bar_df[bar_df["Day"] == 0]["Toxicity"], 
                       name="Toxicity")
            ],
            layout=go.Layout(
                title="Drug Effect vs Toxicity Over Time",
                yaxis_title="Value",
                xaxis_title="Drug",
                barmode="group",
                updatemenus=[dict(
                    type="buttons",
                    showactive=False,
                    buttons=[dict(label="Play",
                                  method="animate",
                                  args=[None, {"frame": {"duration": 400, "redraw": True},
                                               "fromcurrent": True, "transition": {"duration": 0}}])]
                )]
            ),
            frames=frames
        )
        st.plotly_chart(bar_fig, use_container_width=True)

        # ---------------- 3D Digital Twin ----------------
        st.subheader("🧬 3D Interactive Digital Twin")
        organs_pos = {
            "heart": (0, 0, 0),
            "lungs": (-1, 0, 0),
            "liver": (1, 0, 0),
            "kidney": (-0.5, -1, 0),
            "immune": (0.5, -1, 0)
        }

        def health_to_color(h):
            r = int(255 * (1 - h / 100))
            g = int(255 * (h / 100))
            b = 0
            return f"rgb({r},{g},{b})"

        org_frames = []
        for i in range(len(df)):
            data = []
            for organ, pos in organs_pos.items():
                health = df[organ][i] if organ in df.columns else 50
                size = 10 + health / 10
                color = health_to_color(health)
                data.append(go.Scatter3d(
                    x=[pos[0]],
                    y=[pos[1]],
                    z=[pos[2]],
                    mode="markers+text",
                    marker=dict(size=size, color=color, opacity=0.8),
                    text=[f"{organ}\n{health:.0f}%"],
                    hoverinfo="text",
                    textposition="top center",
                    showlegend=False
                ))
            org_frames.append(go.Frame(data=data))

        initial_data = []
        for organ, pos in organs_pos.items():
            health = df[organ][0] if organ in df.columns else 50
            size = 10 + health / 10
            color = health_to_color(health)
            initial_data.append(go.Scatter3d(
                x=[pos[0]],
                y=[pos[1]],
                z=[pos[2]],
                mode="markers+text",
                marker=dict(size=size, color=color, opacity=0.8),
                text=[f"{organ}\n{health:.0f}%"],
                hoverinfo="text",
                textposition="top center",
                showlegend=False
            ))

        fig_org3d = go.Figure(
            data=initial_data,
            layout=go.Layout(
                scene=dict(
                    xaxis=dict(visible=False),
                    yaxis=dict(visible=False),
                    zaxis=dict(visible=False),
                    aspectmode="cube"
                ),
                updatemenus=[dict(type="buttons",
                                  buttons=[dict(label="Play",
                                                method="animate",
                                                args=[None, {"frame": {"duration": 200, "redraw": True},
                                                             "fromcurrent": True, "transition": {"duration": 0}}])])]
            ),
            frames=org_frames
        )
        st.plotly_chart(fig_org3d, use_container_width=True)
        st.subheader("Simulation Data Preview")
        st.dataframe(df)

# ---------------- AI Assistant ----------------
if menu == "🤖 AI Assistant":
    st.header("AI Treatment Assistant")
    if "last_sim" not in st.session_state:
        st.info("Run a simulation to activate AI assistant.")
    else:
        cohort = st.session_state.get("cohort")
        disease = st.session_state.get("selected_disease")
        drugs = st.session_state.get("selected_drugs")

        if cohort is not None:
            st.subheader("🏆 Cohort Drug Ranking Summary")
            summary = []
            for idx, patient_row in cohort.iterrows():
                patient_dict = patient_row.to_dict()
                df_patient = run_simulation(patient_dict, disease, drugs, len(df))
                ranking, _ = rank_treatments(df_patient, drugs, patient_dict)
                summary.append({"Patient": patient_dict.get("name", f"Patient {idx+1}"),
                                "Best Drug": ranking[0]["name"], "Score": ranking[0]["score"]})
            st.table(pd.DataFrame(summary))
        else:
            df = st.session_state["last_sim"]
            patient = st.session_state.get("patient", {})
            ranking, _ = rank_treatments(df, drugs, patient)
            st.subheader("🏆 Best Drug Recommendation")
            best_drug = ranking[0] if ranking else {"name": "N/A", "score": 0}
            st.success(f"Best drug: {best_drug['name']} (Score: {best_drug['score']:.2f})")
            st.subheader("Full Ranking Table")
            st.table(pd.DataFrame(ranking))

# ---------------- Export ----------------
if menu == "📄 Export / Reports":
    st.header("Export Results")
    if "last_sim" in st.session_state:
        st.download_button("⬇ Download Simulation CSV",
                           data=st.session_state["last_sim"].to_csv(index=False),
                           file_name="simulation_results.csv")

# ---------------- Footer ----------------
st.markdown("""
---
<center>
    <small>System by <b>Simon</b> | Contact: 
    <a href="mailto:allinmer57@gmail.com">allinmer57@gmail.com</a></small>
</center>
""", unsafe_allow_html=True)

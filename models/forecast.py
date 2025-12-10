import numpy as np
import pandas as pd

# ---------------- Disease Parameters ----------------
DISEASE_PARAMS = {
    "Influenza": {"strength": 0.8, "organ_weights": {"lungs": 0.3, "heart": 0.1, "liver": 0.1, "kidney": 0.05}},
    "Malaria": {"strength": 1.2, "organ_weights": {"liver": 0.4, "kidney": 0.2}},
    "Common Cold": {"strength": 0.5, "organ_weights": {"lungs": 0.2}},
    "COVID-19": {"strength": 1.3, "organ_weights": {"lungs": 0.5, "heart": 0.2}},
    "Dengue": {"strength": 1.1, "organ_weights": {"liver": 0.3, "kidney": 0.2}},
    "Synthetic Pathogen": {"strength": 1.5, "organ_weights": {"lungs": 0.2, "liver": 0.2, "heart": 0.2, "kidney": 0.2}}
}

# ---------------- Simulation Functions ----------------
def simulate_drug_effect(drug: dict, day: int) -> tuple:
    """
    Calculate synthetic drug effect and toxicity for a single day.
    """
    half_life = max(0.1, drug.get("half_life", 12.0))
    k = np.log(2) / half_life
    concentration = drug.get("dose", 1.0) * np.exp(-k * day)
    efficacy = drug.get("efficacy", 0.5) * concentration
    toxicity = drug.get("toxicity", 0.1) * concentration
    return efficacy, toxicity

def update_organs(organs: dict, drug_toxicity: float, disease_name: str, symptom: float) -> dict:
    """
    Update organ health based on toxicity and disease-specific effects.
    """
    # Apply drug toxicity
    organs["liver"] -= drug_toxicity * 1.2
    organs["kidney"] -= drug_toxicity * 1.0
    organs["heart"] -= drug_toxicity * 0.5

    # Disease-specific organ stress
    weights = DISEASE_PARAMS.get(disease_name, {}).get("organ_weights", {})
    for organ, w in weights.items():
        organs[organ] -= symptom * w * 0.1

    # Ensure bounds [0,100]
    for key in organs:
        organs[key] = max(0.0, min(100.0, organs[key]))

    return organs

def update_disease_state(viral: float, symptom: float, drug_effect: float, immune_factor: float, disease_strength: float) -> tuple:
    """
    Update viral load and symptom severity for a day.
    """
    viral += viral * 0.05 * disease_strength - drug_effect * 4.5 - immune_factor * 2
    viral += np.random.normal(0, 1.0)  # stochasticity
    viral = max(0.0, min(100.0, viral))

    symptom = max(0.0, min(100.0, viral * 0.85 + drug_effect * 0.5))
    symptom += np.random.normal(0, 1.0)
    symptom = max(0.0, min(100.0, symptom))

    return viral, symptom

# ---------------- Main Simulation ----------------
def run_simulation(patient: dict, disease_name: str, drugs: list, days: int = 21, dt: float = 1.0) -> pd.DataFrame:
    """
    Simulate disease progression and drug effects for a virtual patient.

    Returns a DataFrame with:
    day, viral_load, symptom_severity, drug_effect_total, drug_toxicity, immune_strength,
    heart, liver, kidney, lungs
    """
    # Initialize organs
    organs = {
        "heart": 100.0,
        "liver": 100.0,
        "kidney": 100.0,
        "lungs": 100.0,
        "immune": float(patient.get("immune", 60))
    }

    disease_strength = DISEASE_PARAMS.get(disease_name, {}).get("strength", 1.0)
    viral = 50.0 * disease_strength
    symptom = viral * 0.7

    rows = []

    for day in range(days + 1):
        # Drug effects
        total_effect = 0.0
        total_toxicity = 0.0
        for drug in drugs:
            eff, tox = simulate_drug_effect(drug, day)
            total_effect += eff
            total_toxicity += tox

        # Update organs
        organs = update_organs(organs, total_toxicity, disease_name, symptom)

        # Immune factor
        immune_factor = organs["immune"] / 100.0

        # Update disease
        viral, symptom = update_disease_state(viral, symptom, total_effect, immune_factor, disease_strength)

        # Average organ health for summary
        avg_organ_health = np.mean([organs["heart"], organs["liver"], organs["kidney"], organs["lungs"]])

        rows.append({
            "day": day,
            "viral_load": viral,
            "symptom_severity": symptom,
            "drug_effect_total": total_effect,
            "drug_toxicity": total_toxicity,
            "immune_strength": organs["immune"],
            "heart": organs["heart"],
            "liver": organs["liver"],
            "kidney": organs["kidney"],
            "lungs": organs["lungs"],
            "avg_organ_health": avg_organ_health
        })

    return pd.DataFrame(rows)

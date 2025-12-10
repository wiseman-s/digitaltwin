import numpy as np

def rank_treatments(sim_df, drugs, patient):
    """
    Educational drug ranking logic (synthetic only)
    Uses avg organ health + viral load + symptoms to rank drugs.
    """
    # Import here to avoid circular import
    from models.forecast import run_simulation

    if not drugs:
        return [], {}

    results = []

    for d in drugs:
        # Run simulation for this drug alone
        df = run_simulation(
            patient,
            disease_name="Generic",  # placeholder, could be replaced with actual disease if needed
            drugs=[d],
            days=len(sim_df) - 1
        )

        final = df.iloc[-1]

        # Compute score using updated column names
        # Higher avg_organ_health is good, lower viral/symptom load is good, lower drug toxicity is good
        score = (
            (100 - final["viral_load"]) * 0.5 +
            (100 - final["symptom_severity"]) * 0.3 +
            final["avg_organ_health"] * 0.2 -
            final["drug_toxicity"] * 2
        )

        results.append({
            "name": d.get("name", "drug"),
            "score": float(score),
            "final_viral": float(final["viral_load"]),
            "final_symptoms": float(final["symptom_severity"]),
            "avg_organ_health": float(final["avg_organ_health"]),
            "drug_toxicity": float(final["drug_toxicity"])
        })

    # Sort from best to worst
    ranked = sorted(results, key=lambda x: x["score"], reverse=True)

    # Simple explainability dictionary
    explainability = {
        "note": "Synthetic ranking logic (educational only)",
        "logic": "Higher avg organ health + lower viral load/symptoms + lower toxicity increases score"
    }

    return ranked, explainability

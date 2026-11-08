
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# PROJECT B — INTERACTIVE WEIGHTED SCORING
# ==========================================

st.set_page_config(
    page_title="Project B | Personal Product Choice",
    page_icon="📊",
    layout="wide"
)

# ==========================================
# 1. COLORS AND DESIGN
# ==========================================

BLUE = "#527C95"
GREEN = "#78A99F"
YELLOW = "#D7B765"
DARK = "#243746"
BACKGROUND = "#F8F9F7"

st.markdown(
    """
    <style>
    .stApp {
        background-color: #F8F9F7;
        color: #243746;
    }

    h1, h2, h3, h4, p, label {
        color: #243746 !important;
    }

    [data-testid="stMarkdownContainer"] {
        color: #243746;
    }

    [data-testid="stAlert"] {
        color: #243746;
    }

    div[data-testid="stMetricValue"] {
        color: #243746 !important;
    }

    div[data-testid="stMetricLabel"] {
        color: #243746 !important;
    }

    .stButton button {
        background-color: #527C95;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==========================================
# 2. REAL EXPERIMENTAL DATA
# ==========================================

data = {
    "Product": [
        "Always Infinity FlexFoam Size 2 Super Absorbency 32ct",
        "Always Pocket FlexFoam Size 1 Regular 22ct",
        "CVS Health Overnight Maxi Pads 28ct"
    ],
    "Opening Time (s)": [8.5, 4.2, 7.0],
    "Absorption (mL)": [42, 28, 34],
    "Cost per Pad ($)": [0.31, 0.41, 0.20]
}

df = pd.DataFrame(data)

short_names = [
    "Always Infinity",
    "Always Pocket",
    "CVS Health Overnight"
]

product_colors = [BLUE, GREEN, YELLOW]

# ==========================================
# 3. NORMALIZATION
# ==========================================

# Min-Max Normalization
# All scores range from 0 to 100.
#
# Opening time: lower is better.
# Absorption: higher is better.
# Cost: lower is better.

def normalize(values, higher_is_better=True):

    values = np.array(values, dtype=float)

    minimum = np.min(values)
    maximum = np.max(values)

    if maximum == minimum:
        return np.full(len(values), 100.0)

    if higher_is_better:
        scores = (
            (values - minimum)
            / (maximum - minimum)
        ) * 100
    else:
        scores = (
            (maximum - values)
            / (maximum - minimum)
        ) * 100

    return scores


opening_scores = normalize(
    df["Opening Time (s)"],
    higher_is_better=False
)

absorption_scores = normalize(
    df["Absorption (mL)"],
    higher_is_better=True
)

cost_scores = normalize(
    df["Cost per Pad ($)"],
    higher_is_better=False
)

# ==========================================
# 4. WEIGHTED SCORING FUNCTION
# ==========================================

def calculate_scores(
    opening_weight,
    absorption_weight,
    cost_weight
):

    total_scores = (
        opening_scores * opening_weight
        + absorption_scores * absorption_weight
        + cost_scores * cost_weight
    )

    return total_scores


# ==========================================
# 5. TITLE AND INTRODUCTION
# ==========================================

st.title(
    "From Product Performance to Personal Choice"
)

st.subheader(
    "Interactive Weighted Scoring & Sensitivity Analysis"
)

st.write(
    "This interactive mathematical model explores "
    "how different user priorities influence "
    "menstrual product rankings."
)

st.write(
    "Adjust the weights assigned to packaging "
    "accessibility, absorption capacity, and "
    "affordability to examine how product "
    "recommendations change."
)

st.divider()

# ==========================================
# 6. PRODUCT PERFORMANCE
# ==========================================

st.header("1. Product Performance")

st.write(
    "The following measurements were provided "
    "from standardized product testing."
)

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)

st.info(
    "Lower opening time indicates easier packaging "
    "access. Higher absorption indicates greater "
    "measured capacity. Lower cost indicates "
    "better affordability."
)

st.divider()

# ==========================================
# 7. INTERACTIVE WEIGHT SLIDERS
# ==========================================

st.header("2. Adjust Your Priorities")

st.write(
    "Move the sliders to decide which "
    "product characteristics matter most to you."
)

opening_weight_percent = st.slider(
    "Packaging Accessibility (%)",
    min_value=0,
    max_value=100,
    value=50,
    step=5
)

absorption_weight_percent = st.slider(
    "Absorption Capacity (%)",
    min_value=0,
    max_value=100 - opening_weight_percent,
    value=min(30, 100 - opening_weight_percent),
    step=5
)

cost_weight_percent = (
    100
    - opening_weight_percent
    - absorption_weight_percent
)

st.markdown(
    f"**Affordability Weight: "
    f"{cost_weight_percent}% (Automatically Calculated)**"
)

col1, col2, col3 = st.columns(3)

col1.metric(
    "Packaging Accessibility",
    f"{opening_weight_percent}%"
)

col2.metric(
    "Absorption Capacity",
    f"{absorption_weight_percent}%"
)

col3.metric(
    "Affordability",
    f"{cost_weight_percent}%"
)

# Convert percentages to decimals

w_opening = opening_weight_percent / 100
w_absorption = absorption_weight_percent / 100
w_cost = cost_weight_percent / 100

# ==========================================
# 8. CALCULATE WEIGHTED SCORES
# ==========================================

scores = calculate_scores(
    w_opening,
    w_absorption,
    w_cost
)

results = pd.DataFrame({
    "Product": short_names,
    "Weighted Score": scores,
    "Color": product_colors
})

results = results.sort_values(
    "Weighted Score",
    ascending=False,
    kind="stable"
).reset_index(drop=True)

st.divider()

# ==========================================
# 9. WEIGHTED SCORING RESULTS
# ==========================================

st.header("3. Weighted Scoring Results")

st.write(
    "Each product receives a score from 0 to 100 "
    "based on the selected priorities."
)

for index, row in results.iterrows():

    st.markdown(
        f"### {index + 1}. {row['Product']}"
    )

    st.progress(
        float(row["Weighted Score"]) / 100
    )

    st.write(
        f"**Score: {row['Weighted Score']:.1f} / 100**"
    )

winner = results.iloc[0]["Product"]

st.success(
    f"Highest-scoring product under these weights: "
    f"{winner}"
)

st.caption(
    "These scores represent relative performance "
    "among the three tested products, not absolute "
    "product quality or a medical recommendation."
)

# ==========================================
# 10. SIMPLE SENSITIVITY ANALYSIS
# ==========================================

st.divider()

st.header("4. Sensitivity Analysis")

st.write(
    "Sensitivity analysis examines whether "
    "product rankings change when user "
    "priorities are different."
)

st.write(
    "Three example scenarios are compared below."
)

# Scenario weights:
# (Packaging, Absorption, Affordability)

scenarios = {
    "Easy to Open": (0.70, 0.20, 0.10),
    "High Absorption": (0.15, 0.70, 0.15),
    "Low Cost": (0.15, 0.15, 0.70)
}

scenario_results = []

for scenario_name, weights in scenarios.items():

    scenario_scores = calculate_scores(
        weights[0],
        weights[1],
        weights[2]
    )

    for i, product in enumerate(short_names):

        scenario_results.append({
            "Scenario": scenario_name,
            "Product": product,
            "Score": scenario_scores[i]
        })

scenario_df = pd.DataFrame(scenario_results)

# ==========================================
# 11. SIMPLE SCENARIO COMPARISON CHART
# ==========================================

fig, ax = plt.subplots(
    figsize=(10, 5.5)
)

scenario_names = list(scenarios.keys())

x = np.arange(len(scenario_names))

for i, product in enumerate(short_names):

    product_data = scenario_df[
        scenario_df["Product"] == product
    ]

    ax.plot(
        x,
        product_data["Score"].values,
        marker="o",
        markersize=9,
        linewidth=2.5,
        color=product_colors[i],
        label=product
    )

ax.set_xticks(x)

ax.set_xticklabels(
    scenario_names,
    fontsize=11
)

ax.set_ylim(0, 105)

ax.set_ylabel(
    "Weighted Score (0–100)",
    fontsize=12
)

ax.set_title(
    "How Product Rankings Change with User Priorities",
    fontsize=15,
    fontweight="bold",
    color=DARK,
    pad=18
)

ax.grid(
    axis="y",
    alpha=0.2
)

ax.legend(
    loc="upper center",
    bbox_to_anchor=(0.5, -0.15),
    ncol=3,
    frameon=False
)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

fig.patch.set_facecolor("white")
ax.set_facecolor("white")

plt.tight_layout()

st.pyplot(fig)

plt.close(fig)

# ==========================================
# 12. SCENARIO RESULTS TABLE
# ==========================================

st.subheader("Scenario Comparison")

comparison = scenario_df.pivot(
    index="Scenario",
    columns="Product",
    values="Score"
)

comparison = comparison.reindex(scenario_names)

st.dataframe(
    comparison.round(1),
    use_container_width=True
)

# ==========================================
# 13. EXPLAIN THE RESULTS
# ==========================================

st.subheader("What Do These Results Mean?")

for scenario_name in scenario_names:

    subset = scenario_df[
        scenario_df["Scenario"] == scenario_name
    ]

    best_score = subset["Score"].max()

    best_products = subset[
        np.isclose(subset["Score"], best_score)
    ]["Product"].tolist()

    st.write(
        f"**{scenario_name}:** "
        f"Highest-scoring product(s): "
        f"{', '.join(best_products)} "
        f"({best_score:.1f}/100)"
    )

st.divider()

# ==========================================
# 14. RESEARCH CONCLUSION
# ==========================================

st.header("5. Research Conclusion")

st.write(
    "The model demonstrates that product rankings "
    "depend on the priorities assigned to "
    "packaging accessibility, absorption capacity, "
    "and affordability."
)

st.write(
    "Rather than identifying one universally "
    "best menstrual product, weighted scoring "
    "can help individuals compare products "
    "according to their own needs."
)

st.write(
    "Future research could include more products, "
    "repeated measurements, and user feedback "
    "to improve the reliability and usefulness "
    "of this decision-support model."
)

st.caption(
    "Project B | Interactive Mathematical "
    "Decision-Support Model"
)

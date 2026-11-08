
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Project B | Interactive Decision Model",
    page_icon="📊",
    layout="wide"
)

BLUE = "#426A82"
TEAL = "#78A8A4"
YELLOW = "#D4B76A"
COLORS = [BLUE, TEAL, YELLOW]

st.markdown("""
<style>
.stApp {background-color: #F8F8F5;}
h1, h2, h3 {color: #426A82;}
div.stButton > button {
    background-color: #426A82;
    color: white;
}
</style>
""", unsafe_allow_html=True)

st.title("From Product Performance to Personal Choice")
st.subheader("Interactive Weighted Scoring & Sensitivity Analysis")

st.info(
    "ILLUSTRATIVE DATA ONLY — "
    "Replace the sample measurements with actual experimental data."
)

st.markdown("""
This interactive model explores how different user priorities
influence menstrual product rankings.

Adjust the weights to explore trade-offs between packaging
accessibility, absorption capacity, and affordability.
""")

# ---------------------------------
# EXPERIMENTAL DATA
# Replace with actual measurements
# ---------------------------------

df = pd.DataFrame({
    "Product": ["Pad A", "Pad B", "Pad C"],
    "Opening Time (s)": [8.0, 5.0, 11.0],
    "Absorption (mL)": [35.0, 28.0, 43.0],
    "Cost per Pad ($)": [0.24, 0.19, 0.31]
})

def normalize(values, higher_better=True):
    values = np.asarray(values, dtype=float)
    low = values.min()
    high = values.max()

    if high == low:
        return np.ones(len(values))

    if higher_better:
        return (values - low) / (high - low)

    return (high - values) / (high - low)

normalized = pd.DataFrame({
    "Product": df["Product"],
    "Accessibility": normalize(df["Opening Time (s)"], False),
    "Absorbency": normalize(df["Absorption (mL)"], True),
    "Affordability": normalize(df["Cost per Pad ($)"], False)
})

st.divider()
st.header("1. Product Performance")

st.dataframe(df, hide_index=True, use_container_width=True)

st.header("2. Adjust Your Priorities")

st.write(
    "Move the sliders to change the importance "
    "of each criterion."
)

w_access = st.slider(
    "Packaging Accessibility (%)",
    min_value=0,
    max_value=100,
    value=50
)

w_absorb = st.slider(
    "Absorption Capacity (%)",
    min_value=0,
    max_value=100 - w_access,
    value=min(30, 100 - w_access)
)

w_afford = 100 - w_access - w_absorb

st.metric("Affordability Weight (Auto-calculated)", f"{w_afford}%")

weights = np.array([
    w_access,
    w_absorb,
    w_afford
]) / 100

st.divider()
st.header("3. Weighted Scoring Results")

criteria = normalized[
    ["Accessibility", "Absorbency", "Affordability"]
].to_numpy()

result = pd.DataFrame({
    "Product": df["Product"],
    "Score": (criteria @ weights) * 100
})

result = result.sort_values(
    "Score", ascending=False
).reset_index(drop=True)

for i, row in result.iterrows():
    st.write(
        f"**{i+1}. {row['Product']} — "
        f"{row['Score']:.1f} / 100**"
    )
    st.progress(float(row["Score"]) / 100)

st.success(
    f"Highest-scoring product under these weights: "
    f"{result.iloc[0]['Product']}"
)

st.caption(
    "This is a model-based ranking, not a universal "
    "recommendation or medical assessment."
)

st.divider()
st.header("4. Sensitivity Analysis")

st.write(
    "This figure shows which product receives the "
    "highest score across different weight combinations."
)

resolution = 101
grid = np.linspace(0, 1, resolution)
winner = np.full((resolution, resolution), np.nan)

for iy, absorb_weight in enumerate(grid):
    for ix, access_weight in enumerate(grid):

        afford_weight = 1 - access_weight - absorb_weight

        if afford_weight < -1e-9:
            continue

        test_weights = np.array([
            access_weight,
            absorb_weight,
            max(0, afford_weight)
        ])

        test_scores = criteria @ test_weights
        winner[iy, ix] = np.argmax(test_scores)

from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch

fig, ax = plt.subplots(figsize=(8, 6))

cmap = ListedColormap(COLORS)
cmap.set_bad("#F8F8F5")

ax.imshow(
    np.ma.masked_invalid(winner),
    origin="lower",
    extent=[0, 1, 0, 1],
    cmap=cmap,
    vmin=-0.5,
    vmax=len(df)-0.5,
    interpolation="nearest",
    aspect="equal"
)

ax.set_xlabel("Accessibility Weight")
ax.set_ylabel("Absorbency Weight")
ax.set_title("Sensitivity Analysis")

legend_items = [
    Patch(
        facecolor=COLORS[i],
        label=df["Product"].iloc[i]
    )
    for i in range(len(df))
]

ax.legend(
    handles=legend_items,
    bbox_to_anchor=(1.35, 1),
    loc="upper right"
)

plt.tight_layout()
st.pyplot(fig)
plt.close(fig)

st.caption(
    "The affordability weight is calculated as "
    "1 minus the other two weights. "
    "Ties are resolved by product order in this demonstration."
)

st.divider()
st.header("5. Research Purpose")

st.write("""
This model illustrates how mathematical decision-making
can support personalized menstrual product selection.

Rather than identifying one universally best product,
the model highlights how rankings may change when
individual priorities differ.
""")

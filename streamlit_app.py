
import streamlit as st
import pandas as pd
import numpy as np

# ==========================================
# PAGE SETTINGS
# ==========================================

st.set_page_config(
    page_title="From Product Performance to Personal Choice",
    page_icon="🌿",
    layout="wide"
)

# ==========================================
# COLORS AND DESIGN
# ==========================================

st.markdown("""
<style>
.stApp {
    background-color: #F8F9F7;
    color: #243746;
}

h1, h2, h3 {
    color: #365F78 !important;
}

[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li {
    color: #243746;
}

[data-testid="stMetricValue"],
[data-testid="stMetricLabel"] {
    color: #243746 !important;
}

.stProgress > div > div > div > div {
    background-color: #78A99F;
}

div[data-testid="stSlider"] label {
    color: #243746 !important;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# REAL EXPERIMENTAL DATA
# ==========================================

df = pd.DataFrame({
    "Product": [
        "Always Infinity FlexFoam Size 2 Super Absorbency 32ct",
        "Always Pocket FlexFoam Size 1 Regular 22ct",
        "CVS Health Overnight Maxi Pads 28ct"
    ],
    "Opening Time (s)": [8.5, 4.2, 7.0],
    "Absorption (mL)": [42, 28, 34],
    "Cost per Pad ($)": [0.31, 0.41, 0.20]
})

short_names = [
    "Always Infinity",
    "Always Pocket",
    "CVS Health Overnight"
]

# ==========================================
# NORMALIZATION FUNCTION
# ==========================================

def normalize(values, higher_is_better=True):

    values = np.array(values, dtype=float)

    minimum = np.min(values)
    maximum = np.max(values)

    if maximum == minimum:
        return np.full(len(values), 100.0)

    if higher_is_better:
        return (
            (values - minimum)
            / (maximum - minimum)
        ) * 100

    return (
        (maximum - values)
        / (maximum - minimum)
    ) * 100


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
# TITLE
# ==========================================

st.title("From Product Performance to Personal Choice")

st.divider()

# ==========================================
# 1. PURPOSE
# ==========================================

st.header("1. Purpose")

st.write(
    "This project aims to help women with different "
    "needs make informed menstrual product choices."
)

st.write(
    "By comparing packaging opening time, "
    "absorption capacity, and cost per pad, "
    "the model allows users to identify products "
    "that best match their individual priorities."
)

st.divider()

# ==========================================
# 2. PRODUCT COMPARISON
# ==========================================

st.header("2. Product Comparison")

st.write(
    "The following table presents experimental "
    "measurements and recorded costs for "
    "three menstrual products."
)

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)

st.caption(
    "Opening time is measured in seconds (s), "
    "absorption capacity in milliliters (mL), "
    "and cost in US dollars per pad."
)

st.divider()

# ==========================================
# 3. WEIGHTED DECISION MODEL
# ==========================================

st.header("3. Weighted Decision Model")

st.write(
    "Different users may value product "
    "characteristics differently. "
    "Adjust the weights below to find "
    "which product best matches your priorities."
)

# Packaging weight

opening_weight = st.slider(
    "Packaging Accessibility (%)",
    min_value=0,
    max_value=100,
    value=50,
    step=5
)

# Absorption weight

absorption_weight = st.slider(
    "Absorption Capacity (%)",
    min_value=0,
    max_value=100 - opening_weight,
    value=min(30, 100 - opening_weight),
    step=5
)

# Cost weight

cost_weight = (
    100 - opening_weight - absorption_weight
)

st.write(
    f"**Affordability Weight: {cost_weight}%** "
    "(Automatically Calculated)"
)

# Convert percentages to decimals

w1 = opening_weight / 100
w2 = absorption_weight / 100
w3 = cost_weight / 100

# Weighted scoring calculation

total_scores = (
    w1 * opening_scores
    + w2 * absorption_scores
    + w3 * cost_scores
)

results = pd.DataFrame({
    "Product": short_names,
    "Score": total_scores
})

results = results.sort_values(
    "Score",
    ascending=False,
    kind="stable"
).reset_index(drop=True)

st.subheader("Your Results")

for i, row in results.iterrows():

    st.write(
        f"**{i + 1}. {row['Product']} "
        f"— {row['Score']:.1f} / 100**"
    )

    st.progress(
        float(row["Score"]) / 100
    )

# Handle ties

best_score = results["Score"].max()

best_products = results.loc[
    np.isclose(results["Score"], best_score),
    "Product"
].tolist()

if len(best_products) == 1:
    st.success(
        "Recommended Product: "
        + best_products[0]
    )
else:
    st.success(
        "Highest-scoring Products (Tie): "
        + ", ".join(best_products)
    )

st.caption(
    "Recommendations are based on the selected "
    "weights and relative performance among "
    "the three tested products."
)

st.divider()

# ==========================================
# 4. MATHEMATICAL FORMULA
# ==========================================

st.header("4. Mathematical Formula")

st.write(
    "The weighted decision model calculates "
    "a total score using the following formula:"
)

st.latex(
    r"S = w_1x_1 + w_2x_2 + w_3x_3"
)

st.markdown("""
Where:

- **S** = Total weighted score
- **x₁** = Normalized packaging accessibility score
- **x₂** = Normalized absorption capacity score
- **x₃** = Normalized affordability score
- **w₁, w₂, w₃** = User-selected weights
""")

st.latex(
    r"w_1+w_2+w_3=1"
)

st.write(
    "Each measurement is normalized to a "
    "score between 0 and 100 so that "
    "different units can be compared."
)

st.write(
    "For absorption capacity, higher values "
    "receive higher scores. For opening time "
    "and cost, lower values receive higher scores."
)

st.subheader("Example Using Your Current Weights")

st.latex(
    rf"S = {w1:.2f}x_1"
    rf" + {w2:.2f}x_2"
    rf" + {w3:.2f}x_3"
)

st.caption(
    "The weights are selected by users. "
    "Scores are calculated using Min-Max "
    "Normalization of the three tested products."
)

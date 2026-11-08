
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch

# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Project B | Personalized Product Selection",
    page_icon="📊",
    layout="wide"
)

# ==========================================
# COLOR PALETTE
# ==========================================

BLUE = "#426A82"
DARK_BLUE = "#243746"
TEAL = "#78A8A4"
YELLOW = "#D4B76A"
BACKGROUND = "#F8F8F5"
LIGHT_TEAL = "#E4EFED"

PRODUCT_COLORS = [BLUE, TEAL, YELLOW]

# ==========================================
# GLOBAL CSS
# ==========================================

st.markdown("""
<style>
.stApp {
    background-color: #F8F8F5;
    color: #243746;
}

.stApp h1,
.stApp h2,
.stApp h3,
.stApp h4 {
    color: #426A82 !important;
}

[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stWidgetLabel"] p {
    color: #243746 !important;
}

[data-testid="stMetricLabel"] p,
[data-testid="stMetricValue"] {
    color: #243746 !important;
}

[data-testid="stSlider"] label {
    color: #243746 !important;
}

[data-testid="stCaptionContainer"] p {
    color: #536773 !important;
}

hr {
    border-color: #B8C9CC;
}

div.stButton > button {
    background-color: #426A82;
    color: #FFFFFF !important;
    border-radius: 8px;
}

/* Custom notice box */
.research-notice {
    background-color: #E4EFED;
    color: #243746 !important;
    padding: 18px 22px;
    border-left: 5px solid #426A82;
    border-radius: 8px;
    font-size: 16px;
    line-height: 1.6;
    margin: 18px 0 24px 0;
}

.research-notice strong {
    color: #243746 !important;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# TITLE
# ==========================================

st.title(
    "From Product Performance to Personal Choice"
)

st.subheader(
    "Interactive Weighted Scoring & Sensitivity Analysis"
)

# FIXED: LIGHT NOTICE WITH DARK TEXT

st.markdown("""
<div class="research-notice">
    <strong>ILLUSTRATIVE DATA ONLY</strong> —
    Replace all sample measurements with actual
    experimental results before research presentation.
</div>
""", unsafe_allow_html=True)

st.write("""
This interactive mathematical model explores how
different user priorities influence menstrual product
rankings.

Adjust the weights assigned to packaging accessibility,
absorption capacity, and affordability to examine
how product recommendations change.
""")

# ==========================================
# SAMPLE DATA
# REPLACE WITH REAL EXPERIMENTAL RESULTS
# ==========================================

df = pd.DataFrame({
    "Product": [
        "Pad A",
        "Pad B",
        "Pad C"
    ],
    "Opening Time (s)": [
        8.0,
        5.0,
        11.0
    ],
    "Absorption (mL)": [
        35.0,
        28.0,
        43.0
    ],
    "Cost per Pad ($)": [
        0.24,
        0.19,
        0.31
    ]
})

# ==========================================
# NORMALIZATION
# ==========================================

def normalize(values, higher_better=True):

    values = np.asarray(
        values,
        dtype=float
    )

    minimum = np.min(values)
    maximum = np.max(values)

    if maximum == minimum:
        return np.ones(len(values))

    if higher_better:
        return (
            (values - minimum)
            / (maximum - minimum)
        )

    return (
        (maximum - values)
        / (maximum - minimum)
    )


normalized = pd.DataFrame({
    "Product": df["Product"],

    "Accessibility": normalize(
        df["Opening Time (s)"],
        higher_better=False
    ),

    "Absorbency": normalize(
        df["Absorption (mL)"],
        higher_better=True
    ),

    "Affordability": normalize(
        df["Cost per Pad ($)"],
        higher_better=False
    )
})

criteria = normalized[
    [
        "Accessibility",
        "Absorbency",
        "Affordability"
    ]
].to_numpy()

# ==========================================
# SECTION 1 — PRODUCT PERFORMANCE
# ==========================================

st.divider()

st.header("1. Product Performance")

st.write(
    "The following measurements represent "
    "three dimensions of menstrual product performance."
)

st.dataframe(
    df,
    hide_index=True,
    use_container_width=True
)

st.caption(
    "Lower opening time and cost are preferred; "
    "higher absorption capacity is preferred."
)

# ==========================================
# SECTION 2 — INTERACTIVE WEIGHTS
# ==========================================

st.divider()

st.header("2. Adjust Your Priorities")

st.write(
    "Move the sliders to explore how different "
    "personal priorities influence product rankings."
)

w_access = st.slider(
    "Packaging Accessibility (%)",
    min_value=0,
    max_value=100,
    value=50,
    step=1
)

w_absorb = st.slider(
    "Absorption Capacity (%)",
    min_value=0,
    max_value=100 - w_access,
    value=min(30, 100 - w_access),
    step=1
)

w_afford = (
    100 - w_access - w_absorb
)

st.metric(
    "Affordability Weight (Auto-calculated)",
    f"{w_afford}%"
)

st.caption(
    "All three weights always sum to 100%."
)

weights = np.array([
    w_access,
    w_absorb,
    w_afford
]) / 100

# ==========================================
# SECTION 3 — WEIGHTED SCORING
# ==========================================

st.divider()

st.header("3. Weighted Scoring Results")

st.latex(
    r"S_i = w_1 A_i + w_2 B_i + w_3 C_i"
)

st.write(
    "Each product receives a normalized score "
    "based on the selected criterion weights."
)

result = pd.DataFrame({
    "Product": df["Product"],
    "Score": (criteria @ weights) * 100
})

result = result.sort_values(
    by="Score",
    ascending=False
).reset_index(drop=True)

for index, row in result.iterrows():

    st.markdown(
        f"**{index + 1}. {row['Product']} "
        f"— {row['Score']:.1f} / 100**"
    )

    st.progress(
        float(row["Score"]) / 100
    )

top_score = result.iloc[0]["Score"]

top_products = result.loc[
    np.isclose(
        result["Score"],
        top_score
    ),
    "Product"
].tolist()

if len(top_products) == 1:

    st.markdown(
        f"""
        <div style="
            background-color: #E4EFED;
            color: #243746;
            padding: 18px 22px;
            border-left: 5px solid #78A8A4;
            border-radius: 8px;
            font-weight: 600;
        ">
            Highest-scoring product under
            these weights: {top_products[0]}
        </div>
        """,
        unsafe_allow_html=True
    )

else:

    st.write(
        "Tied highest-scoring products: "
        + ", ".join(top_products)
    )

st.caption(
    "Model scores reflect the selected weights "
    "and available measurements. They do not "
    "establish a universally best product."
)

# ==========================================
# SECTION 4 — SENSITIVITY ANALYSIS
# ==========================================

st.divider()

st.header("4. Sensitivity Analysis")

st.write("""
Sensitivity analysis examines how the
highest-scoring product changes when
criterion weights vary.
""")

resolution = 101

weight_range = np.linspace(
    0,
    1,
    resolution
)

winner = np.full(
    (resolution, resolution),
    np.nan
)

for y, absorb_weight in enumerate(weight_range):

    for x, access_weight in enumerate(weight_range):

        afford_weight = (
            1 - access_weight - absorb_weight
        )

        if afford_weight < -1e-9:
            continue

        test_weights = np.array([
            access_weight,
            absorb_weight,
            max(0, afford_weight)
        ])

        test_scores = (
            criteria @ test_weights
        )

        best_indices = np.flatnonzero(
            np.isclose(
                test_scores,
                np.max(test_scores)
            )
        )

        if len(best_indices) == 1:
            winner[y, x] = best_indices[0]

# ==========================================
# SENSITIVITY FIGURE
# ==========================================

fig, ax = plt.subplots(
    figsize=(8, 6)
)

fig.patch.set_facecolor(BACKGROUND)
ax.set_facecolor(BACKGROUND)

cmap = ListedColormap(
    PRODUCT_COLORS
)

cmap.set_bad("#ECECE8")

ax.imshow(
    np.ma.masked_invalid(winner),
    origin="lower",
    extent=[0, 1, 0, 1],
    cmap=cmap,
    vmin=-0.5,
    vmax=len(df) - 0.5,
    interpolation="nearest",
    aspect="equal"
)

ax.set_xlabel(
    "Packaging Accessibility Weight",
    color=DARK_BLUE
)

ax.set_ylabel(
    "Absorption Capacity Weight",
    color=DARK_BLUE
)

ax.set_title(
    "Sensitivity Analysis: Highest-Scoring Product",
    color=BLUE,
    fontsize=14,
    fontweight="bold"
)

ax.tick_params(
    colors=DARK_BLUE
)

legend_items = [
    Patch(
        facecolor=PRODUCT_COLORS[i],
        label=df["Product"].iloc[i]
    )
    for i in range(len(df))
]

legend_items.append(
    Patch(
        facecolor="#ECECE8",
        label="Tie / Invalid Weight Combination"
    )
)

ax.legend(
    handles=legend_items,
    bbox_to_anchor=(1.35, 1),
    loc="upper left",
    frameon=False
)

plt.tight_layout()

st.pyplot(fig)

plt.close(fig)

st.caption(
    "Only weight combinations that sum to 100% "
    "are valid. Gray regions represent ties "
    "or invalid combinations."
)

# ==========================================
# SECTION 5 — RESEARCH PURPOSE
# ==========================================

st.divider()

st.header("5. Research Purpose")

st.write("""
This interactive model demonstrates how
mathematical decision-making can support
personalized menstrual product selection.

Rather than identifying one universally
best product, it highlights how product
rankings can change when individual
priorities differ.

The framework integrates normalized
performance measurements, weighted scoring,
and sensitivity analysis to illustrate
the trade-offs involved in product selection.
""")

st.caption(
    "Project B | Interactive Research Demonstration"
)

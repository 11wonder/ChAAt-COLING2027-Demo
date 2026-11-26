# -*- coding: utf-8 -*-
"""English-only demo mode for the COLING 2027 System Demonstrations video."""

import json

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="ChAAt Demo", layout="wide")

DIMENSIONS = {
    "idiom": "Idiom",
    "classical": "Classical Chinese",
    "dialect": "Dialect",
    "slang": "Internet Slang",
    "pragmatics": "Pragmatics & pronunciation",
}
ENGLISH_DIMENSION_LABELS = {
    **DIMENSIONS,
    "成语与熟语": "Idiom",
    "古汉语": "Classical Chinese",
    "方言书面语": "Dialect",
    "网络新词与谐音": "Internet Slang",
    "歧义与语用": "Pragmatics & pronunciation",
}
MODEL_ORDER = [
    "DeepSeek Flash",
    "GPT-5.4",
    "Qwen Max",
    "GLM-4 Plus",
    "Ollama Qwen3.5 4B",
    "GPT-4o mini",
]


@st.cache_data
def load_demo_data():
    details = pd.read_csv(
        "results/noweb_all/core50/paper_details.csv"
    )
    details = details[details["repeat"] == 1].copy()
    details["correct"] = details["correct"].map(
        lambda value: str(value).strip().lower() == "true"
        if isinstance(value, str)
        else bool(value)
    )
    with open(
        "data/questions_final_hard50_core_shuffled.json", encoding="utf-8"
    ) as stream:
        questions = json.load(stream)["questions"]
    summary = pd.read_csv("results/noweb_all/core50/paper_summary.csv")
    return details, questions, summary


def dimension_accuracy(summary):
    table = (
        summary[summary["dimension"] != "overall"]
        .pivot_table(
            index="model",
            columns="dimension_label",
            values="accuracy",
        )
        .reindex(MODEL_ORDER)
    )
    table.columns = [
        ENGLISH_DIMENSION_LABELS.get(column, column)
        for column in table.columns
    ]
    ordered = [
        "Idiom",
        "Classical Chinese",
        "Dialect",
        "Internet Slang",
        "Pragmatics & pronunciation",
    ]
    table = table[[column for column in ordered if column in table.columns]]
    return table


st.markdown(
    """
    <style>
      .block-container {max-width: 1280px; padding-top: 2rem;}
      [data-testid="stMetricValue"] {font-size: 1.7rem;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("ChAAt")
st.subheader(
    "A Chinese-specific Ability Atlas for probing linguistic diversity in LLMs"
)
st.caption(
    "Demo Mode · precomputed results · no API key required · no network search"
)

with st.sidebar:
    st.header("Demo controls")
    if "demo_loaded" not in st.session_state:
        st.session_state.demo_loaded = False
    if st.button(
        "Load six-model results",
        type="primary",
        use_container_width=True,
    ):
        st.session_state.demo_loaded = True
    loaded = st.session_state.demo_loaded
    st.caption(
        "The video demo uses recorded benchmark outputs, so no API credentials "
        "are exposed and no model run is required."
    )
    st.divider()
    st.markdown("**Benchmark**")
    st.write("50 hard items")
    st.write("41 exam-style items")
    st.write("6 open-ended tasks")
    st.write("Five Chinese-internal dimensions")

if not loaded:
    st.info(
        "Click **Load six-model results** to start the demonstration."
    )
    st.markdown(
        """
        **What the demo answers**

        - Which models lose capability on Chinese-specific language?
        - Which linguistic dimensions fail?
        - Which individual items explain the failure?
        """
    )
    st.subheader("Five Chinese-internal dimensions")
    dimensions = st.columns(5)
    labels = [
        ("Idioms", "Conventional meaning and misuse"),
        ("Classical Chinese", "Classical-to-modern sense shifts"),
        ("Dialect", "Cantonese words and aspect markers"),
        ("Internet Slang", "Context-dependent recent usage"),
        (
            "Pragmatics & pronunciation",
            "Ambiguity, honorific direction, and character pronunciation",
        ),
    ]
    for column, (label, description) in zip(dimensions, labels):
        with column:
            st.markdown(f"**{label}**")
            st.caption(description)
    st.stop()

details, questions, summary = load_demo_data()
dim_table = dimension_accuracy(summary)
overall = (
    summary[summary["dimension"] == "overall"]
    .set_index("model")["accuracy"]
    .reindex(MODEL_ORDER)
)

metric_cols = st.columns(4)
metric_cols[0].metric("Hard items", "50")
metric_cols[1].metric("Dimensions", "5")
metric_cols[2].metric("Models", "6")
metric_cols[3].metric("Repeated runs", "3")

overview_tab, error_tab, method_tab = st.tabs(
    ["Capability overview", "Failure explorer", "Benchmark design"]
)

with overview_tab:
    st.subheader("Overall ranking")
    ranking = (
        overall.sort_values(ascending=False)
        .rename("Accuracy")
        .reset_index()
        .rename(columns={"model": "Model"})
    )
    ranking["Accuracy (%)"] = (ranking["Accuracy"] * 100).round(1)
    ranking["Label"] = ranking["Accuracy (%)"].map(lambda x: f"{x:.1f}%")
    st.plotly_chart(
        px.bar(
            ranking,
            x="Model",
            y="Accuracy (%)",
            color="Accuracy (%)",
            color_continuous_scale="Blues",
            range_y=[0, 100],
            text="Label",
        ),
        use_container_width=True,
    )

    left, right = st.columns([1.35, 1])
    with left:
        st.subheader("Capability profile")
        radar = (
            dim_table.rename_axis("Model")
            .reset_index()
            .melt(
                id_vars="Model",
                var_name="Dimension",
                value_name="Accuracy",
            )
        )
        st.plotly_chart(
            px.line_polar(
                radar,
                r="Accuracy",
                theta="Dimension",
                color="Model",
                line_close=True,
                range_r=[0, 1],
            ),
            use_container_width=True,
        )
    with right:
        st.subheader("Dimension heatmap")
        st.plotly_chart(
            px.imshow(
                dim_table,
                text_auto=".0%",
                color_continuous_scale="Blues",
                zmin=0,
                zmax=1,
                aspect="auto",
            ),
            use_container_width=True,
        )
    st.caption(
        "Results are means over three runs at temperature 0. "
        "GPT-4o mini and the local 4B model expose the largest gaps."
    )

with error_tab:
    st.subheader("Inspect item-level failures")
    selected_model = st.selectbox(
        "Model",
        MODEL_ORDER,
        index=MODEL_ORDER.index("GPT-4o mini"),
    )
    available_dims = (
        details[details["model"] == selected_model]["dimension"]
        .drop_duplicates()
        .tolist()
    )
    selected_dim = st.selectbox(
        "Dimension",
        available_dims,
        index=available_dims.index("idiom") if "idiom" in available_dims else 0,
        format_func=lambda value: DIMENSIONS.get(value, value),
    )
    failures = details[
        (details["model"] == selected_model)
        & (details["dimension"] == selected_dim)
        & (~details["correct"])
    ].drop_duplicates("id")
    if failures.empty:
        st.success("This model answered every item in this dimension correctly.")
    else:
        for _, row in failures.iterrows():
            with st.expander(f"{row['id']} · {row['question']}"):
                st.markdown(f"**Expected answer:** `{row['expected']}`")
                st.markdown(f"**Model answer:** `{row['output']}`")
                st.markdown(f"**Why it matters:** {row['explanation']}")
        st.caption(
            "Benchmark content remains in Chinese because it is the artifact "
            "being evaluated. System labels and explanations are in English."
        )

with method_tab:
    st.subheader("Three-tier benchmark")
    st.markdown(
        """
        1. **50 hard items** test five Chinese-internal dimensions with
           source-verified answers.
        2. **41 exam-style items**, mostly from public mock exams and
           exam-preparation material, provide ecological context.
        3. **6 open tasks** evaluate explanation and production rather than
           answer selection.
        """
    )
    st.subheader("Reproducible protocol")
    st.markdown(
        """
        - Exact-match scoring for single- and multi-select items.
        - Separate, balanced answer-position randomization for six- and
          four-option items.
        - Six models, three runs, temperature 0, and no browser or external
          tools.
        - Two raters plus an independent blind third rater for all 36
          open-ended answers.
        - Per-item pass rate and discrimination for capability-gap analysis.
        """
    )

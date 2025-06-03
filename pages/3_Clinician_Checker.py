import streamlit as st
import pandas as pd

st.set_page_config(page_title="Clinician Safety Checker", layout="wide")
st.title("Clinician Safety Checker")

st.markdown("""
Check if a prescribed **drug** has associated **genetic variants** that affect patient safety, efficacy, or dosing.  
Data is sourced from **PharmGKB clinical annotations.**
""")

# --- Load data once ---
@st.cache_data
def load_annotations():
    df = pd.read_csv("data/clinical_annotations.tsv", sep="\t")
    df = df[[
        "Gene",
        "Variant/Haplotypes",
        "Drug(s)",
        "Phenotype Category",
        "Level of Evidence",
        "Clinical Annotation"  # optional
    ]]
    df.columns = [
        "Gene",
        "Variant",
        "Drug",
        "Response",
        "Evidence Level",
        "Note"
    ]
    return df

annotations_df = load_annotations()

# --- Initialize session state ---
if "drug_input" not in st.session_state:
    st.session_state.drug_input = ""
if "matched_df" not in st.session_state:
    st.session_state.matched_df = pd.DataFrame()

# --- Input ---
drug_input = st.text_input("Enter drug name (e.g. clopidogrel, warfarin, abacavir):", value=st.session_state.drug_input)

if st.button("Check Drug Safety"):
    st.session_state.drug_input = drug_input
    matched = annotations_df[annotations_df["Drug"].str.lower().str.contains(drug_input.strip().lower())]
    st.session_state.matched_df = matched

# --- Results and filters ---
matched = st.session_state.matched_df

if not matched.empty:
    with st.expander("🔍 Filter results"):
        pheno_filter = st.multiselect("Phenotype category", matched["Response"].unique(), default=matched["Response"].unique())
        level_filter = st.multiselect("Evidence level", matched["Evidence Level"].unique(), default=matched["Evidence Level"].unique())
        matched = matched[matched["Response"].isin(pheno_filter) & matched["Evidence Level"].isin(level_filter)]

    # --- Summary counts ---
    high_risk = matched[
    (matched["Response"].str.lower().str.contains("toxicity")|
    (matched["Evidence Level"].isin(["1A", "1B"])) 
    ]

    fatal_adr = matched[matched["Response"].str.contains("toxicity|fatal|hypersensitivity", case=False)]
    non_responders = matched[matched["Response"].str.contains("non-response|no response|resistance", case=False)]

    st.markdown("### 🔎 Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("🟥 High-Risk Variants", len(high_risk))
    col2.metric("☠️ Fatal/Toxic Reactions", len(fatal_adr))
    col3.metric("⚠️ Non-Responders", len(non_responders))

    st.success(f"Found {len(matched)} variant annotations for **{drug_input.title()}**")

    # --- Color-coding for clinical relevance ---
    def color_row(row):
        color = ""
        if row["Evidence Level"] in ["1A", "1B"]:
            color = "background-color: #ffcccc"  # light red
        elif "toxicity" in row["Response"].lower():
            color = "background-color: #ffe0b2"  # light orange
        elif "non-response" in row["Response"].lower():
            color = "background-color: #ffffcc"  # light yellow
        return [color] * len(row)

    styled_df = matched.style.apply(color_row, axis=1)

    st.dataframe(styled_df, use_container_width=True)

    st.download_button("📥 Download results as CSV", data=matched.to_csv(index=False), file_name=f"{drug_input}_variant_safety.csv")
else:
    if st.session_state.drug_input:
        st.warning(f"No variant annotations found for '{st.session_state.drug_input}'. Try another drug.")

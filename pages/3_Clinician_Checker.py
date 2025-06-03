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
    ]]
    df.columns = [
        "Gene",
        "Variant",
        "Drug",
        "Response",
        "Evidence Level",
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

    st.success(f"Found {len(matched)} variant annotations.")
    st.dataframe(matched)
    
    with st.expander("Filter results"):
        pheno_filter = st.multiselect("Phenotype category", options=matched["Response"].unique(), default=matched["Response"].unique())
        level_filter = st.multiselect("Evidence level", options=matched["Evidence Level"].unique(), default=matched["Evidence Level"].unique())
        matched = matched[matched["Response"].isin(pheno_filter) & matched["Evidence Level"].isin(level_filter)]


    st.download_button("Download results as CSV", data=matched.to_csv(index=False), file_name=f"{st.session_state.drug_input}_variant_safety.csv")

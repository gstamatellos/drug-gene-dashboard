import streamlit as st
import pandas as pd

st.set_page_config(page_title="Clinician Safety Checker", layout="wide")
st.title("Clinician Safety Checker")

st.markdown("""
Check if a prescribed **drug** has associated **genetic variants** that affect patient safety, efficacy, or dosing.  
Data is sourced from **PharmGKB clinical annotations**
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
        "Phenotype",
        "Evidence Level",
    ]
    return df



annotations_df = load_annotations()

# --- Input ---
drug_input = st.text_input("Enter drug name (e.g. clopidogrel, warfarin, abacavir):").strip().lower()

if st.button("Check Drug Safety") and drug_input:
    matched = annotations_df[annotations_df["Drug"].str.lower().str.contains(drug_input)]

    if matched.empty:
        st.warning(f"No variant annotations found for '{drug_input}'. Try another drug.")
    else:
        # Filters
        with st.expander("Filter results"):
            pheno_filter = st.multiselect("Phenotype category", options=matched["Phenotype"].unique(), default=matched["Phenotype"].unique())
            level_filter = st.multiselect("Evidence level", options=matched["Evidence Level"].unique(), default=matched["Evidence Level"].unique())
            matched = matched[matched["Phenotype"].isin(pheno_filter) & matched["Evidence Level"].isin(level_filter)]

        st.success(f"Found {len(matched)} variant annotations.")
        st.dataframe(matched)

        # Optional: Download
        st.download_button("Download results as CSV", data=matched.to_csv(index=False), file_name=f"{drug_input}_variant_safety.csv")

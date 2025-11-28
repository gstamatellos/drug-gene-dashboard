# Drug_Gene_Interactions.py
import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="Interactions | PharmXplorer", layout="wide")

st.title("Drug ⇄ Gene — Interaction Table")
st.markdown("---")

# --- REQUIREMENTS:
# This page expects Search.py to have stored results in st.session_state:
# - st.session_state["df"] (pandas DataFrame of interactions)
# - st.session_state["mode"] ("Drug" or "Gene")
# - st.session_state["last_searched_drug"] (uppercase) OR st.session_state["last_searched_gene"]
# - st.session_state["valid_search"] (True/False)
# - Optional: st.session_state["results"] (raw API JSON) for deeper details

# --- Guard: require prior search
if "df" not in st.session_state or not st.session_state.get("valid_search", False):
    st.info("🔍 Please perform a search from the **Home** page (Search) first.")
    st.stop()

df = st.session_state["df"]
if df is None or df.empty:
    st.warning("⚠️ The stored search results are empty. Please run a new search from the Home page.")
    st.stop()

mode = st.session_state.get("mode", "Drug")
# Determine searched input (uppercase)
if mode == "Drug":
    input_val = st.session_state.get("last_searched_drug", st.session_state.get("drug_input", "")).upper()
else:
    input_val = st.session_state.get("last_searched_gene", st.session_state.get("gene_input", "")).upper()

# Validate df columns against mode
expected_col = "Gene" if mode == "Drug" else "Drug"
if expected_col not in df.columns:
    st.error(
        f"❌ Inconsistent results: current app mode is **{mode}** but the stored results "
        f"appear to be for **{', '.join(df.columns)}**. Please run a new search from the Home page."
    )
    st.stop()

# Header info
st.info(f"📊 Displaying interaction results for **{input_val}** (mode: **{mode}**)")

# --- Search Summary block ---
st.subheader("Search Summary")
if mode == "Gene":
    top_row = df.sort_values("Score", ascending=False).iloc[0]
    top_drug = top_row.get("Drug", "N/A")
    st.markdown(
        f"**Gene searched**: `{input_val}`  \n"
        f"**Number of interacting drugs**: `{len(df)}`  \n"
        f"**Top scoring drug**: `{top_drug}`  \n\n"
        f"🔗 [DrugBank search for {top_drug}](https://go.drugbank.com/unearth/q?query={top_drug}&searcher=drugs)  \n"
        f"🔗 [PubChem search for {top_drug}](https://pubchem.ncbi.nlm.nih.gov/#query={top_drug})"
    )
else:
    top_row = df.sort_values("Score", ascending=False).iloc[0]
    top_gene = top_row.get("Gene", "N/A")
    st.markdown(
        f"**Drug searched**: `{input_val}`  \n"
        f"**Number of interacting genes**: `{len(df)}`  \n"
        f"**Top scoring gene**: `{top_gene}`  \n\n"
        f"🔗 [GeneCards for {top_gene}](https://www.genecards.org/cgi-bin/carddisp.pl?gene={top_gene})  \n"
        f"🔗 [NCBI Gene search for {top_gene}](https://www.ncbi.nlm.nih.gov/gene/?term={top_gene})"
    )

st.markdown("---")

# --- Full Interaction Table ---
st.subheader("Full Interaction Table")
st.dataframe(df, use_container_width=True)

# Download interactions CSV
csv_buf = df.to_csv(index=False)
st.download_button("📥 Download interactions as CSV", csv_buf, file_name=f"{input_val}_interactions.csv", mime="text/csv")

# --- Pharmacogenomic annotations (ClinPGx) ---
# Load ClinPGx file (TSV) only when needed; tolerant to missing file
try:
    pharm_df = pd.read_csv("data/clinical_annotations.tsv", sep="\t", dtype=str)
except FileNotFoundError:
    pharm_df = None
    st.info("Pharmacogenomic annotations file not found at `data/clinical_annotations.tsv`.")

if pharm_df is not None:
    # Normalize column names if necessary
    # Expectation: columns include "Gene", "Variant/Haplotypes", "Drug(s)", "Phenotype Category", "Level of Evidence", "Clinical Annotation"
    # Make uppercase copies for reliable matching
    pharm_df_cols = set(pharm_df.columns.str.strip())
    expected_cols = {"Gene", "Variant/Haplotypes", "Drug(s)", "Phenotype Category", "Level of Evidence", "Clinical Annotation"}
    if expected_cols.issubset(pharm_df_cols):
        # If mode == Drug: find rows where Drug(s) contains input_val (case-insensitive)
        if mode == "Drug":
            # Some Drug(s) entries might be comma-separated lists; use contains
            mask = pharm_df["Drug(s)"].astype(str).str.upper().str.contains(input_val.upper(), na=False)
            pharm_subset = pharm_df[mask].copy()
        else:
            # Gene mode: filter by Gene exact match (case-insensitive) or contains
            mask = pharm_df["Gene"].astype(str).str.upper().str.contains(input_val.upper(), na=False)
            pharm_subset = pharm_df[mask].copy()
        
        if not pharm_subset.empty:
            st.markdown("---")
            st.subheader(f"Pharmacogenomic Variant Annotations for `{input_val}`")
            st.markdown(
                "This table shows ClinPGx/PharmGKB-derived clinical annotations relevant to the searched term. "
                "Use Clinician Safety Checker for clinical summaries and gene-panel recommendations."
            )

            # Keep columns consistent with earlier page expectations; rename for readability
            display_cols = ["Gene", "Variant/Haplotypes", "Phenotype Category", "Level of Evidence", "Clinical Annotation", "Drug(s)"]
            available_display_cols = [c for c in display_cols if c in pharm_subset.columns]
            pharm_display = pharm_subset[available_display_cols].reset_index(drop=True)

            st.dataframe(pharm_display, use_container_width=True)

            # store subset in session_state for Visualizations or Clinician page if needed
            st.session_state["pharm_subset"] = pharm_subset.reset_index(drop=True)

            # Download button for pharm subset
            pharm_csv = pharm_display.to_csv(index=False)
            st.download_button(
                "📥 Download ClinPGx subset (CSV)",
                pharm_csv,
                file_name=f"{input_val}_clinpgx_subset.csv",
                mime="text/csv"
            )
        else:
            st.info(f"No pharmacogenomic variant annotations found for **{input_val}** in ClinPGx dataset.")
    else:
        st.warning("Pharmacogenomic file found but expected columns are missing. Skipping pharm annotations display.")
else:
    # pharm_df is None already reported
    pass

st.markdown("---")
st.info("Tip: Use the **Home** page to run a new search. Use **Visualizations** for plots based on the stored results.")

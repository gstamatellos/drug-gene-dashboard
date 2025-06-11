import streamlit as st
import pandas as pd

st.title("Interaction Table")
st.markdown("---")

# Check if df is available in session_state
if "df" not in st.session_state or not st.session_state.get("valid_search", False):
    st.info("🔍 Please perform a search from the Home page first.")
    st.stop()

df = st.session_state["df"]
if df.empty:
    st.warning("⚠️ No interactions found.")
    st.stop()

mode = st.session_state["mode"]
input_val = st.session_state["gene_input"] if mode == "Gene" else st.session_state["drug_input"]

# Ensure mode and df structure match
expected_col = "Drug" if mode == "Gene" else "Gene"
if expected_col not in df.columns:
    st.error(f"❌ You are currently in {mode} mode, but the last results are from {expected_col} search. Please go back and perform a new search.")
    st.stop()

# Show search summary
st.subheader("Search Summary")

if mode == "Gene":
    top_drug = df.sort_values("Score", ascending=False).iloc[0]["Drug"]
    st.markdown(f"""
    **Gene Searched**: `{input_val}`   
    **Number of interacting drugs**: `{len(df)}`  
    **Top scoring drug**: `{top_drug}`  
    🔗 [DrugBank](https://go.drugbank.com/unearth/q?query={top_drug}&searcher=drugs)    
    🔗 [PubChem](https://pubchem.ncbi.nlm.nih.gov/#query={top_drug})

    """)
else:
    top_gene = df.sort_values("Score", ascending=False).iloc[0]["Gene"]
    st.markdown(f"""
    **Drug Searched**: `{input_val}`  
    **Number of interacting genes**: `{len(df)}`  
    **Top scoring gene**: `{top_gene}`  
    🔗 [GeneCards](https://www.genecards.org/cgi-bin/carddisp.pl?gene={top_gene})  
    🔗 [NCBI](https://www.ncbi.nlm.nih.gov/gene/?term={top_gene})
    """)


# Spacer
st.markdown("---")
st.subheader("Full Interaction Table")

# Show DataFrame
st.dataframe(df, use_container_width=True)

# Download button
st.download_button("📥 Download as CSV", df.to_csv(index=False), file_name="interaction_data.csv")


pharm_df = pd.read_csv("data/clinical_annotations.tsv", sep="\t")

drug_name = st.session_state["drug_input"] if st.session_state["mode"] == "Drug" else None

if drug_name:
    # Spacer
    st.markdown("---")
    pharm_subset = pharm_df[pharm_df["Drug(s)"].str.upper() == drug_name.upper()]
    pharm_subset_index = pharm_subset.reset_index(drop = True)

    if not pharm_subset.empty:
        st.subheader(f"Pharmacogenomic Variants for {drug_name}")
        st.session_state["pharm_subset_index"] = pharm_subset_index
        
        st.markdown("""
        This table presents pharmacogenomic variant-drug associations along with clinical annotations to support personalized medicine applications. For more detailed info try searching in the **Clinician Safety Checker** section. Visuals are provided in **Visualizations**.
        """)

        with st.expander("About these results"):
            
            st.markdown("""
            - **Phenotype Category**: Type of drug response or outcome associated with the variant (e.g., toxicity, efficacy, dosage, metabolism/PK)
            - **Level of Evidence**: Graded from 1A (highest) to 4, indicating the strength of clinical support based on PharmGKB guidelines.  
                [More details at PharmGKB](https://www.pharmgkb.org/page/clinAnnLevels)
            - **Clinical Annotation**: Description of observed phenotypes linked to the variant-drug combination, including disease associations or effects on drug response
            """)

        st.dataframe(pharm_subset_index[[
            "Gene", "Variant/Haplotypes", "Phenotype Category", "Level of Evidence", "Clinical Annotation"
        ]])

# Download button
        st.download_button(
        label="📥 Download as TSV",
        data=pharm_subset_index.to_csv(index=False, sep='\t'),
        file_name= "clinical_annotations.tsv",
        mime="text/tab-separated-values"
    )

    else:
        st.info(f"No variant annotations found in PharmGKB for **{drug_name}**.")




        

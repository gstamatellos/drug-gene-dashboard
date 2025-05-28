import streamlit as st
import pandas as pd

st.title("📋 Interaction Table")
st.markdown("---")

# Check if df is available in session_state
if "df" not in st.session_state:
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
    🔗 [GeneCards](https://www.genecards.org/cgi-bin/carddisp.pl?gene={input_val})  
    🔗 [NCBI](https://www.ncbi.nlm.nih.gov/gene/?term={input_val})
    """)
else:
    top_gene = df.sort_values("Score", ascending=False).iloc[0]["Gene"]
    st.markdown(f"""
    **Drug Searched**: `{input_val}`  
    **Number of interacting genes**: `{len(df)}`  
    **Top scoring gene**: `{top_gene}`  
    🔗 [DrugBank](https://go.drugbank.com/unearth/q?query={input_val}&searcher=drugs)  
    🔗 [PubChem](https://pubchem.ncbi.nlm.nih.gov/#query={input_val})
    """)

# Spacer
st.markdown("---")
st.subheader("Full Interaction Table")

# Show DataFrame
st.dataframe(df, use_container_width=True)

# Download button
st.download_button("📥 Download as CSV", df.to_csv(index=False), file_name="interaction_data.csv")

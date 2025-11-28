# Drug_Gene_Interactions.py
import streamlit as st
import pandas as pd
import requests
import json
import time

st.set_page_config(page_title="Interactions | PharmXplorer", layout="wide")
st.title("Drug ⇄ Gene — Interaction Table")
st.markdown("---")

# -----------------------
# Session state defaults
# -----------------------
if "mode" not in st.session_state:
    st.session_state["mode"] = "Drug"
if "drug_input" not in st.session_state:
    st.session_state["drug_input"] = ""
if "gene_input" not in st.session_state:
    st.session_state["gene_input"] = ""
if "last_searched_drug" not in st.session_state:
    st.session_state["last_searched_drug"] = ""
if "last_searched_gene" not in st.session_state:
    st.session_state["last_searched_gene"] = ""
if "searched" not in st.session_state:
    st.session_state["searched"] = False
if "valid_search" not in st.session_state:
    st.session_state["valid_search"] = False
if "df" not in st.session_state:
    st.session_state["df"] = None
if "results" not in st.session_state:
    st.session_state["results"] = None

# -----------------------
# Search UI (on this page)
# -----------------------
st.subheader("Search (DGIdb)")
prev_mode = st.session_state.get("mode", "Drug")
mode = st.radio(
    "Search mode:",
    ["Drug", "Gene"],
    index=0 if prev_mode == "Drug" else 1,
    horizontal=True
)
if mode != prev_mode:
    # reset inputs when mode changes
    st.session_state["drug_input"] = ""
    st.session_state["gene_input"] = ""
    st.session_state["searched"] = False
st.session_state["mode"] = mode

# Text input (preserve case), but we'll uppercase for query
if mode == "Drug":
    input_val = st.text_input("Type drug name:", value=st.session_state["drug_input"], key="dg_drug_input").strip()
    # update session-state copy (not uppercasing here)
    st.session_state["drug_input"] = input_val
else:
    input_val = st.text_input("Type gene name:", value=st.session_state["gene_input"], key="dg_gene_input").strip()
    st.session_state["gene_input"] = input_val

# If user edits input, reset searched flag so new search happens reliably
if mode == "Drug":
    if input_val != st.session_state.get("last_searched_drug", "").lower() and not input_val == "":
        # the last_searched_drug is stored uppercase; compare lower() to be safe
        st.session_state["searched"] = False
else:
    if input_val != st.session_state.get("last_searched_gene", "").lower() and not input_val == "":
        st.session_state["searched"] = False

search_btn = st.button("Search")

# Perform search when clicked
if search_btn:
    if not input_val:
        st.warning("⚠️ Please enter a drug or gene name to search.")
    else:
        input_val_upper = input_val.upper()
        # Save last searched
        if mode == "Drug":
            st.session_state["last_searched_drug"] = input_val_upper
        else:
            st.session_state["last_searched_gene"] = input_val_upper
        st.session_state["searched"] = True

# If search has been triggered (either now or from Search.py), run/ensure results are present
if st.session_state.get("searched", False):
    # Prefer the uppercase last_searched_* stored in session_state if present
    if mode == "Drug":
        search_term_upper = st.session_state.get("last_searched_drug", "").upper()
    else:
        search_term_upper = st.session_state.get("last_searched_gene", "").upper()

    if not search_term_upper:
        st.info("🔍 No search term available. Please enter a term and press Search.")
        st.stop()

    # Display progress bar & message
    st.info(f"⏳ Searching for interactions for **{search_term_upper}**...")
    progress = st.progress(0)
    for i in range(1, 101):
        progress.progress(i)
        time.sleep(0.004)

    # Build GraphQL query and call DGIdb
    url = "https://dgidb.org/api/graphql"
    safe_name = json.dumps(search_term_upper)

    if mode == "Drug":
        query = f"""
        {{
          drugs(names: [{safe_name}]) {{
            nodes {{
              name
              interactions {{
                gene {{
                  name
                  longName
                }}
                interactionScore
              }}
            }}
          }}
        }}
        """
    else:
        query = f"""
        {{
          genes(names: [{safe_name}]) {{
            nodes {{
              name
              interactions {{
                drug {{
                  name
                  conceptId
                }}
                interactionScore
                interactionTypes {{
                   type
                }}
              }}
            }}
          }}
        }}
        """

    try:
        response = requests.post(url, json={"query": query}, timeout=30)
        if response.status_code != 200:
            st.session_state["valid_search"] = False
            st.error(f"❌ API request failed (status {response.status_code}).")
        else:
            results = response.json()
            st.session_state["results"] = results
            interactions = []

            if mode == "Drug":
                nodes = results.get("data", {}).get("drugs", {}).get("nodes", [])
                # filter exact name match (case-insensitive)
                exact_nodes = [n for n in nodes if n.get("name", "").upper() == search_term_upper]
                if not exact_nodes:
                    # try contains fallback
                    exact_nodes = nodes
                for node in exact_nodes:
                    for inter in node.get("interactions", []):
                        gene = inter.get("gene", {}) or {}
                        interactions.append({
                            "Gene": gene.get("name", "N/A"),
                            "Description": gene.get("longName", "N/A"),
                            "Score": inter.get("interactionScore", 0)
                        })
            else:
                nodes = results.get("data", {}).get("genes", {}).get("nodes", [])
                exact_nodes = [n for n in nodes if n.get("name", "").upper() == search_term_upper]
                if not exact_nodes:
                    exact_nodes = nodes
                for node in exact_nodes:
                    for inter in node.get("interactions", []):
                        drug = inter.get("drug", {}) or {}
                        interactions.append({
                            "Drug": drug.get("name", "N/A"),
                            "ID": drug.get("conceptId", "N/A"),
                            "Score": inter.get("interactionScore", 0)
                        })

            if interactions:
                df = pd.DataFrame(interactions)
                st.session_state["df"] = df
                st.session_state["valid_search"] = True
                st.success(f"✅ Search completed for **{search_term_upper}**.")
            else:
                st.session_state["df"] = pd.DataFrame()
                st.session_state["valid_search"] = False
                st.warning(f"⚠️ No interactions found for **{search_term_upper}**.")
    except requests.exceptions.RequestException as e:
        st.session_state["valid_search"] = False
        st.error(f"❌ Request error: {e}")

# -----------------------
# Guard: require results
# -----------------------
if "df" not in st.session_state or not st.session_state.get("valid_search", False):
    st.info("🔍 Please perform a search above (this page) or from the Home page first.")
    st.stop()

df = st.session_state["df"]
if df is None or df.empty:
    st.warning("⚠️ The stored search results are empty. Please run a new search.")
    st.stop()

# -----------------------
# Display header & summary
# -----------------------
mode = st.session_state.get("mode", "Drug")
if mode == "Drug":
    input_val_display = st.session_state.get("last_searched_drug", st.session_state.get("drug_input", "")).upper()
else:
    input_val_display = st.session_state.get("last_searched_gene", st.session_state.get("gene_input", "")).upper()

st.info(f"📊 Displaying interaction results for **{input_val_display}** (mode: **{mode}**)")

st.subheader("Search Summary")
if mode == "Gene":
    top_row = df.sort_values("Score", ascending=False).iloc[0]
    top_drug = top_row.get("Drug", "N/A")
    st.markdown(
        f"**Gene searched**: `{input_val_display}`  \n"
        f"**Number of interacting drugs**: `{len(df)}`  \n"
        f"**Top scoring drug**: `{top_drug}`  \n\n"
        f"🔗 [DrugBank search for {top_drug}](https://go.drugbank.com/unearth/q?query={top_drug}&searcher=drugs)  \n"
        f"🔗 [PubChem search for {top_drug}](https://pubchem.ncbi.nlm.nih.gov/#query={top_drug})"
    )
else:
    top_row = df.sort_values("Score", ascending=False).iloc[0]
    top_gene = top_row.get("Gene", "N/A")
    st.markdown(
        f"**Drug searched**: `{input_val_display}`  \n"
        f"**Number of interacting genes**: `{len(df)}`  \n"
        f"**Top scoring gene**: `{top_gene}`  \n\n"
        f"🔗 [GeneCards for {top_gene}](https://www.genecards.org/cgi-bin/carddisp.pl?gene={top_gene})  \n"
        f"🔗 [NCBI Gene search for {top_gene}](https://www.ncbi.nlm.nih.gov/gene/?term={top_gene})"
    )

st.markdown("---")

# -----------------------
# Full Interaction Table
# -----------------------
st.subheader("Full Interaction Table")
st.dataframe(df, use_container_width=True)

csv_buf = df.to_csv(index=False)
st.download_button("📥 Download interactions as CSV", csv_buf, file_name=f"{input_val_display}_interactions.csv", mime="text/csv")

# -----------------------
# Pharmacogenomic annotations (ClinPGx)
# -----------------------
# Attempt to load ClinPGx file if available
try:
    pharm_df = pd.read_csv("data/clinical_annotations.tsv", sep="\t", dtype=str)
except FileNotFoundError:
    pharm_df = None

if pharm_df is not None:
    # Ensure expected columns exist
    pharm_cols = set([c.strip() for c in pharm_df.columns])
    expected = {"Gene", "Variant/Haplotypes", "Drug(s)", "Phenotype Category", "Level of Evidence", "Clinical Annotation"}
    if expected.issubset(pharm_cols):
        # Filter pharm annotations depending on mode
        if mode == "Drug":
            mask = pharm_df["Drug(s)"].astype(str).str.upper().str.contains(input_val_display, na=False)
            pharm_subset = pharm_df[mask].copy()
        else:
            mask = pharm_df["Gene"].astype(str).str.upper().str.contains(input_val_display, na=False)
            pharm_subset = pharm_df[mask].copy()

        if not pharm_subset.empty:
            st.markdown("---")
            st.subheader(f"Pharmacogenomic Variant Annotations for `{input_val_display}`")
            st.markdown(
                "This table shows ClinPGx/PharmGKB-derived clinical annotations relevant to the searched term."
                " Use the Clinician Safety Checker for clinical summaries and gene-panel recommendations."
            )

            display_cols = ["Gene", "Variant/Haplotypes", "Phenotype Category", "Level of Evidence", "Clinical Annotation", "Drug(s)"]
            available_display_cols = [c for c in display_cols if c in pharm_subset.columns]
            pharm_display = pharm_subset[available_display_cols].reset_index(drop=True)

            st.dataframe(pharm_display, use_container_width=True)
            st.session_state["pharm_subset"] = pharm_subset.reset_index(drop=True)

            pharm_csv = pharm_display.to_csv(index=False)
            st.download_button("📥 Download ClinPGx subset (CSV)", pharm_csv, file_name=f"{input_val_display}_clinpgx_subset.csv", mime="text/csv")
        else:
            st.info(f"No pharmacogenomic variant annotations found for **{input_val_display}** in ClinPGx dataset.")
    else:
        st.warning("Pharmacogenomic file found but expected columns are missing. Skipping pharm annotations display.")
else:
    st.info("Pharmacogenomic annotations file not found at `data/clinical_annotations.tsv`.")

st.markdown("---")
st.info("Tip: Use the Home/Search page to run another search.")


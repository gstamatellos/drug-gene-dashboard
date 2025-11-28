import streamlit as st
import requests
import pandas as pd
import json
import time

# --- Browser tab title and full-width layout ---
st.set_page_config(page_title="Home", layout="wide")
st.image("data/home_image.png")
st.title("Welcome to Drug ⇄ Gene Interaction Explorer")

# --- Intro text ---
st.markdown("""
This app allows you to search **drug–gene interactions** from the [DGIdb](https://dgidb.org) API 
and **pharmacogenomic variant-drug annotations** data from [ClinPGx](https://www.clinpgx.org/).

After searching, use the sidebar to explore:
- **Results Tables** 
- **Interaction - Annotation Visuals**  
""")

st.markdown("---")
# --- Clinician Safety Checker button in main page ---
st.markdown("**NEW: Clinician Safety Checker**")
if st.button("Visit page"):
    st.session_state["goto_clinician_checker"] = True
    st.info("Please click the sidebar page **Clinician Safety Checker** to continue!")

st.markdown("---")

# --- Initialize session state ---
if "mode" not in st.session_state:
    st.session_state["mode"] = "Drug"
if "gene_input" not in st.session_state:
    st.session_state["gene_input"] = ""
if "drug_input" not in st.session_state:
    st.session_state["drug_input"] = ""
if "searched" not in st.session_state:
    st.session_state["searched"] = False
if "valid_search" not in st.session_state:
    st.session_state["valid_search"] = False

# --- Detect mode change and reset input ---
prev_mode = st.session_state.get("mode", "Drug")
mode = st.radio(
    "Select search mode:",
    ["Drug", "Gene"],
    index=0 if prev_mode == "Drug" else 1,
    horizontal=True
)
if mode != prev_mode:
    st.session_state["gene_input"] = ""
    st.session_state["drug_input"] = ""
    st.session_state["searched"] = False
st.session_state["mode"] = mode

# --- Input based on mode ---
if mode == "Drug":
    input_val = st.text_input("Type Drug name:", value=st.session_state["drug_input"]).strip()
else:
    input_val = st.text_input("Type Gene name:", value=st.session_state["gene_input"]).strip()

# --- Clear searched flag if input changes ---
if (mode == "Drug" and input_val != st.session_state["drug_input"]) or \
   (mode == "Gene" and input_val != st.session_state["gene_input"]):
    st.session_state["searched"] = False

# --- Search button ---
search_triggered = st.button("Search")

if search_triggered and input_val:
    # --- Convert to uppercase for API ---
    input_val_upper = input_val.upper()

    # --- Save input in session_state ---
    if mode == "Drug":
        st.session_state["drug_input"] = input_val_upper
    else:
        st.session_state["gene_input"] = input_val_upper

    st.session_state["searched"] = True

# --- Only trigger API search in background, no table preview on home page ---
if st.session_state.get("searched", False):
    input_val_upper = st.session_state["drug_input"] if mode == "Drug" else st.session_state["gene_input"]

    st.info(f"⏳ Searching for interactions for **{input_val_upper}**...")
    progress_bar = st.progress(0)
    for i in range(1, 101):
        progress_bar.progress(i)
        time.sleep(0.005)  # simulate progress for UX

    url = "https://dgidb.org/api/graphql"
    safe_name = json.dumps(input_val_upper)  # GraphQL-safe

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
        response = requests.post(url, json={"query": query})
        interactions = []
        if response.status_code == 200:
            results = response.json()
            if mode == "Drug":
                nodes = results.get("data", {}).get("drugs", {}).get("nodes", [])
                exact_nodes = [n for n in nodes if n.get("name", "").upper() == input_val_upper]
                for node in exact_nodes:
                    for interaction in node.get("interactions", []):
                        gene = interaction["gene"]
                        interactions.append({
                            "Gene": gene.get("name", "N/A"),
                            "Description": gene.get("longName", "N/A"),
                            "Score": interaction.get("interactionScore", 0)
                        })
            else:
                nodes = results.get("data", {}).get("genes", {}).get("nodes", [])
                exact_nodes = [n for n in nodes if n.get("name", "").upper() == input_val_upper]
                for node in exact_nodes:
                    for interaction in node.get("interactions", []):
                        drug = interaction["drug"]
                        interactions.append({
                            "Drug": drug.get("name", "N/A"),
                            "ID": drug.get("conceptId", "N/A"),
                            "Score": interaction.get("interactionScore", 0)
                        })
            # Store dataframe in session_state but do NOT display table on homepage
            if interactions:
                st.session_state["df"] = pd.DataFrame(interactions)
                st.session_state["valid_search"] = True
                st.success("✅ Search completed! Use the sidebar to explore results.")
            else:
                st.session_state["valid_search"] = False
                st.warning("⚠️ No interactions found.")
        else:
            st.session_state["valid_search"] = False
            st.error(f"❌ API request failed with status code {response.status_code}")
    except Exception as e:
        st.session_state["valid_search"] = False
        st.error(f"❌ API request error: {e}")













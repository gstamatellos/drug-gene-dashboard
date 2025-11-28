import streamlit as st
import requests
import pandas as pd
import json

# --- Page config ---
st.set_page_config(page_title="PharmXplorer", layout="wide")
st.image("data/home_image.png")
st.title("Welcome to Drug ⇄ Gene Interaction Explorer")

# --- Sidebar: Navigation ---
with st.sidebar:
    st.header("Navigation")
    st.markdown("🏠 **Home**")  # Home label

    # Button to go to Clinician Safety Checker
    if st.button("🩺 Go to Clinician Safety Checker"):
        # Multipage app: redirect to Clinician Checker
        st.experimental_set_query_params(page="Clinician_Checker")

# --- Intro text ---
st.markdown("""
This app allows you to search **drug–gene interactions** from the [DGIdb](https://dgidb.org) API and **pharmacogenomic variant-drug annotations** data from [ClinPGx](https://www.clinpgx.org/).

After searching, use the sidebar to explore:
- **Results Tables** 
- **Interaction - Annotation Visuals**  

**New feature: Clinician Safety Checker**  
Use the sidebar button 🩺 to navigate there directly!
""")

# ------------------------------
# --- Session State Initialization ---
# ------------------------------
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
st.session_state["mode"] = mode

# --- Input based on mode ---
input_val = ""
if mode == "Drug":
    input_val = st.text_input("Type Drug name:", value=st.session_state["drug_input"]).strip()
else:
    input_val = st.text_input("Type Gene name:", value=st.session_state["gene_input"]).strip()

# --- Search button ---
search_triggered = st.button("Search")

if search_triggered:
    input_val = input_val.upper()  # standardize
    # Save input in session_state
    if mode == "Drug":
        st.session_state["drug_input"] = input_val
    else:
        st.session_state["gene_input"] = input_val
    st.session_state["searched"] = True

# --- Only search if triggered ---
if st.session_state["searched"] and input_val:
    # --- API setup ---
    url = "https://dgidb.org/api/graphql"
    safe_name = json.dumps(input_val)

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

    # Send request
    response = requests.post(url, json={"query": query})
    interactions = []

    if response.status_code == 200:
        results = response.json()
        if mode == "Drug":
            nodes = results.get("data", {}).get("drugs", {}).get("nodes", [])
            exact_nodes = [n for n in nodes if n.get("name", "").upper() == input_val]
            if exact_nodes:
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
            exact_nodes = [n for n in nodes if n.get("name", "").upper() == input_val]
            if exact_nodes:
                for node in exact_nodes:
                    for interaction in node.get("interactions", []):
                        drug = interaction["drug"]
                        interactions.append({
                            "Drug": drug.get("name", "N/A"),
                            "ID": drug.get("conceptId", "N/A"),
                            "Score": interaction.get("interactionScore", 0)
                        })
        if interactions:
            df = pd.DataFrame(interactions)
            if df.empty:
                st.session_state["valid_search"] = False
            else:
                st.session_state["df"] = df
                st.session_state["valid_search"] = True
                st.success("✅ Interactions retrieved! Use the sidebar to explore results.")
        else:
            st.session_state["valid_search"] = False
    else:
        st.error(f"❌ API request failed with status code {response.status_code}")
        st.session_state["valid_search"] = False

# --- Optional: show a small table preview if available ---
if st.session_state.get("valid_search", False):
    st.markdown("---")
    st.markdown(f"### Results Preview ({mode} search)")
    st.dataframe(st.session_state["df"].head(10), use_container_width=True)





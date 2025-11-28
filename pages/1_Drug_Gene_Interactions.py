import streamlit as st
import requests
import pandas as pd
import json
import time

st.title("Drug - Gene Interactions")
st.markdown("---")

# --- Initialize session state ---
if "mode" not in st.session_state:
    st.session_state["mode"] = "Drug"
if "gene_input" not in st.session_state:
    st.session_state["gene_input"] = ""
if "drug_input" not in st.session_state:
    st.session_state["drug_input"] = ""
if "last_searched_drug" not in st.session_state:
    st.session_state["last_searched_drug"] = ""
if "last_searched_gene" not in st.session_state:
    st.session_state["last_searched_gene"] = ""
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

# --- Input based on mode (keep user's original case) ---
if mode == "Drug":
    input_val = st.text_input("Type Drug name:", value=st.session_state["drug_input"], key="drug_text_input").strip()
    st.session_state["drug_input"] = input_val
else:
    input_val = st.text_input("Type Gene name:", value=st.session_state["gene_input"], key="gene_text_input").strip()
    st.session_state["gene_input"] = input_val

# --- Search button ---
search_triggered = st.button("Search")

# --- Perform search when button is clicked ---
if search_triggered and input_val:
    # Convert to uppercase for API search
    input_val_upper = input_val.upper()
    
    # Store what we searched for
    if mode == "Drug":
        st.session_state["last_searched_drug"] = input_val_upper
    else:
        st.session_state["last_searched_gene"] = input_val_upper
    
    st.session_state["searched"] = True
    
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
                st.session_state["results"] = results  # Store full results for interaction types
                st.success(f"✅ Search completed for **{input_val_upper}**! Use the sidebar to explore results.")
            else:
                st.session_state["valid_search"] = False
                st.warning(f"⚠️ No interactions found for **{input_val_upper}**.")
        else:
            st.session_state["valid_search"] = False
            st.error(f"❌ API request failed with status code {response.status_code}")
    except Exception as e:
        st.session_state["valid_search"] = False
        st.error(f"❌ API request error: {e}")

elif search_triggered and not input_val:
    st.warning("⚠️ Please enter a drug or gene name to search.")











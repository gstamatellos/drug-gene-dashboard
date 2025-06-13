import streamlit as st
import requests
import pandas as pd
import json

#--- browser tab title and layout full width
st.set_page_config(page_title="PharmXplorer", layout="wide")
st.image("data/home_image.png")
st.title("Welcome to Drug ⇄ Gene Interaction Explorer")

st.markdown("""
This app allows you to search **drug–gene interactions** from the [DGIdb](https://dgidb.org) API and **pharmacogenomic variant-drug annotations** data from [PharmGKB](https://www.pharmgkb.org/).

After searching, use the sidebar to explore:
- **Results Tables** 
- **Interaction - Annotation Visuals**  

**New feature: Clinician Safety Checker**  
Navigate in the sidebar and take a look!
""")

# --- Initialize session state for inputs
if "mode" not in st.session_state:
    st.session_state["mode"] = "Drug"
    
# --- store the last typed name (avoids repeated searches)
if "gene_input" not in st.session_state:
    st.session_state["gene_input"] = ""
if "drug_input" not in st.session_state:
    st.session_state["drug_input"] = ""

# --- flags whether a search has been performed yet
if "searched" not in st.session_state:
    st.session_state["searched"] = False

st.markdown("---")

# --- Mode select ---
mode = st.radio("Select search mode:", ["Drug", "Gene"], index=0 if st.session_state["mode"] == "Drug" else 1, horizontal=True)
st.session_state["mode"] = mode

# --- Input based on mode ---
# --- .strip() removes accidental spaces
if mode == "Drug":
    input_val = st.text_input("Type Drug name:", value=st.session_state["drug_input"]).strip()
else:
    input_val = st.text_input("Type Gene name:", value=st.session_state["gene_input"]).strip()

# --- Search button ---
search_triggered = st.button("🔍 Search Interactions")

# --- If button is clicked, search
if search_triggered:
    # --- .upper() standardizes input (DGIdb uses uppercase names, e.g., “TP53”)
    input_val = input_val.upper()

    # Show progress bar
    import time
    progress_text = "⏳ Searching for interactions..."
    progress_bar = st.progress(100, text=progress_text)

    # Save input in session_state based on mode
    if mode == "Drug":
        st.session_state["drug_input"] = input_val
    else:
        st.session_state["gene_input"] = input_val

    # --- enables the results in tables and visuals pages
    st.session_state["searched"] = True

    # --- set API endpoint (GraphQL)
    url = "https://dgidb.org/api/graphql"
    # --- wrap input in quotes (makes it safe for GraphQL)
    safe_name = json.dumps(input_val)

    # Build query based on the DGIdb API Documentation
    # For the searched drug retrieve every interacting gene's name, longName, interactionScore
    # For the searched gene retrieve every interacting drug's name, conceptId, interactionScore, interactionType
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

    # Send POST request
    response = requests.post(url, json={"query": query})

    # Check response success, save the response in session_state for other pages to use
    if response.status_code == 200:
        results = response.json()
        st.session_state["results"] = results

        # Initialize an empty list to store parsed results
        interactions = []

        # --- Parse and display results
        # --- Drug mode
        if mode == "Drug":
            nodes = results.get("data", {}).get("drugs", {}).get("nodes", [])
            
            # Filter nodes to exact name match (case-insensitive)
            exact_nodes = [node for node in nodes if node.get("name", "").upper() == input_val]

            if not exact_nodes:
                st.warning("⚠️ No exact matches found for your drug input.")
                st.session_state["valid_search"] = False
            
            else:
                for node in exact_nodes:
                    for interaction in node.get("interactions", []):
                        gene = interaction["gene"]
                        interactions.append({
                            "Gene": gene.get("name", "N/A"),
                            "Description": gene.get("longName", "N/A"),
                            "Score": interaction.get("interactionScore", 0)
                        })
        # Gene mode
        else:  
            nodes = results.get("data", {}).get("genes", {}).get("nodes", [])
            # Filter nodes to exact name match (case-insensitive)
            exact_nodes = [node for node in nodes if node.get("name", "").upper() == input_val]

            if not exact_nodes:
                st.warning("⚠️ No exact matches found for your gene input.")
                st.session_state["valid_search"] = False
            else:
                for node in exact_nodes:
                    for interaction in node.get("interactions", []):
                        drug = interaction["drug"]
                        interactions.append({
                            "Drug": drug.get("name", "N/A"),
                            "ID": drug.get("conceptId", "N/A"),
                            "Score": interaction.get("interactionScore", 0)
                        })

        if interactions:
            # --- If results are collected, create a df for future use
            df = pd.DataFrame(interactions)
            # --- If df empty show warning 
            if df.empty:
                st.session_state["valid_search"] = False
            else:
                st.session_state["df"] = df
                st.success("✅ Interactions retrieved! Use the sidebar to explore results.")
                st.session_state["valid_search"] = True
        # if results not collected show warning
        else:
            st.session_state["valid_search"] = False
    # if request fails show warning
    else:
        st.error(f"❌ API request failed with status code {response.status_code}")
        st.session_state["valid_search"] = False


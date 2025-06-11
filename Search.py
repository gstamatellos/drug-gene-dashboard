import streamlit as st
import requests
import pandas as pd
import json

st.set_page_config(page_title="PharmXplorer", layout="wide")
st.image("data/home_image.png")
st.title("Welcome to Drug ⇄ Gene Interaction Explorer")

st.markdown("""
This app allows you to search **drug–gene interactions** from the [DGIdb](https://dgidb.org) API and **pharmacogenomic variant-drug annotations** data from [PharmGKB](https://www.pharmgkb.org/).

After searching, use the sidebar to explore:
- **Results Tables** 
- **Interaction - Annotation Visuals**  

New feature: Clinician Safety Checker  
Navigate in the sidebar and take a look!
""")

# --- Initialize session state for inputs ---
if "mode" not in st.session_state:
    st.session_state["mode"] = "Drug"
if "gene_input" not in st.session_state:
    st.session_state["gene_input"] = ""
if "drug_input" not in st.session_state:
    st.session_state["drug_input"] = ""
if "searched" not in st.session_state:
    st.session_state["searched"] = False

st.markdown("---")

# --- Mode select ---
mode = st.radio("Select search mode:", ["Drug", "Gene"], index=0 if st.session_state["mode"] == "Drug" else 1, horizontal=True)
st.session_state["mode"] = mode

# --- Input based on mode ---
if mode == "Drug":
    input_val = st.text_input("Type Drug name and press Enter:").strip()
else:
    input_val = st.text_input("Type Gene name and press Enter:").strip()

input_val = input_val.upper()

# --- Auto-search on Enter ---
search_triggered = input_val and (
    input_val != (st.session_state["drug_input"] if mode == "Drug" else st.session_state["gene_input"])
)

if search_triggered:
    # Progress bar setup
    import time
    progress_text = "⏳ Searching for interactions..."
    progress_bar = st.progress(100, text=progress_text)

    # Save input based on mode
    if mode == "Drug":
        st.session_state["drug_input"] = input_val
    else:
        st.session_state["gene_input"] = input_val

    st.session_state["searched"] = True

    url = "https://dgidb.org/api/graphql"
    safe_name = json.dumps(input_val)

    # Build query
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

    if response.status_code == 200:
        results = response.json()
        st.session_state["results"] = results

        interactions = []

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

        else:  # Gene mode
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
            df = pd.DataFrame(interactions)
            if df.empty:
                st.session_state["valid_search"] = False
            else:
                st.session_state["df"] = df
                st.success("✅ Interactions retrieved! Use the sidebar to explore results.")
                st.session_state["valid_search"] = True
        else:
            st.session_state["valid_search"] = False
    else:
        st.error(f"❌ API request failed with status code {response.status_code}")
        st.session_state["valid_search"] = False

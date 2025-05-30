import streamlit as st
import requests
import pandas as pd
import json

st.set_page_config(page_title="PharmXplorer", layout="wide")
st.image("data/home_image.png")
st.title("Welcome to Drug ⇄ Gene Interaction Explorer")

st.markdown("""
This app allows you to search **drug–gene interactions** from the [DGIdb](https://dgidb.org) API and **pharmacogenomic variant-drug annotations** data from [PharmGKB] (https://www.pharmgkb.org/).

After searching, use the sidebar to explore:
- **Results Tables** 
- **Interaction Visuals** 
""")

# --- Initialize session state for inputs ---
if "mode" not in st.session_state:
    st.session_state["mode"] = "Drug"
if "gene_input" not in st.session_state:
    st.session_state["gene_input"] = ""
if "drug_input" not in st.session_state:
    st.session_state["drug_input"] = ""

st.markdown("---")

# --- Mode select ---
mode = st.radio("Select search mode:", ["Drug", "Gene"], index=0 if st.session_state["mode"] == "Drug" else 1, horizontal=True)
st.session_state["mode"] = mode

# --- Input based on mode ---
if mode == "Drug":
    input_val = st.text_input("Enter Drug name:", value=st.session_state["drug_input"]).strip().upper()
else:
    input_val = st.text_input("Enter Gene name:", value=st.session_state["gene_input"]).strip().upper()

# --- On search button click ---
if st.button("Search") and input_val:
    
    # Progress bar setup
    import time
    progress_text = "⏳ Searching for interactions..."
    progress_bar = st.progress(100, text=progress_text)
    
    # Save input based on mode
    if mode == "Drug":
        st.session_state["drug_input"] = input_val
    else:
        st.session_state["gene_input"] = input_val

    url = "https://dgidb.org/api/graphql"
    safe_name = json.dumps(input_val)

    # Build query
    if mode == "Drug":
        query = f"""
        {{
          drugs(names: [{safe_name}]) {{
            nodes {{
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
            for node in results.get("data", {}).get("drugs", {}).get("nodes", []):
                for interaction in node.get("interactions", []):
                    gene = interaction["gene"]
                    interactions.append({
                        "Gene": gene.get("name", "N/A"),
                        "Description": gene.get("longName", "N/A"),
                        "Score": interaction.get("interactionScore", 0)
                    })
        else:
            for node in results.get("data", {}).get("genes", {}).get("nodes", []):
                for interaction in node.get("interactions", []):
                    drug = interaction["drug"]
                    interactions.append({
                        "Drug": drug.get("name", "N/A"),
                        "ID": drug.get("conceptId", "N/A"),
                        "Score": interaction.get("interactionScore", 0)
                    })

        if interactions:
            df = pd.DataFrame(interactions)
            st.session_state["df"] = df
            st.success("✅ Interactions retrieved! Use the sidebar to explore results.")
        else:
            st.warning("⚠️ No interactions found for the provided input.")
    else:
        st.error(f"❌ API request failed with status code {response.status_code}")

import streamlit as st

# --- Browser tab title and full-width layout ---
st.set_page_config(page_title="Home", layout="wide")
st.title("Welcome to Drug ⇄ Gene Interaction Explorer")
st.image("data/home_image.png")

# --- Intro text ---
st.markdown("""
This app allows you to search **drug–gene interactions** from the [DGIdb](https://dgidb.org) API 
and **pharmacogenomic variant-drug annotations** data from [ClinPGx](https://www.clinpgx.org/).

Use the **sidebar** to explore:
- **Drug - Gene Interaction Tables and Visuals** 
- **Clinician Safety Checker**  
""")

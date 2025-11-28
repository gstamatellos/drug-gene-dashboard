import streamlit as st

# --- Browser tab title and full-width layout ---
st.set_page_config(page_title="Home", layout="wide")
st.title("Welcome to Drug ⇄ Gene Interaction Explorer")
st.image("data/home_image.png")

# --- Intro text ---
st.markdown("""
This app allows you to search **drug–gene interactions** from the [DGIdb](https://dgidb.org) API 
and **pharmacogenomic variant-drug annotations** data from [ClinPGx](https://www.clinpgx.org/).

After searching, use the sidebar to explore:
- **Results Tables** 
- **Interaction - Annotation Visuals**  
""")

st.markdown("""
""")

# --- Clinician Safety Checker button in main page ---
st.markdown("**NEW: Clinician Safety Checker**")
if st.button("Visit page"):
    st.session_state["goto_clinician_checker"] = True
    st.info("Please click the sidebar page **Clinician Safety Checker** to continue!")

st.markdown("---")
st.title("Drug - Gene Interactions")

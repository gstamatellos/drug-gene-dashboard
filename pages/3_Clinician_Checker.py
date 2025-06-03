import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Clinician Safety Checker", layout="wide")
st.title("Clinician Safety Checker")
st.markdown("""
Check if a prescribed **drug** has associated **genetic variants** that affect patient safety, efficacy, or dosing.  
Data is sourced from [PharmGKB](https://www.pharmgkb.org).
""")

# --- Input ---
drug = st.text_input("Enter drug name (e.g. clopidogrel, warfarin, abacavir):").strip().lower()

if st.button("Check Drug Safety") and drug:
    with st.spinner("Fetching variant annotations..."):
        # Format drug name for API
        url = f"https://api.pharmgkb.org/v1/data/variantAnnotation?drugName={drug}&limit=1000"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json().get("data", [])
            
            if not data:
                st.warning(f"No variant annotations found for '{drug}'. Try another drug.")
            else:
                # Parse data
                rows = []
                for entry in data:
                    rows.append({
                        "Gene": entry.get("gene", {}).get("name", "N/A"),
                        "Variant": entry.get("variant", {}).get("name", "N/A"),
                        "Phenotype": entry.get("phenotypeCategory", "N/A"),
                        "Evidence Level": entry.get("evidenceLevel", "N/A"),
                        "Clinical Annotation": entry.get("clinicalAnnotation", {}).get("text", "N/A")
                    })
                
                df = pd.DataFrame(rows)
                
                # Filters
                with st.expander("Filter results"):
                    pheno_filter = st.multiselect("Phenotype category", options=df["Phenotype"].unique(), default=df["Phenotype"].unique())
                    level_filter = st.multiselect("Evidence level", options=df["Evidence Level"].unique(), default=df["Evidence Level"].unique())
                    df = df[df["Phenotype"].isin(pheno_filter) & df["Evidence Level"].isin(level_filter)]

                st.success(f"Found {len(df)} variant annotations.")
                st.dataframe(df)

                # Optional: Download
                st.download_button("Download results as CSV", data=df.to_csv(index=False), file_name=f"{drug}_variant_safety.csv")
        else:
            st.error("Failed to fetch data from PharmGKB.")


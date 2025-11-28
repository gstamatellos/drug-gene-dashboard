import streamlit as st
import pandas as pd

st.set_page_config(page_title="Clinician Safety Checker", layout="wide")
st.title("Clinician Safety Checker")

st.markdown("""
Check if a prescribed drug has **associated genetic variants** that affect patient safety, efficacy, or dosing.  
Data is sourced from **ClinPGx clinical annotations.**
""")

st.markdown("---")

# ------------------------------
# --- Session State Fix -------
# ------------------------------
if "search_triggered" not in st.session_state:
    st.session_state.search_triggered = False

if "saved_input" not in st.session_state:
    st.session_state.saved_input = ""

if "saved_type" not in st.session_state:
    st.session_state.saved_type = "Drug"


# --- Load data once ---
@st.cache_data
def load_annotations():
    df = pd.read_csv("data/clinical_annotations.tsv", sep="\t")
    df = df[[
        "Gene",
        "Variant/Haplotypes",
        "Drug(s)",
        "Phenotype Category",
        "Level of Evidence",
        "Clinical Annotation"
    ]]
    df.columns = [
        "Gene",
        "Variant",
        "Drug",
        "Response",
        "Evidence Level",
        "Note"
    ]
    return df

annotations_df = load_annotations()


# --- Search type selection ---
search_type = st.radio(
    "Search by drug name (e.g. warfarin), disease/phenotype (e.g. hemorrhage), or gene (e.g. CYP2C19)",
    ["Drug", "Disease/Phenotype", "Gene"],
    horizontal=True,
    key="saved_type"
)

search_input = st.text_input(
    f"Type {search_type.lower()} and press Enter:",
    key="saved_input"
)

search_button = st.button("Search")


# ------------------------------
# --- Persistent Search Logic --
# ------------------------------
if search_button:
    if st.session_state.saved_input.strip() != "":
        st.session_state.search_triggered = True
    else:
        st.session_state.search_triggered = False


# ------------------------------
# --- Only show results if search triggered ---
# ------------------------------
if st.session_state.search_triggered:
    search_input = st.session_state.saved_input
    search_type = st.session_state.saved_type

    # --- Search logic ---
    if search_type == "Drug":
        matched = annotations_df[
            annotations_df["Drug"].str.lower().str.contains(search_input.strip().lower(), na=False)
        ]

    elif search_type == "Disease/Phenotype":
        matched = annotations_df[
            annotations_df["Note"].str.lower().str.contains(search_input.strip().lower(), na=False)
        ]

    else:  # GENE SEARCH
        matched = annotations_df[
            annotations_df["Gene"].str.lower().str.contains(search_input.strip().lower(), na=False)
        ]

    # --- Only show results if matches exist ---
    if not matched.empty:
        st.markdown(" ")
        st.success(f"Found {len(matched)} variant annotations for **{search_input.title()}**")
        st.markdown("---")

        # --- Filters ---
        with st.expander("🔍 Filter results"):
            pheno_filter = st.multiselect(
                "Phenotype category",
                matched["Response"].unique(),
                default=matched["Response"].unique()
            )
            level_filter = st.multiselect(
                "Evidence level",
                matched["Evidence Level"].unique(),
                default=matched["Evidence Level"].unique()
            )
            matched = matched[
                matched["Response"].isin(pheno_filter) &
                matched["Evidence Level"].isin(level_filter)
            ]

        # --- Recommended Gene Panel (only for Drug and Disease searches) ---
        if search_type in ["Drug", "Disease/Phenotype"]:
            st.markdown("### 🧬 Recommended Gene Panel")
            gene_rows = matched[['Gene', 'Evidence Level', 'Drug']].dropna()
            if not gene_rows.empty:
                # For each gene, show strongest evidence
                best_levels = (
                    gene_rows.groupby('Gene')['Evidence Level']
                    .apply(lambda x: x.mode()[0])
                    .reset_index()
                )

                priority = {"1A": 1, "1B": 2, "2A": 3, "2B": 4, "3": 5}
                best_levels['priority'] = best_levels['Evidence Level'].map(priority)
                best_levels = best_levels.sort_values('priority')

                for _, row in best_levels.iterrows():
                    # For disease searches, also list drugs associated with the gene
                    if search_type == "Disease/Phenotype":
                        drugs_for_gene = gene_rows[gene_rows['Gene'] == row['Gene']]['Drug'].unique()
                        drugs_str = ", ".join(drugs_for_gene)
                        st.markdown(f"- **{row['Gene']}** — evidence: *{row['Evidence Level']}* — Drugs: {drugs_str}")
                    else:
                        st.markdown(f"- **{row['Gene']}** — evidence: *{row['Evidence Level']}*")
            else:
                st.info("No genes found for this search.")

        # --- Summary counts ---
        high_ev = matched[matched["Evidence Level"].isin(["1A", "1B", "2A"])]

        high_risk = matched[
            (matched["Evidence Level"].isin(["1A", "1B", "2A"])) &
            (matched["Response"].str.contains("Toxicity", case=False))
        ]

        efficacy = matched[
            (matched["Evidence Level"].isin(["1A", "1B", "2A"])) &
            (matched["Response"].str.contains("Efficacy", case=False))
        ]

        dosage = matched[
            (matched["Evidence Level"].isin(["1A", "1B", "2A"])) &
            (matched["Response"].str.contains("Dosage", case=False))
        ]

        st.markdown("### 🔎 Summary")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("High Evidence", len(high_ev))
        col2.metric("High-Risk Variants", len(high_risk))
        col3.metric("Probable therapeutic success", len(efficacy))
        col4.metric("Recommended dosage changes", len(dosage))

        # --- Color-coding for clinical relevance ---
        def color_row(row):
            color = ""
            if row["Evidence Level"] in ["1A", "1B", "2A"]:
                if "Toxicity" in str(row["Response"]):
                    color = "background-color: #ffcccc"
                elif "Efficacy" in str(row["Response"]):
                    color = "background-color: #d0f0c0"
                elif "Dosage" in str(row["Response"]):
                    color = "background-color: #ffffcc"
            return [color] * len(row)

        styled_df = matched.style.apply(color_row, axis=1)

        st.dataframe(styled_df, use_container_width=True)

        st.download_button(
            "📥 Download results as CSV",
            data=matched.to_csv(index=False),
            file_name=f"{search_input}_{search_type.lower()}_variant_safety.csv"
        )

        st.markdown(" ")

        with st.expander("About these results"):
            st.markdown("""
            The table above shows pharmacogenomic variant annotations linked to the selected drug or disease. Each row represents a **gene–variant–drug** interaction affecting:

            - **Toxicity**
            - **Efficacy**
            - **Dosage**
            - **Metabolism/PK**
            - **PD (Pharmacodynamics)**

            These variants help guide clinical decisions and selection of gene panels.
            """)

        with st.expander("What do evidence levels mean?"):
            st.markdown("""
            **Evidence Level Summary (from PharmGKB)**  
            - **1A**: Guideline or FDA label + supporting publication  
            - **1B**: High evidence from ≥2 studies  
            - **2A**: Moderate evidence and in a VIP gene  
            """)

        with st.expander("The **Note** column"):
            st.markdown("""
            Provides context about phenotypes associated with the variant–drug interaction.
            """)

    else:
        st.warning(f"No variant annotations found for '{search_input}'. Try another term.")

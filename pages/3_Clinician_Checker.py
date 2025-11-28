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
# --- Only show results if search triggered AND input is non-empty ---
# ------------------------------
if st.session_state.search_triggered and st.session_state.saved_input.strip() != "":
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
            st.markdown("_Panel generated from variants with Evidence Level 1A, 1B, 2A, 2B only._")
            
            # Keep only clinically significant variants
            panel_df = matched[matched["Evidence Level"].isin(["1A","1B","2A","2B"])].copy()
            
            if not panel_df.empty:
                # Group by gene, aggregate variants (and drugs for disease)
                gene_group = panel_df.groupby('Gene').agg({
                    'Variant': lambda x: ", ".join(sorted(set(x))),
                    'Drug': lambda x: ", ".join(sorted(set(x))),
                    'Evidence Level': lambda x: x.mode()[0]
                }).reset_index()

                # Sort by Evidence Level priority
                priority = {"1A": 1, "1B": 2, "2A": 3, "2B": 4}
                gene_group['priority'] = gene_group['Evidence Level'].map(priority)
                gene_group = gene_group.sort_values('priority')

                # Display
                for _, row in gene_group.iterrows():
                    if search_type == "Disease/Phenotype":
                        drugs_for_gene = row['Drug']
                        st.markdown(f"- **{row['Gene']}** — variants: {row['Variant']} — Drugs: {drugs_for_gene}")
                    else:  # Drug search
                        st.markdown(f"- **{row['Gene']}** — variants: {row['Variant']}")
            else:
                st.info("No genes with high evidence found for this search.")

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

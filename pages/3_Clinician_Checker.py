import streamlit as st
import pandas as pd

st.set_page_config(page_title="Clinician Safety Checker", layout="wide")
st.title("Clinician Safety Checker")

st.markdown("""
Check if a prescribed drug has **associated genetic variants** that affect patient safety, efficacy, or dosing.  
Data is sourced from **ClinPGx clinical annotations.**
""")

st.markdown("---")

# --- Initialize session state ---
if "clinic_search_triggered" not in st.session_state:
    st.session_state.clinic_search_triggered = False
if "clinic_input" not in st.session_state:
    st.session_state.clinic_input = ""
if "clinic_type" not in st.session_state:
    st.session_state.clinic_type = "Drug"
if "clinic_last_searched" not in st.session_state:
    st.session_state.clinic_last_searched = ""

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
    "Search by:",
    ["Drug", "Disease/Phenotype", "Gene"],
    horizontal=True,
)

# Store search type
st.session_state.clinic_type = search_type

# --- Input field (maintains lowercase, converts for search) ---
search_input = st.text_input(
    f"Type {search_type.lower()} name:",
    value=st.session_state.clinic_input,
    placeholder=f"e.g., {'warfarin' if search_type == 'Drug' else 'hemorrhage' if search_type == 'Disease/Phenotype' else 'CYP2C19'}",
    key="clinic_text_input"
).strip()

# Update session state with current input
st.session_state.clinic_input = search_input

# --- Search button ---
search_button = st.button("Search", type="primary")

# --- Perform search when button is clicked ---
if search_button and search_input:
    st.session_state.clinic_search_triggered = True
    st.session_state.clinic_last_searched = search_input
elif search_button and not search_input:
    st.warning(f"⚠️ Please enter a {search_type.lower()} name to search.")
    st.session_state.clinic_search_triggered = False

# --- Display results if search has been triggered ---
if st.session_state.clinic_search_triggered and st.session_state.clinic_last_searched:
    search_term = st.session_state.clinic_last_searched
    current_type = st.session_state.clinic_type
    
    # --- Search logic ---
    if current_type == "Drug":
        matched = annotations_df[
            annotations_df["Drug"].str.lower().str.contains(search_term.lower(), na=False)
        ]
    elif current_type == "Disease/Phenotype":
        matched = annotations_df[
            annotations_df["Note"].str.lower().str.contains(search_term.lower(), na=False)
        ]
    else:  # Gene search
        matched = annotations_df[
            annotations_df["Gene"].str.lower().str.contains(search_term.lower(), na=False)
        ]

    # --- Display results ---
    if not matched.empty:
        st.markdown("---")
        st.info(f"📊 Currently viewing results for: **{search_term.title()}**")
        st.success(f"✅ Found **{len(matched)}** variant annotations")

        # --- 1. Clinical Summary (Drug only) ---
        if current_type == "Drug":
            st.markdown("### 📋 Clinical Summary")
            
            high_risk = matched[
                (matched["Evidence Level"].isin(["1A", "1B", "2A", "2B"])) &
                (matched["Response"].str.contains("Toxicity", case=False, na=False))
            ]
            efficacy_variants = matched[
                (matched["Evidence Level"].isin(["1A", "1B", "2A", "2B"])) &
                (matched["Response"].str.contains("Efficacy", case=False, na=False))
            ]
            dosage_issues = matched[
                (matched["Evidence Level"].isin(["1A", "1B", "2A", "2B"])) &
                (matched["Response"].str.contains("Dosage", case=False, na=False))
            ]
            important_genes = matched[matched["Evidence Level"].isin(["1A", "1B", "2A", "2B"])]["Gene"].dropna().unique()

            # Summary text
            summary_parts = []
            
            if len(high_risk) > 0:
                summary_parts.append(f"⚠️ Patient may be at increased risk due to **{len(high_risk)} high-risk variant(s)** affecting toxicity.")
            else:
                summary_parts.append("✅ No high-risk toxicity variants detected.")
            
            if len(efficacy_variants) > 0:
                summary_parts.append(f"- **{len(efficacy_variants)} variant(s)** may impact therapeutic efficacy.")
            
            if len(dosage_issues) > 0:
                summary_parts.append(f"- **{len(dosage_issues)} variant(s)** may require dose adjustments.")
            
            if len(important_genes) > 0:
                gene_list = ', '.join(sorted(important_genes))
                summary_parts.append(f"- Key genes of clinical importance: {gene_list}")
                summary_parts.append("Genetic testing is recommended to guide therapy.")
            else:
                summary_parts.append("• No high-evidence genes identified. Genetic testing may be considered based on clinical context.")

            st.markdown("\n\n".join(summary_parts))
            st.markdown("---")

        # --- 2. Recommended Gene Panel (Drug/Disease only) ---
        if current_type in ["Drug", "Disease/Phenotype"]:
            st.markdown("### 🧬 Recommended Gene Panel")
            st.caption("_Generated from variants with Evidence Level 1A, 1B, 2A, 2B only_")

            panel_df = matched[matched["Evidence Level"].isin(["1A", "1B", "2A", "2B"])].copy()
            
            if not panel_df.empty:
                gene_group = panel_df.groupby('Gene').agg({
                    'Variant': lambda x: ", ".join(sorted(set(x.dropna()))),
                    'Drug': lambda x: ", ".join(sorted(set(x.dropna()))),
                    'Evidence Level': lambda x: x.mode()[0] if not x.empty else None
                }).reset_index()
                
                priority = {"1A": 1, "1B": 2, "2A": 3, "2B": 4}
                gene_group['priority'] = gene_group['Evidence Level'].map(priority)
                gene_group = gene_group.sort_values('priority')
                
                for idx, row in gene_group.iterrows():
                    if current_type == "Disease/Phenotype":
                        st.markdown(f"**{idx+1}.** **{row['Gene']}** (Evidence: {row['Evidence Level']})  \n"
                                  f"   • Variants: {row['Variant']}  \n"
                                  f"   • Associated drugs: {row['Drug']}")
                    else:
                        st.markdown(f"**{idx+1}.** **{row['Gene']}** (Evidence: {row['Evidence Level']})  \n"
                                  f"   • Variants: {row['Variant']}")
            else:
                st.info("No genes with high evidence (1A, 1B, 2A, 2B) found for this search.")

            st.markdown("---")

        # --- 3. Associations Table ---
        st.markdown("### 📊 Detailed Associations Table")

        # Calculate metrics
        high_ev = matched[matched["Evidence Level"].isin(["1A", "1B", "2A"])]
        high_risk_metric = matched[
            (matched["Evidence Level"].isin(["1A", "1B", "2A"])) &
            (matched["Response"].str.contains("Toxicity", case=False, na=False))
        ]
        efficacy_metric = matched[
            (matched["Evidence Level"].isin(["1A", "1B", "2A"])) &
            (matched["Response"].str.contains("Efficacy", case=False, na=False))
        ]
        dosage_metric = matched[
            (matched["Evidence Level"].isin(["1A", "1B", "2A"])) &
            (matched["Response"].str.contains("Dosage", case=False, na=False))
        ]

        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("High Evidence (1A-2A)", len(high_ev))
        col2.metric("High-Risk (Toxicity)", len(high_risk_metric))
        col3.metric("Efficacy Impact", len(efficacy_metric))
        col4.metric("Dosage Adjustments", len(dosage_metric))

        st.markdown("### ")

        # --- Filters ---
        with st.expander("🔍 Filter results"):
            pheno_filter = st.multiselect(
                "Filter by phenotype category:",
                options=sorted(matched["Response"].unique()),
                default=matched["Response"].unique()
            )
            level_filter = st.multiselect(
                "Filter by evidence level:",
                options=sorted(matched["Evidence Level"].unique(), 
                             key=lambda x: {"1A": 1, "1B": 2, "2A": 3, "2B": 4, "3": 5, "4": 6}.get(x, 99)),
                default=matched["Evidence Level"].unique()
            )
        
        # Apply filters
        filtered_matched = matched[
            matched["Response"].isin(pheno_filter) &
            matched["Evidence Level"].isin(level_filter)
        ]

        # Color coding function
        def color_row(row):
            color = ""
            if row["Evidence Level"] in ["1A", "1B", "2A"]:
                if "Toxicity" in str(row["Response"]):
                    color = "background-color: #ffcccc"  # Light red
                elif "Efficacy" in str(row["Response"]):
                    color = "background-color: #d0f0c0"  # Light green
                elif "Dosage" in str(row["Response"]):
                    color = "background-color: #ffffcc"  # Light yellow
            return [color] * len(row)

        # Display styled dataframe
        if not filtered_matched.empty:
            styled_df = filtered_matched.style.apply(color_row, axis=1)
            st.dataframe(styled_df, use_container_width=True)
            
            # Download button
            st.download_button(
                "📥 Download filtered results as CSV",
                data=filtered_matched.to_csv(index=False),
                file_name=f"{search_term.replace(' ', '_')}_{current_type.lower()}_variant_safety.csv",
                mime="text/csv"
            )
        else:
            st.warning("No results match the current filters.")

        # --- Information expanders ---
        st.markdown("### ")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            with st.expander("ℹ️ About these results"):
                st.markdown("""
                The table shows pharmacogenomic variant annotations linked to the selected search term.
                
                Each row represents a **gene–variant–drug** interaction affecting:
                - **Toxicity** (risk of adverse effects)
                - **Efficacy** (treatment effectiveness)
                - **Dosage** (dose adjustments needed)
                - **Metabolism/PK** (pharmacokinetics)
                - **PD** (pharmacodynamics)
                """)
        
        with col2:
            with st.expander("📊 Evidence levels explained"):
                st.markdown("""
                **Evidence Level Summary (PharmGKB)**
                
                - **1A**: Clinical guideline or FDA label + supporting publication
                - **1B**: High-quality evidence from ≥2 independent studies
                - **2A**: Moderate evidence in a VIP (Very Important Pharmacogene)
                - **2B**: Moderate evidence, multiple studies
                - **3**: Limited or conflicting evidence
                - **4**: Case reports or preliminary data
                
                [Learn more at PharmGKB](https://www.pharmgkb.org/page/clinAnnLevels)
                """)
        
        with col3:
            with st.expander("🎨 Color coding"):
                st.markdown("""
                **High evidence (1A-2A) rows are color-coded:**
                
                - 🟥 **Red**: Toxicity concerns
                - 🟩 **Green**: Efficacy impacts
                - 🟨 **Yellow**: Dosage adjustments
                - ⬜ **White**: Other categories or lower evidence
                """)

    else:
        st.markdown("---")
        st.warning(f"⚠️ No variant annotations found for **'{search_term}'**. Try another search term.")
        st.info("💡 **Tips**\n- Check spelling\n- Try a different search type\n- Use generic drug names (e.g., 'paracetamol' instead of 'Depon')")

elif st.session_state.clinic_search_triggered and not st.session_state.clinic_last_searched:
    st.info("🔍 Please enter a search term and click Search.")



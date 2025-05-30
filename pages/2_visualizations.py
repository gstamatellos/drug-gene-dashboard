import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

st.title("📊 Interaction Visuals")
st.markdown("---")

# Require valid DataFrame
if "df" not in st.session_state or st.session_state["df"] is None:
    st.info("🔍 Please perform a search from the Home page first.")
    st.stop()

df = st.session_state["df"]
mode = st.session_state.get("mode", "Drug")

if df.empty:
    st.warning("No interaction data to display.")
    st.stop()

# Determine label column
label_col = "Gene" if mode == "Drug" else "Drug"

if label_col not in df.columns:
    st.error(f"❌ You are currently in {mode} mode, but the last results are from {label_col} search. Please go back and perform a new search.")
    st.stop()

st.subheader("Top Interactions by Score")

# Safe slider logic
num_rows = len(df)
if num_rows < 4:
    st.info(f"Only {num_rows} interactions found. Displaying all available results.")
    top_n = num_rows
else:
    top_n = st.slider("Select top N entries by score", 3, min(10, num_rows), min(5, num_rows))

top_df = df.sort_values("Score", ascending=False).head(top_n)


# Barplot
st.markdown("#### Barplot")
fig2, ax2 = plt.subplots(figsize=(10, 6))
sns.barplot(data=top_df, x="Score", y=label_col, palette="mako", ax=ax2)
ax2.set_xlabel("Interaction Score")
ax2.set_ylabel(label_col)
st.pyplot(fig2)

# Spacer between plots
st.markdown("### ")

# Pie Chart
st.markdown("#### Pie Chart")
fig1, ax1 = plt.subplots()
colors = sns.color_palette("pastel", len(top_df))  
ax1.pie(top_df["Score"], labels=top_df[label_col], autopct="%1.1f%%", startangle=90, colors=colors)
ax1.axis("equal")
st.pyplot(fig1)


# Spacer between plots
st.markdown("### ")

# interaction types
types = []
for node in st.session_state.get("results", {}).get("data", {}).get("genes", {}).get("nodes", []):
    for interaction in node.get("interactions", []):
        for i_type in interaction.get("interactionTypes", []):
            types.append(i_type.get("type"))

if types:
    st.subheader(" Most Common Interaction Types")
    type_df = pd.DataFrame(types, columns=["Type"])
    fig, ax = plt.subplots()
    sns.countplot(data=type_df, y="Type", order=type_df["Type"].value_counts().index, palette="turbo", ax=ax)
    ax.set_xlabel("Count")
    st.pyplot(fig)
else:
    st.subheader(" Most Common Interaction Types")
    st.info("No interaction types information available.")

# --- Pharmacogenomic Associations Visuals ---

st.markdown("---")
st.subheader("Pharmacogenomic Associations")

if mode == "Drug":
    # Check if pharm_subset_index is available and not empty
    pharm_subset_index = st.session_state.get("pharm_subset_index")
    if pharm_subset_index is None or pharm_subset_index.empty:
        st.info("No pharmacogenomics annotations available for this drug.")
        st.stop()

    st.markdown("### 1. Top Genes with Most Variant Annotations")
    gene_counts = pharm_subset_index['Gene'].value_counts().head(10)
    fig1, ax1 = plt.subplots()
    sns.barplot(x=gene_counts.index, y=gene_counts.values, ax=ax1, palette="viridis")
    ax1.set_ylabel("Number of Variants")
    ax1.set_xlabel("Gene")
    ax1.set_title("Top 10 Genes by Variant Count")
    plt.xticks(rotation=45)
    st.pyplot(fig1)

    st.markdown("### 2. Phenotype Category Distribution")
    fig2, ax2 = plt.subplots()
    sns.countplot(data=pharm_subset_index, x='Phenotype Category', order=pharm_subset_index['Phenotype Category'].value_counts().index, palette="coolwarm", ax=ax2)
    ax2.set_title("Phenotype Categories Across Variants")
    plt.xticks(rotation=45)
    st.pyplot(fig2)

    st.markdown("### 3. Score Distribution by Phenotype Category")
    fig3, ax3 = plt.subplots()
    sns.boxplot(data=pharm_subset_index, x='Phenotype Category', y='Score', palette="Set2", ax=ax3)
    ax3.set_title("Score Comparison Across Phenotype Categories")
    plt.xticks(rotation=45)
    st.pyplot(fig3)

    st.markdown("### 4. Heatmap: Gene vs. Phenotype Category")
    heatmap_data = pd.crosstab(pharm_subset_index['Gene'], pharm_subset_index['Phenotype Category'])
    fig4, ax4 = plt.subplots(figsize=(10, 6))
    sns.heatmap(heatmap_data, cmap="YlGnBu", annot=True, fmt="d", linewidths=.5, ax=ax4)
    ax4.set_title("Gene–Phenotype Heatmap")
    st.pyplot(fig4)

    st.markdown("### 5. Interactive Scatter Plot")
    import plotly.express as px
    fig5 = px.scatter(
        pharm_subset_index,
        x='Variant/Haplotypes',
        y='Score',
        color='Phenotype Category',
        hover_data=['Gene', 'Clinical Annotation'],
        title="Pharmacogenomic Variants: Score Distribution"
    )
    fig5.update_layout(xaxis_title="Variant/Haplotype", yaxis_title="Score", height=600)
    st.plotly_chart(fig5)
else:
    st.info("No pharmacogenomic annotations available for gene searches.")
    st.stop()

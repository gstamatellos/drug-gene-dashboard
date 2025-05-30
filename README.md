# PharmXplorer: Drug–Gene Interaction Dashboard

PharmXplorer is a Streamlit web application for querying and visualizing drug–gene interactions using the DGIdb GraphQL API, now extended with pharmacogenomic variant annotations from PharmGKB.

Users can input a human gene (e.g., `TP53`, `BRCA1`) or drug (e.g., `Clopidogrel`, `Tamoxifen`) and retrieve known interaction partners, along with interaction scores, types, and pharmacogenomic insights. It provides an interactive, lightweight interface suitable for bioinformatics, precision medicine, research, and education in pharmacogenomics.

---

## Key Features

- Flexible search: Query by gene or drug name  
- Interactive tables: View and filter DGIdb results  
- Download support: Export results as `.csv`  
- Visual summaries: Graphs of drug–gene interaction types  
- Live API: Real-time data from the DGIdb GraphQL API  
- Pharmacogenomic Annotations: Clinical variant data from PharmGKB  
- New visual analytics:
  - Barplot of genes with the most variants  
  - Phenotype category distributions  
  - Score distribution by phenotype  
  - Gene–phenotype heatmap

---

## Tech Stack

- Python 3.10+  
- Streamlit  
- Pandas  
- Seaborn & Matplotlib  
- Plotly Express  
- DGIdb GraphQL API  
- PharmGKB TSV data

---

## App Structure

The application includes four main pages:

1. **Home**  
   Search by entering a drug or gene name and choosing a search mode.

2. **Interaction Table**  
   View and explore interaction results from DGIdb, pharmacogenomic variant-drug associations from PharmGKB.

3. **Interaction Visuals - Pharamcogenomic Variants**  
   View bar charts and distribution plots summarizing drug–gene interactions, including interaction types and partners.

   **Variant Annotations** (NEW)  
   Visualize curated clinical annotations from PharmGKB related to drug–gene–variant relationships:
   - Top 10 genes with the most variant annotations  
   - Phenotype category distributions (e.g., efficacy, toxicity)  
   - Score distributions across phenotype categories  
   - Heatmaps of gene vs. Clinical Annotation relationships  

---

## Data & Attribution

This app integrates open-access data from:

- [DGIdb](https://dgidb.org) — Drug–Gene Interaction Database  
- [PharmGKB](https://www.pharmgkb.org) — Pharmacogenomics Knowledgebase  
- [NCBI](https://www.ncbi.nlm.nih.gov)  
- [GeneCards](https://www.genecards.org)  
- [DrugBank](https://go.drugbank.com)  
- [PubChem](https://pubchem.ncbi.nlm.nih.gov)

All content is used for educational and research purposes only. Please consult each provider’s terms of use for more information.

---
## Setup Instructions



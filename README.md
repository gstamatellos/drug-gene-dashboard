# PharmXplorer: Drug–Gene Interaction Dashboard

PharmXplorer is a Streamlit web application for querying and visualizing drug–gene interactions using the DGIdb (Drug–Gene Interaction Database) GraphQL API, now extended with **pharmacogenomic variant annotations** from **PharmGKB**.

The app allows users to input a human gene (e.g., `TP53`, `BRCA1`) or drug (e.g., `Trastuzumab`, `Tamoxifen`) and retrieve known interaction partners, along with corresponding interaction scores, types, and pharmacogenomic insights. It offers a lightweight, interactive interface suitable for research, education, and exploratory analysis in pharmacogenomics, bioinformatics, and precision medicine.

---

## Key Features

-  **Flexible search**: Query by either gene or drug name  
-  **Interactive results**: View and filter tabular data with interaction scores  
-  **Download support**: Export results as a `.csv` file  
-  **Visualizations**: Graphical summaries of drug–gene interactions  
-  **Live API access**: Uses DGIdb’s GraphQL API for real-time data  
-  **Pharmacogenomic Variant Annotations**: Display of clinically relevant gene variants from PharmGKB, including:
  - Gene and variant name
  - Drug affected
  - Phenotype (e.g., efficacy, toxicity)
  - Evidence level and score
  - Source link to PharmGKB annotation

---

## Tech Stack

- Python 3.10+  
- Streamlit  
- Pandas  
- Matplotlib & Seaborn  
- DGIdb GraphQL API  
- PharmGKB TSV data  

---

## App Structure

The application has four main pages:

1. **Home**  
   Input a gene or drug name and trigger the search using the DGIdb API.

2. **Interaction Table**  
   View retrieved interaction data, summary statistics, and download the results as a CSV file.

3. **Interaction Visuals**  
   Display plots of top-scoring interactions and explore interaction types.

4. **Variant Annotations** *(NEW)*  
   Visualize curated clinical annotations from PharmGKB related to gene–drug interactions, including variant-specific efficacy and toxicity information.

---

## Data and Resource Attribution

This application uses publicly available data and resources from the following databases:

- **DGIdb** — [https://dgidb.org](https://dgidb.org)  
- **PharmGKB** — [https://www.pharmgkb.org](https://www.pharmgkb.org)  
- **NCBI** — [https://www.ncbi.nlm.nih.gov](https://www.ncbi.nlm.nih.gov)  
- **GeneCards** — [https://www.genecards.org](https://www.genecards.org)  
- **DrugBank** — [https://go.drugbank.com](https://go.drugbank.com)  
- **PubChem** — [https://pubchem.ncbi.nlm.nih.gov](https://pubchem.ncbi.nlm.nih.gov)

These resources are used for educational and research purposes only. All trademarks, logos, and data remain the property of their respective owners. Please refer to each database’s terms of use for more information.

---
## Setup Instructions



# PharmXplorer: Drug–Gene Interaction Dashboard

PharmXplorer is a Streamlit web application for querying and visualizing drug–gene interactions using the DGIdb (Drug–Gene Interaction Database) GraphQL API.

The app allows users to input a human gene (e.g., `TP53`, `BRCA1`) or drug (e.g., `Trastuzumab`, `Tamoxifen`) and retrieve known interaction partners, along with corresponding interaction scores and types. It offers a lightweight, interactive interface suitable for research, education, and exploratory analysis in pharmacogenomics, bioinformatics, and precision medicine.

---

## Key Features

- Flexible search: Query by either gene or drug name  
- Interactive results: View and filter tabular data with interaction scores  
- Download support: Export results as a `.csv` file  
- Visualizations:  
  - Bar and pie charts of top interactions  
  - Summary of common interaction types  
- Live API access: Uses DGIdb’s GraphQL API for real-time data  

---

## Example Use Cases

- A researcher exploring therapeutic targets of a cancer-associated gene  
- A bioinformatician validating gene–drug associations in a pharmacogenomics dataset  
- A clinician or student investigating known drug–gene interactions for educational purposes  

---

## Tech Stack

- Python 3.10+  
- Streamlit  
- Pandas  
- Matplotlib & Seaborn  
- DGIdb GraphQL API  

---

## App Structure

The application has three main pages:

1. **Home**  
   Input a gene or drug name and trigger the search using the DGIdb API.

2. **Interaction Table**  
   View retrieved interaction data, summary statistics, and download the results as a CSV file.

3. **Interaction Visuals**  
   Display plots of top-scoring interactions and explore interaction types.

---

## Setup Instructions

```bash
# Clone the repository
git clone https://github.com/yourusername/pharmxplorer.git
cd pharmxplorer

# (Optional) Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py


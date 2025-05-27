# Drug–Gene Interaction Dashboard

This Streamlit web app allows users to input either a **human gene name** (e.g., `TP53`, `BRCA1`) or a **drug name** (e.g., `Trastuzumab`, `Tamoxifen`) and retrieve known **drug–gene interactions** using the [DGIdb](https://dgidb.org/) API.

It's designed as a lightweight, interactive tool for researchers, students, and healthcare professionals working in pharmacogenomics, precision medicine, and bioinformatics.

---

## Project Goals

- Demonstrate how to integrate and visualize real biomedical data using public APIs
- Build a user-friendly dashboard that supports both gene/drug-based queries
- Showcase practical bioinformatics skills relevant to healthcare and pharma R&D

---

## Features

- **Search drug–gene interactions by gene or drug name**
- View interaction results in a clean, sortable table
- **Download results** as a `.csv` file
- Visual summaries of interaction types (e.g., inhibitors, antagonists)
- Built with Python, Streamlit, Pandas, and the DGIdb GraphQL API

---

## Example Use Cases

- A **researcher** wants to explore all drugs interacting with the gene `TP53`.
- A **pharmacogenomics analyst** wants to find all genes targeted by the drug `Tamoxifen`.

---

## Tech Stack

- Python 3.10
- Streamlit
- Pandas
- DGIdb GraphQL API

---

## Known Limitations

- Some gene or drug names may return no results depending on DGIdb’s current database.
- The app depends on the API’s response and does not store or cache data.
- Matching is case-sensitive and follows official gene (HGNC) and drug naming conventions.

---

## Setup Instructions

```bash
# Clone the repository
git clone https://github.com/yourusername/drug-gene-dashboard.git
cd drug-gene-dashboard

# Set up virtual environment (optional)
python3 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install required packages
pip install -r requirements.txt

# Launch the app
streamlit run app.py

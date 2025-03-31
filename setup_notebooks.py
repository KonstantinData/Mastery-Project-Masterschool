import os
import nbformat as nbf

# Notebook definitions
notebooks = [
    ("01_exploration.ipynb", "# 01 – Exploratory Data Analysis (EDA)"),
    ("02_feature_engineering.ipynb", "# 02 – Feature Engineering"),
    ("03_segmentation.ipynb", "# 03 – Customer Segmentation"),
    ("04_final_analysis.ipynb", "# 04 – Final Analysis & Recommendations"),
]

# Ensure notebooks folder exists
os.makedirs("notebooks", exist_ok=True)

# Create each notebook with a title cell
for filename, title in notebooks:
    nb = nbf.v4.new_notebook()
    nb.cells.append(nbf.v4.new_markdown_cell(title))
    path = os.path.join("notebooks", filename)
    with open(path, "w", encoding="utf-8") as f:
        nbf.write(nb, f)

print("✅ Notebooks created in /notebooks/")

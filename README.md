# 🧠 Mastery Project – TravelTide Perk Recommendation

This project is part of the Masterschool Data Analyst program and focuses on developing a **personalized perk recommendation system** for the fictional travel platform **TravelTide**.

The project is designed to be **public, portable, and reproducible**, using cleaned data from a public AWS S3 bucket and run entirely through Jupyter notebooks. No credentials, `.env` files, or local dependencies are required.

---

## 🔍 Project Objective

The goal is to assign a **personalized perk** to each user, based on their behavior on the platform.  
Only perks supported by available data are included.

### Defined Perks

- ✅ Free checked bag  
- ✅ No cancellation fees  
- ✅ Exclusive discounts  
- ✅ One night free hotel with flight  
- ❌ Free hotel meal *(not supported by the available data)*

[Mastery-Project-Notebook](https://github.com/KonstantinData/Mastery-Project-Masterschool/blob/main/mastery-project-masterschool/notebooks/mastery-project-2025.ipynb)

---

## 🧱 Project Structure

```
mastery-project-masterschool/
├── src/                  custom reusable modules (e.g., data loaders)
├── notebooks/            Jupyter notebooks for each project phase
├── silver_exports/       cleaned data before cohort filtering (excluded from Git)
├── gold_exports/         cohort-filtered data ready for segmentation (excluded from Git)
├── .gitignore            excludes local files from version control
├── pyproject.toml        managed with Rye
```

---

💾 Data Access
All data is loaded directly via public https:// URLs from the TravelTide S3 bucket.
This ensures full portability and avoids the use of credentials or cloud SDKs.

Bronze Layer (Raw Public URLs)<br>
<br>
Users
https://lakehouse-masteryproject-2025.s3.eu-north-1.amazonaws.com/bronze/public_users_export_2025-04-01_101058.csv

Sessions
https://lakehouse-masteryproject-2025.s3.eu-north-1.amazonaws.com/bronze/public_sessions_export_2025-03-31_221253.csv

Flights
https://lakehouse-masteryproject-2025.s3.eu-north-1.amazonaws.com/bronze/public_flights_export_2025-03-31_134734.csv

Hotels
https://lakehouse-masteryproject-2025.s3.eu-north-1.amazonaws.com/bronze/public_hotels_export_2025-03-31_171805.csv

---

## 🔄 Workflow Overview

### 1. 📥 Bronze Layer – Raw Data  
- Raw CSVs loaded via public links  
- Initial exploration, schema inspection, and validation

### 2. 🧹 Silver Layer – Cleaned  
- Dropped columns not needed for perk validation  
- Standardized data types  
- Exported locally as an optional intermediate step

### 3. 🟡 Gold Layer – Cohort Filtered  
- Filtered to users with ≥ 7 sessions since January 4, 2023  
- Only trips and records related to these users are kept  
- Used as the input for clustering

### 4. 👥 Segmentation & Clustering  
- User-level behavior is aggregated across all tables  
- Clustering algorithm applied to segment customers  
- Each cluster is matched with a perk based on its behavior pattern
  
### 5. 🎯 Final Deliverable
- A data-driven strategy that assigns each user to a behavioral segment
- Each segment receives a perk recommendation grounded in actual usage patterns
- Results can be presented through a narrative, notebook, or optional Tableau dashboard

---

## 🧠 Personalization Scope

Perks are assigned based exclusively on **user behavior**, not on demographics or identity.  
This includes:

- Booking and cancellation patterns  
- Discount usage  
- Session volume and engagement  
- Travel behavior (e.g., hotel + flight combinations)

Group or family attributes such as `has_children`, `rooms`, or `seats` are not considered in this logic.

---

## ⚙️ Environment

- ✅ Python with [Rye](https://rye-up.com/) for dependency management  
- ✅ Jupyter Notebooks as the primary interface  
- ✅ `pandas`, `boto3`, `numpy`, `sklearn`, `matplotlib`, etc.  
- ❌ No `.env`, no credentials, no private data

---

## 📁 .gitignore

```
# Local exports – excluded from Git
silver_exports/
gold_exports/

# Notebook clutter
.ipynb_checkpoints/

# Python cache
__pycache__/
```

---

## ✅ Project Status

- ✅ Bronze layer loaded and explored  
- ✅ Silver layer cleaned and column-reduced  
- ✅ Gold layer filtered by cohort (≥ 7 sessions since Jan 4, 2023)  
- ✅ Feature engineering completed (e.g., nights, discount rates)  
- ✅ Silver and gold layers exported (for manual S3 upload)  
- ✅ Segmentation and clustering in progress  
- ⏳ Perk assignment and final presentation pending
- ⏳ Crafting TravelTide Recommendations
- ⏳ Using Visuals to Communicate Key Findings
- ⏳ Project Submission

---

## 📬 Contact

For questions or feedback, please reach out via [GitHub](https://github.com/KonstantinData) or the Masterschool platform.

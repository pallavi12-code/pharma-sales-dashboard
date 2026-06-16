
# Pharma Sales Analytics Dashboard
**Portfolio Project |

An end-to-end analytics project simulating real pharma sales intelligence work —
data pipeline → SQL analysis → interactive BI dashboard.

---

## Tech Stack
| Layer | Tools |
|---|---|
| Data generation | Python (Pandas, NumPy) |
| Storage | SQLite (relational DB) |
| Analysis | SQL (window functions, aggregations, CTEs) |
| Visualization | Streamlit + Plotly |

---



---

## Project Structure
```
pharma_dashboard/
├── 1_generate_dataset.py   ← Creates CSV + SQLite DB
├── 2_sql_analysis.py       ← 8 SQL business questions
├── 3_streamlit_dashboard.py ← Interactive dashboard
├── requirements.txt
└── README.md
```

---

## Key Business Questions Answered
1. Which drugs generate the most revenue?
2. How has each drug grown year-over-year?
3. Which regions contribute most, and what's the concentration risk?
4. Is there a Q4 seasonality effect?
5. Which sales channel has the best margin?
6. Which drug × region segments are highest-value?
7. Which drugs have the best marketing ROI?
8. How did a newly launched drug ramp up over time?

---

#

---

## Dataset Description
Synthetic dataset modeled on realistic pharma sales patterns:
- **1,200+ rows** across 4 years (2021–2024)
- **8 drugs** across 6 therapeutic areas (Oncology, Cardiology, Neurology, etc.)
- **5 regions** in India with city-level granularity
- **4 channels**: Hospital, Retail Pharmacy, Online Pharmacy, Clinic
- **Fields**: units sold, revenue, COGS, gross profit, gross margin %, marketing spend

---

*Built by Rinki Pallavi Marikanti | CBIT AIML 2027 | Portfolio project for analytics roles*

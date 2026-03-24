"""
convert_excel_to_json.py
Reads 'Working on tiktokshop.xlsx' and writes two JSON files:
  - data_files/sheet1_hashtags_keywords.json
  - data_files/sheet2_brands.json

Run once (or whenever the Excel changes):
  python convert_excel_to_json.py
"""

import pandas as pd
import json
import os

EXCEL_PATH = "Working on tiktokshop.xlsx"
OUT_DIR = "data_files"
os.makedirs(OUT_DIR, exist_ok=True)

# ── Sheet 1: Hashtags and keywords ──────────────────────────────────────────
df1 = pd.read_excel(EXCEL_PATH, sheet_name=0, header=1)
df1.columns = ["Category", "Details", "Type"]
df1 = df1.dropna(how="all")

# Forward-fill Category (handles merged cells)
df1["Category"] = df1["Category"].ffill()
df1 = df1.dropna(subset=["Details"])

sheet1 = []
for _, row in df1.iterrows():
    entry = {
        "category": str(row["Category"]).strip(),
        "details":  str(row["Details"]).strip(),
        "type":     str(row["Type"]).strip() if pd.notna(row["Type"]) else "Hashtag",
    }
    sheet1.append(entry)

out1 = os.path.join(OUT_DIR, "sheet1_hashtags_keywords.json")
with open(out1, "w", encoding="utf-8") as f:
    json.dump(sheet1, f, ensure_ascii=False, indent=2)

print(f"✅ Sheet 1 → {out1}  ({len(sheet1)} rows)")

# Quick preview
cats = sorted(set(e["category"] for e in sheet1))
types = sorted(set(e["type"] for e in sheet1))
print(f"   Categories: {cats}")
print(f"   Types: {types}")
print(f"   Sample entries:")
for e in sheet1[:5]:
    print(f"      {e}")

# ── Sheet 2: Brands ─────────────────────────────────────────────────────────
df2 = pd.read_excel(EXCEL_PATH, sheet_name=1, header=0)
df2 = df2.dropna(how="all")

# Normalise column names
df2.columns = [c.strip() for c in df2.columns]
# Expected: Brand, Hashtags, Keywords  (or similar)
print(f"\nSheet 2 columns: {df2.columns.tolist()}")

sheet2 = []
for _, row in df2.iterrows():
    brand = str(row.get("Brand", "") or "").strip()
    if not brand:
        continue
    hashtags_raw = str(row.get("Hashtags", "") or "").strip()
    keywords_raw = str(row.get("Keywords", "") or "").strip()

    entry = {
        "brand":    brand,
        "hashtags": hashtags_raw,
        "keywords": keywords_raw,
    }
    sheet2.append(entry)

out2 = os.path.join(OUT_DIR, "sheet2_brands.json")
with open(out2, "w", encoding="utf-8") as f:
    json.dump(sheet2, f, ensure_ascii=False, indent=2)

print(f"✅ Sheet 2 → {out2}  ({len(sheet2)} brands)")
print(f"   Sample brands:")
for e in sheet2[:5]:
    print(f"      {e}")

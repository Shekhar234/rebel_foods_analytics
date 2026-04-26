"""
Run this script whenever you add new CSV data.
It re-classifies all reviews and saves reviews.pkl
which the web app loads instantly on startup.

Usage:
    python prepare_data.py
"""
import os, sys, glob, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from classifier import classify

BRAND_ALIASES = {
    "Behrouz biryani":                   "Behrouz Biryani",
    "Dabba & Co.":                       "Dabba & Co",
    "Faasos - Wraps & Rolls":            "Faasos - Wraps, Rolls & Shawarma",
    "Faasos Signature Wraps & Rolls":    "Faasos - Wraps, Rolls & Shawarma",
    "Faasos Signature Wraps And Rolls":  "Faasos - Wraps, Rolls & Shawarma",
    "Firangi bake":                      "Firangi Bake",
    "Honest Bowl":                       "Honest bowl",
    "Lunch Box - Meals And Thalis":      "Lunchbox - Meals & Thalis",
    "Sweet Truth - Cake And Desserts":   "Sweet Truth - Cake and Desserts",
    "The biryani life":                  "The Biryani Life",
    "The good bowl":                     "The Good Bowl",
    "The Pizza Project By Oven Story":   "The Pizza Project by Oven Story",
    "The Pizza Project By Oven story":   "The Pizza Project by Oven Story",
    "Veg Darbar By Behrouz Biryani":     "Veg Darbar by Behrouz Biryani",
    "Veg Meals By LunchBox":             "Veg Meals by Lunchbox",
    "Veg Meals By Lunchbox":             "Veg Meals by Lunchbox",
}

def get_week(d):
    if d <= 7:  return "W1"
    if d <= 14: return "W2"
    return "W3"

script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir   = os.path.join(script_dir, "data")
out_path   = os.path.join(data_dir, "reviews.pkl")

files = [f for f in glob.glob(os.path.join(data_dir, "*.csv"))
         if os.path.getsize(f) > 10_000]

if not files:
    print(f"\n  No CSV files found in {data_dir}")
    print("  Add your Zomato/Swiggy CSV files there and re-run.")
    sys.exit(1)

frames = []
for f in files:
    print(f"  Loading: {os.path.basename(f)}")
    try:   df = pd.read_csv(f, encoding="utf-8-sig")
    except: df = pd.read_csv(f, encoding="latin-1")
    df.columns = df.columns.str.strip()

    col_map = {}
    for c in df.columns:
        lc = c.lower().strip()
        if   lc in ("order_id","orderid"):           col_map[c] = "Order_Id"
        elif lc in ("res_id","restaurant_id"):       col_map[c] = "Res_id"
        elif lc in ("res_name","restaurant_name"):   col_map[c] = "Res_name"
        elif lc in ("date","order_date"):            col_map[c] = "Date"
        elif lc in ("delivery_rating",):             col_map[c] = "Delivery_Rating"
        elif lc in ("food_rating","rating"):         col_map[c] = "Food_Rating"
        elif lc in ("comments","review","comment"):  col_map[c] = "Comments"
    df = df.rename(columns=col_map)

    for col in ["Order_Id","Res_id","Res_name","Date","Food_Rating","Comments"]:
        if col not in df.columns: df[col] = None

    df["Food_Rating"] = pd.to_numeric(df["Food_Rating"], errors="coerce")
    df["Comments"]    = df["Comments"].fillna("").astype(str).str.strip()
    df["Res_name"]    = df["Res_name"].fillna("Unknown").str.strip().replace(BRAND_ALIASES)
    df["Date"]        = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
    df["Week"]        = df["Date"].dt.day.apply(lambda d: get_week(int(d)) if pd.notna(d) else "W1")
    df["Source"]      = "swiggy" if "swiggy" in os.path.basename(f).lower() else "zomato"
    frames.append(df)
    print(f"    {len(df):,} rows")

df = pd.concat(frames, ignore_index=True)
print(f"\n  Total rows: {len(df):,}")
print(f"  Classifying... (this takes 30-60 seconds)")

classified     = df.apply(lambda r: classify(r["Comments"], r["Food_Rating"]), axis=1)
df["Topic"]    = classified.apply(lambda x: x[0])
df["Subtopic"] = classified.apply(lambda x: x[1])

df.to_pickle(out_path)
sz = os.path.getsize(out_path) / 1024 / 1024
print(f"\n  Saved: {out_path}")
print(f"  Size : {sz:.1f} MB")
print(f"  Rows with comments: {(df['Comments']!='').sum():,}")
print(f"  Unique brands: {df['Res_name'].nunique()}")
print(f"\n  Done. Restart the server to load the new data.")

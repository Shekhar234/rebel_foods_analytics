"""
Cloud Kitchen Review Analytics — Flask Backend
First run: classifies CSV and saves reviews.pkl locally (takes ~60s)
Subsequent runs: loads pkl instantly (~1s)
The pkl is machine-local — never ship it across machines.
"""
import os, glob, sys
from flask import Flask, jsonify, render_template, request
import pandas as pd
from classifier import classify, TOPIC_COLORS, TOPIC_ORDER

app = Flask(__name__)

@app.after_request
def no_cache(r):
    r.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    r.headers["Pragma"]  = "no-cache"
    r.headers["Expires"] = "0"
    return r

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR   = os.path.join(SCRIPT_DIR, "data")
PKL_PATH   = os.path.join(DATA_DIR, "reviews_local.pkl")   # local only, never committed

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

def get_week(day):
    if day <= 7:  return "W1"
    if day <= 14: return "W2"
    return "W3"

def classify_from_csv():
    """Load CSV(s) from data/ folder and classify. Returns DataFrame."""
    # Prefer enriched CSV (has City, Region, Vendor, Order_Value_INR pre-added)
    enriched = os.path.join(DATA_DIR, "reviews_enriched.csv")
    if os.path.exists(enriched):
        files = [enriched]
        print(f"  Using enriched dataset: reviews_enriched.csv")
    else:
        files = [f for f in glob.glob(os.path.join(DATA_DIR, "*.csv"))
                 if os.path.getsize(f) > 10_000 and "enriched" not in f]
    if not files:
        print("  ERROR: No CSV files found in data/ folder.")
        print(f"  Expected location: {DATA_DIR}")
        return None

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
        print(f"    {len(df):,} rows, {len(df.columns)} columns")

    df = pd.concat(frames, ignore_index=True)
    print(f"\n  Total: {len(df):,} rows")
    print(f"  Classifying reviews (30-60 seconds for large files)...")
    sys.stdout.flush()

    classified     = df.apply(lambda r: classify(r["Comments"], r["Food_Rating"]), axis=1)
    df["Topic"]    = classified.apply(lambda x: x[0])
    df["Subtopic"] = classified.apply(lambda x: x[1])

    # Save locally so next startup is instant — this pkl stays on this machine only
    try:
        df.to_pickle(PKL_PATH)
        sz = os.path.getsize(PKL_PATH) / 1024 / 1024
        print(f"  Saved local cache: reviews_local.pkl ({sz:.1f} MB)")
        print(f"  Next startup will load instantly from cache.")
    except Exception as e:
        print(f"  Could not save cache (will re-classify next time): {e}")

    return df

def load_df():
    # Try local pkl first — but only if it was built on THIS machine
    if os.path.exists(PKL_PATH):
        print(f"  Found local cache (reviews_local.pkl) — loading...")
        try:
            df = pd.read_pickle(PKL_PATH)
            print(f"  Loaded {len(df):,} rows from cache.")
            return df
        except Exception as e:
            print(f"  Cache load failed ({e})")
            print(f"  Deleting bad cache and re-classifying from CSV...")
            try: os.remove(PKL_PATH)
            except: pass

    # No cache or bad cache — classify from CSV
    print("  No local cache found — loading and classifying CSV...")
    return classify_from_csv()

print("\n" + "="*55)
print("  Cloud Kitchen Analytics — starting up")
print("="*55)
DF = load_df()

if DF is None or len(DF) == 0:
    print("\n  WARNING: No data loaded. Dashboard will be empty.")
    print(f"  Add CSV files to: {DATA_DIR}")
    DF = pd.DataFrame(columns=["Order_Id","Res_id","Res_name","Date",
                                "Food_Rating","Comments","Source","Week",
                                "Topic","Subtopic"])
else:
    print(f"\n  Ready: {len(DF):,} rows | "
          f"{(DF['Comments']!='').sum():,} with comments | "
          f"{DF['Res_name'].nunique()} brands\n")

# ── Helpers ───────────────────────────────────────────────────────────────────
def safe_int(v):
    try: return int(v)
    except: return 0

def safe_float(v):
    try:
        f = float(v)
        return round(f, 2) if not pd.isna(f) else None
    except: return None

# ── Routes ────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/debug")
def debug():
    csv_files = [f for f in glob.glob(os.path.join(DATA_DIR,"*.csv")) if os.path.getsize(f)>10_000]
    return jsonify({
        "total_rows"         : len(DF),
        "rows_with_comments" : safe_int((DF["Comments"]!="").sum()) if len(DF) else 0,
        "unique_brands"      : sorted(DF["Res_name"].unique().tolist()) if len(DF) else [],
        "csv_files"          : [os.path.basename(f) for f in csv_files],
        "local_cache_exists" : os.path.exists(PKL_PATH),
        "data_dir"           : DATA_DIR,
        "columns"            : list(DF.columns),
    })

@app.route("/api/summary")
def summary():
    total         = len(DF)
    with_comments = safe_int((DF["Comments"]!="").sum())
    has_comment   = DF[DF["Comments"]!=""]
    topic_rows    = []
    for topic in TOPIC_ORDER + ["No Comment"]:
        t_df  = has_comment[has_comment["Topic"]==topic]
        count = len(t_df)
        if count == 0: continue
        pct = round(count/with_comments*100,1) if with_comments else 0
        subtopics = []
        for sub, s_df in t_df.groupby("Subtopic"):
            subtopics.append({"name":sub,"count":safe_int(len(s_df)),
                              "pct":round(len(s_df)/count*100,1)})
        subtopics.sort(key=lambda x:-x["count"])
        topic_rows.append({"topic":topic,"count":count,"pct":pct,
                           "color":TOPIC_COLORS.get(topic,"#888"),
                           "subtopics":subtopics})
    return jsonify({"total":total,"with_comments":with_comments,
                    "topics":topic_rows,"colors":TOPIC_COLORS})

@app.route("/api/brands")
def brands():
    out         = {}
    has_comment = DF[DF["Comments"]!=""]
    for brand, grp in DF.groupby("Res_name"):
        commented   = has_comment[has_comment["Res_name"]==brand]
        n_commented = len(commented)
        weekly_avgs = {}
        for wk, w_grp in grp.groupby("Week"):
            weekly_avgs[wk] = safe_float(w_grp["Food_Rating"].mean())
        topics_out = []
        for topic in TOPIC_ORDER:
            t_df = commented[commented["Topic"]==topic]
            if not len(t_df): continue
            subtopics = [{"name":s,"count":safe_int(len(sd))}
                         for s,sd in t_df.groupby("Subtopic")]
            subtopics.sort(key=lambda x:-x["count"])
            topics_out.append({"topic":topic,"count":safe_int(len(t_df)),
                               "pct":round(len(t_df)/n_commented*100,1) if n_commented else 0,
                               "subtopics":subtopics})
        out[brand] = {"count":safe_int(len(grp)),
                      "avg_rating":safe_float(grp["Food_Rating"].mean()),
                      "commented":n_commented,"weekly_avgs":weekly_avgs,
                      "topics":topics_out}
    return jsonify(out)

@app.route("/api/reviews")
def reviews():
    brand  = request.args.get("brand","")
    topic  = request.args.get("topic","")
    rating = request.args.get("rating","")
    page   = int(request.args.get("page",1))
    per    = 50
    q = DF[DF["Comments"]!=""].copy()
    if brand:  q = q[q["Res_name"]==brand]
    if topic:  q = q[q["Topic"]==topic]
    if rating:
        try: q = q[q["Food_Rating"]==float(rating)]
        except: pass
    total = len(q)
    q     = q.iloc[(page-1)*per:page*per]
    records = []
    for _, row in q.iterrows():
        records.append({
            "order_id": str(row.get("Order_Id","")),
            "brand":    str(row.get("Res_name","")),
            "date":     str(row["Date"].date()) if pd.notna(row.get("Date")) else "",
            "rating":   safe_float(row.get("Food_Rating")),
            "comment":  str(row.get("Comments",""))[:300],
            "topic":    str(row.get("Topic","")),
            "subtopic": str(row.get("Subtopic","")),
            "source":   str(row.get("Source","zomato")),
        })
    return jsonify({"total":total,"page":page,"per":per,"reviews":records})

@app.route("/api/brands_list")
def brands_list():
    return jsonify(sorted(DF["Res_name"].unique().tolist()))

@app.route("/api/topics_list")
def topics_list():
    return jsonify(TOPIC_ORDER)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"  Open: http://localhost:{port}")
    print(f"  Debug: http://localhost:{port}/api/debug\n")
    app.run(host="0.0.0.0", port=port, debug=False)

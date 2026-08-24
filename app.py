import os
import json
import math
import glob
import functools
import pandas as pd
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)
app.secret_key = "techno_warehouse_secret_2024"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SALES_DIR = os.path.join(BASE_DIR, "sales")
INVENTORY_DIR = os.path.join(BASE_DIR, "INVENTORY")

# ── Column constants ──────────────────────────────────────────────────────────
INV_SKU_COL       = "Each Client SKU ID"
INV_LOCATION_COL  = "Fulfillment Location Name"
INV_AVAIL_COL     = "Total Available Quantity"
INV_STYLE_COL     = "Style"
INV_COLOR_COL     = "Color"
INV_SIZE_COL      = "Size"
INV_CATEGORY_COL  = "Category"
INV_MRP_COL       = "MRP"

SALES_SKU_COL     = "SKU"
SALES_QTY_COL     = "SALE QTY"

WAREHOUSES = ["wms_bagalur", "wms_bhiwandi", "wms_ggn", "wms_kolkata"]
WH_LABELS  = {
    "wms_bagalur":  "Bagalur",
    "wms_bhiwandi": "Bhiwandi",
    "wms_ggn":      "Gurugram",
    "wms_kolkata":  "Kolkata",
}


# ── Data loaders ──────────────────────────────────────────────────────────────
def load_sales() -> pd.DataFrame:
    files = glob.glob(os.path.join(SALES_DIR, "*.xlsx")) + \
            glob.glob(os.path.join(SALES_DIR, "*.xls"))  + \
            glob.glob(os.path.join(SALES_DIR, "*.csv"))
    files = [f for f in files if not os.path.basename(f).startswith("~$")]
    if not files:
        raise FileNotFoundError("No valid sales file found in sales/ folder")
    f = files[0]
    df = pd.read_excel(f) if f.endswith((".xlsx", ".xls")) else pd.read_csv(f)
    return df[[SALES_SKU_COL, SALES_QTY_COL]].dropna(subset=[SALES_SKU_COL])


def load_inventory() -> pd.DataFrame:
    files = glob.glob(os.path.join(INVENTORY_DIR, "*.csv")) + \
            glob.glob(os.path.join(INVENTORY_DIR, "*.xlsx")) + \
            glob.glob(os.path.join(INVENTORY_DIR, "*.xls"))
    files = [f for f in files if not os.path.basename(f).startswith("~$")]
    if not files:
        raise FileNotFoundError("No valid inventory file found in INVENTORY/ folder")
    f = files[0]
    df = pd.read_csv(f) if f.endswith(".csv") else pd.read_excel(f)
    keep = [INV_SKU_COL, INV_LOCATION_COL, INV_AVAIL_COL,
            INV_STYLE_COL, INV_COLOR_COL, INV_SIZE_COL,
            INV_CATEGORY_COL, INV_MRP_COL]
    existing = [c for c in keep if c in df.columns]
    return df[existing]


# ── Core analytics ────────────────────────────────────────────────────────────
def classify_abc(df_sales: pd.DataFrame) -> pd.DataFrame:
    df = df_sales.groupby(SALES_SKU_COL, as_index=False)[SALES_QTY_COL].sum()
    df = df.sort_values(SALES_QTY_COL, ascending=False).reset_index(drop=True)
    total = df[SALES_QTY_COL].sum()
    df["cumulative_qty"] = df[SALES_QTY_COL].cumsum()
    df["cumulative_pct"] = (df["cumulative_qty"] / total * 100).round(2)
    df["sales_pct"]      = (df[SALES_QTY_COL] / total * 100).round(2)
    df["rank"]           = df.index + 1

    def cat(pct):
        if pct <= 50:  return "A"
        if pct <= 75:  return "B"
        return "C"

    df["category"] = df["cumulative_pct"].apply(cat)
    return df


def build_inventory_pivot(df_inv: pd.DataFrame) -> pd.DataFrame:
    """Pivot: rows=SKU, cols=warehouse, values=Total Available Qty"""
    df_pos = df_inv[df_inv[INV_AVAIL_COL] > 0].copy()
    pivot = df_pos.pivot_table(
        index=INV_SKU_COL,
        columns=INV_LOCATION_COL,
        values=INV_AVAIL_COL,
        aggfunc="sum",
        fill_value=0,
    ).reset_index()
    # Ensure all 4 WH columns exist
    for wh in WAREHOUSES:
        if wh not in pivot.columns:
            pivot[wh] = 0
    return pivot


def enrich_sku_meta(df_inv: pd.DataFrame) -> pd.DataFrame:
    """One row per SKU with style/color/size/category/MRP"""
    cols = [INV_SKU_COL]
    for c in [INV_STYLE_COL, INV_COLOR_COL, INV_SIZE_COL, INV_CATEGORY_COL, INV_MRP_COL]:
        if c in df_inv.columns:
            cols.append(c)
    return df_inv[cols].drop_duplicates(subset=[INV_SKU_COL])


@functools.lru_cache(maxsize=1)
def get_merged_data():
    df_sales = load_sales()
    df_inv   = load_inventory()
    abc_df   = classify_abc(df_sales)
    pivot    = build_inventory_pivot(df_inv)
    meta     = enrich_sku_meta(df_inv)

    merged = abc_df.merge(pivot, left_on=SALES_SKU_COL, right_on=INV_SKU_COL, how="left")
    for wh in WAREHOUSES:
        if wh not in merged.columns:
            merged[wh] = 0
        merged[wh] = merged[wh].fillna(0).astype(int)

    merged["total_stock"] = merged[[wh for wh in WAREHOUSES]].sum(axis=1)
    merged["wh_count"]    = (merged[[wh for wh in WAREHOUSES]] > 0).sum(axis=1)
    merged = merged.merge(meta, on=INV_SKU_COL, how="left")
    
    return merged, df_sales, df_inv



# ── Routes ────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/summary")
def api_summary():
    try:
        refresh = request.args.get("refresh", "false").lower() == "true"
        if refresh:
            get_merged_data.cache_clear()

        merged, df_sales, df_inv = get_merged_data()

        total_skus  = len(merged)
        total_sales = int(merged[SALES_QTY_COL].sum())
        total_wh    = len(WAREHOUSES)

        def cat_stats(df_cat, cat_name):
            n = len(df_cat)
            sales = int(df_cat[SALES_QTY_COL].sum())
            wh_dist = df_cat.groupby("wh_count").size().to_dict()
            dist_dict = {str(i): int(wh_dist.get(i, 0)) for i in range(5)}
            return {
                "count":          n,
                "sales":          sales,
                "sales_pct":      round(sales / total_sales * 100, 1) if total_sales else 0,
                "avg_wh":         round(df_cat["wh_count"].mean(), 1) if n > 0 else 0,
                "skus_all_wh":    int((df_cat["wh_count"] == total_wh).sum()),
                "skus_miss_wh":   int((df_cat["wh_count"] < total_wh).sum()),
                "total_stock":    int(df_cat["total_stock"].sum()),
                "wh_distribution": dist_dict,
            }

        cat_a = merged[merged["category"] == "A"]
        cat_b = merged[merged["category"] == "B"]
        cat_c = merged[merged["category"] == "C"]

        # Warehouse-wise stock totals
        wh_stock = {}
        for wh in WAREHOUSES:
            wh_stock[WH_LABELS[wh]] = int(df_inv[df_inv[INV_LOCATION_COL] == wh][INV_AVAIL_COL].sum())

        # Category-wise stock per warehouse
        cat_wh_stock = {}
        for cat_name, df_cat in [("A", cat_a), ("B", cat_b), ("C", cat_c)]:
            cat_wh_stock[cat_name] = {
                WH_LABELS[wh]: int(df_cat[wh].sum()) for wh in WAREHOUSES
            }

        # SKUs with zero inventory (in any WH) — gap analysis
        zero_stock = merged[merged["total_stock"] == 0]
        gap_a = zero_stock[zero_stock["category"] == "A"]

        summary = {
            "total_skus":     total_skus,
            "total_sales":    total_sales,
            "total_wh":       total_wh,
            "wh_labels":      WH_LABELS,
            "categories":     {
                "A": cat_stats(cat_a, "A"),
                "B": cat_stats(cat_b, "B"),
                "C": cat_stats(cat_c, "C"),
            },
            "wh_stock":       wh_stock,
            "cat_wh_stock":   cat_wh_stock,
            "zero_stock_count": int(len(zero_stock)),
            "gap_a_count":    int(len(gap_a)),
            "wh_distribution": (
                merged.groupby("wh_count").size()
                      .reset_index(name="sku_count")
                      .to_dict(orient="records")
            ),
        }
        return jsonify({"success": True, "summary": summary})
    except Exception as e:
        import traceback
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500


@app.route("/api/details")
def api_details():
    """Return paginated SKU detail records for a given category."""
    try:
        category = request.args.get("category", "A")
        page     = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 50))
        search   = request.args.get("search", "").strip().lower()
        wh_filter = request.args.get("wh_filter", "")

        merged, _, _ = get_merged_data()

        df_cat = merged[merged["category"] == category].copy()

        if search:
            df_cat = df_cat[df_cat[SALES_SKU_COL].astype(str).str.lower().str.contains(search)]

        # Calculate warehouse coverage distribution for this category
        wh_dist_counts = df_cat.groupby("wh_count").size().to_dict()
        wh_distribution = {str(i): int(wh_dist_counts.get(i, 0)) for i in range(5)}

        if wh_filter != "":
            df_cat = df_cat[df_cat["wh_count"] == int(wh_filter)]

        total_records = len(df_cat)
        
        start = (page - 1) * per_page
        df_page = df_cat.iloc[start: start + per_page]

        records = []
        for _, row in df_page.iterrows():
            rec = {
                "sku":           str(row[SALES_SKU_COL]),
                "rank":          int(row["rank"]),
                "sales_qty":     int(row[SALES_QTY_COL]),
                "sales_pct":     float(row["sales_pct"]),
                "cumulative_pct": float(row["cumulative_pct"]),
                "category":      row["category"],
                "wh_count":      int(row["wh_count"]),
                "total_stock":   int(row["total_stock"]),
                "coverage_pct":  round(int(row["wh_count"]) / len(WAREHOUSES) * 100, 1),
                "style":         "" if pd.isna(row.get(INV_STYLE_COL)) else str(row.get(INV_STYLE_COL, "")),
                "color":         "" if pd.isna(row.get(INV_COLOR_COL)) else str(row.get(INV_COLOR_COL, "")),
                "size":          "" if pd.isna(row.get(INV_SIZE_COL)) else str(row.get(INV_SIZE_COL, "")),
                "category_name": "" if pd.isna(row.get(INV_CATEGORY_COL)) else str(row.get(INV_CATEGORY_COL, "")),
                "mrp":           0.0 if pd.isna(row.get(INV_MRP_COL)) else float(row.get(INV_MRP_COL, 0) or 0),
            }
            for wh in WAREHOUSES:
                rec[WH_LABELS[wh]] = int(row[wh])
            records.append(rec)

        return jsonify({
            "success":       True,
            "records":       records,
            "total_records": total_records,
            "page":          page,
            "per_page":      per_page,
            "total_pages":   math.ceil(total_records / per_page),
            "wh_distribution": wh_distribution,
        })
    except Exception as e:
        import traceback
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500


from allocation_planner import process_allocation, process_boxwise_allocation
from flask import send_file

@app.route("/api/run_allocation")
def api_run_allocation():
    try:
        df_inv = load_inventory()
        # Ensure we have style, size, avail col
        if INV_STYLE_COL not in df_inv.columns or INV_SIZE_COL not in df_inv.columns:
            return jsonify({"error": "Inventory data missing Style or Size columns."}), 400
            
        group_cols = [INV_SKU_COL, INV_STYLE_COL, INV_COLOR_COL, INV_SIZE_COL]
        group_cols = [c for c in group_cols if c in df_inv.columns]
            
        df_agg = df_inv.groupby(group_cols, as_index=False)[INV_AVAIL_COL].sum()
        
        # We need the NS/PS cap to apply per SKU variant (Style + Color)
        if INV_COLOR_COL in df_agg.columns:
            df_agg['Style_Color_Group'] = df_agg[INV_STYLE_COL].astype(str) + "_" + df_agg[INV_COLOR_COL].astype(str)
            group_col = 'Style_Color_Group'
        else:
            group_col = INV_STYLE_COL
            
        allocated_df = process_allocation(df_agg, style_col=group_col, size_col=INV_SIZE_COL, qty_col=INV_AVAIL_COL)
        
        if 'Style_Color_Group' in allocated_df.columns:
            allocated_df = allocated_df.drop(columns=['Style_Color_Group'])
        
        # Calculate summary stats
        total_qty = int(allocated_df[INV_AVAIL_COL].sum()) if not allocated_df.empty else 0
        bagalur_qty = int(allocated_df['Bagalur'].sum()) if not allocated_df.empty else 0
        bhiwandi_qty = int(allocated_df['Bhiwandi'].sum()) if not allocated_df.empty else 0
        kolkata_qty = int(allocated_df['Kolkata'].sum()) if not allocated_df.empty else 0
        gurgaon_qty = int(allocated_df['Gurgaon'].sum()) if not allocated_df.empty else 0
        
        output_path = os.path.join(BASE_DIR, "allocation_output.csv")
        allocated_df.to_csv(output_path, index=False)
        
        summary = {
            "total_processed": total_qty,
            "bagalur_final": bagalur_qty,
            "bhiwandi_final": bhiwandi_qty,
            "kolkata_final": kolkata_qty,
            "gurgaon_final": gurgaon_qty
        }
        
        return jsonify({"success": True, "summary": summary})
    except Exception as e:
        import traceback
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500


@app.route("/api/run_boxwise_allocation")
def api_run_boxwise_allocation():
    try:
        df_inv = load_inventory()
        if INV_STYLE_COL not in df_inv.columns or INV_SIZE_COL not in df_inv.columns:
            return jsonify({"error": "Inventory data missing Style or Size columns."}), 400

        group_cols = [INV_SKU_COL, INV_STYLE_COL, INV_COLOR_COL, INV_SIZE_COL]
        group_cols = [c for c in group_cols if c in df_inv.columns]

        df_agg = df_inv.groupby(group_cols, as_index=False)[INV_AVAIL_COL].sum()
        df_agg['Grand Total'] = df_agg[INV_AVAIL_COL]
        df_agg['PER BOX QTY'] = 10  # Standard template per-box quantity

        allocated_df = process_boxwise_allocation(
            df_agg,
            style_col=INV_STYLE_COL if INV_STYLE_COL in df_agg.columns else 'Style',
            color_col=INV_COLOR_COL if INV_COLOR_COL in df_agg.columns else 'Color',
            size_col=INV_SIZE_COL,
            qty_col='Grand Total',
            per_box_col='PER BOX QTY'
        )

        total_qty = int(allocated_df['Grand Total'].sum()) if not allocated_df.empty else 0
        bagalur_qty = int(allocated_df['Bagalur'].sum()) if not allocated_df.empty else 0
        bhiwandi_qty = int(allocated_df['Bhiwandi'].sum()) if not allocated_df.empty else 0
        kolkata_qty = int(allocated_df['Kolkata'].sum()) if not allocated_df.empty else 0
        gurgaon_qty = int(allocated_df['Gurgaon'].sum()) if not allocated_df.empty else 0

        total_boxes = round(float(allocated_df['TOTAL BOX'].sum()), 1) if not allocated_df.empty else 0
        bagalur_boxes = round(float(allocated_df['Bagalur_Boxes'].sum()), 1) if not allocated_df.empty else 0
        bhiwandi_boxes = round(float(allocated_df['Bhiwandi_Boxes'].sum()), 1) if not allocated_df.empty else 0
        kolkata_boxes = round(float(allocated_df['Kolkata_Boxes'].sum()), 1) if not allocated_df.empty else 0
        gurgaon_boxes = round(float(allocated_df['Gurgaon_Boxes'].sum()), 1) if not allocated_df.empty else 0

        output_path = os.path.join(BASE_DIR, "allocation_output.csv")
        allocated_df.to_csv(output_path, index=False)

        summary = {
            "total_processed": total_qty,
            "total_boxes": total_boxes,
            "bagalur_final": bagalur_qty,
            "bagalur_boxes": bagalur_boxes,
            "bhiwandi_final": bhiwandi_qty,
            "bhiwandi_boxes": bhiwandi_boxes,
            "kolkata_final": kolkata_qty,
            "kolkata_boxes": kolkata_boxes,
            "gurgaon_final": gurgaon_qty,
            "gurgaon_boxes": gurgaon_boxes,
            "mode": "Box-Wise Allocation"
        }

        return jsonify({"success": True, "summary": summary})
    except Exception as e:
        import traceback
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500

@app.route("/api/validation")
def api_validation():
    try:
        merged, df_sales, df_inv = get_merged_data()
        
        # Load allocation output if it exists
        alloc_path = os.path.join(BASE_DIR, "reports", "allocation_report.csv")
        alloc_skus = set()
        if os.path.exists(alloc_path):
            alloc_df = pd.read_csv(alloc_path)
            if INV_SKU_COL in alloc_df.columns:
                alloc_skus = set(alloc_df[INV_SKU_COL].unique())
                alloc_wh_cols = [WH_LABELS[wh] for wh in WAREHOUSES]
                alloc_wh_cols = [c for c in alloc_wh_cols if c in alloc_df.columns]
                
                alloc_agg = alloc_df.groupby(INV_SKU_COL)[alloc_wh_cols].sum().reset_index()
                
                rename_map = {WH_LABELS[wh]: f"{wh}_alloc" for wh in WAREHOUSES if WH_LABELS[wh] in alloc_wh_cols}
                alloc_agg = alloc_agg.rename(columns=rename_map)
                merged = merged.merge(alloc_agg, on=INV_SKU_COL, how="left")
                
        # Load transit output if it exists
        transit_path = os.path.join(BASE_DIR, "reports", "intransit_report.csv")
        if os.path.exists(transit_path):
            transit_df = pd.read_csv(transit_path)
            if INV_SKU_COL in transit_df.columns:
                transit_wh_cols = [WH_LABELS[wh] for wh in WAREHOUSES]
                transit_wh_cols = [c for c in transit_wh_cols if c in transit_df.columns]
                
                transit_agg = transit_df.groupby(INV_SKU_COL)[transit_wh_cols].sum().reset_index()
                
                rename_map = {WH_LABELS[wh]: f"{wh}_transit" for wh in WAREHOUSES if WH_LABELS[wh] in transit_wh_cols}
                transit_agg = transit_agg.rename(columns=rename_map)
                merged = merged.merge(transit_agg, on=INV_SKU_COL, how="left")
                
        # Fill missing allocation and transit with 0
        for wh in WAREHOUSES:
            alloc_col = f"{wh}_alloc"
            if alloc_col not in merged.columns:
                merged[alloc_col] = 0
            merged[alloc_col] = merged[alloc_col].fillna(0).astype(int)
            
            transit_col = f"{wh}_transit"
            if transit_col not in merged.columns:
                merged[transit_col] = 0
            merged[transit_col] = merged[transit_col].fillna(0).astype(int)
            
            # Projected Stock = Alloc + Transit (if allocated) OR Current + Transit (if no alloc data)
            merged[f"{wh}_projected"] = merged.apply(
                lambda r: r[alloc_col] + r[transit_col] if r[INV_SKU_COL] in alloc_skus else r[wh] + r[transit_col], 
                axis=1
            )

        # Calculate WH Counts for different views
        current_wh_cols = [wh for wh in WAREHOUSES]
        transit_wh_cols = [f"{wh}_with_transit" for wh in WAREHOUSES]
        projected_wh_cols = [f"{wh}_projected" for wh in WAREHOUSES]
        
        for wh in WAREHOUSES:
            merged[f"{wh}_with_transit"] = merged[wh] + merged[f"{wh}_transit"]
            
        merged["current_wh_count_calc"] = (merged[current_wh_cols] > 0).sum(axis=1)
        merged["transit_wh_count"] = (merged[transit_wh_cols] > 0).sum(axis=1)
        merged["projected_wh_count"] = (merged[projected_wh_cols] > 0).sum(axis=1)

        # Build response
        records = []
        for _, row in merged.iterrows():
            rec = {
                "sku": str(row[SALES_SKU_COL]),
                "category": row["category"],
                "style": str(row.get(INV_STYLE_COL, "")),
                "current_wh_count": int(row["current_wh_count_calc"]),
                "projected_wh_count": int(row["projected_wh_count"])
            }
            # Add per-warehouse stats
            wh_stats = {}
            for wh in WAREHOUSES:
                wh_label = WH_LABELS[wh]
                wh_stats[wh_label] = {
                    "current": int(row[wh]),
                    "alloc": int(row[f"{wh}_alloc"]),
                    "transit": int(row[f"{wh}_transit"]),
                    "projected": int(row[f"{wh}_projected"])
                }
            rec["warehouses"] = wh_stats
            records.append(rec)
            
        # Category summaries for three views
        current_summary = {}
        transit_summary = {}
        projected_summary = {}
        
        for cat in ["A", "B", "C"]:
            df_cat = merged[merged["category"] == cat]
            
            c_dist = df_cat.groupby("current_wh_count_calc").size().to_dict()
            current_summary[cat] = {str(i): int(c_dist.get(i, 0)) for i in range(5)}
            
            t_dist = df_cat.groupby("transit_wh_count").size().to_dict()
            transit_summary[cat] = {str(i): int(t_dist.get(i, 0)) for i in range(5)}
            
            p_dist = df_cat.groupby("projected_wh_count").size().to_dict()
            projected_summary[cat] = {str(i): int(p_dist.get(i, 0)) for i in range(5)}

        def get_insights(df, count_col, wh_cols):
            insights = {}
            for cat in ["A", "B", "C"]:
                df_cat = df[df["category"] == cat]
                n = len(df_cat)
                sales = int(df_cat[SALES_QTY_COL].sum()) if SALES_QTY_COL in df_cat.columns else 0
                avg_wh = round(df_cat[count_col].mean(), 1) if n > 0 else 0
                total_stock = int(df_cat[wh_cols].sum().sum())
                insights[cat] = {
                    "skus": n,
                    "sales": sales,
                    "avg_wh": avg_wh,
                    "total_stock": total_stock
                }
            return insights

        current_insights = get_insights(merged, "current_wh_count_calc", current_wh_cols)
        transit_insights = get_insights(merged, "transit_wh_count", transit_wh_cols)
        projected_insights = get_insights(merged, "projected_wh_count", projected_wh_cols)

        return jsonify({
            "success": True, 
            "records": records, 
            "current_category_summary": current_summary,
            "transit_category_summary": transit_summary,
            "projected_category_summary": projected_summary,
            "current_insights": current_insights,
            "transit_insights": transit_insights,
            "projected_insights": projected_insights
        })
    except Exception as e:
        import traceback
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500

@app.route("/api/download_allocation")
def api_download_allocation():
    output_path = os.path.join(BASE_DIR, "allocation_output.csv")
    if os.path.exists(output_path):
        return send_file(output_path, as_attachment=True)
    return "File not found", 404

if __name__ == "__main__":
    app.run(debug=True, port=1980)

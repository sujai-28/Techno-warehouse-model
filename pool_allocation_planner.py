import pandas as pd
import numpy as np

# Base Floor Thresholds for Bagalur Retention
EBO_BASE_FLOOR = 30
D2C_BASE_FLOOR = 20

# Regional 3PL Shares out of Total 36% Push Pool (17% Bhiwandi, 14% Kolkata, 5% Gurgaon)
BHIWANDI_SHARE = 17.0 / 36.0
KOLKATA_SHARE = 14.0 / 36.0
GURGAON_SHARE = 5.0 / 36.0


def calculate_pool_allocation(ebo_qty, d2c_qty=0):
    """
    Calculates pool-based allocation for a single SKU.
    
    Inputs:
        ebo_qty: Available stock in EBO pool for this SKU
        d2c_qty: Available stock in D2C pool for this SKU
        
    Steps:
    1. Total SKU Stock = ebo_qty + d2c_qty
    2. Base 64% / 36% Split:
       - Bagalur Base (64%)
       - 3PL Push Pool (36%)
    3. Sub-Split of 36% Push Pool:
       - EBO Pool Target Share = 60% of Push Pool
       - D2C Pool Target Share = 40% of Push Pool
    4. Base Floor Protection Checks:
       - EBO Floor Check: Bagalur MUST keep at least 30 pcs in EBO.
         If ebo_qty <= 30 => 0 transfer from EBO.
         If ebo_qty > 30 => EBO Transfer = MIN(EBO Target, ebo_qty - 30).
       - D2C Floor Check: Bagalur MUST keep at least 20 pcs in D2C.
         If d2c_qty <= 20 => 0 transfer from D2C.
         If d2c_qty > 20 => D2C Transfer = MIN(D2C Target, d2c_qty - 20).
    5. Final 3PL Regional Split (Bhiwandi 17%, Kolkata 14%, Gurgaon 5%):
       - Split Total Approved 3PL Transfer across Bhiwandi, Kolkata, and Gurgaon.
    """
    e_qty = max(0, int(ebo_qty))
    d_qty = max(0, int(d2c_qty))
    total_qty = e_qty + d_qty

    if total_qty == 0:
        return {
            'Total_Qty': 0, 'EBO_Qty': 0, 'D2C_Qty': 0,
            'Bagalur': 0, 'EBO_Transfer': 0, 'D2C_Transfer': 0,
            'Total_3PL_Transfer': 0, 'Bhiwandi': 0, 'Kolkata': 0, 'Gurgaon': 0
        }

    # Step 1: Base 64% / 36% Split
    bagalur_base = int(round(total_qty * 0.64))
    push_pool_36 = total_qty - bagalur_base

    # Step 2: Sub-Split 36% Push Pool into EBO (60%) and D2C (40%)
    ebo_target = int(round(push_pool_36 * 0.60))
    d2c_target = push_pool_36 - ebo_target

    # Step 3: Base Floor Protection Rules
    # EBO Pool Protection (Base = 30 pcs)
    if e_qty <= EBO_BASE_FLOOR:
        ebo_approved_transfer = 0
    else:
        max_allowable_ebo_push = e_qty - EBO_BASE_FLOOR
        ebo_approved_transfer = min(ebo_target, max_allowable_ebo_push)

    # D2C Pool Protection (Base = 20 pcs)
    if d_qty <= D2C_BASE_FLOOR:
        d2c_approved_transfer = 0
    else:
        max_allowable_d2c_push = d_qty - D2C_BASE_FLOOR
        d2c_approved_transfer = min(d2c_target, max_allowable_d2c_push)

    # Step 4: Total Approved 3PL Transfer & Bagalur Final Retained
    total_3pl_transfer = ebo_approved_transfer + d2c_approved_transfer
    bagalur_retained = total_qty - total_3pl_transfer

    # Step 5: Regional 3PL Split (Bhiwandi 17%, Kolkata 14%, Gurgaon 5%)
    if total_3pl_transfer > 0:
        raw_bhi = int(round(total_3pl_transfer * BHIWANDI_SHARE))
        raw_kol = int(round(total_3pl_transfer * KOLKATA_SHARE))
        raw_gur = total_3pl_transfer - raw_bhi - raw_kol

        if raw_gur < 0:
            raw_bhi = max(0, raw_bhi + raw_gur)
            raw_gur = 0

        bhiwandi = raw_bhi
        kolkata = raw_kol
        gurgaon = raw_gur
    else:
        bhiwandi = 0
        kolkata = 0
        gurgaon = 0

    return {
        'Total_Qty': total_qty,
        'EBO_Qty': e_qty,
        'D2C_Qty': d_qty,
        'Bagalur': bagalur_retained,
        'EBO_Transfer': ebo_approved_transfer,
        'D2C_Transfer': d2c_approved_transfer,
        'Total_3PL_Transfer': total_3pl_transfer,
        'Bhiwandi': bhiwandi,
        'Kolkata': kolkata,
        'Gurgaon': gurgaon
    }


def process_pool_dataframe(df, sku_col='SKU', ebo_col='EBO_Qty', d2c_col='D2C_Qty'):
    """
    Processes a DataFrame of SKU records with EBO and D2C inventory quantities.
    """
    df_out = df.copy()
    
    if ebo_col not in df_out.columns:
        df_out[ebo_col] = 0
    if d2c_col not in df_out.columns:
        df_out[d2c_col] = 0

    n = len(df_out)
    tot_arr = np.zeros(n, dtype=np.int64)
    bag_arr = np.zeros(n, dtype=np.int64)
    ebo_tr_arr = np.zeros(n, dtype=np.int64)
    d2c_tr_arr = np.zeros(n, dtype=np.int64)
    tot_3pl_arr = np.zeros(n, dtype=np.int64)
    bhi_arr = np.zeros(n, dtype=np.int64)
    kol_arr = np.zeros(n, dtype=np.int64)
    gur_arr = np.zeros(n, dtype=np.int64)

    ebo_vals = df_out[ebo_col].fillna(0).to_numpy()
    d2c_vals = df_out[d2c_col].fillna(0).to_numpy()

    for i in range(n):
        alloc = calculate_pool_allocation(ebo_vals[i], d2c_vals[i])
        tot_arr[i] = alloc['Total_Qty']
        bag_arr[i] = alloc['Bagalur']
        ebo_tr_arr[i] = alloc['EBO_Transfer']
        d2c_tr_arr[i] = alloc['D2C_Transfer']
        tot_3pl_arr[i] = alloc['Total_3PL_Transfer']
        bhi_arr[i] = alloc['Bhiwandi']
        kol_arr[i] = alloc['Kolkata']
        gur_arr[i] = alloc['Gurgaon']

    df_out['Total_Qty'] = tot_arr
    df_out['Bagalur'] = bag_arr
    df_out['EBO_Transfer'] = ebo_tr_arr
    df_out['D2C_Transfer'] = d2c_tr_arr
    df_out['Total_3PL_Transfer'] = tot_3pl_arr
    df_out['Bhiwandi'] = bhi_arr
    df_out['Kolkata'] = kol_arr
    df_out['Gurgaon'] = gur_arr

    return df_out


def process_inventory_file(csv_path, output_csv="reports/pool_allocation_report.csv"):
    """
    Parses an OMS Inventory CSV file, filters for 'wms_bagalur',
    extracts EBO and Common Pool (Tiruppur) quantities per SKU,
    runs the pool allocation engine, and exports the final report.
    """
    df = pd.read_csv(csv_path)
    
    # Filter for wms_bagalur
    bagalur_df = df[df['Fulfillment Location Name'] == 'wms_bagalur'].copy()

    # Identify SKU column
    sku_col = 'Each Client SKU ID' if 'Each Client SKU ID' in df.columns else 'Client SKU Id / EAN'
    qty_col = 'Total Available Quantity'
    pool_col = 'Reservation Pool'

    # Filter for the two reservation pools
    common_pool_name = 'Common_Pool-TECHNO SPORTSWEAR PRIVATE LIMITED-wms_tiruppur'

    ebo_sub = bagalur_df[bagalur_df[pool_col] == 'EBO'].groupby(sku_col)[qty_col].sum().reset_index().rename(columns={qty_col: 'EBO_Qty'})
    common_sub = bagalur_df[bagalur_df[pool_col] == common_pool_name].groupby(sku_col)[qty_col].sum().reset_index().rename(columns={qty_col: 'D2C_Qty'})

    merged = pd.merge(ebo_sub, common_sub, on=sku_col, how='outer').fillna(0)
    merged = merged.rename(columns={sku_col: 'SKU'})

    allocated_df = process_pool_dataframe(merged, sku_col='SKU', ebo_col='EBO_Qty', d2c_col='D2C_Qty')

    if output_csv:
        import os
        os.makedirs(os.path.dirname(output_csv), exist_ok=True)
        allocated_df.to_csv(output_csv, index=False)
        print(f"Pool Allocation Report successfully saved to: {output_csv}")

    return allocated_df


if __name__ == "__main__":
    import os
    download_path = r"D:\downloads\Inventory Available for Sales - OMS-2026-09-10T12_10_26.033+05_30.csv"
    if os.path.exists(download_path):
        print(f"Processing downloaded inventory file: {download_path}")
        result = process_inventory_file(download_path)
        print(f"\n--- POOL ALLOCATION SUMMARY ---")
        print(f"Total Unique SKUs Processed: {len(result):,}")
        print(f"Total Available Stock:       {result['Total_Qty'].sum():,}")
        print(f"Bagalur Retained Stock:      {result['Bagalur'].sum():,}")
        print(f"EBO Approved Transfer:       {result['EBO_Transfer'].sum():,}")
        print(f"D2C Approved Transfer:       {result['D2C_Transfer'].sum():,}")
        print(f"Total 3PL Transfer Pool:     {result['Total_3PL_Transfer'].sum():,}")
        print(f"Bhiwandi Allocation (17%):   {result['Bhiwandi'].sum():,}")
        print(f"Kolkata Allocation (14%):    {result['Kolkata'].sum():,}")
        print(f"Gurgaon Allocation (5%):     {result['Gurgaon'].sum():,}")
    else:
        sample_df = pd.DataFrame([
            {'SKU': 'OR10BLKMED', 'EBO_Qty': 120, 'D2C_Qty': 80},
            {'SKU': 'OR10BLKMED', 'EBO_Qty': 60,  'D2C_Qty': 40},
            {'SKU': 'OR10BLKMED', 'EBO_Qty': 34,  'D2C_Qty': 0},
            {'SKU': 'OR10BLKMED', 'EBO_Qty': 28,  'D2C_Qty': 0},
            {'SKU': 'OR20REDLRG', 'EBO_Qty': 0,   'D2C_Qty': 25},
            {'SKU': 'OR20REDLRG', 'EBO_Qty': 0,   'D2C_Qty': 18},
        ])
        result = process_pool_dataframe(sample_df)
        print("=== POOL ALLOCATION PLANNER VERIFICATION ===")
        print(result.to_string(index=False))


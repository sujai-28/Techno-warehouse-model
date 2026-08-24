import pandas as pd
import numpy as np

# Configuration for Min/Max Caps
MENS_SIZE_CAPS = {
    'S':   {'MAX': {'Kolkata': 15, 'Bhiwandi': 15, 'Gurgaon': 10}, 'MIN': {'Kolkata': 5, 'Bhiwandi': 5, 'Gurgaon': 5}},
    'M':   {'MAX': {'Kolkata': 20, 'Bhiwandi': 20, 'Gurgaon': 15}, 'MIN': {'Kolkata': 5, 'Bhiwandi': 5, 'Gurgaon': 5}},
    'L':   {'MAX': {'Kolkata': 30, 'Bhiwandi': 30, 'Gurgaon': 20}, 'MIN': {'Kolkata': 5, 'Bhiwandi': 5, 'Gurgaon': 5}},
    'XL':  {'MAX': {'Kolkata': 30, 'Bhiwandi': 30, 'Gurgaon': 20}, 'MIN': {'Kolkata': 5, 'Bhiwandi': 5, 'Gurgaon': 5}},
    '2XL': {'MAX': {'Kolkata': 20, 'Bhiwandi': 20, 'Gurgaon': 10}, 'MIN': {'Kolkata': 5, 'Bhiwandi': 5, 'Gurgaon': 5}},
    '3XL': {'MAX': {'Kolkata': 10, 'Bhiwandi': 10, 'Gurgaon': 0},  'MIN': {'Kolkata': 3, 'Bhiwandi': 3, 'Gurgaon': 0}},
    '4XL': {'MAX': {'Kolkata': 5,  'Bhiwandi': 5,  'Gurgaon': 0},  'MIN': {'Kolkata': 2, 'Bhiwandi': 2, 'Gurgaon': 0}},
    '5XL': {'MAX': {'Kolkata': 5,  'Bhiwandi': 5,  'Gurgaon': 0},  'MIN': {'Kolkata': 2, 'Bhiwandi': 2, 'Gurgaon': 0}}
}

WOMENS_SIZE_CAPS = {
    'S':   {'MAX': {'Kolkata': 10, 'Bhiwandi': 10, 'Gurgaon': 5},  'MIN': {'Kolkata': 3, 'Bhiwandi': 3, 'Gurgaon': 3}},
    'M':   {'MAX': {'Kolkata': 15, 'Bhiwandi': 15, 'Gurgaon': 10}, 'MIN': {'Kolkata': 3, 'Bhiwandi': 3, 'Gurgaon': 3}},
    'L':   {'MAX': {'Kolkata': 20, 'Bhiwandi': 20, 'Gurgaon': 15}, 'MIN': {'Kolkata': 3, 'Bhiwandi': 3, 'Gurgaon': 3}},
    'XL':  {'MAX': {'Kolkata': 20, 'Bhiwandi': 20, 'Gurgaon': 15}, 'MIN': {'Kolkata': 3, 'Bhiwandi': 3, 'Gurgaon': 3}},
    '2XL': {'MAX': {'Kolkata': 10, 'Bhiwandi': 10, 'Gurgaon': 5},  'MIN': {'Kolkata': 3, 'Bhiwandi': 3, 'Gurgaon': 3}},
    '3XL': {'MAX': {'Kolkata': 0,  'Bhiwandi': 0,  'Gurgaon': 0},  'MIN': {'Kolkata': 0, 'Bhiwandi': 0, 'Gurgaon': 0}},
    '4XL': {'MAX': {'Kolkata': 0,  'Bhiwandi': 0,  'Gurgaon': 0},  'MIN': {'Kolkata': 0, 'Bhiwandi': 0, 'Gurgaon': 0}},
    '5XL': {'MAX': {'Kolkata': 0,  'Bhiwandi': 0,  'Gurgaon': 0},  'MIN': {'Kolkata': 0, 'Bhiwandi': 0, 'Gurgaon': 0}}
}

OVERALL_CAPS = {
    'NS': {'MAX': {'Kolkata': 115, 'Bhiwandi': 115, 'Gurgaon': 75}, 'MIN': {'Kolkata': 25, 'Bhiwandi': 25, 'Gurgaon': 25}},
    'PS': {'MAX': {'Kolkata': 20,  'Bhiwandi': 20,  'Gurgaon': 0},  'MIN': {'Kolkata': 7,  'Bhiwandi': 7,  'Gurgaon': 0}}
}

WOMENS_OVERALL_CAPS = {
    'NS': {'MAX': {'Kolkata': 115, 'Bhiwandi': 115, 'Gurgaon': 75}, 'MIN': {'Kolkata': 3, 'Bhiwandi': 3, 'Gurgaon': 3}},
    'PS': {'MAX': {'Kolkata': 20,  'Bhiwandi': 20,  'Gurgaon': 0},  'MIN': {'Kolkata': 0, 'Bhiwandi': 0, 'Gurgaon': 0}}
}

NS_SIZES = ['S', 'M', 'L', 'XL', '2XL']
PS_SIZES = ['3XL', '4XL', '5XL']

PRIORITY_ORDER = ['Bhiwandi', 'Kolkata', 'Gurgaon']

# Box-Wise Template Rules (from Warehouse_Allocation_Template)
BOXWISE_SIZE_RULES = {
    'SML': {'Kolkata': 15, 'Bhiwandi': 15, 'Gurgaon': 10},
    'MED': {'Kolkata': 20, 'Bhiwandi': 20, 'Gurgaon': 15},
    'LAR': {'Kolkata': 30, 'Bhiwandi': 30, 'Gurgaon': 25},
    'XLR': {'Kolkata': 30, 'Bhiwandi': 30, 'Gurgaon': 25},
    '2XL': {'Kolkata': 20, 'Bhiwandi': 20, 'Gurgaon': 15},
    '3XL': {'Kolkata': 5,  'Bhiwandi': 5,  'Gurgaon': 2},
    '4XL': {'Kolkata': 5,  'Bhiwandi': 5,  'Gurgaon': 2},
    '5XL': {'Kolkata': 5,  'Bhiwandi': 5,  'Gurgaon': 2},
    '06Y': {'Kolkata': 8,  'Bhiwandi': 6,  'Gurgaon': 6},
    '08Y': {'Kolkata': 8,  'Bhiwandi': 6,  'Gurgaon': 6},
    '10Y': {'Kolkata': 8,  'Bhiwandi': 6,  'Gurgaon': 6},
    '12Y': {'Kolkata': 10, 'Bhiwandi': 8,  'Gurgaon': 6},
    '14Y': {'Kolkata': 10, 'Bhiwandi': 8,  'Gurgaon': 6},
    '16Y': {'Kolkata': 10, 'Bhiwandi': 8,  'Gurgaon': 6},
}

SIZE_TO_RULE_KEY = {
    'S': 'SML', 'SML': 'SML',
    'M': 'MED', 'MED': 'MED',
    'L': 'LAR', 'LAR': 'LAR',
    'XL': 'XLR', 'XLR': 'XLR',
    '2XL': '2XL', 'XXL': '2XL',
    '3XL': '3XL', 'XXXL': '3XL',
    '4XL': '4XL', '5XL': '5XL',
    '06Y': '06Y', '6Y': '06Y', '6 Y': '06Y', '30': '06Y',
    '08Y': '08Y', '8Y': '08Y', '8 Y': '08Y', '32': '08Y',
    '10Y': '10Y', '10Y': '10Y', '10 Y': '10Y', '34': '10Y',
    '12Y': '12Y', '12Y': '12Y', '12 Y': '12Y', '36': '12Y',
    '14Y': '14Y', '14Y': '14Y', '14 Y': '14Y', '38': '14Y',
    '16Y': '16Y', '16Y': '16Y', '16 Y': '16Y',
}


def allocate_sku(size, total_qty, gender='M'):
    """
    Allocates total_qty of a specific size across the warehouses.
    Returns a dictionary of allocations.
    gender: 'M' (Mens), 'W' (Womens), 'B' (Kids), 'U' (Unisex)
    """
    caps = WOMENS_SIZE_CAPS if gender in ['W', 'B'] else MENS_SIZE_CAPS
    
    if size not in caps:
        # If size is not standard, default to all in Bagalur
        return {'Bagalur': total_qty, 'Bhiwandi': 0, 'Kolkata': 0, 'Gurgaon': 0}

    # 1. Raw Split
    bagalur_retained = int(round(total_qty * 0.6))
    push_pool = total_qty - bagalur_retained

    raw_bhi = int(round(total_qty * 0.2))
    raw_kol = int(round(total_qty * 0.15))
    raw_gur = push_pool - raw_bhi - raw_kol

    alloc = {
        'Bhiwandi': raw_bhi,
        'Kolkata': raw_kol,
        'Gurgaon': max(0, raw_gur) # Prevent negative if rounding goes weird
    }
    
    bagalur_final = bagalur_retained

    # Fix total allocation if raw_gur was negative and adjusted
    allocated_push = alloc['Bhiwandi'] + alloc['Kolkata'] + alloc['Gurgaon']
    if allocated_push != push_pool:
        # Adjust Bhiwandi as it's P1 to absorb minor rounding errors
        diff = push_pool - allocated_push
        alloc['Bhiwandi'] += diff
        
    # 2. Apply MAX Caps
    for wh in PRIORITY_ORDER:
        max_val = caps[size]['MAX'][wh]
        if alloc[wh] > max_val:
            excess = alloc[wh] - max_val
            alloc[wh] = max_val
            bagalur_final += excess

    # 3. Apply MIN Caps (No Re-allocation)
    for target_wh in PRIORITY_ORDER:
        min_val = caps[size]['MIN'][target_wh]
        if alloc[target_wh] < min_val:
            bagalur_final += alloc[target_wh]
            alloc[target_wh] = 0

    return {
        'Bagalur': bagalur_final,
        'Bhiwandi': alloc['Bhiwandi'],
        'Kolkata': alloc['Kolkata'],
        'Gurgaon': alloc['Gurgaon']
    }


def process_allocation(df, style_col='Style', size_col='Size', qty_col='Total_Qty'):
    """
    Processes a DataFrame containing inventory data and calculates allocations.
    Applies overall NS/PS MIN caps at the style level.
    """
    df_out = df.copy()
    
    SIZE_MAP = {
        'SML': 'S', 'S': 'S',
        'MED': 'M', 'M': 'M',
        'LAR': 'L', 'L': 'L',
        'XLR': 'XL', 'XL': 'XL',
        '2XL': '2XL', 'XXL': '2XL',
        '3XL': '3XL', 'XXXL': '3XL',
        '4XL': '4XL',
        '5XL': '5XL',
        # Kids Mappings
        '30': 'S', '6Y': 'S', '6 Y': 'S',
        '32': 'M', '8Y': 'M', '8 Y': 'M',
        '34': 'L', '10Y': 'L', '10 Y': 'L',
        '36': 'XL', '12Y': 'XL', '12 Y': 'XL',
        '38': '2XL', '14Y': '2XL', '14 Y': '2XL',
    }
    
    def clean_size(val):
        s = str(val).upper().strip()
        if s.startswith('0') and len(s) > 1 and s[1].isdigit():
            s = s.lstrip('0')
        return s

    mapped_sizes = df_out[size_col].apply(clean_size).map(lambda x: SIZE_MAP.get(x, x)).to_numpy()
    genders = df_out[style_col].astype(str).str.upper().str.strip().str[0].to_numpy()
    qtys = df_out[qty_col].to_numpy()
    n = len(df_out)

    bag_arr = np.zeros(n, dtype=np.int64)
    bhi_arr = np.zeros(n, dtype=np.int64)
    kol_arr = np.zeros(n, dtype=np.int64)
    gur_arr = np.zeros(n, dtype=np.int64)

    for i in range(n):
        alloc = allocate_sku(mapped_sizes[i], qtys[i], genders[i])
        bag_arr[i] = alloc['Bagalur']
        bhi_arr[i] = alloc['Bhiwandi']
        kol_arr[i] = alloc['Kolkata']
        gur_arr[i] = alloc['Gurgaon']

    df_out['Bagalur'] = bag_arr
    df_out['Bhiwandi'] = bhi_arr
    df_out['Kolkata'] = kol_arr
    df_out['Gurgaon'] = gur_arr

    # Assign _size_group for NS/PS check
    ns_sizes = set(NS_SIZES)
    ps_sizes = set(PS_SIZES)

    size_groups = np.full(n, 'OTHER', dtype=object)
    for i, s in enumerate(mapped_sizes):
        if s in ns_sizes:
            size_groups[i] = 'NS'
        elif s in ps_sizes:
            size_groups[i] = 'PS'

    df_out['_size_group'] = size_groups
    df_out['_gender'] = genders

    # Group by style_col and _size_group to find sums
    ns_ps_mask = (size_groups == 'NS') | (size_groups == 'PS')
    
    if np.any(ns_ps_mask):
        sub_df = df_out[ns_ps_mask]
        grp_sums = sub_df.groupby([style_col, '_size_group', '_gender'])[['Bhiwandi', 'Kolkata', 'Gurgaon']].sum().reset_index()

        revert_sets = {'Bhiwandi': set(), 'Kolkata': set(), 'Gurgaon': set()}
        for _, row in grp_sums.iterrows():
            st = row[style_col]
            sg = row['_size_group']
            gen = row['_gender']
            caps = WOMENS_OVERALL_CAPS if gen in ['W', 'B'] else OVERALL_CAPS
            
            for wh in PRIORITY_ORDER:
                tot = row[wh]
                min_cap = caps[sg]['MIN'][wh]
                if 0 < tot < min_cap:
                    revert_sets[wh].add((st, sg))

        # Revert items
        styles_arr = df_out[style_col].to_numpy()
        for wh in PRIORITY_ORDER:
            if revert_sets[wh]:
                wh_arr = df_out[wh].to_numpy(copy=True)
                for i in range(n):
                    if (styles_arr[i], size_groups[i]) in revert_sets[wh]:
                        bag_arr[i] += wh_arr[i]
                        wh_arr[i] = 0
                df_out[wh] = wh_arr

        df_out['Bagalur'] = bag_arr

    df_out = df_out.drop(columns=['_size_group', '_gender'], errors='ignore')
    return df_out


def process_boxwise_allocation(df, style_col='Style', color_col='Color', size_col='Size', qty_col='Grand Total', per_box_col='PER BOX QTY'):
    """
    Executes box-wise allocation based on template rules:
    - Kolkata_Alloc = MIN(Size_Min_Rule, Grand_Total * 10%)
    - Bhiwandi_Alloc = MIN(Size_Min_Rule, Grand_Total * 10%)
    - Gurgaon_Alloc = MIN(Size_Min_Rule, Grand_Total * 6%)
    - Retained at Bagalur = Grand_Total - Sum(Pushed)
    - Calculates Box counts per warehouse using PER BOX QTY
    """
    df_out = df.copy()

    # Fallback default for PER BOX QTY if missing or 0
    if per_box_col not in df_out.columns or df_out[per_box_col].isnull().all():
        df_out[per_box_col] = 10.0
    
    df_out[per_box_col] = df_out[per_box_col].fillna(10).replace(0, 10).astype(float)
    df_out['TOTAL BOX'] = (df_out[qty_col] / df_out[per_box_col]).round(2)

    n = len(df_out)
    kol_alloc = np.zeros(n, dtype=float)
    bhi_alloc = np.zeros(n, dtype=float)
    gur_alloc = np.zeros(n, dtype=float)

    sizes = df_out[size_col].astype(str).str.upper().str.strip().to_numpy()
    qtys = df_out[qty_col].to_numpy(dtype=float)

    for i in range(n):
        s_raw = sizes[i]
        rule_key = SIZE_TO_RULE_KEY.get(s_raw, s_raw)
        caps = BOXWISE_SIZE_RULES.get(rule_key, {'Kolkata': 0, 'Bhiwandi': 0, 'Gurgaon': 0})
        
        q = qtys[i]
        kol_alloc[i] = min(caps['Kolkata'], q * 0.10)
        bhi_alloc[i] = min(caps['Bhiwandi'], q * 0.10)
        gur_alloc[i] = min(caps['Gurgaon'], q * 0.06)

    df_out['Kolkata_Alloc'] = kol_alloc
    df_out['Bhiwandi_Alloc'] = bhi_alloc
    df_out['Gurgaon_Alloc'] = gur_alloc
    df_out['Bagalur_Retained'] = (qtys - (kol_alloc + bhi_alloc + gur_alloc)).clip(min=0)

    per_box = df_out[per_box_col].to_numpy()
    df_out['Kolkata_Boxes'] = (kol_alloc / per_box).round(2)
    df_out['Bhiwandi_Boxes'] = (bhi_alloc / per_box).round(2)
    df_out['Gurgaon_Boxes'] = (gur_alloc / per_box).round(2)
    df_out['Bagalur_Boxes'] = (df_out['Bagalur_Retained'] / per_box).round(2)

    # Standard warehouse column names for UI consistency
    df_out['Bagalur'] = df_out['Bagalur_Retained'].astype(int)
    df_out['Bhiwandi'] = df_out['Bhiwandi_Alloc'].astype(int)
    df_out['Kolkata'] = df_out['Kolkata_Alloc'].astype(int)
    df_out['Gurgaon'] = df_out['Gurgaon_Alloc'].astype(int)

    return df_out


if __name__ == "__main__":
    # Example usage / Test cases
    data = [
        # Full Style Test to meet NS Cap (Min 25)
        # Total Qty = 150 -> Bhiwandi ~30, Kol ~22, Gur ~7
        {'Style': 'OR10FULL', 'Size': 'S', 'Total_Qty': 30},
        {'Style': 'OR10FULL', 'Size': 'M', 'Total_Qty': 40},
        {'Style': 'OR10FULL', 'Size': 'L', 'Total_Qty': 40},
        {'Style': 'OR10FULL', 'Size': 'XL', 'Total_Qty': 20},
        {'Style': 'OR10FULL', 'Size': '2XL', 'Total_Qty': 20},
        
        # Original single-size test (will be zeroed out due to NS cap < 25)
        {'Style': 'OR10ASHMED', 'Size': 'M', 'Total_Qty': 40},
        {'Style': 'TEST_MIN_CATCH', 'Size': 'M', 'Total_Qty': 20},
    ]
    df = pd.DataFrame(data)
    
    print("Input Data:")
    print(df)
    print("\nProcessed Allocation:")
    allocated_df = process_allocation(df)
    print(allocated_df)
    
    # Save to CSV for the user
    # allocated_df.to_csv('Allocation_Plan_Output.csv', index=False)

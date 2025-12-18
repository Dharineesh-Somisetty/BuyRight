import pandas as pd
from typing import List, Dict, Any

# Mock Database
data = {
    'name': [
        'whey protein isolate', 'maltodextrin', 'sugar', 'oats', 
        'wheat gluten', 'pea protein', 'brown rice flour', 'soy lecithin',
        'sucralose', 'creatine monohydrate'
    ],
    'type': [
        'Protein', 'Carb', 'Carb', 'Carb', 
        'Protein', 'Protein', 'Carb', 'Emulsifier',
        'Sweetener', 'Supplement'
    ],
    'bioavailability': [
        100, 30, 20, 60, 
        70, 80, 50, 40,
        0, 90
    ],
    'bloat_risk': [
        2, 4, 6, 1, 
        7, 3, 2, 1,
        4, 1
    ]
}

df_ingredients = pd.DataFrame(data)

def calculate_apex_score(ingredients: List[str], mode: str) -> Dict[str, Any]:
    """
    Calculates the Apex Score for a list of ingredients based on the selected mode.
    """
    final_score = 0.0
    warnings = []
    analysis_log = []
    
    current_weight = 1.0
    decay_factor = 0.8
    
    analysis_log.append(f"Starting analysis for {len(ingredients)} ingredients. Mode: {mode}")

    for ingredient in ingredients:
        # Normalize ingredient name for lookup (simple lowercase strip)
        ing_clean = ingredient.lower().strip()
        analysis_log.append(f"Processing: {ingredient} (Weight: {current_weight:.2f})")
        
        # Lookup in DataFrame
        match = df_ingredients[df_ingredients['name'] == ing_clean]
        
        if match.empty:
            analysis_log.append(f"  - Not found in database. Skipping.")
            # Decay even if not found? Usually yes, to penalize position. 
            # User didn't specify, but assuming decay logic applies per list item position.
            current_weight *= decay_factor
            continue
            
        row = match.iloc[0]
        ing_type = row['type']
        bioavailability = row['bioavailability']
        bloat_risk = row['bloat_risk']
        
        # Score Logic: Protein
        if ing_type == 'Protein':
            points = bioavailability * current_weight
            final_score += points
            analysis_log.append(f"  - Protein found. Added {points:.2f} points.")
            
        # Mode Logic: CUT (Penalize high risk carbs)
        if mode == 'CUT' and ing_type == 'Carb' and bloat_risk > 3: 
            # "high-risk carb (like sugar)" - using bloat_risk as proxy or specific check
            # User said "like sugar", sugar has bloat 6 in my mock.
            # Let's say >4 is high risk for simplicity or explicit name check.
            # Or maybe just specific names? User mentioned "high-risk carb (like sugar)".
            # I will use bloat_risk > 5 for 'high risk' general rule, 
            # OR specifically if it is 'sugar' or 'maltodextrin' (which might be high GI).
            # Let's stick to the prompt's bloat logic separately, but for CUT mode:
            # "if ingredient is a high-risk carb (like sugar)".
            # I'll treat 'sugar' specifically or high bloat carbs as high risk.
            if ing_clean in ['sugar', 'maltodextrin'] or bloat_risk >= 5:
                penalty = 10 * current_weight
                final_score -= penalty
                warnings.append(f"Restricted carb found in CUT mode: {ingredient}")
                analysis_log.append(f"  - CUT mode penalty applied: -{penalty:.2f}")

        # Bloat Logic
        if bloat_risk > 5:
            warnings.append(f"High bloat risk: {ingredient}")
            analysis_log.append(f"  - High bloat risk detected ({bloat_risk})")
            
        current_weight *= decay_factor

    analysis_log.append(f"Analysis complete. Final Score: {final_score:.2f}")

    return {
        "final_score": round(final_score, 2),
        "warnings": warnings,
        "analysis_log": analysis_log
    }

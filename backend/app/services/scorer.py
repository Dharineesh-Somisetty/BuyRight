import pandas as pd
from typing import List, Dict, Any

# Mock Database
data = {
    'name': [
        'whey protein isolate', 'maltodextrin', 'sugar', 'oats', 
        'wheat gluten', 'pea protein', 'brown rice flour', 'soy lecithin',
        'sucralose', 'creatine monohydrate', 'whey protein'
    ],
    'type': [
        'Protein', 'Carb', 'Carb', 'Carb', 
        'Protein', 'Protein', 'Carb', 'Emulsifier',
        'Sweetener', 'Supplement', 'Protein'
    ],
    'bioavailability': [
        100, 30, 20, 60, 
        70, 80, 50, 40,
        0, 90, 100
    ],
    'bloat_risk': [
        2, 4, 6, 1, 
        7, 3, 2, 1,
        4, 1, 2
    ]
}

df_ingredients = pd.DataFrame(data)

def calculate_apex_score(ingredients: List[str], mode: str) -> Dict[str, Any]:
    """
    Calculates the Apex Score: starts at 0, adds points for quality, specific penalties.
    """
    final_score = 0.0
    good_ingredients = []
    bad_ingredients = []
    warnings = []
    analysis_log = []
    
    current_weight = 1.0
    decay_factor = 0.9 # Slightly less decay to allow more ingredients to count
    
    analysis_log.append(f"Starting analysis for {len(ingredients)} ingredients. Mode: {mode}")

    for ingredient in ingredients:
        ing_clean = ingredient.lower().strip()
        analysis_log.append(f"Processing: {ingredient} (Weight: {current_weight:.2f})")
        
        # Lookup
        match = df_ingredients[df_ingredients['name'] == ing_clean]
        
        if match.empty:
            analysis_log.append(f"  - Not found. Neutral.")
            current_weight *= decay_factor
            continue
            
        row = match.iloc[0]
        ing_type = row['type']
        bioavailability = row['bioavailability']
        bloat_risk = row['bloat_risk']
        
        points_gained = 0
        penalty_applied = 0
        
        # 1. Gain Points: Quality Protein or Supplement
        if ing_type == 'Protein' or ing_type == 'Supplement':
            # Base points: Bioavailability scaled by weight
            # Example: Whey (100) * 1.0 = 100 pts. Oats (60) * 0.8 = 48 pts.
            # We scale it down slightly so 1 ingredient doesn't instantly max out 100 if we want cumulative
            # OR we just let it add up. Let's add simple points.
            # logic: gain = (bioavailability / 2) * weight. 
            # Whey @ pos 1 = 50 pts.
            points = (bioavailability / 2) * current_weight
            final_score += points
            points_gained += points
            good_ingredients.append(f"{ingredient} (+{points:.1f})")
            analysis_log.append(f"  - Quality found. +{points:.1f}")

        # 2. Penalties: Bloat Risk
        if bloat_risk >= 5:
            penalty = 10.0
            # Don't drop below 0 immediately relative to this ingredient? 
            # Global score checks happen at end, but here we just deduct.
            final_score -= penalty
            penalty_applied += penalty
            bad_ingredients.append(f"{ingredient} (High Bloat Risk)")
            warnings.append(f"Bloat warning: {ingredient}")
            analysis_log.append(f"  - High bloat risk. -{penalty}")

        # 3. Mode Specific Penalties (CUT)
        if mode == 'CUT' and ing_type == 'Carb' and bloat_risk > 3:
            penalty = 15.0 * current_weight
            final_score -= penalty
            penalty_applied += penalty
            bad_ingredients.append(f"{ingredient} (Carb limit in CUT)")
            analysis_log.append(f"  - CUT mode carb penalty. -{penalty:.1f}")

        current_weight *= decay_factor

    # Final Adjustment / Cap
    if final_score < 0:
        final_score = 0.0
    if final_score > 100:
        final_score = 100.0

    # Verdict
    verdict = "Neutral"
    if final_score >= 80:
        verdict = "Excellent for Bulking"
    elif final_score >= 50:
        verdict = "Good Source"
    elif final_score >= 30:
        verdict = "Mediocre"
    else:
        verdict = "Avoid if possible"

    return {
        "final_score": round(final_score, 1),
        "verdict": verdict,
        "good_ingredients": good_ingredients,
        "bad_ingredients": bad_ingredients,
        "warnings": warnings,
        "analysis_log": analysis_log
    }

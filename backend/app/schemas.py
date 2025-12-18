from pydantic import BaseModel
from typing import List, Optional

class IngredientAnalysis(BaseModel):
    name: str
    type: str # e.g., 'Protein', 'Carb'
    bioavailability: int # 0-100
    bloat_risk: int # 0-10
    explanation: str

class ScanRequest(BaseModel):
    ingredients: List[str]
    mode: str = 'BULK'

class ScanResponse(BaseModel):
    final_score: float
    verdict: str
    good_ingredients: List[str]
    bad_ingredients: List[str]
    warnings: List[str]
    analysis_log: List[str]

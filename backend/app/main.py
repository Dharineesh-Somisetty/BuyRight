from fastapi import FastAPI
from .schemas import ScanRequest, ScanResponse
from .services.scorer import calculate_apex_score

app = FastAPI()

@app.post('/scan', response_model=ScanResponse)
def scan_product(request: ScanRequest):
    result = calculate_apex_score(request.ingredients, request.mode)
    return result

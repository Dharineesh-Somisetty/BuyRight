from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .schemas import ScanRequest, ScanResponse
from .services.scorer import calculate_apex_score

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post('/scan', response_model=ScanResponse)
def scan_product(request: ScanRequest):
    result = calculate_apex_score(request.ingredients, request.mode)
    return result

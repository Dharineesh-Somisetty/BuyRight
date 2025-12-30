from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .schemas import ScanRequest, ScanResponse
from .services.scorer import calculate_apex_score

app = FastAPI(title="BuyRight API", version="1.0.0")

# CORS configuration for web application
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/')
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "BuyRight API"}

@app.post('/scan', response_model=ScanResponse)
def scan_product(request: ScanRequest):
    """Analyze product ingredients and return Apex Score"""
    result = calculate_apex_score(request.ingredients, request.mode)
    return result

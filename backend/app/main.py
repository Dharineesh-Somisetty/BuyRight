from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
from .schemas import ScanRequest, ScanResponse
from .services.scorer import calculate_apex_score
from .services.off_service import fetch_product_from_off
from .database import engine, get_db
from . import models

models.Base.metadata.create_all(bind=engine)

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

@app.get('/product/{barcode}')
def get_product_by_barcode(barcode: str, db: Session = Depends(get_db)):
    """
    Get product details by barcode with smart caching:
    1. Check local DB
    2. Fallback to OpenFoodFacts API
    3. Calculate score and save to DB
    """
    # 1. Check DB
    db_product = db.query(models.Product).filter(models.Product.barcode == barcode).first()
    if db_product:
        return {
            "source": "database",
            "name": db_product.name,
            "brand": db_product.brand,
            "image_url": db_product.image_url,
            "ingredients_text": db_product.ingredients_text,
            "apex_score": db_product.apex_score,
            "last_updated": db_product.last_updated
        }

    # 2. Fallback to API
    off_data = fetch_product_from_off(barcode)
    if not off_data:
        raise HTTPException(status_code=404, detail="Product not found")

    # 3. Calculate score
    ingredients_list = off_data.get('ingredients', [])
    ingredients_text = off_data.get('ingredients_text', '')
    
    if not ingredients_list:
        # Fallback to parsing text if tags weren't available
        cleaned_text = ingredients_text.replace("Ingredients:", "").strip()
        ingredients_list = [i.strip() for i in cleaned_text.split(',')]
    
    # We use the cleaned list for scoring to get better matches (e.g. 'sugar' instead of 'sucre')
    score_result = calculate_apex_score(ingredients_list, mode="BULK")
    apex_score = score_result["final_score"]

    # 4. Save to DB
    # We save the English list as the text for consistency? 
    # Or keep original text? The user might want to see the original on the product page?
    # But for search consistency, maybe save English?
    # Let's save the original text for display, but user might be confused if we score based on English.
    # Let's stick to saving what we have. 
    # Actually, if we use the list for scoring, we should probably save a string representation of THAT list 
    # so if we load from DB later, we get the same ingredients?
    # But 'ingredients_text' in DB is string. 
    # Let's save the comma-joined English list to ensure consistency on re-fetch.
    
    final_ingredients_text = ", ".join(ingredients_list)

    new_product = models.Product(
        barcode=barcode,
        name=off_data.get('product_name'),
        brand=off_data.get('brand'),
        image_url=off_data.get('image_url'),
        ingredients_text=final_ingredients_text,
        apex_score=apex_score,
        last_updated=datetime.utcnow()
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return {
        "source": "api",
        "name": new_product.name,
        "brand": new_product.brand,
        "image_url": new_product.image_url,
        "ingredients_text": new_product.ingredients_text,
        "apex_score": new_product.apex_score,
        "last_updated": new_product.last_updated
    }

from sqlalchemy import Column, String, Integer, Float, DateTime
from .database import Base

class Product(Base):
    __tablename__ = "products"

    barcode = Column(String, primary_key=True, index=True)
    name = Column(String)
    brand = Column(String)
    image_url = Column(String)
    ingredients_text = Column(String)
    apex_score = Column(Float)
    last_updated = Column(DateTime)

class IngredientKnowledge(Base):
    __tablename__ = "ingredients_knowledge"

    name = Column(String, primary_key=True)
    type = Column(String)
    bioavailability = Column(Integer)
    bloat_risk = Column(Integer)

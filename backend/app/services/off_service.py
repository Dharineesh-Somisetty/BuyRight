import requests
from typing import Optional, Dict, Any

def fetch_product_from_off(barcode: str) -> Optional[Dict[str, Any]]:
    """
    Fetch product details from OpenFoodFacts API.
    
    Args:
        barcode (str): The barcode of the product to fetch.

    Returns:
        Optional[Dict[str, Any]]: A dictionary containing product_name, image_url, 
        and ingredients_text if found, else None.
    """
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    headers = {
        'User-Agent': 'ApexScanner - Android - Version 1.0'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if data.get('status') == 1:
            product = data.get('product', {})
            
            # Extract and clean ingredient tags to get English names
            raw_tags = product.get('ingredients_tags', [])
            clean_ingredients = []
            
            for tag in raw_tags:
                # Remove 'en:' prefix and other language prefixes if we want to be safe, 
                # but usually we want to prioritize English. 
                # The tags are like "en:sugar", "fr:sucre". 
                # OFF tries to normalize to English tags usually.
                # Let's clean the string as requested: remove 'en:' and replace '-' with ' '
                if ':' in tag:
                    _, value = tag.split(':', 1)
                else:
                    value = tag
                
                clean_value = value.replace('-', ' ')
                clean_ingredients.append(clean_value)

            return {
                'product_name': product.get('product_name', 'Unknown Product'),
                'brand': product.get('brands', ''),
                'image_url': product.get('image_url', ''),
                'ingredients': clean_ingredients,
                'ingredients_text': product.get('ingredients_text', '') # Keep for reference
            }
        return None
        
    except requests.RequestException as e:
        print(f"Error fetching data from OpenFoodFacts: {e}")
        return None

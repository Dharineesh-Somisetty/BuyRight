import os
import csv
import json
import time
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv('GROQ_API_KEY'))

def classify_ingredient(ingredient_name):
    """
    Classifies an ingredient using the Groq API.
    """
    try:
        completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a Nutrition Database. Return ONLY a JSON object with keys: type (Protein/Carb/Fat/Additive), bioavailability (0-100), bloat_risk (0-10), and explanation (short string)."
                },
                {
                    "role": "user",
                    "content": ingredient_name,
                }
            ],
            model="llama-3.1-8b-instant",
        )
        
        response_content = completion.choices[0].message.content
        # Simple cleanup to ensure we get just the JSON if there's markdown wrapping
        if "```json" in response_content:
            response_content = response_content.split("```json")[1].split("```")[0].strip()
        elif "```" in response_content:
            response_content = response_content.split("```")[1].strip()
            
        return json.loads(response_content)
    except Exception as e:
        print(f"Error classifying {ingredient_name}: {e}")
        return None

def run_pipeline():
    ingredients = ['Micellar Casein', 'Yellow 5', 'Dextrose', 'Palm Oil']
    output_dir = "data"
    output_file = os.path.join(output_dir, "ingredients_master.csv")
    
    # Ensure directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    print(f"Starting pipeline. Writing to {output_file}...")
    
    # Open file for writing (append mode or write mode? User said 'Append', but for a fresh run write is safer to avoid dupes if re-run. 
    # I'll use 'a' as requested, but maybe add header if new?)
    file_exists = os.path.isfile(output_file)
    
    with open(output_file, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Write header if file is new
        if not file_exists:
            writer.writerow(['name', 'type', 'bioavailability', 'bloat_risk', 'explanation'])
        
        for ingredient in ingredients:
            print(f"Classifying: {ingredient}...")
            data = classify_ingredient(ingredient)
            
            if data:
                writer.writerow([
                    ingredient,
                    data.get('type'),
                    data.get('bioavailability'),
                    data.get('bloat_risk'),
                    data.get('explanation')
                ])
                print(f"  -> {data}")
            else:
                print("  -> Failed.")
            
            # Rate limit politeness
            time.sleep(1)

    print("Pipeline complete.")

if __name__ == "__main__":
    run_pipeline()

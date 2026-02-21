import requests
import json

class AICategorizer:
    def __init__(self, base_url="http://localhost:11434", model="llama3.2"):
        self.base_url = base_url
        self.model = model
        self.categories = [
            "Groceries", "Restaurants", "Transport", "Healthcare", 
            "Shopping", "Entertainment", "Bills", "Other"
        ]
    
    def categorize(self, description, amount):
        prompt = f"""Categorize this transaction:
Description: {description}
Amount: {amount} PLN

Available categories: {', '.join(self.categories)}

Return only the category name, nothing else."""
        
        response = requests.post(f"{self.base_url}/api/generate", json={
            "model": self.model,
            "prompt": prompt,
            "stream": False
        })
        
        category = response.json()["response"].strip()
        return category if category in self.categories else "Other"
    
    def categorize_batch(self, transactions):
        results = []
        for desc, amount in transactions:
            results.append(self.categorize(desc, amount))
        return results

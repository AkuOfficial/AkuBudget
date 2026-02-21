import requests

class AICategorizer:
    EXPENSE_CATEGORIES = [
        "Other", "Groceries", "Restaurants", "Transport", "Healthcare", 
        "Shopping", "Entertainment", "Bills", "Education"
    ]
    
    INCOME_CATEGORIES = [
        "Other", "Salary", "Freelance", "Investment", "Gift"
    ]
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.2") -> None:
        self.base_url = base_url
        self.model = model
    
    def categorize(self, description: str, amount: float, trans_type: str = "expense") -> str:
        categories = self.EXPENSE_CATEGORIES if trans_type == "expense" else self.INCOME_CATEGORIES
        prompt = f"""Categorize this transaction:
Description: {description}
Amount: {amount} PLN

Available categories: {', '.join(categories)}

Return only the category name, nothing else."""
        
        try:
            response = requests.post(f"{self.base_url}/api/generate", json={
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }, timeout=10)
            
            category = response.json()["response"].strip()
            return category if category in categories else "Other"
        except:
            return self._fallback_categorize(description, trans_type)
    
    def _fallback_categorize(self, description: str, trans_type: str = "expense") -> str:
        if trans_type == "income":
            desc_lower = description.lower()
            if any(x in desc_lower for x in ['salary', 'wynagrodzenie', 'pensja']):
                return "Salary"
            if any(x in desc_lower for x in ['freelance', 'zlecenie', 'contract']):
                return "Freelance"
            if any(x in desc_lower for x in ['dividend', 'interest', 'investment']):
                return "Investment"
            if any(x in desc_lower for x in ['gift', 'prezent']):
                return "Gift"
            return "Other"
        
        desc_lower = description.lower()
        if any(x in desc_lower for x in ['biedronka', 'kaufland', 'lidl', 'auchan', 'carrefour', 'dino']):
            return "Groceries"
        if any(x in desc_lower for x in ['restaurant', 'pizza', 'kebab', 'mcdonalds', 'kfc']):
            return "Restaurants"
        if any(x in desc_lower for x in ['orlen', 'shell', 'bp', 'uber', 'bolt', 'taxi']):
            return "Transport"
        if any(x in desc_lower for x in ['apteka', 'pharmacy', 'clinic', 'hospital']):
            return "Healthcare"
        if any(x in desc_lower for x in ['media', 'rtv', 'empik', 'reserved', 'h&m']):
            return "Shopping"
        if any(x in desc_lower for x in ['cinema', 'kino', 'netflix', 'spotify']):
            return "Entertainment"
        if any(x in desc_lower for x in ['prąd', 'gaz', 'woda', 'internet', 'telefon', 'energy']):
            return "Bills"
        if any(x in desc_lower for x in ['school', 'course', 'book', 'education']):
            return "Education"
        return "Other"
    
    def categorize_batch(self, transactions: list[tuple[str, float, str]]) -> list[str]:
        results: list[str] = []
        for desc, amount, trans_type in transactions:
            results.append(self.categorize(desc, amount, trans_type))
        return results

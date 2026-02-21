import sqlite3
import pandas as pd


class BudgetManager:
    def __init__(self, db_path: str = "budget.db") -> None:
        self.db_path = db_path
        self.init_db()

    def init_db(self) -> None:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS transactions
                     (id INTEGER PRIMARY KEY, date TEXT, description TEXT, 
                      amount REAL, category TEXT, type TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS categories
                     (id INTEGER PRIMARY KEY, name TEXT, type TEXT, UNIQUE(name, type))''')
        conn.commit()
        
        # Initialize default categories
        for cat in ["Other", "Groceries", "Restaurants", "Transport", "Healthcare", "Shopping", "Entertainment", "Bills", "Education"]:
            c.execute("INSERT OR IGNORE INTO categories (name, type) VALUES (?, ?)", (cat, "expense"))
        for cat in ["Other", "Salary", "Freelance", "Investment", "Gift"]:
            c.execute("INSERT OR IGNORE INTO categories (name, type) VALUES (?, ?)", (cat, "income"))
        
        conn.commit()
        conn.close()

    def add_transaction(self, date: str, description: str, amount: float, category: str, trans_type: str = "expense") -> None:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT INTO transactions (date, description, amount, category, type) VALUES (?, ?, ?, ?, ?)",
                  (date, description, amount, category, trans_type))
        conn.commit()
        conn.close()

    def add_salary(self, date: str, amount: float, description: str = "") -> None:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT INTO salary (date, amount, description) VALUES (?, ?, ?)",
                  (date, amount, description))
        conn.commit()
        conn.close()
    
    def get_categories(self, cat_type: str) -> list[str]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT name FROM categories WHERE type = ? ORDER BY CASE WHEN name = 'Other' THEN 0 ELSE 1 END, name", (cat_type,))
        categories = [row[0] for row in c.fetchall()]
        conn.close()
        return categories
    
    def add_category(self, name: str, cat_type: str) -> None:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO categories (name, type) VALUES (?, ?)", (name, cat_type))
        conn.commit()
        conn.close()
    
    def delete_category(self, name: str, cat_type: str) -> None:
        if name.lower() == "other":
            return
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("UPDATE transactions SET category = 'Other' WHERE category = ? AND type = ?", (name, cat_type))
        c.execute("DELETE FROM categories WHERE name = ? AND type = ?", (name, cat_type))
        conn.commit()
        conn.close()

    def get_monthly_spending(self, year: int, month: int) -> pd.DataFrame:
        conn = sqlite3.connect(self.db_path)
        query = f"SELECT * FROM transactions WHERE strftime('%Y', date) = '{year}' AND strftime('%m', date) = '{month:02d}'"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

    def get_summary(self, year: int, month: int) -> dict:
        df = self.get_monthly_spending(year, month)
        expenses = df[df['type'] == 'expense']['amount'].sum()
        income = df[df['type'] == 'income']['amount'].sum()
        
        return {
            'expenses': expenses,
            'income': income,
            'balance': income - expenses,
            'by_category': df[df['type'] == 'expense'].groupby('category')['amount'].sum().to_dict()
        }

    def import_xls(self, file_path: str) -> pd.DataFrame:
        df = pd.read_excel(file_path, engine='xlrd')
        return df

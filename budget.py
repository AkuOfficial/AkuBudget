import sqlite3
import pandas as pd
from datetime import datetime
from pathlib import Path

class BudgetManager:
    def __init__(self, db_path="budget.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS transactions
                     (id INTEGER PRIMARY KEY, date TEXT, description TEXT, 
                      amount REAL, category TEXT, type TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS categories
                     (id INTEGER PRIMARY KEY, name TEXT UNIQUE, type TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS salary
                     (id INTEGER PRIMARY KEY, date TEXT, amount REAL, description TEXT)''')
        conn.commit()
        conn.close()
    
    def add_transaction(self, date, description, amount, category, trans_type="expense"):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT INTO transactions (date, description, amount, category, type) VALUES (?, ?, ?, ?, ?)",
                  (date, description, amount, category, trans_type))
        conn.commit()
        conn.close()
    
    def add_salary(self, date, amount, description=""):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT INTO salary (date, amount, description) VALUES (?, ?, ?)",
                  (date, amount, description))
        conn.commit()
        conn.close()
    
    def get_monthly_spending(self, year, month):
        conn = sqlite3.connect(self.db_path)
        query = f"SELECT * FROM transactions WHERE strftime('%Y', date) = '{year}' AND strftime('%m', date) = '{month:02d}'"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    def get_summary(self, year, month):
        df = self.get_monthly_spending(year, month)
        expenses = df[df['type'] == 'expense']['amount'].sum()
        income = df[df['type'] == 'income']['amount'].sum()
        
        conn = sqlite3.connect(self.db_path)
        salary_query = f"SELECT SUM(amount) FROM salary WHERE strftime('%Y', date) = '{year}' AND strftime('%m', date) = '{month:02d}'"
        salary = pd.read_sql_query(salary_query, conn).iloc[0, 0] or 0
        conn.close()
        
        return {
            'expenses': expenses,
            'income': income + salary,
            'balance': income + salary - expenses,
            'by_category': df.groupby('category')['amount'].sum().to_dict()
        }
    
    def import_xls(self, file_path):
        df = pd.read_excel(file_path, engine='xlrd')
        return df

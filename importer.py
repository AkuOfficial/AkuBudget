import pandas as pd

from ai_categorizer import AICategorizer
from budget import BudgetManager


class BankImporter:
    def __init__(self, budget_manager: BudgetManager, ai_categorizer: AICategorizer) -> None:
        self.bm = budget_manager
        self.ai = ai_categorizer

    def import_bank_xls(self, file_path) -> list[tuple[str, str, float, str]]:
        df = pd.read_excel(file_path, engine='xlrd', skiprows=2)

        date_col = df.columns[0]
        desc_col = df.columns[4]
        amount_col = df.columns[5]

        transactions: list[tuple[str, str, float, str]] = []
        for _, row in df.iterrows():
            date = pd.to_datetime(row[date_col]).strftime('%Y-%m-%d')
            description = str(row[desc_col])
            amount = abs(float(row[amount_col]))

            if pd.notna(amount) and amount > 0:
                trans_type = "income" if row[amount_col] > 0 else "expense"
                category = self.ai.categorize(description, amount, trans_type)

                self.bm.add_transaction(date, description, amount, category, trans_type)
                transactions.append((date, description, amount, category))

        return transactions

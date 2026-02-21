import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from budget import BudgetManager
from ai_categorizer import AICategorizer
from importer import BankImporter


class BudgetApp:
    def __init__(self):
        st.set_page_config(page_title="AkuBudget", page_icon="💰", layout="wide")
        self.bm = BudgetManager()
        self.ai = AICategorizer()
        self.importer = BankImporter(self.bm, self.ai)

    def run(self) -> None:
        st.title("💰 AkuBudget - AI Budget Manager")
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
            ["📊 Dashboard", "💸 Add Expense", "💰 Add Income", "📥 Import", "📋 Transactions", "⚙️ Settings"])

        with tab1:
            self._render_dashboard()
        with tab2:
            self._render_add_expense()
        with tab3:
            self._render_add_income()
        with tab4:
            self._render_import()
        with tab5:
            self._render_transactions()
        with tab6:
            self._render_settings()

        self._render_sidebar()

    def _render_dashboard(self):
        col1, col2 = st.columns(2)
        with col1:
            year = st.selectbox("Year", range(datetime.now().year, 2020, -1), key="dash_year")
        with col2:
            month = st.selectbox("Month", range(1, 13), index=datetime.now().month - 1, key="dash_month")

        summary = self.bm.get_summary(year, month)

        col1, col2, col3 = st.columns(3)
        col1.metric("💰 Income", f"{summary['income']:.2f} PLN")
        col2.metric("💸 Expenses", f"{summary['expenses']:.2f} PLN")
        col3.metric("📈 Balance", f"{summary['balance']:.2f} PLN",
                    delta=f"{summary['balance']:.2f} PLN",
                    delta_color="normal" if summary['balance'] >= 0 else "inverse")

        if summary['by_category']:
            col1, col2 = st.columns(2)
            df_cat = pd.DataFrame(list(summary['by_category'].items()), columns=['Category', 'Amount'])

            with col1:
                st.subheader("Expenses by Category")
                fig = px.pie(df_cat, values='Amount', names='Category', hole=0.4)
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.subheader("Category Breakdown")
                fig = px.bar(df_cat, x='Category', y='Amount', color='Category')
                st.plotly_chart(fig, use_container_width=True)

            df_monthly = self.bm.get_monthly_spending(year, month)
            if not df_monthly.empty:
                st.subheader("Daily Spending Trend")
                df_monthly['date'] = pd.to_datetime(df_monthly['date'])
                daily = df_monthly[df_monthly['type'] == 'expense'].groupby('date')['amount'].sum().reset_index()
                fig = px.line(daily, x='date', y='amount', markers=True)
                st.plotly_chart(fig, use_container_width=True)

    def _render_add_expense(self) -> None:
        st.subheader("Add New Expense")
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("Date", datetime.now())
            description = st.text_input("Description")
        with col2:
            amount = st.number_input("Amount (PLN)", min_value=0.0, step=0.01)

        if st.button("🤖 AI Suggest Category", type="secondary"):
            if description and amount > 0:
                with st.spinner("AI analyzing..."):
                    try:
                        suggested = self.ai.categorize(description, amount, "expense")
                        st.session_state['suggested_category'] = suggested
                        st.success(f"AI suggests: **{suggested}**")
                    except Exception as e:
                        st.warning("Ollama not running. Start it with: `ollama serve`")

        expense_cats = self.bm.get_categories("expense")
        category = st.selectbox("Category", expense_cats,
                                index=expense_cats.index(st.session_state.get('suggested_category', 'Other')) if st.session_state.get('suggested_category', 'Other') in expense_cats else 0)

        if st.button("➕ Add Expense", type="primary"):
            if description and amount > 0:
                self.bm.add_transaction(date.strftime('%Y-%m-%d'), description, amount, category, "expense")
                st.success("✅ Expense added!")
                st.rerun()

    def _render_add_income(self) -> None:
        st.subheader("Add New Income")
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("Date", datetime.now(), key="income_date")
            description = st.text_input("Description", key="income_desc")
        with col2:
            amount = st.number_input("Amount (PLN)", min_value=0.0, step=0.01, key="income_amount")
        
        income_cats = self.bm.get_categories("income")
        category = st.selectbox("Category", income_cats, key="income_cat")

        if st.button("💰 Add Income", type="primary"):
            if description and amount > 0:
                self.bm.add_transaction(date.strftime('%Y-%m-%d'), description, amount, category, "income")
                st.success("✅ Income added!")
                st.rerun()

    def _render_import(self):
        st.subheader("Import Bank Statement")
        uploaded_file = st.file_uploader("Upload XLS file", type=['xls', 'xlsx'])

        if uploaded_file:
            if st.button("🚀 Import & Auto-Categorize", type="primary"):
                with st.spinner("AI categorizing transactions..."):
                    try:
                        transactions = self.importer.import_bank_xls(uploaded_file)
                        st.success(f"✅ Imported {len(transactions)} transactions!")
                        df_imported = pd.DataFrame(transactions, columns=['Date', 'Description', 'Amount', 'Category'])
                        st.dataframe(df_imported, use_container_width=True)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

    def _render_transactions(self):
        st.subheader("All Transactions")
        col1, col2 = st.columns(2)
        with col1:
            filter_year = st.selectbox("Year", range(datetime.now().year, 2020, -1), key="trans_year")
        with col2:
            filter_month = st.selectbox("Month", range(1, 13), index=datetime.now().month - 1, key="trans_month")

        df = self.bm.get_monthly_spending(filter_year, filter_month)
        if not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No transactions found for this period")

    def _render_settings(self) -> None:
        st.subheader("Category Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Expense Categories")
            expense_cats = self.bm.get_categories("expense")
            for cat in expense_cats:
                col_a, col_b = st.columns([3, 1])
                col_a.write(cat)
                if cat.lower() != "other":
                    if col_b.button("❌", key=f"del_exp_{cat}"):
                        self.bm.delete_category(cat, "expense")
                        st.rerun()
            
            new_expense = st.text_input("Add new expense category", key="new_expense")
            if st.button("➕ Add Expense Category"):
                if new_expense:
                    self.bm.add_category(new_expense, "expense")
                    st.success(f"Added: {new_expense}")
                    st.rerun()
        
        with col2:
            st.markdown("### Income Categories")
            income_cats = self.bm.get_categories("income")
            for cat in income_cats:
                col_a, col_b = st.columns([3, 1])
                col_a.write(cat)
                if cat.lower() != "other":
                    if col_b.button("❌", key=f"del_inc_{cat}"):
                        self.bm.delete_category(cat, "income")
                        st.rerun()
            
            new_income = st.text_input("Add new income category", key="new_income")
            if st.button("➕ Add Income Category"):
                if new_income:
                    self.bm.add_category(new_income, "income")
                    st.success(f"Added: {new_income}")
                    st.rerun()

    def _render_sidebar(self) -> None:
        st.sidebar.title("About")
        st.sidebar.info("AI-powered budget manager with automatic categorization")


if __name__ == "__main__":
    app = BudgetApp()
    app.run()

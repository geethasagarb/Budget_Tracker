import streamlit as st
import datetime
import json
from collections import defaultdict
from groq import Groq
import pandas as pd
import plotly.express as px

# Initialize Groq API client
client = Groq(
    api_key="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"  # Replace with your actual API key
)

class BudgetTracker:
    def __init__(self, data_file="budget_data.json"):
        """Initialize the BudgetTracker with default data and categories."""
        self.data_file = data_file
        self.budget = 0.0
        self.daily_budget = 0.0
        self.expenses = defaultdict(list)
        self.categories = {
            'food': ['grocery', 'restaurant', 'coffee', 'snack'],
            'transport': ['bus', 'taxi', 'fuel', 'train'],
            'entertainment': ['movie', 'games', 'concert', 'subscription'],
            'bills': ['electricity', 'water', 'internet', 'rent'],
            'others': []
        }
        self.load_data()

    def save_data(self):
        """Save all data to a JSON file."""
        data = {
            "budget": self.budget,
            "daily_budget": self.daily_budget,
            "expenses": {k: v for k, v in self.expenses.items()},
            "categories": self.categories
        }
        with open(self.data_file, "w") as file:
            json.dump(data, file, default=str, indent=4)

    def load_data(self):
        """Load data from a JSON file."""
        try:
            with open(self.data_file, "r") as file:
                data = json.load(file)
                self.budget = data.get("budget", 0.0)
                self.daily_budget = data.get("daily_budget", 0.0)
                self.expenses = defaultdict(list, data.get("expenses", {}))
        except FileNotFoundError:
            pass  # Start fresh if no data file exists

    def categorize_expense(self, description):
        """Categorize the expense based on keywords in the description."""
        description_lower = description.lower()
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword in description_lower:
                    return category
        return 'others'

    def add_expense(self, amount, description, date):
        """Add an expense to the tracker."""
        category = self.categorize_expense(description)
        expense = {
            'amount': amount,
            'description': description,
            'date': date  # Use provided date
        }
        self.expenses[category].append(expense)

    def show_summary(self):
        """Return a summary of expenses and budget details."""
        total_expenses = 0.0
        category_summary = {}
        for category, items in self.expenses.items():
            category_total = sum(item['amount'] for item in items)
            total_expenses += category_total
            category_summary[category] = category_total
        return {
            "total_expenses": total_expenses,
            "remaining_budget": self.budget - total_expenses,
            "category_summary": category_summary
        }

    def get_groq_suggestions(self):
        """Get AI-powered suggestions for optimizing spending using Groq."""
        total_expenses = sum(item['amount'] for items in self.expenses.values() for item in items)
        expense_breakdown = {
            category: sum(item['amount'] for item in items)
            for category, items in self.expenses.items()
        }
        message = f"""
        I have a budget of ${self.budget:.2f} and have spent ${total_expenses:.2f} so far.
        Here is a breakdown of my expenses by category: {expense_breakdown}.
        Please provide detailed suggestions on how I can optimize my spending and save more.
        """
        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": ""},
                    {"role": "user", "content": message}
                ],
                temperature=0.5,
                model="llama3-8b-8192"  # Groq model
            )
            return chat_completion.choices[0].message.content.strip()
        except Exception as e:
            return f"Error fetching suggestions from Groq API: {e}"

    def get_expenses_chart_data(self):
        """Prepare data for the expense chart."""
        chart_data = []
        for category, items in self.expenses.items():
            for item in items:
                chart_data.append({
                    "date": item['date'][:10],
                    "amount": item['amount'],
                    "category": category
                })
        return chart_data

# Initialize BudgetTracker instance
tracker = BudgetTracker()

# Streamlit UI
st.set_page_config(page_title="Budget Tracker", layout="wide")

# Login Page
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("Welcome to AI-Powered Budget Tracker")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == "BANA7085" and password == "12345":
            st.session_state["authenticated"] = True
            st.success("Login successful!")
        else:
            st.error("Invalid username or password")
else:
    # Main App with Tabs
    st.title("AI-Powered Budget Tracker")
    tab1, tab2, tab3, tab4 = st.tabs(["Budget Setup", "Add Expense", "Summary", "Expense Charts"])

    # Tab 1: Budget Setup
    with tab1:
        st.header("Budget Setup")
        monthly_budget = st.number_input("Set your monthly budget ($):", min_value=0.0, step=10.0, value=tracker.budget)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Update Budget"):
                tracker.budget = monthly_budget
                tracker.daily_budget = monthly_budget / 30
                tracker.save_data()
                st.success(f"Budget updated: ${tracker.budget:.2f} (Daily: ${tracker.daily_budget:.2f})")
        
        with col2:
            if st.button("Clear Budget"):
                tracker.budget = 0.0
                tracker.daily_budget = 0.0
                tracker.save_data()
                st.success("Previous budget cleared. You can now set a new budget.")

    # Tab 2: Add Expense
    with tab2:
        st.header("Add an Expense")
        expense_amount = st.number_input("Expense Amount ($):", min_value=0.0, step=1.0)
        expense_description = st.text_input("Expense Description:")
        expense_date = st.date_input("Date of Expense", value=datetime.date.today())  # Date picker
        
        if st.button("Add Expense"):
            if expense_amount > 0 and expense_description:
                tracker.add_expense(expense_amount, expense_description, expense_date.isoformat())
                tracker.save_data()
                st.success(f"Added expense: ${expense_amount:.2f} ({expense_description}) on {expense_date.isoformat()}")
            else:
                st.error("Please provide a valid amount and description.")

    # Tab 3: Summary
    with tab3:
        st.header("Expense Summary")
        summary = tracker.show_summary()
        st.write(f"**Total Expenses:** ${summary['total_expenses']:.2f}")
        st.write(f"**Remaining Budget:** ${summary['remaining_budget']:.2f}")

        st.subheader("Expenses by Category")
        for category, amount in summary['category_summary'].items():
            st.write(f"- {category.capitalize()}: ${amount:.2f}")

        st.subheader("AI Suggestions for Saving")
        if st.button("Get Suggestions"):
            suggestions = tracker.get_groq_suggestions()
            st.text_area("Groq Suggestions", suggestions, height=200)

    # Tab 4: Expense Charts
    with tab4:
        st.header("Expense Charts")

        chart_data = tracker.get_expenses_chart_data()
        if chart_data:
            df = pd.DataFrame(chart_data)
            df['date'] = pd.to_datetime(df['date'])

            # Line Chart 1: Cumulative Expenses Over Time
            df_cumulative = df.groupby('date')['amount'].sum().cumsum().reset_index()
            fig1 = px.line(
                df_cumulative,
                x='date',
                y='amount',
                title="Cumulative Expenses Over Time",
                labels={'date': 'Date', 'amount': 'Cumulative Amount ($)'},
                markers=True
            )
            fig1.update_layout(template="plotly_white")
            st.plotly_chart(fig1, use_container_width=True)

            # Line Chart 2: Daily Expense Changes
            df_daily = df.groupby('date')['amount'].sum().reset_index()
            fig2 = px.line(
                df_daily,
                x='date',
                y='amount',
                title="Daily Expense Changes",
                labels={'date': 'Date', 'amount': 'Daily Amount ($)'},
                markers=True
            )
            fig2.update_layout(template="plotly_white")
            st.plotly_chart(fig2, use_container_width=True)

            # Pie Chart: Spending by Category
            df_category = df.groupby('category')['amount'].sum().reset_index()
            fig3 = px.pie(
                df_category,
                names='category',
                values='amount',
                title="Spending by Category",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.write("No expense data available to show the charts.")

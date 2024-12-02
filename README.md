Budget Tracker
Budget Tracker is an AI-powered tool to help you manage and optimize your budget and expenses.

Features
Budget Setup: Set your monthly budget and clear it when needed.
Add Expenses: Log your expenses with descriptions and dates.
Expense Summary: View a summary of your expenses with filters for date and category.
Expense Charts: Visualize your expenses over time with interactive charts.
AI Suggestions: Get personalized suggestions for optimizing your spending.
Installation
Clone the Repository:

git clone https://github.com/geethasagarb/Budget_Tracker.git
cd Budget_Tracker
Set Up the Development Container:
Ensure that Docker is installed on your machine. The project uses Dev Containers for development.

{
  "image": "mcr.microsoft.com/devcontainers/python:1-3.11-bullseye",
  "customizations": {
    "vscode": {
      "extensions": ["ms-python.python", "ms-python.vscode-pylance"]
    }
  },
  "postAttachCommand": {
    "server": "streamlit run budget.py --server.enableCORS false --server.enableXsrfProtection false"
  },
  "forwardPorts": [8501]
}
Usage
Run the Application:

streamlit run budget.py
Login Page:

Username: BANA7085
Password: 12345


Main App:

Navigate through tabs such as Budget Setup, Add Expense, Summary, Expense Charts, and AI Suggestions.
Contributing
Contributions are welcome! Please create issues for any bugs or feature requests and feel free to submit pull requests.

License
This project does not have a license specified.

Contributors
geethasagarb
Repository Information
Languages: Python (100%)

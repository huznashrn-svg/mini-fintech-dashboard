from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

DATABASE = "database.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            type TEXT NOT NULL,
            date TEXT NOT NULL,
            note TEXT
        )
    """)

    conn.commit()
    conn.close()


@app.route('/')
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Filters
    selected_category = request.args.get('category', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')

    # Transaction Query
    query = "SELECT * FROM transactions WHERE 1=1"
    params = []

    if selected_category:
        query += " AND category = ?"
        params.append(selected_category)

    if start_date:
        query += " AND date >= ?"
        params.append(start_date)

    if end_date:
        query += " AND date <= ?"
        params.append(end_date)

    query += " ORDER BY date DESC"

    cursor.execute(query, params)
    transactions = cursor.fetchall()

    # Summary Cards
    cursor.execute("""
        SELECT COALESCE(SUM(amount), 0)
        FROM transactions
        WHERE type='income'
    """)
    total_income = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COALESCE(SUM(amount), 0)
        FROM transactions
        WHERE type='expense'
    """)
    total_expense = cursor.fetchone()[0]

    net_balance = total_income - total_expense

    # Top Spending Category
    cursor.execute("""
        SELECT category, SUM(amount) AS total
        FROM transactions
        WHERE type='expense'
        GROUP BY category
        ORDER BY total DESC
        LIMIT 1
    """)

    result = cursor.fetchone()

    if result:
        top_category = result["category"]
        top_category_amount = result["total"]
    else:
        top_category = "None"
        top_category_amount = 0

    # Pie Chart Data
    cursor.execute("""
        SELECT category, SUM(amount) AS total
        FROM transactions
        WHERE type='expense'
        GROUP BY category
    """)

    chart_data = cursor.fetchall()

    chart_labels = []
    chart_values = []

    for row in chart_data:
        chart_labels.append(row["category"])
        chart_values.append(row["total"])

    # Rule-Based Insight
    insight = "Start tracking your spending to unlock insights."

    if total_expense > 0 and top_category != "None":
        percentage = (top_category_amount / total_expense) * 100

        if percentage >= 40:
            insight = (
                f"{top_category} accounts for "
                f"{percentage:.0f}% of your expenses. "
                "Consider reviewing this category."
            )
        elif net_balance > 0:
            savings_rate = (net_balance / total_income) * 100 if total_income > 0 else 0

            insight = (
                f"Great job! You saved "
                f"{savings_rate:.0f}% of your income."
            )
        else:
            insight = (
                "Your expenses are higher than your savings. "
                "Consider reducing non-essential spending."
            )

    conn.close()

    return render_template(
        'dashboard.html',
        transactions=transactions,
        total_income=total_income,
        total_expense=total_expense,
        net_balance=net_balance,
        top_category=top_category,
        selected_category=selected_category,
        start_date=start_date,
        end_date=end_date,
        chart_labels=chart_labels,
        chart_values=chart_values,
        insight=insight
    )


@app.route('/add', methods=['GET', 'POST'])
def add_transaction():

    if request.method == 'POST':
        amount = float(request.form['amount'])
        category = request.form['category']
        transaction_type = request.form['type']
        date = request.form['date']
        note = request.form.get('note', '')

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO transactions
            (amount, category, type, date, note)
            VALUES (?, ?, ?, ?, ?)
        """, (
            amount,
            category,
            transaction_type,
            date,
            note
        ))

        conn.commit()
        conn.close()

        return redirect('/')

    return render_template('add_transaction.html')

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
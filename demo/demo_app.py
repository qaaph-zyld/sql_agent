#!/usr/bin/env python3
"""
SQL Agent Demo — Streamlit Cloud Edition
Showcases NL-to-SQL capabilities with a sample SQLite database.
Supports OpenAI API for live generation or demo mode with pre-computed results.
"""

import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from pathlib import Path
from datetime import datetime

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DB_PATH = Path(__file__).parent / "sample.db"

DEMO_QUERIES = {
    "Show me the top 10 customers by total spending": {
        "sql": """SELECT c.name, c.country, c.segment,
       COUNT(o.order_id) AS total_orders,
       ROUND(SUM(o.total_amount), 2) AS total_spent
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE o.status != 'Cancelled'
GROUP BY c.customer_id
ORDER BY total_spent DESC
LIMIT 10""",
    },
    "What are the monthly revenue trends for 2025?": {
        "sql": """SELECT strftime('%Y-%m', order_date) AS month,
       COUNT(order_id) AS num_orders,
       ROUND(SUM(total_amount), 2) AS revenue
FROM orders
WHERE order_date >= '2025-01-01' AND status != 'Cancelled'
GROUP BY month
ORDER BY month""",
    },
    "Which product categories generate the most revenue?": {
        "sql": """SELECT p.category,
       COUNT(DISTINCT oi.order_id) AS orders_count,
       SUM(oi.quantity) AS units_sold,
       ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount)), 2) AS revenue
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.status != 'Cancelled'
GROUP BY p.category
ORDER BY revenue DESC""",
    },
    "Show me the average order value by customer segment": {
        "sql": """SELECT c.segment,
       COUNT(o.order_id) AS total_orders,
       ROUND(AVG(o.total_amount), 2) AS avg_order_value,
       ROUND(SUM(o.total_amount), 2) AS total_revenue
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE o.status != 'Cancelled'
GROUP BY c.segment
ORDER BY avg_order_value DESC""",
    },
    "Which countries have the most customers?": {
        "sql": """SELECT country, COUNT(*) AS customer_count,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM customers), 1) AS pct
FROM customers
GROUP BY country
ORDER BY customer_count DESC""",
    },
    "Show order status breakdown": {
        "sql": """SELECT status,
       COUNT(*) AS order_count,
       ROUND(SUM(total_amount), 2) AS total_value
FROM orders
GROUP BY status
ORDER BY order_count DESC""",
    },
    "What are the top 5 best-selling products?": {
        "sql": """SELECT p.name, p.category,
       SUM(oi.quantity) AS units_sold,
       ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount)), 2) AS revenue
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.status != 'Cancelled'
GROUP BY p.product_id
ORDER BY units_sold DESC
LIMIT 5""",
    },
    "Show me employee count and average salary by department": {
        "sql": """SELECT department,
       COUNT(*) AS headcount,
       ROUND(AVG(salary), 2) AS avg_salary,
       ROUND(MIN(salary), 2) AS min_salary,
       ROUND(MAX(salary), 2) AS max_salary
FROM employees
GROUP BY department
ORDER BY avg_salary DESC""",
    },
    "How many new customers did we get each month?": {
        "sql": """SELECT strftime('%Y-%m', created_at) AS month,
       COUNT(*) AS new_customers
FROM customers
GROUP BY month
ORDER BY month""",
    },
    "Show me products with low stock (under 50 units)": {
        "sql": """SELECT name, category, stock_qty, unit_price
FROM products
WHERE stock_qty < 50
ORDER BY stock_qty ASC""",
    },
}

# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def get_connection():
    return sqlite3.connect(DB_PATH)


def run_query(sql: str) -> pd.DataFrame:
    conn = get_connection()
    try:
        df = pd.read_sql_query(sql, conn)
        return df
    finally:
        conn.close()


def get_schema_info() -> str:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [r[0] for r in c.fetchall()]
    schema_parts = []
    for t in tables:
        c.execute(f"PRAGMA table_info({t})")
        cols = c.fetchall()
        col_strs = [f"  {col[1]} {col[2]}{'  PRIMARY KEY' if col[5] else ''}" for col in cols]
        schema_parts.append(f"TABLE {t} (\n" + ",\n".join(col_strs) + "\n)")
    conn.close()
    return "\n\n".join(schema_parts)


# ---------------------------------------------------------------------------
# OpenAI SQL generation
# ---------------------------------------------------------------------------

def generate_sql_openai(question: str, api_key: str, schema: str) -> str:
    """Use OpenAI to generate SQL from natural language."""
    try:
        from openai import OpenAI
    except ImportError:
        return "ERROR: openai package not installed"

    client = OpenAI(api_key=api_key)
    prompt = f"""You are an expert SQL analyst. Given the following SQLite database schema, 
write a SQL query that answers the user's question. Return ONLY the SQL query, no explanation.

DATABASE SCHEMA:
{schema}

RULES:
- Use SQLite syntax (e.g., strftime for dates, LIMIT instead of TOP)
- Always alias aggregated columns
- Use JOINs where needed
- Return only the SQL, no markdown formatting, no code fences

USER QUESTION: {question}

SQL:"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=500,
    )
    sql = response.choices[0].message.content.strip()
    # Clean up any markdown code fences
    if sql.startswith("```"):
        sql = sql.split("\n", 1)[1] if "\n" in sql else sql[3:]
    if sql.endswith("```"):
        sql = sql[:-3]
    return sql.strip()


# ---------------------------------------------------------------------------
# Streamlit UI
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="SQL Agent — NL to SQL Demo",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
<style>
    .block-container { padding-top: 2rem; }
    .main-title { font-size: 2.2rem; font-weight: 800; color: #1a73e8; text-align: center; margin-bottom: 0; }
    .sub-title { text-align: center; color: #5f6368; font-size: 1.1rem; margin-bottom: 2rem; }
    .sql-card { background: #f8f9fa; border-left: 4px solid #1a73e8; padding: 1rem; border-radius: 0.4rem; margin: 0.8rem 0; }
    .metric-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1.2rem;
                   border-radius: 0.8rem; text-align: center; }
    .metric-card h3 { margin: 0; font-size: 2rem; }
    .metric-card p { margin: 0; font-size: 0.85rem; opacity: 0.9; }
    .cta-box { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white;
               padding: 1.5rem; border-radius: 0.8rem; text-align: center; margin-top: 2rem; }
    .cta-box a { color: white; text-decoration: underline; font-weight: bold; }
    .badge { display: inline-block; padding: 0.25rem 0.75rem; border-radius: 1rem; font-size: 0.75rem;
             font-weight: 600; margin-right: 0.5rem; }
    .badge-demo { background: #e8f5e9; color: #2e7d32; }
    .badge-live { background: #e3f2fd; color: #1565c0; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/3d-fluency/94/database.png", width=60)
    st.markdown("## SQL Agent")
    st.markdown("*Natural Language → SQL → Results*")
    st.divider()

    mode = st.radio("Mode", ["🎯 Demo (no API key needed)", "⚡ Live (OpenAI API)"],
                     help="Demo mode uses pre-built queries. Live mode generates SQL with GPT-4o-mini.")

    api_key = ""
    if "Live" in mode:
        api_key = st.text_input("OpenAI API Key", type="password",
                                help="Your key is never stored. Used only for this session.")
        if not api_key:
            st.warning("Enter your OpenAI API key to use Live mode.")

    st.divider()
    st.markdown("### 📊 Sample Database")
    st.markdown("""
    - **200** customers across 10 countries
    - **26** products in 4 categories
    - **1,500** orders with line items
    - **~30** employees in 5 departments
    """)

    # Schema viewer
    with st.expander("🔍 View Database Schema"):
        st.code(get_schema_info(), language="sql")

    st.divider()
    st.markdown("""
    <div class="cta-box">
        <strong>Need this for YOUR database?</strong><br>
        We set up NL-to-SQL for enterprise databases.<br><br>
        <a href="https://nkj-development.netlify.app/contact">📩 Get a Quote</a>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Main content
# ---------------------------------------------------------------------------
st.markdown('<p class="main-title">🤖 SQL Agent</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Ask questions about your data in plain English — get SQL + results + charts instantly</p>', unsafe_allow_html=True)

# Quick stats
col1, col2, col3, col4 = st.columns(4)
try:
    stats = {
        "customers": run_query("SELECT COUNT(*) as n FROM customers").iloc[0, 0],
        "orders": run_query("SELECT COUNT(*) as n FROM orders").iloc[0, 0],
        "revenue": run_query("SELECT ROUND(SUM(total_amount),0) as n FROM orders WHERE status!='Cancelled'").iloc[0, 0],
        "products": run_query("SELECT COUNT(*) as n FROM products").iloc[0, 0],
    }
except Exception:
    stats = {"customers": 200, "orders": 1500, "revenue": 2500000, "products": 26}

with col1:
    st.metric("Customers", f"{stats['customers']:,}")
with col2:
    st.metric("Orders", f"{stats['orders']:,}")
with col3:
    st.metric("Revenue", f"${stats['revenue']:,.0f}")
with col4:
    st.metric("Products", f"{stats['products']:,}")

st.divider()

# --- Demo Mode ---
if "Demo" in mode:
    st.markdown("### 💡 Select a question to see the AI-generated SQL and results")
    selected = st.selectbox("Choose a question:", list(DEMO_QUERIES.keys()))

    if st.button("🔍 Run Query", type="primary", use_container_width=True):
        query_info = DEMO_QUERIES[selected]
        sql = query_info["sql"]

        st.markdown("#### Generated SQL")
        st.code(sql, language="sql")

        with st.spinner("Executing query..."):
            try:
                df = run_query(sql)
                st.markdown(f"#### Results ({len(df)} rows)")
                st.dataframe(df, use_container_width=True)

                # Auto-chart
                numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
                non_numeric_cols = df.select_dtypes(exclude=["number"]).columns.tolist()

                if numeric_cols and non_numeric_cols:
                    fig = px.bar(df, x=non_numeric_cols[0], y=numeric_cols[-1],
                                 title=f"{numeric_cols[-1]} by {non_numeric_cols[0]}",
                                 color_discrete_sequence=["#1a73e8"])
                    fig.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig, use_container_width=True)
                elif numeric_cols and len(df) > 1:
                    fig = px.line(df, y=numeric_cols[-1], title=f"{numeric_cols[-1]} trend",
                                  color_discrete_sequence=["#1a73e8"])
                    st.plotly_chart(fig, use_container_width=True)

            except Exception as e:
                st.error(f"Query error: {e}")

# --- Live Mode ---
else:
    if not api_key:
        st.info("👈 Enter your OpenAI API key in the sidebar to start asking questions.")
        st.stop()

    question = st.text_input("Ask anything about the database:",
                              placeholder="e.g., Which customers spent the most in Q1 2025?")

    if st.button("🔍 Generate & Run SQL", type="primary", use_container_width=True) and question.strip():
        schema = get_schema_info()
        with st.spinner("Generating SQL with GPT-4o-mini..."):
            sql = generate_sql_openai(question, api_key, schema)

        if sql.startswith("ERROR"):
            st.error(sql)
        else:
            st.markdown("#### Generated SQL")
            st.code(sql, language="sql")

            with st.spinner("Executing query..."):
                try:
                    df = run_query(sql)
                    st.markdown(f"#### Results ({len(df)} rows)")
                    st.dataframe(df, use_container_width=True)

                    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
                    non_numeric_cols = df.select_dtypes(exclude=["number"]).columns.tolist()

                    if numeric_cols and non_numeric_cols and len(df) <= 50:
                        fig = px.bar(df, x=non_numeric_cols[0], y=numeric_cols[-1],
                                     title=f"{numeric_cols[-1]} by {non_numeric_cols[0]}",
                                     color_discrete_sequence=["#1a73e8"])
                        fig.update_layout(xaxis_tickangle=-45)
                        st.plotly_chart(fig, use_container_width=True)

                except Exception as e:
                    st.error(f"Query execution error: {e}")
                    st.markdown("The AI-generated SQL may have a syntax issue. Try rephrasing your question.")

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #9e9e9e; font-size: 0.85rem;">
    <strong>SQL Agent</strong> by <a href="https://nkj-development.netlify.app" style="color: #1a73e8;">NKJ Development</a> 
    · Powered by OpenAI + SQLite + Streamlit
    · <a href="https://github.com/qaaph-zyld/sql_agent" style="color: #1a73e8;">GitHub</a>
</div>
""", unsafe_allow_html=True)

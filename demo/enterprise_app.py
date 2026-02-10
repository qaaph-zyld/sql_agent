#!/usr/bin/env python3
"""
SQL Agent Enterprise — Multi-DB NL-to-SQL Platform
Supports SQLite, PostgreSQL, MySQL, and SQL Server.
Team management, query history, and usage analytics.
"""

import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime, timedelta
import json
import hashlib

# ---------------------------------------------------------------------------
# Constants & Config
# ---------------------------------------------------------------------------
DB_PATH = Path(__file__).parent / "sample.db"

SUPPORTED_DATABASES = {
    "SQLite": {"icon": "🗄️", "port": None, "driver": "sqlite3"},
    "PostgreSQL": {"icon": "🐘", "port": 5432, "driver": "psycopg2"},
    "MySQL": {"icon": "🐬", "port": 3306, "driver": "mysqlclient"},
    "SQL Server": {"icon": "🏢", "port": 1433, "driver": "pyodbc"},
}

DEMO_QUERIES = {
    "Top 10 customers by total spending": """SELECT c.name, c.country, c.segment,
       COUNT(o.order_id) AS total_orders,
       ROUND(SUM(o.total_amount), 2) AS total_spent
FROM customers c JOIN orders o ON c.customer_id = o.customer_id
WHERE o.status != 'Cancelled'
GROUP BY c.customer_id ORDER BY total_spent DESC LIMIT 10""",

    "Monthly revenue trends for 2025": """SELECT strftime('%Y-%m', order_date) AS month,
       COUNT(order_id) AS num_orders,
       ROUND(SUM(total_amount), 2) AS revenue
FROM orders WHERE order_date >= '2025-01-01' AND status != 'Cancelled'
GROUP BY month ORDER BY month""",

    "Revenue by product category": """SELECT p.category,
       COUNT(DISTINCT oi.order_id) AS orders_count,
       SUM(oi.quantity) AS units_sold,
       ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount)), 2) AS revenue
FROM order_items oi JOIN products p ON oi.product_id = p.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.status != 'Cancelled' GROUP BY p.category ORDER BY revenue DESC""",

    "Customer segments distribution": """SELECT segment, COUNT(*) AS count,
       ROUND(AVG(JULIANDAY('now') - JULIANDAY(created_at)), 0) AS avg_days_since_signup
FROM customers GROUP BY segment ORDER BY count DESC""",

    "Order status breakdown": """SELECT status, COUNT(*) AS count,
       ROUND(SUM(total_amount), 2) AS total_value
FROM orders GROUP BY status ORDER BY count DESC""",

    "Top products by quantity sold": """SELECT p.name, p.category,
       SUM(oi.quantity) AS total_qty,
       ROUND(SUM(oi.quantity * oi.unit_price), 2) AS gross_revenue
FROM order_items oi JOIN products p ON oi.product_id = p.product_id
GROUP BY p.product_id ORDER BY total_qty DESC LIMIT 10""",
}

# Demo team data
TEAM_MEMBERS = [
    {"name": "Admin User", "email": "admin@company.com", "role": "Admin", "queries": 342, "joined": "2025-10-01"},
    {"name": "Data Analyst", "email": "analyst@company.com", "role": "Analyst", "queries": 1205, "joined": "2025-11-15"},
    {"name": "BI Developer", "email": "bi@company.com", "role": "Developer", "queries": 876, "joined": "2025-12-01"},
    {"name": "Marketing Lead", "email": "marketing@company.com", "role": "Viewer", "queries": 94, "joined": "2026-01-10"},
]

# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def get_connection():
    if not DB_PATH.exists():
        st.error(f"Sample database not found at {DB_PATH}. Run create_sample_db.py first.")
        st.stop()
    return sqlite3.connect(DB_PATH)


def run_query(sql: str) -> pd.DataFrame:
    conn = get_connection()
    try:
        df = pd.read_sql_query(sql, conn)
        return df
    except Exception as e:
        st.error(f"Query error: {e}")
        return pd.DataFrame()
    finally:
        conn.close()


def get_schema_info() -> dict:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    schema = {}
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [{"name": row[1], "type": row[2], "nullable": not row[3], "pk": bool(row[5])} for row in cursor.fetchall()]
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        row_count = cursor.fetchone()[0]
        schema[table] = {"columns": columns, "row_count": row_count}
    conn.close()
    return schema


# ---------------------------------------------------------------------------
# OpenAI integration
# ---------------------------------------------------------------------------

def generate_sql_openai(question: str, schema_context: str) -> str:
    try:
        from openai import OpenAI
        api_key = st.session_state.get("openai_key", "")
        if not api_key:
            return ""
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"You are a SQL expert. Generate ONLY a valid SQL query for SQLite. No explanations.\n\nSchema:\n{schema_context}"},
                {"role": "user", "content": question}
            ],
            temperature=0,
            max_tokens=500,
        )
        sql = response.choices[0].message.content.strip()
        sql = sql.replace("```sql", "").replace("```", "").strip()
        return sql
    except Exception as e:
        st.error(f"OpenAI error: {e}")
        return ""


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------

st.set_page_config(page_title="SQL Agent Enterprise", page_icon="🏢", layout="wide")

st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; }
    .stTabs [data-baseweb="tab-list"] { gap: 4px; }
    .metric-card { background: linear-gradient(135deg, #1e293b, #0f172a); padding: 1.2rem;
                   border-radius: 0.75rem; border: 1px solid #334155; }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 🏢 SQL Agent Enterprise")
    st.caption("Multi-DB NL-to-SQL Platform")
    st.divider()

    # Database connection
    st.markdown("#### Database Connection")
    db_type = st.selectbox("Database Type", list(SUPPORTED_DATABASES.keys()), index=0)
    db_info = SUPPORTED_DATABASES[db_type]

    if db_type == "SQLite":
        st.success(f"✅ Connected to demo database ({DB_PATH.name})")
    else:
        st.text_input("Host", value="localhost", disabled=True)
        st.number_input("Port", value=db_info["port"], disabled=True)
        st.text_input("Database", value="my_database", disabled=True)
        st.info(f"💡 {db_type} connection available in Enterprise plan")

    st.divider()

    # AI Engine
    st.markdown("#### AI Engine")
    engine = st.selectbox("LLM Provider", ["Demo Mode", "OpenAI GPT-4o", "Ollama (Local)", "Azure OpenAI"])

    if engine == "OpenAI GPT-4o":
        api_key = st.text_input("API Key", type="password", key="openai_key_input")
        if api_key:
            st.session_state["openai_key"] = api_key
            st.success("✅ API key set")
    elif engine in ["Ollama (Local)", "Azure OpenAI"]:
        st.info("Available in Enterprise plan")

    st.divider()

    # Plan info
    st.markdown("#### Current Plan")
    plan_col1, plan_col2 = st.columns(2)
    with plan_col1:
        st.metric("Plan", "Enterprise")
    with plan_col2:
        st.metric("Seats", "4/10")

    st.progress(0.65, text="6,500 / 10,000 queries this month")

# Main content
tab_query, tab_schema, tab_team, tab_history, tab_settings = st.tabs(
    ["💬 Query", "📊 Schema Explorer", "👥 Team", "📜 History", "⚙️ Settings"]
)

# ---------------------------------------------------------------------------
# Query Tab
# ---------------------------------------------------------------------------
with tab_query:
    st.markdown("### Ask Your Database Anything")

    col_input, col_examples = st.columns([3, 1])

    with col_input:
        question = st.text_area(
            "Natural Language Query",
            placeholder="e.g., Show me the top customers by spending in Q1 2025",
            height=80,
        )

    with col_examples:
        st.markdown("**Quick Examples:**")
        for label in list(DEMO_QUERIES.keys())[:4]:
            if st.button(label, key=f"ex_{label[:20]}", use_container_width=True):
                question = label

    if st.button("🔍 Generate & Run SQL", type="primary", use_container_width=True) or question:
        if question:
            # Generate SQL
            sql = DEMO_QUERIES.get(question, None)

            if sql is None and engine == "OpenAI GPT-4o" and st.session_state.get("openai_key"):
                schema = get_schema_info()
                schema_text = "\n".join([
                    f"Table: {t} ({info['row_count']} rows)\n  Columns: {', '.join([c['name'] + ' ' + c['type'] for c in info['columns']])}"
                    for t, info in schema.items()
                ])
                with st.spinner("Generating SQL with GPT-4o..."):
                    sql = generate_sql_openai(question, schema_text)
            elif sql is None:
                sql = DEMO_QUERIES[list(DEMO_QUERIES.keys())[0]]
                st.info("💡 Using closest demo query. Enable OpenAI for custom NL-to-SQL generation.")

            # Show SQL
            with st.expander("📝 Generated SQL", expanded=True):
                st.code(sql, language="sql")

            # Run query
            with st.spinner("Executing query..."):
                df = run_query(sql)

            if not df.empty:
                st.markdown(f"**Results:** {len(df)} rows returned")
                st.dataframe(df, use_container_width=True, height=300)

                # Auto-visualization
                if len(df.columns) >= 2:
                    st.markdown("#### 📈 Auto-Visualization")
                    num_cols = df.select_dtypes(include=["number"]).columns.tolist()
                    str_cols = df.select_dtypes(include=["object"]).columns.tolist()

                    if str_cols and num_cols:
                        chart_col1, chart_col2 = st.columns(2)
                        with chart_col1:
                            fig = px.bar(df.head(15), x=str_cols[0], y=num_cols[-1],
                                        title=f"{num_cols[-1]} by {str_cols[0]}",
                                        color_discrete_sequence=["#3b82f6"])
                            fig.update_layout(height=350)
                            st.plotly_chart(fig, use_container_width=True)
                        with chart_col2:
                            if len(num_cols) >= 2:
                                fig2 = px.scatter(df, x=num_cols[0], y=num_cols[-1],
                                                  text=str_cols[0] if str_cols else None,
                                                  title=f"{num_cols[-1]} vs {num_cols[0]}",
                                                  color_discrete_sequence=["#8b5cf6"])
                                fig2.update_layout(height=350)
                                st.plotly_chart(fig2, use_container_width=True)
                            else:
                                fig2 = px.pie(df.head(8), names=str_cols[0], values=num_cols[0],
                                              title=f"{num_cols[0]} Distribution")
                                fig2.update_layout(height=350)
                                st.plotly_chart(fig2, use_container_width=True)

                # Export
                csv = df.to_csv(index=False)
                st.download_button("📥 Download CSV", csv, f"query_results_{datetime.now():%Y%m%d_%H%M}.csv", "text/csv")

# ---------------------------------------------------------------------------
# Schema Explorer Tab
# ---------------------------------------------------------------------------
with tab_schema:
    st.markdown("### Database Schema")
    schema = get_schema_info()

    schema_cols = st.columns(len(schema))
    for i, (table, info) in enumerate(schema.items()):
        with schema_cols[i % len(schema_cols)]:
            st.markdown(f"#### 📋 {table}")
            st.caption(f"{info['row_count']:,} rows")
            for col in info["columns"]:
                pk_icon = "🔑 " if col["pk"] else ""
                st.markdown(f"- {pk_icon}`{col['name']}` *{col['type']}*")

    # ERD visualization
    st.markdown("#### Relationships")
    st.code("""
customers (1) ──→ (N) orders
orders    (1) ──→ (N) order_items
products  (1) ──→ (N) order_items
    """, language=None)

# ---------------------------------------------------------------------------
# Team Tab
# ---------------------------------------------------------------------------
with tab_team:
    st.markdown("### Team Management")

    team_col1, team_col2 = st.columns([3, 1])
    with team_col2:
        st.button("➕ Invite Member", use_container_width=True)

    st.dataframe(
        pd.DataFrame(TEAM_MEMBERS),
        use_container_width=True,
        column_config={
            "name": st.column_config.TextColumn("Name", width="medium"),
            "email": st.column_config.TextColumn("Email", width="medium"),
            "role": st.column_config.SelectboxColumn("Role", options=["Admin", "Analyst", "Developer", "Viewer"], width="small"),
            "queries": st.column_config.NumberColumn("Queries", format="%d"),
            "joined": st.column_config.DateColumn("Joined"),
        },
        hide_index=True,
    )

    st.markdown("#### Role Permissions")
    perms = pd.DataFrame({
        "Permission": ["Run queries", "View schema", "Export results", "Manage team", "Configure DB", "View audit log", "API access"],
        "Admin": ["✅"] * 7,
        "Analyst": ["✅", "✅", "✅", "❌", "❌", "✅", "✅"],
        "Developer": ["✅", "✅", "✅", "❌", "✅", "✅", "✅"],
        "Viewer": ["✅", "✅", "❌", "❌", "❌", "❌", "❌"],
    })
    st.dataframe(perms, use_container_width=True, hide_index=True)

# ---------------------------------------------------------------------------
# History Tab
# ---------------------------------------------------------------------------
with tab_history:
    st.markdown("### Query History")

    demo_history = [
        {"time": "2026-02-10 00:45", "user": "analyst@company.com", "query": "Top customers by spending", "rows": 10, "ms": 45},
        {"time": "2026-02-10 00:42", "user": "admin@company.com", "query": "Monthly revenue trends", "rows": 8, "ms": 32},
        {"time": "2026-02-09 23:15", "user": "bi@company.com", "query": "Product category revenue", "rows": 5, "ms": 28},
        {"time": "2026-02-09 22:30", "user": "analyst@company.com", "query": "Order status breakdown", "rows": 4, "ms": 18},
        {"time": "2026-02-09 21:10", "user": "marketing@company.com", "query": "Customer segments", "rows": 3, "ms": 22},
    ]

    st.dataframe(
        pd.DataFrame(demo_history),
        use_container_width=True,
        column_config={
            "time": st.column_config.TextColumn("Timestamp"),
            "user": st.column_config.TextColumn("User"),
            "query": st.column_config.TextColumn("Query", width="large"),
            "rows": st.column_config.NumberColumn("Rows"),
            "ms": st.column_config.NumberColumn("Time (ms)", format="%dms"),
        },
        hide_index=True,
    )

    # Usage chart
    st.markdown("#### Usage Over Time")
    dates = pd.date_range(end=datetime.now(), periods=14, freq="D")
    usage_df = pd.DataFrame({
        "date": dates,
        "queries": [45, 62, 38, 91, 78, 55, 42, 88, 95, 71, 63, 107, 89, 112],
    })
    fig = px.area(usage_df, x="date", y="queries", title="Daily Query Volume",
                  color_discrete_sequence=["#3b82f6"])
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------------------
# Settings Tab
# ---------------------------------------------------------------------------
with tab_settings:
    st.markdown("### Enterprise Settings")

    settings_col1, settings_col2 = st.columns(2)

    with settings_col1:
        st.markdown("#### Subscription")
        st.markdown("""
        | | |
        |---|---|
        | **Plan** | Enterprise |
        | **Price** | $199/month |
        | **Seats** | 4 / 10 |
        | **Queries** | 6,500 / 10,000 |
        | **Databases** | 2 / 5 |
        | **Renewal** | March 10, 2026 |
        """)

        st.markdown("#### Connected Databases")
        for db_name, status in [("Production SQLite (demo)", "🟢 Connected"), ("Analytics PostgreSQL", "🔴 Not configured")]:
            st.markdown(f"- {status} — {db_name}")

    with settings_col2:
        st.markdown("#### Security")
        st.toggle("Enable SSO (SAML)", value=False, disabled=True)
        st.toggle("Enforce 2FA", value=True, disabled=True)
        st.toggle("IP Allowlisting", value=False, disabled=True)
        st.toggle("Audit Logging", value=True, disabled=True)
        st.toggle("Query Rate Limiting", value=True, disabled=True)

        st.markdown("#### API")
        st.text_input("API Endpoint", value="https://api.sql-agent.dev/v1", disabled=True)
        st.code("sk-ent-...7f3d", language=None)

    # Pricing CTA
    st.divider()
    st.markdown("### Upgrade Your Plan")
    pricing_cols = st.columns(3)

    plans = [
        {"name": "Starter", "price": "$49/mo", "features": ["1 user", "1 database", "1,000 queries/mo", "Community support"]},
        {"name": "Team", "price": "$99/mo", "features": ["5 users", "3 databases", "5,000 queries/mo", "Priority support", "Query history"]},
        {"name": "Enterprise", "price": "$199/mo", "features": ["10 users", "5 databases", "10,000 queries/mo", "24/7 support", "SSO/SAML", "Audit logs", "API access"]},
    ]

    for i, plan in enumerate(plans):
        with pricing_cols[i]:
            current = plan["name"] == "Enterprise"
            st.markdown(f"**{plan['name']}** {'✅ Current' if current else ''}")
            st.markdown(f"### {plan['price']}")
            for f in plan["features"]:
                st.markdown(f"- ✓ {f}")
            if not current:
                st.button(f"Switch to {plan['name']}", key=f"plan_{plan['name']}", use_container_width=True)

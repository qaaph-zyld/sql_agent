#!/usr/bin/env python3
"""
Streamlit Web Interface for SQL Agent
Provides a user-friendly web interface for natural language to SQL queries
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import logging
from pathlib import Path

# Import our SQL Agent
from sql_agent import EnhancedSQLAgent

# Configure page
st.set_page_config(
    page_title="SQL Agent - Natural Language to SQL",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sql-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #ffe6e6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ff4444;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #e6ffe6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #44ff44;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def initialize_agent():
    """Initialize the SQL Agent (cached to avoid reinitialization)"""
    try:
        agent = EnhancedSQLAgent()
        return agent
    except Exception as e:
        st.error(f"Failed to initialize SQL Agent: {e}")
        return None

@st.cache_data
def train_agent_cached(_agent):
    """Train the agent (cached to avoid retraining)"""
    if _agent:
        try:
            _agent.train_vanna()
            return True, "Agent trained successfully!"
        except Exception as e:
            return False, f"Training failed: {e}"
    return False, "Agent not initialized"

def display_results(result):
    """Display query results in a formatted way"""
    if result['error']:
        st.markdown(f'<div class="error-box"><strong>Error:</strong> {result["error"]}</div>', 
                   unsafe_allow_html=True)
        return
    
    if result['sql']:
        st.markdown('<div class="sql-box"><strong>Generated SQL:</strong></div>', 
                   unsafe_allow_html=True)
        st.code(result['sql'], language='sql')
    
    if result['results'] is not None and not result['results'].empty:
        st.markdown(f'<div class="success-box"><strong>Results ({result["row_count"]} rows):</strong></div>', 
                   unsafe_allow_html=True)
        
        # Display results table
        st.dataframe(result['results'], use_container_width=True)
        
        # Offer to create visualizations for numeric data
        numeric_columns = result['results'].select_dtypes(include=['number']).columns.tolist()
        if len(numeric_columns) > 0:
            create_visualization(result['results'], numeric_columns)
    else:
        st.info("Query executed successfully but returned no results.")

def create_visualization(df, numeric_columns):
    """Create visualizations for numeric data"""
    if len(df) == 0:
        return
    
    st.subheader("📊 Data Visualization")
    
    col1, col2 = st.columns(2)
    
    with col1:
        chart_type = st.selectbox("Chart Type", ["Bar Chart", "Line Chart", "Scatter Plot", "Histogram"])
    
    with col2:
        if chart_type in ["Bar Chart", "Line Chart", "Scatter Plot"]:
            y_column = st.selectbox("Y-axis", numeric_columns)
        else:
            y_column = st.selectbox("Column", numeric_columns)
    
    try:
        if chart_type == "Bar Chart":
            # Use first non-numeric column as x-axis, or index if all numeric
            non_numeric_cols = df.select_dtypes(exclude=['number']).columns.tolist()
            if non_numeric_cols:
                x_column = non_numeric_cols[0]
                # Group by x_column and sum y_column if needed
                if len(df) > 20:  # Aggregate if too many rows
                    plot_df = df.groupby(x_column)[y_column].sum().reset_index()
                else:
                    plot_df = df
                fig = px.bar(plot_df, x=x_column, y=y_column, title=f"{y_column} by {x_column}")
            else:
                fig = px.bar(df.head(20), y=y_column, title=f"{y_column} Distribution")
        
        elif chart_type == "Line Chart":
            fig = px.line(df, y=y_column, title=f"{y_column} Trend")
        
        elif chart_type == "Scatter Plot":
            if len(numeric_columns) > 1:
                x_column = st.selectbox("X-axis", [col for col in numeric_columns if col != y_column])
                fig = px.scatter(df, x=x_column, y=y_column, title=f"{y_column} vs {x_column}")
            else:
                fig = px.scatter(df, y=y_column, title=f"{y_column} Distribution")
        
        elif chart_type == "Histogram":
            fig = px.histogram(df, x=y_column, title=f"{y_column} Distribution")
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error creating visualization: {e}")

def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown('<h1 class="main-header">🤖 SQL Agent</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Ask questions about your database in natural language</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Initialize agent
        agent = initialize_agent()
        
        if agent is None:
            st.error("❌ Agent initialization failed")
            st.stop()
        
        # Training status
        st.subheader("🎓 Training Status")
        if st.button("Train Agent", help="Train the agent with database schema and examples"):
            with st.spinner("Training agent..."):
                success, message = train_agent_cached(agent)
                if success:
                    st.success(message)
                    agent.is_trained = True
                else:
                    st.error(message)
        
        # Database info
        st.subheader("🗄️ Database Info")
        st.info(f"**Server:** {agent.config['database']['server']}\n**Database:** {agent.config['database']['database']}")
        
        # Example questions
        st.subheader("💡 Example Questions")
        example_questions = [
            "Show me the top 10 sales orders",
            "How many parts are in the system?",
            "Which customers have the most orders?",
            "Show me recent transactions",
            "What are the most popular parts?"
        ]
        
        for question in example_questions:
            if st.button(question, key=f"example_{question}"):
                st.session_state.current_question = question
    
    # Main content area
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Question input
        question = st.text_input(
            "Ask a question about your database:",
            value=st.session_state.get('current_question', ''),
            placeholder="e.g., Show me all customers with orders in the last month",
            help="Type your question in natural language"
        )
    
    with col2:
        st.write("")  # Spacing
        ask_button = st.button("🔍 Ask", type="primary", use_container_width=True)
    
    # Process question
    if ask_button and question.strip():
        if not agent.is_trained:
            st.warning("⚠️ Agent not trained yet. Training now...")
            with st.spinner("Training agent..."):
                success, message = train_agent_cached(agent)
                if not success:
                    st.error(f"Training failed: {message}")
                    st.stop()
                agent.is_trained = True
        
        with st.spinner("Processing your question..."):
            result = agent.ask_question(question)
        
        # Display results
        display_results(result)
        
        # Save to history
        if 'query_history' not in st.session_state:
            st.session_state.query_history = []
        
        st.session_state.query_history.append({
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'question': question,
            'sql': result.get('sql', ''),
            'success': result.get('error') is None,
            'row_count': result.get('row_count', 0)
        })
    
    # Query History
    if 'query_history' in st.session_state and st.session_state.query_history:
        st.subheader("📝 Query History")
        
        # Create history dataframe
        history_df = pd.DataFrame(st.session_state.query_history)
        
        # Display in expandable sections
        for idx, row in history_df.iterrows():
            status_icon = "✅" if row['success'] else "❌"
            with st.expander(f"{status_icon} {row['timestamp']} - {row['question'][:50]}..."):
                st.write(f"**Question:** {row['question']}")
                if row['sql']:
                    st.code(row['sql'], language='sql')
                st.write(f"**Status:** {'Success' if row['success'] else 'Failed'}")
                if row['success']:
                    st.write(f"**Rows returned:** {row['row_count']}")
        
        # Clear history button
        if st.button("🗑️ Clear History"):
            st.session_state.query_history = []
            st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown(
        '<p style="text-align: center; color: #666; font-size: 0.9rem;">'
        'Powered by Vanna.AI, Ollama, and Streamlit | '
        'Built for QADEE2798 Database'
        '</p>', 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()

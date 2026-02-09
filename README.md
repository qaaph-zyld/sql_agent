# SQL Agent - Natural Language to SQL Converter

An intelligent SQL agent that converts natural language questions into SQL queries using AI. Built with Vanna.AI, Ollama, and Streamlit for the QADEE2798 database.

## 🌟 Features

- **Natural Language Processing**: Ask questions in plain English and get SQL queries
- **AI-Powered**: Uses Vanna.AI with RAG (Retrieval-Augmented Generation) for accurate SQL generation
- **Open Source**: Built entirely with free, open-source tools
- **Web Interface**: User-friendly Streamlit web application
- **Database Integration**: Direct connection to QADEE2798 SQL Server database
- **Training System**: Learns from your database schema, examples, and business context
- **Visualization**: Automatic chart generation for query results

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit     │    │   SQL Agent     │    │   Database      │
│   Web UI        │◄──►│   (Vanna.AI)    │◄──►│   QADEE2798     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Ollama        │
                       │   (Llama3)      │
                       └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   ChromaDB      │
                       │   Vector Store  │
                       └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+**
2. **Ollama** - Install from [https://ollama.ai/](https://ollama.ai/)
3. **SQL Server Access** - Connection to QADEE2798 database

### Installation

1. **Clone and setup:**
   ```bash
   git clone <your-repo-url>
   cd SQL_agent
   python setup.py
   ```

2. **Start Ollama (if not running):**
   ```bash
   ollama serve
   ```

3. **Configure database connection** (if needed):
   Edit `.env` file with your database credentials

4. **Run the web interface:**
   ```bash
   streamlit run streamlit_app.py
   ```

5. **Or use command line:**
   ```bash
   python sql_agent.py
   ```

## 📁 Project Structure

```
SQL_agent/
├── sql_agent.py                 # Main SQL Agent implementation
├── streamlit_app.py             # Web interface
├── training_data_extractor.py   # Extracts training data from docs
├── setup.py                     # Setup and installation script
├── requirements.txt             # Python dependencies
├── config.json                  # Configuration file
├── .env                         # Environment variables (created by setup)
├── README.md                    # This file
├── existing_repo/               # Cloned qaaph-zyld/sql_agent repository
├── initial_docs/                # Initial documentation
├── logs/                        # Application logs
├── chroma_db/                   # ChromaDB vector database
└── data/                        # Training data and exports
```

## 🎯 Usage Examples

### Web Interface

1. Open the Streamlit app: `streamlit run streamlit_app.py`
2. Click "Train Agent" in the sidebar
3. Ask questions like:
   - "Show me the top 10 sales orders"
   - "How many parts are in the system?"
   - "Which customers have the most orders?"
   - "Show me recent transactions"

### Command Line

```python
from sql_agent import EnhancedSQLAgent

# Initialize agent
agent = EnhancedSQLAgent()

# Train with database knowledge
agent.train_vanna()

# Ask questions
result = agent.ask_question("Show me all customers with orders in the last month")
print(result['sql'])
print(result['results'])
```

## 🧠 How It Works

### 1. Training Phase
- **Schema Extraction**: Automatically extracts database schema (tables, columns, relationships)
- **Example Queries**: Learns from provided SQL examples
- **Business Context**: Incorporates business rules and documentation
- **Vector Storage**: Stores knowledge in ChromaDB for fast retrieval

### 2. Query Processing
- **Natural Language Input**: User asks question in plain English
- **Context Retrieval**: RAG system finds relevant schema and examples
- **SQL Generation**: Ollama/Llama3 generates SQL based on context
- **Validation**: Validates generated SQL for safety and correctness
- **Execution**: Runs SQL against database and returns results

### 3. Result Presentation
- **Data Display**: Shows query results in formatted tables
- **SQL Transparency**: Displays generated SQL for verification
- **Visualizations**: Creates charts for numeric data
- **History**: Maintains query history for reference

## ⚙️ Configuration

### Database Configuration
Edit `.env` file:
```env
DB_SERVER=your_server
DB_NAME=your_database
DB_USERNAME=your_username
DB_PASSWORD=your_password
```

### AI Model Configuration
```env
OLLAMA_MODEL=llama3        # Or other Ollama models
OLLAMA_TEMPERATURE=0.1     # Lower = more deterministic
```

### Advanced Configuration
Edit `config.json` for detailed settings:
```json
{
  "database": { ... },
  "vanna": {
    "model": "llama3",
    "temperature": 0.1,
    "chroma_path": "./chroma_db"
  },
  "training": {
    "auto_train_on_startup": true,
    "include_business_context": true
  }
}
```

## 🔧 Customization

### Adding Training Data

1. **SQL Examples**: Add to `data/training_data.json`
2. **Business Rules**: Update `Column_prompts.md` in existing_repo
3. **Documentation**: Add business context to training

### Custom Models

Replace Ollama model:
```python
# In sql_agent.py, change model configuration
"model": "mistral"  # or other Ollama models
```

### Database Support

Currently supports SQL Server. To add other databases:
1. Update connection string in `_create_database_engine()`
2. Modify schema extraction queries
3. Update Vanna database connection method

## 🛠️ Troubleshooting

### Common Issues

1. **Ollama not found**
   ```bash
   # Install Ollama and pull model
   ollama pull llama3
   ollama serve
   ```

2. **Database connection failed**
   - Check credentials in `.env`
   - Verify SQL Server is accessible
   - Check ODBC driver installation

3. **Training fails**
   - Ensure database connection works
   - Check if existing_repo is cloned
   - Verify training data files exist

4. **Slow responses**
   - Use smaller Ollama model (e.g., `llama3:8b`)
   - Increase temperature for faster generation
   - Check system resources

### Logs

Check logs for detailed error information:
- `sql_agent.log` - Main application logs
- `logs/` directory - Component-specific logs

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit pull request

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- **Vanna.AI** - RAG framework for SQL generation
- **Ollama** - Local LLM serving
- **Streamlit** - Web application framework
- **qaaph-zyld/sql_agent** - Base repository and database documentation

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review logs for error details
3. Open an issue on GitHub
4. Check Vanna.AI and Ollama documentation

---

**Built with ❤️ for intelligent database interaction**

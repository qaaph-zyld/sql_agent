# SQL Agent Deployment Guide

## 🚀 Quick Deployment

### Step 1: Install Dependencies
```bash
pip install pandas sqlalchemy streamlit plotly python-dotenv vanna chromadb ollama
```

### Step 2: Install and Setup Ollama
1. Download Ollama from [https://ollama.ai/](https://ollama.ai/)
2. Install and start Ollama:
   ```bash
   ollama serve
   ```
3. Pull the Llama3 model:
   ```bash
   ollama pull llama3
   ```

### Step 3: Configure Database Connection
1. Copy `.env.template` to `.env`:
   ```bash
   copy .env.template .env
   ```
2. Edit `.env` with your database credentials:
   ```env
   DB_SERVER=your_server
   DB_NAME=QADEE2798
   DB_USERNAME=your_username
   DB_PASSWORD=your_password
   ```

### Step 4: Extract Training Data
```bash
python training_data_extractor.py
```

### Step 5: Launch the Application
```bash
streamlit run streamlit_app.py
```

The application will be available at `http://localhost:8501`

## 🔧 Advanced Configuration

### Custom Model Configuration
Edit `config.json` to use different models:
```json
{
  "vanna": {
    "model": "mistral",
    "temperature": 0.2
  }
}
```

### Database Connection Options
The system supports various connection methods:
- Windows Authentication
- SQL Server Authentication
- Connection strings
- Environment variables

### Training Data Customization
Add your own training data in `data/training_data.json`:
```json
{
  "example_queries": [
    {
      "sql": "SELECT * FROM your_table",
      "description": "Get all records"
    }
  ]
}
```

## 🧪 Testing

Run the test suite to verify everything is working:
```bash
python simple_test.py
```

## 🌐 Web Interface Features

- **Natural Language Input**: Ask questions in plain English
- **SQL Generation**: Automatic SQL query generation
- **Result Visualization**: Charts and graphs for numeric data
- **Query History**: Track previous queries and results
- **Training Management**: Train the AI with your data

## 📊 Usage Examples

### Example Questions
- "Show me the top 10 sales orders"
- "How many customers do we have?"
- "What are the most popular products?"
- "Show me orders from last month"
- "Which vendors have the most purchase orders?"

### Expected Workflow
1. **First Time**: Click "Train Agent" to load database knowledge
2. **Ask Questions**: Type natural language questions
3. **Review Results**: Check generated SQL and data results
4. **Visualize**: Use automatic charts for numeric data
5. **Iterate**: Refine questions based on results

## 🔒 Security Considerations

- Database credentials are stored in `.env` file (not in code)
- SQL queries are validated before execution
- Only SELECT queries are recommended for safety
- Database contents never leave your environment

## 🛠️ Troubleshooting

### Common Issues

1. **"Ollama not found"**
   - Install Ollama from https://ollama.ai/
   - Ensure `ollama serve` is running

2. **"Database connection failed"**
   - Check credentials in `.env` file
   - Verify SQL Server is accessible
   - Check ODBC driver installation

3. **"Training data not found"**
   - Run `python training_data_extractor.py`
   - Ensure `existing_repo` directory exists

4. **"Slow responses"**
   - Use smaller model (e.g., `llama3:8b`)
   - Increase temperature for faster generation
   - Check system resources

### Log Files
Check these files for detailed error information:
- `sql_agent.log` - Main application logs
- `logs/` directory - Component-specific logs

## 📈 Performance Optimization

### Model Selection
- **llama3:8b** - Faster, good for simple queries
- **llama3:13b** - Balanced performance and accuracy
- **codellama** - Specialized for code generation

### System Requirements
- **Minimum**: 8GB RAM, 4GB free disk space
- **Recommended**: 16GB RAM, SSD storage
- **GPU**: Optional but improves performance

### Caching
The system uses multiple caching layers:
- Schema caching for database structure
- Vector store for training data
- Query result caching (optional)

## 🔄 Updates and Maintenance

### Updating Training Data
When database schema changes:
1. Run `python training_data_extractor.py`
2. Restart the application
3. Click "Train Agent" to refresh knowledge

### Model Updates
To use newer Ollama models:
1. `ollama pull new_model_name`
2. Update `config.json` or `.env`
3. Restart application

### Backup
Important files to backup:
- `.env` (database credentials)
- `config.json` (configuration)
- `chroma_db/` (trained knowledge)
- `data/` (training data)

## 🤝 Support

For issues:
1. Check this deployment guide
2. Review log files
3. Run `python simple_test.py`
4. Check Vanna.AI documentation
5. Check Ollama documentation

## 📝 License

This project is open source under the MIT License.

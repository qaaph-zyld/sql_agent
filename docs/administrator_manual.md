# SQL Agent Administrator Manual

*Last updated: 2025-06-04*

## Overview

This administrator manual provides instructions for installing, configuring, and maintaining the SQL Agent system. It is intended for system administrators and technical staff responsible for the deployment and operation of the SQL Agent.

## Installation

### System Requirements

- **Operating System**: Linux (Ubuntu 20.04+, CentOS 8+), Windows Server 2019+
- **CPU**: 4+ cores recommended
- **Memory**: 8GB+ RAM
- **Storage**: 50GB+ free space
- **Database**: PostgreSQL 12+, MySQL 8+, or SQL Server 2019+
- **Python**: Version 3.8+

### Installation Steps

1. **Clone the Repository**

```bash
git clone https://github.com/example/sql-agent.git
cd sql-agent
```

2. **Create Virtual Environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure Environment**

Copy the example environment file and update with your settings:

```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Initialize the Database**

```bash
python scripts/setup/initialize_db.py
```

6. **Start the Service**

```bash
python scripts/core/run_server.py
```

## Configuration

### Core Configuration

The main configuration file is `.env` in the root directory. Key settings include:

```
# Database Connection
DB_HOST=localhost
DB_PORT=5432
DB_NAME=sqlagent
DB_USER=admin
DB_PASSWORD=secure_password

# API Settings
API_PORT=8000
API_HOST=0.0.0.0
API_DEBUG=false

# Security
SECRET_KEY=your_secret_key
ENABLE_AUTH=true
AUTH_METHOD=jwt

# Logging
LOG_LEVEL=info
LOG_DIR=logs
```

### Security Configuration

Security settings are managed in `config/security_config.json`:

```json
{
  "allowed_tables": ["public_data", "shared_data"],
  "restricted_tables": ["user_data", "sensitive_data"],
  "query_timeout_seconds": 30,
  "max_rows_returned": 10000,
  "enable_query_validation": true,
  "enable_sql_injection_protection": true
}
```

### Logging Configuration

Logging is configured in `config/logging_config.json`:

```json
{
  "version": 1,
  "formatters": {
    "standard": {
      "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    }
  },
  "handlers": {
    "console": {
      "class": "logging.StreamHandler",
      "level": "INFO",
      "formatter": "standard"
    },
    "file": {
      "class": "logging.handlers.RotatingFileHandler",
      "level": "INFO",
      "formatter": "standard",
      "filename": "logs/sql_agent.log",
      "maxBytes": 10485760,
      "backupCount": 10
    }
  },
  "loggers": {
    "": {
      "handlers": ["console", "file"],
      "level": "INFO"
    }
  }
}
```

## User Management

### Adding Users

```bash
python scripts/admin/add_user.py --username john.doe --email john.doe@example.com --role analyst
```

### Managing Roles

Available roles:
- `admin`: Full system access
- `analyst`: Can create and execute queries
- `viewer`: Can only view saved queries and results

To change a user's role:

```bash
python scripts/admin/update_user.py --username john.doe --role admin
```

### API Key Management

Generate an API key for a user:

```bash
python scripts/admin/generate_api_key.py --username john.doe
```

Revoke an API key:

```bash
python scripts/admin/revoke_api_key.py --key API_KEY_VALUE
```

## Maintenance

### Backup and Restore

#### Database Backup

```bash
python scripts/maintenance/backup_database.py --output backup/sqlagent_db_backup.sql
```

#### Configuration Backup

```bash
python scripts/maintenance/backup_config.py --output backup/sqlagent_config_backup.zip
```

#### System Restore

```bash
python scripts/maintenance/restore_system.py --db-backup backup/sqlagent_db_backup.sql --config-backup backup/sqlagent_config_backup.zip
```

### Log Management

#### Log Rotation

Logs are automatically rotated based on the configuration in `logging_config.json`.

To manually rotate logs:

```bash
python scripts/maintenance/rotate_logs.py
```

#### Log Analysis

```bash
python scripts/maintenance/analyze_logs.py --days 7 --output log_analysis_report.html
```

## Monitoring

### Health Check

```bash
python scripts/monitoring/health_check.py
```

### Performance Monitoring

```bash
python scripts/monitoring/performance_monitor.py --duration 3600 --interval 60
```

### Alert Configuration

Edit `config/alerts_config.json` to configure alert thresholds and notification methods.

## Troubleshooting

### Common Issues

#### Service Won't Start

Check:
- Database connection settings in `.env`
- Port availability
- Python environment

#### Slow Query Performance

Check:
- Database indexes
- Query complexity
- Database server resources

#### Authentication Failures

Check:
- User permissions
- API key validity
- Authentication configuration

### Diagnostic Tools

```bash
# Run system diagnostics
python scripts/tools/run_diagnostics.py --comprehensive

# Check database connection
python scripts/tools/check_db_connection.py

# Validate configuration
python scripts/tools/validate_config.py
```

## Security Best Practices

1. **Regular Updates**: Keep the system updated with the latest security patches
2. **Strong Passwords**: Enforce strong password policies
3. **API Key Rotation**: Rotate API keys regularly
4. **Access Control**: Limit access to sensitive data
5. **Audit Logging**: Enable audit logging for all critical operations
6. **Network Security**: Deploy behind a firewall and use HTTPS

## Appendix

### Command Reference

A complete list of administrative commands is available in `docs/command_reference.md`.

### Configuration Reference

Detailed configuration options are documented in `docs/configuration_reference.md`.

### Changelog Integration

The SQL Agent implements a comprehensive changelog system. Ensure that all system changes follow the changelog protocol as described in `docs/changelog_system_guide.md`.

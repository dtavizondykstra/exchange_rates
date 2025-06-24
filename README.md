# Exchange Rates ETL - Simplified for Raspberry Pi

A simple ETL pipeline for fetching and storing exchange rate data, optimized for deployment on Raspberry Pi.

## Structure

```
.
├── main.py                 # Main ETL script
├── config.py              # Configuration management
├── extract.py             # Data extraction from API
├── transform.py           # Data transformation
├── load.py                # Data loading to MySQL
├── db_utilities.py        # Database utilities
├── data_utilities.py      # Data processing utilities
├── logging_utilities.py   # Logging setup
├── requirements.txt       # Python dependencies
├── deploy.sh             # Deployment script
├── .env                  # Environment variables (create from template)
├── configs/
│   └── default.yaml      # Application configuration
├── data/
│   ├── processed/        # Generated CSV files
│   └── raw/             # Sample data
├── logs/                # Application logs
├── scripts/             # Utility scripts
└── sql/                # Database schema files
```

## Quick Setup for Raspberry Pi

1. **Clone and deploy:**
   ```bash
   git clone <your-repo>
   cd exchange_rates
   chmod +x deploy.sh
   ./deploy.sh
   ```

2. **Configure environment:**
   Edit the `.env` file with your API key and database credentials:
   ```bash
   nano .env
   ```

3. **Run the ETL:**
   ```bash
   python3 main.py
   ```

4. **Set up daily automation:**
   ```bash
   crontab -e
   # Add: 0 9 * * * /full/path/to/exchange_rates/scripts/run_daily.sh
   ```

## Dependencies

- Python 3.8+
- PyYAML
- python-dotenv
- requests
- mysql-connector-python
- pandas (optional, for data analysis)

## Features

- ✅ Simple flat structure (no complex package hierarchy)
- ✅ Easy deployment on Raspberry Pi
- ✅ Environment-based configuration
- ✅ Comprehensive logging
- ✅ Error handling and recovery
- ✅ Sample data for testing
- ✅ Automated daily runs via cron

## Usage

```python
# Run with sample data (for testing)
python3 main.py

# Run with live API data (modify main.py: use_sample=False)
python3 main.py
```

This structure is much simpler than a full Python package and perfect for Raspberry Pi deployment!

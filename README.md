
# AVGO Options Scanner & Dashboard

This project is a Python-based options scanner and interactive dashboard for analyzing **weekly AVGO (Broadcom) options activity**, with a focus on **high-volume calls and puts**.

It consists of:
- A **scanner** that pulls options data from Yahoo Finance and saves it daily
- A **Streamlit dashboard** that visualizes volume and open interest by strike and over time

---

## 📊 Features

### Scanner
- Pulls options data using `yfinance`
- Automatically selects the **nearest valid expiration**
- Filters options by minimum volume threshold
- Supports **both calls and puts**
- Appends historical scan results to a CSV file
- Designed for automation (daily runs)

### Dashboard
- Interactive Streamlit UI
- Toggle between **Calls / Puts / Both**
- View:
  - Volume by strike
  - Total volume over time
  - Side-by-side call and put tables
- Always displays the **latest scan**

---

## 📸 Dashboard Preview

### Main Dashboard
![Main Dashboard](images/dashboard_main.png)

### Options Pressure Heatmap
![Pressure Heatmap](images/pressure_heatmap.png)

### Volume Analysis
![Volume Analysis](images/volume_analysis.png)

The dashboard provides an interactive view of AVGO options activity, including:
- Current AVGO price and daily change
- Volume and open interest by strike
- Call vs Put pressure visualization
- Historical volume trends
- Dynamic filtering for Calls, Puts, or Both

---

## 📁 Project Structure
```text
options_scanner/
│
├── scanner.py          # Automated options scanner
├── dashboard.py        # Streamlit dashboard
├── scanner_log.txt     # Scan execution logs
├── avgo_options.csv    # Historical options data
├── README.md           # Project documentation
└── requirements.txt    # Project dependencies
```

## ⚙️ Requirements

Python 3.9+

Install dependencies:

```bash
pip install yfinance pandas streamlit matplotlib
```

---

## 🚀 How to Run the Scanner

The scanner pulls the latest options data and appends it to the CSV.
```bash
python scanner.py
```

What it does:

- Fetches the nearest expiration for AVGO
- Filters options with volume > 500
- Saves calls and puts to avgo_options.csv


You can run this:

- Manually
- Daily via Task Scheduler (Windows) or cron (Mac/Linux)


## 📈 How to Run the Dashboard

Start the Streamlit app:
```bash
streamlit run dashboard.py
```
Then open the URL shown in your terminal (usually http://localhost:8501)

---

## 🤖 Automation & Logging

The scanner is designed to run automatically using Windows Task Scheduler.

Features include:
- Scheduled scanning during market hours
- Persistent scan history
- Execution logging
- Error tracking and troubleshooting support

The scanner writes execution details to scanner_log.txt including:
- Scan start time
- Scan completion status
- Selected expiration
- Volume statistics
- Error messages


## 🧠 Data Columns

The CSV file includes:

| Column | Description |
|------|------------|
| ticker | Stock symbol |
| date | Scan date |
| expiration | Option expiration |
| optionType | CALL or PUT |
| strike | Strike price |
| volume | Daily traded volume |
| openInterest | Open interest |
| impliedVolatility | Implied volatility |
| lastPrice | Last traded price |


## 🔧 Configuration

Inside scanner.py:

TICKER = "AVGO"
MIN_VOLUME = 500

You can easily modify:
- The ticker symbol
- Volume thresholds
- Output path
- Filters (e.g. open interest, strike range)


## 🧠 Design Decisions
Why Yahoo Finance (yfinance)?
Yahoo Finance was chosen because it provides:
- Free access to equity and options chains
- Reliable expiration listings
- Sufficient granularity for volume and open interest analysis

This project prioritizes accessibility and rapid iteration over institutional-grade data sources.


Why Volume-Based Filtering?
The scanner filters options using a minimum volume threshold to:
- Reduce noise from illiquid contracts
- Highlight strikes with meaningful market participation
- Focus analysis on areas more likely to reflect institutional activity

This approach keeps the dataset small, relevant, and dashboard-friendly.


Why Separate Scanner and Dashboard?
The scanner and dashboard are intentionally decoupled:
- scanner.py is designed for automation and scheduled execution
- dashboard.py is designed for interactive exploration

This separation allows:
- The scanner to run daily without user interaction
- The dashboard to remain fast and responsive

It also makes future transitions to a database or API-based backend straightforward.


Why a CSV-Based Data Store?
A CSV file was chosen instead of a database to:
- Keep the project lightweight and dependency-minimal
- Allow easy inspection and debugging
- Enable simple versioning and portability

The schema is kept stable to support future migration to:
- SQLite
- PostgreSQL
- Cloud storage


Why Dynamic Expiration Selection?
Options expirations change weekly.
The scanner automatically selects the nearest valid expiration to:
- Avoid manual updates
- Prevent broken scans after expiration rollovers
- Support long-running automation

This ensures the scanner remains reliable over time.


Why Streamlit for Visualization?
Streamlit was chosen because it:
- Enables rapid dashboard development
- Requires minimal boilerplate
- Allows easy filtering and interaction

The goal of the dashboard is analysis and exploration, not production deployment, making Streamlit a strong fit.


## 🛠️ Future Enhancements

Potential upgrades:
- Multi-ticker scanning
- Open interest filters
- Volume / OI ratio
- Gamma exposure calculations
- Alerts for unusual options activity




## ⚠️ Disclaimer

This project is for educational and analytical purposes only.
It is not financial advice.


## 👤 Author

Built by Brian Kassin
Focused on learning options flow, data analysis, and dashboarding with Python.
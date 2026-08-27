# 📊 YouData – YouTube Data Analysis Tool (CLI)

A command‑line tool that fetches video statistics from any YouTube channel, stores them in a local SQLite database, and generates insightful reports (top videos, daily trends, Excel exports).  
Designed for content creators, analysts, and researchers who want to track engagement, spot trending topics, and study successful content strategies.

---

## ✨ Features

- **Download video data** – Fetch titles, views, likes, comments, publication date, thumbnails, and descriptions for any channel over a custom date range (day, week, month, year).
- **Local SQLite storage** – Efficiently store and query video data.
- **Top videos dashboard** – Automatically shows the top 10 videos from today, yesterday, and the day before (ranked by views) with trending keywords.
- **Flexible querying** – View top videos for any single date or a range of dates.
- **Excel report generation** – Export top videos (up to 5,000) to a `.xlsx` file, either for a single day or a combined report for a date range.
- **Channel management** – Add, delete, and switch between multiple YouTube channels.
- **Timezone‑aware timestamps** – Convert UTC publication times to your local timezone (configurable).
- **Keyword extraction** – Automatically extract trending keywords from video titles to identify popular topics.

---

## 🛠️ Tech Stack

- Python 3.10+
- Google YouTube Data API v3
- SQLite (local database)
- pandas (data manipulation and Excel export)
- pytz (timezone handling)
- python-dotenv (environment variables)
- openpyxl (Excel writing)

---

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/edbarron/youdata.git
   cd youdata
   ```

2. **Create and activate a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**  
   Create a `.env` file in the root directory:
   ```env
   YOUTUBE_API_KEY=your_youtube_api_key
   ```
   > You need a valid YouTube Data API v3 key. Get one from the [Google Cloud Console](https://console.cloud.google.com/).

5. **Run the application**
   ```bash
   python main.py
   ```

---

## ⚙️ Configuration

### Environment Variables (`.env`)

| Variable | Description |
| :--- | :--- |
| `YOUTUBE_API_KEY` | Your YouTube Data API v3 key (required). |

### Timezone

Edit the `LOCAL_TIMEZONE` variable in `main.py` (line ~11) to match your local timezone. Default is `America/Phoenix`.

```python
LOCAL_TIMEZONE = timezone('America/Phoenix')   # change to your own
```

---

## 📊 How It Works

1. **Add a channel** – Use the channel configuration menu to add a YouTube channel (by its channel ID).
2. **Set active channel** – Choose which channel you want to analyse.
3. **Download data** – Select a time frame (today, yesterday, last week, custom range) and fetch video data from the API.
4. **View top videos** – The main menu automatically shows today's, yesterday's, and the day‑before‑yesterday's top videos, with trending keyword summaries.
5. **Generate reports** – Export video data to Excel for a single date or a combined range.
6. **Repeat** – Download data for different ranges to build a historical database.

---

## 📁 File Structure

```
youdata/
├── main.py                 # Main application logic and menu
├── db_utils.py             # Database operations (insert, fetch, manage channels)
├── utils.py                # Helper functions (time frame selection, table display, keyword extraction)
├── fetch_videos_by_range.py# Batch data retrieval and combined Excel export
├── .env                    # Environment variables (API key) – NOT tracked
├── requirements.txt        # Python dependencies
├── youdata.db              # SQLite database (auto‑created)
├── top_videos_*.xlsx       # Exported Excel reports (auto‑generated)
└── README.md               # This file
```

---

## 🧪 Testing

- Start with a small date range (e.g., "today") to verify the API connection.
- Use the dashboard to confirm that videos are being stored and displayed.
- Generate an Excel report to ensure the export works.

---

## 🔮 Future Improvements

- Automated scheduling for regular data collection.
- Graphical visualisations (e.g., `matplotlib`).
- Trend prediction using machine learning.
- Export multiple days in a single Excel file (already implemented in `generate_report_combined()`).
- Support for multiple timezones per user.

---

## 📄 License

MIT – free to use, modify, and distribute.

---

## 🙏 Acknowledgements

Developed as the final project for Harvard’s CS50 Python course.  
Special thanks to Professor David Malan and the CS50 staff.

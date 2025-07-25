import os

# Load all config variables from environment (exported via systemd service file)

# Job search filters
TOWN = os.getenv("JOB_TOWN", "Leigh")
POSTCODE = os.getenv("JOB_POSTCODE", "WN7 1NX")
RADIUS_MILES = int(os.getenv("JOB_RADIUS_MILES", "5"))
PART_TIME_ONLY = os.getenv("JOB_PART_TIME_ONLY", "true").lower() == "true"

# Scrape limits and scheduling
LINKEDIN_DAILY_LIMIT = int(os.getenv("LINKEDIN_DAILY_LIMIT", "25"))
INDEED_DAILY_LIMIT = int(os.getenv("INDEED_DAILY_LIMIT", "25"))

# Telegram Bot
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# Hugging Face API for ranking/filtering
HF_API_KEY = os.getenv("HF_API_KEY", "")

# Cookie storage paths (assumed to be files or JSON strings)
LINKEDIN_COOKIES_PATH = os.getenv("LINKEDIN_COOKIES_PATH", "/path/to/linkedin_cookies.json")
INDEED_COOKIES_PATH = os.getenv("INDEED_COOKIES_PATH", "/path/to/indeed_cookies.json")

# Other settings
LOG_FILE = os.getenv("LOG_FILE", "./logs/bot.log")

# Job scoring thresholds
MIN_SALARY_ANNUAL = int(os.getenv("MIN_SALARY_ANNUAL", "17500"))  # in GBP pro-rata
MIN_SALARY_HOURLY = float(os.getenv("MIN_SALARY_HOURLY", "11.0"))

MIN_COMPANY_RATING = float(os.getenv("MIN_COMPANY_RATING", "6.0"))  # 1 to 10 scale
MIN_CV_MATCH_SCORE = float(os.getenv("MIN_CV_MATCH_SCORE", "7.0"))  # 0 to 10 scale semantic

# Misc
MAX_JOB_DESCRIPTION_LENGTH = int(os.getenv("MAX_JOB_DESCRIPTION_LENGTH", "1000"))  # truncate descriptions

# Scheduler times (24h format)
SCRAPE_TIMES = [
    os.getenv("SCRAPE_TIME_1", "08:30"),
    os.getenv("SCRAPE_TIME_2", "13:45"),
    os.getenv("SCRAPE_TIME_3", "17:00"),
]

SEND_TIMES = [
    os.getenv("SEND_TIME_1", "09:00"),
    os.getenv("SEND_TIME_2", "18:00"),
    os.getenv("SEND_TIME_3", "21:00"),
]

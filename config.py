import os

# Job search filters
TOWN = os.getenv("JOB_TOWN", "Leigh")
POSTCODE = os.getenv("JOB_POSTCODE", "WN7 1NX")
try:
    RADIUS_MILES = int(os.getenv("JOB_RADIUS_MILES", "5"))
except (ValueError, TypeError):
    RADIUS_MILES = 5

PART_TIME_ONLY = os.getenv("JOB_PART_TIME_ONLY", "true").strip().lower() == "true"

# Scrape limits and scheduling
try:
    LINKEDIN_DAILY_LIMIT = int(os.getenv("LINKEDIN_DAILY_LIMIT", "25"))
except (ValueError, TypeError):
    LINKEDIN_DAILY_LIMIT = 25

try:
    INDEED_DAILY_LIMIT = int(os.getenv("INDEED_DAILY_LIMIT", "25"))
except (ValueError, TypeError):
    INDEED_DAILY_LIMIT = 25

# Telegram Bot credentials
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()

# Hugging Face API for ranking/filtering
HF_API_KEY = os.getenv("HF_API_KEY", "").strip()

# Cookie storage paths (file paths or JSON strings)
LINKEDIN_COOKIES_PATH = os.getenv("LINKEDIN_COOKIES_PATH", "/home/ubuntu/job-bot/linkedin_cookies.json").strip()
INDEED_COOKIES_PATH = os.getenv("INDEED_COOKIES_PATH", "/home/ubuntu/job-bot/indeed_cookies.json").strip()

# Logging
LOG_FILE = os.getenv("LOG_FILE", "./logs/bot.log").strip()

# Job scoring thresholds
try:
    MIN_SALARY_ANNUAL = int(os.getenv("MIN_SALARY_ANNUAL", "17500"))
except (ValueError, TypeError):
    MIN_SALARY_ANNUAL = 17500

try:
    MIN_SALARY_HOURLY = float(os.getenv("MIN_SALARY_HOURLY", "11.0"))
except (ValueError, TypeError):
    MIN_SALARY_HOURLY = 11.0

try:
    MIN_COMPANY_RATING = float(os.getenv("MIN_COMPANY_RATING", "6.0"))
except (ValueError, TypeError):
    MIN_COMPANY_RATING = 6.0

try:
    MIN_CV_MATCH_SCORE = float(os.getenv("MIN_CV_MATCH_SCORE", "7.0"))
except (ValueError, TypeError):
    MIN_CV_MATCH_SCORE = 7.0

# CV file path for ranking module (must exist)
CV_PATH = os.getenv("CV_PATH", "/home/ubuntu/job-bot/cv.pdf").strip()

# Ranking thresholds for filtering
try:
    RANKING_THRESHOLD = float(os.getenv("RANKING_THRESHOLD", "0.7"))  # semantic similarity usually 0-1 scale
except (ValueError, TypeError):
    RANKING_THRESHOLD = 0.7

try:
    COMPANY_RATING_THRESHOLD = float(os.getenv("COMPANY_RATING_THRESHOLD", "6.0"))
except (ValueError, TypeError):
    COMPANY_RATING_THRESHOLD = 6.0

# Misc
try:
    MAX_JOB_DESCRIPTION_LENGTH = int(os.getenv("MAX_JOB_DESCRIPTION_LENGTH", "1000"))
except (ValueError, TypeError):
    MAX_JOB_DESCRIPTION_LENGTH = 1000

# Scheduler times (24h format) - fallback to list of strings if not set
SCRAPE_TIMES = [
    os.getenv("SCRAPE_TIME_1", "08:30").strip(),
    os.getenv("SCRAPE_TIME_2", "13:45").strip(),
    os.getenv("SCRAPE_TIME_3", "17:00").strip(),
]

SEND_TIMES = [
    os.getenv("SEND_TIME_1", "09:00").strip(),
    os.getenv("SEND_TIME_2", "18:00").strip(),
    os.getenv("SEND_TIME_3", "21:00").strip(),
]

import requests
import logging
from typing import List, Dict
from utils import safe_request, clean_text, parse_salary
from config import INDEED_COOKIES, JOB_RADIUS_MILES, JOB_LOCATION_POSTCODE, JOB_TYPE_PART_TIME

logger = logging.getLogger("jobbot.scrape_indeed")

BASE_URL = "https://www.indeed.com/jobs"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Cookie": "; ".join([f"{k}={v}" for k, v in INDEED_COOKIES.items()]),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
}

def build_query_params(start: int = 0) -> Dict[str, str]:
    return {
        "q": "",  # Blank keyword to get all jobs
        "l": JOB_LOCATION_POSTCODE,
        "radius": str(JOB_RADIUS_MILES),
        "jt": JOB_TYPE_PART_TIME,
        "start": str(start),
    }

def scrape_indeed_jobs(max_jobs: int = 100) -> List[Dict]:
    """
    Scrapes Indeed jobs matching filters.
    Returns list of job dicts with:
      - title
      - company
      - location
      - salary (optional)
      - description snippet
      - job_url
    """
    jobs = []
    start = 0

    while len(jobs) < max_jobs:
        params = build_query_params(start)
        response = safe_request("GET", BASE_URL, headers=HEADERS, params=params)
        if response is None:
            logger.error("Indeed scrape failed at start=%s", start)
            break

        try:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(response.text, "html.parser")
            job_cards = soup.select("div.jobsearch-SerpJobCard")
            if not job_cards:
                logger.info("No more Indeed jobs found at start=%s", start)
                break

            for card in job_cards:
                title = clean_text(card.select_one("h2.title").get_text(strip=True)) if card.select_one("h2.title") else ""
                company = clean_text(card.select_one("span.company").get_text(strip=True)) if card.select_one("span.company") else ""
                location = clean_text(card.select_one("div.location").get_text(strip=True)) if card.select_one("div.location") else ""
                salary = None
                salary_tag = card.select_one("span.salaryText")
                if salary_tag:
                    salary = parse_salary(salary_tag.get_text(strip=True))
                description = clean_text(card.select_one("div.summary").get_text(strip=True)) if card.select_one("div.summary") else ""
                job_url_tag = card.select_one("a.jobtitle")
                job_url = "https://www.indeed.com" + job_url_tag['href'] if job_url_tag and 'href' in job_url_tag.attrs else ""

                job_dict = {
                    "title": title,
                    "company": company,
                    "location": location,
                    "salary": salary,
                    "description": description,
                    "job_url": job_url,
                }
                jobs.append(job_dict)
                if len(jobs) >= max_jobs:
                    break
            start += len(job_cards)
        except Exception as e:
            logger.error("Failed to parse Indeed response: %s", e)
            break

    logger.info("Scraped %d Indeed jobs", len(jobs))
    return jobs

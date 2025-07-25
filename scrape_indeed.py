import requests
import logging
import json
from typing import List, Dict
from utils import safe_request, clean_text, parse_salary
from config import INDEED_COOKIES_PATH, RADIUS_MILES, POSTCODE, PART_TIME_ONLY

logger = logging.getLogger("jobbot.scrape_indeed")

BASE_URL = "https://www.indeed.com/jobs"

try:
    with open(INDEED_COOKIES_PATH, "r") as f:
        INDEED_COOKIES = json.load(f)
except Exception as e:
    logger.error("Failed to load Indeed cookies JSON: %s", e)
    INDEED_COOKIES = {}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Cookie": "; ".join([f"{k}={v}" for k, v in INDEED_COOKIES.items()]),
    "Accept": "text/html,application/xhtml+xml,application/xml",
}

def build_query_params(start: int = 0) -> Dict[str, str]:
    # indeed pagination uses start param (e.g. start=10)
    # part-time filter = jt=parttime, location filter via l param
    params = {
        "q": "",
        "l": POSTCODE,
        "radius": str(RADIUS_MILES),
        "jt": "parttime" if PART_TIME_ONLY else "fulltime",
        "start": str(start),
    }
    return params

def scrape_indeed_jobs(max_jobs: int = 100) -> List[Dict]:
    jobs = []
    start = 0

    while len(jobs) < max_jobs:
        params = build_query_params(start)
        response = safe_request("GET", BASE_URL, headers=HEADERS, params=params)
        if response is None:
            logger.error("Indeed scrape failed at start=%s", start)
            break

        try:
            # Indeed doesn't have JSON API - scrape HTML and parse jobs out
            html = response.text

            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, "html.parser")

            job_cards = soup.find_all("div", class_="job_seen_beacon")
            if not job_cards:
                logger.info("No more Indeed jobs found at start=%s", start)
                break

            for card in job_cards:
                title_tag = card.find("h2", class_="jobTitle")
                company_tag = card.find("span", class_="companyName")
                location_tag = card.find("div", class_="companyLocation")
                desc_tag = card.find("div", class_="job-snippet")

                title = clean_text(title_tag.get_text() if title_tag else "")
                company = clean_text(company_tag.get_text() if company_tag else "")
                location = clean_text(location_tag.get_text() if location_tag else "")
                description = clean_text(desc_tag.get_text() if desc_tag else "")
                
                salary = None
                salary_tag = card.find("div", class_="salary-snippet")
                if salary_tag:
                    salary = parse_salary(clean_text(salary_tag.get_text()))

                job_url = ""
                # Extract job URL reliably
                link_tag = card.find("a", href=True)
                if link_tag:
                    job_url = "https://www.indeed.com" + link_tag["href"]

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
            logger.error("Error parsing Indeed jobs: %s", e)
            break

    logger.info("Scraped %d Indeed jobs", len(jobs))
    return jobs

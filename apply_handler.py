import logging
import json
import re
from typing import List, Dict
from urllib.parse import urlencode
from bs4 import BeautifulSoup

import requests
from utils import clean_text, safe_request, parse_salary
from config import POSTCODE, RADIUS_MILES, PART_TIME_ONLY

logger = logging.getLogger("jobbot.scrape_indeed")

BASE_URL = "https://www.indeed.co.uk/jobs"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}


def build_indeed_query(start: int = 0) -> str:
    query_params = {
        "q": "part time" if PART_TIME_ONLY else "",
        "l": POSTCODE,
        "radius": RADIUS_MILES,
        "start": start,
        "sort": "date",
        "fromage": "1",  # posted today only
        "limit": "25"
    }
    return f"{BASE_URL}?{urlencode(query_params)}"


def extract_job_cards(html: str) -> List[Dict]:
    soup = BeautifulSoup(html, "html.parser")
    job_cards = soup.find_all("a", attrs={"data-hide-spinner": "true", "data-jk": True})
    jobs = []

    for card in job_cards:
        try:
            title = clean_text(card.find("h2").text)
            company_span = card.find("span", class_="companyName")
            company = clean_text(company_span.text if company_span else "")

            location_span = card.find("div", class_="companyLocation")
            location = clean_text(location_span.text if location_span else "")

            summary_span = card.find("div", class_="job-snippet")
            description = clean_text(summary_span.text if summary_span else "")

            job_id = card.get("data-jk")
            job_url = f"https://www.indeed.co.uk/viewjob?jk={job_id}"

            salary_text = ""
            salary_span = card.find("div", class_="metadata salary-snippet-container")
            if salary_span:
                salary_text = clean_text(salary_span.text)

            salary = parse_salary(salary_text) if salary_text else None

            job = {
                "title": title,
                "company": company,
                "location": location,
                "salary": salary,
                "description": description,
                "job_url": job_url,
                "platform": "indeed",
                "id": job_id,
            }
            jobs.append(job)
        except Exception as e:
            logger.warning(f"Failed to parse job card: {e}")
            continue

    return jobs


def scrape_indeed_jobs(max_jobs: int = 100) -> List[Dict]:
    all_jobs = []
    start = 0

    while len(all_jobs) < max_jobs:
        url = build_indeed_query(start)
        response = safe_request("GET", url, headers=HEADERS)
        if not response:
            logger.error(f"Indeed request failed at start={start}")
            break

        jobs = extract_job_cards(response.text)
        if not jobs:
            logger.info(f"No jobs found on Indeed at start={start}")
            break

        all_jobs.extend(jobs)
        if len(jobs) < 25:
            break

        start += 25

    logger.info("Scraped %d Indeed jobs", len(all_jobs))
    return all_jobs[:max_jobs]

import requests
import logging
import json
from typing import List, Dict
from utils import safe_request, clean_text
from config import LINKEDIN_COOKIES_PATH, RADIUS_MILES, POSTCODE, PART_TIME_ONLY

logger = logging.getLogger("jobbot.scrape_linkedin")

BASE_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"

try:
    with open(LINKEDIN_COOKIES_PATH, "r") as f:
        LINKEDIN_COOKIES = json.load(f)
except Exception as e:
    logger.error("Failed to load LinkedIn cookies JSON: %s", e)
    LINKEDIN_COOKIES = {}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Csrf-Token": LINKEDIN_COOKIES.get("JSESSIONID", ""),
    "Cookie": "; ".join([f"{k}={v}" for k, v in LINKEDIN_COOKIES.items()]),
    "Accept": "application/json",
}

def build_query_params(start: int = 0) -> Dict[str, str]:
    return {
        "keywords": "",
        "location": POSTCODE,
        "distance": str(RADIUS_MILES),
        "f_TP": "1",  # last 24 hours only
        "f_JT": "parttime" if PART_TIME_ONLY else "fulltime",
        "start": str(start),
        "count": "25",
    }

def scrape_linkedin_jobs(max_jobs: int = 100) -> List[Dict]:
    jobs = []
    start = 0

    while len(jobs) < max_jobs:
        params = build_query_params(start)
        response = safe_request("GET", BASE_URL, headers=HEADERS, params=params)
        if response is None:
            logger.error("LinkedIn scrape failed at start=%s", start)
            break

        try:
            if not response.text.strip().startswith("<!DOCTYPE html>"):
                data = response.json()
                elements = data.get("elements", [])
            else:
                logger.warning("LinkedIn returned HTML instead of JSON at start=%s", start)
                break

            if not elements:
                logger.info("No more LinkedIn jobs found at start=%s", start)
                break

            for job in elements:
                job_dict = {
                    "title": clean_text(job.get("title", "")),
                    "company": clean_text(job.get("companyName", "")),
                    "location": clean_text(job.get("formattedLocation", "")),
                    "salary": None,  # LinkedIn rarely has salary data
                    "description": clean_text(job.get("descriptionSnippet", "")),
                    "job_url": job.get("jobPostingUrl", ""),
                }
                jobs.append(job_dict)
                if len(jobs) >= max_jobs:
                    break

            start += len(elements)

        except Exception as e:
            logger.error("Error parsing LinkedIn jobs: %s", e)
            break

    logger.info("Scraped %d LinkedIn jobs", len(jobs))
    return jobs

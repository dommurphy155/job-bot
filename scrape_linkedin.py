import requests
import logging
from typing import List, Dict, Optional
from utils import safe_request, clean_text, parse_salary
from config import LINKEDIN_COOKIES, JOB_RADIUS_MILES, JOB_LOCATION_POSTCODE, JOB_TYPE_PART_TIME

logger = logging.getLogger("jobbot.scrape_linkedin")

BASE_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Csrf-Token": LINKEDIN_COOKIES.get("JSESSIONID", ""),
    "Cookie": "; ".join([f"{k}={v}" for k, v in LINKEDIN_COOKIES.items()]),
    "Accept": "application/json",
}

def build_query_params(start: int = 0) -> Dict[str, str]:
    return {
        "keywords": "",
        "location": JOB_LOCATION_POSTCODE,
        "distance": str(JOB_RADIUS_MILES),
        "f_TP": "1",  # Past 24 hours (to limit new jobs)
        "f_JT": JOB_TYPE_PART_TIME,
        "start": str(start),
        "count": "25",
    }

def scrape_linkedin_jobs(max_jobs: int = 100) -> List[Dict]:
    """
    Scrapes LinkedIn job listings within the set filters.
    Returns a list of job dicts with fields:
      - title
      - company
      - location
      - salary (optional)
      - description
      - job_url
    """
    jobs = []
    start = 0

    while len(jobs) < max_jobs:
        params = build_query_params(start)
        response = safe_request("GET", BASE_URL, headers=HEADERS, params=params)
        if response is None:
            logger.error("LinkedIn scrape failed at start=%s", start)
            break

        try:
            data = response.json()
            elements = data.get("elements", [])
            if not elements:
                logger.info("No more LinkedIn jobs found at start=%s", start)
                break
            for job in elements:
                # Extract fields with fallback and cleaning
                title = clean_text(job.get("title", ""))
                company = clean_text(job.get("companyName", ""))
                location = clean_text(job.get("formattedLocation", ""))
                description = clean_text(job.get("descriptionSnippet", ""))
                job_url = job.get("jobPostingUrl", "")

                # Salary parsing optional - LinkedIn rarely shows directly in this API
                salary = None
                # Add custom logic if salary found in description or elsewhere

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
            start += len(elements)
        except Exception as e:
            logger.error("Failed to parse LinkedIn response: %s", e)
            break

    logger.info("Scraped %d LinkedIn jobs", len(jobs))
    return jobs

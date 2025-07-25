import json
import logging
from typing import List, Dict
import httpx
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
    "Cookie": "; ".join([f"{k}={v}" for k, v in LINKEDIN_COOKIES.items()]) if LINKEDIN_COOKIES else "",
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

async def scrape_linkedin_jobs(max_jobs: int = 100) -> List[Dict]:
    jobs = []
    start = 0

    async with httpx.AsyncClient(headers=HEADERS, timeout=15) as client:
        while len(jobs) < max_jobs:
            params = build_query_params(start)
            response = await safe_request(client, "GET", BASE_URL, params=params)
            if response is None:
                logger.error(f"LinkedIn scrape failed at start={start}")
                break

            try:
                text = response.text
                if text.strip().startswith("<!DOCTYPE html>"):
                    logger.warning(f"LinkedIn returned HTML instead of JSON at start={start}")
                    break

                data = response.json()
                elements = data.get("elements", [])
                if not elements:
                    logger.info(f"No more LinkedIn jobs found at start={start}")
                    break

                for job in elements:
                    job_dict = {
                        "title": clean_text(job.get("title", "")),
                        "company": clean_text(job.get("companyName", "")),
                        "location": clean_text(job.get("formattedLocation", "")),
                        "salary": None,  # LinkedIn rarely has salary data
                        "description": clean_text(job.get("descriptionSnippet", "")),
                        "url": job.get("jobPostingUrl", ""),  # consistent key name
                    }
                    jobs.append(job_dict)
                    if len(jobs) >= max_jobs:
                        break

                start += len(elements)

            except Exception as e:
                logger.error(f"Error parsing LinkedIn jobs at start={start}: {e}")
                break

    logger.info(f"Scraped {len(jobs)} LinkedIn jobs")
    return jobs

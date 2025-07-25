import logging
import requests
import json
from typing import Dict
from config import LINKEDIN_COOKIES_PATH, INDEED_COOKIES_PATH, APPLY_TIMEOUT_SECONDS

logger = logging.getLogger("jobbot.apply_handler")

# Load cookies dynamically from JSON files
with open(LINKEDIN_COOKIES_PATH, "r") as f:
    LINKEDIN_COOKIES = json.load(f)

with open(INDEED_COOKIES_PATH, "r") as f:
    INDEED_COOKIES = json.load(f)

class AutoApplyHandler:
    def __init__(self):
        self.linkedin_cookies = LINKEDIN_COOKIES
        self.indeed_cookies = INDEED_COOKIES
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (compatible; JobBot/1.0; +https://github.com/dommurphy155/job-bot)"
        })

    def _get_cookies_for_platform(self, platform: str) -> Dict:
        platform_lower = platform.lower()
        if platform_lower == "linkedin":
            return self.linkedin_cookies
        elif platform_lower == "indeed":
            return self.indeed_cookies
        else:
            return {}

    def auto_apply(self, job: Dict) -> bool:
        platform = job.get("platform")
        apply_url = job.get("apply_url")
        job_id = job.get("id", "unknown")

        if not platform or not apply_url:
            logger.warning(f"Job {job_id} missing platform or apply_url")
            return False

        cookies = self._get_cookies_for_platform(platform)
        if not cookies:
            logger.error(f"No cookies configured for platform: {platform}")
            return False

        try:
            resp = self.session.get(apply_url, cookies=cookies, timeout=APPLY_TIMEOUT_SECONDS)
            resp.raise_for_status()

            if self._contains_questions(resp.text):
                logger.info(f"Job {job_id} requires interactive questions; skipping auto-apply.")
                return False

            payload = self._build_application_payload(job)
            post_resp = self.session.post(apply_url, cookies=cookies, data=payload, timeout=APPLY_TIMEOUT_SECONDS)
            post_resp.raise_for_status()

            if self._application_success(post_resp.text):
                logger.info(f"Successfully auto-applied to job {job_id} on {platform}")
                return True
            else:
                logger.warning(f"Auto-apply failed validation for job {job_id}")
                return False

        except requests.RequestException as e:
            logger.error(f"Network error during auto-apply for job {job_id}: {e}")
            return False

    def _contains_questions(self, html: str) -> bool:
        question_keywords = ["question", "captcha", "assessment", "quiz", "test"]
        html_lower = html.lower()
        return any(keyword in html_lower for keyword in question_keywords)

    def _build_application_payload(self, job: Dict) -> Dict:
        # Minimal placeholder payload, extend as needed
        return {
            "applicant_name": job.get("applicant_name", ""),
            "applicant_email": job.get("applicant_email", ""),
            # Add more fields here per platform/form specifics
        }

    def _application_success(self, html: str) -> bool:
        success_markers = [
            "thank you for applying",
            "application received",
            "we have received your application"
        ]
        html_lower = html.lower()
        return any(marker in html_lower for marker in success_markers)

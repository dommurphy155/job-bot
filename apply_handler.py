import logging
import requests
from typing import Dict, Optional
from config import LINKEDIN_COOKIES, INDEED_COOKIES, APPLY_TIMEOUT_SECONDS

logger = logging.getLogger("jobbot.apply_handler")

class AutoApplyHandler:
    def __init__(self):
        # Load cookies for LinkedIn and Indeed from config (dict format)
        self.linkedin_cookies = LINKEDIN_COOKIES
        self.indeed_cookies = INDEED_COOKIES
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (compatible; JobBot/1.0; +https://github.com/dommurphy155/job-bot)"
        })

    def _get_cookies_for_platform(self, platform: str) -> Dict:
        if platform.lower() == "linkedin":
            return self.linkedin_cookies
        elif platform.lower() == "indeed":
            return self.indeed_cookies
        else:
            return {}

    def auto_apply(self, job: Dict) -> bool:
        """
        Attempt to auto-apply to a job if no interactive questions.
        Returns True if application was submitted successfully,
        False otherwise (including if questions block auto-apply).
        """
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
            # Simulate GET request to fetch apply page/form
            resp = self.session.get(apply_url, cookies=cookies, timeout=APPLY_TIMEOUT_SECONDS)
            resp.raise_for_status()

            # Check page content for presence of questions, captchas, or interactive forms
            if self._contains_questions(resp.text):
                logger.info(f"Job {job_id} requires interactive questions; skipping auto-apply.")
                return False

            # POST form submission payload -- this is highly platform-specific and
            # must be adjusted per site implementation.
            payload = self._build_application_payload(job)
            post_resp = self.session.post(apply_url, cookies=cookies, data=payload, timeout=APPLY_TIMEOUT_SECONDS)
            post_resp.raise_for_status()

            # Check response for success indicator (varies by platform)
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
        """
        Simple heuristic: detect presence of interactive questions or captchas
        in the HTML form, skipping auto-apply if found.
        """
        question_keywords = ["question", "captcha", "assessment", "quiz", "test"]
        html_lower = html.lower()
        return any(keyword in html_lower for keyword in question_keywords)

    def _build_application_payload(self, job: Dict) -> Dict:
        """
        Build application payload for POST request. Minimal payload here; extend as needed.
        """
        # Placeholder: basic payload with required fields
        payload = {
            "applicant_name": job.get("applicant_name", ""),
            "applicant_email": job.get("applicant_email", ""),
            # Additional fields go here, customized per platform and job form requirements
        }
        return payload

    def _application_success(self, html: str) -> bool:
        """
        Detect if the application submission was successful by looking for known success markers.
        """
        success_markers = ["thank you for applying", "application received", "we have received your application"]
        html_lower = html.lower()
        return any(marker in html_lower for marker in success_markers)
    

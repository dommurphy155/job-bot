import requests
from typing import Optional, Dict, Any
import json
import logging

logger = logging.getLogger("jobbot.utils")


def safe_request(
    method: str,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Any] = None,
    json_data: Optional[Dict[str, Any]] = None,
    timeout: int = 15,
) -> Optional[requests.Response]:
    """
    Safe HTTP request wrapper with error handling and logging.
    Supports GET, POST, etc.
    """
    try:
        response = requests.request(
            method=method, url=url, headers=headers, params=params, data=data, json=json_data, timeout=timeout
        )
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        logger.error(f"HTTP {method} request to {url} failed: {e}")
        return None


def clean_text(text: str) -> str:
    """
    Sanitize text by stripping whitespace and removing problematic characters.
    """
    if not text:
        return ""
    return " ".join(text.strip().split())


def parse_salary(salary_str: str) -> Optional[float]:
    """
    Extract a numeric salary value from a string, approximate or None if invalid.
    Supports annual or hourly rates, GBP assumed.
    Examples:
      '£25,000 a year' -> 25000.0
      '£11 per hour' -> 11.0
    """
    if not salary_str:
        return None
    import re

    salary_str = salary_str.lower().replace(",", "")
    match = re.search(r"£\s?(\d+\.?\d*)", salary_str)
    if not match:
        return None
    value = float(match.group(1))
    # Convert hourly to annual (roughly 40h/week * 52 weeks)
    if "hour" in salary_str:
        value *= 40 * 52
    return value


def chunk_list(lst: list, chunk_size: int) -> list[list]:
    """
    Split list into chunks of chunk_size.
    """
    return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]

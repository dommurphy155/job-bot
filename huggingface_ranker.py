import os
import logging
from typing import List, Dict, Tuple
from transformers import pipeline
from config import CV_PATH, RANKING_THRESHOLD, COMPANY_RATING_THRESHOLD

logger = logging.getLogger("jobbot.hf_ranker")

# Load a sentence similarity pipeline (or semantic search)
# Use a lightweight model for resource efficiency on Micro Flex E2
_similarity_pipeline = pipeline("sentence-similarity", model="sentence-transformers/all-MiniLM-L6-v2")

def load_cv_text(cv_path: str = CV_PATH) -> str:
    """Load and extract plain text from the CV PDF."""
    from PyPDF2 import PdfReader

    try:
        reader = PdfReader(cv_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text.strip()
    except Exception as e:
        logger.error(f"Failed to load CV text: {e}")
        return ""

CV_TEXT = load_cv_text()

def semantic_score(job_title: str, job_desc: str, cv_text: str = CV_TEXT) -> float:
    """
    Calculate semantic similarity score between the job posting and CV.
    Returns a float between 0 and 1.
    """
    try:
        # Combine job title and description for matching
        job_text = f"{job_title}. {job_desc}"
        results = _similarity_pipeline(job_text, cv_text)
        # results example: [{'score': 0.85, 'label': 'entailment'}] or list of dicts
        # Take the max score if list, else just the score
        if isinstance(results, list):
            max_score = max([r.get('score', 0) for r in results])
            return max_score
        return results.get('score', 0)
    except Exception as e:
        logger.error(f"Semantic scoring failed: {e}")
        return 0.0

def company_rating_and_summary(company_reviews: List[str]) -> Tuple[int, str]:
    """
    Calculate a company rating (1-10) and a short summary based on review sentiment.
    Uses Hugging Face sentiment analysis pipeline.
    """
    from transformers import pipeline
    sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

    if not company_reviews:
        return 5, "No reviews available."

    positive, negative = 0, 0
    for review in company_reviews:
        try:
            result = sentiment_analyzer(review[:512])[0]  # Truncate long texts
            if result['label'].lower() == 'positive':
                positive += 1
            else:
                negative += 1
        except Exception as e:
            logger.warning(f"Sentiment analysis failed on review: {e}")

    total = positive + negative
    if total == 0:
        return 5, "No valid reviews."

    score = int(round((positive / total) * 10))
    summary = f"{score}/10 rating based on {total} employee reviews."

    if score >= 8:
        summary += " Overall very positive work environment."
    elif score >= 5:
        summary += " Mixed reviews; some positives and negatives."
    else:
        summary += " Mostly negative feedback; caution advised."

    return score, summary

def filter_and_rank_jobs(jobs: List[Dict]) -> List[Dict]:
    """
    Filter jobs by semantic match, company rating, salary, and role whitelist.
    Rank by combined score descending.
    """
    filtered_jobs = []
    for job in jobs:
        # Placeholder for company reviews scraping; dummy empty list for now
        company_reviews = job.get("company_reviews", [])

        rating, rating_summary = company_rating_and_summary(company_reviews)
        sem_score = semantic_score(job.get("title", ""), job.get("description", ""))
        salary = job.get("salary", None)

        if sem_score < RANKING_THRESHOLD:
            continue
        if rating < COMPANY_RATING_THRESHOLD:
            continue
        # Salary filter can be customized here (e.g. min salary threshold)
        if salary is not None and salary < 11000:  # annual pro-rata example threshold
            continue

        job["semantic_score"] = sem_score
        job["company_rating"] = rating
        job["company_summary"] = rating_summary
        filtered_jobs.append(job)

    # Sort descending by semantic_score then company_rating
    filtered_jobs.sort(key=lambda x: (x["semantic_score"], x["company_rating"]), reverse=True)
    return filtered_jobs

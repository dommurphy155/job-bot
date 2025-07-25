import os
import logging
from typing import List, Dict, Tuple
from transformers import pipeline
from config import CV_PATH, RANKING_THRESHOLD, COMPANY_RATING_THRESHOLD

logger = logging.getLogger("jobbot.hf_ranker")

# Ensure cache env var is set
os.environ["TRANSFORMERS_CACHE"] = os.getenv("TRANSFORMERS_CACHE", "/home/ubuntu/.cache/huggingface/hub")

# Load semantic similarity pipeline (MiniLM model is efficient and fast)
_similarity_pipeline = pipeline("text-similarity", model="sentence-transformers/all-MiniLM-L6-v2")

# Load sentiment analysis pipeline once (for company review scoring)
_sentiment_pipeline = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")


def load_cv_text(cv_path: str = CV_PATH) -> str:
    """Load plain text from the PDF CV file."""
    from PyPDF2 import PdfReader

    try:
        reader = PdfReader(cv_path)
        text = "".join(page.extract_text() or "" for page in reader.pages)
        return text.strip()
    except Exception as e:
        logger.error(f"[CV_LOAD_FAIL] Error reading CV: {e}")
        return ""

CV_TEXT = load_cv_text()


def semantic_score(job_title: str, job_desc: str, cv_text: str = CV_TEXT) -> float:
    """Compute semantic match score between job posting and the CV."""
    try:
        job_text = f"{job_title.strip()}. {job_desc.strip()}"
        results = _similarity_pipeline(job_text, cv_text)
        if isinstance(results, list):
            return max(r.get('score', 0.0) for r in results)
        return float(results.get('score', 0.0))
    except Exception as e:
        logger.warning(f"[SEMANTIC_FAIL] Could not score job: {e}")
        return 0.0


def company_rating_and_summary(company_reviews: List[str]) -> Tuple[int, str]:
    """Rate company from reviews and generate a summary string."""
    if not company_reviews:
        return 5, "No reviews available."

    pos, neg = 0, 0
    for review in company_reviews:
        try:
            result = _sentiment_pipeline(review[:512])[0]
            label = result.get("label", "").lower()
            if "positive" in label:
                pos += 1
            else:
                neg += 1
        except Exception as e:
            logger.warning(f"[REVIEW_ANALYSIS_FAIL] Skipped one review: {e}")

    total = pos + neg
    if total == 0:
        return 5, "No valid reviews."

    score = round((pos / total) * 10)
    summary = f"{score}/10 rating from {total} reviews. "
    if score >= 8:
        summary += "Strongly positive feedback overall."
    elif score >= 5:
        summary += "Mixed reputation, exercise discretion."
    else:
        summary += "Mostly negative sentiment."

    return score, summary


def filter_and_rank_jobs(jobs: List[Dict]) -> List[Dict]:
    """Filter and rank job list based on semantic relevance, company score, and salary."""
    filtered = []

    for job in jobs:
        title = job.get("title", "")
        desc = job.get("description", "")
        reviews = job.get("company_reviews", [])
        salary = job.get("salary")

        sem_score = semantic_score(title, desc)
        if sem_score < RANKING_THRESHOLD:
            continue

        rating, summary = company_rating_and_summary(reviews)
        if rating < COMPANY_RATING_THRESHOLD:
            continue

        if salary is not None and salary < 11000:
            continue

        job.update({
            "semantic_score": sem_score,
            "company_rating": rating,
            "company_summary": summary
        })

        filtered.append(job)

    # Rank strictly by semantic_score, fallback to rating
    return sorted(filtered, key=lambda j: (j["semantic_score"], j["company_rating"]), reverse=True)
    

import os
import logging
from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer, util
from transformers import pipeline
from config import CV_PATH, RANKING_THRESHOLD, COMPANY_RATING_THRESHOLD

logger = logging.getLogger("jobbot.hf_ranker")

# Set cache path for Hugging Face transformers
os.environ["TRANSFORMERS_CACHE"] = os.getenv("TRANSFORMERS_CACHE", "/home/ubuntu/.cache/huggingface/hub")

# Load embedding model once (reuse)
_embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Load sentiment analysis pipeline once (reuse)
_sentiment_pipeline = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")


def load_cv_text(cv_path: str = CV_PATH) -> str:
    """Load plain text from CV PDF file."""
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
    """
    Compute semantic similarity between job posting and CV text.
    Returns cosine similarity in [0,1].
    """
    try:
        job_text = f"{job_title.strip()}. {job_desc.strip()}"
        job_emb = _embedding_model.encode(job_text, convert_to_tensor=True)
        cv_emb = _embedding_model.encode(cv_text, convert_to_tensor=True)
        similarity = util.cos_sim(job_emb, cv_emb).item()
        return similarity
    except Exception as e:
        logger.warning(f"[SEMANTIC_FAIL] Could not score job: {e}")
        return 0.0


def company_rating_and_summary(company_reviews: List[str]) -> Tuple[int, str]:
    """
    Generate a company rating out of 10 based on sentiment analysis of reviews,
    and a text summary explaining the rating.
    """
    if not company_reviews:
        return 5, "No reviews available."

    pos, neg = 0, 0
    for review in company_reviews:
        try:
            # Limit to first 512 chars to avoid pipeline overload
            result = _sentiment_pipeline(review[:512])[0]
            label = result.get("label", "").lower()
            if "positive" in label:
                pos += 1
            else:
                neg += 1
        except Exception as e:
            logger.warning(f"[REVIEW_ANALYSIS_FAIL] Skipped review due to error: {e}")

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


def rank_jobs(jobs: List[Dict]) -> List[Dict]:
    """
    Filter and rank jobs based on semantic relevance, company rating, and salary thresholds.
    Returns a list sorted by semantic score (descending), then company rating.
    """
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

    return sorted(filtered, key=lambda j: (j["semantic_score"], j["company_rating"]), reverse=True)

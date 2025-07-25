import os
import logging
from db import DBHandler
from config import LOG_DIR, MAX_LOG_AGE_DAYS, MAX_JOB_AGE_DAYS
from datetime import datetime, timedelta

logger = logging.getLogger("jobbot.cleanup")
db = DBHandler()

def cleanup_old_jobs():
    """Delete jobs that have been accepted or declined older than MAX_JOB_AGE_DAYS."""
    cutoff_date = datetime.utcnow() - timedelta(days=MAX_JOB_AGE_DAYS)
    deleted_count = db.delete_old_jobs(cutoff_date)
    logger.info(f"Deleted {deleted_count} old accepted/declined jobs.")

def cleanup_old_logs():
    """Remove log files older than MAX_LOG_AGE_DAYS."""
    cutoff_date = datetime.utcnow() - timedelta(days=MAX_LOG_AGE_DAYS)
    if not os.path.exists(LOG_DIR):
        logger.warning(f"Log directory {LOG_DIR} does not exist, skipping log cleanup.")
        return

    deleted_files = 0
    for filename in os.listdir(LOG_DIR):
        file_path = os.path.join(LOG_DIR, filename)
        if os.path.isfile(file_path):
            file_mtime = datetime.utcfromtimestamp(os.path.getmtime(file_path))
            if file_mtime < cutoff_date:
                try:
                    os.remove(file_path)
                    deleted_files += 1
                    logger.info(f"Deleted old log file: {file_path}")
                except Exception as e:
                    logger.error(f"Error deleting log file {file_path}: {e}")
    logger.info(f"Deleted {deleted_files} old log files.")

def cleanup_temp_files():
    """Placeholder for any temporary files cleanup if applicable."""
    # Implement if your bot generates temp files or caches that need clearing
    pass

def run_cleanup():
    logger.info("Starting cleanup routine.")
    cleanup_old_jobs()
    cleanup_old_logs()
    cleanup_temp_files()
    logger.info("Cleanup routine finished.")

import sqlite3
import threading
from typing import Optional, List, Dict, Any

DB_PATH = "jobbot.db"
_lock = threading.Lock()

class Database:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._initialize_db()

    def _initialize_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                source TEXT NOT NULL,
                title TEXT,
                company TEXT,
                location TEXT,
                salary TEXT,
                description TEXT,
                url TEXT,
                company_rating REAL,
                company_rating_summary TEXT,
                cv_match_score REAL,
                sent BOOLEAN DEFAULT 0,
                accepted BOOLEAN DEFAULT NULL,
                timestamp INTEGER
            );
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_actions (
                job_id TEXT PRIMARY KEY,
                accepted BOOLEAN NOT NULL,
                action_timestamp INTEGER NOT NULL
            );
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS stats (
                key TEXT PRIMARY KEY,
                value INTEGER
            );
            """)
            conn.commit()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        return conn

    def add_job(self, job_data: Dict[str, Any]) -> bool:
        with _lock, self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                INSERT INTO jobs (id, source, title, company, location, salary, description, url, company_rating, company_rating_summary, cv_match_score, sent, accepted, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, NULL, strftime('%s','now'))
                """, (
                    job_data["id"],
                    job_data["source"],
                    job_data.get("title"),
                    job_data.get("company"),
                    job_data.get("location"),
                    job_data.get("salary"),
                    job_data.get("description"),
                    job_data.get("url"),
                    job_data.get("company_rating"),
                    job_data.get("company_rating_summary"),
                    job_data.get("cv_match_score"),
                ))
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                # Duplicate job id
                return False

    def mark_job_sent(self, job_id: str):
        with _lock, self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE jobs SET sent=1 WHERE id=?", (job_id,))
            conn.commit()

    def mark_job_action(self, job_id: str, accepted: bool):
        with _lock, self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT OR REPLACE INTO user_actions (job_id, accepted, action_timestamp) VALUES (?, ?, strftime('%s','now'))
            """, (job_id, accepted))
            cursor.execute("UPDATE jobs SET accepted=? WHERE id=?", (accepted, job_id))
            conn.commit()

    def get_unsent_jobs(self, limit: int) -> List[Dict[str, Any]]:
        with _lock, self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT id, source, title, company, location, salary, description, url, company_rating, company_rating_summary, cv_match_score
            FROM jobs WHERE sent=0 AND accepted IS NULL
            ORDER BY cv_match_score DESC
            LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]

    def get_job_count(self) -> int:
        with _lock, self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM jobs")
            (count,) = cursor.fetchone()
            return count

    def _row_to_dict(self, row):
        return {
            "id": row[0],
            "source": row[1],
            "title": row[2],
            "company": row[3],
            "location": row[4],
            "salary": row[5],
            "description": row[6],
            "url": row[7],
            "company_rating": row[8],
            "company_rating_summary": row[9],
            "cv_match_score": row[10],
        }

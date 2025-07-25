import logging
from datetime import datetime
from config import SCRAPE_TIMES, SEND_TIMES
from scrape_linkedin import scrape_linkedin_jobs
from scrape_indeed import scrape_indeed_jobs  # your original imports had build_query_params here; replaced with function to scrape jobs
from huggingface_ranker import filter_and_rank_jobs  # match function name you gave me, not 'rank_jobs'
from telegram_bot import send_jobs_to_telegram
from cleanup import run_cleanup
from db import DBHandler
import asyncio

logger = logging.getLogger("jobbot.pipeline")
db = DBHandler()

async def schedule_scraping():
    while True:
        now = datetime.utcnow().time()
        for scrape_time_str in SCRAPE_TIMES:
            scrape_time = datetime.strptime(scrape_time_str, "%H:%M").time()
            if now >= scrape_time:
                logger.info(f"Starting scraping at {scrape_time_str}")

                linkedin_jobs = await scrape_linkedin_jobs()
                indeed_jobs = await scrape_indeed_jobs()
                all_jobs = linkedin_jobs + indeed_jobs
                logger.info(f"Scraped {len(all_jobs)} jobs total.")

                ranked_jobs = filter_and_rank_jobs(all_jobs)
                db.save_jobs(ranked_jobs)
                logger.info(f"Saved {len(ranked_jobs)} ranked jobs to DB.")

                # Sleep to avoid duplicate scrapes in same window
                await asyncio.sleep(60)
                break
        await asyncio.sleep(30)

async def schedule_sending():
    while True:
        now = datetime.utcnow().time()
        for send_time_str in SEND_TIMES:
            send_time = datetime.strptime(send_time_str, "%H:%M").time()
            if now >= send_time:
                logger.info(f"Sending jobs to Telegram at {send_time_str}")
                jobs_to_send = db.get_jobs_to_send(limit=50)
                await send_jobs_to_telegram(jobs_to_send)
                logger.info(f"Sent {len(jobs_to_send)} jobs to Telegram.")

                run_cleanup()
                # Sleep to avoid duplicate sends in same window
                await asyncio.sleep(60)
                break
        await asyncio.sleep(30)

async def main():
    logger.info("Job pipeline started.")
    scraping_task = asyncio.create_task(schedule_scraping())
    sending_task = asyncio.create_task(schedule_sending())
    await asyncio.gather(scraping_task, sending_task)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

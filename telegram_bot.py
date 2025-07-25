import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from db import DBHandler
from utils import format_job_message
from config import TELEGRAM_BOT_TOKEN

logger = logging.getLogger("jobbot.telegram_bot")
db = DBHandler()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Job Bot is online. Use /status to check bot status.")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total_scraped = db.count_scraped_jobs()
    total_sent = db.count_sent_jobs()
    total_accepted = db.count_accepted_jobs()
    uptime = db.get_bot_uptime()
    pending_jobs = db.count_pending_jobs()

    msg = (
        f"📊 Bot Status:\n"
        f"• Jobs scraped: {total_scraped}\n"
        f"• Jobs sent: {total_sent}\n"
        f"• Jobs accepted: {total_accepted}\n"
        f"• Pending jobs: {pending_jobs}\n"
        f"• Uptime: {uptime}\n"
    )
    await update.message.reply_text(msg)

async def sendjob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    job = db.get_random_pending_job()
    if not job:
        await update.message.reply_text("No pending jobs available to send.")
        return

    msg = format_job_message(job)
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Accept", callback_data=f"accept:{job['id']}"),
         InlineKeyboardButton("❌ Decline", callback_data=f"decline:{job['id']}")]
    ])
    await update.message.reply_text(msg, reply_markup=keyboard)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user = query.from_user

    action, job_id = data.split(":")
    job = db.get_job_by_id(job_id)

    if not job:
        await query.edit_message_text("Job no longer available.")
        return

    if action == "accept":
        db.mark_job_accepted(job_id, user.id)
        await query.edit_message_text(f"✅ You accepted the job:\n\n{format_job_message(job)}")
        # Trigger auto-apply process externally
    elif action == "decline":
        db.mark_job_declined(job_id, user.id)
        await query.edit_message_text("❌ Job declined and removed from your feed.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "🤖 Job Bot Commands:\n"
        "/status - Show bot statistics\n"
        "/sendjob - Send one random job\n"
        "/help - Show this message\n"
        "/accepted - List accepted jobs\n"
        "/pending - List pending jobs\n"
        "/declined - List declined jobs\n"
    )
    await update.message.reply_text(msg)

def run_telegram_bot():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("sendjob", sendjob))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button_handler))

    logger.info("Starting Telegram bot...")
    app.run_polling()

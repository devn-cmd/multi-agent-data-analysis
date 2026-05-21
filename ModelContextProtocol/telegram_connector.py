import os
import re
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Initialize the Telegram Bot
bot = Bot(token=TOKEN)

async def get_latest_trigger_message() -> dict | None:
    """
    Check Telegram updates for a message containing 'analyze'.
    Returns a simplified dictionary matching your original logic.
    """
    try:
        # Fetch recent updates (messages sent to the bot)
        updates = await bot.get_updates(limit=10, allowed_updates=["message"])
        
        # Check updates in reverse (newest first)
        for update in reversed(updates):
            if update.message and update.message.text:
                text = update.message.text.lower()
                if "analyze" in text:
                    return {
                        "text": update.message.text,
                        "chat_id": update.message.chat_id
                    }
    except Exception as e:
        print(f"Telegram error fetching updates: {e}")
    return None


def extract_filename_from_message(message: dict) -> str | None:
    """Extract a .csv filename mentioned in the Telegram message."""
    text = message.get("text", "")
    match = re.search(r"[\w\-]+\.csv", text)
    return match.group(0) if match else None


async def post_report_to_telegram(report: str, triggered_by: str = "pipeline") -> bool:
    """Post the final analysis report as a Telegram message."""
    try:
        # Telegram character limit is 4096 (generous compared to Slack's 3000)
        clean_report = report[:4000]
        
        formatted_text = f"<b>Analysis Report</b> (triggered by: {triggered_by})\n\n{clean_report}"
        
        await bot.send_message(
            chat_id=CHAT_ID,
            text=formatted_text,
            parse_mode="HTML"  # Allows bolding via <b> tags
        )
        print("Report posted to Telegram successfully")
        return True
    except Exception as e:
        print(f"Failed to post to Telegram: {e}")
        return False


async def post_error_to_telegram(error_msg: str):
    """Notify the chat if the pipeline fails."""
    try:
        await bot.send_message(
            chat_id=CHAT_ID,
            text=f"⚠️ <b>Pipeline failed:</b> {error_msg}",
            parse_mode="HTML"
        )
    except Exception:
        pass
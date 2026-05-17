import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

load_dotenv()

client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))
CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID")


def get_latest_trigger_message() -> dict | None:
    """Check Slack channel for a message containing 'analyze'."""
    try:
        response = client.conversations_history(channel=CHANNEL_ID, limit=10)
        for msg in response["messages"]:
            text = msg.get("text", "").lower()
            if "analyze" in text:
                return msg
    except SlackApiError as e:
        print(f"Slack error: {e.response['error']}")
    return None


def extract_filename_from_message(message: dict) -> str | None:
    """Extract a .csv filename mentioned in the Slack message."""
    import re
    text = message.get("text", "")
    match = re.search(r"[\w\-]+\.csv", text)
    return match.group(0) if match else None


def post_report_to_slack(report: str, triggered_by: str = "pipeline") -> bool:
    """Post the final analysis report as a Slack message."""
    try:
        client.chat_postMessage(
            channel=CHANNEL_ID,
            text=f"*Analysis Report* (triggered by: {triggered_by})\n\n{report[:2900]}"
            # Slack messages have a 3000 char limit; truncate if needed
        )
        print("Report posted to Slack successfully")
        return True
    except SlackApiError as e:
        print(f"Failed to post to Slack: {e.response['error']}")
        return False


def post_error_to_slack(error_msg: str):
    """Notify the channel if the pipeline fails."""
    try:
        client.chat_postMessage(
            channel=CHANNEL_ID,
            text=f":warning: Pipeline failed: {error_msg}"
        )
    except SlackApiError:
        pass
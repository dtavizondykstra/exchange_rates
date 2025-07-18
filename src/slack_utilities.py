# slack_utilities.py
"""Slack utilities for sending notifications and uploading files in the ETL pipeline."""

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from pathlib import Path
import logging
from config import get_slack_token
from retrying import retry
from utilities import get_current_date

logger = logging.getLogger(__name__)


def _get_client() -> WebClient:
    """Create and return a Slack WebClient instance."""
    token = get_slack_token()
    return WebClient(token=token)


def post_message(text: str, slack_channel: str) -> None:
    """Send a simple text message to Slack."""
    try:
        client = _get_client()
        if not client:
            raise RuntimeError("Failed to create Slack client. Check your token.")
        client.chat_postMessage(channel=slack_channel, text=text)
    except SlackApiError as e:
        # if you want to log Slack errors, you could re-raise or print
        raise RuntimeError(f"Slack post failed: {e.response['error']}")


def upload_file(file_path: Path, slack_channel: str) -> None:
    """Upload the given file into Slack as a snippet."""
    try:
        client = _get_client()
        if not client:
            raise RuntimeError("Failed to create Slack client. Check your token.")
        client.files_upload(
            channels=slack_channel,
            file=str(file_path),
            title=f"ETL log: {file_path.name}",
        )
    except SlackApiError as e:
        raise RuntimeError(f"Slack file upload failed: {e.response['error']}")


@retry(
    stop_max_attempt_number=3,
    wait_fixed=2000,
    retry_on_exception=lambda e: isinstance(e, SlackApiError),
)
def notify_success(log_path: Path, slack_channel: str) -> None:
    """Notify Slack about successful ETL completion and upload log file."""
    post_message(f":white_check_mark: ETL completed *successfully* for {get_current_date()}!", slack_channel)


@retry(
    stop_max_attempt_number=3,
    wait_fixed=2000,
    retry_on_exception=lambda e: isinstance(e, SlackApiError),
)
def notify_failure(log_path: Path, error_msg: str, slack_channel: str) -> None:
    """Notify Slack about ETL failure and upload log file."""
    post_message(f":x: ETL *failed* for {get_current_date()} with error: {error_msg}", slack_channel)
    upload_file(log_path, slack_channel)

# tests/test_slack_utilities.py
import pytest
from pathlib import Path
from slack_sdk.errors import SlackApiError
import sys

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import slack_utilities as su


class DummyResponse:
    def __init__(self, error):
        self.error = error

    def __getitem__(self, item):
        if item == "error":
            return self.error


@pytest.fixture(autouse=True)
def fake_client(monkeypatch):
    """Replace su.client with a dummy that records calls."""

    class FakeClient:
        def __init__(self):
            self.posts = []
            self.uploads = []

        def chat_postMessage(self, channel, text):
            # simulate normal behavior
            self.posts.append((channel, text))
            return {"ok": True}

        def files_upload(self, channels, file, title):
            self.uploads.append((channels, file, title))
            return {"ok": True}

    fake = FakeClient()
    monkeypatch.setattr(su, "client", fake)
    return fake


def test_post_message_success(fake_client):
    su.post_message("hello", "#chan")
    assert fake_client.posts == [("#chan", "hello")]


def test_post_message_failure(monkeypatch):
    # make client.chat_postMessage raise SlackApiError
    def bad_post(self, *args, **kwargs):
        raise SlackApiError(message="fail", response=DummyResponse("bad_auth"))

    fake = type("C", (object,), {"chat_postMessage": bad_post})()
    monkeypatch.setattr(su, "client", fake)

    with pytest.raises(RuntimeError) as exc:
        su.post_message("hello", "#chan")

    assert "bad_auth" in str(exc.value)


def test_upload_file_success(fake_client, tmp_path):
    logfile = tmp_path / "log.txt"
    logfile.write_text("test")
    su.upload_file(logfile, "#chan")
    assert fake_client.uploads == [("#chan", str(logfile), f"ETL log: {logfile.name}")]


def test_upload_file_failure(monkeypatch, tmp_path):
    def bad_upload(self, *args, **kwargs):
        raise SlackApiError(message="fail", response=DummyResponse("too_large"))

    fake = type("C", (object,), {"files_upload": bad_upload})()
    monkeypatch.setattr(su, "client", fake)

    logfile = tmp_path / "log.txt"
    logfile.write_text("test")

    with pytest.raises(RuntimeError) as exc:
        su.upload_file(logfile, "#chan")

    assert "too_large" in str(exc.value)


def test_notify_success(fake_client, tmp_path, monkeypatch):
    # Patch CURRENT_DATE so message is predictable
    monkeypatch.setattr(su, "CURRENT_DATE", "2099-12-31")
    log = tmp_path / "d.log"
    log.write_text("x")
    su.notify_success(log, "#chan")
    assert fake_client.posts[-1] == ("#chan", ":white_check_mark: ETL completed *successfully* for 2099-12-31!")


def test_notify_failure(fake_client, tmp_path, monkeypatch):
    monkeypatch.setattr(su, "CURRENT_DATE", "2099-12-31")
    log = tmp_path / "d.log"
    log.write_text("x")
    su.notify_failure(log, "oops", "#chan")
    # last two calls: failure message, then upload
    assert fake_client.posts[-1] == ("#chan", ":x: ETL *failed* for 2099-12-31 with error: oops")
    assert fake_client.uploads[-1][1] == str(log)

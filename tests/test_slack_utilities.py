import pytest
from pathlib import Path
from slack_sdk.errors import SlackApiError
import sys

# Ensure we import the version under src/
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

import slack_utilities as su


class DummyResponse:
    def __init__(self, error):
        self.error = error

    def __getitem__(self, item):
        if item == "error":
            return self.error


@pytest.fixture(autouse=True)
def fake_client_and_date(monkeypatch):
    """Make su._get_client return a fake client and su.get_current_date return fixed date."""

    # Fake Slack client
    class FakeClient:
        def __init__(self):
            self.posts = []
            self.uploads = []

        def chat_postMessage(self, **kwargs):
            self.posts.append((kwargs["channel"], kwargs["text"]))
            return {"ok": True}

        def files_upload(self, **kwargs):
            self.uploads.append((kwargs["channels"], kwargs["file"], kwargs["title"]))
            return {"ok": True}

    fake = FakeClient()
    # Patch the Slack client factory
    monkeypatch.setattr(su, "_get_client", lambda: fake)
    # Patch the date helper in slack_utilities
    monkeypatch.setattr(su, "get_current_date", lambda: "2099-12-31")
    return fake


def test_post_message_success(fake_client_and_date):
    su.post_message("hello", "#chan")
    assert fake_client_and_date.posts == [("#chan", "hello")]


def test_post_message_failure(monkeypatch):
    # Make chat_postMessage raise SlackApiError
    def bad_post(self, **kwargs):
        raise SlackApiError(message="fail", response=DummyResponse("bad_auth"))

    fake = type("C", (), {"chat_postMessage": bad_post})()
    monkeypatch.setattr(su, "_get_client", lambda: fake)

    with pytest.raises(RuntimeError) as exc:
        su.post_message("hello", "#chan")
    assert "bad_auth" in str(exc.value)


def test_upload_file_success(fake_client_and_date, tmp_path):
    logfile = tmp_path / "log.txt"
    logfile.write_text("test")
    su.upload_file(logfile, "#chan")
    assert fake_client_and_date.uploads == [("#chan", str(logfile), f"ETL log: {logfile.name}")]


def test_upload_file_failure(monkeypatch, tmp_path):
    # Make files_upload raise SlackApiError
    def bad_upload(self, **kwargs):
        raise SlackApiError(message="fail", response=DummyResponse("too_large"))

    fake = type("C", (), {"files_upload": bad_upload})()
    monkeypatch.setattr(su, "_get_client", lambda: fake)

    logfile = tmp_path / "log.txt"
    logfile.write_text("test")

    with pytest.raises(RuntimeError) as exc:
        su.upload_file(logfile, "#chan")
    assert "too_large" in str(exc.value)


def test_notify_success(fake_client_and_date, tmp_path):
    log = tmp_path / "d.log"
    log.write_text("x")
    su.notify_success(log, "#chan")
    assert fake_client_and_date.posts[-1] == (
        "#chan",
        ":white_check_mark: ETL completed *successfully* for 2099-12-31!",
    )


def test_notify_failure(fake_client_and_date, tmp_path):
    log = tmp_path / "d.log"
    log.write_text("x")
    su.notify_failure(log, "oops", "#chan")
    # Expect failure message then file upload
    assert fake_client_and_date.posts[-1] == ("#chan", ":x: ETL *failed* for 2099-12-31 with error: oops")
    assert fake_client_and_date.uploads[-1][1] == str(log)

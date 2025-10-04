from time import time

from logging_utils import (
    LogEntry,
    filter_logs,
    serialize_logs_text,
    compute_metrics,
    read_history,
)


def _sample_logs():
    t = time()
    return [
        {"timestamp_epoch": t, "level": "INFO", "message": "Server started", "logger": "app"},
        {"timestamp_epoch": t + 1, "level": "ERROR", "message": "Failed to connect DB", "logger": "db"},
        {"timestamp_epoch": t + 2, "level": "INFO", "message": "Listening on port 8080", "logger": "app"},
        {"timestamp_epoch": t + 3, "level": "WARNING", "message": "Slow query", "logger": "db"},
    ]


def test_filter_by_level_and_search():
    logs = _sample_logs()
    only_info = filter_logs(logs, level="INFO")
    assert len(only_info) == 2

    db_errors = filter_logs(logs, level="ERROR", search="db")
    assert len(db_errors) == 1
    assert "Failed to connect" in db_errors[0]["message"]


def test_serialize_logs_text():
    logs = _sample_logs()
    text = serialize_logs_text(logs)
    assert "INFO" in text and "ERROR" in text
    assert "Server started" in text


def test_compute_metrics():
    logs = _sample_logs()
    metrics = compute_metrics(logs)
    assert metrics["total"] == 4
    assert metrics["counts"]["INFO"] == 2
    assert metrics["counts"]["ERROR"] == 1
    assert metrics["rate_per_minute"] > 0


def test_read_history_not_found_returns_empty(tmp_path):
    path = tmp_path / "missing.jsonl"
    result = read_history(str(path))
    assert result == []

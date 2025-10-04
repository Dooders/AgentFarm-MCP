"""Utilities for logging integration in the Streamlit demo.

This module contains only pure-Python helpers with no Streamlit imports,
so unit tests can run without the app environment.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple
import json
from datetime import datetime


@dataclass
class LogEntry:
    timestamp_epoch: float
    level: str
    message: str
    logger: str | None = None

    def to_dict(self) -> Dict:
        return {
            "timestamp_epoch": self.timestamp_epoch,
            "timestamp": datetime.fromtimestamp(self.timestamp_epoch).isoformat(timespec="seconds"),
            "level": self.level,
            "message": self.message,
            "logger": self.logger,
        }


def filter_logs(logs: Iterable[Dict], level: str = "All", search: str = "") -> List[Dict]:
    """Filter logs by level and substring search (case-insensitive).

    - level: one of 'All', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
    - search: plain substring matched against message and logger
    """
    level = (level or "All").upper()
    search_norm = (search or "").strip().lower()

    filtered: List[Dict] = []
    for entry in logs:
        entry_level = (entry.get("level") or "").upper()
        entry_message = str(entry.get("message", ""))
        entry_logger = str(entry.get("logger", ""))

        if level != "ALL" and entry_level != level:
            continue
        if search_norm:
            hay = f"{entry_message}\n{entry_logger}".lower()
            if search_norm not in hay:
                continue
        filtered.append(entry)
    return filtered


def serialize_logs_text(logs: Iterable[Dict]) -> str:
    """Serialize logs to a simple human-readable text format."""
    lines: List[str] = []
    for e in logs:
        ts = e.get("timestamp")
        if not ts and (ep := e.get("timestamp_epoch")):
            ts = datetime.fromtimestamp(float(ep)).isoformat(timespec="seconds")
        level = e.get("level", "").upper()
        message = str(e.get("message", ""))
        logger = e.get("logger")
        prefix = f"[{ts}] {level}" if ts else level
        if logger:
            prefix += f" {logger}"
        lines.append(f"{prefix}: {message}")
    return "\n".join(lines)


def compute_metrics(logs: Iterable[Dict]) -> Dict:
    """Compute per-level counts and a simple messages-per-minute rate.

    Rate is computed over the time window between the first and last log that
    have a timestamp; if unavailable or window is 0, rate is 0.
    """
    levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    counts = {lvl: 0 for lvl in levels}

    timestamps: List[float] = []
    total = 0

    for e in logs:
        lvl = (e.get("level") or "").upper()
        if lvl in counts:
            counts[lvl] += 1
        total += 1
        ep = e.get("timestamp_epoch")
        if isinstance(ep, (int, float)):
            timestamps.append(float(ep))

    rate_per_minute = 0.0
    if len(timestamps) >= 2:
        start, end = min(timestamps), max(timestamps)
        duration_seconds = max(0.0, end - start)
        if duration_seconds > 0:
            rate_per_minute = total / (duration_seconds / 60.0)

    return {
        "counts": counts,
        "total": total,
        "rate_per_minute": rate_per_minute,
    }


def read_history(path: str) -> List[Dict]:
    """Read JSONL logs from disk; returns a list of dicts."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]
    except FileNotFoundError:
        return []


def append_history(path: str, entry: Dict) -> None:
    """Append one log entry as JSONL to disk."""
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def clear_history(path: str) -> None:
    """Clear the history file."""
    with open(path, "w", encoding="utf-8") as f:
        f.truncate(0)

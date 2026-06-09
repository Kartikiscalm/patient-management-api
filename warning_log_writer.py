
from pathlib import Path


ERROR_KEYWORDS = ("warning", "warn", "error", "critical", "exception", "failed", "failure")


def has_warning_or_error(message: str) -> bool:
    lower_message = message.lower()
    return any(keyword in lower_message for keyword in ERROR_KEYWORDS)


def format_log(log: dict) -> str:
    labels = log["labels"]
    source = labels.get("pod") or labels.get("job") or labels.get("container") or "unknown"
    return f'{log["time"]} | {source} | {log["message"]}'


def append_flagged_logs(logs: list[dict], output_file: Path, written_ids: set[tuple[str, str]]) -> int:
    flagged_logs = []

    for log in logs:
        log_id = (log["timestamp"], log["message"])
        if log_id in written_ids:
            continue

        if has_warning_or_error(log["message"]):
            flagged_logs.append(log)
            written_ids.add(log_id)

    if not flagged_logs:
        return 0

    with output_file.open("a", encoding="utf-8") as file:
        for log in reversed(flagged_logs):
            file.write(format_log(log) + "\n")

    return len(flagged_logs)
#generated
import argparse
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

from warning_log_writer import append_flagged_logs, format_log


DEFAULT_LOKI_URL = "http://localhost:3100"
DEFAULT_QUERY = '{namespace="default"}'
DEFAULT_OUTPUT_FILE = "warning_error_logs.txt"


def ns_to_time(ns_timestamp: str) -> str:
    seconds = int(ns_timestamp) / 1_000_000_000
    return datetime.fromtimestamp(seconds, tz=timezone.utc).isoformat()


def flatten_loki_streams(result: list[dict]) -> list[dict]:
    logs = []

    for stream in result:
        labels = stream.get("stream", {})
        for timestamp, message in stream.get("values", []):
            logs.append(
                {
                    "timestamp": timestamp,
                    "time": ns_to_time(timestamp),
                    "message": message,
                    "labels": labels,
                }
            )

    logs.sort(key=lambda item: int(item["timestamp"]), reverse=True)
    return logs


def fetch_latest_logs(client: httpx.Client, loki_url: str, query: str, limit: int) -> list[dict]:
    response = client.get(
        f"{loki_url.rstrip('/')}/loki/api/v1/query_range",
        params={
            "query": query,
            "limit": limit,
            "direction": "backward",
        },
    )
    response.raise_for_status()

    payload = response.json()
    if payload.get("status") != "success":
        raise RuntimeError(f"Loki query failed: {payload}")

    return flatten_loki_streams(payload["data"]["result"])[:limit]


def poll_logs(args: argparse.Namespace) -> None:
    output_file = Path(args.output_file)
    written_ids: set[tuple[str, str]] = set()

    print(f"Polling Loki every {args.interval} seconds")
    print(f"Loki URL: {args.loki_url}")
    print(f"Query: {args.query}")
    print(f"Writing warning/error logs to: {output_file}")
    print("Press Ctrl+C to stop.\n")

    with httpx.Client(timeout=args.timeout) as client:
        while True:
            try:
                logs = fetch_latest_logs(client, args.loki_url, args.query, args.limit)
                print(f"Latest {len(logs)} logs at {datetime.now().strftime('%H:%M:%S')}:")

                for log in logs:
                    print(format_log(log))

                added_count = append_flagged_logs(logs, output_file, written_ids)
                if added_count:
                    print(f"Added {added_count} warning/error log(s) to {output_file}")

                print()
            except httpx.HTTPError as exc:
                print(f"Could not reach Loki: {exc}")
            except Exception as exc:
                print(f"Could not read logs: {exc}")

            time.sleep(args.interval)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Poll Loki logs and save warning/error entries.")
    parser.add_argument("--loki-url", default=DEFAULT_LOKI_URL)
    parser.add_argument("--query", default=DEFAULT_QUERY)
    parser.add_argument("--interval", type=int, default=5)
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--output-file", default=DEFAULT_OUTPUT_FILE)
    parser.add_argument("--timeout", type=float, default=10.0)
    return parser.parse_args()


if __name__ == "__main__":
    try:
        poll_logs(parse_args())
    except KeyboardInterrupt:
        print("\nStopped.")
#generated
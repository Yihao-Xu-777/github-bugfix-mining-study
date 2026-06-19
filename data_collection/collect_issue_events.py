import os
import time
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv
from requests.exceptions import RequestException, Timeout, ConnectionError


PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_ISSUES_CSV = PROJECT_ROOT / "dataset" / "raw" / "bug_issues_raw.csv"
RAW_EVENTS_CSV = PROJECT_ROOT / "dataset" / "raw" / "issue_events_raw.csv"
CLOSURE_EVENTS_CSV = PROJECT_ROOT / "dataset" / "processed" / "issue_closure_events.csv"

GITHUB_API_BASE = "https://api.github.com"


EVENT_COLUMNS = [
    "owner",
    "repo",
    "issue_number",
    "event_id",
    "event",
    "event_created_at",
    "commit_id",
    "commit_url",
    "actor_login",
]


CLOSURE_COLUMNS = [
    "owner",
    "repo",
    "issue_number",
    "closed_event_created_at",
    "commit_id",
    "commit_url",
    "closed_by",
    "closure_type",
]


def get_headers():
    load_dotenv()

    token = os.getenv("GITHUB_TOKEN")

    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "github-bugfix-mining-study",
    }

    if token:
        headers["Authorization"] = f"Bearer {token}"

    return headers


def request_with_retry(url, headers, params, max_retries=3):
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=60,
            )

            return response

        except (Timeout, ConnectionError, RequestException) as error:
            print(f"Request failed on attempt {attempt}/{max_retries}: {error}")

            if attempt < max_retries:
                wait_time = attempt * 10
                print(f"Waiting {wait_time} seconds before retrying...")
                time.sleep(wait_time)
            else:
                print("Max retries reached. Skipping this request.")
                return None


def fetch_issue_events(owner, repo, issue_number, max_pages=3):
    headers = get_headers()
    rows = []

    for page in range(1, max_pages + 1):
        url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/issues/{issue_number}/events"

        params = {
            "per_page": 100,
            "page": page,
        }

        response = request_with_retry(url, headers, params)

        if response is None:
            break

        if response.status_code != 200:
            print(
                f"Failed to fetch events for {owner}/{repo} issue #{issue_number}, "
                f"page {page}: {response.status_code}"
            )
            print(response.text[:300])
            break

        events = response.json()

        if not events:
            break

        for event in events:
            rows.append(
                {
                    "owner": owner,
                    "repo": repo,
                    "issue_number": issue_number,
                    "event_id": event.get("id"),
                    "event": event.get("event"),
                    "event_created_at": event.get("created_at"),
                    "commit_id": event.get("commit_id"),
                    "commit_url": event.get("commit_url"),
                    "actor_login": (event.get("actor") or {}).get("login"),
                }
            )

        time.sleep(0.5)

    return rows


def build_closure_event_table(events_df):
    if events_df.empty:
        return pd.DataFrame(columns=CLOSURE_COLUMNS)

    if "event" not in events_df.columns:
        return pd.DataFrame(columns=CLOSURE_COLUMNS)

    closed_events = events_df[events_df["event"] == "closed"].copy()

    if closed_events.empty:
        return pd.DataFrame(columns=CLOSURE_COLUMNS)

    closed_events["event_created_at"] = pd.to_datetime(
        closed_events["event_created_at"], errors="coerce", utc=True
    )

    closed_events = closed_events.sort_values("event_created_at")

    latest_closed_events = (
        closed_events.groupby(["owner", "repo", "issue_number"])
        .tail(1)
        .copy()
    )

    latest_closed_events["closure_type"] = latest_closed_events["commit_id"].apply(
        lambda value: "commit_linked"
        if pd.notna(value) and str(value).strip()
        else "manual_or_unknown"
    )

    result = latest_closed_events.rename(
        columns={
            "event_created_at": "closed_event_created_at",
            "actor_login": "closed_by",
        }
    )

    return result[CLOSURE_COLUMNS]


def load_existing_events():
    if RAW_EVENTS_CSV.exists():
        try:
            existing = pd.read_csv(RAW_EVENTS_CSV)

            if existing.empty:
                return pd.DataFrame(columns=EVENT_COLUMNS)

            return existing

        except pd.errors.EmptyDataError:
            return pd.DataFrame(columns=EVENT_COLUMNS)

    return pd.DataFrame(columns=EVENT_COLUMNS)


def save_outputs(events_df):
    RAW_EVENTS_CSV.parent.mkdir(parents=True, exist_ok=True)
    CLOSURE_EVENTS_CSV.parent.mkdir(parents=True, exist_ok=True)

    events_df.to_csv(RAW_EVENTS_CSV, index=False, encoding="utf-8")

    closure_events = build_closure_event_table(events_df)
    closure_events.to_csv(CLOSURE_EVENTS_CSV, index=False, encoding="utf-8")

    print(f"Progress saved to: {RAW_EVENTS_CSV}")
    print(f"Closure events saved to: {CLOSURE_EVENTS_CSV}")


def main():
    if not RAW_ISSUES_CSV.exists():
        print("Raw bug issue data not found. Run data_collection/collect_bug_issues.py first.")
        return

    issues = pd.read_csv(RAW_ISSUES_CSV)

    if issues.empty:
        print("No bug issues found in raw issue data.")
        return

    existing_events = load_existing_events()

    completed_issues = set()

    if not existing_events.empty:
        completed_issues = set(
            zip(
                existing_events["owner"],
                existing_events["repo"],
                existing_events["issue_number"],
            )
        )

    all_events = existing_events.to_dict("records")

    try:
        for _, row in issues.iterrows():
            owner = row["owner"]
            repo = row["repo"]
            issue_number = row["issue_number"]

            issue_key = (owner, repo, issue_number)

            if issue_key in completed_issues:
                print(f"Skipping already collected issue: {owner}/{repo} #{issue_number}")
                continue

            print(f"Collecting events for {owner}/{repo} issue #{issue_number}")

            events = fetch_issue_events(owner, repo, issue_number)
            all_events.extend(events)

            events_df = pd.DataFrame(all_events, columns=EVENT_COLUMNS)
            save_outputs(events_df)

            completed_issues.add(issue_key)

        final_events_df = pd.DataFrame(all_events, columns=EVENT_COLUMNS)
        save_outputs(final_events_df)

        print(f"Total events collected: {len(final_events_df)}")
        print("Issue event collection completed.")

    except KeyboardInterrupt:
        print("Interrupted by user. Saving current progress...")
        events_df = pd.DataFrame(all_events, columns=EVENT_COLUMNS)
        save_outputs(events_df)


if __name__ == "__main__":
    main()


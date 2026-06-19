import os
import time
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]

CLOSURE_EVENTS_CSV = PROJECT_ROOT / "dataset" / "processed" / "issue_closure_events.csv"

BUGFIX_COMMITS_CSV = PROJECT_ROOT / "dataset" / "processed" / "bugfix_commits.csv"
BUGFIX_COMMIT_FILES_CSV = PROJECT_ROOT / "dataset" / "processed" / "bugfix_commit_files.csv"

RESULTS_BUGFIX_COMMITS_CSV = PROJECT_ROOT / "results" / "tables" / "bugfix_commits.csv"

GITHUB_API_BASE = "https://api.github.com"


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


def get_file_extension(filename):
    filename = str(filename)

    if "." not in filename:
        return "no_extension"

    extension = filename.rsplit(".", 1)[-1].lower()

    if not extension:
        return "no_extension"

    return f".{extension}"


def fetch_commit_detail(owner, repo, commit_sha):
    headers = get_headers()

    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/commits/{commit_sha}"

    response = requests.get(url, headers=headers, timeout=30)

    if response.status_code != 200:
        print(f"Failed to fetch commit {owner}/{repo}@{commit_sha}: {response.status_code}")
        print(response.text[:300])
        return None

    return response.json()


def parse_commit(owner, repo, commit_sha, commit_data):
    stats = commit_data.get("stats") or {}
    commit = commit_data.get("commit") or {}
    author = commit.get("author") or {}

    commit_row = {
        "owner": owner,
        "repo": repo,
        "project": f"{owner}/{repo}",
        "commit_id": commit_sha,
        "commit_message": commit.get("message"),
        "commit_date": author.get("date"),
        "total_changes": stats.get("total", 0),
        "additions": stats.get("additions", 0),
        "deletions": stats.get("deletions", 0),
        "changed_files": len(commit_data.get("files") or []),
        "html_url": commit_data.get("html_url"),
    }

    file_rows = []

    for file_item in commit_data.get("files") or []:
        filename = file_item.get("filename")

        file_rows.append(
            {
                "owner": owner,
                "repo": repo,
                "project": f"{owner}/{repo}",
                "commit_id": commit_sha,
                "filename": filename,
                "file_extension": get_file_extension(filename),
                "status": file_item.get("status"),
                "additions": file_item.get("additions", 0),
                "deletions": file_item.get("deletions", 0),
                "changes": file_item.get("changes", 0),
            }
        )

    return commit_row, file_rows


def main():
    if not CLOSURE_EVENTS_CSV.exists():
        print("Closure event data not found. Run data_collection/collect_issue_events.py first.")
        return

    closure_events = pd.read_csv(CLOSURE_EVENTS_CSV)

    if closure_events.empty:
        print("Closure event data is empty.")
        return

    linked_events = closure_events[
        closure_events["commit_id"].notna()
        & (closure_events["commit_id"].astype(str).str.strip() != "")
    ].copy()

    if linked_events.empty:
        print("No commit-linked closure events found.")
        return

    unique_commits = (
        linked_events[["owner", "repo", "commit_id"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )

    commit_rows = []
    file_rows = []

    for _, row in unique_commits.iterrows():
        owner = row["owner"]
        repo = row["repo"]
        commit_sha = row["commit_id"]

        print(f"Collecting commit detail for {owner}/{repo}@{commit_sha}")

        commit_data = fetch_commit_detail(owner, repo, commit_sha)

        if commit_data is None:
            continue

        commit_row, commit_file_rows = parse_commit(owner, repo, commit_sha, commit_data)

        commit_rows.append(commit_row)
        file_rows.extend(commit_file_rows)

        time.sleep(0.5)

    BUGFIX_COMMITS_CSV.parent.mkdir(parents=True, exist_ok=True)
    RESULTS_BUGFIX_COMMITS_CSV.parent.mkdir(parents=True, exist_ok=True)

    commits_df = pd.DataFrame(commit_rows)
    files_df = pd.DataFrame(file_rows)

    commits_df.to_csv(BUGFIX_COMMITS_CSV, index=False, encoding="utf-8")
    files_df.to_csv(BUGFIX_COMMIT_FILES_CSV, index=False, encoding="utf-8")
    commits_df.to_csv(RESULTS_BUGFIX_COMMITS_CSV, index=False, encoding="utf-8")

    print(f"Bug-fix commits saved to: {BUGFIX_COMMITS_CSV}")
    print(f"Bug-fix commit files saved to: {BUGFIX_COMMIT_FILES_CSV}")
    print(f"Results bug-fix commits saved to: {RESULTS_BUGFIX_COMMITS_CSV}")
    print(f"Total linked commits collected: {len(commits_df)}")
    print(f"Total changed files collected: {len(files_df)}")


if __name__ == "__main__":
    main()
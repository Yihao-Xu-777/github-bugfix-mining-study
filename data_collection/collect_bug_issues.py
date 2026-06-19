import os
import time
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPOS_CSV = PROJECT_ROOT / "config" / "repos.csv"
OUTPUT_CSV = PROJECT_ROOT / "dataset" / "raw" / "bug_issues_raw.csv"


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


def fetch_closed_bug_issues(owner, repo, max_pages=3):
    """
    Fetch closed issues with the 'bug' label from a GitHub repository.

    Pull requests are filtered out because GitHub returns pull requests
    in the issues endpoint as issue-like objects.
    """
    headers = get_headers()
    all_rows = []

    for page in range(1, max_pages + 1):
        url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/issues"

        params = {
            "state": "closed",
            "labels": "bug",
            "per_page": 100,
            "page": page,
        }

        response = requests.get(url, headers=headers, params=params, timeout=30)

        if response.status_code != 200:
            print(f"Failed to fetch {owner}/{repo}, page {page}: {response.status_code}")
            print(response.text[:300])
            break

        issues = response.json()

        if not issues:
            break

        for issue in issues:
            # Skip pull requests
            if "pull_request" in issue:
                continue

            labels = [label["name"] for label in issue.get("labels", [])]

            row = {
                "owner": owner,
                "repo": repo,
                "issue_number": issue.get("number"),
                "title": issue.get("title"),
                "state": issue.get("state"),
                "created_at": issue.get("created_at"),
                "closed_at": issue.get("closed_at"),
                "comments": issue.get("comments"),
                "labels": ";".join(labels),
                "html_url": issue.get("html_url"),
            }

            all_rows.append(row)

        print(f"Fetched {owner}/{repo}, page {page}, issues collected so far: {len(all_rows)}")

        time.sleep(1)

    return all_rows


def main():
    repos = pd.read_csv(REPOS_CSV)

    all_issues = []

    for _, row in repos.iterrows():
        owner = row["owner"]
        repo = row["repo"]

        print(f"Collecting closed bug issues from {owner}/{repo}")
        issues = fetch_closed_bug_issues(owner, repo, max_pages=3)
        all_issues.extend(issues)

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)

    result = pd.DataFrame(all_issues)
    result.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")

    print(f"Saved raw bug issue data to: {OUTPUT_CSV}")
    print(f"Total collected issues: {len(result)}")


if __name__ == "__main__":
    main()
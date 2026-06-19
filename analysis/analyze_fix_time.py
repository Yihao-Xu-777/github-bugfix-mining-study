from collections import Counter
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_CSV = PROJECT_ROOT / "dataset" / "raw" / "bug_issues_raw.csv"
PROCESSED_CSV = PROJECT_ROOT / "dataset" / "processed" / "bug_issues_processed.csv"
PROJECT_SUMMARY_CSV = PROJECT_ROOT / "dataset" / "processed" / "project_summary.csv"
KEYWORD_SUMMARY_CSV = PROJECT_ROOT / "dataset" / "processed" / "keyword_summary.csv"

RESULTS_PROJECT_SUMMARY = PROJECT_ROOT / "results" / "tables" / "project_summary.csv"
RESULTS_KEYWORD_SUMMARY = PROJECT_ROOT / "results" / "tables" / "keyword_summary.csv"


STOPWORDS = {
    "the", "a", "an", "and", "or", "to", "of", "in", "on", "for", "with",
    "is", "are", "be", "not", "when", "from", "by", "as", "at", "into",
    "error", "bug", "issue", "fix", "fixed", "fail", "fails", "failure",
}


def clean_and_compute_fix_time(data):
    data = data.copy()

    data["created_at"] = pd.to_datetime(data["created_at"], errors="coerce", utc=True)
    data["closed_at"] = pd.to_datetime(data["closed_at"], errors="coerce", utc=True)

    data = data.dropna(subset=["created_at", "closed_at"])

    data["fix_time_hours"] = (
        data["closed_at"] - data["created_at"]
    ).dt.total_seconds() / 3600

    data["fix_time_days"] = data["fix_time_hours"] / 24

    # Remove abnormal negative values if any
    data = data[data["fix_time_hours"] >= 0]

    data["project"] = data["owner"] + "/" + data["repo"]

    return data


def generate_project_summary(data):
    summary = (
        data.groupby("project")
        .agg(
            bug_issues=("issue_number", "count"),
            avg_fix_time_days=("fix_time_days", "mean"),
            median_fix_time_days=("fix_time_days", "median"),
            avg_comments=("comments", "mean"),
        )
        .reset_index()
    )

    summary["avg_fix_time_days"] = summary["avg_fix_time_days"].round(2)
    summary["median_fix_time_days"] = summary["median_fix_time_days"].round(2)
    summary["avg_comments"] = summary["avg_comments"].round(2)

    return summary


def tokenize_title(title):
    title = str(title).lower()

    cleaned = ""

    for char in title:
        if char.isalnum() or char.isspace():
            cleaned += char
        else:
            cleaned += " "

    words = cleaned.split()

    words = [
        word for word in words
        if word not in STOPWORDS and len(word) >= 3
    ]

    return words


def generate_keyword_summary(data, top_n=30):
    counter = Counter()

    for title in data["title"].dropna():
        counter.update(tokenize_title(title))

    rows = [
        {"keyword": keyword, "count": count}
        for keyword, count in counter.most_common(top_n)
    ]

    return pd.DataFrame(rows)


def main():
    if not RAW_CSV.exists():
        print("Raw data not found. Run data_collection/collect_bug_issues.py first.")
        return

    data = pd.read_csv(RAW_CSV)

    if data.empty:
        print("Raw data is empty.")
        return

    processed = clean_and_compute_fix_time(data)
    project_summary = generate_project_summary(processed)
    keyword_summary = generate_keyword_summary(processed)

    PROCESSED_CSV.parent.mkdir(parents=True, exist_ok=True)
    RESULTS_PROJECT_SUMMARY.parent.mkdir(parents=True, exist_ok=True)

    processed.to_csv(PROCESSED_CSV, index=False, encoding="utf-8")
    project_summary.to_csv(PROJECT_SUMMARY_CSV, index=False, encoding="utf-8")
    keyword_summary.to_csv(KEYWORD_SUMMARY_CSV, index=False, encoding="utf-8")

    project_summary.to_csv(RESULTS_PROJECT_SUMMARY, index=False, encoding="utf-8")
    keyword_summary.to_csv(RESULTS_KEYWORD_SUMMARY, index=False, encoding="utf-8")

    print(f"Processed data saved to: {PROCESSED_CSV}")
    print(f"Project summary saved to: {PROJECT_SUMMARY_CSV}")
    print(f"Keyword summary saved to: {KEYWORD_SUMMARY_CSV}")


if __name__ == "__main__":
    main()
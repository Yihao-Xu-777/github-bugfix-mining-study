from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

BUG_ISSUES_PROCESSED_CSV = PROJECT_ROOT / "dataset" / "processed" / "bug_issues_processed.csv"
CLOSURE_EVENTS_CSV = PROJECT_ROOT / "dataset" / "processed" / "issue_closure_events.csv"
BUGFIX_COMMITS_CSV = PROJECT_ROOT / "dataset" / "processed" / "bugfix_commits.csv"
BUGFIX_COMMIT_FILES_CSV = PROJECT_ROOT / "dataset" / "processed" / "bugfix_commit_files.csv"

RESULTS_DIR = PROJECT_ROOT / "results" / "tables"

BUG_ISSUE_COMMIT_LINKS_CSV = RESULTS_DIR / "bug_issue_commit_links.csv"
PROJECT_SUMMARY_V2_CSV = RESULTS_DIR / "project_summary_v2.csv"
FILE_EXTENSION_SUMMARY_CSV = RESULTS_DIR / "file_extension_summary.csv"


def read_csv_if_exists(path):
    path = Path(path)

    if not path.exists():
        print(f"Missing file: {path}")
        return pd.DataFrame()

    return pd.read_csv(path)


def build_issue_commit_links(issues, closure_events, commits):
    issues = issues.copy()

    issues["project"] = issues["owner"] + "/" + issues["repo"]

    links = issues.merge(
        closure_events,
        on=["owner", "repo", "issue_number"],
        how="left",
    )

    if not commits.empty:
        commit_columns = [
            "owner",
            "repo",
            "commit_id",
            "commit_message",
            "commit_date",
            "total_changes",
            "additions",
            "deletions",
            "changed_files",
            "html_url",
        ]

        available_commit_columns = [
            column for column in commit_columns if column in commits.columns
        ]

        links = links.merge(
            commits[available_commit_columns],
            on=["owner", "repo", "commit_id"],
            how="left",
            suffixes=("", "_commit"),
        )

    links["linked_to_commit"] = links["commit_id"].notna() & (
        links["commit_id"].astype(str).str.strip() != ""
    )

    selected_columns = [
        "owner",
        "repo",
        "project",
        "issue_number",
        "title",
        "created_at",
        "closed_at",
        "fix_time_days",
        "comments",
        "labels",
        "html_url",
        "closed_event_created_at",
        "commit_id",
        "commit_message",
        "commit_date",
        "total_changes",
        "additions",
        "deletions",
        "changed_files",
        "linked_to_commit",
        "closure_type",
    ]

    selected_columns = [column for column in selected_columns if column in links.columns]

    return links[selected_columns]


def build_project_summary_v2(issue_commit_links):
    grouped = (
        issue_commit_links.groupby("project")
        .agg(
            bug_issues=("issue_number", "count"),
            linked_bug_issues=("linked_to_commit", "sum"),
            avg_fix_time_days=("fix_time_days", "mean"),
            median_fix_time_days=("fix_time_days", "median"),
            avg_comments=("comments", "mean"),
            avg_total_changes=("total_changes", "mean"),
            avg_additions=("additions", "mean"),
            avg_deletions=("deletions", "mean"),
            avg_changed_files=("changed_files", "mean"),
        )
        .reset_index()
    )

    grouped["commit_link_rate"] = (
        grouped["linked_bug_issues"] / grouped["bug_issues"] * 100
    )

    numeric_columns = [
        "avg_fix_time_days",
        "median_fix_time_days",
        "avg_comments",
        "avg_total_changes",
        "avg_additions",
        "avg_deletions",
        "avg_changed_files",
        "commit_link_rate",
    ]

    for column in numeric_columns:
        if column in grouped.columns:
            grouped[column] = grouped[column].round(2)

    return grouped


def build_file_extension_summary(commit_files):
    if commit_files.empty:
        return pd.DataFrame(
            columns=[
                "file_extension",
                "changed_files",
                "total_changes",
                "total_additions",
                "total_deletions",
            ]
        )

    summary = (
        commit_files.groupby("file_extension")
        .agg(
            changed_files=("filename", "count"),
            total_changes=("changes", "sum"),
            total_additions=("additions", "sum"),
            total_deletions=("deletions", "sum"),
        )
        .reset_index()
        .sort_values("changed_files", ascending=False)
    )

    return summary


def main():
    issues = read_csv_if_exists(BUG_ISSUES_PROCESSED_CSV)
    closure_events = read_csv_if_exists(CLOSURE_EVENTS_CSV)
    commits = read_csv_if_exists(BUGFIX_COMMITS_CSV)
    commit_files = read_csv_if_exists(BUGFIX_COMMIT_FILES_CSV)

    if issues.empty:
        print("Processed bug issue data is required. Run analysis/analyze_fix_time.py first.")
        return

    if closure_events.empty:
        print("Closure event data is required. Run data_collection/collect_issue_events.py first.")
        return

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    issue_commit_links = build_issue_commit_links(issues, closure_events, commits)
    project_summary_v2 = build_project_summary_v2(issue_commit_links)
    file_extension_summary = build_file_extension_summary(commit_files)

    issue_commit_links.to_csv(
        BUG_ISSUE_COMMIT_LINKS_CSV, index=False, encoding="utf-8"
    )

    project_summary_v2.to_csv(
        PROJECT_SUMMARY_V2_CSV, index=False, encoding="utf-8"
    )

    file_extension_summary.to_csv(
        FILE_EXTENSION_SUMMARY_CSV, index=False, encoding="utf-8"
    )

    print(f"Bug issue commit links saved to: {BUG_ISSUE_COMMIT_LINKS_CSV}")
    print(f"Project summary V2 saved to: {PROJECT_SUMMARY_V2_CSV}")
    print(f"File extension summary saved to: {FILE_EXTENSION_SUMMARY_CSV}")


if __name__ == "__main__":
    main()
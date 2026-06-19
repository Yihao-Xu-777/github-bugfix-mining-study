from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

TABLES_DIR = PROJECT_ROOT / "results" / "tables"
FIGURES_DIR = PROJECT_ROOT / "results" / "figures"

PROJECT_SUMMARY_CSV = TABLES_DIR / "project_summary.csv"
KEYWORD_SUMMARY_CSV = TABLES_DIR / "keyword_summary.csv"

PROJECT_SUMMARY_V2_CSV = TABLES_DIR / "project_summary_v2.csv"
FILE_EXTENSION_SUMMARY_CSV = TABLES_DIR / "file_extension_summary.csv"


def save_bar_chart(series, title, xlabel, ylabel, output_path, rotation=25):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 6))
    series.plot(kind="bar", ax=ax)

    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    plt.xticks(rotation=rotation, ha="right")
    plt.tight_layout()

    fig.savefig(output_path, dpi=200)
    plt.close(fig)


def generate_v1_figures():
    if PROJECT_SUMMARY_CSV.exists():
        project_summary = pd.read_csv(PROJECT_SUMMARY_CSV)

        if not project_summary.empty:
            bug_issue_series = project_summary.set_index("project")["bug_issues"]

            save_bar_chart(
                bug_issue_series,
                "Closed Bug Issues by Project",
                "Project",
                "Number of Closed Bug Issues",
                FIGURES_DIR / "bug_issue_count_by_project.png",
            )

            avg_fix_time_series = project_summary.set_index("project")[
                "avg_fix_time_days"
            ]

            save_bar_chart(
                avg_fix_time_series,
                "Average Bug Fix Time by Project",
                "Project",
                "Average Fix Time (Days)",
                FIGURES_DIR / "avg_fix_time_by_project.png",
            )

    if KEYWORD_SUMMARY_CSV.exists():
        keyword_summary = pd.read_csv(KEYWORD_SUMMARY_CSV)

        if not keyword_summary.empty:
            top_keywords = keyword_summary.head(15)
            keyword_series = top_keywords.set_index("keyword")["count"]

            save_bar_chart(
                keyword_series,
                "Top Keywords in Bug Issue Titles",
                "Keyword",
                "Frequency",
                FIGURES_DIR / "top_bug_keywords.png",
            )


def generate_commit_link_rate_figure(project_summary_v2):
    series = project_summary_v2.set_index("project")["commit_link_rate"]

    save_bar_chart(
        series,
        "Bug Issue to Commit Link Rate by Project",
        "Project",
        "Commit Link Rate (%)",
        FIGURES_DIR / "commit_link_rate_by_project.png",
    )


def generate_avg_changed_files_figure(project_summary_v2):
    series = project_summary_v2.set_index("project")["avg_changed_files"].fillna(0)

    save_bar_chart(
        series,
        "Average Changed Files per Linked Bug-Fix Commit",
        "Project",
        "Average Changed Files",
        FIGURES_DIR / "avg_changed_files_by_project.png",
    )


def generate_file_extension_figure(file_extension_summary):
    top_extensions = file_extension_summary.head(10)

    if top_extensions.empty:
        return

    series = top_extensions.set_index("file_extension")["changed_files"]

    save_bar_chart(
        series,
        "Most Common File Extensions in Bug-Fix Commits",
        "File Extension",
        "Changed Files",
        FIGURES_DIR / "file_extension_distribution.png",
    )


def generate_v2_figures():
    if PROJECT_SUMMARY_V2_CSV.exists():
        project_summary_v2 = pd.read_csv(PROJECT_SUMMARY_V2_CSV)

        if not project_summary_v2.empty:
            generate_commit_link_rate_figure(project_summary_v2)
            generate_avg_changed_files_figure(project_summary_v2)

    if FILE_EXTENSION_SUMMARY_CSV.exists():
        file_extension_summary = pd.read_csv(FILE_EXTENSION_SUMMARY_CSV)

        if not file_extension_summary.empty:
            generate_file_extension_figure(file_extension_summary)


def main():
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    generate_v1_figures()
    generate_v2_figures()

    print(f"Figures saved to: {FIGURES_DIR}")


if __name__ == "__main__":
    main()
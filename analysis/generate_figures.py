from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

PROJECT_SUMMARY_CSV = PROJECT_ROOT / "results" / "tables" / "project_summary.csv"
KEYWORD_SUMMARY_CSV = PROJECT_ROOT / "results" / "tables" / "keyword_summary.csv"

FIGURES_DIR = PROJECT_ROOT / "results" / "figures"


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


def generate_bug_issue_count_figure(project_summary):
    series = project_summary.set_index("project")["bug_issues"]

    save_bar_chart(
        series,
        "Closed Bug Issues by Project",
        "Project",
        "Number of Closed Bug Issues",
        FIGURES_DIR / "bug_issue_count_by_project.png",
    )


def generate_avg_fix_time_figure(project_summary):
    series = project_summary.set_index("project")["avg_fix_time_days"]

    save_bar_chart(
        series,
        "Average Bug Fix Time by Project",
        "Project",
        "Average Fix Time (Days)",
        FIGURES_DIR / "avg_fix_time_by_project.png",
    )


def generate_keyword_figure(keyword_summary):
    top_keywords = keyword_summary.head(15)
    series = top_keywords.set_index("keyword")["count"]

    save_bar_chart(
        series,
        "Top Keywords in Bug Issue Titles",
        "Keyword",
        "Frequency",
        FIGURES_DIR / "top_bug_keywords.png",
    )


def main():
    if not PROJECT_SUMMARY_CSV.exists():
        print("project_summary.csv not found. Run analysis/analyze_fix_time.py first.")
        return

    if not KEYWORD_SUMMARY_CSV.exists():
        print("keyword_summary.csv not found. Run analysis/analyze_fix_time.py first.")
        return

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    project_summary = pd.read_csv(PROJECT_SUMMARY_CSV)
    keyword_summary = pd.read_csv(KEYWORD_SUMMARY_CSV)

    generate_bug_issue_count_figure(project_summary)
    generate_avg_fix_time_figure(project_summary)
    generate_keyword_figure(keyword_summary)

    print(f"Figures saved to: {FIGURES_DIR}")


if __name__ == "__main__":
    main()
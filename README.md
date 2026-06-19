# GitHub Bug-Fix Mining Study

An empirical study of bug-fixing patterns in open-source Python repositories.

## Background

Bug fixing is a central activity in software maintenance. Open-source repositories on GitHub provide useful data for studying how bugs are reported, discussed, and resolved.

This project mines GitHub issue data from selected Python repositories and analyzes bug issue volume, closing time, and common keywords in bug issue titles.

## Research Questions

- RQ1: How many closed bug issues are collected from each project?
- RQ2: How long does it usually take to close bug issues?
- RQ3: What keywords commonly appear in bug issue titles?

## Project Structure

```text
github-bugfix-mining-study/
├── config/
│   └── repos.csv
├── data_collection/
│   └── collect_bug_issues.py
├── analysis/
│   ├── analyze_fix_time.py
│   └── generate_figures.py
├── dataset/
│   ├── raw/
│   │   └── bug_issues_raw.csv
│   └── processed/
│       ├── bug_issues_processed.csv
│       ├── project_summary.csv
│       └── keyword_summary.csv
├── results/
│   ├── tables/
│   │   ├── project_summary.csv
│   │   └── keyword_summary.csv
│   └── figures/
│       ├── bug_issue_count_by_project.png
│       ├── avg_fix_time_by_project.png
│       └── top_bug_keywords.png
├── docs/
│   └── mini_report.md
├── README.md
├── requirements.txt
└── .env.example
```

## Dataset

The V1 dataset includes closed issues labeled as `bug` from three Python repositories:

| Repository | Language |
|---|---|
| pallets/flask | Python |
| psf/requests | Python |
| scrapy/scrapy | Python |

Pull requests are filtered out from the issue data.

## Installation

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file based on `.env.example`:

```env
GITHUB_TOKEN=your_github_token_here
```

## How to Run

Collect closed bug issues:

```bash
python data_collection/collect_bug_issues.py
```

Analyze bug issue closing time and keywords:

```bash
python analysis/analyze_fix_time.py
```

Generate figures:

```bash
python analysis/generate_figures.py
```

## Results

The generated tables are saved in:

```text
results/tables/project_summary.csv
results/tables/keyword_summary.csv
```

The generated figures are saved in:

```text
results/figures/bug_issue_count_by_project.png
results/figures/avg_fix_time_by_project.png
results/figures/top_bug_keywords.png
```

### Closed Bug Issues by Project

![Closed Bug Issues by Project](results/figures/bug_issue_count_by_project.png)

### Average Bug Fix Time by Project

![Average Bug Fix Time by Project](results/figures/avg_fix_time_by_project.png)

### Top Keywords in Bug Issue Titles

![Top Bug Keywords](results/figures/top_bug_keywords.png)

## Current Limitations

- Only three repositories are analyzed in V1.
- Only issues labeled as `bug` are collected.
- Issue closing time may not exactly represent actual bug-fixing time.
- Different repositories may use labels differently.
- Pull requests are excluded from the issue dataset.
- The keyword analysis is simple and does not use advanced NLP.

## Future Work

- Expand the dataset to more repositories
- Collect related commits and pull requests
- Analyze changed files in bug-fixing commits
- Compare bug issues with feature issues
- Add CI status analysis
- Use NLP methods for issue title and description analysis

## Mini Report

A short project report is available in:

```text
docs/mini_report.md
```

## License

This project is licensed under the MIT License.
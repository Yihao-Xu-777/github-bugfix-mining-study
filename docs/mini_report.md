# Mini Report: GitHub Bug-Fix Mining Study

## 1. Introduction

Bug fixing is an important activity in software maintenance. Open-source repositories provide useful data for studying how bugs are reported, discussed, and fixed.

This project conducts a small empirical study of closed bug issues in selected open-source Python repositories.

## 2. Objective

The objective of this project is to mine GitHub issue data and analyze bug-fixing patterns across open-source Python projects.

## 3. Research Questions

RQ1: How many closed bug issues are collected from each project?

RQ2: How long does it usually take to close bug issues?

RQ3: What keywords commonly appear in bug issue titles?

## 4. Dataset

The V1 dataset includes closed issues labeled as `bug` from three Python repositories:

- pallets/flask
- psf/requests
- scrapy/scrapy

Pull requests are filtered out from the issue data.

## 5. Methodology

The project uses the GitHub REST API to collect closed issues with the `bug` label. The collected data includes issue title, creation time, closing time, number of comments, labels, and issue URL.

The fix time is calculated as the time difference between `created_at` and `closed_at`.

The analysis generates project-level summaries and keyword frequency statistics from bug issue titles.

## 6. Results

The generated result tables are stored in:

- `results/tables/project_summary.csv`
- `results/tables/keyword_summary.csv`

The generated figures are stored in:

- `results/figures/bug_issue_count_by_project.png`
- `results/figures/avg_fix_time_by_project.png`
- `results/figures/top_bug_keywords.png`

## 7. Discussion

The project-level summary helps compare bug issue volume and average closing time across repositories. The keyword analysis provides a simple view of common terms in bug reports.

These results should be interpreted carefully because issue closing time is only an approximation of bug-fixing time. Some issues may be closed without code changes, while some bugs may be fixed before the issue is closed.

## 8. Threats to Validity

Several threats may affect the validity of this study:

- Only three repositories are analyzed in V1.
- Only issues labeled as `bug` are collected.
- Issue closing time may not exactly represent actual bug-fixing time.
- Labeling practices differ across repositories.
- Pull requests are excluded from the issue dataset.
- Keyword analysis is simple and does not capture deeper semantic meaning.

## 9. Future Work

Future work includes:

- Expanding the dataset to more repositories
- Collecting related commits and pull requests
- Analyzing files changed in bug-fixing commits
- Comparing bug issues with feature issues
- Using NLP methods for more advanced text analysis

## 10. Conclusion

This project demonstrates a small but reproducible Mining Software Repositories workflow using GitHub issue data, data cleaning, fix-time analysis, keyword analysis, CSV summaries, and visualizations.
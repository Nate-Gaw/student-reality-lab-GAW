1. College Scorecard – Full Earnings & Debt Data (U.S. Department of Education)

Description: This is the official U.S. College Scorecard dataset that includes institution-level data on completion, earnings, debts, and more. You can filter it to get computer science bachelor’s vs. master’s outcomes.

CSV data files:

college-scorecard-institution.csv.gz – contains salaries and student debt results by institution.

Link: https://collegescorecard.ed.gov/data/
 (scroll to Data Downloads)

You’ll need to filter these CSVs for:

CS bachelor’s degree programs

CS master’s degree programs
(using the PREDDEG and CIP code for CS)

2. “Degrees That Pay Back” Dataset (GitHub CSV)

Description: A public dataset that lists majors, median salaries, and earnings outcomes including computer science.
It’s not specific to master’s vs bachelor’s, but you can extract and compare CS bachelor’s salary (and approximate earnings).

Download CSV:
https://github.com/YujiShen/anly-500-project/blob/master/degrees-that-pay-back.csv

This CSV includes data like:

Major	Median Salary
Computer Science	(salary number)

You can pair this with debt numbers from another source.

3. Education Data Initiative Student Debt by Major (May Need Manual CSV)

Description: A comprehensive list of median student debt by major, including both bachelor’s and master’s levels.

Example relevant rows:

Bachelor’s CS median debt ≈ $23,184 (for Computer Science)

Master’s CS median debt ≈ $36,729 (for Computer Science)

Although this page doesn’t provide a direct ready-made CSV, you can turn it into one easily by scraping the major columns.

Raw source (convert to CSV for your project):
https://educationdata.org/student-loan-debt-by-major
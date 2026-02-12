#Is Graduate School Financially Worth It for Computer Science Majors?


Essential Question
Does earning a master’s degree in computer science significantly improve long-term financial outcomes compared to stopping at a bachelor’s degree?

Claim (Hypothesis)
CS graduates with a master’s degree earn enough additional income over time to justify the extra student loan debt.

Audience
Computer science students, prospective graduate students, academic advisors, and parents.

STAR Draft

Situation
- Many CS students consider graduate school to increase job prospects.
- Graduate programs are expensive and often require taking on debt.
- Students lack clear information on whether higher degrees pay off financially.
- Rising interest rates increase the cost of student loans.

Task
- Compare salaries of CS bachelor’s and master’s degree holders.
- Compare typical graduate school debt.
- Show how long it takes to recover the cost of graduate school.

Action
- Build visualizations showing:
  - Average salary by degree level
  - Average graduate debt
  - Payback period over time
- Create an interactive dashboard to compare degree paths.

Result
- Expect master’s degree holders to earn more over time.
- Will report: Break-even Years (years needed to recover grad school cost).

Dataset & Provenance

| Source | Link | Date Retrieved | License |
|--------|------|---------------|---------|
| Bureau of Labor Statistics | https://www.bls.gov/emp/tables/unemployment-earnings-education.htm | Jan 2026 | Public Domain |
| Average Student Loan Debt By Degree (2026) | https://www.badcredit.org/studies/average-student-loan-debt-by-degree/ | June 2026 | Educational Use |
| Average Student Loan Amounts by Debt Type
 | https://www.nerdwallet.com/student-loans/learn/average-student-loan-debt-graduate-school| May 2023 | Public Domain |
| New Data on Field of Degree | https://www.census.gov/newsroom/press-releases/2023/field-of-degree-earnings.html | Oct 2023 | Public Domain |


Data Dictionary

| Column Name | Meaning | Units |
|-------------|---------|-------|
| year | Year of data | Year |
| degree_level | Bachelor or Master | Text |
| avg_salary | Average annual salary | USD/year |
| avg_grad_debt | Average graduate school debt | USD |
| salary_increase | Salary difference vs bachelor | USD/year |
| break_even_years | Years to repay grad cost | Years |

Data Viability Audit

Missing Values / Weird Fields
- Some years missing salary data for master’s graduates.
- NACE survey data is self-reported.
- Graduate debt varies widely by institution.
- Salary data is reported in nominal dollars.

Cleaning Plan
- Remove rows with missing salary or debt values.
- Convert all monetary values to numeric format.
- Standardize degree labels (Bachelor, Master).
- Adjust values to constant 2026 dollars using CPI.
- Remove duplicate year entries.
- Calculate salary increase and break-even years.

What This Dataset Cannot Prove (Limits/Bias)
- Does not include:
  - Job satisfaction
  - Career advancement speed
  - Employer-paid tuition
  - Stock compensation
- Uses national averages.
- Does not reflect regional tech markets.
- Does not account for unemployment risk.
- Does not measure networking benefits.


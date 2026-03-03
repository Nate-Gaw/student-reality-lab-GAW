const SOURCES = [
  {
    text: 'Education Data: Student Loan Debt by Major',
    url: 'https://educationdata.org/student-loan-debt-by-major'
  },
  {
    text: 'GitHub: Degrees That Pay Back (ANLY 500)',
    url: 'https://github.com/YujiShen/anly-500-project/blob/master/degrees-that-pay-back.csv'
  },
  {
    text: 'College Scorecard: Official U.S. Education Department Data',
    url: 'https://collegescorecard.ed.gov/data/'
  }
];

export function populateSourcesList(listElement) {
  if (!listElement) return;

  listElement.innerHTML = SOURCES
    .map((source) => `<li><a href="${source.url}" target="_blank" rel="noopener noreferrer">${source.text}</a></li>`)
    .join('');
}

"""
API-based data sources for university information.
Examples include government education databases and international registries.
"""
import httpx
import os
from typing import List, Dict, Optional
from datetime import datetime


class APIDataSource:
    """Base class for API data sources."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.session = httpx.Client(timeout=30.0)
    
    async def fetch_data(self, endpoint: str, params: Dict = None) -> Dict:
        """Fetch data from API endpoint."""
        raise NotImplementedError
    
    def normalize_response(self, raw_data: Dict) -> List[Dict]:
        """Convert API response to normalized schema."""
        raise NotImplementedError


class CollegeScorecard(APIDataSource):
    """
    US Department of Education College Scorecard API.
    Get a free API key at https://api.data.gov/signup/ and set
    COLLEGE_SCORECARD_API_KEY in your .env file.
    Falls back to DEMO_KEY (heavily rate-limited) if no key is set.
    """

    BASE_URL = "https://api.data.gov/ed/collegescorecard/v1/schools"
    FIELDS = (
        "school.name,school.city,school.state,school.school_url,"
        "latest.cost.tuition.in_state,latest.cost.tuition.out_of_state,"
        "latest.cost.roomboard.oncampus,latest.cost.roomboard.offcampus,"
        "latest.cost.attendance.academic_year,"
        "latest.admissions.admission_rate.overall,"
        "latest.completion.completion_rate_4yr_150nt,"
        "latest.student.size,latest.student.grad_students,"
        "latest.aid.students_with_pell_grant,"
        "school.institutional_characteristics.level"
    )

    def __init__(self):
        super().__init__()
        self.api_key = os.getenv("COLLEGE_SCORECARD_API_KEY", "DEMO_KEY")
        if self.api_key == "DEMO_KEY":
            print("[CollegeScorecard] WARNING: Using DEMO_KEY – heavily rate-limited. "
                  "Get a free key at https://api.data.gov/signup/ and set COLLEGE_SCORECARD_API_KEY in .env")

    def _get(self, params: dict) -> dict:
        params["api_key"] = self.api_key
        params["_fields"] = self.FIELDS
        response = self.session.get(self.BASE_URL, params=params)
        if response.status_code == 429:
            raise RuntimeError(
                "College Scorecard API rate limited. "
                "Get a free key at https://api.data.gov/signup/ and set COLLEGE_SCORECARD_API_KEY in .env"
            )
        if response.status_code >= 400:
            raise RuntimeError(f"College Scorecard API error: HTTP {response.status_code}")
        return response.json() if response.status_code == 200 else {}

    def search_by_name(self, name: str, limit: int = 5) -> List[Dict]:
        """Direct targeted search for a university by name."""
        data = self._get({"school.name": name, "_per_page": limit, "_page": 0})
        return self.normalize_response(data)

    def fetch_universities(self, limit: int = 100, page: int = 0, search_name: Optional[str] = None) -> List[Dict]:
        """Fetch US universities from College Scorecard."""
        params: dict = {"_page": page, "_per_page": limit}
        if search_name:
            params["school.name"] = search_name
        data = self._get(params)
        return self.normalize_response(data)

    def normalize_response(self, raw_data: Dict) -> List[Dict]:
        """Convert College Scorecard data to our schema."""
        normalized = []

        for school in raw_data.get("results", []):
            try:
                # College Scorecard returns flat dot-notation keys, e.g. "school.name",
                # "latest.cost.tuition.out_of_state" — NOT nested dicts.
                def _f(key):
                    return school.get(key)

                name = _f("school.name")
                if not name:
                    continue

                in_state = _f("latest.cost.tuition.in_state")
                out_of_state = _f("latest.cost.tuition.out_of_state")
                housing = _f("latest.cost.roomboard.oncampus") or _f("latest.cost.roomboard.offcampus")
                total_attendance = _f("latest.cost.attendance.academic_year")
                grad_students = _f("latest.student.grad_students")

                shared = {
                    "university_name": name,
                    "country": "United States",
                    "city": _f("school.city"),
                    "currency": "USD",
                    "domestic_tuition": in_state,
                    # Out-of-state tuition is the closest proxy for non-resident / international cost
                    "international_tuition": out_of_state,
                    "estimated_housing_cost": housing,
                    "estimated_total_annual_cost": total_attendance,
                    "acceptance_rate": _f("latest.admissions.admission_rate.overall"),
                    "graduation_rate": _f("latest.completion.completion_rate_4yr_150nt"),
                    "official_website": _f("school.school_url"),
                    "enrollment_count": _f("latest.student.size"),
                    "has_financial_aid": bool(_f("latest.aid.students_with_pell_grant")),
                    "data_source": "US College Scorecard API",
                    "last_updated": datetime.now(),
                }

                # Bachelor record
                bachelor = {**shared, "degree_level": "bachelor"}
                normalized.append(bachelor)

                # Master record – grad_students flag signals graduate programs exist
                if grad_students:
                    master = {**shared, "degree_level": "master"}
                    normalized.append(master)

            except Exception as e:
                print(f"Error normalizing school: {e}")
                continue

        return normalized


class TimesHigherEducation(APIDataSource):
    """
    Times Higher Education API (requires subscription/key).
    Placeholder implementation for international universities.
    """
    
    BASE_URL = "https://www.timeshighereducation.com/api/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
    
    def fetch_universities(self, country: Optional[str] = None) -> List[Dict]:
        """Fetch international university rankings and data."""
        # TODO: Implement when API access is available
        print("Times Higher Education API requires subscription")
        return []


class OpenDataPortal:
    """
    Aggregator for open government data portals worldwide.
    """
    
    PORTALS = {
        "UK": "https://data.gov.uk/",
        "Canada": "https://open.canada.ca/",
        "Australia": "https://data.gov.au/",
        "EU": "https://data.europa.eu/",
    }
    
    @staticmethod
    def get_available_portals() -> List[str]:
        """Return list of available data portals."""
        return list(OpenDataPortal.PORTALS.keys())
    
    @staticmethod
    def fetch_from_portal(country: str) -> List[Dict]:
        """Fetch university data from government portal."""
        # Placeholder for country-specific implementations
        print(f"Portal integration for {country} not yet implemented")
        return []

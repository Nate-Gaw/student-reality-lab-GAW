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
    Free, no key required for basic access.
    """
    
    BASE_URL = "https://api.data.gov/ed/collegescorecard/v1/schools"
    
    def __init__(self):
        super().__init__()
    
    def fetch_universities(self, limit: int = 100, page: int = 0, search_name: Optional[str] = None) -> List[Dict]:
        """Fetch US universities from College Scorecard."""
        params = {
            "api_key": "DEMO_KEY",
            "_page": page,
            "_per_page": limit,
            "_fields": "school.name,school.city,school.state,latest.cost.tuition.in_state,latest.cost.tuition.out_of_state,latest.cost.roomboard.oncampus,latest.admissions.admission_rate.overall,latest.completion.completion_rate_4yr_150nt,school.school_url"
        }

        if search_name:
            params["school.name"] = search_name
        
        response = self.session.get(self.BASE_URL, params=params)

        if response.status_code == 429:
            raise RuntimeError("College Scorecard API rate limited (HTTP 429). Try again later or use a dedicated API key.")
        if response.status_code >= 400:
            raise RuntimeError(f"College Scorecard API error: HTTP {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            return self.normalize_response(data)
        return []
    
    def normalize_response(self, raw_data: Dict) -> List[Dict]:
        """Convert College Scorecard data to our schema."""
        normalized = []
        
        for school in raw_data.get("results", []):
            try:
                school_data = school.get("school", {})
                latest = school.get("latest", {})
                cost = latest.get("cost", {})
                tuition = cost.get("tuition", {})
                admissions = latest.get("admissions", {})
                completion = latest.get("completion", {})
                
                # Bachelor's program
                bachelor_record = {
                    "university_name": school_data.get("name"),
                    "country": "United States",
                    "city": school_data.get("city"),
                    "degree_level": "bachelor",
                    "currency": "USD",
                    "domestic_tuition": tuition.get("in_state"),
                    "international_tuition": tuition.get("out_of_state"),
                    "estimated_housing_cost": cost.get("roomboard", {}).get("oncampus"),
                    "acceptance_rate": admissions.get("admission_rate", {}).get("overall"),
                    "graduation_rate": completion.get("completion_rate_4yr_150nt"),
                    "official_website": school_data.get("school_url"),
                    "data_source": "US College Scorecard API",
                    "last_updated": datetime.now()
                }
                
                if bachelor_record["university_name"]:
                    normalized.append(bachelor_record)
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

"""
Query handler for processing user requests and coordinating data acquisition.
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import statistics
import re
from difflib import SequenceMatcher

from data.storage.database import DatabaseManager
from data.acquisition.api_sources import CollegeScorecard
from data.acquisition.web_scraper import UniversityWebScraper


class QueryHandler:
    """Handle queries and coordinate data acquisition."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.api_sources = {
            "us_college_scorecard": CollegeScorecard()
        }
        self.web_scraper = UniversityWebScraper()
        self.cache_ttl_days = 90  # Refresh data after 90 days
        self.last_acquire_error: Optional[str] = None
    
    def get_university_cost(
        self,
        university_name: str,
        degree_level: str,
        student_type: str = "international"
    ) -> Dict:
        """
        Get cost breakdown for a university.
        Fetches from database or triggers data acquisition if missing/stale.
        """
        # Try exact match first
        results = self.db.get_university_by_name(university_name, degree_level)
        
        if results and self._is_data_fresh(results[0]):
            cost_data = results[0]
            return self._format_cost_response(cost_data, student_type)
        
        # Try fuzzy search across all universities in database if exact match fails
        if not results:
            normalized_query = self._normalize_name(university_name)
            all_candidates = self.db.search_universities("", limit=500)
            
            best_match = None
            best_score = 0.0
            
            for candidate in all_candidates:
                if candidate.get("degree_level") != degree_level:
                    continue
                    
                candidate_name = candidate.get("university_name", "")
                normalized_candidate = self._normalize_name(candidate_name)
                score = self._score_name_match(normalized_query, normalized_candidate)
                
                if score > best_score:
                    best_score = score
                    best_match = candidate
            
            # Use fuzzy match if confidence is high enough
            if best_match and best_score >= 0.6 and self._is_data_fresh(best_match):
                return self._format_cost_response(best_match, student_type)
        
        # If requested degree is unavailable, try any available degree for this school
        if not results:
            any_degree_results = self.db.get_university_by_name(university_name)
            if any_degree_results and self._is_data_fresh(any_degree_results[0]):
                cost_data = any_degree_results[0]
                return self._format_cost_response(cost_data, student_type)

        # Data missing or stale - trigger acquisition
        print(f"Acquiring fresh data for {university_name}...")
        self.last_acquire_error = None
        new_data = self._acquire_university_data(university_name, degree_level)
        
        if new_data:
            # Store in database
            self.db.add_university(new_data)
            return self._format_cost_response(new_data, student_type)
        
        failure_payload = {
            "error": f"Could not find cost data for {university_name}",
            "suggestion": "Try searching by exact university name or check available data sources"
        }
        if self.last_acquire_error:
            failure_payload["source_detail"] = self.last_acquire_error
        return failure_payload
    
    def get_universities_by_country(
        self,
        country: str,
        degree_level: Optional[str] = None,
        limit: int = 50
    ) -> Dict:
        """Get all universities in a country."""
        results = self.db.get_universities_by_country(country, degree_level)
        
        if not results:
            # Try to acquire data for this country
            print(f"No cached data for {country}. Checking data sources...")
            self._acquire_country_data(country)
            results = self.db.get_universities_by_country(country, degree_level)
        
        return {
            "country": country,
            "degree_level": degree_level or "all",
            "count": len(results),
            "universities": results[:limit]
        }
    
    def compare_university_costs(
        self,
        university_names: List[str],
        degree_level: str,
        student_type: str = "international"
    ) -> Dict:
        """Compare costs across multiple universities."""
        comparison = {
            "degree_level": degree_level,
            "student_type": student_type,
            "universities": []
        }
        
        for name in university_names:
            cost_data = self.get_university_cost(name, degree_level, student_type)
            if "error" not in cost_data:
                comparison["universities"].append(cost_data)
        
        # Add ranking by total cost
        if comparison["universities"]:
            sorted_unis = sorted(
                comparison["universities"],
                key=lambda x: x.get("estimated_total_annual_cost", float('inf'))
            )
            
            for i, uni in enumerate(sorted_unis):
                uni["cost_rank"] = i + 1
            
            comparison["universities"] = sorted_unis
            comparison["lowest_cost"] = sorted_unis[0]["university_name"]
            comparison["highest_cost"] = sorted_unis[-1]["university_name"]
        
        return comparison
    
    def search_universities(self, search_term: str, limit: int = 20) -> Dict:
        """Search universities by name, location, or program."""
        results = self.db.search_universities(search_term, limit)
        
        return {
            "search_term": search_term,
            "count": len(results),
            "results": results
        }
    
    def get_cost_statistics(
        self,
        country: Optional[str] = None,
        degree_level: Optional[str] = None
    ) -> Dict:
        """Get statistical analysis of costs."""
        # Get relevant records
        if country:
            records = self.db.get_universities_by_country(country, degree_level)
        else:
            records = self.db.search_universities("", limit=1000)
        
        if not records:
            return {"error": "No data available for analysis"}
        
        # Calculate statistics
        tuitions = [r.get("international_tuition") for r in records if r.get("international_tuition")]
        total_costs = [r.get("estimated_total_annual_cost") for r in records if r.get("estimated_total_annual_cost")]
        
        stats = {
            "sample_size": len(records),
            "country": country or "global",
            "degree_level": degree_level or "all"
        }
        
        if tuitions:
            stats["tuition_statistics"] = {
                "mean": round(statistics.mean(tuitions), 2),
                "median": round(statistics.median(tuitions), 2),
                "min": round(min(tuitions), 2),
                "max": round(max(tuitions), 2),
                "std_dev": round(statistics.stdev(tuitions), 2) if len(tuitions) > 1 else 0
            }
        
        if total_costs:
            stats["total_cost_statistics"] = {
                "mean": round(statistics.mean(total_costs), 2),
                "median": round(statistics.median(total_costs), 2),
                "min": round(min(total_costs), 2),
                "max": round(max(total_costs), 2)
            }
        
        return stats
    
    def _is_data_fresh(self, record: Dict) -> bool:
        """Check if data is within cache TTL."""
        if not record.get("last_updated"):
            return False
        
        last_updated = datetime.fromisoformat(record["last_updated"])
        age = datetime.now() - last_updated
        return age.days < self.cache_ttl_days
    
    def _acquire_university_data(self, university_name: str, degree_level: str) -> Optional[Dict]:
        """
        Attempt to acquire data from available sources.
        Priority: APIs > Datasets > Web Scraping
        """
        # Try API sources first (most reliable). For now this source is US-focused,
        # but we still attempt it for natural-language names like "Rutgers New Brunswick".
        try:
            best_match = None
            best_score = 0.0
            normalized_query = self._normalize_name(university_name)

            seed_terms = [university_name]
            seed_terms.extend([token for token in normalized_query.split() if len(token) >= 4][:3])

            # Try filtered requests first to increase recall for natural names.
            for term in seed_terms:
                filtered = self.api_sources["us_college_scorecard"].fetch_universities(
                    limit=100,
                    page=0,
                    search_name=term,
                )
                for uni in filtered:
                    candidate = uni.get("university_name", "")
                    if not candidate:
                        continue
                    normalized_candidate = self._normalize_name(candidate)
                    score = self._score_name_match(normalized_query, normalized_candidate)
                    if score > best_score:
                        best_score = score
                        best_match = uni
                if best_score >= 0.7:
                    break

            # Search across multiple pages because first page is not guaranteed
            # to include the requested institution (e.g., Rutgers campuses).
            for page in range(0, 20):
                data = self.api_sources["us_college_scorecard"].fetch_universities(limit=100, page=page)
                if not data:
                    break

                for uni in data:
                    candidate = uni.get("university_name", "")
                    if not candidate:
                        continue
                    normalized_candidate = self._normalize_name(candidate)

                    if normalized_query and normalized_query in normalized_candidate:
                        score = 1.0
                    else:
                        score = self._score_name_match(normalized_query, normalized_candidate)

                    if score > best_score:
                        best_score = score
                        best_match = uni

                # Early exit for strong match.
                if best_score >= 0.78:
                    break

            if best_match and best_score >= 0.52:
                best_match["degree_level"] = degree_level
                costs = [
                    best_match.get("international_tuition", 0),
                    best_match.get("estimated_housing_cost", 0),
                    best_match.get("estimated_living_cost", 0),
                    best_match.get("student_fees", 0),
                    best_match.get("books_supplies", 0),
                    best_match.get("health_insurance", 0),
                ]
                best_match["estimated_total_annual_cost"] = sum(c for c in costs if c)
                return best_match
        except Exception as e:
            self.last_acquire_error = str(e)
            print(f"API fetch failed: {e}")
        
        # TODO: Try web scraping as fallback
        # This would require knowing the university's website
        return None
    
    def _acquire_country_data(self, country: str):
        """Acquire data for all universities in a country."""
        if country.lower() in ["united states", "usa", "us"]:
            try:
                print("Fetching US university data from College Scorecard...")
                data = self.api_sources["us_college_scorecard"].fetch_universities(limit=500)
                
                # Batch insert
                for uni_data in data:
                    try:
                        self.db.add_university(uni_data)
                    except Exception as e:
                        print(f"Error adding university: {e}")
                
                print(f"Added {len(data)} universities to database")
            except Exception as e:
                print(f"Error acquiring country data: {e}")

    @staticmethod
    def _normalize_name(name: str) -> str:
        text = re.sub(r"[^a-z0-9\s]", " ", (name or "").lower())
        text = re.sub(r"\s+", " ", text).strip()
        # Normalize common abbreviations and campus naming differences.
        text = text.replace("univ ", "university ")
        text = text.replace("u ", "university ")
        text = text.replace("new brunswick", "new brunswick")
        return text

    @staticmethod
    def _score_name_match(query: str, candidate: str) -> float:
        if not query or not candidate:
            return 0.0
        base = SequenceMatcher(None, query, candidate).ratio()
        query_tokens = set(query.split())
        candidate_tokens = set(candidate.split())
        overlap = len(query_tokens & candidate_tokens) / max(len(query_tokens), 1)
        return max(base, overlap)
    
    @staticmethod
    def _format_cost_response(cost_data: Dict, student_type: str) -> Dict:
        """Format cost data for response."""
        tuition_key = "international_tuition" if student_type == "international" else "domestic_tuition"
        tuition = cost_data.get(tuition_key) or cost_data.get("international_tuition")
        
        response = {
            "university_name": cost_data.get("university_name"),
            "country": cost_data.get("country"),
            "city": cost_data.get("city"),
            "degree_level": cost_data.get("degree_level"),
            "currency": cost_data.get("currency", "USD"),
            "costs": {
                "tuition": tuition,
                "application_fee": cost_data.get("application_fee"),
                "housing": cost_data.get("estimated_housing_cost"),
                "living_expenses": cost_data.get("estimated_living_cost"),
                "student_fees": cost_data.get("student_fees"),
                "books_supplies": cost_data.get("books_supplies"),
                "health_insurance": cost_data.get("health_insurance")
            },
            "estimated_total_annual_cost": cost_data.get("estimated_total_annual_cost"),
            "financial_aid": {
                "has_scholarships": cost_data.get("has_scholarships"),
                "has_financial_aid": cost_data.get("has_financial_aid"),
                "average_scholarship": cost_data.get("average_scholarship_amount")
            },
            "statistics": {
                "acceptance_rate": cost_data.get("acceptance_rate"),
                "graduation_rate": cost_data.get("graduation_rate"),
                "enrollment": cost_data.get("enrollment_count")
            },
            "official_website": cost_data.get("official_website"),
            "data_quality": cost_data.get("data_quality_score", 1.0),
            "last_updated": cost_data.get("last_updated")
        }
        
        return response

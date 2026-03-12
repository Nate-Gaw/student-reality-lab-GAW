"""
Web scraping module for extracting university cost data from official websites.
"""
import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional, List
import re
import time
import os
from urllib.parse import urljoin


class UniversityWebScraper:
    """Base class for scraping university websites."""
    
    def __init__(self, rate_limit_delay: float = 2.0):
        self.rate_limit_delay = rate_limit_delay
        self.headers = {
            "User-Agent": "UniversityCostMCP/1.0 (Educational Research Bot)"
        }
        self.session = requests.Session()
    
    def fetch_page(self, url: str) -> Optional[str]:
        """Fetch webpage content with rate limiting."""
        try:
            time.sleep(self.rate_limit_delay)
            response = self.session.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def find_tuition_page(self, university_website: str) -> Optional[str]:
        """Attempt to find the tuition/costs page from main website."""
        html = self.fetch_page(university_website)
        if not html:
            return None
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Look for links containing cost/tuition keywords
        keywords = ['tuition', 'cost', 'fees', 'financial', 'admissions', 'pricing']
        
        for link in soup.find_all('a', href=True):
            link_text = link.get_text().lower()
            link_href = link['href'].lower()
            
            if any(keyword in link_text or keyword in link_href for keyword in keywords):
                full_url = urljoin(university_website, link['href'])
                if full_url.startswith('http'):
                    return full_url
        
        return None
    
    def extract_costs_from_page(self, url: str) -> Dict:
        """Extract cost information from a university page."""
        html = self.fetch_page(url)
        if not html:
            return {}
        
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text()
        
        costs = {}
        
        # Extract tuition (look for patterns like $12,000 or $12000)
        tuition_patterns = [
            r'tuition[:\s]+\$?([\d,]+)',
            r'annual tuition[:\s]+\$?([\d,]+)',
            r'undergraduate tuition[:\s]+\$?([\d,]+)',
        ]
        
        for pattern in tuition_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                costs['tuition'] = self._parse_currency(match.group(1))
                break
        
        # Extract housing costs
        housing_patterns = [
            r'housing[:\s]+\$?([\d,]+)',
            r'room and board[:\s]+\$?([\d,]+)',
            r'accommodation[:\s]+\$?([\d,]+)',
        ]
        
        for pattern in housing_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                costs['housing'] = self._parse_currency(match.group(1))
                break
        
        # Extract application fee
        app_fee_patterns = [
            r'application fee[:\s]+\$?([\d,]+)',
            r'apply[:\s]+\$?([\d,]+)',
        ]
        
        for pattern in app_fee_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                costs['application_fee'] = self._parse_currency(match.group(1))
                break
        
        return costs
    
    @staticmethod
    def _parse_currency(value_str: str) -> float:
        """Parse currency string to float."""
        cleaned = value_str.replace(',', '').replace('$', '').strip()
        try:
            return float(cleaned)
        except ValueError:
            return 0.0
    
    def scrape_university(self, university_name: str, website: str) -> Dict:
        """
        Complete scraping workflow for a university.
        Returns normalized cost data.
        """
        print(f"Scraping {university_name}...")
        
        # Find tuition page
        tuition_url = self.find_tuition_page(website)
        if not tuition_url:
            print(f"Could not find tuition page for {university_name}")
            return {}
        
        # Extract costs
        costs = self.extract_costs_from_page(tuition_url)
        
        if costs:
            costs['university_name'] = university_name
            costs['official_website'] = website
            costs['data_source'] = 'web_scraper'
        
        return costs


class LLMEnhancedScraper(UniversityWebScraper):
    """
    Web scraper enhanced with LLM for intelligent extraction.
    Uses AI to parse unstructured cost information.
    """
    
    def __init__(self, openai_api_key: Optional[str] = None):
        super().__init__()
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
    
    def extract_with_llm(self, html_content: str, prompt_context: str) -> Dict:
        """
        Use OpenAI to extract structured data from HTML.
        """
        # TODO: Implement LLM-based extraction
        # This would send the HTML content to GPT-4 with a prompt asking
        # it to extract tuition, fees, housing costs, etc.
        pass


def scrape_multiple_universities(university_list: List[Dict]) -> List[Dict]:
    """
    Scrape multiple universities in batch.
    
    Args:
        university_list: List of dicts with 'name' and 'website' keys
    
    Returns:
        List of normalized cost dictionaries
    """
    scraper = UniversityWebScraper(rate_limit_delay=3.0)
    results = []
    
    for university in university_list:
        try:
            data = scraper.scrape_university(
                university['name'],
                university['website']
            )
            if data:
                results.append(data)
        except Exception as e:
            print(f"Error scraping {university['name']}: {e}")
    
    return results

"""
__init__.py for data.acquisition package
"""
from .api_sources import CollegeScorecard, TimesHigherEducation, OpenDataPortal
from .web_scraper import UniversityWebScraper, LLMEnhancedScraper

__all__ = [
    'CollegeScorecard',
    'TimesHigherEducation',
    'OpenDataPortal',
    'UniversityWebScraper',
    'LLMEnhancedScraper'
]

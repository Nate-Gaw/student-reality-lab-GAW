"""
Data schema definitions for university cost information.
"""
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime
from enum import Enum


class DegreeLevel(str, Enum):
    BACHELOR = "bachelor"
    MASTER = "master"
    DOCTORAL = "doctoral"
    CERTIFICATE = "certificate"


class Currency(str, Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    CAD = "CAD"
    AUD = "AUD"
    JPY = "JPY"
    CNY = "CNY"
    INR = "INR"


class UniversityCost(BaseModel):
    """Normalized university cost data schema."""
    
    # Identification
    university_id: Optional[int] = None
    university_name: str
    country: str
    city: str
    
    # Program Details
    degree_level: DegreeLevel
    program_name: Optional[str] = None
    programs: Optional[List[str]] = None  # Available majors/programs
    
    # Costs (annual, in local currency)
    currency: Currency = Currency.USD
    domestic_tuition: Optional[float] = None
    international_tuition: Optional[float] = None
    application_fee: Optional[float] = None
    estimated_housing_cost: Optional[float] = None
    estimated_living_cost: Optional[float] = None
    estimated_total_annual_cost: Optional[float] = None
    
    # Additional Costs
    student_fees: Optional[float] = None
    books_supplies: Optional[float] = None
    health_insurance: Optional[float] = None
    
    # Financial Aid
    has_scholarships: Optional[bool] = None
    has_financial_aid: Optional[bool] = None
    average_scholarship_amount: Optional[float] = None
    
    # Statistics
    acceptance_rate: Optional[float] = None  # 0.0 to 1.0
    graduation_rate: Optional[float] = None  # 0.0 to 1.0
    enrollment_count: Optional[int] = None
    international_student_percentage: Optional[float] = None
    
    # Metadata
    official_website: Optional[HttpUrl] = None
    data_source: str = "unknown"
    last_updated: datetime = Field(default_factory=datetime.now)
    data_quality_score: float = 1.0  # 0.0 to 1.0, based on completeness
    
    class Config:
        use_enum_values = True


class UniversityProfile(BaseModel):
    """Complete university profile with all degree programs."""
    
    university_name: str
    country: str
    city: str
    official_website: Optional[HttpUrl] = None
    founded_year: Optional[int] = None
    institution_type: Optional[str] = None  # public, private, etc.
    
    programs: List[UniversityCost] = []
    
    # Rankings (optional)
    world_ranking: Optional[int] = None
    national_ranking: Optional[int] = None
    
    last_updated: datetime = Field(default_factory=datetime.now)


class DataSourceConfig(BaseModel):
    """Configuration for a data source."""
    
    source_name: str
    source_type: str  # "api", "dataset", "scraper"
    base_url: Optional[str] = None
    requires_auth: bool = False
    api_key_env_var: Optional[str] = None
    rate_limit: int = 10  # requests per second
    priority: int = 1  # Lower number = higher priority
    countries_covered: List[str] = []
    reliability_score: float = 0.8

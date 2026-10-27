from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

# --- Схеми для створення (Request) ---

class PriceItemCreate(BaseModel):
    ticket_type: str = Field(..., alias="ticketType")
    price: float
    currency: str
    note: Optional[str] = None


class FineItemCreate(BaseModel):
    violation: str
    amount: float
    currency: str
    note: Optional[str] = None


class RuleCreate(BaseModel):
    city_id: int = Field(..., alias="cityId")
    description: str
    general_rules: str = Field(..., alias="generalRules")
    rules_source_url: str = Field(..., alias="rulesSourceUrl")
    prices_source_url: str = Field(..., alias="pricesSourceUrl")
    fines_source_url: str = Field(..., alias="finesSourceUrl")
    prices: List[PriceItemCreate] = []
    fines: List[FineItemCreate] = []


class CountryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=2, max_length=10)


class CityCreate(BaseModel):
    country_id: int = Field(..., alias="countryId")
    name: str = Field(..., min_length=1, max_length=100)

    model_config = ConfigDict(populate_by_name=True)


# --- Схеми для відповідей (Response) ---

class PriceItemResponse(BaseModel):
    id: int
    ticket_type: str
    price: float
    currency: str
    note: Optional[str] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class FineItemResponse(BaseModel):
    id: int
    violation: str
    amount: float
    currency: str
    note: Optional[str] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class AuthorShortResponse(BaseModel):
    id: int
    username: str
    badge: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CityResponse(BaseModel):
    id: int
    name: str
    country_id: int

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class CountryResponse(BaseModel):
    id: int
    name: str
    code: str

    model_config = ConfigDict(from_attributes=True)


class CountryDetailResponse(CountryResponse):
    cities: List[CityResponse] = []

    model_config = ConfigDict(from_attributes=True)


class RuleListResponse(BaseModel):
    id: int
    city_id: int
    country_id: int
    city_name: str
    country_name: str
    description: Optional[str] = None
    status: str
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RuleDetailResponse(BaseModel):
    id: int
    city: CityResponse
    country: CountryResponse
    author: AuthorShortResponse
    status: str
    description: Optional[str] = None
    general_rules: Optional[str] = None
    rules_source_url: Optional[str] = None
    prices_source_url: Optional[str] = None
    fines_source_url: Optional[str] = None
    verified_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    price_items: List[PriceItemResponse] = []
    fine_items: List[FineItemResponse] = []

    model_config = ConfigDict(from_attributes=True)
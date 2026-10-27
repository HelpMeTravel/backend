from pydantic import BaseModel, Field
from typing import Optional, List

# --- Country ---
class CountryBase(BaseModel):
    name: str
    code: str

class CountryCreate(CountryBase):
    pass

class CountryResponse(CountryBase):
    id: int

    class Config:
        from_attributes = True

# --- City ---
class CityBase(BaseModel):
    country_id: int = Field(..., alias="countryId")
    name: str

class CityCreate(CityBase):
    pass

class CityResponse(CityBase):
    id: int

    class Config:
        from_attributes = True
        populate_by_name = True
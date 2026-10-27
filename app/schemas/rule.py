from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, HttpUrl, Field

# Таблиця цін
class PriceItemCreate(BaseModel):
    ticket_type: str = Field(..., alias="ticketType")
    price: float
    currency: str
    note: Optional[str] = None

class PriceItemResponse(PriceItemCreate):
    id: int
    rule_id: int = Field(..., alias="ruleId")

    class Config:
        from_attributes = True
        populate_by_name = True

# Таблиця штрафів
class FineItemCreate(BaseModel):
    violation: str
    amount: float
    currency: str
    note: Optional[str] = None

class FineItemResponse(FineItemCreate):
    id: int
    rule_id: int = Field(..., alias="ruleId")

    class Config:
        from_attributes = True
        populate_by_name = True

# Основне правило (Створення / Оновлення)
class RuleCreate(BaseModel):
    city_id: int = Field(..., alias="cityId")
    description: str
    general_rules: str = Field(..., alias="generalRules")
    rules_source_url: str = Field(..., alias="rulesSourceUrl")
    prices_source_url: str = Field(..., alias="pricesSourceUrl")
    fines_source_url: str = Field(..., alias="finesSourceUrl")
    prices: List[PriceItemCreate] = []
    fines: List[FineItemCreate] = []

class RuleResponse(RuleCreate):
    id: int
    author_id: int = Field(..., alias="authorId")
    status: str  # draft, notPublished, published, rejected, expired[cite: 6, 7]
    verified_by: Optional[int] = Field(None, alias="verifiedBy")
    verified_at: Optional[datetime] = Field(None, alias="verifiedAt")
    expires_at: Optional[datetime] = Field(None, alias="expiresAt")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")

    class Config:
        from_attributes = True
        populate_by_name = True
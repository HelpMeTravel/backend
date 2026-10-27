from datetime import datetime
from pydantic import BaseModel, Field

# --- Favorite ---
class FavoriteBase(BaseModel):
    rule_id: int = Field(..., alias="ruleId")

class FavoriteCreate(FavoriteBase):
    pass

class FavoriteResponse(FavoriteBase):
    user_id: int = Field(..., alias="userId")
    created_at: datetime = Field(..., alias="createdAt")

    class Config:
        from_attributes = True
        populate_by_name = True

# --- Badge ---
class BadgeBase(BaseModel):
    name: str
    min_rules_count: int = Field(..., alias="minRulesCount")

class BadgeCreate(BadgeBase):
    pass

class BadgeResponse(BadgeBase):
    id: int

    class Config:
        from_attributes = True
        populate_by_name = True
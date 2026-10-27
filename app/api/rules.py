from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.models import Rule, City, Country
from app.models.enums import RuleStatus
from app.schemas.rule import RuleListResponse, RuleDetailResponse

router = APIRouter(prefix="/rules", tags=["Public Rules"])


@router.get("", response_model=List[RuleListResponse])
async def get_published_rules(
    country_id: Optional[int] = Query(None, description="Фільтр за ID країни"),
    city_id: Optional[int] = Query(None, description="Фільтр за ID міста"),
    search: Optional[str] = Query(None, description="Пошук за містом, країною або описом правил"),
    limit: int = Query(20, ge=1, le=100, description="Кількість записів на сторінку"),
    offset: int = Query(0, ge=0, description="Зсув для пагінації"),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(Rule)
        .join(Rule.city)
        .join(City.country)
        .where(Rule.status == RuleStatus.PUBLISHED)
        .options(selectinload(Rule.city).selectinload(City.country))
    )

    if country_id is not None:
        stmt = stmt.where(City.country_id == country_id)
    if city_id is not None:
        stmt = stmt.where(Rule.city_id == city_id)
    if search:
        pattern = f"%{search.strip()}%"
        stmt = stmt.where(
            or_(
                City.name.ilike(pattern),
                Country.name.ilike(pattern),
                Rule.description.ilike(pattern),
                Rule.general_rules.ilike(pattern),
            )
        )

    stmt = stmt.order_by(Rule.updated_at.desc()).offset(offset).limit(limit)
    result = await db.execute(stmt)
    rules = result.scalars().all()

    return [
        RuleListResponse(
            id=r.id,
            city_id=r.city.id,
            country_id=r.city.country.id,
            city_name=r.city.name,
            country_name=r.city.country.name,
            description=r.description,
            status=r.status.value,
            updated_at=r.updated_at,
        )
        for r in rules
    ]


@router.get("/{rule_id}", response_model=RuleDetailResponse)
async def get_rule_detail(rule_id: int, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Rule)
        .where(Rule.id == rule_id, Rule.status == RuleStatus.PUBLISHED)
        .options(
            selectinload(Rule.city).selectinload(City.country),
            selectinload(Rule.author),
            selectinload(Rule.price_items),
            selectinload(Rule.fine_items),
        )
    )
    result = await db.execute(stmt)
    rule = result.scalar_one_or_none()

    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Published rule not found",
        )

    return RuleDetailResponse(
        id=rule.id,
        city=rule.city,
        country=rule.city.country,
        author=rule.author,
        status=rule.status.value,
        description=rule.description,
        general_rules=rule.general_rules,
        rules_source_url=rule.rules_source_url,
        prices_source_url=rule.prices_source_url,
        fines_source_url=rule.fines_source_url,
        verified_at=rule.verified_at,
        expires_at=rule.expires_at,
        created_at=rule.created_at,
        updated_at=rule.updated_at,
        price_items=rule.price_items,
        fine_items=rule.fine_items,
    )
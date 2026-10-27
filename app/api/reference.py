from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.models import Country, City
from app.schemas.rule import (
    CountryCreate,
    CountryResponse,
    CountryDetailResponse,
    CityCreate,
    CityResponse,
)

router = APIRouter(prefix="/reference", tags=["Reference Data"])


@router.get("/countries", response_model=List[CountryResponse])
async def get_countries(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Country).order_by(Country.name))
    return result.scalars().all()


@router.get("/countries/{country_id}", response_model=CountryDetailResponse)
async def get_country_with_cities(country_id: int, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Country)
        .where(Country.id == country_id)
        .options(selectinload(Country.cities))
    )
    country = (await db.execute(stmt)).scalar_one_or_none()
    if not country:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Country not found")
    return country


@router.post("/countries", response_model=CountryResponse, status_code=status.HTTP_201_CREATED)
async def create_country(data: CountryCreate, db: AsyncSession = Depends(get_db)):
    stmt = select(Country).where(
        or_(Country.name.ilike(data.name), Country.code.ilike(data.code))
    )
    existing = (await db.execute(stmt)).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Country with this name or code already exists",
        )

    new_country = Country(name=data.name.strip(), code=data.code.strip().upper())
    db.add(new_country)
    await db.commit()
    await db.refresh(new_country)
    return new_country


@router.get("/cities", response_model=List[CityResponse])
async def get_cities(
    country_id: Optional[int] = Query(None, description="Фільтр міст за ID країни"),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(City)
    if country_id is not None:
        stmt = stmt.where(City.country_id == country_id)
    result = await db.execute(stmt.order_by(City.name))
    return result.scalars().all()


@router.post("/cities", response_model=CityResponse, status_code=status.HTTP_201_CREATED)
async def create_city(data: CityCreate, db: AsyncSession = Depends(get_db)):
    country = (
        await db.execute(select(Country).where(Country.id == data.country_id))
    ).scalar_one_or_none()
    if not country:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Country not found")

    existing_city = (
        await db.execute(
            select(City).where(
                City.country_id == data.country_id, City.name.ilike(data.name.strip())
            )
        )
    ).scalar_one_or_none()
    if existing_city:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="City already exists in this country",
        )

    new_city = City(country_id=data.country_id, name=data.name.strip())
    db.add(new_city)
    await db.commit()
    await db.refresh(new_city)
    return new_city
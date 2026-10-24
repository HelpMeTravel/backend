from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import RuleStatus, UserRole


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    password_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # Nullable під Google OAuth
    google_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.USER, nullable=False)
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    badge: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    rules: Mapped[List["Rule"]] = relationship("Rule", back_populates="author", foreign_keys="Rule.author_id")
    favorites: Mapped[List["Favorite"]] = relationship("Favorite", back_populates="user", cascade="all, delete-orphan")


class Country(Base):
    __tablename__ = "countries"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)  # наприклад, UA, PL, DE

    cities: Mapped[List["City"]] = relationship("City", back_populates="country", cascade="all, delete-orphan")


class City(Base):
    __tablename__ = "cities"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    country_id: Mapped[int] = mapped_column(ForeignKey("countries.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    country: Mapped["Country"] = relationship("Country", back_populates="cities")
    rules: Mapped[List["Rule"]] = relationship("Rule", back_populates="city")


class Rule(Base):
    __tablename__ = "rules"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    city_id: Mapped[int] = mapped_column(ForeignKey("cities.id", ondelete="RESTRICT"), nullable=False)
    status: Mapped[RuleStatus] = mapped_column(Enum(RuleStatus), default=RuleStatus.DRAFT, nullable=False)

    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    general_rules: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    rules_source_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    prices_source_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    fines_source_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    verified_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    author: Mapped["User"] = relationship("User", foreign_keys=[author_id], back_populates="rules")
    city: Mapped["City"] = relationship("City", back_populates="rules")
    price_items: Mapped[List["PriceItem"]] = relationship("PriceItem", back_populates="rule", cascade="all, delete-orphan")
    fine_items: Mapped[List["FineItem"]] = relationship("FineItem", back_populates="rule", cascade="all, delete-orphan")
    favorited_by: Mapped[List["Favorite"]] = relationship("Favorite", back_populates="rule", cascade="all, delete-orphan")


class PriceItem(Base):
    __tablename__ = "price_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    rule_id: Mapped[int] = mapped_column(ForeignKey("rules.id", ondelete="CASCADE"), nullable=False)
    ticket_type: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="EUR", nullable=False)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    rule: Mapped["Rule"] = relationship("Rule", back_populates="price_items")


class FineItem(Base):
    __tablename__ = "fine_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    rule_id: Mapped[int] = mapped_column(ForeignKey("rules.id", ondelete="CASCADE"), nullable=False)
    violation: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="EUR", nullable=False)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    rule: Mapped["Rule"] = relationship("Rule", back_populates="fine_items")


class Favorite(Base):
    __tablename__ = "favorites"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    rule_id: Mapped[int] = mapped_column(ForeignKey("rules.id", ondelete="CASCADE"), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship("User", back_populates="favorites")
    rule: Mapped["Rule"] = relationship("Rule", back_populates="favorited_by")


class Badge(Base):
    __tablename__ = "badges"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    min_rules_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
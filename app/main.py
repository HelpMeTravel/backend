from datetime import datetime, timezone, timedelta
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy import select

from app.core.database import engine, Base, async_session_maker
import app.models.models
from app.models.models import User, Country, City, Rule, PriceItem, FineItem
from app.models.enums import UserRole, RuleStatus
from app.api.reference import router as reference_router
from app.api.rules import router as rules_router
from app.routers.auth import router as auth_router  # <-- Підключаємо роутер аутентифікації


async def seed_initial_data():
    async with async_session_maker() as session:
        existing = (await session.execute(select(Country).limit(1))).scalar_one_or_none()
        if existing:
            return

        now = datetime.now(timezone.utc)

        author = User(
            email="guide@helpmetravel.com",
            username="TravelExpert",
            role=UserRole.USER,
            is_blocked=False,
            badge="Top Contributor",
            password_hash="hashed_dummy_password"
        )
        session.add(author)

        ua = Country(name="Ukraine", code="UA")
        pl = Country(name="Poland", code="PL")
        de = Country(name="Germany", code="DE")
        session.add_all([ua, pl, de])
        await session.flush()

        lviv = City(country_id=ua.id, name="Lviv")
        kyiv = City(country_id=ua.id, name="Kyiv")
        warsaw = City(country_id=pl.id, name="Warsaw")
        krakow = City(country_id=pl.id, name="Krakow")
        berlin = City(country_id=de.id, name="Berlin")
        session.add_all([lviv, kyiv, warsaw, krakow, berlin])
        await session.flush()

        lviv_rule = Rule(
            author_id=author.id,
            city_id=lviv.id,
            status=RuleStatus.PUBLISHED,
            description="Public transport in Lviv consists of trams, trolleybuses, and buses with electronic payment.",
            general_rules="Validate your LeoCard, bank card, or QR ticket immediately after boarding at the validator inside the vehicle.",
            rules_source_url="https://leocard.lviv.ua/",
            prices_source_url="https://leocard.lviv.ua/taryfy/",
            fines_source_url="https://city-adm.lviv.ua/",
            verified_at=now,
            expires_at=now + timedelta(days=180),
        )
        warsaw_rule = Rule(
            author_id=author.id,
            city_id=warsaw.id,
            status=RuleStatus.PUBLISHED,
            description="Warsaw Public Transport (WTP) integrates metro, buses, trams, and SKM urban trains.",
            general_rules="Paper tickets must be validated immediately upon entering the vehicle or before passing metro gates.",
            rules_source_url="https://www.wtp.waw.pl/en/regulations/",
            prices_source_url="https://www.wtp.waw.pl/en/ticket-tariff/",
            fines_source_url="https://www.wtp.waw.pl/en/additional-fees/",
            verified_at=now,
            expires_at=now + timedelta(days=180),
        )
        session.add_all([lviv_rule, warsaw_rule])
        await session.flush()

        session.add_all([
            PriceItem(rule_id=lviv_rule.id, ticket_type="LeoCard / App", price=13.00, currency="UAH", note="Free transfers within 40 min"),
            PriceItem(rule_id=lviv_rule.id, ticket_type="Bank Card / NFC", price=15.00, currency="UAH", note="Single trip"),
            PriceItem(rule_id=lviv_rule.id, ticket_type="Paper ticket (Driver)", price=25.00, currency="UAH", note="Cash payment"),
            FineItem(rule_id=lviv_rule.id, violation="Fare evasion (no validated ticket)", amount=300.00, currency="UAH", note="Paid on the spot"),
            PriceItem(rule_id=warsaw_rule.id, ticket_type="20-minute ticket (Zone 1&2)", price=3.40, currency="PLN", note="Unlimited transfers"),
            PriceItem(rule_id=warsaw_rule.id, ticket_type="75-minute ticket (Zone 1)", price=4.40, currency="PLN", note="Standard single fare"),
            FineItem(rule_id=warsaw_rule.id, violation="Riding without a valid ticket", amount=266.00, currency="PLN", note="Reduced if paid within 7 days"),
        ])

        await session.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await seed_initial_data()
    yield
    await engine.dispose()


app = FastAPI(
    title="HelpMeTravel",
    version="1.0",
    lifespan=lifespan
)

# Обов'язково для Google OAuth сесій
app.add_middleware(
    SessionMiddleware,
    secret_key="super-secret-key-for-session-transport-app"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Підключення всіх роутерів під загальним префіксом /api
app.include_router(reference_router, prefix="/api")
app.include_router(rules_router, prefix="/api")
app.include_router(auth_router, prefix="/api")  # <-- Реєстрація / Логін / OAuth


@app.get("/health")
async def health_check():
    return {
        "status": "online",
        "service": "backend",
        "message": "backend successfully launched in docker container"
    }
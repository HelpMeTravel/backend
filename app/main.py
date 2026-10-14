from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(
    title="HelpMeTravel",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",    # Дозволяємо класичний React через localhost
        "http://127.0.0.1:3000"     # Дозволяємо через IP-адресу
    ],
    allow_credentials=True,         # Дозволяємо передавати кукі та авторизаційні заголовки (токени)
    allow_methods=["*"],            # Дозволяємо всі методи: GET (читати), POST (створювати), DELETE (видаляти), PUT (оновлювати)
    allow_headers=["*"],            # Дозволяємо будь-які заголовки запитів від браузера

)

@app.get("/app/health")
async def health_check():
    return {
        "status":"online",
        "service":"backend",
        "message":"backend successfully launched in docker container="
    }
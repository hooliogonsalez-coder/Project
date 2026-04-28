from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import employees, rooms, sync

app = FastAPI(title="Biometric Access API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(employees.router)
app.include_router(rooms.router)
app.include_router(sync.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
from fastapi import FastAPI
from backend.api import router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Backend Océanos de Papel")

app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
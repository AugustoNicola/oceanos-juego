from fastapi import FastAPI
from backend.api import router

app = FastAPI(title="Backend Océanos de Papel")

app.include_router(router)
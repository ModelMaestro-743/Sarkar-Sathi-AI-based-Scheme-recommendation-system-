from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.api.routes import router

app = FastAPI(title="Sarkar Sathi - Government Schemes Assistant")
app.include_router(router)

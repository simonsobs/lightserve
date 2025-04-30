"""
Main API App for lightgest.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .auth import setup_auth
from .bands import band_router
from .observations import observations_router
from .settings import settings
from .sources import sources_router

app = FastAPI(root_path="/api/v1")

if settings.add_cors:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app = setup_auth(app)

app.include_router(sources_router)
app.include_router(observations_router)
app.include_router(band_router)

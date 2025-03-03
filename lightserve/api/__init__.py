"""
Main API App for lightserve.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .settings import settings

from .cutouts import cutouts_router
from .lightcurves import lightcurves_router
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

app.include_router(lightcurves_router)
app.include_router(sources_router)
app.include_router(cutouts_router)

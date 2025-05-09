"""
Main API App for lightserve.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .auth import setup_auth
from .cutouts import cutouts_router
from .lightcurves import lightcurves_router
from .settings import settings
from .sources import sources_router

app = FastAPI()

if settings.add_cors:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app = setup_auth(app)

app.include_router(lightcurves_router)
app.include_router(sources_router)
app.include_router(cutouts_router)

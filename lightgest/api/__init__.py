"""
Main API App for lightgest.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .auth import setup_auth
from .instruments import band_router
from .observations import observations_router
from .settings import settings
from .sources import sources_router

openapi_tags = [
    {
        "name": "Sources",
        "description": (
            "Create and delete sources in lightcurvedb. "
            "Entity: Source. Requires scopes lcs:create or lcs:delete."
        ),
    },
    {
        "name": "Observations",
        "description": (
            "Ingest flux measurements and optional cutouts into lightcurvedb. "
            "Entities: FluxMeasurementCreate, Cutout. Requires scope lcs:create."
        ),
    },
    {
        "name": "Instruments",
        "description": (
            "Create and delete instruments in lightcurvedb. "
            "Entity: Instrument. Requires scopes lcs:create or lcs:delete."
        ),
    },
]

app = FastAPI(openapi_tags=openapi_tags)

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

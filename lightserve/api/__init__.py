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
from .analysis import analysis_router


openapi_tags = [
    {
        "name": "Lightcurves",
        "description": (
            "Read-only lightcurve retrieval backed by lightcurvedb. "
            "Entities: Source, FluxMeasurement, Instrument/Frequency views. "
            "Requires scope lcs:read."
        ),
    },
    {
        "name": "Sources",
        "description": (
            "Read-only source catalog and statistics backed by lightcurvedb. "
            "Entities: Source, SourceStatistics. Requires scope lcs:read."
        ),
    },
    {
        "name": "Cutouts",
        "description": (
            "Retrieve cutouts for flux measurements backed by lightcurvedb. "
            "Entities: Cutout, FluxMeasurement. Requires scope lcs:read."
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

app.include_router(lightcurves_router)
app.include_router(sources_router)
app.include_router(cutouts_router)
app.include_router(analysis_router)

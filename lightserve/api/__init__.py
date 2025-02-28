"""
Main API App for lightserve.
"""

from fastapi import FastAPI

from .lightcurves import lightcurves_router
from .sources import sources_router

app = FastAPI(root_path="/api/v1")

app.include_router(lightcurves_router)
app.include_router(sources_router)

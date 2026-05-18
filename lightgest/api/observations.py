"""
Add observations to a source.
"""

from uuid import UUID

import pandas as pd
from fastapi import APIRouter, HTTPException, Request, UploadFile, status
from lightcurvedb.models.cutout import Cutout
from lightcurvedb.models.flux import FluxMeasurement

from lightgest.database import DatabaseBackend

from .auth import requires

observations_router = APIRouter(prefix="/observations", tags=["Observations"])


@observations_router.put(
    "/",
    summary="Create observation",
    description=(
        "Create a flux measurement and optional cutout. Requires scope lcs:create."
    ),
)
@requires("lcs:create")
async def add_observation(
    request: Request,
    flux_measurement: FluxMeasurement,
    backend: DatabaseBackend,
    cutout: Cutout | None = None,
) -> tuple[UUID, UUID | None]:
    measurement_id = await backend.fluxes.create(measurement=flux_measurement)

    if cutout is not None:
        enforced_cutout = Cutout(
            **{**cutout.model_dump(), "measurement_id": measurement_id}
        )

        cutout_id = await backend.cutouts.create(cutout=enforced_cutout)
    else:
        cutout_id = None

    return measurement_id, cutout_id


@observations_router.put(
    "/batch",
    summary="Create observations in batch",
    description=(
        "Create multiple flux measurements with optional cutouts in a single call. "
        "Requires scope lcs:create."
    ),
)
@requires("lcs:create")
async def add_observation_batch(
    request: Request,
    flux_measurements: list[FluxMeasurement],
    backend: DatabaseBackend,
    cutouts: list[Cutout] | None = None,
) -> tuple[list[UUID], list[UUID] | None]:
    measurement_ids = await backend.fluxes.create_batch(measurements=flux_measurements)

    if cutouts and len(cutouts) > 0:
        if len(cutouts) != len(measurement_ids):
            return HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Number of cutouts must match number of flux measurements",
            )

        cutouts = [
            Cutout(**{**cutout.model_dump(), "measurement_id": measurement_id})
            for measurement_id, cutout in zip(measurement_ids, cutouts)
        ]

        cutout_ids = await backend.cutouts.create_batch(cutouts=cutouts)
    else:
        cutout_ids = None

    return measurement_ids, cutout_ids


@observations_router.post(
    "/parquet",
    summary="Create observations from parquet file",
    description=(
        "Create flux measurements and optional cutouts from a parquet file. Requires scope lcs:create"
    ),
)
@requires("lcs:create")
async def add_observation_parquet(
    request: Request,
    file: UploadFile,
    backend: DatabaseBackend,
) -> list[UUID]:
    """
    Create flux measurements and cutouts from a parquet file. The parquet file should
    contain all necessary information to create the flux measurements and cutouts, and
    should be formatted according to the specifications outlined in the documentation.
    """

    try:
        measurement_ids = await backend.fluxes.ingest_dataframe(
            df=pd.read_parquet(file.file)
        )
        return measurement_ids
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error processing parquet file: {str(e)}",
        )

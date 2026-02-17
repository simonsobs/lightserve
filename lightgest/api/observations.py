"""
Add observations to a source.
"""

from uuid import UUID

from fastapi import APIRouter, HTTPException, Request, status
from lightcurvedb.models.cutout import Cutout
from lightcurvedb.models.flux import FluxMeasurementCreate

from lightgest.database import DatabaseBackend

from .auth import requires

observations_router = APIRouter(prefix="/observations")


@observations_router.put("/")
@requires("lcs:create")
async def add_observation(
    request: Request,
    flux_measurement: FluxMeasurementCreate,
    backend: DatabaseBackend,
    cutout: Cutout | None = None,
) -> tuple[UUID, UUID | None]:
    measurement_id = await backend.fluxes.create(flux_measurement=flux_measurement)

    if cutout is not None:
        enforced_cutout = Cutout(
            measurement_id=measurement_id,
            **cutout.model_dump(),
        )

        cutout_id = await backend.cutouts.create(cutout=enforced_cutout)
    else:
        cutout_id = None

    return measurement_id, cutout_id


@observations_router.put("/batch")
@requires("lcs:create")
async def add_observation_batch(
    request: Request,
    flux_measurements: list[FluxMeasurementCreate],
    backend: DatabaseBackend,
    cutouts: list[Cutout] | None = None,
) -> tuple[list[UUID], list[UUID] | None]:
    measurement_ids = await backend.fluxes.create_batch(
        flux_measurements=flux_measurements
    )

    if cutouts and len(cutouts) > 0:
        if len(cutouts) != len(measurement_ids):
            return HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Number of cutouts must match number of flux measurements",
            )

        cutouts = [
            Cutout(
                measurement_id=measurement_id,
                **cutout.model_dump(),
            )
            for measurement_id, cutout in zip(measurement_ids, cutouts)
        ]

        cutout_ids = await backend.cutouts.create_batch(cutouts=cutouts)
    else:
        cutout_ids = None

    return measurement_ids, cutout_ids

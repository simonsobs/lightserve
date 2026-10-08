import io

import pyarrow as pa
import pyarrow.parquet as pq


import h5py
from pydantic_csv import BasemodelCSVWriter

from lightcurvedb.models.flux import FluxMeasurement


def _transform_flux_measurements_to_parquet(
    data: list[FluxMeasurement], handle: io.BytesIO
):
    """
    Transform a list of flux measurements to Parquet format, using pyarrow
    directly.

    Arguments
    ---------
    data: list[FluxMeasurement]
        List of flux measurements
    handle: io.BytesIO
        Binary stream to write to (managed by caller)
    """

    rb = pa.RecordBatch.from_pylist([x.model_dump() for x in data])
    # Write to Parquet
    pq.write_table(pa.Table.from_batches([rb]), handle)

    return


def _transform_flux_measurements_to_csv(
    data: list[FluxMeasurement], handle: io.StringIO
):
    """
    Transform a list of flux measurements to CSV format.

    Arguments
    ---------
    data: list[FluxMeasurement]
        List of flux measurements
    handle: io.StringIO
        String stream to write to (managed by caller)
    """

    if not data:
        return

    writer = BasemodelCSVWriter(handle, data=data, model=FluxMeasurement)
    writer.write()

    return


def _transform_flux_measurements_to_hdf5(
    data: list[FluxMeasurement], handle: io.BytesIO
):
    """
    Transform a list of flux measurements to HDF5 format.

    Arguments
    ---------
    data: list[FluxMeasurement]
        List of flux measurements
    handle: io.BytesIO
        Binary stream to write to (managed by caller)
    """

    if not data:
        return

    def serialize_flux_measurement(fm: FluxMeasurement) -> dict:
        base = fm.model_dump()
        return {
            "measurement_id": str(base["measurement_id"]),
            "frequency": base["frequency"],
            "module": base["module"],
            "source_id": str(base["source_id"]),
            "time": base["time"].isoformat(),
            "flux": base["flux"],
            "flux_err": base["flux_err"],
            "ra": base["ra"],
            "dec": base["dec"],
            "ra_uncertainty": base["ra_uncertainty"],
            "dec_uncertainty": base["dec_uncertainty"],
            "extra": str(base["extra"]) if base["extra"] is not None else "",
        }

    data = [serialize_flux_measurement(fm) for fm in data]

    with h5py.File(handle, "w") as hf:
        for field in FluxMeasurement.model_fields.keys():
            hf.create_dataset(field, data=[x[field] for x in data])

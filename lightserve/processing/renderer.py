import csv
import io
from typing import Any, Dict, List

import h5py
from lightcurvedb.client.lightcurve import LightcurveBandResult, LightcurveResult

LIGHTCURVE_FIELD_CONFIG: Dict[str, Dict[str, Any]] = {
    "id": {
        "description": "Source ID",
        "units": "dimensionless",
        "csv_header": "source_id"
    },
    "time": {
        "description": "Observation timestamp",
        "units": "seconds in unix isoformat",
        "csv_header": "obs_time_unix"
    },
    "i_flux": {
        "description": "Source intensity",
        "units": "mJy",
        "csv_header": "flux_mjy"
    },
    "i_uncertainty": {
        "description": "Source intensity uncertainty",
        "units": "mJy",
        "csv_header": "flux_err_mjy"
    },
    "ra": {
        "description": "Source right ascension",
        "units": "degrees",
        "csv_header": "ra_deg"
    },
    "dec": {
        "description": "Source declination",
        "units": "degrees",
        "csv_header": "dec_deg"
    },
    "ra_uncertainty": {
        "description": "Source right ascension uncertainty",
        "units": "degrees",
        "csv_header": "ra_err_deg"
    },
    "dec_uncertainty": {
        "description": "Source declination uncertainty",
        "units": "degrees",
        "csv_header": "dec_err_deg"
    },
    "band": {
        "description": "Source band",
        "units": "GHz",
        "csv_header": "frequency_GHz"
    }
}

FIELD_ORDER = [
    "id", "time", "i_flux", "i_uncertainty", 
    "ra", "dec", "ra_uncertainty", "dec_uncertainty", "band"
]


def _prepare_data(lightcurve_band: LightcurveBandResult) -> Dict[str, List[Any]]:
    """
    Prepare lightcurve data for writing.
    
    Args:
        lightcurve_band: Single band lightcurve data
        
    Returns:
        Dictionary with field names as keys and lists of values
    """
    data = {}
    
    for field in FIELD_ORDER:
        if field == "band":
            data[field] = [int(lightcurve_band.band.name[1:])] * len(lightcurve_band.id)
        elif field == "time":  
            data[field] = [t.timestamp() for t in lightcurve_band.time]  
        else:
            data[field] = getattr(lightcurve_band, field)
    
    return data


def _get_csv_headers() -> List[str]:
    """
    Get CSV header from field configuration.
    """
    return [LIGHTCURVE_FIELD_CONFIG[field]["csv_header"] for field in FIELD_ORDER]


def _transform_band_lc_to_csv(
    lightcurve_band: LightcurveBandResult, 
    handle: io.StringIO
) -> str:
    """
    Transform a single band's lightcurve data to CSV format.

    Args:
        lightcurve_band: Single band lightcurve data
        handle: Text stream to write to (managed by caller)
        
    Returns:
        CSV content as string
    """
    # Prepare data
    data = _prepare_data(lightcurve_band)
    num_rows = len(lightcurve_band.id)
    
    def row_generator():
        yield _get_csv_headers()
        for i in range(num_rows):
            yield [data[field][i] for field in FIELD_ORDER]
    
    csv_writer = csv.writer(handle,quoting=csv.QUOTE_MINIMAL)
    csv_writer.writerows(row_generator()) 
    
    return handle.getvalue()


def _transform_lc_to_csv(
    lightcurve: LightcurveResult, 
    handle: io.StringIO
) -> str:
    """
    Transform multi-band lightcurve data to CSV format.
    
    Args:
        lightcurve: Multi-band lightcurve data
        handle: Text stream to write to
        
    Returns:
        CSV content as string
    """

    def all_rows_generator():
        yield _get_csv_headers()
        
        for band_data in lightcurve.bands:
            data = _prepare_data(band_data)
            num_rows = len(band_data.id)
            
            for i in range(num_rows):
                yield [data[field][i] for field in FIELD_ORDER]
    
    csv_writer = csv.writer(handle,quoting=csv.QUOTE_MINIMAL)
    csv_writer.writerows(all_rows_generator())
    
    return handle.getvalue()


def _create_hdf5_dataset(group: h5py.Group, field: str, data: list) -> None:
    """
    Create an HDF5 dataset with metadata from configuration.
    
    Args:
        group: HDF5 group to create dataset in
        field: Field name from FIELD_ORDER
        data: Numpy array to store
    """
    config = LIGHTCURVE_FIELD_CONFIG[field]
    
    # Create dataset
    dataset = group.create_dataset(
        field,
        data=data,
    )
    
    dataset.attrs["description"] = config["description"]
    dataset.attrs["units"] = config["units"]


def _transform_band_lc_to_hdf5(
    lightcurve_band: LightcurveBandResult, 
    handle: io.BytesIO
) -> bytes:
    """
    Transform a single band's lightcurve data to HDF5 format.

    Args:
        lightcurve_band: Single band lightcurve data
        handle: Binary stream to write to (managed by caller)
        
    Returns:
        HDF5 content as bytes
    """
    with h5py.File(handle, 'w') as hf:
        
        # Prepare data
        data = _prepare_data(lightcurve_band)
        
        # Create datasets for each field
        for field in FIELD_ORDER:
            _create_hdf5_dataset(hf, field, data[field])
    
    return handle.getvalue()


def _transform_lc_to_hdf5(
    lightcurve: LightcurveResult, 
    handle: io.BytesIO
) -> bytes:
    """
    Transform multi-band lightcurve data to HDF5 format.
    
    Args:
        lightcurve: Multi-band lightcurve data
        handle: Binary stream to write to
        
    Returns:
        HDF5 content as bytes
    """
    with h5py.File(handle, 'w') as hf:
        
        for band_data in lightcurve.bands:
            # Create group for this band
            band_group = hf.create_group(band_data.band.name)
        
            data = _prepare_data(band_data)
            
            for field in FIELD_ORDER:
                _create_hdf5_dataset(band_group, field, data[field])
    
    return handle.getvalue()
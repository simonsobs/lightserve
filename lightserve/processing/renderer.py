import io

import h5py
from lightcurvedb.client.lightcurve import LightcurveBandResult, LightcurveResult

LIGHTCURVE_FIELD_CONFIG: dict[str, dict[str, str]] = {
    "id": {
        "description": "Source ID",
        "output_type": "i4",
        "units": "dimensionless",
        "format_string": r"{:08d}",
    },
    "time": {
        "description": "Observation timestamp",
        "output_type": "i8",
        "units": "seconds",
        "conversion_function": lambda x: int(x.timestamp()),
        "format_string": r"{:d}",
    },
    "i_flux": {
        "description": "Source intensity",
        "output_type": "f4",
        "units": "Jy",
        "format_string": r"{:+010.4f}",  # Up to 9999 Jy with 0.1 mJy precision
    },
    "i_uncertainty": {
        "description": "Source intensity uncertainty",
        "output_type": "f4",
        "units": "Jy",
        "format_string": r"{:+010.4f}",  # Up to 9999 Jy with 1 mJy precision
    },
    "ra": {
        "description": "Source right ascension",
        "units": "degrees",
        "output_type": "f4",
        "format_string": r"{:+08.3f}",  # down to 4 arcsec precision with leading zeros and +/-
    },
    "dec": {
        "description": "Source declination",
        "units": "degrees",
        "output_type": "f4",
        "format_string": r"{:+07.3f}",  # down to 4 arcsec precision with leading zeros and +/-
    },
    # "ra_uncertainty": {
    #     "description": "Source right ascension uncertainty",
    #     "output_type": "f4",
    #     "units": "degrees",
    # },
    # "dec_uncertainty": {
    #     "description": "Source declination uncertainty",
    #     "output_type": "f4",
    #     "units": "degrees",
    # },
}


def _prepare_data_columnar(
    lightcurve_band: LightcurveBandResult,
) -> dict[str, list[float | str | int]]:
    """
    Prepare lightcurve data for writing in a columnar format by using
    conversion functions where specified.

    Arguments
    ---------
    lightcurve_band: LightcurveBandResult
        The columnar formatted band result.

    Returns
    -------
    dict[str,  list[float | str | int]]
        Columns formatted using "conversion_function"s.


    """

    data = {}

    for field, config in LIGHTCURVE_FIELD_CONFIG.items():
        data[field] = getattr(lightcurve_band, field)

        if "conversion_function" in config:
            data[field] = list(map(config["conversion_function"], data[field]))

    return data


def _prepare_data_row(lightcurve_band: LightcurveBandResult) -> list[str]:
    """
    Prepare lightcurve data for wirting in a row-based format, i.e. formats
    them as comma-separated strings according to their string formatter.

    Arguments
    ---------
    lightcurve_band: LightcurveBandResult
        The columnar formatted band result.

    Returns
    -------
    list[str]
        Rows formatted using "conversion_function"s and the "format_string"
        options above.

    """

    formatting_string = ",".join(
        c["format_string"] for c in LIGHTCURVE_FIELD_CONFIG.values()
    )

    data = [
        formatting_string.format(*args)
        for args in zip(
            *_prepare_data_columnar(lightcurve_band=lightcurve_band).values()
        )
    ]

    return data


def _get_csv_headers() -> str:
    """
    Get CSV header from field configuration.
    """
    return "# " + ",".join(
        [
            f"{field} [{config['units']}]"
            for field, config in LIGHTCURVE_FIELD_CONFIG.items()
        ]
    )


def _transform_band_lc_to_csv(
    lightcurve_band: LightcurveBandResult, handle: io.StringIO
):
    """
    Transform a single band's lightcurve data to CSV format.

    Arguments
    ---------
    lightcurve_band: LightcurveBandResult
        Single band lightcurve data
    handle: io.StringIO
        Byte stream supporting string I/O (managed by caller)
    """

    def row_generator():
        yield _get_csv_headers() + "\n"
        for row in _prepare_data_row(lightcurve_band):
            yield row + "\n"

    handle.writelines(row_generator())

    return


def _transform_lc_to_csv(lightcurve: LightcurveResult, handle: io.StringIO):
    """
    Transform multi-band lightcurve data to CSV format.

    Arguments
    ---------
    lightcurve: LightcurveResult
        Multi-band lightcurve data
    handle: io.StringIO
        Byte stream supporting string I/O (managed by caller)
    """

    def row_generator():
        # Same as above, but need to add band as final argument.
        header = _get_csv_headers() + ",band [Ghz]" + "\n"
        yield header

        for band_data in sorted(lightcurve.bands, key=lambda x: x.band.frequency):
            for row in _prepare_data_row(band_data):
                yield row + f",{band_data.band.frequency:03.0f}\n"

    handle.writelines(row_generator())

    return


def _create_hdf5_dataset(group: h5py.Group, field: str, data: list):
    """
    Create an HDF5 dataset with metadata from configuration.

    Arguments
    ---------
    group: h5py.Group
        HDF5 group to create dataset in
    field: str
        Field name from LIGHTCURVE_FIELD_CONFIG, specifies output type
        and additional metadata
    data: list
        Numpy array or list to store in dataset
    """
    config = LIGHTCURVE_FIELD_CONFIG[field]

    dataset = group.create_dataset(field, data=data, dtype=config["output_type"])

    dataset.attrs["description"] = config["description"]
    dataset.attrs["units"] = config["units"]


def _transform_band_lc_to_hdf5(
    lightcurve_band: LightcurveBandResult, handle: io.BytesIO
):
    """
    Transform a single band's lightcurve data to HDF5 format.

    Arguments
    ---------
    lightcurve_band: LightcurveBandResult
        Single band lightcurve data
    handle: io.BytesIO
        Binary stream to write to (managed by caller)
    """

    with h5py.File(handle, "w") as hf:
        data = _prepare_data_columnar(lightcurve_band)

        for field in LIGHTCURVE_FIELD_CONFIG.keys():
            _create_hdf5_dataset(hf, field, data[field])

    return


def _transform_lc_to_hdf5(lightcurve: LightcurveResult, handle: io.BytesIO):
    """
    Transform multi-band lightcurve data to HDF5 format.

    Arguments
    ---------
    lightcurve: LightcurveResult
        Multi-band lightcurve data
    handle: io.BytesIO
        Binary stream to write to (managed by caller)
    """
    with h5py.File(handle, "w") as hf:
        for band_data in lightcurve.bands:
            band_group = hf.create_group(band_data.band.name)
            band_group.attrs.update(**band_data.band.model_dump())

            data = _prepare_data_columnar(band_data)

            for field in LIGHTCURVE_FIELD_CONFIG.keys():
                _create_hdf5_dataset(band_group, field, data[field])

    return

import csv
import io

import h5py
from lightcurvedb.client.lightcurve import LightcurveBandResult, LightcurveResult

lightcurve_save_items = [
    "id",
    "time",
    "i_flux",
    "i_uncertainty",
    "ra",
    "dec",
    "ra_uncertainty",
    "dec_uncertainty",
    "band",
]
def _transform_lc_to_csv(lightcurve_file: LightcurveBandResult | LightcurveResult) -> tuple[bytes, str]:
    output = io.StringIO()
    csv_writer = csv.writer(output)
    csv_writer.writerow(lightcurve_save_items)
    if isinstance(lightcurve_file, LightcurveBandResult):
        for i in range(len(lightcurve_file.time)):
            csv_writer.writerow([lightcurve_file.id[i],lightcurve_file.time[i], lightcurve_file.i_flux[i], lightcurve_file.i_uncertainty[i], lightcurve_file.ra[i], lightcurve_file.dec[i], lightcurve_file.ra_uncertainty[i], lightcurve_file.dec_uncertainty[i],lightcurve_file.band.name])
    if isinstance(lightcurve_file, LightcurveResult):
        for band_data in lightcurve_file.bands:
            for i in range(len(band_data.time)):
                csv_writer.writerow([band_data.id[i],band_data.time[i], band_data.i_flux[i], band_data.i_uncertainty[i], band_data.ra[i], band_data.dec[i], band_data.ra_uncertainty[i], band_data.dec_uncertainty[i],band_data.band.name])
    csv_content = output.getvalue()
    media_type = "text/csv"
    return csv_content, media_type

def _transform_lc_to_hdf5(lightcurve_file: LightcurveBandResult | LightcurveResult) -> tuple[bytes, str]:
    output = io.BytesIO()
    with h5py.File(output, 'w') as hf:
        if isinstance(lightcurve_file, LightcurveBandResult):
            hf.create_dataset(lightcurve_save_items[0], data=lightcurve_file.id)
            hf.create_dataset(lightcurve_save_items[1], data=[t.isoformat() for t in lightcurve_file.time])
            hf.create_dataset(lightcurve_save_items[2], data=lightcurve_file.i_flux)
            hf.create_dataset(lightcurve_save_items[3], data=lightcurve_file.i_uncertainty)
            hf.create_dataset(lightcurve_save_items[4], data=lightcurve_file.ra)
            hf.create_dataset(lightcurve_save_items[5], data=lightcurve_file.dec)
            hf.create_dataset(lightcurve_save_items[6], data=lightcurve_file.ra_uncertainty)
            hf.create_dataset(lightcurve_save_items[7], data=lightcurve_file.dec_uncertainty)
            hf.create_dataset(lightcurve_save_items[8], data=lightcurve_file.band.name)
        elif isinstance(lightcurve_file, LightcurveResult):
            for band_data in lightcurve_file.bands:
                band_group = hf.create_group(band_data.band.name)
                band_group.create_dataset(lightcurve_save_items[0], data=band_data.id)
                band_group.create_dataset(lightcurve_save_items[1], data=[t.isoformat() for t in band_data.time])
                band_group.create_dataset(lightcurve_save_items[2], data=band_data.i_flux)
                band_group.create_dataset(lightcurve_save_items[3], data=band_data.i_uncertainty)
                band_group.create_dataset(lightcurve_save_items[4], data=band_data.ra)
                band_group.create_dataset(lightcurve_save_items[5], data=band_data.dec)
                band_group.create_dataset(lightcurve_save_items[6], data=band_data.ra_uncertainty)
                band_group.create_dataset(lightcurve_save_items[7], data=band_data.dec_uncertainty)
                band_group.create_dataset(lightcurve_save_items[8], data=band_data.band.name)
    hdf5_content = output.getvalue()
    media_type = "application/x-hdf5"
    return hdf5_content, media_type
"""
Endpoints to get cutouts corresponding to specific observations.
"""

import io
from pathlib import Path
from typing import Any, BinaryIO, Literal, Optional, Union

import matplotlib.pyplot as plt
import numpy as np
from astropy.io import fits
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from lightcurvedb.client.cutouts import CutoutNotFound, cutout_read_from_flux_id
from matplotlib.colors import LogNorm
from pydantic import BaseModel, Field

from lightserve.database import AsyncSessionDependency

from .auth import requires

cutouts_router = APIRouter(prefix="/cutouts")


class RenderOptions(BaseModel):
    cmap: str = Field(default="viridis")
    "Color map to use for rendering, defaults to 'viridis', and may not be used if RGBA buffers are provided."
    vmin: float = Field(default=0.0)
    "Color map range minimum, defaults to 0.0"
    vmax: float = Field(default=1000.0)
    "Color map range maximum, defaults to 1000.0"
    log_norm: bool = Field(default=False)
    "Whether to use a log normalization, defaults to False."
    clip: bool = Field(default=True)
    "Whether to clip values outside of the range, defaults to True."

    @property
    def norm(self) -> plt.Normalize:
        if self.log_norm:
            return LogNorm(vmin=self.vmin, vmax=self.vmax, clip=self.clip)
        else:
            return plt.Normalize(vmin=self.vmin, vmax=self.vmax, clip=self.clip)


class Renderer:
    format: Optional[str]
    "Format to render images to, defaults to 'webp'."
    pil_kwargs: Optional[dict[str, Any]]
    "Keyword arguments to pass to PIL for rendering, defaults to None."

    def __init__(
        self,
        format: Optional[str] = "webp",
        pil_kwargs: Optional[dict[str, Any]] = None,
    ):
        self.format = format
        self.pil_kwargs = pil_kwargs

        return

    def render(
        self,
        fname: Union[str, Path, BinaryIO],
        buffer: np.ndarray,
        render_options: RenderOptions,
    ):
        """
        Renders the buffer to the given file.

        Parameters
        ----------
        fname : Union[str, Path, BinaryIO]
            Output for the rendering.
        buffer : np.ndarray
            Buffer to render to disk or IO.
        render_options : RenderOptions
            Options for rendering.

        Notes
        -----

        Buffer is transposed in x, y to render correctly within this function.
        """

        if buffer.ndim == 2:
            # Render with colour mapping, this is 'raw data'.
            cmap = plt.get_cmap(render_options.cmap)
            cmap.set_bad("#dddddd", 0.0)
            plt.imsave(
                fname,
                render_options.norm(buffer),
                cmap=cmap,
                pil_kwargs=self.pil_kwargs,
                format=self.format,
                # Data is pre-normalized using render_options.norm
                vmin=0.0,
                vmax=1.0,
                origin="lower",
            )
        else:
            # Direct rendering
            plt.imsave(
                fname,
                np.ascontiguousarray(buffer.swapaxes(0, 1)),
                pil_kwargs=self.pil_kwargs,
                format=self.format,
            )

        return


render_options = RenderOptions()
renderer = Renderer(format="png")


@cutouts_router.get("/flux/{id}")
@requires("lcs:read")
async def cutouts_get_from_flux_id(
    request: Request,
    id: int,
    ext: Literal["png", "fits","hdf5"],
    conn: AsyncSessionDependency,
    render_options: RenderOptions = Depends(RenderOptions),
) -> Response:
    """
    Return the cutout assocaited with a flux measurement's ID.
    """

    try:
        cutout = await cutout_read_from_flux_id(flux_measurement_id=id, conn=conn)
    except CutoutNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cutout not found for flux measurement {id}",
        )

    numpy_buf = np.array(cutout.data)
    if ext == "png":
        with io.BytesIO() as output:
            renderer.render(output, numpy_buf, render_options=render_options)
            return Response(content=output.getvalue(), media_type="image/png")
    if ext == "fits":
        with io.BytesIO() as output:
            hdu = fits.PrimaryHDU(data=numpy_buf)
            hdu.writeto(output)
            return Response(content=output.getvalue(), media_type="image/fits")
    if ext == "hdf5":
        with io.BytesIO() as output:
            import h5py
            with h5py.File(output, "w") as f:
                f.create_dataset("data", data=numpy_buf)
            return Response(content=output.getvalue(), media_type="application/x-hdf5")
    

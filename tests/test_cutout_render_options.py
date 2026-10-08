"""
Tests for RenderOptions' vmin/vmax defaulting (lightserve/api/cutouts.py).

Cutout pixel data can be stored in different flux units depending on the
source/instrument (Jy, mJy, ...), so a fixed numeric vmin/vmax default is
never right for every cutout -- e.g. a source stored in Jy (peak ~1) would
render as a flat, saturated-black image under a vmax=1000 default tuned for
mJy-scale data. RenderOptions instead defaults to the cutout's own min/max
when the caller doesn't explicitly request a range.
"""

import numpy as np

from lightserve.api.cutouts import RenderOptions


def test_defaults_to_buffer_min_max_when_unset():
    buffer = np.array([[0.0, 0.5], [1.0, 0.25]])

    norm = RenderOptions().norm(buffer)

    assert norm.vmin == 0.0
    assert norm.vmax == 1.0


def test_explicit_vmin_vmax_overrides_buffer_range():
    buffer = np.array([[0.0, 0.5], [1.0, 0.25]])

    norm = RenderOptions(vmin=-10.0, vmax=10.0).norm(buffer)

    assert norm.vmin == -10.0
    assert norm.vmax == 10.0


def test_small_jy_scale_buffer_is_not_washed_out_by_a_large_fixed_default():
    """Regression check for the old vmax=1000.0 default: a Jy-scale cutout
    (peak ~0.9) should span the normalized [0, 1] range on its own values,
    not collapse to ~0 under a scale tuned for mJy data."""
    buffer = np.array([[0.1, 0.9], [0.05, 0.3]])

    norm = RenderOptions().norm(buffer)
    normalized = norm(buffer)

    assert normalized.max() == 1.0
    assert normalized.min() == 0.0


def test_only_one_of_vmin_vmax_overridden():
    buffer = np.array([[0.0, 0.5], [1.0, 0.25]])

    norm = RenderOptions(vmin=-1.0).norm(buffer)

    assert norm.vmin == -1.0
    assert norm.vmax == 1.0  # falls back to buffer max

"""
Importing anything under lightserve.api eagerly instantiates the module-level
`settings` object (lightserve/api/settings.py), which requires
TELEMETRY__ENABLE to be set -- there's no default, since normally it's
supplied via the environment when running the actual server. Set it before
test collection so `pytest` works without extra setup.
"""

import os

os.environ.setdefault("TELEMETRY__ENABLE", "false")

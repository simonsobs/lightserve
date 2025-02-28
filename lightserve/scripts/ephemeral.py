"""
Run an ephemeral server, alongside an ephemeral lightcurve server.
"""

import uvicorn
from lightcurvedb.cli.ephemeral import core


def main():
    # Setup that DB
    with core(number=16):
        print("Starting webapp")
        from lightserve.api import app

        uvicorn.run(app)


if __name__ == "__main__":
    main()

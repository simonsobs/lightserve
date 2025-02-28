"""
Run an ephemeral server, alongside an ephemeral lightcurve server.
"""

import uvicorn
from lightcurvedb.cli.ephemeral import core


def main():
    # Setup that DB
    with core(number=16, probability_of_flare=0.9):
        print("Starting webapp")
        from lightserve.api import app

        uvicorn.run(app)


if __name__ == "__main__":
    main()

"""
Run an ephemeral server, alongside an ephemeral lightcurve server.
"""

import uvicorn
from lightcurvedb.cli.ephemeral import core as db

from lightserve.telemetry import start_jaeger


def core(backend: str = "postgres"):
    jaeger, ui_url = start_jaeger()
    try:
        # Setup that DB
        with db(number=0, backend_type=backend):
            print("Starting webapp")
            uvicorn.run("lightgest.api:app", reload=True)
    finally:
        jaeger.stop()


def main():
    from argparse import ArgumentParser

    parser = ArgumentParser(description="Run an ephemeral server.")

    parser.add_argument(
        "-b",
        "--backend",
        choices=["postgres", "timescale", "parquet"],
        default="postgres",
    )

    args = parser.parse_args()

    core(args.backend)


if __name__ == "__main__":
    main()

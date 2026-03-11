"""
Run an ephemeral server, alongside an ephemeral lightcurve server.
"""

import uvicorn
from lightcurvedb.cli.ephemeral import core as db


def core(number: int = 16, backend: str = "postgres"):
    # Setup that DB
    with db(number=number, probability_of_flare=0.9, backend=backend):
        print("Starting webapp")

        uvicorn.run("lightserve.api:app", reload=True)


def main():
    from argparse import ArgumentParser

    parser = ArgumentParser(description="Run an ephemeral server.")
    parser.add_argument(
        "-n",
        "--number",
        type=int,
        default=16,
        help="Number of objects to create in the database.",
    )
    parser.add_argument(
        "-b",
        "--backend",
        choices=["postgres", "timescale", "parquet"],
        default="postgres"
    )

    args = parser.parse_args()
    core(args.number, args.backend)


if __name__ == "__main__":
    main()

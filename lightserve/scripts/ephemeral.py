"""
Run an ephemeral server, alongside an ephemeral lightcurve server.
"""

import multiprocessing as mp

import uvicorn
from lightcurvedb.cli.ephemeral import core as db

from lightserve.telemetry import start_jaeger


def run_server(app: str, port: int):
    uvicorn.run(app, port=port, log_level="info", reload=True)


def make_process(app: str, port: int):
    p = mp.Process(target=run_server, args=(app, port))
    p.start()

    return p


def setup_servers(run_ingest: bool = False):
    processes = [make_process("lightserve.api:app", 8000)]

    if run_ingest:
        processes.append(make_process("lightgest.api:app", 8001))

    for p in processes:
        p.join()


def core(number: int = 16, backend: str = "postgres", run_ingest: bool = False):
    jaeger, ui_url = start_jaeger()
    try:
        # Setup that DB
        with db(number=number, probability_of_flare=0.9, backend_type=backend):
            print("Starting webapp")
            setup_servers(run_ingest)
    finally:
        jaeger.stop()


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
        default="postgres",
    )
    parser.add_argument(
        "--run-ingest",
        action="store_true",
        help="If this parameter is provided, we also run the lightgest server.",
    )

    args = parser.parse_args()
    core(args.number, args.backend, args.run_ingest)


if __name__ == "__main__":
    main()

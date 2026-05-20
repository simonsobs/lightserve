"""
Run an ephemeral server, alongside an ephemeral lightcurve server.
"""

import multiprocessing as mp

import uvicorn
from lightcurvedb.cli.ephemeral import core as db

from lightserve.telemetry import start_jaeger


def run_server(app: str, port: int, workers: int):
    uvicorn.run(app, port=port, log_level="info", reload=workers == 1, workers=workers)


def make_process(app: str, port: int, workers: int):
    p = mp.Process(target=run_server, args=(app, port, workers))
    p.start()

    return p


def setup_servers(run_ingest: bool = False, workers: int = 1):
    processes = [make_process("lightserve.api:app", 8000, workers)]

    if run_ingest:
        processes.append(make_process("lightgest.api:app", 8001, workers))

    for p in processes:
        p.join()


def core(number: int = 16, backend: str = "postgres", run_ingest: bool = False, workers: int = 1):
    jaeger, ui_url, otlp_endpoint = start_jaeger()
    try:
        # Setup that DB
        with db(
            number=number,
            probability_of_flare=0.9,
            backend_type=backend,
        ):
            print("Starting webapp")
            setup_servers(run_ingest, workers)
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
    parser.add_argument(
        "-w",
        "--workers",
        type=int,
        default=1,
        help=(
            "Number of workers to use for the FastAPI servers. Note that using more than 1 worker "
            "will cause issues with the in-memory backend, and may cause issues with the parquet "
            "backend as well. Use with caution. Reloading is disabled when workers > 1."
        ),
    )

    args = parser.parse_args()
    core(args.number, args.backend, args.run_ingest, args.workers)


if __name__ == "__main__":
    main()

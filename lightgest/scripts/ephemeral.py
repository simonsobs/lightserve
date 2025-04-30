"""
Run an ephemeral server, alongside an ephemeral lightcurve server.
"""

import uvicorn
from lightcurvedb.cli.ephemeral import core as db


def core():
    # Setup that DB
    with db(number=0):
        print("Starting webapp")

        uvicorn.run("lightgest.api:app", reload=True)


def main():
    from argparse import ArgumentParser

    parser = ArgumentParser(description="Run an ephemeral server.")
    _ = parser.parse_args()
    core()


if __name__ == "__main__":
    main()

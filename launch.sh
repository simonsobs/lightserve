#!/bin/bash -L

lightcurvedb-setup

uvicorn lightserve.api:app --port 8000 --host 0.0.0.0 --root-path /egress &
uvicorn lightgest.api:app --port 8001 --host 0.0.0.0 --root-path /ingest &

wait
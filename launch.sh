#!/bin/bash -L

lightcurvedb-setup

uvicorn lightserve.api:app --port 8000 &
uvicorn lightgest.api:app --port 8001 &

wait
FROM python:3.11

COPY ./lightserve lightserve/lightserve
COPY ./pyproject.toml lightserve/pyproject.toml
WORKDIR /lightserve
RUN pip install setuptools wheel
RUN pip install --no-build-isolation ".[dev,ephemeral]"
WORKDIR /

CMD ["uvicorn", "--number", "1"]
FROM python:3.13

COPY ./launch.sh launch.sh

RUN pip install setuptools wheel build

RUN git clone https://github.com/simonsobs/soauth /soauth
WORKDIR /soauth
RUN python3 -m pip install .

RUN git clone https://github.com/simonsobs/lightcurvedb /lightcurvedb
WORKDIR /lightcurvedb
RUN python3 -m pip install .

RUN mkdir /app
COPY pyproject.toml /app
COPY lightgest/ /app/lightgest/
COPY lightserve/ /app/lightserve/
WORKDIR /app
RUN pip install .[telemetry]

WORKDIR /

CMD ["bash", "launch.sh"]

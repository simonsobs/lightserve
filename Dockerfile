FROM python:3.11

COPY ./launch.sh launch.sh

COPY lightcurvedb*.whl /
COPY soauth*.whl /
COPY lightserve*.whl /

RUN pip install setuptools wheel
RUN pip install lightcurvedb*.whl
RUN pip install soauth*.whl
RUN pip install lightserve*.whl

CMD ["bash", "launch.sh"]
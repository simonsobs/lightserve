"""
OpenTelemetry tracing configuration shared by lightserve and lightgest.

Call :func:`configure_telemetry` once per process when telemetry is enabled.
The function is a no-op when the OTEL SDK packages are not installed, so the
rest of the application can import it unconditionally.

Call :func:`start_jaeger` from ephemeral scripts to launch a local
Jaeger all-in-one container and configure the environment automatically.
"""

import os

from fastapi import FastAPI
from pydantic import BaseModel


class OpenTelemetrySettings(BaseModel):
    service_name: str

    enable: bool = True
    stdout: bool = False
    endpoint: str = "localhost:4317"
    insecure: bool = True

    def resource(self):
        from opentelemetry.sdk.resources import Resource

        return Resource.create({"service.name": self.service_name})

    def tracer_provider(self):
        from opentelemetry.sdk.trace import TracerProvider

        return TracerProvider(resource=self.resource())

    def exported_provider(self):
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
            OTLPSpanExporter,
        )
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        provider = self.tracer_provider()

        if self.stdout:
            from opentelemetry.sdk.trace.export import ConsoleSpanExporter

            provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
        else:
            provider.add_span_processor(
                BatchSpanProcessor(
                    OTLPSpanExporter(
                        endpoint=self.endpoint,
                        insecure=self.insecure,
                    )
                )
            )

        return provider

    def trace(self):
        from opentelemetry import trace

        trace.set_tracer_provider(self.exported_provider())


def configure_telemetry(
    app: FastAPI,
    settings: OpenTelemetrySettings,
) -> None:
    """
    Configure OpenTelemetry tracing for the given FastAPI app based on the provided settings.
    """
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

    if settings.enable:
        FastAPIInstrumentor.instrument_app(app)
        settings.trace()


def start_jaeger():
    """Start a Jaeger all-in-one container and return ``(container, ui_url)``.

    Exports OTLP gRPC on the mapped port for 4317 and serves the UI on the
    mapped port for 16686.  Sets ``OTEL_EXPORTER_OTLP_ENDPOINT`` and
    ``ENABLE_TELEMETRY`` in the current process environment so that child
    uvicorn processes inherit them and pydantic-settings enables telemetry
    automatically.

    The caller is responsible for stopping the returned container.
    """
    from testcontainers.core.container import DockerContainer
    from testcontainers.core.waiting_utils import wait_for_logs

    container = (
        DockerContainer("cr.jaegertracing.io/jaegertracing/jaeger:2.18.0")
        .with_exposed_ports(4317, 16686, 4318, 5778, 9411)
        .with_env("COLLECTOR_OTLP_ENABLED", "true")
    )

    container.start()
    wait_for_logs(container, "Everything is ready.", timeout=60)

    otlp_port = container.get_exposed_port(4317)
    ui_port = container.get_exposed_port(16686)
    host = container.get_container_host_ip()

    otlp_endpoint = f"{host}:{otlp_port}"
    ui_url = f"http://{host}:{ui_port}"

    os.environ["TELEMETRY__ENDPOINT"] = otlp_endpoint
    os.environ["TELEMETRY__ENABLE"] = "true"

    print("----- JAEGER STARTED -----")
    print(f"Jaeger UI:  {ui_url}")
    print(f"OTLP gRPC:  {otlp_endpoint}")

    return container, ui_url, otlp_endpoint

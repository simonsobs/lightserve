"""
OpenTelemetry tracing configuration shared by lightserve and lightgest.

Call :func:`configure_telemetry` once per process when telemetry is enabled.
The function is a no-op when the OTEL SDK packages are not installed, so the
rest of the application can import it unconditionally.

Call :func:`start_jaeger` from ephemeral scripts to launch a local
Jaeger all-in-one container and configure the environment automatically.
"""

import os


def configure_telemetry(service_name: str, endpoint: str) -> None:
    """Configure OTLP gRPC tracing for *service_name*.

    Args:
        service_name: Resource name reported to the collector (e.g. ``"lightserve"``).
        endpoint: OTLP gRPC collector URL (e.g. ``"http://localhost:4317"``).

    Does nothing if ``opentelemetry-sdk`` is not installed.
    """
    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
            OTLPSpanExporter,
        )
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
    except ImportError:
        return

    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)
    exporter = OTLPSpanExporter(endpoint=endpoint)
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)


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

    otlp_endpoint = f"http://{host}:{otlp_port}"
    ui_url = f"http://{host}:{ui_port}"

    os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = otlp_endpoint
    os.environ["ENABLE_TELEMETRY"] = "true"

    print(f"\n  Jaeger UI:  {ui_url}")
    print(f"  OTLP gRPC:  {otlp_endpoint}\n")

    return container, ui_url

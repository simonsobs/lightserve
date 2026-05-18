"""
Settings for the project.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    origins: list[str] | None = ["*"]
    add_cors: bool = True
    "Settings for managng CORS middleware; useful for development."

    auth_system: str | None = None

    soauth_service_url: str | None = None
    soauth_app_id: str | None = None
    soauth_public_key: str | None = None
    soauth_base_url: str | None = None
    soauth_client_secret: str | None = None
    soauth_key_pair_type: str = "Ed25519"

    bearer_token_fixed: str | None = None

    enable_telemetry: bool = False
    "Enable OpenTelemetry tracing. Set ENABLE_TELEMETRY=true to activate."

    otel_exporter_otlp_endpoint: str = "http://localhost:4317"
    "OTLP gRPC collector endpoint. Reads OTEL_EXPORTER_OTLP_ENDPOINT from the environment."


settings = Settings()

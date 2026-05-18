"""
Settings for the project.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from lightserve.telemetry import OpenTelemetrySettings


class LightServeOtelSettings(OpenTelemetrySettings):
    service_name: str = Field(default="lightgest-api")
    "Service name to use for OpenTelemetry traces. Can be overridden with environment variable TELEMETRY__SERVICE_NAME."


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

    telemetry: LightServeOtelSettings
    "Settings for OpenTelemetry tracing. Set environment variables with prefix TELEMETRY__ to override defaults."

    model_config = SettingsConfigDict(env_nested_delimiter="__")


settings = Settings()

"""
Settings for the project.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    origins: list[str] | None = ["*"]
    add_cors: bool = True
    "Settings for managing CORS middleware; useful for development or running behind a proxy."

    feed_module: str = "i1"
    feed_frequency: int = 145
    "Band information to use for feeds"

    auth_system: str | None = None

    soauth_service_url: str | None = None
    soauth_app_id: str | None = None
    soauth_public_key: str | None = None
    soauth_base_url: str | None = None
    soauth_client_secret: str | None = None
    soauth_key_pair_type: str = "Ed25519"


settings = Settings()

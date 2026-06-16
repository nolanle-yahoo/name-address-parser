from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment / .env file."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Which validator implementation to use: mock | usps | smarty
    address_validator: str = "mock"

    # USPS Web Tools
    usps_user_id: str = ""

    # Smarty US Street API
    smarty_auth_id: str = ""
    smarty_auth_token: str = ""
    smarty_license: str = ""

    # Nominatim / OpenStreetMap (free, no key). User-Agent is required by policy.
    nominatim_url: str = "https://nominatim.openstreetmap.org"
    nominatim_user_agent: str = "name-address-parser/1.0 (contact: nolanle@gmail.com)"

    cors_origins: str = "http://localhost:5173,http://localhost:3000,http://localhost:8081,http://localhost:19006"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()

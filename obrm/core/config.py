"""Application configuration."""

from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    primary_provider: str = "yahoo"
    fallback_providers: tuple[str, ...] = ("bitstamp",)
    asset_symbol: str = "BTC-USD"
    update_frequency: str = "daily"
    display_date_format: str = "%d-%b-%Y"


def load_config() -> AppConfig:
    """Return the default OBRM configuration."""
    return AppConfig()

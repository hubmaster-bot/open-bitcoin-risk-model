"""Provider registry."""

from obrm.data.providers.base import MarketDataProvider
from obrm.data.providers.bitstamp import BitstampProvider
from obrm.data.providers.yahoo import YahooProvider


def build_provider(name: str) -> MarketDataProvider:
    """Create a provider by configuration name."""
    providers: dict[str, type[MarketDataProvider]] = {
        "yahoo": YahooProvider,
        "bitstamp": BitstampProvider,
    }

    try:
        provider_class = providers[name.lower()]
    except KeyError as exc:
        supported = ", ".join(sorted(providers))
        raise ValueError(
            f"Unknown provider '{name}'. Supported providers: {supported}"
        ) from exc

    return provider_class()

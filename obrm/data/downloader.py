from pathlib import Path

from obrm.data.providers.coingecko import CoinGeckoProvider
from obrm.data.storage import save_parquet
from obrm.data.validator import validate_price_data


def download_btc_history() -> Path:
    provider = CoinGeckoProvider()
    df = provider.get_btc_daily_price()

    validate_price_data(df)

    output_path = Path("data/processed/btc_daily_price.parquet")
    save_parquet(df, output_path)

    return output_path
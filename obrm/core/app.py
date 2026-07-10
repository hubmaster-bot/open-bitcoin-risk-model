"""Main application runner."""

import logging

from obrm.core.config import load_config
from obrm.core.logging_config import setup_logging
from obrm.core.version import APP_NAME, APP_SHORT_NAME, APP_VERSION
from obrm.data.downloader import download_btc_history


def run() -> None:
    setup_logging()
    logger = logging.getLogger(__name__)

    config = load_config()

    print("=" * 55)
    print(f" {APP_NAME} ({APP_SHORT_NAME})")
    print(f" Version {APP_VERSION}")
    print("=" * 55)
    print()

    logger.info("Configuration loaded: %s", config)
    logger.info("Downloading Bitcoin price history...")

    output_path = download_btc_history()

    logger.info("Download complete.")
    print()
    print("Complete.")
    print(f"Saved to: {output_path}")
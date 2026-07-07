from obrm.data.downloader import download_btc_history


def run() -> None:
    print("=" * 55)
    print(" Open Bitcoin Risk Model (OBRM)")
    print(" Version 0.2.0")
    print("=" * 55)
    print()

    print("Downloading Bitcoin price history...")
    output_path = download_btc_history()

    print()
    print("Complete.")
    print(f"Saved to: {output_path}")
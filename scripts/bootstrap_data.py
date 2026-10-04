#!/usr/bin/env python3
"""Download public NDVI release assets during a cloud build."""

import os
import shutil
import tempfile
import urllib.request
import zipfile
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")
DATA_DIR = Path(os.getenv("SOURCE_DATA_DIR", PROJECT_ROOT / "data" / "runtime"))
RASTER_URL = os.getenv(
    "RASTER_ARCHIVE_URL",
    "https://github.com/caophuthinh-cntt2/ndvi-ai-web/releases/latest/download/anh12thang.zip",
)
FORECAST_URL = os.getenv(
    "FORECAST_ARCHIVE_URL",
    "https://github.com/caophuthinh-cntt2/ndvi-ai-web/releases/latest/download/HCM_NDVI_Forecast_Maps_2026.zip",
)


def download(url: str, destination: Path):
    print(f"Downloading {destination.name}...")
    request = urllib.request.Request(url, headers={"User-Agent": "ndvi-ai-render-build/1.0"})
    with urllib.request.urlopen(request, timeout=600) as response, destination.open("wb") as output:
        shutil.copyfileobj(response, output)


def ensure_rasters():
    expected = [DATA_DIR / f"HCM_NDVI_{year}.tif" for year in range(2015, 2026)]
    if all(path.exists() for path in expected):
        return
    with tempfile.TemporaryDirectory() as temp_dir:
        archive_path = Path(temp_dir) / "annual.zip"
        extract_dir = Path(temp_dir) / "extract"
        download(RASTER_URL, archive_path)
        with zipfile.ZipFile(archive_path) as archive:
            archive.extractall(extract_dir)
        for year in range(2015, 2026):
            candidates = list(extract_dir.rglob(f"*{year}.tif"))
            if len(candidates) != 1:
                raise RuntimeError(f"Expected one GeoTIFF for {year}, found {len(candidates)}")
            shutil.copy2(candidates[0], DATA_DIR / f"HCM_NDVI_{year}.tif")


def ensure_forecast():
    destination = DATA_DIR / "HCM_NDVI_Forecast_Maps_2026.zip"
    if not destination.exists():
        download(FORECAST_URL, destination)


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    ensure_rasters()
    ensure_forecast()
    print(f"Deployment data ready in {DATA_DIR}")


if __name__ == "__main__":
    main()

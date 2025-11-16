"""
Data fetching module for GEFS and ECMWF IFS-ENS ensemble data.
Uses Dynamical.org's cloud-optimized Zarr datasets.
"""

import xarray as xr
import numpy as np
from typing import Tuple, Optional
from datetime import datetime, timedelta


class EnsembleDataFetcher:
    """Fetch and process ensemble forecast data from multiple sources."""

    GEFS_URL = "https://data.dynamical.org/noaa/gefs/forecast-35-day/latest.zarr"
    ECMWF_URL = "https://data.dynamical.org/ecmwf/ifs-ens/forecast-15-day-0-25-degree/latest.zarr"

    def __init__(self, email: Optional[str] = None):
        """
        Initialize the data fetcher.

        Args:
            email: Optional email for usage tracking
        """
        self.email = email or "[email protected]"

    def fetch_gefs(self,
                   lat_bounds: Tuple[float, float],
                   lon_bounds: Tuple[float, float],
                   max_lead_hours: int = 240) -> xr.Dataset:
        """
        Fetch GEFS ensemble data.

        Args:
            lat_bounds: (min_lat, max_lat) in degrees
            lon_bounds: (min_lon, max_lon) in degrees (0-360 or -180 to 180)
            max_lead_hours: Maximum forecast lead time in hours

        Returns:
            xr.Dataset with GEFS ensemble data
        """
        print(f"Fetching GEFS data (31 members)...")
        url = f"{self.GEFS_URL}?email={self.email}"

        ds = xr.open_zarr(url, chunks=None)

        # Select region and time range
        # Convert longitude if needed
        if lon_bounds[0] < 0:
            lon_bounds = (lon_bounds[0] % 360, lon_bounds[1] % 360)

        ds_subset = ds.sel(
            latitude=slice(lat_bounds[1], lat_bounds[0]),  # Note: descending
            longitude=slice(lon_bounds[0], lon_bounds[1]),
            lead_time=slice(0, max_lead_hours)
        )

        # Get latest init time
        latest_init = ds_subset.init_time.max().values
        ds_subset = ds_subset.sel(init_time=latest_init)

        print(f"  Loaded GEFS init time: {latest_init}")
        print(f"  Members: {len(ds_subset.ensemble_member)}")
        print(f"  Lead times: {len(ds_subset.lead_time)}")

        return ds_subset

    def fetch_ecmwf(self,
                    lat_bounds: Tuple[float, float],
                    lon_bounds: Tuple[float, float],
                    max_lead_hours: int = 240) -> xr.Dataset:
        """
        Fetch ECMWF IFS-ENS ensemble data.

        Args:
            lat_bounds: (min_lat, max_lat) in degrees
            lon_bounds: (min_lon, max_lon) in degrees (0-360 or -180 to 180)
            max_lead_hours: Maximum forecast lead time in hours

        Returns:
            xr.Dataset with ECMWF ensemble data
        """
        print(f"Fetching ECMWF IFS-ENS data (51 members)...")
        url = f"{self.ECMWF_URL}?email={self.email}"

        ds = xr.open_zarr(url, chunks=None)

        # Convert longitude if needed
        if lon_bounds[0] < 0:
            lon_bounds = (lon_bounds[0] % 360, lon_bounds[1] % 360)

        ds_subset = ds.sel(
            latitude=slice(lat_bounds[1], lat_bounds[0]),
            longitude=slice(lon_bounds[0], lon_bounds[1]),
            lead_time=slice(0, max_lead_hours)
        )

        # Get latest init time
        latest_init = ds_subset.init_time.max().values
        ds_subset = ds_subset.sel(init_time=latest_init)

        print(f"  Loaded ECMWF init time: {latest_init}")
        print(f"  Members: {len(ds_subset.ensemble_member)}")
        print(f"  Lead times: {len(ds_subset.lead_time)}")

        return ds_subset

    def fetch_all(self,
                  lat_bounds: Tuple[float, float],
                  lon_bounds: Tuple[float, float],
                  max_lead_hours: int = 240) -> Tuple[xr.Dataset, xr.Dataset]:
        """
        Fetch both GEFS and ECMWF ensemble data.

        Args:
            lat_bounds: (min_lat, max_lat) in degrees
            lon_bounds: (min_lon, max_lon) in degrees
            max_lead_hours: Maximum forecast lead time in hours

        Returns:
            Tuple of (gefs_data, ecmwf_data)
        """
        gefs_data = self.fetch_gefs(lat_bounds, lon_bounds, max_lead_hours)
        ecmwf_data = self.fetch_ecmwf(lat_bounds, lon_bounds, max_lead_hours)

        print(f"\nTotal ensemble members: {len(gefs_data.ensemble_member) + len(ecmwf_data.ensemble_member)}")

        return gefs_data, ecmwf_data

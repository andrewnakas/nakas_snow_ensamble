#!/usr/bin/env python3
"""
Quick test to verify Dynamical.org data is accessible.
"""

import sys
import warnings
warnings.filterwarnings('ignore')

print("Testing data fetch from Dynamical.org...")
print("="*60)

try:
    import xarray as xr
    print("✓ xarray imported successfully")
except ImportError as e:
    print(f"✗ Failed to import xarray: {e}")
    sys.exit(1)

# Test GEFS
print("\n1. Testing GEFS data access...")
try:
    gefs_url = "https://data.dynamical.org/noaa/gefs/forecast-35-day/[email protected]"
    print(f"   URL: {gefs_url}")

    ds = xr.open_zarr(gefs_url, chunks=None)
    print(f"   ✓ GEFS data accessible!")
    print(f"   - Init times: {len(ds.init_time)}")
    print(f"   - Latest: {ds.init_time.max().values}")
    print(f"   - Ensemble members: {len(ds.ensemble_member)}")
    print(f"   - Variables: {list(ds.data_vars)[:5]}...")
except Exception as e:
    print(f"   ✗ GEFS fetch failed: {e}")
    print(f"   This might be normal if the dataset isn't fully available yet")

# Test ECMWF
print("\n2. Testing ECMWF IFS-ENS data access...")
try:
    ecmwf_url = "https://data.dynamical.org/ecmwf/ifs-ens/forecast-15-day-0-25-degree/[email protected]"
    print(f"   URL: {ecmwf_url}")

    ds = xr.open_zarr(ecmwf_url, chunks=None)
    print(f"   ✓ ECMWF data accessible!")
    print(f"   - Init times: {len(ds.init_time)}")
    print(f"   - Latest: {ds.init_time.max().values}")
    print(f"   - Ensemble members: {len(ds.ensemble_member)}")
    print(f"   - Variables: {list(ds.data_vars)[:5]}...")
except Exception as e:
    print(f"   ✗ ECMWF fetch failed: {e}")
    print(f"   This might be normal if the dataset isn't fully available yet")

print("\n" + "="*60)
print("Test complete!")
print("\nIf both datasets are accessible, you can generate forecasts.")
print("If not, the datasets may still be in development at Dynamical.org")
print("="*60)

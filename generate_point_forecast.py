#!/usr/bin/env python3
"""
Generate a point forecast for a specific location.
This can be called interactively or via API.
"""

import argparse
import json
from datetime import datetime
import xarray as xr
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

from src.data_fetcher import EnsembleDataFetcher
from src.snow_calculator import SnowCalculator


def generate_point_forecast(lat, lon, max_hours=240, output_file=None):
    """
    Generate a forecast for a specific lat/lon point.

    Args:
        lat: Latitude in degrees
        lon: Longitude in degrees
        max_hours: Maximum forecast hours
        output_file: Optional output JSON file

    Returns:
        dict: Forecast data
    """
    print(f"Generating forecast for: {lat:.2f}°N, {abs(lon):.2f}°W")

    # Fetch data
    fetcher = EnsembleDataFetcher()

    # Use a small region around the point (±2 degrees)
    lat_bounds = (lat - 2, lat + 2)
    lon_bounds = (lon - 2, lon + 2)

    try:
        print("Fetching ensemble data...")
        gefs_data, ecmwf_data = fetcher.fetch_all(lat_bounds, lon_bounds, max_hours)

        # Extract variables
        gefs_precip = gefs_data['precipitation_surface']
        gefs_temp = gefs_data['temperature_2m']
        ecmwf_precip = ecmwf_data['precipitation_surface']
        ecmwf_temp = ecmwf_data['temperature_2m']

        # Calculate snow
        print("Calculating snowfall...")
        calculator = SnowCalculator()
        gefs_snow = calculator.process_ensemble_snow(gefs_precip, gefs_temp)
        ecmwf_snow = calculator.process_ensemble_snow(ecmwf_precip, ecmwf_temp)

        # Combine ensembles
        gefs_snow_renamed = gefs_snow.assign_coords(
            ensemble_member=('ensemble_member',
                            [f'GEFS_{i}' for i in range(len(gefs_snow.ensemble_member))])
        )
        ecmwf_snow_renamed = ecmwf_snow.assign_coords(
            ensemble_member=('ensemble_member',
                            [f'ECMWF_{i}' for i in range(len(ecmwf_snow.ensemble_member))])
        )
        combined_snow = xr.concat([gefs_snow_renamed, ecmwf_snow_renamed],
                                 dim='ensemble_member')

        # Select nearest point
        lon_360 = lon % 360
        point_snow = combined_snow.sel(
            latitude=lat,
            longitude=lon_360,
            method='nearest'
        )

        # Get actual selected coordinates
        actual_lat = float(point_snow.latitude.values)
        actual_lon = float(point_snow.longitude.values)

        print(f"Using grid point: {actual_lat:.2f}°N, {actual_lon:.2f}°E")

        # Calculate statistics
        lead_times = point_snow.lead_time.values
        cumulative_snow = point_snow.cumsum(dim='lead_time')

        forecast_data = {
            'location': {
                'requested_lat': lat,
                'requested_lon': lon,
                'grid_lat': actual_lat,
                'grid_lon': actual_lon
            },
            'metadata': {
                'init_time': str(gefs_data.init_time.values),
                'generation_time': datetime.utcnow().isoformat(),
                'num_members': len(combined_snow.ensemble_member),
                'max_hours': max_hours
            },
            'forecast': {
                'lead_times': lead_times.tolist(),
                'ensemble_members': []
            }
        }

        # Add each ensemble member
        for member_idx, member_name in enumerate(combined_snow.ensemble_member.values):
            member_cumulative = cumulative_snow.isel(ensemble_member=member_idx).values
            forecast_data['forecast']['ensemble_members'].append({
                'name': str(member_name),
                'cumulative_snow': member_cumulative.tolist()
            })

        # Calculate statistics
        mean_snow = cumulative_snow.mean(dim='ensemble_member').values
        p10_snow = cumulative_snow.quantile(0.1, dim='ensemble_member').values
        p90_snow = cumulative_snow.quantile(0.9, dim='ensemble_member').values
        median_snow = cumulative_snow.median(dim='ensemble_member').values

        forecast_data['forecast']['statistics'] = {
            'mean': mean_snow.tolist(),
            'median': median_snow.tolist(),
            'p10': p10_snow.tolist(),
            'p90': p90_snow.tolist(),
            'total_mean': float(mean_snow[-1]),
            'total_median': float(median_snow[-1]),
            'total_p10': float(p10_snow[-1]),
            'total_p90': float(p90_snow[-1])
        }

        # Save to file if requested
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(forecast_data, f, indent=2)
            print(f"Saved forecast to: {output_file}")

        return forecast_data

    except Exception as e:
        print(f"Error generating forecast: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate point forecast')
    parser.add_argument('--lat', type=float, required=True, help='Latitude')
    parser.add_argument('--lon', type=float, required=True, help='Longitude (negative for West)')
    parser.add_argument('--max-hours', type=int, default=240, help='Max forecast hours')
    parser.add_argument('--output', type=str, help='Output JSON file')

    args = parser.parse_args()

    result = generate_point_forecast(args.lat, args.lon, args.max_hours, args.output)

    if result:
        stats = result['forecast']['statistics']
        print(f"\n{'='*60}")
        print(f"10-Day Snow Forecast Summary")
        print(f"{'='*60}")
        print(f"Mean: {stats['total_mean']:.1f} mm")
        print(f"Median: {stats['total_median']:.1f} mm")
        print(f"10th percentile: {stats['total_p10']:.1f} mm")
        print(f"90th percentile: {stats['total_p90']:.1f} mm")
        print(f"{'='*60}")

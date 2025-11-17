#!/usr/bin/env python3
"""
Main script to generate snow ensemble forecasts.
Fetches data, calculates snow, and creates visualizations.

This script is designed to run automatically via GitHub Actions.
It downloads live GEFS and ECMWF IFS-ENS data from Dynamical.org.
"""

import os
import sys
import argparse
from datetime import datetime
import xarray as xr
import numpy as np
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

from src.data_fetcher import EnsembleDataFetcher
from src.snow_calculator import SnowCalculator
from src.visualizations import SnowEnsembleVisualizer


# Define regions of interest
REGIONS = {
    'western_us': {
        'name': 'Western United States',
        'lat_bounds': (32.0, 49.0),  # Southern to Northern border
        'lon_bounds': (-125.0, -102.0),  # West coast to Rockies
        'cities': [
            ('Salt Lake City, UT', 40.76, -111.89),
            ('Denver, CO', 39.74, -104.99),
            ('Seattle, WA', 47.61, -122.33),
            ('Boise, ID', 43.62, -116.21),
        ]
    },
    'intermountain_west': {
        'name': 'Intermountain West',
        'lat_bounds': (37.0, 45.0),
        'lon_bounds': (-114.0, -107.0),
        'cities': [
            ('Salt Lake City, UT', 40.76, -111.89),
            ('Park City, UT', 40.65, -111.50),
            ('Alta, UT', 40.59, -111.64),
            ('Brighton, UT', 40.60, -111.58),
        ]
    }
}


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description='Generate snow ensemble forecasts')
    parser.add_argument('--region', type=str, default='intermountain_west',
                       choices=list(REGIONS.keys()),
                       help='Region to generate forecast for')
    parser.add_argument('--max-hours', type=int, default=240,
                       help='Maximum forecast hours (default: 240 = 10 days)')
    parser.add_argument('--output-dir', type=str, default='docs',
                       help='Output directory for visualizations')
    parser.add_argument('--email', type=str, default='[email protected]',
                       help='Email for Dynamical.org usage tracking')

    args = parser.parse_args()

    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)

    # Get region configuration
    region_config = REGIONS[args.region]
    print(f"\n{'='*60}")
    print(f"❄️  Snow Ensemble Forecast Generator")
    print(f"{'='*60}")
    print(f"Region: {region_config['name']}")
    print(f"Maximum forecast hours: {args.max_hours}")
    print(f"Cities: {len(region_config['cities'])}")
    print(f"Lat range: {region_config['lat_bounds']}")
    print(f"Lon range: {region_config['lon_bounds']}")
    print(f"Output: {args.output_dir}")
    print(f"{'='*60}\n")

    # Step 1: Fetch ensemble data
    print("Step 1: Fetching ensemble data...")
    fetcher = EnsembleDataFetcher(email=args.email)

    try:
        gefs_data, ecmwf_data = fetcher.fetch_all(
            lat_bounds=region_config['lat_bounds'],
            lon_bounds=region_config['lon_bounds'],
            max_lead_hours=args.max_hours
        )
    except Exception as e:
        print(f"Error fetching data: {e}")
        print("\nNote: This script requires internet access to Dynamical.org")
        print("If you're seeing 404 errors, the datasets may not be available yet.")
        sys.exit(1)

    # Step 2: Extract precipitation, temperature, and wind data
    print("\nStep 2: Processing precipitation, temperature, and wind data...")

    # GEFS variables
    gefs_precip = gefs_data['precipitation_surface']  # Already in mm
    gefs_temp = gefs_data['temperature_2m']  # Kelvin

    # Try to get wind data (for MLR-based SLR)
    gefs_u_wind = gefs_data.get('u_component_of_wind_10m', None)
    gefs_v_wind = gefs_data.get('v_component_of_wind_10m', None)

    if gefs_u_wind is not None and gefs_v_wind is not None:
        print("  GEFS: Using wind data for MLR-based SLR")
    else:
        print("  GEFS: Wind data not available, using temperature-only MLR")

    # ECMWF variables
    ecmwf_precip = ecmwf_data['precipitation_surface']  # Already in mm
    ecmwf_temp = ecmwf_data['temperature_2m']  # Kelvin

    ecmwf_u_wind = ecmwf_data.get('u_component_of_wind_10m', None)
    ecmwf_v_wind = ecmwf_data.get('v_component_of_wind_10m', None)

    if ecmwf_u_wind is not None and ecmwf_v_wind is not None:
        print("  ECMWF: Using wind data for MLR-based SLR")
    else:
        print("  ECMWF: Wind data not available, using temperature-only MLR")

    # Step 3: Calculate snowfall using MLR (Utah method)
    print("\nStep 3: Calculating snowfall using MLR-based SLR (Utah method)...")
    calculator = SnowCalculator()

    gefs_snow = calculator.process_ensemble_snow(
        gefs_precip, gefs_temp, gefs_u_wind, gefs_v_wind
    )
    ecmwf_snow = calculator.process_ensemble_snow(
        ecmwf_precip, ecmwf_temp, ecmwf_u_wind, ecmwf_v_wind
    )

    # Combine ensembles
    print("\nStep 4: Combining ensemble members...")
    # Rename ensemble_member dimension to avoid conflicts
    gefs_snow_renamed = gefs_snow.assign_coords(
        ensemble_member=('ensemble_member',
                        [f'GEFS_{i}' for i in range(len(gefs_snow.ensemble_member))])
    )
    ecmwf_snow_renamed = ecmwf_snow.assign_coords(
        ensemble_member=('ensemble_member',
                        [f'ECMWF_{i}' for i in range(len(ecmwf_snow.ensemble_member))])
    )

    # Concatenate along ensemble dimension
    combined_snow = xr.concat([gefs_snow_renamed, ecmwf_snow_renamed],
                             dim='ensemble_member')

    print(f"  Total ensemble members: {len(combined_snow.ensemble_member)}")

    # Step 5: Calculate accumulation periods
    print("\nStep 5: Calculating accumulation periods...")

    # 10-day total (all lead times)
    snow_10day = combined_snow.sum(dim='lead_time')

    # 24-hour accumulations (cumulative)
    snow_24h = combined_snow.rolling(lead_time=8, min_periods=1).sum()
    snow_24h_max = snow_24h.max(dim='lead_time')

    # Step 6: Create visualizations
    print("\nStep 6: Creating visualizations...")
    visualizer = SnowEnsembleVisualizer()

    # Get initialization time for titles
    init_time = str(gefs_data.init_time.values)[:19]

    # Four-panel map: 10-day total
    visualizer.create_four_panel_map(
        snow_10day,
        f"10-Day Total Snowfall Forecast - {region_config['name']}\nInit: {init_time}",
        os.path.join(args.output_dir, 'snow_10day_total.png')
    )

    # Four-panel map: 24-hour maximum
    visualizer.create_four_panel_map(
        snow_24h_max,
        f"Maximum 24-Hour Snowfall - {region_config['name']}\nInit: {init_time}",
        os.path.join(args.output_dir, 'snow_24h_max.png')
    )

    # Ensemble spread map
    visualizer.create_ensemble_spread_map(
        snow_10day,
        f"10-Day Snowfall Ensemble Spread - {region_config['name']}\nInit: {init_time}",
        os.path.join(args.output_dir, 'snow_ensemble_spread.png')
    )

    # Violin plots for specific cities
    print("\nStep 7: Creating location-specific plume plots...")
    for city_name, lat, lon in region_config['cities']:
        try:
            # Convert longitude to 0-360 if needed
            lon_360 = lon % 360

            # Select nearest grid point
            city_snow = combined_snow.sel(
                latitude=lat,
                longitude=lon_360,
                method='nearest'
            )

            # Create safe filename
            safe_name = city_name.replace(',', '').replace(' ', '_').lower()

            visualizer.create_violin_plot(
                city_snow,
                city_name,
                os.path.join(args.output_dir, f'snow_plume_{safe_name}.png'),
                lat,
                abs(lon)
            )
        except Exception as e:
            print(f"  Warning: Could not create plot for {city_name}: {e}")

    # Step 8: Generate metadata
    print("\nStep 8: Generating forecast metadata...")
    metadata = {
        'generation_time': datetime.utcnow().isoformat(),
        'init_time': init_time,
        'region': region_config['name'],
        'max_hours': args.max_hours,
        'num_members': len(combined_snow.ensemble_member),
        'gefs_members': len(gefs_snow.ensemble_member),
        'ecmwf_members': len(ecmwf_snow.ensemble_member),
    }

    # Save metadata as JSON
    import json
    with open(os.path.join(args.output_dir, 'metadata.json'), 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"\n{'='*60}")
    print("✅ Forecast generation complete!")
    print(f"{'='*60}")
    print(f"Output directory: {args.output_dir}")
    print(f"Generated files:")
    for filename in os.listdir(args.output_dir):
        if filename.endswith('.png') or filename.endswith('.json'):
            filepath = os.path.join(args.output_dir, filename)
            filesize = os.path.getsize(filepath) / 1024  # KB
            print(f"  - {filename} ({filesize:.1f} KB)")
    print(f"{'='*60}\n")
    print("🌐 Forecast will be deployed to GitHub Pages automatically")
    print("📊 Check the Actions tab for deployment status\n")


if __name__ == '__main__':
    main()

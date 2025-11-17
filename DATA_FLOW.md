# Snow Ensemble Data Flow

## How We Fetch and Process Ensemble Data (Like Utah)

### Data Sources (Identical to Utah)
- **ECMWF IFS-ENS**: 51 ensemble members from Dynamical.org
- **NOAA GEFS**: 31 ensemble members from Dynamical.org
- **Total**: 82 combined ensemble members
- **Resolution**: 0.25° × 0.25° grid (~20km)
- **Forecast Period**: 240 hours (10 days) at 3-hour intervals

### Complete Workflow

#### Step 1: Data Fetching (`src/data_fetcher.py`)
```python
# Downloads from Dynamical.org cloud-optimized Zarr datasets
GEFS_URL = "https://data.dynamical.org/noaa/gefs/forecast-35-day/latest.zarr"
ECMWF_URL = "https://data.dynamical.org/ecmwf/ifs-ens/forecast-15-day-0-25-degree/latest.zarr"

# For each model:
1. Open Zarr dataset via xarray
2. Select geographic region (lat/lon bounds)
3. Select lead time range (0-240 hours)
4. Get latest initialization time
5. Download precipitation_surface and temperature_2m variables
```

**Result**: Two xarray Datasets containing:
- GEFS: 31 members × 81 time steps × lat × lon grid
- ECMWF: 51 members × 81 time steps × lat × lon grid

#### Step 2: Snow Calculation (`src/snow_calculator.py`)
```python
# Simplified temperature-based SLR (Utah uses MLR with wind)
For each ensemble member:
    For each grid point:
        temp_c = temperature_2m - 273.15

        if temp_c < -15°C:
            SLR = 15:1
        elif -15°C ≤ temp_c < -5°C:
            SLR = linear interpolation (15:1 to 12:1)
        elif -5°C ≤ temp_c < 0°C:
            SLR = linear interpolation (12:1 to 10:1)
        elif 0°C ≤ temp_c < 0.5°C:
            SLR = 10:1
        else:
            SLR = 0 (rain)

        snow_mm = precipitation_mm × SLR × (1 if temp < 0.5°C else 0)
```

**Result**: Snow accumulation arrays for each model:
- GEFS snow: 31 members × 81 time steps × lat × lon
- ECMWF snow: 51 members × 81 time steps × lat × lon

#### Step 3: Ensemble Combination
```python
# Rename ensemble members to avoid conflicts
gefs_members = ['GEFS_0', 'GEFS_1', ..., 'GEFS_30']  # 31 total
ecmwf_members = ['ECMWF_0', 'ECMWF_1', ..., 'ECMWF_50']  # 51 total

# Concatenate along ensemble dimension
combined_snow = xr.concat([gefs_snow, ecmwf_snow], dim='ensemble_member')
```

**Result**: Single array with 82 ensemble members × 81 time steps × lat × lon

#### Step 4: Regional Forecast (`generate_forecast.py`)
```python
# Calculate statistics across ensemble members
control = combined_snow[0]  # First member
mean = combined_snow.mean(dim='ensemble_member')
minimum = combined_snow.min(dim='ensemble_member')
maximum = combined_snow.max(dim='ensemble_member')
std_dev = combined_snow.std(dim='ensemble_member')

# Generate visualizations
- Four-panel maps (control, mean, min, max)
- Ensemble spread maps
- Violin plots for specific cities
```

**Outputs**:
- `docs/snow_10day_total.png`
- `docs/snow_24h_max.png`
- `docs/snow_ensemble_spread.png`
- `docs/snow_plume_*.png` (city plots)

#### Step 5: Point Forecasts (`generate_point_forecast.py`)
```python
# For each ski resort location (lat, lon):
1. Fetch data for ±2° region around point
2. Calculate snow for all 82 ensemble members
3. Select nearest grid point
4. Compute cumulative snow over time
5. Calculate statistics (mean, median, p10, p90)
6. Save to JSON file

# JSON structure:
{
    "location": {"lat": 40.59, "lon": -111.64},
    "metadata": {"init_time": "2025-01-15T12:00:00", "num_members": 82},
    "forecast": {
        "lead_times": [0, 3, 6, ..., 240],  # hours
        "statistics": {
            "mean": [0, 0.5, 1.2, ..., 45.3],  # cumulative mm
            "median": [0, 0.4, 1.0, ..., 42.1],
            "p10": [0, 0.1, 0.3, ..., 18.5],
            "p90": [0, 1.2, 2.8, ..., 68.9]
        },
        "ensemble_members": [
            {"name": "GEFS_0", "cumulative_snow": [...]},
            {"name": "GEFS_1", "cumulative_snow": [...]},
            ...
            {"name": "ECMWF_50", "cumulative_snow": [...]}
        ]
    }
}
```

**Outputs**:
- `docs/forecasts/alta_ut.json`
- `docs/forecasts/park_city_ut.json`
- `docs/forecasts/brighton_ut.json`
- `docs/forecasts/salt_lake_city_ut.json`

#### Step 6: Interactive Visualization (`docs/interactive.html`)
```javascript
// When user clicks a ski resort:
1. Fetch corresponding JSON file
2. Extract statistics array
3. Plot ensemble mean, median, and percentiles
4. Display forecast uncertainty via violin plot
5. Show total accumulation statistics
```

## Key Differences from Utah System

| Feature | Utah | Our System |
|---------|------|------------|
| SLR Method | MLR with temp + wind + climatology | Simplified temp-based |
| Downscaling | 800m using precip-altitude relationships | Native 0.25° grid |
| Data Source | Direct from NCEP/ECMWF | Via Dynamical.org Zarr |
| Automation | Unknown | GitHub Actions daily |
| Interactive Map | No | Yes (Leaflet + Chart.js) |

## Verification

The system fetches **REAL** ensemble data because:

1. **URLs are correct**: Points to Dynamical.org's live Zarr datasets
2. **Latest data**: Uses `.max()` to get most recent initialization
3. **All members**: Downloads full 31 GEFS + 51 ECMWF ensembles
4. **No simulation**: Zero fake/simulated data in the pipeline
5. **Traceable**: Every forecast includes `init_time` metadata

## Workflow Execution (GitHub Actions)

```yaml
1. Install dependencies (xarray, zarr, matplotlib, cartopy, metpy)
2. Run generate_forecast.py
   - Fetches GEFS from Dynamical.org
   - Fetches ECMWF from Dynamical.org
   - Processes all 82 members
   - Generates regional maps
3. Run generate_point_forecast.py (4 times)
   - Alta: 40.59°N, 111.64°W
   - Park City: 40.65°N, 111.50°W
   - Brighton: 40.60°N, 111.58°W
   - Salt Lake City: 40.76°N, 111.89°W
4. Commit forecast products to docs/
5. Deploy to GitHub Pages
```

## Data Flow Diagram

```
Dynamical.org GEFS (31 members)
         ↓
    [xarray.open_zarr]
         ↓
  Temperature + Precipitation
         ↓
    [Calculate SLR]
         ↓
    GEFS Snow Array
         ↓
         ↓──────────────────┐
         ↓                  ↓
Dynamical.org ECMWF (51)    ↓
         ↓                  ↓
    [xarray.open_zarr]      ↓
         ↓                  ↓
  Temperature + Precipitation ↓
         ↓                  ↓
    [Calculate SLR]         ↓
         ↓                  ↓
    ECMWF Snow Array        ↓
         ↓                  ↓
         └──[xr.concat]─────┘
                ↓
        82-Member Ensemble
                ↓
        ┌───────┴───────┐
        ↓               ↓
   Regional Maps    Point Forecasts
        ↓               ↓
    PNG files       JSON files
        ↓               ↓
    GitHub Pages ← Interactive Map
```

## Troubleshooting

If forecasts fail to generate:

1. **Check Dynamical.org availability**
   - Run: `python test_data_fetch.py`
   - Verifies both GEFS and ECMWF URLs are accessible

2. **Check workflow logs**
   - Actions tab → Latest run → Click on failed step
   - Look for xarray/zarr errors

3. **Verify data structure**
   - Ensure `precipitation_surface` and `temperature_2m` variables exist
   - Confirm `ensemble_member`, `lead_time`, `latitude`, `longitude` dimensions

4. **Check JSON output**
   - Point forecasts should have 82 ensemble members
   - Statistics arrays should have 81 time steps
   - All values should be non-negative

This system replicates Utah's ensemble approach while leveraging modern cloud-native data formats and automated deployment.

# ❄️ Snow Ensemble Forecast

An automated snow ensemble forecasting system that combines 82 ensemble members from NOAA GEFS and ECMWF IFS-ENS to provide probabilistic snowfall forecasts for the western United States.

## ⚡ Getting Started

**GitHub Actions is running now!** 🎉

1. **Enable GitHub Pages** (required): See [SETUP.md](SETUP.md) for step-by-step instructions
2. **Monitor the workflow**: Go to the [Actions tab](../../actions) to watch the forecast generation
3. **View your forecast**: Once complete, visit `https://andrewnakas.github.io/nakas_snow_ensamble/`

The workflow takes about **10-15 minutes** for the first run.

## 🎯 Features

- **82-Member Ensemble**: Combines 31 GEFS members + 51 ECMWF IFS-ENS members
- **High Resolution**: 0.25° (~20km) grid resolution
- **10-Day Forecasts**: Up to 240 hours of snowfall predictions
- **Multiple Visualizations**:
  - Four-panel maps (control, mean, min, max)
  - Ensemble spread maps showing forecast uncertainty
  - Violin/plume plots for specific locations
- **Automated Updates**: Daily forecasts via GitHub Actions
- **GitHub Pages**: Interactive web interface for viewing forecasts

## 🌟 Inspiration

This project is inspired by the [Utah Snow Ensemble](https://wasatchweatherweenies.blogspot.com/2024/09/the-utah-snow-ensemble.html) developed by weather researchers in Utah. It uses similar ensemble combination techniques and visualization approaches to provide probabilistic snow forecasts.

## 📊 Data Sources

- **NOAA GEFS**: Global Ensemble Forecast System via [Dynamical.org](https://dynamical.org/catalog/noaa-gefs-forecast-35-day/)
- **ECMWF IFS-ENS**: Integrated Forecasting System Ensemble via [Dynamical.org](https://dynamical.org/catalog/models/ifs-ens/)

All data is accessed through cloud-optimized Zarr datasets provided by Dynamical.org.

## 🚀 Quick Start

### Local Usage

1. **Clone the repository**:
   ```bash
   git clone https://github.com/andrewnakas/nakas_snow_ensamble.git
   cd nakas_snow_ensamble
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Generate a forecast**:
   ```bash
   python generate_forecast.py --region intermountain_west
   ```

4. **View results**:
   Open `docs/index.html` in your browser

### Available Regions

- `intermountain_west`: Utah, Idaho, and surrounding areas
- `western_us`: Entire western United States

## 🤖 GitHub Actions Automation

The repository includes a GitHub Actions workflow that:

1. **Runs daily at 12:00 UTC** (after model runs are typically available)
2. **Fetches latest ensemble data** from Dynamical.org
3. **Generates snow forecasts** and visualizations
4. **Deploys to GitHub Pages** automatically

### Manual Trigger

You can manually trigger a forecast generation:

1. Go to the **Actions** tab in your GitHub repository
2. Select **Generate Snow Ensemble Forecast**
3. Click **Run workflow**
4. Optionally select a different region

## 📈 Methodology

### Snow Calculation

The system uses a simplified temperature-based snow-to-liquid ratio (SLR) calculation:

- **Very cold (< -15°C)**: SLR ~15:1
- **Cold (-15 to -5°C)**: SLR ~12:1
- **Moderate (-5 to 0°C)**: SLR ~10:1
- **Warm (> 0°C)**: Rain (SLR = 0)

This is a simplification of the more complex multiple linear regression approach used by the Utah ensemble, which incorporates temperature, wind, and climatological relationships.

### Ensemble Processing

1. **Data Fetching**: Downloads latest GEFS and ECMWF IFS-ENS forecasts
2. **Snow Conversion**: Applies SLR to convert liquid precipitation to snow
3. **Ensemble Combination**: Merges all 82 members into a single ensemble
4. **Statistical Analysis**: Computes mean, min, max, spread, and percentiles
5. **Visualization**: Generates maps and location-specific plots

## 📁 Project Structure

```
nakas_snow_ensamble/
├── src/
│   ├── data_fetcher.py      # Fetch GEFS and ECMWF data
│   ├── snow_calculator.py   # Calculate snow from precipitation
│   └── visualizations.py    # Create maps and plots
├── docs/
│   └── index.html          # GitHub Pages interface
├── .github/
│   └── workflows/
│       └── generate-forecast.yml  # GitHub Actions workflow
├── generate_forecast.py    # Main script
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## ⚙️ Configuration

### Modify Regions

Edit the `REGIONS` dictionary in `generate_forecast.py` to add new regions or cities:

```python
REGIONS = {
    'your_region': {
        'name': 'Your Region Name',
        'lat_bounds': (min_lat, max_lat),
        'lon_bounds': (min_lon, max_lon),
        'cities': [
            ('City Name', latitude, longitude),
            # Add more cities...
        ]
    }
}
```

### Adjust Forecast Parameters

- **Forecast hours**: Use `--max-hours` flag (default: 240)
- **Output directory**: Use `--output-dir` flag (default: docs)
- **Region**: Use `--region` flag

## 🔧 Requirements

- Python 3.11+
- xarray >= 2025.1.2
- zarr >= 3.0.8
- matplotlib >= 3.7.0
- cartopy >= 0.22.0
- metpy >= 1.5.0
- numpy, pandas, scipy, seaborn

## ⚠️ Limitations

- **Simplified SLR**: Uses temperature-based SLR instead of full multiple linear regression
- **Warm Nose Issues**: May struggle with complex temperature profiles aloft
- **Rain/Snow Mix**: Cannot reliably identify freezing rain or ice pellets
- **Data Availability**: Dependent on Dynamical.org data availability

**Always consult official National Weather Service forecasts for critical decisions.**

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- [ ] Implement full multiple linear regression SLR calculation
- [ ] Add wet-bulb temperature analysis for rain/snow boundary
- [ ] Include more regions and cities
- [ ] Add historical verification statistics
- [ ] Improve downscaling methods

## 📜 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- **Utah Snow Ensemble Team**: For the original methodology and inspiration
- **Dynamical.org**: For providing cloud-optimized ensemble forecast data
- **NOAA** and **ECMWF**: For the ensemble forecast models

## 📞 Contact

For questions or issues, please open an issue on GitHub.

---

**Note**: This is an experimental forecasting tool for educational and research purposes. Always rely on official National Weather Service forecasts for important decisions.

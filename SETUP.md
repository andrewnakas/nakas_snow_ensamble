# Setup Instructions

## Quick Start

The GitHub Actions workflow has been configured to run automatically. Here's how to get your snow ensemble forecast running:

### 1. Enable GitHub Pages

**Important**: You must enable GitHub Pages for the forecast website to work.

1. Go to your repository on GitHub: `https://github.com/andrewnakas/nakas_snow_ensamble`
2. Click **Settings** (top menu)
3. Click **Pages** (left sidebar)
4. Under "Build and deployment":
   - **Source**: Select "GitHub Actions"
5. Click **Save**

Your forecast site will be available at:
```
https://andrewnakas.github.io/nakas_snow_ensamble/
```

### 2. Monitor the First Run

The workflow will start automatically when you push changes. To monitor it:

1. Go to the **Actions** tab in your repository
2. Look for the "Generate Snow Ensemble Forecast" workflow
3. Click on the running workflow to see live logs
4. The workflow takes about 10-15 minutes for the first run

### 3. Check the Results

Once the workflow completes:

1. **View the website**: Go to `https://andrewnakas.github.io/nakas_snow_ensamble/`
2. **Download artifacts**: In the Actions tab, click on a completed run and download the "forecast-maps" artifact
3. **Check the code**: The workflow commits generated images to the `docs/` folder

## Workflow Triggers

The workflow runs in three scenarios:

### Automatic Daily Run
- **Time**: 12:00 UTC every day
- **Purpose**: Generate fresh forecasts with latest model data

### On Code Push
The workflow triggers when you push changes to:
- `src/**` (any Python module)
- `generate_forecast.py` (main script)
- `requirements.txt` (dependencies)
- `.github/workflows/generate-forecast.yml` (workflow file)

### Manual Trigger
1. Go to **Actions** tab
2. Click **Generate Snow Ensemble Forecast**
3. Click **Run workflow**
4. Select region (optional): `intermountain_west` or `western_us`
5. Click **Run workflow** button

## Troubleshooting

### Workflow Fails on First Run

**Common causes**:
1. **GitHub Pages not enabled**: See step 1 above
2. **Permissions issue**: Make sure Actions has write permissions:
   - Settings → Actions → General
   - Scroll to "Workflow permissions"
   - Select "Read and write permissions"
   - Check "Allow GitHub Actions to create and approve pull requests"
   - Click Save

3. **Data availability**: Dynamical.org datasets might be temporarily unavailable
   - Check the workflow logs for specific errors
   - The workflow will retry on the next scheduled run

### Images Not Showing on Website

1. Wait 2-3 minutes after workflow completes for Pages to deploy
2. Clear your browser cache
3. Check that images exist in the `docs/` folder on GitHub

### Want to See Logs?

Download the workflow artifact:
1. Actions tab → Click on a completed run
2. Scroll to "Artifacts" section
3. Download "forecast-maps"
4. Unzip and look at `forecast.log`

## Customization

### Add Your Own Cities

Edit `generate_forecast.py`:

```python
REGIONS = {
    'intermountain_west': {
        'name': 'Intermountain West',
        'lat_bounds': (37.0, 45.0),
        'lon_bounds': (-114.0, -107.0),
        'cities': [
            ('Salt Lake City, UT', 40.76, -111.89),
            ('Your City Name', latitude, longitude),  # Add here
        ]
    }
}
```

### Change Forecast Length

Edit the workflow file or run manually:
```bash
python generate_forecast.py --max-hours 360  # 15 days instead of 10
```

### Change Update Schedule

Edit `.github/workflows/generate-forecast.yml`:
```yaml
schedule:
  - cron: '0 6,18 * * *'  # Run twice daily at 6am and 6pm UTC
```

## Data Sources

- **GEFS**: 31 ensemble members from NOAA
- **ECMWF IFS-ENS**: 51 ensemble members from ECMWF
- **Provider**: [Dynamical.org](https://dynamical.org)
- **Format**: Cloud-optimized Zarr
- **Resolution**: 0.25° (~20km)

## Next Steps

1. ✅ Enable GitHub Pages (see above)
2. ✅ Wait for first workflow run to complete
3. ✅ Visit your forecast website
4. ✅ Star the repository ⭐
5. ✅ Customize regions and cities
6. ✅ Share with friends!

## Support

- **Issues**: Open an issue on GitHub
- **Logs**: Check Actions tab for detailed error messages
- **Data**: Visit [Dynamical.org](https://dynamical.org) for data status

---

**Happy Forecasting!** ❄️

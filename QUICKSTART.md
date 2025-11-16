## 🚀 Quick Start Guide

### The forecast will populate automatically!

Your GitHub Actions workflow is configured and will run to fetch real data from Dynamical.org and generate forecasts.

## What's Happening Now

1. **✅ GitHub Actions Workflow is Set Up**
   - Triggers on code pushes
   - Runs daily at 12:00 UTC
   - Can be manually triggered

2. **✅ GitHub Pages is Live**
   - Your site: `https://andrewnakas.github.io/nakas_snow_ensamble/`
   - Currently showing placeholder message
   - Will update automatically when workflow runs

3. **✅ Interactive Map is Ready**
   - Visit: `https://andrewnakas.github.io/nakas_snow_ensamble/interactive.html`
   - Click anywhere for simulated forecasts
   - Real data version coming after first workflow run

## When Will I See Real Data?

### Option 1: Wait for Next Scheduled Run
- **Next automatic run**: Today at 12:00 UTC
- Workflow will fetch live GEFS and ECMWF data
- Generates all maps and forecasts
- Deploys to your website automatically

### Option 2: Trigger Manually (Recommended!)
Do this now to get your first forecast:

1. Go to: https://github.com/andrewnakas/nakas_snow_ensamble/actions
2. Click "Generate Snow Ensemble Forecast" (on the left)
3. Click "Run workflow" button (on the right)
4. Select region: "intermountain_west" (or "western_us")
5. Click the green "Run workflow" button

**Time to complete**: ~10-15 minutes

### Option 3: Run Locally (For Testing)

```bash
# Install dependencies
pip install -r requirements.txt

# Generate full forecast
python generate_forecast.py --region intermountain_west

# OR generate a single point forecast
python generate_point_forecast.py --lat 40.59 --lon -111.64
```

## What Gets Generated

When the workflow runs successfully, it creates:

### Regional Maps (in `docs/`)
- `snow_10day_total.png` - 10-day total snowfall (4 panels)
- `snow_24h_max.png` - Maximum 24-hour snowfall (4 panels)
- `snow_ensemble_spread.png` - Forecast uncertainty map

### City Forecasts (in `docs/`)
- `snow_plume_salt_lake_city_ut.png`
- `snow_plume_park_city_ut.png`
- `snow_plume_alta_ut.png`
- `snow_plume_brighton_ut.png`

### Metadata
- `docs/metadata.json` - Forecast details

All files are automatically committed and deployed to GitHub Pages.

## Check Workflow Status

### In Browser
Visit: https://github.com/andrewnakas/nakas_snow_ensamble/actions

Look for:
- 🟢 Green checkmark = Success!
- 🟡 Yellow circle = Running
- 🔴 Red X = Failed (check logs)

### From Command Line
```bash
./check_workflow_status.sh
```

## Troubleshooting

### Workflow Fails
**Common causes:**
1. Dynamical.org data temporarily unavailable
2. GitHub Actions permissions not set
3. Network timeout

**Solutions:**
- Check workflow logs for specific error
- Try manual trigger again in a few hours
- Verify Settings → Actions → Permissions = "Read and write"

### No Images on Website
- Wait 2-3 minutes after workflow completes
- Hard refresh browser (Ctrl+Shift+R or Cmd+Shift+R)
- Check `docs/` folder on GitHub - images should be there

### Want to Customize?
Edit `generate_forecast.py` to add your own:
- Regions
- Cities
- Forecast parameters

Then push changes - workflow will run automatically!

## The Data Sources

Your forecasts use:
- **31 GEFS ensemble members** from NOAA
- **51 ECMWF IFS-ENS members** from ECMWF
- **Total: 82 ensemble members**
- **Resolution**: 0.25° (~20km grid spacing)
- **Forecast length**: 240 hours (10 days)

All data comes from [Dynamical.org](https://dynamical.org) - free, cloud-optimized ensemble forecasts!

## Next Steps

1. ✅ **Trigger the workflow manually** (see Option 2 above)
2. ✅ **Wait 10-15 minutes** for it to complete
3. ✅ **Refresh your website** to see the forecasts
4. ✅ **Try the interactive map** with real data
5. ✅ **Share with friends** who love snow!

---

**Questions?** Open an issue on GitHub or check the logs in the Actions tab.

**Happy snow forecasting!** ❄️⛷️

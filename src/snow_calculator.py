"""
Snow calculation module for ensemble forecasts.
Implements snow-to-liquid ratio calculations and wet-bulb temperature methods.
"""

import numpy as np
import xarray as xr
from metpy.calc import wet_bulb_temperature
from metpy.units import units


class SnowCalculator:
    """Calculate snowfall from liquid precipitation using temperature-based methods."""

    @staticmethod
    def calculate_slr_simple(temp_2m_k: np.ndarray) -> np.ndarray:
        """
        Calculate snow-to-liquid ratio using a simplified temperature-based method.

        This is a simplified version. Utah uses a multiple linear regression
        with temperature and wind, but this provides a reasonable approximation.

        Based on typical SLR relationships:
        - Very cold (< -15°C): SLR ~15:1
        - Cold (-15 to -5°C): SLR ~12:1
        - Moderate (-5 to 0°C): SLR ~10:1
        - Warm (> 0°C): SLR ~0:1 (rain)

        Args:
            temp_2m_k: 2-meter temperature in Kelvin

        Returns:
            Snow-to-liquid ratio (dimensionless)
        """
        temp_c = temp_2m_k - 273.15

        # Initialize SLR array
        slr = np.zeros_like(temp_c)

        # Apply temperature-based SLR
        # Very cold: 15:1
        slr = np.where(temp_c < -15, 15.0, slr)
        # Cold: linear from 15:1 to 12:1
        slr = np.where((temp_c >= -15) & (temp_c < -5),
                       15.0 + (temp_c + 15) * (-3.0 / 10.0), slr)
        # Moderate: linear from 12:1 to 10:1
        slr = np.where((temp_c >= -5) & (temp_c < 0),
                       12.0 + (temp_c + 5) * (-2.0 / 5.0), slr)
        # Warm but freezing: 10:1
        slr = np.where((temp_c >= 0) & (temp_c < 0.5), 10.0, slr)
        # Above freezing: 0:1 (rain)
        slr = np.where(temp_c >= 0.5, 0.0, slr)

        return slr

    @staticmethod
    def calculate_wet_bulb_height(temp_k: np.ndarray,
                                   pressure_pa: np.ndarray,
                                   dewpoint_k: np.ndarray) -> np.ndarray:
        """
        Calculate wet-bulb temperature for rain/snow determination.

        Utah method uses wet-bulb 0.5°C as the boundary, with linear transition
        over 200m below that level.

        Args:
            temp_k: Temperature in Kelvin
            pressure_pa: Pressure in Pascals
            dewpoint_k: Dewpoint temperature in Kelvin

        Returns:
            Wet-bulb temperature in Kelvin
        """
        # Convert to MetPy units
        temp = temp_k * units.kelvin
        pressure = pressure_pa * units.pascal
        dewpoint = dewpoint_k * units.kelvin

        # Calculate wet-bulb temperature
        wb_temp = wet_bulb_temperature(pressure, temp, dewpoint)

        return wb_temp.magnitude

    @staticmethod
    def calculate_snow_from_precip(precip_mm: xr.DataArray,
                                   temp_2m_k: xr.DataArray,
                                   use_simple_slr: bool = True) -> xr.DataArray:
        """
        Calculate snowfall from liquid precipitation and temperature.

        Args:
            precip_mm: Precipitation in mm
            temp_2m_k: 2-meter temperature in Kelvin
            use_simple_slr: If True, use simplified SLR method

        Returns:
            Snowfall in mm (liquid equivalent converted to snow depth)
        """
        # Calculate SLR
        slr = SnowCalculator.calculate_slr_simple(temp_2m_k.values)

        # Calculate snow
        # Only count as snow where temperature is below freezing
        temp_c = temp_2m_k.values - 273.15
        snow_mask = temp_c < 0.5

        snow_mm = precip_mm.values * slr * snow_mask

        # Create xarray DataArray with same coordinates
        snow = xr.DataArray(
            snow_mm,
            coords=precip_mm.coords,
            dims=precip_mm.dims,
            attrs={'units': 'mm', 'long_name': 'Snowfall (liquid equivalent * SLR)'}
        )

        return snow

    @staticmethod
    def process_ensemble_snow(precip: xr.DataArray,
                              temp_2m: xr.DataArray) -> xr.DataArray:
        """
        Process entire ensemble for snow calculation.

        Args:
            precip: Precipitation DataArray with ensemble dimension
            temp_2m: 2-meter temperature DataArray with ensemble dimension

        Returns:
            Snow DataArray with ensemble dimension
        """
        print("Calculating snowfall from precipitation and temperature...")

        # Calculate snow for all ensemble members
        snow = SnowCalculator.calculate_snow_from_precip(precip, temp_2m)

        print(f"  Computed snow for {snow.sizes.get('ensemble_member', 1)} members")

        return snow

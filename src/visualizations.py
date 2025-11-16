"""
Visualization module for snow ensemble forecasts.
Creates four-panel maps and violin/plume plots similar to Utah's system.
"""

import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import xarray as xr
from matplotlib.gridspec import GridSpec
from typing import Tuple, Optional, List
import seaborn as sns
from datetime import datetime


class SnowEnsembleVisualizer:
    """Create visualizations for snow ensemble forecasts."""

    def __init__(self, figsize: Tuple[int, int] = (20, 16)):
        """
        Initialize visualizer.

        Args:
            figsize: Figure size for plots
        """
        self.figsize = figsize
        # Set style
        sns.set_style("whitegrid")
        plt.rcParams['font.size'] = 10

    def create_four_panel_map(self,
                              snow_data: xr.DataArray,
                              title: str,
                              output_path: str,
                              control_idx: int = 0) -> None:
        """
        Create four-panel map showing control, mean, min, and max forecasts.

        Args:
            snow_data: Snow data with (ensemble_member, lat, lon) dimensions
            title: Main title for the figure
            output_path: Path to save the figure
            control_idx: Index of control member (default 0)
        """
        print(f"Creating four-panel map: {title}")

        # Calculate statistics across ensemble members
        control = snow_data.isel(ensemble_member=control_idx)
        mean = snow_data.mean(dim='ensemble_member')
        minimum = snow_data.min(dim='ensemble_member')
        maximum = snow_data.max(dim='ensemble_member')

        # Create figure with 2x2 subplots
        fig = plt.figure(figsize=self.figsize)
        projection = ccrs.PlateCarree()

        panels = [
            (control, 'Control Member Forecast', 0),
            (mean, 'Ensemble Mean', 1),
            (minimum, 'Ensemble Minimum', 2),
            (maximum, 'Ensemble Maximum', 3)
        ]

        for data, subtitle, idx in panels:
            ax = fig.add_subplot(2, 2, idx + 1, projection=projection)

            # Add map features
            ax.add_feature(cfeature.STATES, linewidth=0.5, edgecolor='black')
            ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
            ax.add_feature(cfeature.BORDERS, linewidth=0.5)

            # Plot snow data
            levels = [0.1, 1, 2, 5, 10, 15, 20, 30, 40, 50, 75, 100, 150, 200]
            contourf = ax.contourf(
                data.longitude,
                data.latitude,
                data.values,
                levels=levels,
                cmap='YlGnBu',
                extend='max',
                transform=projection
            )

            # Add colorbar
            cbar = plt.colorbar(contourf, ax=ax, orientation='horizontal',
                               pad=0.05, shrink=0.8)
            cbar.set_label('Snowfall (mm liquid equivalent)', fontsize=9)

            # Set title
            ax.set_title(subtitle, fontsize=12, fontweight='bold')

            # Add gridlines
            gl = ax.gridlines(draw_labels=True, linewidth=0.5,
                            color='gray', alpha=0.5, linestyle='--')
            gl.top_labels = False
            gl.right_labels = False

        # Add main title
        fig.suptitle(title, fontsize=16, fontweight='bold', y=0.98)

        # Add timestamp
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
        fig.text(0.99, 0.01, f'Generated: {timestamp}',
                ha='right', va='bottom', fontsize=8, style='italic')

        plt.tight_layout(rect=[0, 0.02, 1, 0.97])
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()

        print(f"  Saved: {output_path}")

    def create_violin_plot(self,
                          snow_timeseries: xr.DataArray,
                          location_name: str,
                          output_path: str,
                          lat: float,
                          lon: float) -> None:
        """
        Create violin/plume plot showing ensemble uncertainty over time.

        Args:
            snow_timeseries: Snow data with (ensemble_member, lead_time) dimensions
            location_name: Name of the location
            output_path: Path to save the figure
            lat: Latitude of location
            lon: Longitude of location
        """
        print(f"Creating violin plot for {location_name}")

        fig, axes = plt.subplots(2, 1, figsize=(16, 10))

        # Prepare data for plotting
        lead_times = snow_timeseries.lead_time.values

        # Plot 1: Accumulated snowfall violin plot
        ax1 = axes[0]
        positions = lead_times / 24  # Convert hours to days

        # Calculate cumulative snow for each ensemble member
        cumulative_snow = snow_timeseries.cumsum(dim='lead_time')

        # Create violin plot
        violin_data = []
        for lt in lead_times:
            data_at_time = cumulative_snow.sel(lead_time=lt).values
            violin_data.append(data_at_time[~np.isnan(data_at_time)])

        parts = ax1.violinplot(violin_data, positions=positions,
                               widths=0.3, showmeans=True, showmedians=True)

        # Customize violin plot colors
        for pc in parts['bodies']:
            pc.set_facecolor('#8da0cb')
            pc.set_alpha(0.7)

        ax1.set_xlabel('Forecast Day', fontsize=12)
        ax1.set_ylabel('Accumulated Snowfall (mm)', fontsize=12)
        ax1.set_title(f'Cumulative Snowfall Ensemble Forecast - {location_name}',
                     fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)

        # Plot 2: Individual ensemble member traces
        ax2 = axes[1]

        # Plot each ensemble member
        for member_idx in range(len(cumulative_snow.ensemble_member)):
            member_data = cumulative_snow.isel(ensemble_member=member_idx)
            ax2.plot(positions, member_data.values,
                    alpha=0.3, linewidth=1, color='steelblue')

        # Plot ensemble mean
        mean_data = cumulative_snow.mean(dim='ensemble_member')
        ax2.plot(positions, mean_data.values,
                color='red', linewidth=3, label='Ensemble Mean', zorder=10)

        # Plot percentiles
        p10 = cumulative_snow.quantile(0.1, dim='ensemble_member')
        p90 = cumulative_snow.quantile(0.9, dim='ensemble_member')
        ax2.fill_between(positions, p10.values, p90.values,
                        alpha=0.2, color='gray', label='10th-90th Percentile')

        ax2.set_xlabel('Forecast Day', fontsize=12)
        ax2.set_ylabel('Accumulated Snowfall (mm)', fontsize=12)
        ax2.set_title(f'Ensemble Member Traces - {location_name}',
                     fontsize=14, fontweight='bold')
        ax2.legend(loc='upper left', fontsize=10)
        ax2.grid(True, alpha=0.3)

        # Add location info
        fig.text(0.5, 0.98, f'Location: {location_name} ({lat:.2f}°N, {lon:.2f}°W)',
                ha='center', va='top', fontsize=11, style='italic')

        # Add timestamp
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
        fig.text(0.99, 0.01, f'Generated: {timestamp}',
                ha='right', va='bottom', fontsize=8, style='italic')

        plt.tight_layout(rect=[0, 0.02, 1, 0.97])
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()

        print(f"  Saved: {output_path}")

    def create_ensemble_spread_map(self,
                                   snow_data: xr.DataArray,
                                   title: str,
                                   output_path: str) -> None:
        """
        Create map showing ensemble spread (standard deviation).

        Args:
            snow_data: Snow data with (ensemble_member, lat, lon) dimensions
            title: Main title for the figure
            output_path: Path to save the figure
        """
        print(f"Creating ensemble spread map: {title}")

        # Calculate standard deviation
        std = snow_data.std(dim='ensemble_member')

        # Create figure
        fig = plt.figure(figsize=(14, 10))
        projection = ccrs.PlateCarree()
        ax = fig.add_subplot(1, 1, 1, projection=projection)

        # Add map features
        ax.add_feature(cfeature.STATES, linewidth=0.5, edgecolor='black')
        ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
        ax.add_feature(cfeature.BORDERS, linewidth=0.5)

        # Plot ensemble spread
        levels = [0.1, 1, 5, 10, 20, 30, 40, 50, 75, 100]
        contourf = ax.contourf(
            std.longitude,
            std.latitude,
            std.values,
            levels=levels,
            cmap='RdYlBu_r',
            extend='max',
            transform=projection
        )

        # Add colorbar
        cbar = plt.colorbar(contourf, ax=ax, orientation='horizontal',
                           pad=0.05, shrink=0.8)
        cbar.set_label('Ensemble Spread (Standard Deviation, mm)', fontsize=10)

        # Set title
        ax.set_title(title, fontsize=14, fontweight='bold')

        # Add gridlines
        gl = ax.gridlines(draw_labels=True, linewidth=0.5,
                         color='gray', alpha=0.5, linestyle='--')
        gl.top_labels = False
        gl.right_labels = False

        # Add timestamp
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
        fig.text(0.99, 0.01, f'Generated: {timestamp}',
                ha='right', va='bottom', fontsize=8, style='italic')

        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()

        print(f"  Saved: {output_path}")

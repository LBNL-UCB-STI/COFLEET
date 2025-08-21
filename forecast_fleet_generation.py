#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 20 13:04:57 2025

@author: xiaodanxu
"""

from pandas import read_csv
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")

# customized modules
import configs as cf # load tool specs
from utils.rate_based_fleet_projection_moves import fleet_size_projection_moves
# load MOVES age projection generator
from utils.vmt_fraction_forecast_moves import moves_vmt_forecast
# load MOVES VMT projection generator
from utils.rate_based_fleet_projection_vius import fleet_size_projection_vius
# load VIUS age projection generator
from utils.vmt_fraction_forecast_vius import vius_vmt_forecast
# load VIUS VMT projection generator
from utils.compile_fleet_distribution_forecast import compile_vmt_forecast_by_fuel
# load VMT by fuel generator 




###### DEFINE PATH AND I-O FILES ###########
path_to_data = cf.proj_path
# please change this to the local directory where the data folder is located
os.chdir(path_to_data)

### load input files ###

# generic inputs
path_to_plot = cf.plot_dir
moves_definition_file = cf.moves_definition_file

###### RUN MOVES FLEET PROJECTION #######
moves_vmt_growth_rate_file = cf.moves_vmt_growth_rate_file
moves_turnover_rate_file = cf.moves_turnover_rate_file
moves_age_projection_file = cf.moves_age_projection_file
moves_future_vmt_by_stmy_file = cf.moves_future_vmt_by_stmy_file 
moves_future_vmt_check_file = cf.moves_future_vmt_check_file

vius_vmt_growth_rate_file = cf.vius_vmt_growth_rate_file
vius_base_vmt_by_stmy_file = cf.vius_base_vmt_by_stmy_file
vius_age_projection_file = cf.vius_age_projection_file
vius_rmar_file = cf.vius_rmar_file
vius_future_vmt_by_stmy_file = cf.vius_future_vmt_by_stmy_file
vius_future_vmt_check_file = cf.vius_future_vmt_check_file

list_of_avft_file = cf.list_of_avft_file
avft_scenario_lookup = cf.avft_scenario_lookup
vmt_scenario_lookup = cf.vmt_scenario_lookup
avft_by_scenario_file = cf.avft_by_scenario_file
joint_future_vmt_by_fuel_file = cf.joint_future_vmt_by_fuel_file



print('Generate MOVES future year fleet composition...')

print('Step 1 -- project MOVES age distribution by count...')

"""
Projects fleet size, age distribution, turnover rates, and VMT growth rates
for commercial vehicle types based on MOVES model definitions and baseline data.

Parameters
----------
moves_definition_file : str
    Path to an Excel file containing MOVES model reference data.  
moves_vmt_growth_rate_file : str
    Output CSV file path where calculated cumulative VMT growth rates by HPMS vehicle type
    will be saved.
moves_turnover_rate_file : str
    Output CSV file path where calculated annual turnover rates (scrappage and new sales)
    by source type will be saved.
moves_age_projection_file : str
    Output CSV file path where projected age distributions by source type and year will be saved.
path_to_plot : str
    Directory path where generated age distribution plots will be saved.
adjust_tail : bool, optional
    If ``True``, adjusts the tail of the age distribution (older vehicle bins) to maintain
    consistency across projection years. Defaults to ``False``.

"""
    
fleet_size_projection_moves(moves_definition_file, moves_vmt_growth_rate_file,
                            moves_turnover_rate_file, moves_age_projection_file,
                            path_to_plot, adjust_tail = False)

print('Step 2 -- Generate MOVES VMT fraction forecast...')

"""
Forecasts vehicle miles traveled (VMT) by source type, model year, and vehicle class
using MOVES growth rates, age projections, and relative mileage accumulation rates (RMAR).
Generates forecast outputs, summary checks, and growth rate plots for both MOVES and VIUS formats.

Parameters
----------
moves_definition_file : str
    Path to an Excel file containing MOVES reference data
moves_vmt_growth_rate_file : str
    Path to a CSV file containing projected HPMS-level VMT growth rates by year
    and vehicle type, used for scaling forecast VMT.
moves_turnover_rate_file : str
    Path to a CSV file containing MOVES vehicle turnover rates (currently unused in function).
moves_age_projection_file : str
    Path to a CSV file containing projected age distributions by MOVES source type and year.
moves_future_vmt_by_stmy_file : str
    Output CSV file path where forecasted VMT by source type and model year will be saved.
moves_future_vmt_check_file : str
    Output CSV file path where aggregated forecasted VMT by source type and year
    will be saved for validation purposes.
vius_vmt_growth_rate_file : str
    Output CSV file path where VMT growth rates will be saved in VIUS-compatible format.
path_to_plot : str
    Directory path where generated forecast plots.
"""

moves_vmt_forecast(moves_definition_file, moves_vmt_growth_rate_file,
                   moves_turnover_rate_file, moves_age_projection_file,
                   moves_future_vmt_by_stmy_file, moves_future_vmt_check_file, 
                   vius_vmt_growth_rate_file, path_to_plot)

print('Generate VIUS future year fleet composition...')

print('Step 1 -- project VIUS age distribution by count...')

"""
Projects future fleet size and age distribution for commercial vehicle types using
VIUS baseline data, MOVES turnover rates, and survival curves. Optionally adjusts
the tail of the age distribution for vehicles older than 30 years.

Parameters
----------
moves_definition_file : str
    Path to an Excel file containing MOVES reference data.
moves_turnover_rate_file : str
    Path to a CSV file containing MOVES vehicle turnover rates.
vius_base_vmt_by_stmy_file : str
    Path to a CSV file containing VIUS-derived baseline fleet mix by source type,
    model year, and age distribution. Used as the starting point for projections.
vius_age_projection_file : str
    Output CSV file path where the projected age distribution by source type and year
    will be saved.
path_to_plot : str
    Directory path where generated fleet age projection plots will be saved as PNG files.
adjust_tail : bool, optional
    If True, adjusts the tail of the age distribution (age > 30) to maintain
    proportionality with the baseline tail distribution. Default is False.
"""
fleet_size_projection_vius(moves_definition_file,
                           moves_turnover_rate_file, vius_base_vmt_by_stmy_file,
                           vius_age_projection_file, path_to_plot, adjust_tail = False)

print('Step 2 -- Generate VIUS VMT fraction forecast...')

"""
Forecasts Vehicle Miles Traveled (VMT) by source type, model year, and vehicle class
using VIUS-derived base-year VMT, MOVES age projections, and VIUS relative mileage
accumulation rates (RMAR). Produces forecasted VMT distributions, validation files,
and growth rate plots for commercial vehicle types.

Parameters
----------
moves_definition_file : str
    Path to an Excel file containing MOVES reference data.
vius_rmar_file : str
    Path to a CSV file containing VIUS-derived Relative Mileage Accumulation Rates (RMAR)
    by source type and age ID.
vius_vmt_growth_rate_file : str
    Path to a CSV file containing projected HPMS-level VMT growth rates in VIUS format,
    including cumulative growth factors by year and vehicle type.
vius_base_vmt_by_stmy_file : str
    Path to a CSV file containing VIUS-derived base-year VMT by source type and model year.
vius_age_projection_file : str
    Path to a CSV file containing projected age distributions for VIUS vehicle types
    by year and source type.
vius_future_vmt_by_stmy_file : str
    Output CSV file path where forecasted VIUS-based VMT by source type and model year
    will be saved.
vius_future_vmt_check_file : str
    Output CSV file path where aggregated forecasted VMT by source type and year
    will be saved for validation purposes.
path_to_plot : str
    Directory path where generated forecast plots (e.g., commercial vehicle growth factors)
    will be saved as PNG files.
"""
vius_vmt_forecast(moves_definition_file, vius_rmar_file, vius_vmt_growth_rate_file,
                  vius_base_vmt_by_stmy_file, vius_age_projection_file,
                  vius_future_vmt_by_stmy_file, vius_future_vmt_check_file,
                  path_to_plot)

print('Generate MOVES AND VIUS future year fleet composition by FUEL TYPE...')

"""
Compiles and merges Alternative Vehicle and Fuel Technology (AVFT) scenarios with 
VMT forecast scenarios to produce joint VMT-by-fuel-type projections for commercial vehicles. 
Generates scenario comparison plots and outputs combined datasets for further analysis.

Parameters
----------
moves_definition_file : str
    Path to an Excel file containing MOVES reference data.
list_of_avft_file : list of str
    List of file paths to CSV files containing AVFT scenario data for different 
    electrification or fuel adoption pathways.
avft_scenario_lookup : dict
    Dictionary mapping AVFT file names (basename only) to descriptive scenario names.
    Used to label scenarios in plots and outputs.
vmt_scenario_lookup : dict
    Dictionary mapping VMT distribution CSV file names to descriptive scenario names.
    Keys are file paths, values are scenario labels.
avft_by_scenario_file : str
    Output CSV file path where compiled AVFT scenario data (fuel mix by year, source type, and fuel type) will be saved.
joint_future_vmt_by_fuel_file : str
    Output CSV file path for VMT distributions by fuel type for all forecast years and scenarios.
path_to_plot : str
    Directory path where generated plots (e.g., electrification fraction trends, median vehicle age by scenario) will be saved as PNG files.
"""

compile_vmt_forecast_by_fuel(moves_definition_file, list_of_avft_file, avft_scenario_lookup,
                             vmt_scenario_lookup, avft_by_scenario_file,
                             joint_future_vmt_by_fuel_file, path_to_plot)
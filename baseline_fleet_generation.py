#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 20 11:43:23 2025

@author: xiaodanxu
"""

from pandas import read_csv
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings

# customized modules
import configs as cf # load tool specs
from utils.baseline_fleet_generation_from_moves import moves_baseline_fleet_generator
# load baseline MOVES fleet generator
from utils.baseline_fleet_generation_from_vius import vius_baseline_fleet_generator

warnings.filterwarnings("ignore")


###### DEFINE PATH AND I-O FILES ###########
path_to_data = cf.proj_path
# please change this to the local directory where the data folder is located
os.chdir(path_to_data)

### load input files ###

# generic inputs
path_to_plot = cf.plot_dir
moves_definition_file = cf.moves_definition_file

# MOVES baseline inputs
moves_vmt_by_stmy_file = cf.moves_base_vmt_by_stmy_file
moves_vmt_by_fuel_file = cf.moves_base_vmt_by_fuel_file
moves_base_vmt_check_file = cf.moves_base_vmt_check_file

# VIUS baseline inputs
vius_data_cleaned = cf.vius_data_cleaned
vius_base_vmt_by_stmy_file = cf.vius_base_vmt_by_stmy_file
vius_base_vmt_by_fuel_file = cf.vius_base_vmt_by_fuel_file
vius_rmar_file = cf.vius_rmar_file

###### RUN MOVES BASELINE FLEET GENERATION #######

"""
Parameters
----------
moves_definition_file : str
    (Required) Path to Excel file with MOVES definitions and data sheets.
path_to_plot : str
    (Required) Directory to save fleet mix plots.
moves_vmt_by_stmy_file : str
    (Required) Output CSV path for VMT fractions by source type & model year.
moves_vmt_by_fuel_file : str
    (Required) Output CSV path for VMT fractions by source type, model year & fuel type.
moves_base_vmt_check_file : str
    (Required) Output CSV path for base-year VMT totals (check file).
commercial_only : bool, optional
    (Default=True) Whether to restrict to commercial vehicle types only.
"""

print('Starting baseline fleet generation using MOVES4 default database...')
moves_baseline_fleet_generator(moves_definition_file, path_to_plot,
                               moves_vmt_by_stmy_file, moves_vmt_by_fuel_file,
                               moves_base_vmt_check_file, commercial_only = True)

###### RUN VIUS BASELINE FLEET GENERATION #######

"""
Parameters
----------
vius_data_cleaned : str
    Path to the cleaned VIUS dataset (CSV) containing vehicle-level records,
    including weights, annual mileage, vehicle class, fuel type, etc.
moves_definition_file : str
    Path to an Excel file with MOVES model reference data, specifically the
    `AGE_distribution` sheet used for age imputation.
moves_vmt_by_stmy_file : str
    Path to a MOVES-generated CSV containing VMT fractions by source type
    and model year, used for adjusting VIUS data for older vehicle ages.
vius_base_vmt_by_stmy_file : str
    Output CSV file where the computed VIUS-based VMT fractions by source type
    and model year will be saved.
vius_rmar_file : str
    Output CSV file where the computed VIUS-based Relative Mileage Accumulation
    Rates (RMAR) will be saved.
vius_base_vmt_by_fuel_file : str
    Output CSV file where the computed VIUS-based VMT fractions by source type,
    model year, and fuel type will be saved.
path_to_plot : str
    Directory path where generated plots (e.g., age distribution, VMT per truck,
    RMAR) will be saved as PNG files.
"""

print('Starting baseline fleet generation using cleaned 2021 US VIUS...')
vius_baseline_fleet_generator(vius_data_cleaned, moves_definition_file, 
                              moves_vmt_by_stmy_file, vius_base_vmt_by_stmy_file,
                              vius_rmar_file, vius_base_vmt_by_fuel_file, path_to_plot)
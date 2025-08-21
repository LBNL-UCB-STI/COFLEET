#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 20 11:08:27 2025

@author: xiaodanxu
"""

# this file define all the data paths

import os

### define project path ###
proj_path = '/Users/xiaodanxu/Documents/VIUS_Fleet_and_Emission'

### define data folders ###
input_dir = 'Input' # contains VIUS data (raw/cleaned) and emission rates 
param_dir = 'Parameter' # contains MOVES default values, AVFT inputs and processed MOVES fleet characteristics 
plot_dir = 'Plot' # contains all the visualizations
output_dir = 'Output' # contains base year and future year fleet compositions, as well as summary statistics 

### define list of files to be used ##


## list of files downloaded from external sources: ##

# raw input downloaded from BTS: https://www.census.gov/data/datasets/2021/econ/vius/2021-vius-puf.html
vius_data_raw = os.path.join(input_dir, 'vius_2021_puf.csv')

# data dictionary input downloaded from BTS: https://www.census.gov/data/datasets/2021/econ/vius/2021-vius-puf.html
vius_data_dictionary = os.path.join(input_dir, 
                                    'vius-2021-puf-data-dictionary_categorical_decoding.xlsx')

# MOVES4 default database for selected attributes
moves_definition_file = os.path.join(param_dir, 'moves_definition.xlsx')


##list of files generated from COFLEET: ##


# cleaned VIUS data
vius_data_cleaned = os.path.join(input_dir, 'vius_2021_com_crosswalk.csv')


# base year outputs
moves_base_vmt_by_stmy_file = os.path.join(output_dir, 'moves_VMT_fraction_base.csv')
moves_base_vmt_by_fuel_file = os.path.join(output_dir, 'moves_VMT_fraction_base_with_fuel.csv')
moves_base_vmt_check_file = os.path.join(output_dir, 'moves_VMT_check_base.csv')

vius_base_vmt_by_stmy_file = os.path.join(output_dir, 'vius_VMT_fraction_base.csv')
vius_base_vmt_by_fuel_file = os.path.join(output_dir,'vius_VMT_fraction_base_with_fuel.csv')

vius_rmar_file = os.path.join(output_dir,'vius_rmar.csv')

# future year outputs (no fuel)
moves_vmt_growth_rate_file = os.path.join(param_dir, 'turnover', 'moves_VMT_growth_rate.csv')
moves_turnover_rate_file = os.path.join(param_dir, 'turnover', 'pop_growth_and_turnover_rate.csv')
moves_age_projection_file = os.path.join(output_dir, 'age_distribution_moves_forecast.csv')
moves_future_vmt_by_stmy_file = os.path.join(param_dir, 'turnover', 'moves_VMT_fraction_future.csv')
moves_future_vmt_check_file = os.path.join(param_dir, 'turnover', 'moves_VMT_check_forecast.csv')

vius_vmt_growth_rate_file = os.path.join(param_dir, 'turnover', 'vius_vmt_growth_rate.csv')
vius_age_projection_file = os.path.join(output_dir, 'age_distribution_vius_forecast.csv')
vius_future_vmt_by_stmy_file = os.path.join(param_dir, 'turnover', 'vius_VMT_fraction_future.csv')
vius_future_vmt_check_file = os.path.join(param_dir, 'turnover', 'vius_VMT_check_forecast.csv')

# future year scenario specifications
avft_files = ['TDA_AVFT_HOP_highp2.csv', 'TDA_AVFT_HOP_highp6.csv', 'TDA_AVFT_HOP_highp10.csv',
                     'TDA_AVFT_Ref_highp2.csv', 'TDA_AVFT_Ref_highp6.csv', 'TDA_AVFT_Ref_highp10.csv']

avft_scenario_lookup = {'TDA_AVFT_HOP_highp2.csv': 'TITAN high oil, low elec', 
                   'TDA_AVFT_HOP_highp6.csv': 'TITAN high oil, mid elec',
                   'TDA_AVFT_HOP_highp10.csv': 'TITAN high oil, high elec',
                     'TDA_AVFT_Ref_highp2.csv': 'TITAN low oil, low elec', 
                     'TDA_AVFT_Ref_highp6.csv': 'TITAN low oil, mid elec',
                     'TDA_AVFT_Ref_highp10.csv': 'TITAN low oil, high elec'}

vmt_scenario_lookup = {moves_future_vmt_by_stmy_file: 'MOVES baseline',
                       vius_future_vmt_by_stmy_file: 'VIUS baseline'}
list_of_avft_file = [os.path.join(param_dir, 'turnover', file) for file in avft_files]

# future year outputs (with fuel)
avft_by_scenario_file = os.path.join(output_dir, 'avft_by_scenario.csv')

joint_future_vmt_by_fuel_file = \
    os.path.join(output_dir, 'vmt_distribution_by_scenario.csv') # final VMT distribution by all combinations
    
# emission rates
er_file_head = os.path.join(input_dir, 'Seattle_MOVES4_emission_rate_per_mile_')
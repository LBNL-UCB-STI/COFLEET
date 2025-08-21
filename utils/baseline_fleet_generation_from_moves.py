#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  6 11:28:36 2023

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

plt.style.use('ggplot')
sns.set(font_scale=1.2)  # larger font

def moves_baseline_fleet_generator(moves_definition_file, path_to_plot,
                                   moves_vmt_by_stmy_file, moves_vmt_by_fuel_file,
                                   moves_base_vmt_check_file, commercial_only = True):

    """
    Parameters
    ----------
    moves_definition_file : str
        (Required) Path to Excel file with MOVES definitions and data sheets.
    path_to_plot : str
        (Required) Directory to save fleet mix plot PNG.
    moves_vmt_by_stmy_file : str
        (Required) Output CSV path for VMT fractions by source type & model year.
    moves_vmt_by_fuel_file : str
        (Required) Output CSV path for VMT fractions by source type, model year & fuel type.
    moves_base_vmt_check_file : str
        (Required) Output CSV path for base-year VMT totals (check file).
    commercial_only : bool, optional
        (Default=True) Whether to restrict to commercial vehicle types only.
    """
    
    hpms_definition = pd.read_excel(moves_definition_file, 
                                    sheet_name = 'HPMS_definition')
    source_type_hpms = pd.read_excel(moves_definition_file, 
                                    sheet_name = 'source_type_HPMS')
    source_type_population = pd.read_excel(moves_definition_file, 
                                    sheet_name = 'source_type_population')
    
    hpms_vmt = pd.read_excel(moves_definition_file, 
                                    sheet_name = 'HPMS_VMT')
    age_distribution = pd.read_excel(moves_definition_file, 
                                    sheet_name = 'AGE_distribution')
    fuel_type_distribution = pd.read_excel(moves_definition_file, 
                                    sheet_name = 'fuel_type_distribution')
    fuel_type_definition = pd.read_excel(moves_definition_file, 
                                    sheet_name = 'fuel_type_definition')
    RMAR_factor = pd.read_excel(moves_definition_file, 
                                    sheet_name = 'RMAR')
    
    # <codecell>
    
    # generate VMT distribution by source type and model year
    analysis_year = 2021
    
    selected_type = [32, 52, 53, 61, 62]
    # commercial_only = True # 1 = yes, 0 = no
    
    # select vehicle composition from the analysis year
    source_type_population_year = \
        source_type_population.loc[source_type_population['yearID'] == analysis_year]
    source_type_population_year = source_type_population_year.drop(columns = 'yearID')
    hpms_vmt_year = hpms_vmt.loc[hpms_vmt['yearID'] == analysis_year]
    hpms_vmt_year = hpms_vmt_year[['HPMSVtypeID', 'HPMSBaseYearVMT']]
            
    age_distribution_year = \
        age_distribution.loc[age_distribution['yearID'] == analysis_year]
    age_distribution_year.loc[:, 'modelYearID'] = \
        analysis_year - age_distribution_year.loc[:, 'ageID'] 
    
    # generate VMT fraction by vehicle type and age
    fleet_mix_by_hpms = pd.merge(source_type_hpms, hpms_definition,
                                  on = 'HPMSVtypeID', how = 'left')
    fleet_mix_by_hpms = pd.merge(fleet_mix_by_hpms, hpms_vmt_year,
                                  on = 'HPMSVtypeID', how = 'left')
    fleet_mix_by_hpms = pd.merge(fleet_mix_by_hpms, source_type_population_year,
                                  on = 'sourceTypeID', how = 'left')
    fleet_mix_by_hpms = pd.merge(fleet_mix_by_hpms, age_distribution_year,
                                  on = 'sourceTypeID', how = 'left')
    
    fleet_mix_by_hpms.loc[:, 'population_by_year'] =  \
        fleet_mix_by_hpms.loc[:, 'sourceTypePopulation'] * \
            fleet_mix_by_hpms.loc[:, 'ageFraction']
            
         
    # <codecell>
    
    # calculate VMT fraction
    fleet_mix_by_hpms = pd.merge(fleet_mix_by_hpms, RMAR_factor,
                                  on = ['sourceTypeID', 'ageID'], 
                                  how = 'left') 
    print('base year total VMT:')
    print(hpms_vmt_year['HPMSBaseYearVMT'].sum())
    fleet_mix_by_hpms.loc[:, 'weighted_vmt_rate'] =  \
        fleet_mix_by_hpms.loc[:, 'population_by_year'] * \
            fleet_mix_by_hpms.loc[:, 'relativeMAR']
            
    fleet_mix_by_hpms.loc[:, 'weighted_vmt_by_hpms'] =  \
        fleet_mix_by_hpms.loc[:, 'weighted_vmt_rate'] / \
            fleet_mix_by_hpms.groupby('HPMSVtypeID')['weighted_vmt_rate'].transform('sum')
            
    fleet_mix_by_hpms.loc[:, 'weighted_vmt_by_hpms'] = \
        fleet_mix_by_hpms.loc[:, 'weighted_vmt_by_hpms']* \
            fleet_mix_by_hpms.loc[:, 'HPMSBaseYearVMT'] 
    
    print('base year total VMT after allocation:')
    print(fleet_mix_by_hpms['weighted_vmt_by_hpms'].sum())        
    moves_vmt_by_st = fleet_mix_by_hpms.groupby('sourceTypeName')['weighted_vmt_by_hpms'].sum()
    moves_vmt_by_st.to_csv(moves_base_vmt_check_file)   
    
    # <codecell>
    if commercial_only:
        fleet_mix_by_hpms = \
            fleet_mix_by_hpms.loc[fleet_mix_by_hpms['sourceTypeID'].isin(selected_type)]
    # calculate VMT fraction
    fleet_mix_by_hpms.loc[:, 'vmt_fraction'] =  \
        fleet_mix_by_hpms.loc[:, 'weighted_vmt_by_hpms'] / \
            fleet_mix_by_hpms.loc[:, 'weighted_vmt_by_hpms'].sum()
    fleet_mix_by_hpms = fleet_mix_by_hpms[['sourceTypeID', 
                                            'ageID',
                                            'HPMSVtypeID', 
                                            'sourceTypeName', 
                                            'HPMSVtypeName',
                                            'sourceTypePopulation',
                                            'ageFraction', 
                                            'modelYearID',
                                            'population_by_year',
                                            'weighted_vmt_by_hpms',
                                            'vmt_fraction']]
    # if commercial_only:
    fleet_mix_by_hpms.to_csv(moves_vmt_by_stmy_file, index = False)

    
    
    # plot MOVES commercial vehicle fleet mix
    sns.lineplot(data=fleet_mix_by_hpms, x="ageID", y="vmt_fraction", hue="sourceTypeName")
    plt.xlabel('Vehicle Age')
    plt.ylabel('VMT fraction')
    plt.legend(fontsize = 12)
    plt.title('MOVES VMT fraction by vehicle type and age')
    
    plt.savefig(os.path.join(path_to_plot, 'MOVES_commercial_vehicle_age_dist.png'), 
                bbox_inches = 'tight', dpi = 300)
    plt.show()
            
    # <codecell>
    # append fuel types
    
    '''
    MOVES specs:
    stmyFuelEngFraction - fraction of vehicles within the source type, model year, 
    fuel type combination which will be allocated to the given reg class
    
    stmyFraction - fraction of vehicles within the source type, model year combination 
    which are of the given reg class and fuel type
    
    fuelDensity - the density of the given fuel type in grams / gallon
    '''
    
    fuel_type_agg_frac = \
        fuel_type_distribution.groupby(['sourceTypeID', 'modelYearID', 'fuelTypeID'])[['stmyFraction']].sum()
    fuel_type_agg_frac = fuel_type_agg_frac.reset_index()    
    
    fuel_type_definition = fuel_type_definition[['fuelTypeID', 'fuelTypeDesc']]
    fuel_type_agg_frac = pd.merge(fuel_type_agg_frac,
                                  fuel_type_definition,
                                  on = 'fuelTypeID',
                                  how = 'left')
    
    fleet_mix_with_fuel = pd.merge(fleet_mix_by_hpms, fuel_type_agg_frac,
                                   on = ['sourceTypeID', 'modelYearID'],
                                   how = 'left')
    
    fleet_mix_with_fuel.loc[:, 'vmt_fraction'] = \
        fleet_mix_with_fuel.loc[:, 'vmt_fraction'] * fleet_mix_with_fuel.loc[:, 'stmyFraction']
        
    fleet_mix_with_fuel.loc[:, 'weighted_vmt_by_hpms'] = \
        fleet_mix_with_fuel.loc[:, 'weighted_vmt_by_hpms'] * fleet_mix_with_fuel.loc[:, 'stmyFraction']
    print(len(fleet_mix_with_fuel))
    print(fleet_mix_with_fuel.loc[:, 'vmt_fraction'].sum())
    
    # if commercial_only:
    fleet_mix_with_fuel.to_csv(moves_vmt_by_fuel_file, index = False)

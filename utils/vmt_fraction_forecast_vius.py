#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 24 13:36:21 2024

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

# path_to_data = '/Users/xiaodanxu/Library/CloudStorage/GoogleDrive-arielinseu@gmail.com/My Drive/BEAM-CORE/SynthFirm/Release/VIUS_Fleet_and_Emission' 
# # please change this to the local directory where the data folder is located
# os.chdir(path_to_data)


# # load input

# path_to_moves = 'Parameter'
# path_to_vius = 'Input'
# path_to_plot = 'Plot'
def vius_vmt_forecast(moves_definition_file, vius_rmar_file, vius_vmt_growth_rate_file,
                      vius_base_vmt_by_stmy_file, vius_age_projection_file,
                      vius_future_vmt_by_stmy_file, vius_future_vmt_check_file,
                      path_to_plot):
    
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
    hpms_definition = pd.read_excel(moves_definition_file, 
                                    sheet_name = 'HPMS_definition')
    source_type_hpms = pd.read_excel(moves_definition_file, 
                                    sheet_name = 'source_type_HPMS')
    RMAR_factor = read_csv(vius_rmar_file)
    
    vmt_growth_rate_for_vius = read_csv(vius_vmt_growth_rate_file) 
    
    hpms_vmt_from_vius = read_csv(vius_base_vmt_by_stmy_file)
    hpms_vmt_from_vius = pd.merge(hpms_vmt_from_vius, source_type_hpms,
                                         on = 'sourceTypeID', how = 'left')
    hpms_vmt_from_vius = pd.merge(hpms_vmt_from_vius, hpms_definition,
                                         on = 'HPMSVtypeID', how = 'left')
    
    age_distribution_forecast = read_csv(vius_age_projection_file)
    age_distribution_forecast = pd.merge(age_distribution_forecast, source_type_hpms,
                                         on = 'sourceTypeID', how = 'left')
    age_distribution_forecast = pd.merge(age_distribution_forecast, hpms_definition,
                                         on = 'HPMSVtypeID', how = 'left')
    print(age_distribution_forecast.columns)
    # baseline_year = 2021
    selected_type = [32, 52, 53, 61, 62]
    
    # <codecell>
    
    # generate forecasted VMT for VIUS
    vmt_rate_sel = vmt_growth_rate_for_vius[['yearID', 'HPMSVtypeID', 'HPMSVtypeName', 
                                             'Cumulative VMT growth rate']]
    vius_hpms_vmt = \
        hpms_vmt_from_vius.groupby(['HPMSVtypeID', 'HPMSVtypeName'])[['WGT_VMT']].sum()
    vius_hpms_vmt = vius_hpms_vmt.reset_index()   
    
    vius_hpms_vmt.rename(columns = {'WGT_VMT':'HPMSBaseYearVMT'}, 
                                  inplace = True)
    print('total base year VMT:')
    print(vius_hpms_vmt.HPMSBaseYearVMT.sum())
    vius_hpms_vmt_forecast = pd.merge(vius_hpms_vmt,
                                      vmt_rate_sel,
                                      on = 'HPMSVtypeID', how = 'left')
    
    vius_hpms_vmt_forecast.loc[:, 'HPMSBaseYearVMT'] *= \
        vius_hpms_vmt_forecast.loc[:, 'Cumulative VMT growth rate'] 
        
    # <codecell>
    
    # generate fleet mix for VIUS data
    fleet_mix_by_hpms = pd.merge(age_distribution_forecast, vius_hpms_vmt_forecast,
                                  on = ['HPMSVtypeID', 'yearID'], how = 'left')
    
    RMAR_factor = RMAR_factor[['sourceTypeID', 'ageID', 'relativeMAR']]
    
    fleet_mix_by_hpms = pd.merge(fleet_mix_by_hpms, RMAR_factor,
                                  on = ['sourceTypeID', 'ageID'], 
                                  how = 'left') 
    
    print('Total VMT before assignment:')
    print(vius_hpms_vmt_forecast['HPMSBaseYearVMT'].sum())
    
    fleet_mix_by_hpms.loc[:, 'weighted_vmt_rate'] =  \
        fleet_mix_by_hpms.loc[:, 'population_by_year'] * \
            fleet_mix_by_hpms.loc[:, 'relativeMAR']
            
    fleet_mix_by_hpms.loc[:, 'weighted_vmt_by_hpms'] =  \
        fleet_mix_by_hpms.loc[:, 'weighted_vmt_rate'] / \
            fleet_mix_by_hpms.groupby(['HPMSVtypeID', 'yearID'])['weighted_vmt_rate'].transform('sum')
            
    fleet_mix_by_hpms.loc[:, 'weighted_vmt_by_hpms'] = \
        fleet_mix_by_hpms.loc[:, 'weighted_vmt_by_hpms']* \
            fleet_mix_by_hpms.loc[:, 'HPMSBaseYearVMT'] 
    
    
    fleet_mix_by_hpms.loc[:, 'vmt_fraction'] =  \
        fleet_mix_by_hpms.loc[:, 'weighted_vmt_by_hpms'] / \
            fleet_mix_by_hpms.groupby(['yearID'])['weighted_vmt_by_hpms'].transform('sum')
    fleet_mix_by_hpms.to_csv(vius_future_vmt_by_stmy_file)         
    
    print('Total VMT after allocation:')
    print(fleet_mix_by_hpms['weighted_vmt_by_hpms'].sum())    
        
    vius_vmt_by_st = \
        fleet_mix_by_hpms.groupby(['yearID','HPMSVtypeID','HPMSVtypeName', 'sourceTypeID','sourceTypeName'])['weighted_vmt_by_hpms'].sum()
    vius_vmt_by_st = vius_vmt_by_st.reset_index()
    vius_vmt_by_st = vius_vmt_by_st.rename(columns = {'weighted_vmt_by_hpms':'annualVMT'})
    vius_vmt_by_st.to_csv(vius_future_vmt_check_file)
    
    
    # <codecell>
    sns.set(font_scale=1.4)  # larger font  
    sns.set_style("whitegrid")
    # calculate VMT growth factor from VIUS
    vius_vmt_by_st = vius_vmt_by_st.sort_values(by = 'yearID', ascending = True)
    vius_vmt_by_st.loc[:, 'PreYearVMT'] = \
        vius_vmt_by_st.groupby('sourceTypeID')['annualVMT'].shift(1)
    vius_vmt_by_st.loc[:, 'VMTGrowthFactor'] = vius_vmt_by_st.loc[:, 'annualVMT']/ \
        vius_vmt_by_st.loc[:, 'PreYearVMT']
    vius_vmt_by_st.loc[:, 'VMTGrowthFactor'].fillna(1, inplace = True)
    
    vius_vmt_by_st.loc[:, 'Cumulative VMT growth rate'] = \
        vius_vmt_by_st.groupby('sourceTypeID')['VMTGrowthFactor'].cumprod()
        
    com_vmt_rate = \
        vius_vmt_by_st.loc[vius_vmt_by_st['sourceTypeID'].isin(selected_type)]
    year_to_plot = [2021, 2030, 2040, 2050]
    com_vmt_rate = \
            com_vmt_rate.loc[com_vmt_rate['yearID'].isin(year_to_plot)]
    com_vmt_rate = com_vmt_rate.sort_values(by = 'sourceTypeID')    
    ax = sns.lineplot(data=com_vmt_rate, x="yearID", y="Cumulative VMT growth rate", 
                 hue = "sourceTypeName", style = "sourceTypeName")
    plt.legend(fontsize = 12)
    plt.ylim([1, 2])
    plt.savefig(os.path.join(path_to_plot, 'plot_forecast', 'com_growth_factor_vius.png'), dpi = 300,
                bbox_inches = 'tight')
    plt.show()
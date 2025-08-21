#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 11:48:14 2024

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

# # list_of_matrix_file = ['penn_2018_7_75_50.csv']
# path_to_moves = 'Parameter'
# path_to_vius = 'Input'
# path_to_plot = 'Plot'

def fleet_size_projection_vius(moves_definition_file, 
                               moves_turnover_rate_file, vius_base_vmt_by_stmy_file,
                               vius_age_projection_file, path_to_plot, adjust_tail = False):
    
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
    # hpms_definition = pd.read_excel(moves_definition_file, 
    #                                 sheet_name = 'HPMS_definition')
    source_type_hpms = pd.read_excel(moves_definition_file, 
                                    sheet_name = 'source_type_HPMS')
    RMAR_factor = pd.read_excel(moves_definition_file, 
                                    sheet_name = 'RMAR')
    
    pop_turnover_rate = read_csv(moves_turnover_rate_file)
    baseline_year = 2021
    selected_type = [32, 52, 53, 61, 62]
    
    fleet_mix_baseyear = read_csv(vius_base_vmt_by_stmy_file)
    # adjust_tail = False
    
    
    # post-process baseline fleet mix from VIUS
    fleet_mix_baseyear.rename(columns = {'TABWEIGHT': 'population_by_year'}, inplace = True)
    fleet_mix_baseyear.loc[:, 'sourceTypePopulation'] =\
        fleet_mix_baseyear.groupby(['sourceTypeID'])['population_by_year'].transform('sum')
    
    # collecting other data
    survival_rate = RMAR_factor[['ageID', 'sourceTypeID', 'survivalRate']]
    print(fleet_mix_baseyear.groupby('sourceTypeID')['population_by_year'].sum())

    
    # project population
    pop_turnover_rate_sel = pop_turnover_rate[['yearID', 'sourceTypeID', 'PopGrowthFactor', 'ageID', 
                                           'Cumulative growth rate', 'ageFraction']]
    source_type_population = fleet_mix_baseyear.groupby('sourceTypeID')[['population_by_year']].sum()
    source_type_population = source_type_population.reset_index()
    source_type_population.rename(columns = {'population_by_year':'sourceTypePopulation'}, 
                                  inplace = True)
    source_type_population_with_sale = pd.merge(source_type_population,
                                                pop_turnover_rate_sel,
                                                on = 'sourceTypeID', how = 'left')
    
    source_type_population_with_sale.loc[:, 'sourceTypePopulation'] *= \
        source_type_population_with_sale.loc[:, 'Cumulative growth rate']
        
    source_type_population_with_sale.loc[:, 'NewSale'] = \
        source_type_population_with_sale.loc[:, 'sourceTypePopulation'] * \
            source_type_population_with_sale.loc[:, 'ageFraction']
    
    source_type_population_with_sale = \
        source_type_population_with_sale.sort_values(by = 'yearID', ascending = True)
    source_type_population_with_sale.loc[:, 'sourceTypePopulationPre'] = \
        source_type_population_with_sale.groupby('sourceTypeID')['sourceTypePopulation'].shift(1)
    
    source_type_population_with_sale.loc[:, 'DeltaPop'] = \
        source_type_population_with_sale.loc[:, 'sourceTypePopulationPre'] * (source_type_population_with_sale.loc[:, 'PopGrowthFactor'] - 1)
    source_type_population_with_sale.loc[:, 'DeltaPop'].fillna(0, inplace = True)
    
    
    source_type_population_with_sale.loc[:, 'ScrappedVeh'] = \
        source_type_population_with_sale.loc[:, 'NewSale'] - \
            source_type_population_with_sale.loc[:, 'DeltaPop']
    
    source_type_population_with_sale = \
        source_type_population_with_sale.sort_values(by = 'yearID', ascending = True)
    source_type_population_with_sale.loc[:, 'ScrappedVeh'] = \
        source_type_population_with_sale.groupby('sourceTypeID')['ScrappedVeh'].shift(-1)
    source_type_population_with_sale.loc[:, 'ScrappedVeh'].fillna(0, inplace = True)
    
    
    
    # fleet projection
    fleet_mix_current_year = fleet_mix_baseyear[['sourceTypeID', 'population_by_year', 'yearID', 
                                                 'ageID', 'ageFraction', 'sourceTypePopulation']]
    
    fleet_mix_age_30_plus = fleet_mix_current_year.loc[fleet_mix_current_year['ageID'] == 30]
    fleet_mix_next_year = None
    
    end_year = source_type_population_with_sale.yearID.max()
    list_of_years = list(range(baseline_year, end_year))
    
    fleet_mix_by_year = fleet_mix_current_year # all year mix
    n_iter = 100
    for year in list_of_years:
        next_year = year + 1
        print('generate age distribution for year=' + str(next_year))
        
        fleet_total_by_year = \
            source_type_population_with_sale.loc[source_type_population_with_sale['yearID'] == year]
        fleet_total_by_year = \
            fleet_total_by_year.sort_values('sourceTypeID', ascending = True)
        
        fleet_mix_next_year = fleet_mix_current_year.copy()
        # re-append survival rate for every year, because after normalization it will be gone
        fleet_mix_next_year = pd.merge(fleet_mix_next_year,
                                      survival_rate,
                                      on = ['sourceTypeID', 'ageID'], how = 'left')
                
        fleet_mix_next_year.loc[:, 'veh_to_scrap'] = \
            fleet_mix_next_year.loc[:, 'population_by_year'] * \
                (1 - fleet_mix_next_year.loc[:, 'survivalRate'])
        scrappage_goal = fleet_total_by_year[['sourceTypeID', 'ScrappedVeh']]
        scrappage_est = fleet_mix_next_year.groupby('sourceTypeID')['veh_to_scrap'].sum()
        scrappage_est = scrappage_est.reset_index()
        print('scrappage vehicle compare before k-adjust (left - goal, right - estimate):')
        print(scrappage_goal.ScrappedVeh.sum(), scrappage_est.veh_to_scrap.sum())
        
        # calculate and apply k-adj factor
        k_factor = pd.merge(scrappage_goal, scrappage_est, 
                            on = 'sourceTypeID', how = 'outer')
        k_factor.loc[:, 'k_factor'] = \
            k_factor.loc[:, 'ScrappedVeh'] / k_factor.loc[:, 'veh_to_scrap']
        k_factor = k_factor[['sourceTypeID',  'k_factor']]
        fleet_mix_next_year = pd.merge(fleet_mix_next_year,
                                       k_factor, on = 'sourceTypeID', how = 'left')
        fleet_mix_next_year.loc[:, 'veh_to_scrap'] = \
            fleet_mix_next_year.loc[:, 'veh_to_scrap'] * fleet_mix_next_year.loc[:, 'k_factor']
    
        scrappage_est_2 = fleet_mix_next_year.groupby('sourceTypeID')['veh_to_scrap'].sum()
        scrappage_est_2 = scrappage_est_2.reset_index()
        print('scrappage vehicle compare after k-adjust (left - goal, right - estimate):')
        print(scrappage_goal.ScrappedVeh.sum(), scrappage_est_2.veh_to_scrap.sum())   
        
        # generate population after scrappage
        fleet_mix_next_year.loc[:, 'population_by_year'] = \
            fleet_mix_next_year.loc[:, 'population_by_year'] - fleet_mix_next_year.loc[:, 'veh_to_scrap']
        fleet_mix_next_year.drop(columns = ['veh_to_scrap', 'k_factor'], inplace = True)
                
        # increasing age id by 1
        fleet_mix_next_year.loc[:, 'ageID'] += 1
        fleet_mix_next_year.loc[:, 'yearID'] = next_year
        # append new sale
        next_year_new_sale = \
            source_type_population_with_sale.loc[source_type_population_with_sale['yearID'] == next_year]
        next_year_new_sale = \
        next_year_new_sale[['sourceTypeID', 'sourceTypePopulation', 'yearID', 'ageID',
                            'ageFraction', 'NewSale']]   
        next_year_new_sale.loc[:, 'survivalRate'] = 1
    
        next_year_new_sale.rename(columns = {'NewSale': 'population_by_year'}, inplace = True)
        fleet_mix_next_year = pd.concat([fleet_mix_next_year, next_year_new_sale])
        
        fleet_mix_next_year.loc[:, 'ageFraction'] = \
            fleet_mix_next_year.loc[:, 'population_by_year']/ \
            fleet_mix_next_year.groupby('sourceTypeID')['population_by_year'].transform('sum')
    
        # fleet_mix_next_year.loc[fleet_mix_next_year['ageID'] > 30, 'ageFraction'] = \
        #     fleet_mix_next_year.loc[fleet_mix_next_year['ageID'] > 30, 'ageFraction'].shift(1)
        fleet_mix_next_year.loc[fleet_mix_next_year['ageID'] > 30, 'ageID'] = 30
    
    
        # renormalize age distribution
        agg_var = ['sourceTypeID', 'yearID', 'ageID']
        fleet_mix_next_year = fleet_mix_next_year.groupby(agg_var)[['population_by_year']].sum()
        
        fleet_mix_next_year =fleet_mix_next_year.reset_index()
        
        
        fleet_mix_next_year.loc[:, 'sourceTypePopulation'] = \
            fleet_mix_next_year.groupby('sourceTypeID')['population_by_year'].transform('sum')
    
        fleet_mix_next_year.loc[:, 'ageFraction'] = \
            fleet_mix_next_year.loc[:, 'population_by_year'] / fleet_mix_next_year.loc[:, 'sourceTypePopulation']
        
        # fix the tail
        if adjust_tail:
            source_type_next_year = \
                fleet_mix_next_year.groupby(['sourceTypeID', 'yearID'])[['population_by_year']].sum()
            source_type_next_year = source_type_next_year.reset_index()
            source_type_next_year.rename(columns = {'population_by_year': 'sourceTypePopulation'}, 
                                          inplace = True)
            age_distribution_next_year = \
                fleet_mix_next_year[['sourceTypeID', 'ageID', 'ageFraction']]
            age_distribution_next_year = \
                age_distribution_next_year.loc[age_distribution_next_year['ageID'] <= 29]
            age_distribution_tail = fleet_mix_age_30_plus[['sourceTypeID', 'ageID',
                    'ageFraction']]
            age_distribution_next_year = pd.concat([age_distribution_next_year,
                                                    age_distribution_tail])
            
            # re-normalize the age distribution
            age_distribution_next_year.loc[:, 'adj_bin'] = 'yes'
            age_distribution_next_year.loc[age_distribution_next_year['ageID'].isin([0, 30]), 'adj_bin'] = 'no'
            tail_adj_factor = pd.pivot_table(age_distribution_next_year,
                                        columns = 'adj_bin',
                                        index = 'sourceTypeID', 
                                        values = 'ageFraction', aggfunc='sum')
            tail_adj_factor = tail_adj_factor.reset_index()
            
            tail_adj_factor.loc[:, 'adj_factor'] = \
                (1- tail_adj_factor.loc[:, 'no'])/ \
                    tail_adj_factor.loc[:, 'yes']
            tail_adj_factor = tail_adj_factor[['sourceTypeID', 'adj_factor']]
            age_distribution_next_year = pd.merge(age_distribution_next_year,
                                                  tail_adj_factor, on = 'sourceTypeID',
                                                  how = 'left')
            
            adj_index = (age_distribution_next_year['adj_bin'] == 'yes')
            age_distribution_next_year.loc[adj_index, 'ageFraction'] *= \
                age_distribution_next_year.loc[adj_index, 'adj_factor']
            # print(age_distribution_next_year.groupby('sourceTypeID')['ageFraction'].sum())
            age_distribution_next_year.drop(columns = ['adj_bin', 'adj_factor'], inplace = True)
            
            fleet_mix_next_year = pd.merge(source_type_next_year,
                                            age_distribution_next_year,
                                            on = 'sourceTypeID', how = 'left')
            fleet_mix_next_year.loc[:, 'population_by_year'] = \
                fleet_mix_next_year.loc[:, 'ageFraction'] * fleet_mix_next_year.loc[:, 'sourceTypePopulation']
            
        
        # prepare for next iteration
        fleet_mix_by_year = pd.concat([fleet_mix_by_year, fleet_mix_next_year])
        fleet_mix_current_year = fleet_mix_next_year.copy()
        # break
    fleet_mix_by_year.to_csv(vius_age_projection_file, index = False)
    
    # <codecell>
    sns.set_theme(style="whitegrid", font_scale=1.4)
    fleet_mix_by_year = pd.merge(fleet_mix_by_year, source_type_hpms,
                        on = 'sourceTypeID', how = 'left')
    # plot selected age distribution
    fleet_mix_to_plot = fleet_mix_by_year.loc[fleet_mix_by_year['sourceTypeID'].isin(selected_type)]
    fleet_mix_to_plot = fleet_mix_to_plot.loc[fleet_mix_to_plot['yearID'].isin([2021, 2030, 2040, 2050])]
    fleet_mix_to_plot = fleet_mix_to_plot.sort_values(by = 'sourceTypeID', ascending = True)
    ax = sns.relplot(data = fleet_mix_to_plot, x= 'ageID', y = 'ageFraction',
                hue = 'yearID', col='sourceTypeName', col_wrap = 3, kind = 'line', palette='Spectral')
    ax.set_titles("{col_name}")
    ax.set(ylim=(0, 0.2))
    plt.savefig(os.path.join(path_to_plot, 'plot_forecast', 'com_age_projection_vius.png'), dpi = 300,
                bbox_inches = 'tight')
    plt.show()





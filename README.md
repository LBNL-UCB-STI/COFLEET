
# COFLEET -- COmmercial Fleet Level Emissions and Energy Tracker
<p> <b> A commercial fleet generation and emission analysis tool  </b> </p>
<p> <b>Methodology deployed in the paper 'Improving Commercial Truck Fleet Composition in Emission Modeling using 2021 US VIUS Data' </b> </p>
<p> <b>Developers </b>: Xiaodan Xu, Ph.D.  (XiaodanXu@lbl.gov); Hung-Chia Yang (hcyang@lbl.gov) </p>
<p> <b>Contact</b>: Xiaodan Xu, Ph.D.  (XiaodanXu@lbl.gov) </p>
<p> <b>Updates (June 11, 2025)</b>: code uploaded, cleaned and data uploaded </p>

## Data preparation before start ##
* Dataset can be downloaded here: https://doi.org/10.5281/zenodo.15643435
* Check all the file directories and names under [configs](configs.py)

## Part 1 -- VIUS data cleaning and vehicle type assignment ##
* Corresponding to Section 2.1 of the paper
* Download VIUS PUF file and data dictionary from BTS website:https://www.census.gov/data/datasets/2021/econ/vius/2021-vius-puf.html
* Perform data cleaning and variable generation using [VIUS2021_commercial fleet generation_clean](VIUS2021_commercial fleet generation_clean.ipynb)
 * Writing VIUS data output with generated attributes: 'vius_2021_com_crosswalk.csv'


## Part 2 -- Baseline fleets generation ##
* <b>Run master code file: </b> [baseline_fleet_generation](baseline_fleet_generation.py)

### 2.1 -- MOVES baseline fleet generation ###
* Corresponding to Section 2.2.1 of the paper
* Call the MOVES fleet generation code [baseline_fleet_generation_from_moves](utils/baseline_fleet_generation_from_moves.py) 
* Producing MOVES fleet output file: 'moves_VMT_fraction_base_with_fuel.csv'

### 2.2 -- VIUS baseline fleet generation ###
* Corresponding to Section 2.2.2 of the paper
* Call the VIUS fleet generation code [baseline_fleet_generation_from_vius](utils/baseline_fleet_generation_from_vius.py)
* Relying on output from 2.1 for age distribution imputation (age > 23 yr)
* Producing VIUS fleet output file: 'vius_VMT_fraction_base_with_fuel.csv'

## Part 3 -- Fleet forecast ###
* <b>Run master code file: </b> [forecast_fleet_generation](forecast_fleet_generation.py)

### 3.1 -- rate-based fleet turnover ###
* Corresponding to Section 2.3.1 of the paper
  * Call vehicle population turnover from MOVES base fleet:       [rate_based_fleet_projection_moves](utils/rate_based_fleet_projection_moves.py)
    * Produce MOVES age distribution by year: 'age_distribution_moves_forecast.csv'
  * Call VMT composition from projected MOVES fleet:
  [vmt_fraction_forecast_moves](utils/vmt_fraction_forecast_moves.py)
  * Call vehicle population turnover from VIUS base fleet:
  [rate_based_fleet_projection_vius](utils/rate_based_fleet_projection_vius.py)
    * Produce VIUS age distribution by year: 'age_distribution_moves_forecast.csv'
  * Call VMT composition from projected VIUS fleet:
  [vmt_fraction_forecast_vius](utils/vmt_fraction_forecast_vius.py)


### 3.2 -- fuel mix generation ###
* Corresponding to Section 2.3.2 of the paper
* The raw TITAN results cannot be shared due to data restrictions. The AVFT (alternative vehicle fuel type) generation code can be accessed [AVFT_from_TDA](AVFT_from_TDA.py), and the results are available under the 'Parameter/turnover' folder under shared data (Note: TDA is the previous project name acronym for TITAN project)
* The scenario description can be found under file [opcost_sensitivity_analysis](parameters/opcost_sensitivity_analysis.csv)

* Call the VMT distribution generation by fuel, using AVFT results combined with VMT distributions from 3.1 above with script [compile_fleet_distribution_forecast](compile_fleet_distribution_forecast.py)
  * Produce output AVFT tables for all selected scenarios 'avft_by_scenario.csv'
  * Produce VMT distribution by fuel for all scenarios: 'vmt_distribution_by_scenario.csv'


## Part 4 -- Fleet composition comparison ###
* Corresponding to Section 3 of the paper
* The base year fleet compositions are compared under [vius_moves_fleet_comparison](vius_moves_fleet_comparison.ipynb)
* The future fleet results are generated in 3.2 above

## Part 5 -- Emission comparison ###
* Corresponding to Section 4 of the paper
* The base year emission results are calculated and compared under [compare_emission_baseyear](compare_emission_baseyear.py)
* The future year emission results are calculated and compared under [compare_emission_forecast](compare_emission_forecast.py)






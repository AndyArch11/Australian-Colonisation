"""
    Creates an animation covering the colonialisation of Australia and the impact on the Indigenous population
"""
__author__ = "Andrew Arch"
__copyright__ = "Copyright 2025"
__license__ = "GPL"
__version__ = "1.3.0"
__maintainer__ = "Andrew Arch"
__email__ = "andy.arch11@gmail.com"
__status__ = "Production"


import pandas as pd
import json

import numpy as np
import re
import math
import datetime
import textwrap

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Rectangle
import matplotlib.animation as animation

import cartopy.crs as ccrs
import cartopy


#Select what to display
display_state_boundaries = True
loop_display = False

display_colonisation = True
display_blak_history = True
display_white_blak_hx_back_to_back = False #ignores display_blak_history, as runs both scenarios back to back
display_explorers = True
display_explorers = display_colonisation and display_explorers
display_towns = True
display_towns = display_colonisation and display_towns
display_undated_towns = True
display_undated_towns = display_colonisation and display_undated_towns
display_railway_lines = True
display_railway_lines = display_colonisation and display_railway_lines
display_massacre_sites = True
display_massacre_sites = display_colonisation and display_massacre_sites and display_blak_history
display_missions = True
display_missions = display_colonisation and display_missions and display_blak_history
display_massacre_text = True
display_massacre_text = display_colonisation and display_massacre_text and display_blak_history
display_deaths_in_custody = True
display_deaths_in_custody = display_colonisation and display_deaths_in_custody and display_blak_history
display_incarceration_rates = True
display_incarceration_rates = display_colonisation and display_incarceration_rates and display_blak_history
display_defining_moments = True
display_defining_moments = display_colonisation and display_defining_moments
display_australian_conflict = True
display_australian_conflict = display_colonisation and display_australian_conflict

#TODO add life expectancy indigenous vs non-indigenous, other closing the gap indicators? Birth weight, Literacy, Year 12+ qualifications, employment rates, 
# appropriate housing, rates of child protection, domestic violence, suicide rates, languages spoken, digital access
# https://www.closingthegap.gov.au/national-agreement/targets

display_first_nations_milestones = True
display_first_nations_milestones = display_first_nations_milestones and display_blak_history

display_legal_controls = not display_colonisation
display_legislation = display_legal_controls
display_protection_boards = display_legal_controls

explorer_zorder = 1
undated_town_zorder = 2
town_zorder = 3
state_boundary_zorder = 4
massacre_zorder = 5
mission_zorder = 6
railway_zorder = 7
scrolling_text_zorder = 8

number_repeat_frames_at_start_and_end = 1

# https://www.captaincooksociety.com/home/detail/the-first-voyage-1768-1771
# Captain Cook left Plymouth Aug 1768
# Arrived at Rio de Janeiro Nov 1768
# Arrived at Tierra del Fuego Jan 1769
# Arrived at Tahiti April 1769 for the Transit of Venus observation - 3rd June 1769. Kills "natives"
# Arrived at New Zealand Oct 1769.  Kills "natives"
# Arrived at Australia April 1770, first sighting Point Hicks (Cape Everard) in Victoria 19th April 1770, 
# sailing north to Possession Island in the Torres Strait, stopping at Botany Bay and Cooktown
colonial_epoch = 1766 #1768
final_anime_year = 2020
#override values
#colonial_epoch = 1850
#final_anime_year = 1868

previous_year_indigenous_population = 750000
previous_year_non_indigenous_population = 0

#regex of geocoord
reg_dec = re.compile(r"[-+]?[0-9]{1,3}[.]{1}[0-9]+")

start_of_town_growth = 1840
timelapse_period = final_anime_year - colonial_epoch + 1
anime_interval = 500 #ms, time between animation frames

image_title = ''
if display_colonisation:
    if display_white_blak_hx_back_to_back:
        image_title = 'A White and Blak telling of the Colonisation of Australia'
    elif display_blak_history:
        image_title = 'Colonisation of Australia - a Blak History'
    else:
        image_title = 'The White History of Australia'
elif display_legal_controls:
    image_title = 'Legislative Control of Australian First Nations'

# common screen aspect ratios 
# 4:3 (NTSC/PAL)
# 3:2 (35mm film, DSLR, smartphone cameras)
# 16:9 (common desktop, smartphones: 1980x1080 - 3840x2160)
# 16:10 (widescreen: 1920x1200)
# 21:9 (ultra-widescreen: 3440x1440)
screen_ratio = 16/9

ylat0=-45
ylat1=-8
xlon0=105
xlon1=xlon0 + abs((ylat0 - ylat1) * screen_ratio)

figure_height_inches = 13
figure_width_inches = figure_height_inches * screen_ratio

#create figure to host animation.  N.B. if this is declared after Basemap, it will plot points to its own window
#size is in inches, width x height.
fig = plt.figure(figsize=[figure_width_inches, figure_height_inches], constrained_layout=True)

ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_extent([xlon0, xlon1, ylat0, ylat1], crs=ccrs.PlateCarree())

#ax.set_aspect('auto')
ax.coastlines(resolution='50m', color='0', linewidth=0.25, zorder=state_boundary_zorder)
ax.add_feature(cartopy.feature.LAND, color='white')
ax.add_feature(cartopy.feature.OCEAN)
#ax.add_feature(cartopy.feature.LAKES, edgecolor='black', alpha=0.5)
#ax.add_feature(cartopy.feature.RIVERS)

ax.set_title(image_title)

state_dictionary = {}
state_x_plots = {}
state_y_plots = {}
explorer_dictionary = {}
explorer_x_plots = {}
explorer_y_plots = {}
list_items = []

#Initialise Population coords
pop_x1 = 108
pop_x2 = 119
pop_x3 = 121
pop_x4 = 133
pop_y1 = -40.2
pop_y2 = -40.7
pop_perc_width = 12

#need to initialise all the writers up front for blt to work in file output
#set up percentage population bar
pop_perc_backing_rectangle = Rectangle((pop_x3, -42.5), pop_perc_width, 1, edgecolor='0.75', facecolor='white', linewidth=1.5, alpha=0)
ax.add_patch(pop_perc_backing_rectangle) 
pop_perc_bar = Rectangle((pop_x3, -42.5), pop_perc_width, 1, edgecolor='0.75', facecolor='black', linewidth=1.5, fill=True, alpha=0)  
ax.add_patch(pop_perc_bar) 
prison_perc_backing_rectangle = Rectangle((pop_x3, -44.5), pop_perc_width, 1, edgecolor='0.75', facecolor='white', linewidth=1.5, alpha=0)
ax.add_patch(prison_perc_backing_rectangle) 
prison_perc_bar = Rectangle((pop_x3, -44.5), pop_perc_width, 1, edgecolor='0.75', facecolor='black', linewidth=1.5, fill=True, alpha=0)
ax.add_patch(prison_perc_bar)

#initialise scatters
town_scatter = ax.scatter([], [], s=20, c="#e1910a", zorder=town_zorder)
unknown_town_est_year_scatter = ax.scatter([], [], s=20, c="#e1910a", zorder=town_zorder)
closed_mission_scatter = ax.scatter([], [], s=10, c="lightblue", marker='D', zorder=mission_zorder)
open_mission_scatter = ax.scatter([], [], s=15, c="blue", marker='D', zorder=mission_zorder)
massacre_scatter = ax.scatter([], [], s=20, facecolors="#cf210a", edgecolors="#cf210a", alpha=0.35, zorder=massacre_zorder)

#initialise text
acknowledgment_text = ax.text(115.0, -26.0, '', horizontalalignment='left', color='0.1', alpha=0, fontsize=10)
est_current_indig_pop_text = ax.text(pop_x1, pop_y1, '', horizontalalignment='left', color='k', fontsize=10)
est_current_indig_pop_value_text = ax.text(pop_x2, pop_y1, '', horizontalalignment='right', color='k', fontsize=10)
est_delta_indig_pop_text = ax.text(pop_x3, pop_y1, '', horizontalalignment='left', color='k', fontsize=10) 
est_delta_indig_pop_value_text = ax.text(pop_x4, pop_y1, '', horizontalalignment='right', color='k', fontsize=10)
est_current_nonindig_pop_text = ax.text(pop_x1, pop_y2, '', horizontalalignment='left', color='k', fontsize=10) 
est_current_nonindig_pop_value_text = ax.text(pop_x2, pop_y2, '', horizontalalignment='right', color='k', fontsize=10)
est_delta_nonindig_pop_text = ax.text(pop_x3, pop_y2, '', horizontalalignment='left', color='k', fontsize=10)
est_delta_nonindig_pop_value_text = ax.text(pop_x4, pop_y2, '', horizontalalignment='right', color='k', fontsize=10)
indig_pop_perc_text = ax.text(pop_x3, -41, '', verticalalignment='top', horizontalalignment='left', color='k', fontsize=10)
indig_incarc_pop_perc_text = ax.text(pop_x3, -42.9, '', verticalalignment='top', horizontalalignment='left', color='k', fontsize=10)
year_text = ax.text(136.5, -9.5, '', verticalalignment='top', horizontalalignment='left', color='blue', fontsize=15)

death_in_custody_royal_commission_1_txt = ax.text(156.05, -13.6, '', horizontalalignment='left', color='0.2', fontsize=8, alpha=0)
death_in_custody_royal_commission_2_txt = ax.text(156.05, -13.6, '', horizontalalignment='left', color='0.2', fontsize=8, alpha=0)   
death_in_custody_txt = ax.text(156.05, -14, '', horizontalalignment='left', color='0.2', fontsize=7)
aggregate_deaths_in_custody_txt = ax.text(156.05, -14.5, '', horizontalalignment='left', color='0.2', fontsize=7)
incarcerated_indigenous_txt = ax.text(156.05, -15, '', horizontalalignment='left', color='0.2', fontsize=7)
incarcerated_nonindigenous_txt = ax.text(156.05, -15.5, '', horizontalalignment='left', color='0.2', fontsize=7)

# initialise pools for dynamic use
number_conflict_lines = 100 #should only require ~70 at most
reference_conflicts = []
if display_australian_conflict:
    for i in range(number_conflict_lines):
        reference_conflicts.append(ax.text(106, -9, '', horizontalalignment='left', color='0.1', fontsize=7, zorder=scrolling_text_zorder))    

number_defining_moment_lines_to_display = 98 # number of text references need to be more than number we want to display due to wordwrap exploding number count
reference_defining_moments = []
if display_defining_moments:
    for i in range(int(number_defining_moment_lines_to_display * 1.7)):
        reference_defining_moments.append(ax.text(153, -11, '', horizontalalignment='left', color='0.1', fontsize=7, zorder=scrolling_text_zorder))

number_massacre_lines_to_display = 95
reference_massacre_lines = []
if display_massacre_text:
    for i in range(number_massacre_lines_to_display + 1):
        reference_massacre_lines.append(ax.text(162, -11, '', horizontalalignment='left', color='0.1', fontsize=7, zorder=scrolling_text_zorder))

number_milestones_to_display = 169 # 13 x 13 matrix
reference_milestones = []
if display_first_nations_milestones:
    for i in range(number_milestones_to_display):
        reference_milestones.append(ax.text(120, -35, '', horizontalalignment='left', color='0.1', fontsize=8))

number_state_boundary_features = 10
reference_state_boundary_features = []
number_state_names = 15
reference_state_names = []
if display_state_boundaries:
    for i in range(number_state_boundary_features):
        state_boundary_plot, = ax.plot([],[], color='0.7', linewidth=0.5, zorder=state_boundary_zorder)
        reference_state_boundary_features.append(state_boundary_plot)
    
    for i in range(number_state_names):
        reference_state_names.append(ax.text(110, -25, '', verticalalignment='center', horizontalalignment='left', color='0.6', fontsize=10, zorder=state_boundary_zorder))

number_legislation = 10000
reference_legislation = []
if display_legal_controls:
    for i in range(number_legislation):
        reference_legislation.append(ax.text(110, -25, '', horizontalalignment='left', color='0', fontsize=6))

number_explorer_paths = 40
reference_explorer_paths = []
number_explorer_names = 40
reference_explorer_names = []
if display_explorers:
    for i in range(number_explorer_paths):
        path_plot, = ax.plot([], [], color='purple', linestyle='dotted', alpha=0, zorder=explorer_zorder)
        reference_explorer_paths.append(path_plot)

    for i in range(number_explorer_names):
        reference_explorer_names.append(ax.text(106, -27.5, '', horizontalalignment='left', color='0', fontsize=7, alpha=0, zorder=scrolling_text_zorder))

number_railway_segments = 20000
reference_railway_segments = []
if display_railway_lines:
    for i in range(number_railway_segments):
        line_plot, = ax.plot([], [], color='1', linestyle='dashed', linewidth=0.7, zorder=railway_zorder)
        reference_railway_segments.append(line_plot)

def init():   
    """
        Initialisation function to set up the first frame of the animation

    """
    global list_items
    return list_items

def init_file_load(display_state_boundaries=False, display_first_nations_milestones=False, display_australian_conflict=False):
    """
        Loads files into memory on start 

        Parameters
        ----------
        (Optional) display_state_boundaries
            boolean: whether to load the 'States.csv' file

        (Optional) display_first_nations_milestone
            boolean: whether to load the 'First Nations milestones.csv' file

        (Optional) display_australian_conflict
            boolean: whether to load the 'Australia in Conflict.csv' file
        
        Returns
        -------
        population
            Panda DataFrame: containing the contents of the 'population.csv' file, 
                indexed on the 'Year' column

        state_boundaries
            Panda DataFrame: containing the contents of the 'States.csv' file, 
                indexed on the 'YearEffectiveFrom' column

        first_nations_milestones
            Panda DataFrame: containing the contents of the 'First Nations milestones.csv' file 
                not indexed

        australian_conflicts
            Panda DataFrame: containing the contents of the 'Australia in Conflict.csv' file
                not indexed
                'Current' value in the 'To' field replaced with the 'final_anime_year' value
    """

    #Year [0], Indigenous Population [1], Colonial Population [2], Total Population [3], Indigenous percentage [4], Indigenous Percentage drop from Baseline [5]
    population = pd.read_csv('./data/population.csv', index_col='Year')
    state_boundaries = pd.DataFrame()
    first_nations_milestones = pd.DataFrame()
    australian_conflicts = pd.DataFrame()

    if display_state_boundaries:  
        state_boundaries = pd.read_csv('./data/States.csv', index_col='YearEffectiveFrom')

    if display_first_nations_milestones:
        first_nations_milestones = pd.read_csv('./data/First Nations milestones.csv', index_col=None)

    if display_australian_conflict:
        australian_conflicts = pd.read_csv('./data/Australia in Conflict.csv')

        australian_conflicts['From'] = pd.to_numeric(australian_conflicts['From'])
        
        australian_conflicts['To'].replace('Current', final_anime_year, inplace=True)
        australian_conflicts['To'] = pd.to_numeric(australian_conflicts['To'])

    return population, state_boundaries, first_nations_milestones, australian_conflicts

def init_colonial_file_load(display_explorers=False, display_towns=False, display_undated_towns=False, display_railway_lines=False, display_massacre_sites=False, \
                            display_missions=False, display_deaths_in_custody=False, display_incarceration_rates=False, display_defining_moments=False): 
    """
        Loads files into memory that relate to the colonisation mapping

        Parameters
        ----------
        (Optional) display_explorers
            boolean: whether to load the 'Explorers.csv' file

        (Optional) display_towns
            boolean: whether to load the 'city_list.csv' file

        (Optional) display_undated_towns
            boolean: whether to load the 'undated_city_list.csv' file

         (Optional) display_railway_lines
            boolean: whether to load the 'Railway_Lines_vw_-3300151204749464250.geojson' and 'operating_dates_of_australian_railway_lines.csv' files

        (Optional) display_massacre_sites
            boolean: whether to load the 'ColonialMassacresInAustralia_Data.json' file

        (Optional) display_missions
            boolean: whether to load the 'Aboriginal and Torres Strait Islander Missions and Reserves.csv' file

        (Optional) display_deaths_in_custody
            boolean: whether to load the 'Deaths in Custody.csv' file

        (Optional) display_incarceration_rates
            boolean: whether to load the 'Prisoner characteristics, Australia (Tables 1 to 13) 1997 - 2013.xlsx' and 'Prisoner characteristics, Australia (Tables 1 to 13) 2014 - 2024.xlsx' files

        (Optional) display_defining_moments
            boolean: whether to load the 'Australian defining moments.csv' file

        Returns
        -------
        explorers
            Panda DataFrame: containing the contents of the 'Explorers.csv' file
                indexed on the 'From' column

        cities
            Panda DataFrame: containing the contents of the 'city_list.csv' file
                indexed on the 9th column 'established date (city page)'

        undated_cities
            Panda DataFrame: containing the contents of the 'undated_city_list.csv' file
                not indexed

        railways
            Panda DataFrame: containing the normalised contents of the 'Railway_Lines_vw_-3300151204749464250.geojson' file
                indexed on the 'properties.name' attribute

        railway_operating_dates
            Panda DataFrame: containing the contents of the 'operating_dates_of_australian_railway_lines.csv' file
                not indexed

        massacres
            Panda DataFrame: containing the normalised contents of the 'ColonialMassacresInAustralia_Data.json' file
                indexed on the derived 'yearofmassacre' column, generated from the 'properties.datestart' attribute

        missions
            Panda DataFrame: containing the contents of the 'Aboriginal and Torres Strait Islander Missions and Reserves.csv' file
                not indexed
                'Lat' and 'Lon' columns converted to decimal geocoordinates
                'current' value in the 'To' field replaced with the 'final_anime_year' value

        deaths_in_custody
            Panda DataFrame: containing the contents of the 'Deaths in Custody.csv' file
                'StartReportingYear' column and 'EndReportingYear' columns derived from the 'Year'
                indexed on the derived 'StartReportingYear' column

        incarceration_rates
            Panda DataFrame: containing the merged contents of the 'Table 2' worksheets from the 'Prisoner characteristics, Australia (Tables 1 to 13) 1997 - 2013.xlsx' and 'Prisoner characteristics, Australia (Tables 1 to 13) 2014 - 2024.xlsx' files
                indexed on 'Reference period' column 0
                derived 'Percentage' column, based on 'Aboriginal and Torres Strait Islander' / 'Aboriginal and Torres Strait Islander' + 'Non-Indigenous' columns
        
        defining_moments
            Panda DataFrame: containing the contents of the 'Australian defining moments.csv' file
                not indexed

    """
    explorers = pd.DataFrame()
    cities = pd.DataFrame()
    undated_cities = pd.DataFrame()
    railways = pd.DataFrame()
    railway_operating_dates = pd.DataFrame()
    massacres = pd.DataFrame()
    missions = pd.DataFrame()
    deaths_in_custody = pd.DataFrame()
    incarceration_rates = pd.DataFrame()
    defining_moments = pd.DataFrame()

    if display_explorers:
        #From [0], To [1], Explorer [2], GeoJson [3], MapReference [4]
        explorers = pd.read_csv('./data/Explorers.csv', index_col='From')
    if display_towns:
        #Town Name [0], Title [1], HREF Text [2], State [3], wikipedia href [4], dms_latitude [5], dms_longitude [6], dec_latitude [7], dec_longitude [8], established date (city page) [9], established date (parent page) [10], population [11]
        cities = pd.read_csv('./data/city_list.csv', header=None, quotechar='"', index_col=9).sort_index()
    if display_undated_towns:
        undated_cities = pd.read_csv('./data/undated_city_list.csv', header=None, quotechar='"')
    if display_railway_lines:
        #type: FeatureCollection, crs, features -> type: feature, id, geometry, properties -> objectid, featuressubtype, name, operational_status, feature_date, feature_source, attribute_date, attribute_source, source_ufi, source_jurisdiction, custodian_agency, custodian licensing, loading_date, track_gauge, ground_relationship, tracks, length_km, alternative_name, owner, source_supply_date, infrastructuretype, field, globalid
        #                                          type: feature, id, geometry, coordinates        
        railway_line_data = json.load(open('./data/Railway_Lines_vw_-3300151204749464250.geojson'))
        railways = pd.json_normalize(railway_line_data, 'features', errors='ignore')
        railways.set_index('properties.name', inplace=True)
        railways = railways.sort_index()  

        #Name, Features, Alternative Name, Wikipedia, Commenced, Opened, Closed, LineLength(km)
        railway_operating_dates = pd.read_csv('./data/operating_dates_of_australian_railway_lines.csv')

    if display_massacre_sites:
        #features -> type: feature, geometry, properties -> name, description, id, source, datestart, dateend, udatestart, udateend, latitude, longitude, linkback, Source_ID, LanguageGroup, Colony, StateOrTerritory, PoliceDistrict, KnownDate, AttackTime, Victims, VictimsDead, VictimDescription, Attackers, AttackersDead, AttackerDescription, Transport, Motive, WeaponsUsed, CorroborationRating, TLCMapLinkBack, TLCMapDataset
        massacre_data = json.load(open('./data/ColonialMassacresInAustralia_Data.json'))
        massacres = pd.json_normalize(massacre_data, 'features', errors='ignore')
        massacres['properties.datestart'] = pd.to_datetime(massacres['properties.datestart'])
        massacres['yearofmassacre'] = massacres['properties.datestart'].dt.year
        massacres.set_index('yearofmassacre', inplace=True)
        massacres = massacres.sort_index()

    if display_missions:
        # Mission, State, From, To, Run By, Lat, Lon, Wikipedia
        missions = pd.read_csv('./data/Aboriginal and Torres Strait Islander Missions and Reserves.csv')
        
        missions['From'] = pd.to_numeric(missions['From'])

        missions['To'].replace('current', final_anime_year + 1, inplace=True)
        missions['To'] = pd.to_numeric(missions['To'])

        missions['Lat'] = missions['Lat'].apply(dms2dec)
        missions['Lon'] = missions['Lon'].apply(dms2dec)

    if display_deaths_in_custody:
        #Year,Prison,Police,Youth detention,Other,Total
        #Year reporting is from July to June, so need to take the right hand value as the year
        deaths_in_custody = pd.read_csv('./data/Deaths in Custody.csv')
        split_years = deaths_in_custody['Year'].str.split(pat="–", n=1, expand=True)
        deaths_in_custody['StartReportingYear'] = split_years[0].astype(int)
        deaths_in_custody['EndReportingYear'] = split_years[1].astype(int)
        deaths_in_custody.set_index('StartReportingYear', inplace=True)
        deaths_in_custody = deaths_in_custody.sort_index()

    if display_incarceration_rates:        
        incarceration_cols = [0,3,4]
        inceration_skipped_rows = [0,1,2,3,4,6]
        incarceration_dtypes = {'Reference period': pd.Int32Dtype(), 'Aboriginal and Torres Strait Islander': pd.Int32Dtype(), 'Non-Indigenous': pd.Int32Dtype()}
        incarceration_rates_1 = pd.read_excel('./data/Prisoner characteristics, Australia (Tables 1 to 13) 1997 - 2013.xlsx', sheet_name='Table _2', header=0, skiprows=5, skipfooter=20, usecols=incarceration_cols, index_col=0, dtype=incarceration_dtypes, keep_default_na=True)
        incarceration_rates_2 = pd.read_excel('./data/Prisoner characteristics, Australia (Tables 1 to 13) 2014 - 2024.xlsx', sheet_name='Table 2', header=0, skiprows=inceration_skipped_rows, skipfooter=13, usecols=incarceration_cols, index_col=0, dtype=incarceration_dtypes, keep_default_na=True)
        incarceration_rates = pd.concat([incarceration_rates_1, incarceration_rates_2])
        incarceration_rates['Percentage'] = incarceration_rates['Aboriginal and Torres Strait Islander'] / (incarceration_rates['Aboriginal and Torres Strait Islander'] + incarceration_rates['Non-Indigenous'])

    if display_defining_moments:
        defining_moments = pd.read_csv('./data/Australian defining moments.csv')

        defining_moments['From'] = pd.to_numeric(defining_moments['From'])
        defining_moments['To'] = pd.to_numeric(defining_moments['To'])
    
    return explorers, cities, undated_cities, railways, railway_operating_dates, massacres, missions, deaths_in_custody, incarceration_rates, defining_moments

def dms2dec(dms_str):
    """
        Converts degree/minute/second values to decimal values

        Parameters
        ----------
        dms_str
            String: degree/minute/second formatted values

        Returns
        -------
        dec_value
            Converted decimal value
                empty string if dms_str is NA, otherwise returns a float
    """

    dec_value = ''

    if pd.isna(dms_str):
        return dms_str

    dms_str = re.sub(r'\s', '', dms_str) #strip white space characters
    
    sign = -1 if re.search('[swSW]', dms_str) else 1 #South and West directions have a negative value

    # check if decimal, assumes not an integer value, otherwise treat as degree/minute/second
    if re.search('^[-+]?[0-9]{1,3}[.]{1}[0-9]+', dms_str):
        m = reg_dec.findall(dms_str)
        dec_str = m[0]
        dec_value = sign * float(dec_str)
    else:    
        numbers = [*filter(len, re.split(r'\D+', dms_str, maxsplit=4))]

        if len(numbers) > 0:
            degree = numbers[0] # A fractional degree should have already been addressed
            minute = numbers[1] if len(numbers) >= 2 else '0' # A fractional minute will be incorrectly treated as a second in this approach
            second = numbers[2] if len(numbers) >= 3 else '0'
            frac_seconds = numbers[3] if len(numbers) >= 4 else '0'
            
            second += "." + frac_seconds

            dec_value = sign * (int(degree) + float(minute) / 60 + float(second) / 3600)
    
    return dec_value

def init_legal_file_load():
    """
        Loads the legal data from files into memory
       
        Returns
        -------
        state_protection_boards
            Panda DataFrame: containing the contents of the 'Aboriginal Protector Boards.csv' file
                not indexed
        
        british_legislation
            Panda DataFrame: containing the contents of the worksheet 'British Empire' from the 'Aboriginal Protector Boards.csv' file
                not indexed
        
        commonwealth_legislation
            Panda DataFrame: containing the contents of the worksheet 'Australian Commonwealth' from the 'Aboriginal Protector Boards.csv' file
                not indexed

        act_legislation
            Panda DataFrame: containing the contents of the worksheet 'Australian Capital Territory' from the 'Aboriginal Protector Boards.csv' file
                not indexed   
        
        qld_legislation
            Panda DataFrame: containing the contents of the worksheet 'Queensland' from the 'Aboriginal Protector Boards.csv' file
                not indexed         
        
        wa_legislation
            Panda DataFrame: containing the contents of the worksheet 'Western Australia' from the 'Aboriginal Protector Boards.csv' file
                not indexed 
        
        sa_legislation
            Panda DataFrame: containing the contents of the worksheet 'South Australia' from the 'Aboriginal Protector Boards.csv' file
                not indexed
        
        nsw_legislation
            Panda DataFrame: containing the contents of the worksheet 'New South Wales' from the 'Aboriginal Protector Boards.csv' file
                not indexed        
        
        nt_legislation
            Panda DataFrame: containing the contents of the worksheet 'Northern Territory' from the 'Aboriginal Protector Boards.csv' file
                not indexed
                
        tas_legislation
            Panda DataFrame: containing the contents of the worksheet 'Tasmania' from the 'Aboriginal Protector Boards.csv' file
                not indexed
        
        vic_legislation
            Panda DataFrame: containing the contents of the worksheet 'Victoria' from the 'Aboriginal Protector Boards.csv' file
                not indexed
    """

    #State [0], Impact [1], BoardName [2], From [3], To [4]
    state_protection_boards = pd.read_csv('./data/Aboriginal Protector Boards.csv')
    #Worksheets: British Empire, Australian Commonwealth, Australian Capital Territory, Queensland, Western Australia, South Australia, New South Wales, Northern Territory, Tasmania, Victoria
    # State [0], Impact [1], From [2], To [3], Legislation Name [4], Amended By [5], Repealed By [6], Description [7]
    legislation_file_path = './data/Aboriginal Control Legislation.xlsx'
    legislation_cols = ['State', 'Impact', 'From', 'To', 'Legislation Name']
    legislation_dtypes = {'From': pd.Int32Dtype(), 'To': pd.Int32Dtype()}
    british_legislation = pd.read_excel(legislation_file_path, sheet_name='British Empire', header=0, usecols=legislation_cols, dtype=legislation_dtypes, keep_default_na=True)
    commonwealth_legislation = pd.read_excel(legislation_file_path, sheet_name='Australian Commonwealth', header=0, usecols=legislation_cols, dtype=legislation_dtypes, keep_default_na=True)
    act_legislation = pd.read_excel(legislation_file_path, sheet_name='Australian Capital Territory', header=0, usecols=legislation_cols, dtype=legislation_dtypes, keep_default_na=True)
    qld_legislation = pd.read_excel(legislation_file_path, sheet_name='Queensland', header=0, usecols=legislation_cols, dtype=legislation_dtypes, keep_default_na=True)
    wa_legislation = pd.read_excel(legislation_file_path, sheet_name='Western Australia', header=0, usecols=legislation_cols, dtype=legislation_dtypes, keep_default_na=True)
    sa_legislation = pd.read_excel(legislation_file_path, sheet_name='South Australia', header=0, usecols=legislation_cols, dtype=legislation_dtypes, keep_default_na=True)
    nsw_legislation = pd.read_excel(legislation_file_path, sheet_name='New South Wales', header=0, usecols=legislation_cols, dtype=legislation_dtypes, keep_default_na=True)
    nt_legislation = pd.read_excel(legislation_file_path, sheet_name='Northern Territory', header=0, usecols=legislation_cols, dtype=legislation_dtypes, keep_default_na=True)
    tas_legislation = pd.read_excel(legislation_file_path, sheet_name='Tasmania', header=0, usecols=legislation_cols, dtype=legislation_dtypes, keep_default_na=True)
    vic_legislation = pd.read_excel(legislation_file_path, sheet_name='Victoria', header=0, usecols=legislation_cols, dtype=legislation_dtypes, keep_default_na=True)

    return state_protection_boards, british_legislation, commonwealth_legislation, act_legislation, qld_legislation, wa_legislation, sa_legislation, nsw_legislation, nt_legislation, tas_legislation, vic_legislation


def update_year(frame): 
    """
        Constructs the indexed animation frame

        Parameters
        ----------
        frame
            Integer: frame index

        Returns
        -------
        list_items
           List containing MatplotLib ax objects to be drawn for this animation frame
    """
    global list_items, reference_railway_segments, town_scatter, unknown_town_est_year_scatter, closed_mission_scatter, open_mission_scatter, massacre_scatter
    global display_blak_history, display_missions, display_massacre_sites, display_massacre_text, display_deaths_in_custody, display_incarceration_rates, display_first_nations_milestones
    global pop_perc_backing_rectangle, pop_perc_bar
    global previous_year_indigenous_population, previous_year_non_indigenous_population
    global acknowledgment_text, est_current_indig_pop_text, est_current_indig_pop_value_text, est_delta_indig_pop_text, est_delta_indig_pop_value_text, est_current_nonindig_pop_text, \
        est_current_nonindig_pop_value_text, est_delta_nonindig_pop_text, est_delta_nonindig_pop_value_text, indig_pop_perc_text, indig_incarc_pop_perc_text, year_text
    
    if not display_white_blak_hx_back_to_back:
        reference_frame = frame
    elif display_white_blak_hx_back_to_back and frame < (timelapse_period + (number_repeat_frames_at_start_and_end * 2)):
        reference_frame = frame
        display_blak_history = False
        temp_display_blak_history = display_blak_history
        display_blak_history = False
        temp_display_missions = display_missions
        display_missions = False
        temp_display_massacre_sites = display_massacre_sites
        display_massacre_sites = False
        temp_display_massacre_text = display_massacre_text
        display_massacre_text = False
        temp_display_deaths_in_custody = display_deaths_in_custody
        display_deaths_in_custody = False
        temp_display_incarceration_rates = display_incarceration_rates
        display_incarceration_rates = False
        temp_display_first_nations_milestones = display_first_nations_milestones
        display_first_nations_milestones = False
    else:
        reference_frame = frame - timelapse_period - (number_repeat_frames_at_start_and_end * 2)
        for ax in reference_railway_segments:
            ax.set_data([], [])

        #Unfortunately you can't set an empty scatter artist by calling set_offsets() with ([[]]) or ([],[])
        #so resetting the scatter artists with a masked array
        empty_offset = np.ma.masked_array([0,0], mask=True)
        town_scatter.set_offsets(empty_offset)
        unknown_town_est_year_scatter.set_offsets(empty_offset)
        closed_mission_scatter.set_offsets(empty_offset)
        open_mission_scatter.set_offsets(empty_offset)

        massacre_scatter.set_offsets(empty_offset)
        massacre_scatter.set_sizes([])
        massacre_scatter.set_facecolors([])
        massacre_scatter.set_edgecolors([]) 

        display_blak_history = True
        
    current_frame = reference_frame % (timelapse_period + (number_repeat_frames_at_start_and_end * 2))
    if current_frame <= number_repeat_frames_at_start_and_end:
        current_year = colonial_epoch
    elif current_frame >= timelapse_period + number_repeat_frames_at_start_and_end:
        current_year = colonial_epoch + timelapse_period - 1
    else:
        current_year = colonial_epoch + current_frame - number_repeat_frames_at_start_and_end

    pop_year = population.loc[current_year:current_year]
    pop_percentage = pop_year['Indigenous percentage'].values[0]
    pop_percentage_value = (float(pop_percentage.rstrip('%')))/100
    print(datetime.datetime.now())
    print('Current Year: ' + str(current_year))
    print('Pop Perc: ' + str(pop_percentage_value))

    if display_blak_history:
        current_year_indigenous_population = int(pop_year['Indigenous Population'].values[0].replace(',',''))
        current_year_non_indigenous_population = int(pop_year['Total Population'].values[0].replace(',','')) - current_year_indigenous_population
    else:
        current_year_non_indigenous_population = int(pop_year['Colonial Population'].values[0].replace(',',''))

    indigenous_population_change = 0
    non_indigenous_population_change = 0

    if current_year != colonial_epoch:
        if display_blak_history:
            indigenous_population_change = current_year_indigenous_population - previous_year_indigenous_population  
            previous_year_indigenous_population = current_year_indigenous_population 
        
        non_indigenous_population_change = current_year_non_indigenous_population - previous_year_non_indigenous_population
        previous_year_non_indigenous_population = current_year_non_indigenous_population
    else:
        previous_year_indigenous_population = 750000
        previous_year_non_indigenous_population = 0

    #reset reference to a new list of items
    #list_items = []
    list_items.clear()
        
    #State boundaries
    if display_state_boundaries:
        map_state_boundaries(current_year, list_items)
    
    if display_colonisation:
        #explorer paths
        if display_explorers:
            map_explorers(current_year, list_items)

        #undated cities and towns
        if display_undated_towns and current_year >= start_of_town_growth:
            map_undated_towns(current_year, list_items)
        
        #cities and towns
        if display_towns:
            map_towns(current_year, list_items)

        #massacres
        if display_massacre_sites:
            map_massacres(current_year, list_items)

        #railway lines
        if display_railway_lines:            
            map_railway_lines(current_year, list_items)

        if display_missions:
            map_missions(current_year, list_items)
    
    #Legislation
    if display_legal_controls:
        map_legislation(current_year, list_items)

    #Acknowledgement to Country
    if display_blak_history and current_year < 1788:
        ack_alpha = 1 - (current_year - colonial_epoch)/(1787 - colonial_epoch)
        acknowledgment_text.set_x(115.0)
        acknowledgment_text.set_y(-26.0)
        acknowledgment_text.set_text("Acknowledging the traditional owners of this land, paying respect to the people, the cultures, and the elders past and present, that which has been lost, and that which has survived")
        acknowledgment_text.set_alpha(ack_alpha)
        list_items.append(acknowledgment_text)
    elif current_year < 1788:        
        ack_alpha = 1 - (current_year - colonial_epoch)/(1787 - colonial_epoch)
        acknowledgment_text.set_x(132.5)
        acknowledgment_text.set_y(-26.0)
        acknowledgment_text.set_text("Terra Nullius")
        acknowledgment_text.set_alpha(ack_alpha)
        list_items.append(acknowledgment_text)
         
    # Population Numbers
    #Indigenous Population
    if display_blak_history:
        est_current_indig_pop_text.set_text('Est. Indigenous Population: ')
        list_items.append(est_current_indig_pop_text)
        est_current_indig_pop_value_text.set_text(format(current_year_indigenous_population,',').rjust(10,' '))
        list_items.append(est_current_indig_pop_value_text)

        #Indigenous Population Delta
        if indigenous_population_change == 0:
            txt_colour = '0.25'
        else:
            txt_colour = 'k'
            
        est_delta_indig_pop_text.set_text('Est. Indigenous Population Change: ')  
        est_delta_indig_pop_text.set_color(txt_colour)
        list_items.append(est_delta_indig_pop_text) 

        if indigenous_population_change < 0:
            txt_colour = '#cf210a'
        elif indigenous_population_change == 0:
            txt_colour = '0.25'
        else:
            txt_colour='k'

        est_delta_indig_pop_value_text.set_text(format(indigenous_population_change,',').rjust(7,' '))
        est_delta_indig_pop_value_text.set_color(txt_colour)
        list_items.append(est_delta_indig_pop_value_text )

    #Non-Indigenous Population
    if display_blak_history:
        population_x_position = pop_x1
        population_y_position = pop_y2
        population_value_x_position = pop_x2
        population_value_y_position = pop_y2
        population_txt = 'Est. non-Indigenous Population: '
        population_change_x_position = pop_x3
        population_change_y_position = pop_y2
        population_change_txt = 'Est. non-Indigenous Population Change: ' 
        population_change_value_x_position = pop_x4
        population_change_value_y_position = pop_y2       
    else:     
        population_x_position = 113
        population_y_position = pop_y2
        population_value_x_position = pop_x2
        population_value_y_position = pop_y2
        population_txt = 'Est. Population: '
        population_change_x_position = pop_x3
        population_change_y_position = pop_y2
        population_change_txt = 'Est. Population Change: '
        population_change_value_x_position = 128
        population_change_value_y_position = pop_y2

    if current_year_non_indigenous_population == 0:
        txt_colour = '0.25'
    else:
        txt_colour = 'k'
    est_current_nonindig_pop_text.set_x(population_x_position)
    est_current_nonindig_pop_text.set_y(population_y_position)
    est_current_nonindig_pop_text.set_text(population_txt)
    est_current_nonindig_pop_text.set_color(txt_colour)
    list_items.append(est_current_nonindig_pop_text)

    est_current_nonindig_pop_value_text.set_x(population_value_x_position)
    est_current_nonindig_pop_value_text.set_y(population_value_y_position)
    est_current_nonindig_pop_value_text.set_text(format(current_year_non_indigenous_population,',').rjust(10,' '))
    est_current_nonindig_pop_value_text.set_color(txt_colour)
    list_items.append(est_current_nonindig_pop_value_text)

    #Non-Indigenous Population Change
    if non_indigenous_population_change == 0:
        txt_colour = '0.25'
    else:
        txt_colour = 'k'
    est_delta_nonindig_pop_text.set_x(population_change_x_position)
    est_delta_nonindig_pop_text.set_y(population_change_y_position)
    est_delta_nonindig_pop_text.set_text(population_change_txt)
    est_delta_nonindig_pop_text.set_color(txt_colour)
    list_items.append(est_delta_nonindig_pop_text)

    if non_indigenous_population_change < 0:
        txt_colour = '#cf210a'
    elif non_indigenous_population_change == 0:
        txt_colour = '0.25'
    else:
        txt_colour='k'
    est_delta_nonindig_pop_value_text.set_x(population_change_value_x_position)
    est_delta_nonindig_pop_value_text.set_y(population_change_value_y_position)
    est_delta_nonindig_pop_value_text.set_text(format(non_indigenous_population_change,',').rjust(7,' '))
    est_delta_nonindig_pop_value_text.set_color(txt_colour)
    list_items.append(est_delta_nonindig_pop_value_text)
    
    if display_blak_history:
        # Percentage Indigenous Pop
        #indig_pop_colour = str(1 - pop_percentage_value)
        indig_pop_colour = '0.9'
        indig_pop_perc_text.set_text('Percent Indigenous Population: ' + pop_percentage)
        indig_pop_perc_text.set_color(indig_pop_colour)
        list_items.append(indig_pop_perc_text) 

        # Percentage Indigenous Pop bar
        pop_perc_backing_rectangle.set_alpha(1)
        list_items.append(pop_perc_backing_rectangle)

        pop_perc_bar.set_width(pop_perc_width * pop_percentage_value)
        pop_perc_bar.set_facecolor(str(1 - pop_percentage_value))
        pop_perc_bar.set_alpha(1)
        list_items.append(pop_perc_bar)  

        if display_incarceration_rates and current_year >= incarceration_rates.index[0]:  
            incarceration_perc = incarceration_rates.loc[current_year]['Percentage']
            #incarceration_colour = str(1 - incarceration_perc)
            incarceration_colour = '0.9'
            indig_incarc_pop_perc_text.set_text('Percent Incarcerated that are Indigenous: ' + str("{:.1%}".format(incarceration_perc)))
            indig_incarc_pop_perc_text.set_color(incarceration_colour)
            list_items.append(indig_incarc_pop_perc_text) 
            
            prison_perc_backing_rectangle.set_alpha(1)
            list_items.append(prison_perc_backing_rectangle)

            prison_perc_bar.set_alpha(1)
            prison_perc_bar.set_width(pop_perc_width * incarceration_perc)
            prison_perc_bar.set_facecolor(incarceration_colour)
            list_items.append(prison_perc_bar) 

            add_incarcerated(current_year, list_items)
        else:
            prison_perc_backing_rectangle.set_alpha(0)
            list_items.append(prison_perc_backing_rectangle)
            prison_perc_bar.set_alpha(0)
            list_items.append(prison_perc_bar)

    # Current Year
    year_text.set_text('Year: ' + str(current_year))
    year_text.set_color('blue')
    list_items.append(year_text)  

    # Milestone table
    if display_first_nations_milestones:
        add_first_nations_milestones(current_year, list_items)

    # Conflict Text
    if display_australian_conflict:
        add_australian_conflicts(current_year, list_items)

    if display_defining_moments:
        add_australian_defining_moments(current_year, list_items)

    if display_deaths_in_custody:
        add_deaths_in_custody(current_year, list_items)

    if display_white_blak_hx_back_to_back and frame < (timelapse_period + (number_repeat_frames_at_start_and_end * 2)):
        display_blak_history = temp_display_blak_history
        display_missions = temp_display_missions
        display_massacre_sites = temp_display_massacre_sites
        display_massacre_text = temp_display_massacre_text
        display_deaths_in_custody = temp_display_deaths_in_custody
        display_incarceration_rates = temp_display_incarceration_rates
        display_first_nations_milestones = temp_display_first_nations_milestones
    
    print(datetime.datetime.now())
    print('')

    return list_items

def add_first_nations_milestones(current_year, list_items):
    """
        Constructs a matrix of dates where some significant milestones are met

        Parameters
        ----------
        current_year
            integer: current year to display
            
        list_items
            list: MatplotLib ax objects to be drawn for this animation frame
    """
    global reference_milestones

    init_x = 120.1
    init_y = -34.8
    init_offset = 0.1
    column_offset = 1.2
    row_offset = 0.4

    txt_colour = '0.25'
    txt_fontsize=8

    min_row_values = first_nations_milestones.min(axis=1)
    min_col_values = first_nations_milestones.min(axis=0)
    max_row_values = first_nations_milestones.max(axis=1)

    independence_row = first_nations_milestones.index.get_loc(first_nations_milestones[first_nations_milestones['Event'] == 'Independence from Australia'].index[0])
    protectors_row = first_nations_milestones.index.get_loc(first_nations_milestones[first_nations_milestones['Event'] == 'Protectors'].index[0])
    protection_board_row = first_nations_milestones.index.get_loc(first_nations_milestones[first_nations_milestones['Event'] == 'Protection Boards'].index[0])
    protection_board_abolished_row = first_nations_milestones.index.get_loc(first_nations_milestones[first_nations_milestones['Event'] == 'Protection Boards Abolished'].index[0])

    counted_row = 0

    if current_year >= min_row_values.min():
        # state column headers
        for col in range(len(first_nations_milestones.columns)):
            if col > 0:
                if current_year >= min_col_values[col]:                    
                    text_pyplot_axes = reference_milestones[col]
                    text_pyplot_axes.set_x(init_x + init_offset + (col * column_offset))
                    text_pyplot_axes.set_y(init_y)
                    text_pyplot_axes.set_text((first_nations_milestones.columns)[col])
                    text_pyplot_axes.set_horizontalalignment('center')
                    text_pyplot_axes.set_color(txt_colour)
                    text_pyplot_axes.set_fontsize(txt_fontsize)   
                    list_items.append(text_pyplot_axes)  
                    #states_txt = ax.text(init_x + init_offset + (col * column_offset), init_y, (first_nations_milestones.columns)[col], horizontalalignment='center', color=str(txt_colour), fontsize=txt_fontsize)
                    #list_items.append(states_txt)  
        # date matrix
        for row in range(len(first_nations_milestones)):   
            if current_year >= min_row_values[row]:              
                for i in range(len(first_nations_milestones.iloc[row])):   
                    # set colour of text
                    event_txt_colour = txt_colour                    
                    # check if Protection boards are abolished  
                    if i == 0 and current_year >= max_row_values[protection_board_abolished_row] and row >= protectors_row and row <= protection_board_row:
                        event_txt_colour = '0.5'
                    elif i == 0 and row <= independence_row or row > protection_board_row:
                        event_txt_colour = txt_colour

                    #set colour of dates
                    event_year_txt_colour = txt_colour
                    if i > 0 and (current_year >= first_nations_milestones.iloc[protection_board_abolished_row][i] or current_year >= max_row_values[protection_board_abolished_row]) and row >= protectors_row and row <= protection_board_row:  
                        # Protection boards are abolished
                        event_year_txt_colour = '0.5'
                    elif i > 0 and current_year >= first_nations_milestones.iloc[independence_row][i] and row > independence_row:
                        # Independence is granted
                        event_year_txt_colour = '0.5'   
                    elif i > 0 and row <= independence_row or row > protection_board_row:
                        event_year_txt_colour = txt_colour

                    # write out the matrix of dates
                    if i == 0:
                        pointer = (len(first_nations_milestones.columns) * (row + 1))
                        text_pyplot_axes = reference_milestones[pointer]
                        text_pyplot_axes.set_x(init_x + (i * column_offset))
                        text_pyplot_axes.set_y(init_y - (row_offset * (counted_row + 1)))
                        text_pyplot_axes.set_text((first_nations_milestones.iloc[row])[i])
                        text_pyplot_axes.set_horizontalalignment('right')
                        text_pyplot_axes.set_color(event_txt_colour)
                        text_pyplot_axes.set_fontsize(txt_fontsize)   
                        list_items.append(text_pyplot_axes) 
                        #event_txt = ax.text(init_x + (i * column_offset), init_y - (row_offset * (counted_row + 1)), (first_nations_milestones.iloc[row])[i], horizontalalignment='right', color=str(event_txt_colour), fontsize=txt_fontsize)
                        #list_items.append(event_txt)             
                    else:      
                        if current_year >= (first_nations_milestones.iloc[row])[i] and pd.notna((first_nations_milestones.iloc[row])[i]): 
                            pointer = (len(first_nations_milestones.columns) * (row + 1)) + i
                            text_pyplot_axes = reference_milestones[pointer]
                            text_pyplot_axes.set_x(init_x + init_offset + (i * column_offset))
                            text_pyplot_axes.set_y(init_y - (row_offset * (counted_row + 1)))
                            text_pyplot_axes.set_text(str(int((first_nations_milestones.iloc[row])[i])))
                            text_pyplot_axes.set_horizontalalignment('center')
                            text_pyplot_axes.set_color(event_year_txt_colour)
                            text_pyplot_axes.set_fontsize(txt_fontsize)   
                            list_items.append(text_pyplot_axes)     
                            #event_txt = ax.text(init_x + init_offset + (i * column_offset), init_y - (row_offset * (counted_row + 1)), str(int((first_nations_milestones.iloc[row])[i])), horizontalalignment='center', color=str(event_year_txt_colour), fontsize=txt_fontsize)
                            #list_items.append(event_txt)     
                counted_row += 1    

def add_australian_conflicts(current_year, list_items):
    """
        Lists conflicts Australia has been involved in

        Parameters
        ----------
        current_year
            integer: current year to display
            
        list_items
            list: MatplotLib ax objects to be drawn for this animation frame
    """
    global reference_conflicts

    # clean up residual from previous year to avoid ghosting in generating movie
    for ax in reference_conflicts:
        ax.set_text("")

    veteran_memory = 60

    init_x = 106
    init_y = -9
    row_offset = 0.34

    txt_active_conflict_colour = '0.1'
    txt_past_conflict_colour = '0.3'
    txt_fontsize=8

    counted_row = 0

    active_conflicts = pd.DataFrame()
    past_conflicts = pd.DataFrame()

    if display_blak_history:
        active_conflicts = australian_conflicts[((australian_conflicts['From'] <= current_year) & ((australian_conflicts['To'] >= current_year) | (australian_conflicts['To'].isna())))]
        past_conflicts = australian_conflicts[((australian_conflicts['To'] > current_year - veteran_memory) & (australian_conflicts['To'] < current_year))]
        past_conflicts = past_conflicts.sort_values(by=['To', 'From'], ascending=[False, True])
    else:
        active_conflicts = australian_conflicts[((australian_conflicts['From'] <= current_year) & ((australian_conflicts['To'] >= current_year) | (australian_conflicts['To'].isna())) & (australian_conflicts['Blak Hx'] != True))]
        past_conflicts = australian_conflicts[((australian_conflicts['To'] > current_year - veteran_memory) & (australian_conflicts['To'] < current_year) & (australian_conflicts['Blak Hx'] != True))]
        past_conflicts = past_conflicts.sort_values(by=['To', 'From'], ascending=[False, True])

    if active_conflicts.size > 0 or past_conflicts.size > 0:        
        text_pyplot_axes = reference_conflicts[counted_row]
        text_pyplot_axes.set_x(init_x)
        text_pyplot_axes.set_y(init_y)
        text_pyplot_axes.set_text("Australian Conflicts")
        text_pyplot_axes.set_color(txt_active_conflict_colour)
        text_pyplot_axes.set_fontsize(10)   
        list_items.append(text_pyplot_axes)  
        #list_items.append(ax.text(init_x, init_y - (counted_row * row_offset), "Australian Conflicts", horizontalalignment='left', color=str(txt_colour), fontsize=10))
        counted_row += 1              
        text_pyplot_axes = reference_conflicts[counted_row]
        text_pyplot_axes.set_x(init_x)
        text_pyplot_axes.set_y(init_y - (counted_row * row_offset))
        text_pyplot_axes.set_text("")
        text_pyplot_axes.set_color(txt_active_conflict_colour)
        text_pyplot_axes.set_fontsize(txt_fontsize)   
        list_items.append(text_pyplot_axes)  
        #list_items.append(ax.text(init_x, init_y - (counted_row * row_offset), "", horizontalalignment='left', color=str(txt_colour), fontsize=10))
        counted_row += 1

        if active_conflicts.size > 0:
            for conflict in active_conflicts.itertuples():
                conflict_text = conflict_str(conflict, True, current_year)
                if conflict[1] == 'Frontier Wars' or conflict[2] == 'Frontier Wars' or conflict[2] == 'Hawkesbury and Nepean Wars':
                    txt_active_conflict_colour = '#cf210a'
                elif '(Peacekeeping)' in conflict[1]:
                    txt_active_conflict_colour = '#5b92e5'
                else:
                    txt_active_conflict_colour = '0.15'

                text_pyplot_axes = reference_conflicts[counted_row]
                text_pyplot_axes.set_x(init_x)
                text_pyplot_axes.set_y(init_y - (counted_row * row_offset))
                text_pyplot_axes.set_text(conflict_text)
                text_pyplot_axes.set_color(txt_active_conflict_colour)
                text_pyplot_axes.set_fontsize(txt_fontsize)              
                text_pyplot_axes.set_alpha(1)
                list_items.append(text_pyplot_axes)
                #list_items.append(ax.text(init_x, init_y - (counted_row * row_offset), conflict_text, horizontalalignment='left', color=str(txt_active_conflict_colour), fontsize=txt_fontsize))
                counted_row += 1

        if past_conflicts.size > 0:
            for past_conflict in past_conflicts.itertuples():
                conflict_text = conflict_str(past_conflict, False, current_year)
                conflict_alpha = math.sqrt(1 - ((current_year - past_conflict[5])/veteran_memory)**2)

                text_pyplot_axes = reference_conflicts[counted_row]
                text_pyplot_axes.set_x(init_x)
                text_pyplot_axes.set_y(init_y - (counted_row * row_offset))
                text_pyplot_axes.set_text(conflict_text)
                text_pyplot_axes.set_color(txt_past_conflict_colour)
                text_pyplot_axes.set_fontsize(txt_fontsize)   
                text_pyplot_axes.set_alpha(conflict_alpha)
                list_items.append(text_pyplot_axes)
                #list_items.append(ax.text(init_x, init_y - (counted_row * row_offset), conflict_text, horizontalalignment='left', color=txt_past_conflict_colour, fontsize=txt_fontsize, alpha=conflict_alpha))        
                counted_row += 1

def conflict_str(conflict, active, current_year):
    """
        Creates the string to display for the individual conflict

        Parameters
        ----------
        conflict
            conflict row to be formatted

        active
            boolean: whether the conflict is active in the current year or not

        current_year
            integer: current year to include in formatted text

        Returns
        -------
        conflict_text
            String: formatted text of conflict
    """
    conflict_col = 1
    parent_conflict_col = 2
    from_col = 4
    to_col = 5

    if pd.isna(conflict[parent_conflict_col]):
        parent_conflict = ""
    else:
        parent_conflict = "".join(["[", conflict[parent_conflict_col], "] "])

    if active:
        to_year = current_year
    else:
        to_year = conflict[to_col]

    conflict_text = "".join([str(conflict[from_col]), "-", str(to_year), ": ", parent_conflict, conflict[conflict_col]])
    
    return conflict_text
     
def add_australian_defining_moments(current_year, list_items):
    """
        Lists defining moments in Australia's history

        Parameters
        ----------
        current_year
            integer: current year to display
            
        list_items
            list: MatplotLib ax objects to be drawn for this animation frame
    """  
    global reference_defining_moments
    global number_defining_moment_lines_to_display

    # clean up residual from previous year to avoid ghosting in generating movie
    for ax in reference_defining_moments:
        ax.set_text("")

    citizen_memory = 10    

    if display_blak_history:
        init_x = 153.8
    else:
        init_x = 156.2

    init_y = -11.25
    row_offset = 0.34

    txt_active_moment_colour = '0.15'
    txt_past_moment_colour = '0.3'
    txt_fontsize=7

    counted_row = 0

    active_moments= pd.DataFrame()
    past_moments = pd.DataFrame()

    if display_blak_history:
        active_moments = defining_moments[((defining_moments['From'] <= current_year) & ((defining_moments['To'] >= current_year) | (defining_moments['To'].isna())))]
        past_moments = defining_moments[((defining_moments['To'] > current_year - citizen_memory) & (defining_moments['To'] < current_year))]
        past_moments = past_moments.sort_values(by=['To', 'From'], ascending=[False, True])
    else:
        active_moments = defining_moments[((defining_moments['From'] <= current_year) & ((defining_moments['To'] >= current_year) | (defining_moments['To'].isna())) & (defining_moments['Blak Hx'] != True))]
        past_moments = defining_moments[((defining_moments['To'] > current_year - citizen_memory) & (defining_moments['To'] < current_year) & (defining_moments['Blak Hx'] != True))]
        past_moments = past_moments.sort_values(by=['To', 'From'], ascending=[False, True])

    if active_moments.size > 0 or past_moments.size > 0:
        text_pyplot_axes = reference_defining_moments[counted_row]
        text_pyplot_axes.set_x(init_x)
        text_pyplot_axes.set_y(init_y - (counted_row * row_offset))
        text_pyplot_axes.set_text("Defining Moments")
        text_pyplot_axes.set_color(txt_active_moment_colour)
        text_pyplot_axes.set_fontsize(10)   
        list_items.append(text_pyplot_axes)  
        #list_items.append(ax.text(init_x, init_y - (counted_row * row_offset), "Defining Moments", horizontalalignment='left', color=str(txt_colour), fontsize=10))
        counted_row += 2 # allow a greater gap under the heading
        text_pyplot_axes = reference_defining_moments[counted_row]
        text_pyplot_axes.set_x(init_x)
        text_pyplot_axes.set_y(init_y - (counted_row * row_offset))
        text_pyplot_axes.set_text("")
        text_pyplot_axes.set_fontsize(txt_fontsize)    
        list_items.append(text_pyplot_axes)
        #list_items.append(ax.text(init_x, init_y - (counted_row * row_offset), "", horizontalalignment='left', color=str(txt_colour), fontsize=10))
        counted_row += 1

        active_moments_with_wrapped_lines = []
        past_moments_with_wrapped_lines = []

        if active_moments.size > 0:  
            for active_moment in active_moments.itertuples():
                initial_indent = "".join([str(active_moment[3]), ": "])
                wrapped_lines = textwrap.wrap(text=active_moment[1], width=50, initial_indent=initial_indent, subsequent_indent="      ")
                for line in wrapped_lines:
                    text_pyplot_axes = reference_defining_moments[counted_row]
                    text_pyplot_axes.set_x(init_x)
                    text_pyplot_axes.set_y(init_y - (counted_row * row_offset))
                    text_pyplot_axes.set_text(line)
                    text_pyplot_axes.set_color(txt_active_moment_colour)
                    text_pyplot_axes.set_fontsize(txt_fontsize)    
                    text_pyplot_axes.set_alpha(1)
                    active_moments_with_wrapped_lines.append(text_pyplot_axes)  
                    #list_items.append(ax.text(init_x, init_y - (counted_row * row_offset), line, horizontalalignment='left', color=str(txt_colour), fontsize=txt_fontsize))
                    counted_row += 1

        if past_moments.size > 0:            
            for past_moment in past_moments.itertuples():                   
                initial_indent = "".join([str(past_moment[3]), ": "])             
                wrapped_lines = textwrap.wrap(text=past_moment[1], width=50, initial_indent=initial_indent, subsequent_indent="      ")
                moment_alpha = math.sqrt(1 - ((current_year - past_moment[4])/citizen_memory)**2)
                
                for line in wrapped_lines:                                  
                    text_pyplot_axes = reference_defining_moments[counted_row]
                    text_pyplot_axes.set_x(init_x)
                    text_pyplot_axes.set_y(init_y - (counted_row * row_offset))
                    text_pyplot_axes.set_text(line)
                    text_pyplot_axes.set_color(txt_past_moment_colour)
                    text_pyplot_axes.set_fontsize(txt_fontsize)   
                    text_pyplot_axes.set_alpha(moment_alpha)
                    past_moments_with_wrapped_lines.append(text_pyplot_axes) 
                    #past_moments_with_wrapped_lines.append(ax.text(init_x, init_y - (counted_row * row_offset), line, horizontalalignment='left', color='0.3', fontsize=txt_fontsize, alpha=moment_alpha))
                    counted_row += 1

        if len(active_moments_with_wrapped_lines) + len(past_moments_with_wrapped_lines) > number_defining_moment_lines_to_display:
            past_moments_with_wrapped_lines = past_moments_with_wrapped_lines[:(number_defining_moment_lines_to_display - len(active_moments_with_wrapped_lines))]
        
        for wrapped_line in active_moments_with_wrapped_lines:
            list_items.append(wrapped_line)

        for wrapped_line in past_moments_with_wrapped_lines:  
            list_items.append(wrapped_line)

        # clean up extraneous ax entries so doesn't effect generated movies
        if counted_row + 1 > number_defining_moment_lines_to_display:
            for i in range(number_defining_moment_lines_to_display, counted_row):
                reference_defining_moments[i].set_text("")


def map_state_boundaries(current_year, list_items):
    """
        Maps the states and territories for the current year

        Parameters
        ----------
        current_year
            integer: current year to display
            
        list_items
            list: MatplotLib ax objects to be drawn for this animation frame
    """
    global reference_state_boundary_features, reference_state_names

    # clean up residual from previous year to avoid ghosting in generating movie
    for ax in reference_state_boundary_features:
        ax.set_data([], [])

    for ax in reference_state_names:
        ax.set_text("")

    boundary_row = state_boundaries[(current_year >= state_boundaries.index) & (current_year <= state_boundaries.YearEffectiveTo)]
    if len(boundary_row) > 0:
        state_boundary_path = boundary_row.GeoJsonFile.values[0]
        state_geo_paths = pd.read_json('./data/' + state_boundary_path)
        features = state_geo_paths['features']
        feature_ctr = 0       
        
        for feature in features:
            geometries = feature['geometry']
            coords = geometries['coordinates']
            df = pd.DataFrame(coords, columns=['longitude','latitude'])               
            plot_pyplot_axes = reference_state_boundary_features[feature_ctr]
            plot_pyplot_axes.set_data(df.longitude.values, df.latitude.values)
            list_items.append(plot_pyplot_axes)
            #state_line_plot, = ax.plot(df.longitude.values, df.latitude.values, color='0.7', linewidth=0.5, zorder=state_boundary_zorder)  
            #list_items.append(state_line_plot)
            feature_ctr += 1
        
        state_name_ctr = 0
        state_text_path = boundary_row.StateNameFile.values[0]
        state_names = pd.read_csv('./data/' + state_text_path)
        if display_colonisation:
            state_name_list = state_names.loc[state_names["Mapping"] == "Colonisation"]
        else:
            state_name_list = state_names.loc[state_names["Mapping"] == "Legislation"]
        for index, state_name in state_name_list.iterrows():                                           
            text_pyplot_axes = reference_state_names[state_name_ctr]
            text_pyplot_axes.set_x(float(state_name['Longitude']))
            text_pyplot_axes.set_y(float(state_name['Latitude']))
            text_pyplot_axes.set_text(state_name['StateName'])
            list_items.append(text_pyplot_axes) 
            #list_items.append(ax.text(float(state_name['Longitude']), float(state_name['Latitude']), state_name['StateName'], verticalalignment='center', horizontalalignment='left', color='0.6', fontsize=10, zorder=state_boundary_zorder))
            state_name_ctr += 1


def map_legislation(current_year, list_items):
    """
        Lists legislation active in the current year for the various States

        Parameters
        ----------
        current_year
            integer: current year to display
            
        list_items
            list: MatplotLib ax objects to be drawn for this animation frame
    """
    global reference_legislation
    legislation_count = 0

    # clean up residual from previous year to avoid ghosting in generating movie
    for ax in reference_legislation:
        ax.set_text("")

    active_british_legislation = british_legislation[((british_legislation['From'] <= current_year) & ((british_legislation['To'] > current_year) | (british_legislation['To'].isna())))]
    active_commonwealth_legislation = commonwealth_legislation[((commonwealth_legislation['From'] <= current_year) & ((commonwealth_legislation['To'] > current_year) | (commonwealth_legislation['To'].isna())))]
    active_act_legislation = act_legislation[((act_legislation['From'] <= current_year) & ((act_legislation['To'] > current_year) | (act_legislation['To'].isna())))]
    active_qld_legislation = qld_legislation[((qld_legislation['From'] <= current_year) & ((qld_legislation['To'] > current_year) | (qld_legislation['To'].isna())))]
    active_wa_legislation = wa_legislation[((wa_legislation['From'] <= current_year) & ((wa_legislation['To'] > current_year) | (wa_legislation['To'].isna())))]
    active_sa_legislation = sa_legislation[((sa_legislation['From'] <= current_year) & ((sa_legislation['To'] > current_year) | (sa_legislation['To'].isna())))]
    active_nsw_legislation = nsw_legislation[((nsw_legislation['From'] <= current_year) & ((nsw_legislation['To'] > current_year) | (nsw_legislation['To'].isna())))]
    active_nt_legislation = nt_legislation[((nt_legislation['From'] <= current_year) & ((nt_legislation['To'] > current_year) | (nt_legislation['To'].isna())))]
    active_tas_legislation = tas_legislation[((tas_legislation['From'] <= current_year) & ((tas_legislation['To'] > current_year) | (tas_legislation['To'].isna())))]
    active_vic_legislation = vic_legislation[((vic_legislation['From'] <= current_year) & ((vic_legislation['To'] > current_year) | (vic_legislation['To'].isna())))]
    
    #Aboriginal Protection Boards and Legislation
    pb_txt_locations = {'State':['VIC','NSW','WA','QLD','SA','NT','ACT','TAS','CTH','BRITAIN'],'Longitude':[141.5,141.5,116.0,140.0,129.5,129.5,155.5,145.5,153.0,111.0],'Latitude':[-36.0,-30.4,-23.4,-20.9,-27.9,-16.4,-34.7,-41.2,-12.0,-12.0]}
    pb_locations_df = pd.DataFrame(pb_txt_locations)

    for index, state_pb in pb_locations_df.iterrows():
        pb_txt_x = state_pb['Longitude']
        pb_txt_y = state_pb['Latitude']

        #Legislation
        # TODO - confirm negative/positive impact of legislation
        # TODO - check end dates of legislation
        if display_legislation:
            y_offset = pb_txt_y - 0.2
            if state_pb['State'] == 'VIC':               
                legislation_count += add_legislation(list_items, active_vic_legislation, pb_txt_x, y_offset, reference_legislation, legislation_count)
            elif state_pb['State'] == 'NSW':               
                legislation_count += add_legislation(list_items, active_nsw_legislation, pb_txt_x, y_offset, reference_legislation, legislation_count)
            elif state_pb['State'] == 'WA':               
                legislation_count += add_legislation(list_items, active_wa_legislation, pb_txt_x, y_offset, reference_legislation, legislation_count)
            elif state_pb['State'] == 'QLD':               
                legislation_count += add_legislation(list_items, active_qld_legislation, pb_txt_x, y_offset, reference_legislation, legislation_count)
            elif state_pb['State'] == 'SA':               
                legislation_count += add_legislation(list_items, active_sa_legislation, pb_txt_x, y_offset, reference_legislation, legislation_count)
            elif state_pb['State'] == 'NT':               
                legislation_count += add_legislation(list_items, active_nt_legislation, pb_txt_x, y_offset, reference_legislation, legislation_count)
            elif state_pb['State'] == 'ACT':               
                y_offset -= 0.8
                legislation_count += add_legislation(list_items, active_act_legislation, pb_txt_x, y_offset, reference_legislation, legislation_count)
            elif state_pb['State'] == 'TAS':    
                legislation_count += add_legislation(list_items, active_tas_legislation, pb_txt_x, y_offset, reference_legislation, legislation_count)
            elif state_pb['State'] == 'CTH':
                if len(active_commonwealth_legislation) > 0:
                    text_pyplot_axes = reference_legislation[legislation_count]
                    text_pyplot_axes.set_x(pb_txt_x)
                    text_pyplot_axes.set_y(pb_txt_y)
                    text_pyplot_axes.set_text('Commonwealth Parliament')
                    text_pyplot_axes.set_color('0.25')      
                    text_pyplot_axes.set_verticalalignment('center')              
                    text_pyplot_axes.set_horizontalalignment('left')
                    text_pyplot_axes.set_fontsize(10)
                    list_items.append(text_pyplot_axes)
                    #list_items.append(ax.text(pb_txt_x, pb_txt_y, 'Commonwealth Parliament', verticalalignment='center', horizontalalignment='left', color='0.25', fontsize=10))
                    legislation_count += 1
                legislation_count += add_legislation(list_items, active_commonwealth_legislation, pb_txt_x, y_offset, reference_legislation, legislation_count)
            elif state_pb['State'] == 'BRITAIN':
                if len(active_british_legislation) > 0:                    
                    text_pyplot_axes = reference_legislation[legislation_count]
                    text_pyplot_axes.set_x(pb_txt_x)
                    text_pyplot_axes.set_y(pb_txt_y)
                    text_pyplot_axes.set_text('British Parliament')
                    text_pyplot_axes.set_color('0.25')      
                    text_pyplot_axes.set_verticalalignment('center')              
                    text_pyplot_axes.set_horizontalalignment('left')
                    text_pyplot_axes.set_fontsize(10)
                    list_items.append(text_pyplot_axes)
                    #list_items.append(ax.text(pb_txt_x, pb_txt_y, 'British Parliament', verticalalignment='center', horizontalalignment='left', color='0.25', fontsize=10))  
                    legislation_count += 1       
                legislation_count += add_legislation(list_items, active_british_legislation, pb_txt_x, y_offset, reference_legislation, legislation_count)

        #protection boards
        if display_protection_boards:
            protection_boards = state_protection_boards[(current_year >= state_protection_boards.From) & (current_year < state_protection_boards.To) & (state_pb.State == state_protection_boards.State)]
            for index, protection_board in protection_boards.iterrows():
                impact_colour = 'm'
                if protection_board['Impact'] == 'Positive':
                    impact_colour = '0.25'

                #print(protection_board['BoardName'])                                
                text_pyplot_axes = reference_legislation[legislation_count]
                text_pyplot_axes.set_x(pb_txt_x)
                text_pyplot_axes.set_y(pb_txt_y)
                text_pyplot_axes.set_text(protection_board['BoardName'])
                text_pyplot_axes.set_color(impact_colour)      
                text_pyplot_axes.set_verticalalignment('center')              
                text_pyplot_axes.set_horizontalalignment('left')
                text_pyplot_axes.set_fontsize(8)
                list_items.append(text_pyplot_axes)
                #pb_txt = ax.text(pb_txt_x, pb_txt_y, protection_board['BoardName'], horizontalalignment='left', color=impact_colour, fontsize=8)
                #list_items.append(pb_txt)
                legislation_count += 1
    
    #print("Legislation count: " + str(legislation_count))

def add_legislation(list_items, df_legislation, anchor_x_offset, anchor_y_offset, reference_legislation, legislation_count):
    """
        Transform from source to target coordinates.

        Parameters
        ----------
        list_items
            ist: MatplotLib ax objects to be drawn for this animation frame

        df_legislation
            Dataframe: legislation to list

        anchor_x_offset
            Float: geocoordinate latitude to start listing from

        anchor_y_offset
            Float: geocoordinate longitude to start listing from

        reference_legislation
            List: pre-initialised MatPlotLib ax objects to use in mapping legislation text

        legislation_count
            Integer: current count of legislation that has been added so far

        Returns
        -------
        legal_count
            Integer: count of legislation items added, building on the legislation_count value at beginning of function call
    """
    legal_count = legislation_count

    y_offset = anchor_y_offset - 0.25
    for index, legislation in df_legislation.iterrows():
        y_offset -= 0.25
        impact_colour = '#cf210a'
        if legislation['Impact'] == '+':
            impact_colour = '0.25'

        text_pyplot_axes = reference_legislation[legal_count]
        text_pyplot_axes.set_x(anchor_x_offset)
        text_pyplot_axes.set_y(y_offset)
        text_pyplot_axes.set_text(legislation['Legislation Name'])
        text_pyplot_axes.set_color(impact_colour)   
        text_pyplot_axes.set_verticalalignment('center')
        text_pyplot_axes.set_horizontalalignment('left')
        text_pyplot_axes.set_fontsize(6)
        list_items.append(text_pyplot_axes)
        #legal_txt = ax.text(anchor_x_offset, y_offset, legislation['Legislation Name'], horizontalalignment='left', color=impact_colour, fontsize=6)
        #list_items.append(legal_txt)
        legal_count += 1

    return legal_count
    
def map_explorers(current_year, list_items):
    """
        Map path of explorers

        Parameters
        ----------
        current_year
            integer: current year to display
            
        list_items
            list: MatplotLib ax objects to be drawn for this animation frame
    """
    global reference_explorer_paths

    # clean up residual from previous year to avoid ghosting in generating movie
    for ax in reference_explorer_paths:
        ax.set_data([], [])

    num_explorer_paths = 0

    explorer_memory = 70
    explorer_start = current_year - explorer_memory
    explorer_files = explorers.loc[explorer_start:current_year]
    explorer_files.reset_index(inplace=True) #reclaiming index column
    list_explorers = []
    if len(explorer_files) > 0:
        for i in range(len(explorer_files)):
            explorer = explorer_files.iloc[i]
            explorer_from_date = explorer['From']
            explorer_to_date = explorer['To']
            explorer_name = explorer['Explorer']
            explorer_file_path = explorer['GeoJson']
            explorer_colour = 'purple'
            explorer_alpha = 1.0
            if explorer_from_date != explorer_to_date and explorer_to_date > current_year:
                #still exploring, results not published, so gradual realisation of path
                explorer_colour = 'grey'
                explorer_alpha = 1 / (explorer_to_date - current_year)
            elif current_year > explorer_to_date:
                #now in the past, so begin fading path from "memory"
                explorer_alpha = 1 - ((current_year - explorer_to_date)/explorer_memory)
                if explorer_alpha < 0:
                    explorer_alpha = 0
                            
            feature_ctr = 0    
            explorer_geo_path = pd.read_json('./data/' + explorer_file_path)
            features = explorer_geo_path['features']
            for feature in features:
                geometries = feature['geometry']
                coords = geometries['coordinates']
                df = pd.DataFrame(coords, columns=['longitude','latitude'])
                plot_pyplot_axes = reference_explorer_paths[num_explorer_paths]
                plot_pyplot_axes.set_data(df.longitude.values, df.latitude.values)
                plot_pyplot_axes.set_color(explorer_colour)
                plot_pyplot_axes.set_linestyle('dotted')
                plot_pyplot_axes.set_alpha(explorer_alpha)   
                list_items.append(plot_pyplot_axes)
                #explorer_line_plot, = ax.plot(df.longitude.values, df.latitude.values, color=explorer_colour, linestyle='dotted', alpha=explorer_alpha, zorder=explorer_zorder)  
                #list_items.append(explorer_line_plot)
                feature_ctr += 1
                num_explorer_paths += 1
            
            list_explorers.append([str(explorer_from_date) + " - " + str(explorer_to_date) + ": " + explorer_name, explorer_alpha])

        add_explorers(list_items, list_explorers, 106, -27.5, 'purple')

def add_explorers(list_items, explorer_list, anchor_x_offset, anchor_y_offset, colour):
    """
        List explorers in recent time window

        Parameters
        ----------            
        list_items
            list: MatplotLib ax objects to be drawn for this animation frame

        explorer_list
            list: names of explorers to list, processed in reverse order

        anchor_x_offset
            Float: geocoordinate latitude to start listing from

        anchor_y_offset
            Float: geocoordinate longitude to start listing from        
        
        colour
            String: colour of text
    """
    global reference_explorer_names

    # clean up residual from previous year to avoid ghosting in generating movie
    for ax in reference_explorer_names:
        ax.set_text("")

    y_offset = anchor_y_offset

    text_pyplot_axes = reference_explorer_names[0]
    text_pyplot_axes.set_x(anchor_x_offset)
    text_pyplot_axes.set_y(y_offset)
    text_pyplot_axes.set_text("Explorers")
    text_pyplot_axes.set_color(colour)
    text_pyplot_axes.set_fontsize(10)
    text_pyplot_axes.set_alpha(max([row[1] for row in explorer_list]))   
    list_items.append(text_pyplot_axes)
    #explorer_txt = ax.text(anchor_x_offset, y_offset, "Explorers", horizontalalignment='left', color=colour, fontsize=10, alpha=max([row[1] for row in explorer_list]))
    #list_items.append(explorer_txt)    
    y_offset -= 0.4
    for i in range(len(explorer_list) - 1, -1, -1):
        y_offset -= 0.34

        text_pyplot_axes = reference_explorer_names[i + 1]
        text_pyplot_axes.set_x(anchor_x_offset)
        text_pyplot_axes.set_y(y_offset)
        text_pyplot_axes.set_text(explorer_list[i][0])
        text_pyplot_axes.set_color(colour)
        text_pyplot_axes.set_fontsize(7)
        text_pyplot_axes.set_alpha(explorer_list[i][1])   
        list_items.append(text_pyplot_axes)
        #explorer_txt = ax.text(anchor_x_offset, y_offset, explorer_list[i][0], horizontalalignment='left', color=colour, fontsize=7, alpha=explorer_list[i][1])
        #list_items.append(explorer_txt)


def map_massacres(current_year, list_items):
    """
        Map locations of massacres

        Parameters
        ----------
        current_year
            integer: current year to display
            
        list_items
            list: MatplotLib ax objects to be drawn for this animation frame
    """
    global massacre_scatter

    earliest_recorded_massacre = massacres.index[0]
    anime_massacre_duration = final_anime_year - earliest_recorded_massacre

    if current_year >= earliest_recorded_massacre:
        massacre_sites = massacres.loc[earliest_recorded_massacre:current_year]
        list_massacres = []
        previous_massacre_year = earliest_recorded_massacre

        if len(massacre_sites) > 0:
            lat = massacre_sites['properties.latitude'].values
            lon = massacre_sites['properties.longitude'].values
            victims_dead = massacre_sites['properties.VictimsDead'].values
            attackers_dead = massacre_sites['properties.AttackersDead'].values                    
            massacre_dates = massacre_sites['properties.datestart'].values
            known_date = massacre_sites['properties.KnownDate'].values
            language_group = massacre_sites['properties.LanguageGroup'].values
            attackers = massacre_sites['properties.Attackers'].values
            victims = massacre_sites['properties.Victims'].values
            weapons = massacre_sites['properties.WeaponsUsed'].values

            massacre_plot_locations = np.zeros(len(massacre_sites), dtype=[('position', float, 2)])
            massacre_size = np.zeros(len(massacre_sites), dtype=int)
            massacre_colour = np.empty(len(massacre_sites), dtype=object)  
            massacre_alpha = np.ones(len(massacre_sites), dtype=float)     

            num_attacks_by_colonists = 0
            num_colonist_attackers_dead = 0
            num_colonist_victims_dead = 0
            num_attacks_by_Aboriginals = 0  
            num_Aboriginal_attackers_dead = 0
            num_Aboriginal_victims_dead = 0          

            for i in range(len(massacre_sites)):
                massacre_plot_locations['position'][i][0] = lon[i]
                massacre_plot_locations['position'][i][1] = lat[i]

                number_dead = int(victims_dead[i]) + int(attackers_dead[i])

                massacre_size[i] = massacre_display_size(number_dead)

                massacre_year = int(pd.to_datetime(massacre_dates[i]).year)
                massacre_colour[i], massacre_alpha[i] = massacre_display_colour(current_year, massacre_year, anime_massacre_duration)    

                if massacre_year - previous_massacre_year > 1:
                    for no_massacre_year in range(1, massacre_year - previous_massacre_year):
                        list_massacres.append(["", massacre_colour[i]])
                        
                previous_massacre_year = massacre_year    

                if pd.isna(known_date[i]):
                    massacre_known_date = str(massacre_year)
                else:
                    massacre_known_date = str(known_date[i])
                        
                if pd.isna(language_group[i]):
                    first_nations_language = ""
                else:
                    first_nations_language = str(language_group[i])

                if pd.isna(weapons[i]):
                    weapons_used = ""
                else:
                    weapons_used = str(weapons[i])
                        
                list_massacres.append(["", massacre_colour[i]])

                massacre_text = "".join(["Attack involved ", weapons_used])
                wrapped_lines = textwrap.wrap(text=massacre_text, width=63, subsequent_indent="      ")
                for line_number in range(len(wrapped_lines) - 1, -1, -1):
                    list_massacres.append([wrapped_lines[line_number], massacre_colour[i]])

                massacre_text = "".join([str(attackers[i]), " attacked ", str(victims[i])])
                wrapped_lines = textwrap.wrap(text=massacre_text, width=63, subsequent_indent="      ")
                for line_number in range(len(wrapped_lines) - 1, -1, -1):
                    list_massacres.append([wrapped_lines[line_number], massacre_colour[i]])

                massacre_text = "".join([str(number_dead), " dead. Attackers: ", str(attackers_dead[i]), ", Victims: ", str(victims_dead[i])])
                wrapped_lines = textwrap.wrap(text=massacre_text, width=63, subsequent_indent="      ")
                for line_number in range(len(wrapped_lines) - 1, -1, -1):
                    list_massacres.append([wrapped_lines[line_number], massacre_colour[i]])     

                massacre_text = "".join([massacre_known_date, " - ", first_nations_language])
                wrapped_lines = textwrap.wrap(text=massacre_text, width=63, subsequent_indent="      ")
                for line_number in range(len(wrapped_lines) - 1, -1, -1):
                    list_massacres.append([wrapped_lines[line_number], massacre_colour[i]])     

                # Count dead betwween colonial initiated conflicts and First Nations initiated conflicts
                # Not currently counting First Nations vs First Nations conflicts in the running totals
                if attackers[i] == "Colonists":
                    num_attacks_by_colonists += 1
                    num_colonist_attackers_dead += int(attackers_dead[i])
                    num_colonist_victims_dead += int(victims_dead[i])
                elif attackers[i][:10] == "Aboriginal":
                    num_attacks_by_Aboriginals += 1
                    num_Aboriginal_attackers_dead += int(attackers_dead[i])
                    num_Aboriginal_victims_dead += int(victims_dead[i])

            #TODO, create individual ax.scatter objects each with their own alpha values
            massacre_scatter.set_offsets(massacre_plot_locations['position'])
            massacre_scatter.set_sizes(massacre_size)
            massacre_scatter.set_facecolors(massacre_colour)
            massacre_scatter.set_edgecolors('#690a03')
            list_items.append(massacre_scatter)

            last_massacre_year = int(pd.to_datetime(massacre_dates[-1]).year)
            if last_massacre_year < current_year:
                for i in range (1, current_year - last_massacre_year):
                    list_massacres.append(["", massacre_colour[0]])

            list_massacres.append(["", massacre_colour[0]])
            list_massacres.append(["", massacre_colour[0]])
            list_massacres.append(["".join(['{:,}'.format(num_attacks_by_Aboriginals), " attacks by First Nations; ", '{:,}'.format(num_Aboriginal_victims_dead), " victims. ", '{:,}'.format(num_Aboriginal_attackers_dead), " attackers died"]), massacre_colour[0]])
            list_massacres.append(["".join(['{:,}'.format(num_attacks_by_colonists), " attacks by colonists; ", '{:,}'.format(num_colonist_victims_dead), " victims. ", '{:,}'.format(num_colonist_attackers_dead), " attackers died"]), massacre_colour[0]])
            list_massacres.append(["".join(['{:,}'.format(num_attacks_by_colonists + num_attacks_by_Aboriginals), " identified massacre events; ", '{:,}'.format(num_colonist_attackers_dead + num_colonist_victims_dead + num_Aboriginal_attackers_dead + num_Aboriginal_victims_dead), " dead"]), massacre_colour[0]])

            if display_massacre_text:
                add_massacres(list_items, list_massacres, 161.7, -11.25)

def add_massacres(list_items, massacre_list, anchor_x_offset, anchor_y_offset):
    """
        List massacres in recent time window

        Parameters
        ----------            
        list_items
            list: MatplotLib ax objects to be drawn for this animation frame

        massacre_list
            list: text fragments of massacres to list, processed in reverse order

        anchor_x_offset
            Float: geocoordinate latitude to start listing from

        anchor_y_offset
            Float: geocoordinate longitude to start listing from 
    """
    global reference_massacre_lines, number_massacre_lines_to_display

    # clean up residual from previous year to avoid ghosting in generating movie
    for ax in reference_massacre_lines:
        ax.set_text("")
   
    y_offset = anchor_y_offset
    
    text_pyplot_axes = reference_massacre_lines[-1]
    text_pyplot_axes.set_x(anchor_x_offset)
    text_pyplot_axes.set_y(y_offset)
    text_pyplot_axes.set_text("Massacres")
    text_pyplot_axes.set_color(massacre_list[0][1])
    text_pyplot_axes.set_fontsize(10)
    text_pyplot_axes.set_alpha(1)   
    list_items.append(text_pyplot_axes)  
    #massacre_txt = ax.text(anchor_x_offset, y_offset, "Massacres", horizontalalignment='left', color=massacre_list[0][1], fontsize=10)
    #list_items.append(massacre_txt) 

    last_massacre_events = massacre_list[(-1 * number_massacre_lines_to_display):]
    y_offset -= 0.68

    alpha_array = np.ones(number_massacre_lines_to_display, dtype=float)

    '''
    # linear fade: y = 1/x
    for i in range(len(alpha_array)):
        if len(alpha_array) - i > 5:
            alpha_array[i] = i/(len(alpha_array) - 5)
    '''

    # radial fade: x^2 + y^2 = r^2
    for i in range(len(alpha_array)):
        if len(alpha_array) - i > 5:
            alpha_array[i] = math.sqrt(1 - (1 - ((i + 1) / (len(alpha_array) - 5)))**2)

    #iterate through the massacre events backwards so that the latest entries are at the top and oldest at the bottom
    for i in range(len(last_massacre_events) - 1, -1, -1):
        y_offset -= 0.34

        alpha_pointer = len(alpha_array)
        alpha_pointer = alpha_pointer - (len(last_massacre_events) - i)
        
        massacre_event_txt = last_massacre_events[i][0]

        text_pyplot_axes = reference_massacre_lines[i]
        text_pyplot_axes.set_x(anchor_x_offset)
        text_pyplot_axes.set_y(y_offset)
        text_pyplot_axes.set_text(massacre_event_txt)
        text_pyplot_axes.set_color(massacre_list[i][1])
        text_pyplot_axes.set_fontsize(7)   
        text_pyplot_axes.set_alpha(alpha_array[alpha_pointer])
        list_items.append(text_pyplot_axes)  
        #massacre_txt = ax.text(anchor_x_offset, y_offset, massacre_event_txt, horizontalalignment='left', color=last_massacre_events[i][1], fontsize=7, alpha=alpha_array[alpha_pointer])
        #list_items.append(massacre_txt)

def massacre_display_colour(current_year, massacre_year, anime_massacre_duration):
    """
        Determine colour for massacre based on age of event

        Parameters
        ----------            
        current_year
            Integer: current year to determine age of event from

        massacre_year
            Integer: year of the event

        anime_massacre_duration
            Integer: number of years over which the animation spans

        Returns
        -------
        current_massacre_colour
            String: hex colour for massacre based on the age of the event

        massacre_alpha
            Float: Degree of transparency based on the age of the event
    """
    time_passed = current_year - massacre_year

    #cf210a
    red_base = 207
    green_base = 33
    blue_base = 10

    #690a03
    red_target = 105
    green_target = 10
    blue_target = 3

    yearly_red_increment = anime_massacre_duration / (red_base - red_target)
    yearly_green_increment = anime_massacre_duration / (green_base - green_target)
    yearly_blue_increment = anime_massacre_duration / (blue_base - blue_target)

    red_delta = int(time_passed / yearly_red_increment)
    green_delta = int(time_passed / yearly_green_increment)
    blue_delta = int(time_passed / yearly_blue_increment)

    red_value = red_base - red_delta
    green_value = green_base - green_delta
    blue_value = blue_base - blue_delta

    current_massacre_colour = "#" + hex(red_value)[2:].rjust(2, "0") + hex(green_value)[2:].rjust(2, "0") + hex(blue_value)[2:].rjust(2, "0")

    massacre_alpha = 1 - (time_passed / anime_massacre_duration) / 2

    return current_massacre_colour, massacre_alpha

def massacre_display_size(number_dead):
    """
        Determine diameter of massacre to display based on number of dead

        Parameters
        ----------            
        number_dead
            Integer: number who died in the event

        Returns
        -------
        current_massacre_colour
            String: hex colour for massacre based on the age of the event

        massacre_diam
            Integer: diameter of circle to display massacre
    """
    massacre_diam = 0
    # number ranges from 6 to 200
    '''
    if number_dead <= 10:
        massacre_diam = 4
    elif number_dead <= 20:
        massacre_diam = 8
    elif number_dead <= 40:
        massacre_diam = 16
    elif number_dead <= 80:
        massacre_diam = 32
    elif number_dead <= 100:
        massacre_diam = 64
    elif number_dead <= 200:
        massacre_diam = 128
    elif number_dead > 200:
        massacre_diam = 256
    return massacre_diam
    '''
    massacre_diam = number_dead
    return massacre_diam


def add_deaths_in_custody(current_year, list_items):
    """
        Display Aboriginal and Torres Strait Islander deaths in custody

        Parameters
        ----------
        current_year
            integer: current year to display
            
        list_items
            list: MatplotLib ax objects to be drawn for this animation frame
    """
    global death_in_custody_royal_commission_1_txt, death_in_custody_royal_commission_2_txt, death_in_custody_txt, aggregate_deaths_in_custody_txt

    anchor_x_offset = 133.5
    y_offset = -41.5

    earliest_recorded_death_in_custody = deaths_in_custody.index[0]

    if current_year >= 1987 and current_year <= 1991:
        commission_alpha = (current_year - 1987) / (1991 - 1987)
    else:
        commission_alpha = 1
    
    if current_year >= 1987: 
        death_in_custody_royal_commission_1_txt.set_x(anchor_x_offset)
        death_in_custody_royal_commission_1_txt.set_y(y_offset)
        death_in_custody_royal_commission_1_txt.set_text('1987-1991: Royal Commission Report into')
        death_in_custody_royal_commission_1_txt.set_alpha(commission_alpha)
        list_items.append(death_in_custody_royal_commission_1_txt)  
        y_offset -= 0.4 
        death_in_custody_royal_commission_2_txt.set_x(anchor_x_offset)
        death_in_custody_royal_commission_2_txt.set_y(y_offset)
        death_in_custody_royal_commission_2_txt.set_text('     Aboriginal Deaths in Custody released')
        death_in_custody_royal_commission_2_txt.set_alpha(commission_alpha)
        list_items.append(death_in_custody_royal_commission_2_txt)
    else:
        y_offset -= 0.4
    
    y_offset -= 0.8

    if current_year >= earliest_recorded_death_in_custody:
        deaths_in_custody_to_current_year = deaths_in_custody.loc[:current_year]
        deaths_in_custody_in_current_year = deaths_in_custody_to_current_year.iloc[-1]
        deaths_in_custody_aggregate = deaths_in_custody_to_current_year['Total'].sum()

        death_in_custody_txt.set_x(anchor_x_offset)
        death_in_custody_txt.set_y(y_offset)
        death_in_custody_txt.set_text('First Nations deaths in custody in current year: ' + str(deaths_in_custody_in_current_year['Total']))
        list_items.append(death_in_custody_txt)
        y_offset -= 0.4
        aggregate_deaths_in_custody_txt.set_x(anchor_x_offset)
        aggregate_deaths_in_custody_txt.set_y(y_offset)
        aggregate_deaths_in_custody_txt.set_text('First Nations deaths in custody since 1980: ' + str(deaths_in_custody_aggregate))
        list_items.append(aggregate_deaths_in_custody_txt)

def add_incarcerated(current_year, list_items):
    """
        Display Aboriginal and Torres Strait Islander incarceration numbers

        Parameters
        ----------
        current_year
            integer: current year to display
            
        list_items
            list: MatplotLib ax objects to be drawn for this animation frame
    """
    global incarcerated_indigenous_txt, incarcerated_nonindigenous_txt

    anchor_x_offset = 133.5
    y_offset = -43.9

    earliest_incarceration = incarceration_rates.index[0]

    if current_year >= earliest_incarceration:
        incarcerated_indigenous = incarceration_rates.loc[current_year]['Aboriginal and Torres Strait Islander']
        incarcerated_nonindigenous =  incarceration_rates.loc[current_year]['Non-Indigenous']
        
        incarcerated_indigenous_txt.set_x(anchor_x_offset)
        incarcerated_indigenous_txt.set_y(y_offset)
        incarcerated_indigenous_txt.set_text('First Nations incarcerated in current year: ' + '{:,}'.format(incarcerated_indigenous))
        list_items.append(incarcerated_indigenous_txt)
        y_offset -= 0.4
        incarcerated_nonindigenous_txt.set_x(anchor_x_offset)
        incarcerated_nonindigenous_txt.set_y(y_offset)
        incarcerated_nonindigenous_txt.set_text('Non-Indigenous incarcerated in current year: ' + '{:,}'.format(incarcerated_nonindigenous))
        list_items.append(incarcerated_nonindigenous_txt)


def map_towns(current_year, list_items):
    """
        Map town and city locations based on their founding date

        Parameters
        ----------
        current_year
            integer: current year to display
            
        list_items
            list: MatplotLib ax objects to be drawn for this animation frame
    """
    global town_scatter

    start_slice = 0
    if cities.index.min() < colonial_epoch:
        start_slice = colonial_epoch
    else:
        start_slice = cities.index.min()
    colonial_period_cities = cities.loc[start_slice:current_year]
    if len(colonial_period_cities) > 0:
        lat = colonial_period_cities[7].values
        lon = colonial_period_cities[8].values
        pop = colonial_period_cities[11].values

        plot_locations = np.zeros(len(colonial_period_cities), dtype=[('position', float, 2)])
        pop_size = np.zeros(len(colonial_period_cities), dtype=int)
        city_colour = np.empty(len(colonial_period_cities), dtype=object)

        size_town(colonial_period_cities, current_year, lat, lon, pop, plot_locations, pop_size, city_colour, -1)
      
        town_scatter.set_offsets(plot_locations['position'])
        town_scatter.set_sizes(pop_size)
        town_scatter.set_color(city_colour)
        #colonial_scat.set_zorder(city_zorder)
        list_items.append(town_scatter)

def map_undated_towns(current_year, list_items):
    """
        Map town and city locations for those that do not have a founding date in their data

        Parameters
        ----------
        current_year
            integer: current year to display
            
        list_items
            list: MatplotLib ax objects to be drawn for this animation frame
    """
    global unknown_town_est_year_scatter

    lat = undated_cities[7].values
    lon = undated_cities[8].values
    pop = undated_cities[11].values

    plot_locations = np.zeros(len(undated_cities), dtype=[('position', float, 2)])
    pop_size = np.zeros(len(undated_cities), dtype=int)
    city_colour = np.empty(len(undated_cities), dtype=object)

    city_perc = 1 - (final_anime_year - current_year)/(final_anime_year - start_of_town_growth)

    size_town(undated_cities, current_year, lat, lon, pop, plot_locations, pop_size, city_colour, city_perc)

    unknown_town_est_year_scatter.set_offsets(plot_locations['position'])
    unknown_town_est_year_scatter.set_sizes(pop_size)
    unknown_town_est_year_scatter.set_color(city_colour)
    # as we don't know their establishment dates, fade them in, in the last 100 years
    unknown_town_est_year_scatter.set_alpha(city_perc)
    list_items.append(unknown_town_est_year_scatter)

def size_town(cities, current_year, lat, lon, pop, plot_locations, pop_size, city_colour, city_perc):
    """
        Display Aboriginal and Torres Strait Islander deaths in custody

        Parameters
        ----------
        cities
            Dataframe: data read from file
        
        current_year
            integer: current year to display
        
        lat
            Float: geocoordinate latitude to start listing from
        
        lon
            Float: geocoordinate longitude to start listing from
        
        pop
            Integer: population size of town or city
        
        plot_locations
            Numpy 2D Float Array: empty array to hold location for town
        
        pop_size
            Numpy Integer Array: empty array to hold size of town / city
        
        city_colour
            Numpy Object Array: empty array to hold colour string in or town / city, changes as the settlement ages
        
        city_perc
            Float: size factor of city to display, only used for undated cities to grow to full size over time
    """
    for i in range(len(cities)):
        plot_locations['position'][i][0] = lon[i]
        plot_locations['position'][i][1] = lat[i]

        if city_perc < 0:
            settlement_year = cities.index[i]
            town_age = final_anime_year - settlement_year
            if town_age != 0:
                pop_per_year = pop[i] / town_age
                current_town_age = current_year - settlement_year
                current_town_pop = pop_per_year * current_town_age

                red_delta = int(current_town_age / 9.2)
                green_delta = int(current_town_age / 3.5)
                blue_delta = int(current_town_age / 1.77)
            else:
                current_town_pop = 0

                red_delta = int(0)
                green_delta = int(0)
                blue_delta = int(0)
        else:
            current_town_pop = pop[i] * city_perc

            red_delta = int(0)
            green_delta = int(0)
            blue_delta = int(0)
                    
        #250, 210, 140 - #FAD28C
        #225, 145, 10 - #E1910A

        #230 years
        # R reduce 1 every 9.2 years
        # G reduce 1 every 3.5 years
        # B reduce 1 every 1.77 years

        red_value = 250 - red_delta
        green_value = 210 - green_delta
        blue_value = 140 - blue_delta

        current_city_colour = "#" + hex(red_value)[2:].rjust(2, "0") + hex(green_value)[2:].rjust(2, "0") + hex(blue_value)[2:].rjust(2, "0")
        city_colour[i] = current_city_colour      

        pop_size[i] = town_display_size(current_town_pop)

def town_display_size(current_town_pop):
    """
        Calculate town / city size to display based on population size

        Parameters
        ----------
        current_town_pop
            Integer: population of town / city

        Returns
        -------
        return
            display size of town / city

    """
    if pd.isna(current_town_pop):
        pop = 4
    else:
        pop = current_town_pop
    
    # treat the population as a volume of a sphere and return the radius
    # V = (4/3)*pi*r^3
    return int((((6*pop)/np.pi)**(1/3))/2)

def map_railway_lines(current_year, list_items):
    """
        Map railway lines

        Parameters
        ----------        
        current_year
            integer: current year to display
            
        list_items
            list: MatplotLib ax objects to be drawn for this animation frame
    """
    commenced_lines = railway_operating_dates[((railway_operating_dates['Commenced'] <= current_year) & (railway_operating_dates['Opened'] > current_year) & ((railway_operating_dates['Closed'] > current_year) | (railway_operating_dates['Closed'].isna())))]
    opened_lines = railway_operating_dates[((railway_operating_dates['Opened'] <= current_year) & ((railway_operating_dates['Closed'] > current_year) | (railway_operating_dates['Closed'].isna())))]
    closed_lines = railway_operating_dates[(railway_operating_dates['Closed'] <= current_year)]
    
    num_railway_segments = 0
    for i in range(len(commenced_lines)):
        num_railway_segments =+ map_railway_segments(list_items, commenced_lines, i, num_railway_segments, '0.5', 'dashed')

    for i in range(len(opened_lines)):   
        num_railway_segments =+ map_railway_segments(list_items, opened_lines, i, num_railway_segments, '0.3', '-')   

    for i in range(len(closed_lines)):   
        num_railway_segments =+ map_railway_segments(list_items, closed_lines, i, num_railway_segments, '0.6', 'dotted') 

    #print("Number of railway segments: " + str(num_railway_segments)) 

def map_railway_segments(list_items, mapped_lines, i, num_railway_segments, colour='0.3', line_style='-'):
    """
        Map railway segments for a specific railway line

        Parameters
        ----------
        list_items
            list: MatplotLib ax objects to be drawn for this animation frame

        mapped_lines
            list: railway segments to be mapped for railway line

        i
            Integer: count of railway lines being mapped for current railway status - commenced, open, closed
        
        num_railway_segments
            Integer: number of railway segments counted so far in mapping the railway lines
        
        (Optional) colour
            String: colour of railway line
                defaults to '0.3'        
        
        (Optional) line_style
            String: line style for railway line 
                defaults to '-'

        Returns
        -------
        railway_segment_ctr
            number of railway segments in mapped railway lines
    """
    global reference_railway_segments

    railway_segment_ctr = num_railway_segments

    line_name = mapped_lines.iloc[i]['Name']
    #print(line_name)
    railway_line = railways.loc[line_name]        
    if len(railway_line.shape) == 1:
        # single LineString
        plot_pyplot_axes = reference_railway_segments[railway_segment_ctr]
        plot_pyplot_axes.set_data([x[0] for x in railway_line['geometry.coordinates']], [y[1] for y in railway_line['geometry.coordinates']])
        plot_pyplot_axes.set_color(colour)
        plot_pyplot_axes.set_linestyle(line_style)
        list_items.append(plot_pyplot_axes)  
        #rail_line_plot, = ax.plot([x[0] for x in railway_line['geometry.coordinates']], [y[1] for y in railway_line['geometry.coordinates']], color=colour, linestyle=line_style, linewidth=0.7, zorder=railway_zorder)
        #list_items.append(rail_line_plot)
        railway_segment_ctr += 1
    elif len(railway_line.shape) == 2:
        # multiple LineStrings
        for line_coords_segment in railway_line['geometry.coordinates']:
            try:  
                # multiple line_name entries, line_coords_segment will be an array of lat/lon values
                if list_dimension(line_coords_segment) == 1:                    
                    plot_pyplot_axes = reference_railway_segments[railway_segment_ctr]
                    plot_pyplot_axes.set_data([line_coords_segment[0]], [line_coords_segment[1]])
                    plot_pyplot_axes.set_color(colour)
                    plot_pyplot_axes.set_linestyle(line_style)
                    list_items.append(plot_pyplot_axes)
                    #rail_line_plot, = ax.plot([line_coords_segment[0]], [line_coords_segment[1]], color=colour, linestyle=line_style, linewidth=0.7, zorder=railway_zorder)
                    #list_items.append(rail_line_plot)
                    railway_segment_ctr += 1
                elif list_dimension(line_coords_segment) == 2: 
                    plot_pyplot_axes = reference_railway_segments[railway_segment_ctr]
                    plot_pyplot_axes.set_data([x[0] for x in line_coords_segment], [y[1] for y in line_coords_segment])
                    plot_pyplot_axes.set_color(colour)
                    plot_pyplot_axes.set_linestyle(line_style)
                    list_items.append(plot_pyplot_axes)              
                    #rail_line_plot, = ax.plot([x[0] for x in line_coords_segment], [y[1] for y in line_coords_segment], color=colour, linestyle=line_style, linewidth=0.7, zorder=railway_zorder)
                    #list_items.append(rail_line_plot)
                    railway_segment_ctr += 1
                elif list_dimension(line_coords_segment) == 3:
                    # handle MultiLineStrings
                    for row in line_coords_segment:                        
                        plot_pyplot_axes = reference_railway_segments[railway_segment_ctr]
                        plot_pyplot_axes.set_data([x[0] for x in row], [y[1] for y in row])
                        plot_pyplot_axes.set_color(colour)
                        plot_pyplot_axes.set_linestyle(line_style)
                        list_items.append(plot_pyplot_axes)
                        #rail_line_plot, = ax.plot([x[0] for x in row], [y[1] for y in row], color=colour, linestyle=line_style, linewidth=0.7, zorder=railway_zorder)
                        #list_items.append(rail_line_plot)
                        railway_segment_ctr += 1
            except ValueError as err:
                print(f"Unexpected {err=}, {type(err)=}")
                print("Value Error processing commenced line: " + line_name)
                print(line_coords_segment)
            except Exception as err:
                print(f"Unexpected {err=}, {type(err)=}")
                print("Error processing commenced line: " + line_name)
                print(line_coords_segment)

    return railway_segment_ctr

def map_missions(current_year, list_items):
    """
        Map missions

        Parameters
        ----------        
        current_year
            integer: current year to display
            
        list_items
            list: MatplotLib ax objects to be drawn for this animation frame
    """
    global closed_mission_scatter, open_mission_scatter

    closed_missions = missions[((missions['To'] <= current_year) & pd.notna(missions['Lat']) & pd.notna(missions['Lon']))]
    if len(closed_missions) > 0:        
        plot_locations = np.zeros(len(closed_missions), dtype=[('position', float, 2)])         
        lon = closed_missions['Lon'].values
        lat = closed_missions['Lat'].values
        for i in range(len(closed_missions)):
            plot_locations['position'][i][0] = lon[i]
            plot_locations['position'][i][1] = lat[i]
        closed_mission_scatter.set_offsets(plot_locations['position'])
        list_items.append(closed_mission_scatter)

    open_missions = missions[((missions['From'] <= current_year) & (missions['To'] > current_year) & pd.notna(missions['Lat']) & pd.notna(missions['Lon']))]
    if len(open_missions) > 0:
        plot_locations = np.zeros(len(open_missions), dtype=[('position', float, 2)])  
        lon = open_missions['Lon'].values
        lat = open_missions['Lat'].values
        for i in range(len(open_missions)):
            plot_locations['position'][i][0] = lon[i]
            plot_locations['position'][i][1] = lat[i]
        open_mission_scatter.set_offsets(plot_locations['position'])
        list_items.append(open_mission_scatter)


def list_dimension(testlist, dim=0):
    """
        determine number of dimensions that a list holds, calls itself recursively

        Parameters
        ----------
        testlist
            list: list to be tested

        (Optional) dim
            list: current call depth in recursion

        Returns
        -------
        dim
            returns the dimension in current recursive call
    """
   # tests if testlist is a list and how many dimensions it has
   # returns -1 if it is no list at all, 0 if list is empty 
   # and otherwise the dimensions of it - from Stackoverflow by https://stackoverflow.com/users/4112844/bunkus
    if isinstance(testlist, list):
        if testlist == []:
            return dim
        dim = dim + 1
        dim = list_dimension(testlist[0], dim) #recursion to the end of the dimensions
        return dim
    else:
        if dim == 0:
            return -1
        else:
            return dim


#fetch data
population, state_boundaries, first_nations_milestones, australian_conflicts = init_file_load(display_state_boundaries, display_first_nations_milestones, display_australian_conflict)

if display_colonisation:
    explorers, cities, undated_cities, railways, railway_operating_dates, massacres, missions, deaths_in_custody, incarceration_rates, defining_moments \
        = init_colonial_file_load(display_explorers, display_towns, display_undated_towns, display_railway_lines, display_massacre_sites, display_missions, display_deaths_in_custody, display_incarceration_rates, display_defining_moments)

    #set up legend with dummy scatter points and plot lines
    #lat, lon, size, lw=, edgecolors=, facecolors=, zorder
    town_scat = ax.scatter([], [], s=20, c="#e1910a", zorder=town_zorder)
    #unknown_town_est_year_scat = ax.scatter([], [], s=20, c="#e1910a", zorder=50)
    massacre_scat = ax.scatter([], [], s=20, c="#cf210a", zorder=massacre_zorder)
    mission_plot = ax.scatter([], [], marker='D', s=10, c="blue", zorder=mission_zorder)
    explorer_plot, = ax.plot([],[], color='purple', linestyle='dotted', alpha=1, zorder=explorer_zorder)
    railway_plot, = ax.plot([],[], color='0.3', linestyle='-', linewidth=0.7, zorder=railway_zorder)

    legend_list = []
    legend_label_list = []
    if display_massacre_sites:
        legend_list.append(massacre_scat)
        legend_label_list.append('Massacres')
    if display_missions:
        legend_list.append(mission_plot)
        legend_label_list.append('Missions and Reserves')
    if display_towns or display_undated_towns:
        legend_list.append(town_scat)
        legend_label_list.append('Towns and Cities')
    if display_explorers:
        legend_list.append(explorer_plot)
        legend_label_list.append('Explorers')
    if display_railway_lines:
        legend_list.append(railway_plot)
        legend_label_list.append('Railways')   

    if legend_list:
        plt.legend(legend_list, legend_label_list, loc='lower left')   

elif display_legal_controls:
    state_protection_boards, british_legislation, commonwealth_legislation, act_legislation, qld_legislation, wa_legislation, sa_legislation, nsw_legislation, nt_legislation, tas_legislation, vic_legislation = init_legal_file_load()

if display_white_blak_hx_back_to_back:
    white_to_blak = 2
else: 
    white_to_blak = 1

anim = animation.FuncAnimation(plt.gcf(), update_year, frames=(timelapse_period + (number_repeat_frames_at_start_and_end * 2)) * white_to_blak, interval=anime_interval, blit=True, repeat=loop_display, init_func=init)

if display_white_blak_hx_back_to_back:
    output_file_name = 'Australia in 4 minutes - a White and Blak history.mp4'
elif display_blak_history:
    output_file_name = 'Australia in 2 minutes - a Blak history.mp4'
else:
    output_file_name = 'Australia in 2 minutes - a White history.mp4'

#ffmpeg
anim.save(output_file_name, extra_args=['-vcodec', 'h264', '-framerate', '2', '-vf', 'fps=24', '-pix_fmt', 'yuv420p'])
#plt.show()

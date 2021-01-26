"""Creates an animation covering the colonialisation of Australia and the impact on the Indigenous population
"""

import pandas as pd
import re
from datetime import date

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Rectangle
from matplotlib.collections import PatchCollection
import matplotlib.gridspec as gridspec
import matplotlib.animation as animation
import matplotlib.colors as colour

import cartopy.crs as ccrs
import cartopy

__author__ = "Andrew Arch"
__copyright__ = "Copyright 2020"
__license__ = "GPL"
__version__ = "1.1.0"
__maintainer__ = "Andrew Arch"
__email__ = "andy.arch11@gmail.com"
__status__ = "Production"

#Select what to display
display_state_boundaries = True
loop_display = True

display_colonisation = False
display_towns = display_colonisation
display_explorers = display_colonisation

display_legal_controls = not display_colonisation
display_legislation = display_legal_controls
display_protection_boards = display_legal_controls

image_title = ''
if display_colonisation:
    image_title = 'Colonisation of Australia'
elif display_legal_controls:
    image_title = 'Legislative Control of Australian First Nations'

#create figure to host animation.  N.B. if this is declared after Basemap, it will plot points to its own window
fig = plt.figure(figsize=[17, 13], constrained_layout=True)
#ax = fig.add_subplot()

#draw map - Australia -26.8372557,127.5859928

# lon_0 is the central longitude of the projection.
# resolution = 'l' means use low resolution coastlines.
# optional parameter 'satellite_height' may be used to
# specify height of orbit above earth (default 35,786 km).

lon_0=127.5860
lat_0=-26.8373
#mrc = ccrs.LambertConformal(lon_0, lat_0)
mrc = ccrs.PlateCarree()
xlon0=110
xlon1=165
ylat0=-46
ylat1=-7

#ax = fig.add_subplot(1, 1, 1, projection=mrc)
ax = plt.axes(projection=mrc)
ax.set_extent([xlon0, xlon1, ylat0, ylat1], crs=ccrs.PlateCarree())
ax.coastlines(resolution='50m', color='0', linewidth=0.25)
ax.add_feature(cartopy.feature.LAND, color='white')
ax.add_feature(cartopy.feature.OCEAN)
#ax.add_feature(cartopy.feature.LAKES, edgecolor='black', alpha=0.5)
#ax.add_feature(cartopy.feature.RIVERS)

ax.set_title(image_title)


#Title [0], City Name [1], State [2], wikipedia href [3], dms_latitude [4], dms_longitude [5], dec_latitude [6], dec_longitude [7], established date (city page) [8], established date (parent page) [9]
cities = pd.read_csv('./data/city_list.csv', header=None, quotechar='"', index_col=9)
state_boundaries = pd.read_csv('./data/States.csv', index_col='YearEffectiveFrom')
population = pd.read_csv('./data/population.csv', index_col='Year')
explorers = pd.read_csv('./data/Explorers.csv', index_col='From')
state_protection_boards = pd.read_csv('./data/Aboriginal Protector Boards.csv')

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

# https://www.captaincooksociety.com/home/detail/the-first-voyage-1768-1771
# Captain Cook left Plymouth Aug 1768
# Arrived at Rio de Janeiro Nov 1768
# Arrived at Tierra del Fuego Jan 1769
# Arrived at Tahiti April 1769 for the Transit of Venus observation - 3rd June 1769. Kills natives
# Arrived at New Zealand Oct 1769.  Kills natives
# Arrived at Australia April 1770, first sighting Point Hicks (Cape Everard) in Victoria 19th April 1770, 
# sailing north to Possession Island in the Torres Strait, stopping at Botany Bay and Cooktown
colonial_epoch = 1768 
timelapse_period = 2020 - colonial_epoch + 1

state_dictionary = {}
state_x_plots = {}
state_y_plots = {}
explorer_dictionary = {}
explorer_x_plots = {}
explorer_y_plots = {}
init_items = []
list_items = []

#set up legend with dummy scatter points and plot lines
#lat, lon, size, lw=, edgecolors=, facecolors=, zorder
scat = ax.scatter([], [], s=5, c="blue", zorder=100)
legend_plot, = ax.plot([],[], color='purple', linestyle='dotted', alpha=1)
if display_towns and display_explorers:
    plt.legend([scat, legend_plot], ['Cities', 'Explorers'], loc='lower left')
elif display_towns:
    plt.legend([scat], ['Cities'], loc='lower left')
elif display_explorers:
    plt.legend([legend_plot], ['Explorers'], loc='lower left')

#Initialise Population coords
pop_x1 = 0.025
pop_x2 = 0.22
pop_x3 = 0.24
pop_x4 = 0.45
pop_y1 = 0.13
pop_y2 = 0.115
pop_perc_width = 0.21

#set up percentage population bar
ax.add_patch(patches.Rectangle((pop_x3, 0.06), pop_perc_width, 0.02, transform=ax.transAxes, edgecolor='0.75', facecolor='white', linewidth=1.5))
perc_bar = Rectangle((pop_x3, 0.06), pop_perc_width, 0.02, transform=ax.transAxes, edgecolor='0.75', facecolor='black', linewidth=1.5, fill=True)

previous_year_indigenous_population = 750000
previous_year_non_indigenous_population = 0

def init():    
    list_init_items = []
    #create percentage bar  
    perc_bar.set_width(0.295) 
    ax.add_patch(perc_bar)
    list_init_items.append(perc_bar)
    return list_init_items

def add_legislation(list_items, df_legislation, anchor_x_offset, anchor_y_offset):
    y_offset = anchor_y_offset - 0.25
    for index, legislation in df_legislation.iterrows():
        y_offset -= 0.35
        impact_colour = 'r'
        if legislation['Impact'] == '+':
            impact_colour = '0.25'
        legal_txt = ax.text(anchor_x_offset, y_offset, legislation['Legislation Name'], horizontalalignment='left', color=impact_colour, fontsize=8)
        list_items.append(legal_txt)

def update_cities(frame):    
    current_frame = frame % (timelapse_period)
    current_year = colonial_epoch + current_frame
    pop_year = population.loc[current_year:current_year]
    pop_percentage = pop_year['Indigenous percentage'].values[0]
    pop_percentage_value = (float(pop_percentage.rstrip('%')))/100
    print('Current Year: ' + str(current_year))
    print('Pop Perc: ' + str(pop_percentage_value))

    current_year_indigenous_population = int(pop_year['Indigenous Population'].values[0].replace(',',''))
    current_year_non_indigenous_population = int(pop_year['Total Population'].values[0].replace(',','')) - current_year_indigenous_population

    global previous_year_indigenous_population
    global previous_year_non_indigenous_population
    indigenous_population_change = 0
    non_indigenous_population_change = 0

    if current_year != colonial_epoch:
        indigenous_population_change = current_year_indigenous_population - previous_year_indigenous_population  
        previous_year_indigenous_population = current_year_indigenous_population  

        non_indigenous_population_change = current_year_non_indigenous_population - previous_year_non_indigenous_population
        previous_year_non_indigenous_population = current_year_non_indigenous_population
    else:
        previous_year_indigenous_population = 750000
        previous_year_non_indigenous_population = 0

    #reset reference to a new list of items
    list_items = []
    
    #State boundaries
    if display_state_boundaries:
        boundary_row = state_boundaries[(current_year >= state_boundaries.index) & (current_year <= state_boundaries.YearEffectiveTo)]
        if len(boundary_row) > 0:
            state_boundary_path = boundary_row.GeoJsonFile.values[0]
            state_geo_paths = pd.read_json('./data/' + state_boundary_path)
            features = state_geo_paths['features']
            feature_ctr = 0       
            if (state_boundary_path + '_' + str(feature_ctr)) in state_dictionary:
            #if False:
                while (state_boundary_path + '_' + str(feature_ctr)) in state_dictionary:
                    x0 = state_x_plots[state_boundary_path + '_' + str(feature_ctr)]
                    y0 = state_y_plots[state_boundary_path + '_' + str(feature_ctr)]
                    state_line_plot, = ax.plot(x0,y0, color='0.7', linewidth=0.5) 
                    list_items.append(state_line_plot)
                    feature_ctr += 1
            else:
                for feature in features:
                    geometries = feature['geometry']
                    coords = geometries['coordinates']
                    df = pd.DataFrame(coords, columns=['longitude','latitude'])
                    state_line_plot, = ax.plot(df.longitude.values, df.latitude.values, color='0.7', linewidth=0.5)  
                    state_dictionary[state_boundary_path + '_' + str(feature_ctr)] = state_line_plot
                    state_x_plots[state_boundary_path + '_' + str(feature_ctr)] = df.longitude.values
                    state_y_plots[state_boundary_path + '_' + str(feature_ctr)] = df.latitude.values
                    list_items.append(state_line_plot)
                    feature_ctr += 1

            state_text_path = boundary_row.StateNameFile.values[0]
            state_names = pd.read_csv('./data/' + state_text_path)
            for index, state_name in state_names.iterrows(): 
                list_items.append(ax.text(float(state_name['Longitude']), float(state_name['Latitude']), state_name['StateName'], verticalalignment='center', horizontalalignment='left', color='0.6', fontsize=10))
    
    #explorer paths
    if display_explorers:
        explorer_start = current_year - 105
        explorer_files = explorers.loc[explorer_start:current_year]
        explorer_files.reset_index(inplace=True) #reclaiming index column
        if len(explorer_files) > 0:
            for i in range(len(explorer_files)):
                explorer = explorer_files.iloc[i]
                explorer_from_date = explorer['From']
                explorer_to_date = explorer['To']
                explorer_file_path = explorer['GeoJson']
                explorer_colour = 'purple'
                explorer_alpha = 1.0
                if explorer_from_date != explorer_to_date and explorer_to_date > current_year:
                    #still exploring, results not published, so gradual realisation of path
                    explorer_colour = 'grey'
                    explorer_alpha = 1 / (explorer_to_date - current_year)
                elif current_year > explorer_to_date:
                    #now in the past, so begin fading path from "memory"
                    explorer_alpha = 1 - ((current_year - explorer_to_date)/100)
                    if explorer_alpha < 0:
                        explorer_alpha = 0
                        
                feature_ctr = 0      
                if (explorer_file_path + '_' + str(feature_ctr)) in explorer_dictionary:
                    while (explorer_file_path + '_' + str(feature_ctr)) in explorer_dictionary:
                        x0 = explorer_x_plots[explorer_file_path + '_' + str(feature_ctr)]
                        y0 = explorer_y_plots[explorer_file_path + '_' + str(feature_ctr)]
                        explorer_line_plot, = ax.plot(x0,y0, color=explorer_colour, linestyle='dotted', alpha=explorer_alpha)
                        list_items.append(explorer_line_plot)

                        feature_ctr += 1
                else:
                    explorer_geo_path = pd.read_json('./data/' + explorer_file_path)
                    features = explorer_geo_path['features']
                    for feature in features:
                        geometries = feature['geometry']
                        coords = geometries['coordinates']
                        df = pd.DataFrame(coords, columns=['longitude','latitude'])
                        explorer_line_plot, = ax.plot(df.longitude.values, df.latitude.values, color=explorer_colour, linestyle='dotted', alpha=explorer_alpha)                   
                        explorer_dictionary[explorer_file_path + '_' + str(feature_ctr)] = explorer_line_plot
                        explorer_x_plots[explorer_file_path + '_' + str(feature_ctr)] = df.longitude.values
                        explorer_y_plots[explorer_file_path + '_' + str(feature_ctr)] = df.latitude.values
                        list_items.append(explorer_line_plot)
                        feature_ctr += 1

    #cities
    if display_towns:
        colonial_period_cities = cities.loc[colonial_epoch:current_year]
        if len(colonial_period_cities) > 0:
            lat = colonial_period_cities[6].values
            lon = colonial_period_cities[7].values

            plot_locations = np.zeros(len(colonial_period_cities), dtype=[('position', float, 2)])

            for i in range(len(colonial_period_cities)):
                plot_locations['position'][i][0] = lon[i]
                plot_locations['position'][i][1] = lat[i]
            scat.set_offsets(plot_locations['position'])
            list_items.append(scat)
    
    #Legislation
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

    print(active_nsw_legislation)
    #Aboriginal Protection Boards and Legislation
    pb_txt_locations = {'State':['VIC','NSW','WA','QLD','SA','NT','ACT','TAS','CTH','BRITAIN'],'Longitude':[142.0,143.0,117.0,140.0,130.0,130.0,153.0,145.5,110.7,111.0],'Latitude':[-37.5,-31.0,-25,-22.0,-28.0,-17.0,-36.2,-42.5,-12.6,-10.1]}
    pb_locations_df = pd.DataFrame(pb_txt_locations)
    for index, state_pb in pb_locations_df.iterrows():
            
        pb_txt_x = state_pb['Longitude']
        pb_txt_y = state_pb['Latitude']
        print(str(pb_txt_x) + ',' + str(pb_txt_y))

        #Legislation
        if display_legislation:
            y_offset = pb_txt_y - 0.25
            if state_pb['State'] == 'VIC':               
                add_legislation(list_items, active_vic_legislation, pb_txt_x, y_offset)
            elif state_pb['State'] == 'NSW':               
                add_legislation(list_items, active_nsw_legislation, pb_txt_x, y_offset)
            elif state_pb['State'] == 'WA':               
                add_legislation(list_items, active_wa_legislation, pb_txt_x, y_offset)
            elif state_pb['State'] == 'QLD':               
                add_legislation(list_items, active_qld_legislation, pb_txt_x, y_offset)
            elif state_pb['State'] == 'SA':               
                add_legislation(list_items, active_sa_legislation, pb_txt_x, y_offset)
            elif state_pb['State'] == 'NT':               
                add_legislation(list_items, active_nt_legislation, pb_txt_x, y_offset)
            elif state_pb['State'] == 'ACT':               
                y_offset -= 0.8
                add_legislation(list_items, active_act_legislation, pb_txt_x, y_offset)
            elif state_pb['State'] == 'TAS':               
                add_legislation(list_items, active_tas_legislation, pb_txt_x, y_offset)
            elif state_pb['State'] == 'CTH':
                if len(active_commonwealth_legislation) > 0:
                    list_items.append(ax.text(pb_txt_x, pb_txt_y, 'Commonwealth Parliament', verticalalignment='center', horizontalalignment='left', color='0.25', fontsize=10)) 
                add_legislation(list_items, active_commonwealth_legislation, pb_txt_x, y_offset)
            elif state_pb['State'] == 'BRITAIN':
                if len(active_british_legislation) > 0:
                    list_items.append(ax.text(pb_txt_x, pb_txt_y, 'British Parliament', verticalalignment='center', horizontalalignment='left', color='0.25', fontsize=10))         
                add_legislation(list_items, active_british_legislation, pb_txt_x, y_offset)

        #protection boards
        if display_protection_boards:
            protection_boards = state_protection_boards[(current_year >= state_protection_boards.From) & (current_year < state_protection_boards.To) & (state_pb.State == state_protection_boards.State)]
            for index, protection_board in protection_boards.iterrows():
                impact_colour = 'm'
                if protection_board['Impact'] == 'Positive':
                    impact_colour = '0.25'

                print(protection_board['BoardName'])
                pb_txt = ax.text(pb_txt_x, pb_txt_y, protection_board['BoardName'], horizontalalignment='left', color=impact_colour, fontsize=8)
                list_items.append(pb_txt)
         
    # Population Numbers
    #Indigenous Population
    est_current_indig_pop_text = ax.text(pop_x1, pop_y1, 'Est. Indigenous Population: ', horizontalalignment='left', color='k', transform=ax.transAxes, fontsize=10)
    list_items.append(est_current_indig_pop_text)
    est_current_indig_pop_value_text = ax.text(pop_x2, pop_y1, format(current_year_indigenous_population,',').rjust(10,' '), horizontalalignment='right', color='k', transform=ax.transAxes, fontsize=10)
    list_items.append(est_current_indig_pop_value_text)

    #Indigenous Population Delta
    if indigenous_population_change == 0:
        txt_colour = '0.25'
    else:
        txt_colour = 'k'
    est_delta_indig_pop_text = ax.text(pop_x3, pop_y1, 'Est. Indigenous Population Change: ', horizontalalignment='left', color=txt_colour, transform=ax.transAxes, fontsize=10)   
    list_items.append(est_delta_indig_pop_text) 
    if indigenous_population_change < 0:
        txt_colour = 'r'
    elif indigenous_population_change == 0:
        txt_colour = '0.25'
    else:
        txt_colour='k'
    est_delta_indig_pop_value_text = ax.text(pop_x4, pop_y1, format(indigenous_population_change,',').rjust(7,' '), horizontalalignment='right', color=txt_colour, transform=ax.transAxes, fontsize=10)
    list_items.append(est_delta_indig_pop_value_text )

    #Non-Indigenous Population
    if current_year_non_indigenous_population == 0:
        txt_colour = '0.25'
    else:
        txt_colour = 'k'
    est_current_nonindig_pop_text = ax.text(pop_x1, pop_y2, 'Est. non-Indigenous Population: ', horizontalalignment='left', color=txt_colour, transform=ax.transAxes, fontsize=10) 
    list_items.append(est_current_nonindig_pop_text)
    est_current_nonindig_pop_value_text = ax.text(pop_x2, pop_y2, format(current_year_non_indigenous_population,',').rjust(10,' '), horizontalalignment='right', color=txt_colour, transform=ax.transAxes, fontsize=10) 
    list_items.append(est_current_nonindig_pop_value_text)

    #Non-Indigenous Population Change
    if non_indigenous_population_change == 0:
        txt_colour = '0.25'
    else:
        txt_colour = 'k'
    est_delta_nonindig_pop_text = ax.text(pop_x3, pop_y2, 'Est. non-Indigenous Population Change: ', horizontalalignment='left', color=txt_colour, transform=ax.transAxes, fontsize=10)
    list_items.append(est_delta_nonindig_pop_text)
    if non_indigenous_population_change < 0:
        txt_colour = 'r'
    elif non_indigenous_population_change == 0:
        txt_colour = '0.25'
    else:
        txt_colour='k'
    est_delta_nonindig_pop_value_text = ax.text(pop_x4, pop_y2, format(non_indigenous_population_change,',').rjust(7,' '), horizontalalignment='right', color=txt_colour, transform=ax.transAxes, fontsize=10)
    list_items.append(est_delta_nonindig_pop_value_text)
    
    # Percentage Indigenous Pop
    indig_pop_perc_text = ax.text(pop_x3, 0.1, 'Percent Indigenous Population: ' + pop_percentage, verticalalignment='top', horizontalalignment='left', color=str(1-pop_percentage_value), transform=ax.transAxes, fontsize=12)
    list_items.append(indig_pop_perc_text) 

    # Percentage Indigenous Pop bar
    perc_bar.set_width(pop_perc_width * pop_percentage_value)
    perc_bar.set_facecolor(str(1-pop_percentage_value))
    list_items.append(perc_bar)  

    # Current Year
    year_text = ax.text(pop_x3 + (pop_perc_width / 3), 0.05, 'Year: ' + str(current_year), verticalalignment='top', horizontalalignment='left', color='blue', transform=ax.transAxes, fontsize=15)
    list_items.append(year_text)  

    print('')
    
    return list_items

anim = animation.FuncAnimation(plt.gcf(), update_cities, frames=timelapse_period, interval=500, blit=True, repeat=loop_display, init_func=init)
#TODO create an animation that actually works when saved
#anim.save('colonisation.mp4', fps=30, extra_args=['-vcodec', 'h264', '-pix_fmt', 'yuv420p'])
Writer = animation.writers['ffmpeg']
writer = Writer(metadata=dict(artist='Me'))
#anim.save('colonisation.mp4', writer=writer)
#anim.save('colonisation.gif', writer='imagemagick', fps=60)
plt.show()
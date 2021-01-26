import pandas as pd
import numpy as np

#Title [0], City Name [1], State [2], wikipedia href [3], dms_latitude [4], dms_longitude [5], dec_latitude [6], dec_longitude [7], established date (city page) [8], established date (parent page) [9]
cities = pd.read_csv('./data/city_list.csv', header=None, quotechar='"', index_col=9)
population = pd.read_csv('./data/population.csv', index_col='Year')
explorers = pd.read_csv('./data/Explorers.csv', index_col='From')
state_boundaries = pd.read_csv('./data/States.csv', index_col='YearEffectiveFrom')
state_protection_boards = pd.read_csv('./data/Aboriginal Protector Boards.csv')
british_legislation = pd.read_excel('./data/Aboriginal Control Legislation.xlsx', sheet_name='British Empire', header=0, usecols=['State', 'Impact', 'From', 'To', 'Legislation Name'], dtype={'From': pd.Int32Dtype(), 'To': pd.Int32Dtype()}, keep_default_na=True)
commonwealth_legislation = pd.read_excel('./data/Aboriginal Control Legislation.xlsx', sheet_name='Australian Commonwealth', header=0, usecols=['State', 'Impact', 'From', 'To', 'Legislation Name'], dtype={'From': pd.Int32Dtype(), 'To': pd.Int32Dtype()}, keep_default_na=True)


current_year = 2018

print(commonwealth_legislation)

active_legislation = commonwealth_legislation[((commonwealth_legislation['From'] <= current_year) & ((commonwealth_legislation['To'] > current_year) | (commonwealth_legislation['To'].isna())))]

print(active_legislation)


"""
#pb_txt_locations = [['VIC',100,-40],['NSW',100,-40],['WA',100,-40],['QLD',100,-40],['SA',100,-40],['NT',100,-40]]
pb_txt_locations = {'State':['VIC','NSW','WA','QLD','SA','NT'],'Longitude':[100,90,80,70,60,50],'Latitude':[-40,-35,-30,-25,-20,-15]}
pb_locations_df = pd.DataFrame(pb_txt_locations)
protection_boards = state_protection_boards[(current_year >= state_protection_boards.From) & (current_year < state_protection_boards.To)]
print(protection_boards)
for index, protection_board in protection_boards.iterrows():
    print(protection_board['State'])
    print(protection_board['Impact'])
    print(protection_board['BoardName'])
    print(protection_board['From'])
    print(protection_board['To'])
    print()

    pb_txt_series = pb_locations_df.loc[pb_locations_df['State'] == protection_board['State']]

    pb_txt_x = pb_txt_series['Longitude'].values[0]
    pb_txt_y = pb_txt_series['Latitude'].values[0]
    print(pb_txt_x)
    print(pb_txt_y)
    print()


state_names = pd.read_csv('./data/' + '1859 States.csv')
#print(state_names)
for index, state_name in state_names.iterrows():
    print(state_name)
    print(state_name['Longitude'])
    print(state_name['Latitude'])
    print(state_name['StateName'])

boundary_row = state_boundaries.query('(1788 >= index) & (1788 < YearEffectiveTo)')
print(boundary_row)

boundary_row = state_boundaries[(current_year >= state_boundaries.index) & (current_year <= state_boundaries.YearEffectiveTo)]
print(boundary_row)

state_boundary_path = boundary_row.GeoJsonFile.values[0]

print(state_boundary_path)

state_geo_paths = pd.read_json('./data/' + state_boundary_path)
print(state_geo_paths)
features = state_geo_paths['features']
for feature in features:
    print('feature')
    geometries = feature['geometry']
    coords = geometries['coordinates']
    print(coords)        
    df = pd.DataFrame(coords)
    print(df)
    print(df[[0]])
    print(df[[1]])


print(cities.dtypes)
print(cities.index)

print(cities.loc[1789:1789])

colonial_period_cities = cities.loc[1788:1789]

lat = colonial_period_cities[6].values
lon = colonial_period_cities[7].values

plot_locations = np.zeros(len(colonial_period_cities), dtype=[('location', float, 2)])
print('empty plot_locations')
print(plot_locations)
#x, y = m(lon, lat)
for i in range(len(colonial_period_cities)):
    plot_locations['location'][i][0] = lon[i]
    plot_locations['location'][i][1] = lat[i]
print('plot_locations')
print(plot_locations)

if plot_locations['location'].ndim != 2:
    print('vertices must be a 2D list or array with shape Nx2 - ndim = ' + str(plot_locations['location'].ndim))
elif plot_locations['location'].shape[1] != 2:
    print('vertices must be a 2D list or array with shape Nx2 - shape[1] = ' + str(plot_locations['location'].shape[1]))
else:
    print('Correct list format')

pop_year = population.loc[1900:1900]
pop_percentage = pop_year['Indigenous percentage'].values[0]
pop_percentage_value = (float(pop_percentage.rstrip('%')))/100
print(str(pop_percentage_value))
print('hex value: ' + hex(round(255 * (1 - pop_percentage_value))).strip('0x'))
plot_colour = '#0000' + (hex(round(255 * (1 - pop_percentage_value))).strip('0x')).zfill(2)
print(plot_colour)

explorer_files = explorers.loc[1768:1790]
print(explorer_files['GeoJson'].values)
print(explorer_files['To'].values)

for explorer_file_paths in explorer_files['GeoJson'].values:
    explorer_geo_path = pd.read_json('./data/' + explorer_file_paths)
    print(explorer_file_paths)
    #print(explorer_geo_path)
    features = explorer_geo_path['features']
    for feature in features:
        print('feature')
        geometries = feature['geometry']
        coords = geometries['coordinates']
        print(coords)        
        df = pd.DataFrame(coords)
        print(df)
        print(df[[0]])
        print(df[[1]])
            
"""



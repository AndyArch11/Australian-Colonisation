"""Maps Indigenous population by Australian Federal electorate

This product (Indigenous_population_by_electorate.py) incorporates data that is:
    © Commonwealth of Australia (Australian Electoral Commission) 2020
    © Commonwealth of Australia (Australian Bureau of Statistics) 2020

"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as colors
import matplotlib.colorbar as colorbar
import shapefile as shp
from mpl_toolkits.axes_grid1.inset_locator import TransformedBbox, BboxPatch, BboxConnector, Bbox, zoomed_inset_axes, mark_inset
#hack to get Basemap working in default install environment
import os
os.environ['PROJ_LIB']='C:\\Users\\Andy\\Anaconda3\\pkgs\\proj4-5.2.0-ha925a31_1\\Library\\share'
from mpl_toolkits.basemap import Basemap

__author__ = "Andrew Arch"
__copyright__ = "Copyright 2020"
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Andrew Arch"
__email__ = "andy.arch11@gmail.com"
__status__ = "Production"

#create figure to host map.  N.B. if this is declared after Basemap, it will plot points to its own window
fig, (ax,ax_colorbar) = plt.subplots(1,2, figsize=[25.5, 13], gridspec_kw = {'width_ratios':[4, 0.02]}, constrained_layout=True)

#TODO refactor the capital city mappings into functions driven by datasets, and make execution more efficient, processing datasets in bulk rather than iterating over individual values

#Define the size and position of the inset maps
perth_ax = zoomed_inset_axes(ax, 7, bbox_to_anchor=(0.24, 0.35), bbox_transform=ax.figure.transFigure)
#Inset sizing - Upper right, Lower left corners: ([0][0], [0][1]), ([1][0], [1],[1])
perth_boundary = [[115.35, -31.55],[116.49, -32.6]]
mid_perth_lon = perth_boundary[0][0] + ((perth_boundary[1][0] - perth_boundary[0][0])/2)
mid_perth_lat = perth_boundary[1][1] + ((perth_boundary[0][1] - perth_boundary[1][1])/2)

inner_perth_ax = zoomed_inset_axes(perth_ax, 2, bbox_to_anchor=(0.135, 0.30), bbox_transform=ax.figure.transFigure)
inner_perth_boundary = [[115.704, -31.68],[116.05, -32.12]]
inner_mid_perth_lon = inner_perth_boundary[0][0] + ((inner_perth_boundary[1][0] - inner_perth_boundary[0][0])/2)
inner_mid_perth_lat = inner_perth_boundary[1][1] + ((inner_perth_boundary[0][1] - inner_perth_boundary[1][1])/2)

adelaide_ax = zoomed_inset_axes(ax, 7, bbox_to_anchor=(0.475, 0.295), bbox_transform=ax.figure.transFigure)
adelaide_boundary = [[138.1, -34.4],[139.1, -35.4]]
mid_adelaide_lon = adelaide_boundary[0][0] + ((adelaide_boundary[1][0] - adelaide_boundary[0][0])/2)
mid_adelaide_lat = adelaide_boundary[1][1] + ((adelaide_boundary[0][1] - adelaide_boundary[1][1])/2)

inner_adelaide_ax = zoomed_inset_axes(adelaide_ax, 3, bbox_to_anchor=(0.385, 0.25), bbox_transform=ax.figure.transFigure)
inner_adelaide_boundary = [[138.47, -34.76],[138.78, -35.08]]
inner_mid_adelaide_lon = inner_adelaide_boundary[0][0] + ((inner_adelaide_boundary[1][0] - inner_adelaide_boundary[0][0])/2)
inner_mid_adelaide_lat = inner_adelaide_boundary[1][1] + ((inner_adelaide_boundary[0][1] - inner_adelaide_boundary[1][1])/2)

hobart_ax = zoomed_inset_axes(ax, 7, bbox_to_anchor=(0.57, 0.115), bbox_transform=ax.figure.transFigure)
hobart_boundary = [[146.8, -42.6],[147.8, -43.1]]
mid_hobart_lon = hobart_boundary[0][0] + ((hobart_boundary[1][0] - hobart_boundary[0][0])/2)
mid_hobart_lat = hobart_boundary[1][1] + ((hobart_boundary[0][1] - hobart_boundary[1][1])/2)

melbourne_ax = zoomed_inset_axes(ax, 7, bbox_to_anchor=(0.786, 0.225), bbox_transform=ax.figure.transFigure)
melbourne_boundary = [[144.1, -37.4],[145.9, -38.5]]
mid_melbourne_lon = melbourne_boundary[0][0] + ((melbourne_boundary[1][0] - melbourne_boundary[0][0])/2)
mid_melbourne_lat = melbourne_boundary[1][1] + ((melbourne_boundary[0][1] - melbourne_boundary[1][1])/2)

inner_melbourne_ax = zoomed_inset_axes(melbourne_ax, 2.5, bbox_to_anchor=(0.92, 0.23), bbox_transform=ax.figure.transFigure)
inner_melbourne_boundary = [[144.71, -37.58],[145.377, -38.04]]
inner_mid_melbourne_lon = inner_melbourne_boundary[0][0] + ((inner_melbourne_boundary[1][0] - inner_melbourne_boundary[0][0])/2)
inner_mid_melbourne_lat = inner_melbourne_boundary[1][1] + ((inner_melbourne_boundary[0][1] - inner_melbourne_boundary[1][1])/2)

act_ax = zoomed_inset_axes(ax, 4, bbox_to_anchor=(0.85, 0.365), bbox_transform=ax.figure.transFigure)
act_boundary = [[148.5, -35.0],[149.6, -36.0]]
mid_act_lon = act_boundary[0][0] + ((act_boundary[1][0] - act_boundary[0][0])/2)
mid_act_lat = act_boundary[1][1] + ((act_boundary[0][1] - act_boundary[1][1])/2)

sydney_ax = zoomed_inset_axes(ax, 6, bbox_to_anchor=(0.919, 0.72), bbox_transform=ax.figure.transFigure)
sydney_boundary = [[150.2, -32.65],[152.2, -34.70]]
mid_sydney_lon = sydney_boundary[0][0] + ((sydney_boundary[1][0] - sydney_boundary[0][0])/2)
mid_sydney_lat = sydney_boundary[1][1] + ((sydney_boundary[0][1] - sydney_boundary[1][1])/2)

inner_sydney_ax = zoomed_inset_axes(sydney_ax, 2.9, bbox_to_anchor=(0.919, 0.98), bbox_transform=ax.figure.transFigure)
inner_sydney_boundary = [[150.7, -33.6],[151.4, -34.1]]
inner_mid_sydney_lon = inner_sydney_boundary[0][0] + ((inner_sydney_boundary[1][0] - inner_sydney_boundary[0][0])/2)
inner_mid_sydney_lat = inner_sydney_boundary[1][1] + ((inner_sydney_boundary[0][1] - inner_sydney_boundary[1][1])/2)

brisbane_ax = zoomed_inset_axes(ax, 7, bbox_to_anchor=(0.775, 0.98), bbox_transform=ax.figure.transFigure)
brisbane_boundary = [[152.5, -26.3],[153.6, -28.2]]
mid_brisbane_lon = brisbane_boundary[0][0] + ((brisbane_boundary[1][0] - brisbane_boundary[0][0])/2)
mid_brisbane_lat = brisbane_boundary[1][1] + ((brisbane_boundary[0][1] - brisbane_boundary[1][1])/2)

darwin_ax = zoomed_inset_axes(ax, 7, bbox_to_anchor=(0.42, 0.98), bbox_transform=ax.figure.transFigure)
darwin_boundary = [[130.7, -12.2],[131.2, -12.7]]
mid_darwin_lon = darwin_boundary[0][0] + ((darwin_boundary[1][0] - darwin_boundary[0][0])/2)
mid_darwin_lat = darwin_boundary[1][1] + ((darwin_boundary[0][1] - darwin_boundary[1][1])/2)

#turn off any axes ticks on the diagram
plt.xticks(visible=False)
plt.yticks(visible=False)

#TODO address the deprecation warning coming from the Basemap constructor call - The dedent function was deprecated in Matplotlib 3.1 and will be removed in 3.3. Use inspect.cleandoc instead.
#draw map - Australia -26.8372557,127.5859928
m = Basemap(projection='aea', lat_0=-22.5, lon_0=130.5, resolution='l', llcrnrlat=-42, urcrnrlat=-3, llcrnrlon=95, urcrnrlon=166, ax=ax)
m.drawcoastlines(color='0', linewidth=0.25)
m.fillcontinents(color='white', alpha=1)
m.drawparallels(np.arange(-47,0,23.5))
m.drawmeridians(np.arange(100,180,20))

#create a map for each inset
perth_m = Basemap(projection='aea', lat_0=mid_perth_lat, lon_0=mid_perth_lon, resolution='i', llcrnrlat=perth_boundary[1][1], urcrnrlat=perth_boundary[0][1], llcrnrlon=perth_boundary[0][0], urcrnrlon=perth_boundary[1][0], ax=perth_ax)
perth_m.drawcoastlines(color='0', linewidth=0.25)
perth_m.fillcontinents(color='white', alpha=1)

inner_perth_m = Basemap(projection='aea', lat_0=inner_mid_perth_lat, lon_0=inner_mid_perth_lon, resolution='i', llcrnrlat=inner_perth_boundary[1][1], urcrnrlat=inner_perth_boundary[0][1], llcrnrlon=inner_perth_boundary[0][0], urcrnrlon=inner_perth_boundary[1][0], ax=inner_perth_ax)
inner_perth_m.drawcoastlines(color='0', linewidth=0.25)
inner_perth_m.fillcontinents(color='white', alpha=1)

adelaide_m = Basemap(projection='aea', lat_0=mid_adelaide_lat, lon_0=mid_adelaide_lon, resolution='i', llcrnrlat=adelaide_boundary[1][1], urcrnrlat=adelaide_boundary[0][1], llcrnrlon=adelaide_boundary[0][0], urcrnrlon=adelaide_boundary[1][0], ax=adelaide_ax)
adelaide_m.drawcoastlines(color='0', linewidth=0.25)
adelaide_m.fillcontinents(color='white', alpha=1)

inner_adelaide_m = Basemap(projection='aea', lat_0=inner_mid_adelaide_lat, lon_0=inner_mid_adelaide_lon, resolution='i', llcrnrlat=inner_adelaide_boundary[1][1], urcrnrlat=inner_adelaide_boundary[0][1], llcrnrlon=inner_adelaide_boundary[0][0], urcrnrlon=inner_adelaide_boundary[1][0], ax=inner_adelaide_ax)
inner_adelaide_m.drawcoastlines(color='0', linewidth=0.25)
inner_adelaide_m.fillcontinents(color='white', alpha=1)

hobart_m = Basemap(projection='aea', lat_0=mid_hobart_lat, lon_0=mid_hobart_lon, resolution='i', llcrnrlat=hobart_boundary[1][1], urcrnrlat=hobart_boundary[0][1], llcrnrlon=hobart_boundary[0][0], urcrnrlon=hobart_boundary[1][0], ax=hobart_ax)
hobart_m.drawcoastlines(color='0', linewidth=0.25)
hobart_m.fillcontinents(color='white', alpha=1)

melbourne_m = Basemap(projection='aea', lat_0=mid_melbourne_lat, lon_0=mid_melbourne_lon, resolution='i', llcrnrlat=melbourne_boundary[1][1], urcrnrlat=melbourne_boundary[0][1], llcrnrlon=melbourne_boundary[0][0], urcrnrlon=melbourne_boundary[1][0], ax=melbourne_ax)
melbourne_m.drawcoastlines(color='0', linewidth=0.25)
melbourne_m.fillcontinents(color='white', alpha=1)

inner_melbourne_m = Basemap(projection='aea', lat_0=inner_mid_melbourne_lat, lon_0=inner_mid_melbourne_lon, resolution='i', llcrnrlat=inner_melbourne_boundary[1][1], urcrnrlat=inner_melbourne_boundary[0][1], llcrnrlon=inner_melbourne_boundary[0][0], urcrnrlon=inner_melbourne_boundary[1][0], ax=inner_melbourne_ax)
inner_melbourne_m.drawcoastlines(color='0', linewidth=0.25)
inner_melbourne_m.fillcontinents(color='white', alpha=1)

act_m = Basemap(projection='aea', lat_0=mid_act_lat, lon_0=mid_act_lon, resolution='i', llcrnrlat=act_boundary[1][1], urcrnrlat=act_boundary[0][1], llcrnrlon=act_boundary[0][0], urcrnrlon=act_boundary[1][0], ax=act_ax)
act_m.drawcoastlines(color='0', linewidth=0.25)
act_m.fillcontinents(color='white', alpha=1)

sydney_m = Basemap(projection='aea', lat_0=mid_sydney_lat, lon_0=mid_sydney_lon, resolution='i', llcrnrlat=sydney_boundary[1][1], urcrnrlat=sydney_boundary[0][1], llcrnrlon=sydney_boundary[0][0], urcrnrlon=sydney_boundary[1][0], ax=sydney_ax)
sydney_m.drawcoastlines(color='0', linewidth=0.25)
sydney_m.fillcontinents(color='white', alpha=1)

inner_sydney_m = Basemap(projection='aea', lat_0=inner_mid_sydney_lat, lon_0=inner_mid_sydney_lon, resolution='i', llcrnrlat=inner_sydney_boundary[1][1], urcrnrlat=inner_sydney_boundary[0][1], llcrnrlon=inner_sydney_boundary[0][0], urcrnrlon=inner_sydney_boundary[1][0], ax=inner_sydney_ax)
inner_sydney_m.drawcoastlines(color='0', linewidth=0.25)
inner_sydney_m.fillcontinents(color='white', alpha=1)

brisbane_m = Basemap(projection='aea', lat_0=mid_brisbane_lat, lon_0=mid_brisbane_lon, resolution='i', llcrnrlat=brisbane_boundary[1][1], urcrnrlat=brisbane_boundary[0][1], llcrnrlon=brisbane_boundary[0][0], urcrnrlon=brisbane_boundary[1][0], ax=brisbane_ax)
brisbane_m.drawcoastlines(color='0', linewidth=0.25)
brisbane_m.fillcontinents(color='white', alpha=1)

darwin_m = Basemap(projection='aea', lat_0=mid_darwin_lat, lon_0=mid_darwin_lon, resolution='i', llcrnrlat=darwin_boundary[1][1], urcrnrlat=darwin_boundary[0][1], llcrnrlon=darwin_boundary[0][0], urcrnrlon=darwin_boundary[1][0], ax=darwin_ax)
darwin_m.drawcoastlines(color='0', linewidth=0.25)
darwin_m.fillcontinents(color='white', alpha=1)

def mark_geo_inset(ax, ax2, m, m2, loc1=(1, 2), loc2=(3, 4), **kwargs):
    """ Patched mark_inset to work with Basemap.
    
    Reason: Basemap converts Geographic (lon/lat) to Map Projection (x/y) coordinates
    See: https://stackoverflow.com/questions/41610834/basemap-projection-geos-controlling-mark-inset-location

    Args:
        ax (subplot): parent subplot where inset is marked on parent map
        ax2 (subplot): inset subplot where inset map is displayed
        m (basemap): parent basemap associated with ax
        m2 (basemap): inset basemap associated with ax2
        loc1 (tuple): start and end locations of connector 1
        loc2 (tuple): start and end locations of connector 2
        **kwargs (optional args): to manage the presentation of the connectors and inset markers
   
        loc tuple values:
        'upper right'  : 1,
        'upper left'   : 2,
        'lower left'   : 3,
        'lower right'  : 4

    Returns:
        BboxPatch: Patch for the inset coverage on the parent subplot
        BboxConnector: Connector line 1 connecting the coverage rectangle on the parent subplot to the inset map
        BboxConnector: Connector line 2 connecting the coverage rectanlge on the parent subplot to the inset map
    """

    # Doesn't work for Basemap
    #    rect = TransformedBbox(inset_axes.viewLim, parent_axes.transData)
    #    axzoom_geoLims = np.array(m2(*ax2.viewLim._points.T, inverse=True))

    axzoom_geoLims = m2(ax2.get_xlim(), ax2.get_ylim(), inverse=True)
    rect = TransformedBbox(Bbox(np.array(m(*axzoom_geoLims)).T), ax.transData)

    pp = BboxPatch(rect, fill=False, **kwargs)
    ax.add_patch(pp)

    p1 = BboxConnector(ax2.bbox, rect, loc1=loc1[0], loc2=loc1[1], **kwargs)
    ax2.add_patch(p1)
    p1.set_clip_on(False)
    p2 = BboxConnector(ax2.bbox, rect, loc1=loc2[0], loc2=loc2[1], **kwargs)
    ax2.add_patch(p2)
    p2.set_clip_on(False)

    return pp, p1, p2

def read_shapefile(sf):
    """ Loads a shapefile into a Panda Dataframe.
    
    Args:
        sf (shapefile): the shapefile containing the shapes

    Returns:
        dataframe: dataframe of shapefile coords
    """

    fields = [x[0] for x in sf.fields][1:]
    records = sf.records()
    shps = [s.points for s in sf.shapes()]

    df = pd.DataFrame(columns=fields, data=records)
    df = df.assign(coords=shps)
    
    return df

def plot_shape(id, sf, s=None):
    """ Display a shape from a shape file, intended for testing/verification purposes.
    
    Args:
        id -- name of shape in the shapefile used to extract the required shape
        sf -- the shapefile containing the shape
        s -- text to display with the shapefile (default: None)
    """

    plt.figure()
    ax = plt.axes()
    ax.set_aspect('equal')

    shape_ex = sf.shape(id)
    x_subshapes = []  
    x_lon_subshapes = []
    y_subshapes = []
    y_lat_subshapes = []

    #print(shape_ex.points)

    begin_row = 0
    x_begin = shape_ex.points[begin_row][0]
    y_begin = shape_ex.points[begin_row][1]
    end_point = False

    for ip in range(len(shape_ex.points)):
        x_lon_subshapes.append(shape_ex.points[ip][0])
        y_lat_subshapes.append(shape_ex.points[ip][1])
        if ip > begin_row and x_begin == shape_ex.points[ip][0] and y_begin == shape_ex.points[ip][1]:            
            end_point = True
            x_subshapes.append(x_lon_subshapes)
            y_subshapes.append(y_lat_subshapes)            
            x_lon_subshapes = []
            y_lat_subshapes = []
        elif end_point:
            begin_row = ip
            x_begin = shape_ex.points[ip][0]
            y_begin = shape_ex.points[ip][1]
            end_point = False

    for row in range(len(x_subshapes)):
        x_lon = np.zeros((len(x_subshapes[row]),1))
        y_lat = np.zeros((len(x_subshapes[row]),1))
        for ip in range(len(x_subshapes[row])):
            x_lon[ip] = x_subshapes[row][ip]
        for ip in range(len(y_subshapes[row])):
            y_lat[ip] = y_subshapes[row][ip]

        plt.plot(x_lon, y_lat)

        if row == 0:
            x0 = np.mean(x_lon)
            y0 = np.mean(y_lat)
            ax.text(x0, y0, s, fontsize=10)

    # use bbox (bounding box) to set plot limits
    plt.xlim(shape_ex.bbox[0], shape_ex.bbox[2])
    plt.show()


def plot_map(sf, pop_heatmap):
    """ Overly long function to map the heatmap, requires refactoring.
    
    Args:
        sf -- the shapefile containing the shapes of the electorates
    """

    global m
    global ax
    global plt  

    #Minimum area to display text for in the different zoomed in areas
    min_national_electorate_area = 2000
    min_capital_electorate_area = 130
    
    x_subshapes = []  
    x_lon_subshapes = []
    y_subshapes = []
    y_lat_subshapes = []

    x_electorate_points = []
    y_electorate_points = []

    # begin map boundary in center of map, then expand based on coordinates
    min_x = 127.5860
    max_x = 127.5860
    min_y = -26.8373
    max_y = -26.8373

    if pop_heatmap == heatmap[1]: #Indigenous Population
        max_indig_pop = round(indigenous_population['Indigenous Population'].max())
    elif pop_heatmap == heatmap[2]: #Indigenous Population per SqKm
        max_indig_pop_density = round(indigenous_population['Indigenous per SqKM'].max(),2)

    #iterate through the electorates in the shape file, breaking out the non-contiguous shapes that make up each electorate
    for electorate_row in range(len(sf)):
        shape_ex = sf.shape(electorate_row)   

        #In order to deal with non-contiguous mapping areas in the shape files, such as Islands, need to detect start and end of polygons
        #based on end coordinate matching start coordinate and then move onto the next contiguous mapping in the same shapefile.
        begin_row = 0
        x_begin = shape_ex.points[begin_row][0]
        elect_min_x = shape_ex.points[begin_row][0]
        elect_max_x = shape_ex.points[begin_row][0]
        y_begin = shape_ex.points[begin_row][1]
        elect_min_y = shape_ex.points[begin_row][1]
        elect_max_y = shape_ex.points[begin_row][1]
        end_point = False

        for ip in range(len(shape_ex.points)):
            x_lon_subshapes.append(shape_ex.points[ip][0])
            if min_x > shape_ex.points[ip][0]:
                min_x = shape_ex.points[ip][0]
            if max_x < shape_ex.points[ip][0]:
                max_x = shape_ex.points[ip][0]
            
            y_lat_subshapes.append(shape_ex.points[ip][1])
            if min_y > shape_ex.points[ip][1]:
                min_y = shape_ex.points[ip][1]
            if max_y < shape_ex.points[ip][1]:
                max_y = shape_ex.points[ip][1]          

            if ip > begin_row and x_begin == shape_ex.points[ip][0] and y_begin == shape_ex.points[ip][1]:            
                end_point = True
                x_subshapes.append(x_lon_subshapes)
                y_subshapes.append(y_lat_subshapes)            
                x_lon_subshapes = []
                y_lat_subshapes = []
            elif end_point:
                begin_row = ip
                x_begin = shape_ex.points[ip][0]
                y_begin = shape_ex.points[ip][1]
                end_point = False
            
        x_electorate_points.append(x_subshapes)
        y_electorate_points.append(y_subshapes)
        x_subshapes = []
        y_subshapes = []

    # iterate through the non-contiguous shapes that have been extracted in the previous iteration of the shapefile
    for electorate in range(len(x_electorate_points)):
        electorate_name = sf.records()[electorate][0]
        electorate_area = float(sf.records()[electorate][7])
        electorate_state = sf.records()[electorate][1]

        # determine the colour of the electorate based on the number of Indigenous people
        cmap = cm.get_cmap('Reds')
        electorate_colour = 'k'
        indig_text = ''
        max_boundary = 0.0
        
        if pop_heatmap == heatmap[0]: #Indigenous Population Percentage
            electorate_indig_pop_perc = indigenous_population.loc[electorate_name].values[4]
            indig_text = electorate_indig_pop_perc
            electorate_indig_pop_perc_value = float(electorate_indig_pop_perc.rstrip('%'))/100
            max_indig_perc = 0.402
            max_boundary = max_indig_perc
            electorate_colour = cmap(electorate_indig_pop_perc_value/max_indig_perc)        
        elif pop_heatmap == heatmap[1]: #Indigenous Population
            electorate_indig_pop = indigenous_population.loc[electorate_name].values[5]
            electorate_indig_pop_value = round(float(electorate_indig_pop))
            indig_text = str(electorate_indig_pop_value)
            max_boundary = max_indig_pop
            electorate_colour = cmap(electorate_indig_pop_value/max_indig_pop)
        elif pop_heatmap == heatmap[2]: #Indigenous Population per SqKm
            electorate_indig_density = indigenous_population.loc[electorate_name].values[7]
            electorate_indig_density_value = round(float(electorate_indig_density),2)
            indig_text = str(electorate_indig_density_value)
            max_boundary = max_indig_pop_density
            electorate_colour = cmap(electorate_indig_density_value/max_indig_pop_density)
        
        elect_min_x = x_electorate_points[electorate][0][0]
        elect_max_x = x_electorate_points[electorate][0][0]
        elect_min_y = y_electorate_points[electorate][0][0]
        elect_max_y = y_electorate_points[electorate][0][0]

        #iterate through each of the contiguous electoral shapes, one electoral region may consist of multiple non-contiguous shapes, such as islands, etc
        for row in range(len(x_electorate_points[electorate])):
            #determine the size of the electorate min/max X, min/max Y
            x_lon = np.zeros((len(x_electorate_points[electorate][row]),1))
            y_lat = np.zeros((len(y_electorate_points[electorate][row]),1))
            for ip in range(len(x_electorate_points[electorate][row])):
                x_lon[ip] = x_electorate_points[electorate][row][ip]                
                if elect_min_x > x_electorate_points[electorate][row][ip]:
                    elect_min_x = x_electorate_points[electorate][row][ip]
                if elect_max_x < x_electorate_points[electorate][row][ip]:
                    elect_max_x = x_electorate_points[electorate][row][ip]
            for ip in range(len(y_electorate_points[electorate][row])):
                y_lat[ip] = y_electorate_points[electorate][row][ip]
                if elect_min_y > y_electorate_points[electorate][row][ip]:
                    elect_min_y = y_electorate_points[electorate][row][ip]
                if elect_max_y < y_electorate_points[electorate][row][ip]:
                    elect_max_y = y_electorate_points[electorate][row][ip] 

            #hack to get around ACT embedded in middle of Eden-Monaro
            alpha = 0.6
            zorder = 100
            if electorate_state == 'ACT':
                #TODO mask ACT from Eden-Monaro so that Eden-Monaro is not done over ACT.  This is a quick hack to deal with it.
                #See https://sgillies.net/2010/04/06/painting-punctured-polygons-with-matplotlib.html for an example
                zorder = 500
                alpha = 1
            
            #map the electorate to the map          
            line_colour = '0'
            x_map_lon, y_map_lat = m(x_lon, y_lat) 
            ax.plot(x_map_lon, y_map_lat, color=line_colour, linewidth=0.25)  
            ax.fill(x_map_lon, y_map_lat, color=electorate_colour, alpha=alpha, zorder=zorder)   

            #determine where to place the name of the electorate
            x0 = elect_min_x + ((elect_max_x - elect_min_x)/3)
            y0 = elect_max_y + ((elect_min_y - elect_max_y)/2)
            x0_map, y0_map = m(x0, y0)

            #print electorate value where the area is large enough to display it
            if row == 0 and (electorate_area > min_national_electorate_area or electorate_name == 'Herbert'):
                #ax.text(x0_map, y0_map, electorate_name, fontsize=8, zorder=600)
                ax.text(x0_map, y0_map, indig_text, fontsize=8, zorder=600)

            #map the inset map jurisdictions and determine where to display the electorate value in the inset maps  
            if electorate_state == 'WA':
                x_perthmap_lon, y_perthmap_lat = perth_m(x_lon, y_lat)
                perth_ax.plot(x_perthmap_lon, y_perthmap_lat, color=line_colour, linewidth=0.25)
                perth_ax.fill(x_perthmap_lon, y_perthmap_lat, color=electorate_colour, alpha=alpha, zorder=zorder)              
                if row == 0 and x0 > perth_boundary[0][0] and x0 < perth_boundary[1][0] and y0 > perth_boundary[1][1] and y0 < perth_boundary[0][1] and electorate_area > min_capital_electorate_area:
                    x0_perthmap, y0_perthmap = perth_m(x0, y0)
                    #perth_ax.text(x0_perthmap, y0_perthmap, electorate_name, fontsize=8, zorder=600)
                    perth_ax.text(x0_perthmap, y0_perthmap, indig_text, fontsize=8, zorder=600)

                x_innerperthmap_lon, y_innerperthmap_lat = inner_perth_m(x_lon, y_lat)
                inner_perth_ax.plot(x_innerperthmap_lon, y_innerperthmap_lat, color=line_colour, linewidth=0.25)
                inner_perth_ax.fill(x_innerperthmap_lon, y_innerperthmap_lat, color=electorate_colour, alpha=alpha, zorder=zorder)
                if row == 0 and x0 > inner_perth_boundary[0][0] and x0 < inner_perth_boundary[1][0] and y0 > inner_perth_boundary[1][1] and y0 < inner_perth_boundary[0][1]:
                    x0_innerperthmap, y0_innerperthmap = inner_perth_m(x0, y0)
                    #inner_perth_ax.text(x0_innerperthmap, y0_innerperthmap, electorate_name, fontsize=8, zorder=600)
                    inner_perth_ax.text(x0_innerperthmap, y0_innerperthmap, indig_text, fontsize=8, zorder=600)

            if electorate_state == 'SA':
                x_adelaidemap_lon, y_adelaidemap_lat = adelaide_m(x_lon, y_lat)
                adelaide_ax.plot(x_adelaidemap_lon, y_adelaidemap_lat, color=line_colour, linewidth=0.25)
                adelaide_ax.fill(x_adelaidemap_lon, y_adelaidemap_lat, color=electorate_colour, alpha=alpha, zorder=zorder)              
                if row == 0 and x0 > adelaide_boundary[0][0] and x0 < adelaide_boundary[1][0] and y0 > adelaide_boundary[1][1] and y0 < adelaide_boundary[0][1] and electorate_area > min_capital_electorate_area:
                    x0_adelaidemap, y0_adelaidemap = adelaide_m(x0, y0)
                    #adelaide_ax.text(x0_adelaidemap, y0_adelaidemap, electorate_name, fontsize=8, zorder=600)
                    adelaide_ax.text(x0_adelaidemap, y0_adelaidemap, indig_text, fontsize=8, zorder=600)
                
                x_inneradelaidemap_lon, y_inneradelaidemap_lat = inner_adelaide_m(x_lon, y_lat)
                inner_adelaide_ax.plot(x_inneradelaidemap_lon, y_inneradelaidemap_lat, color=line_colour, linewidth=0.25)
                inner_adelaide_ax.fill(x_inneradelaidemap_lon, y_inneradelaidemap_lat, color=electorate_colour, alpha=alpha, zorder=zorder)
                if row == 0 and x0 > inner_adelaide_boundary[0][0] and x0 < inner_adelaide_boundary[1][0] and y0 > inner_adelaide_boundary[1][1] and y0 < inner_adelaide_boundary[0][1]:
                    x0_inneradelaidemap, y0_inneradelaidemap = inner_adelaide_m(x0, y0)
                    #inner_adelaide_ax.text(x0_inneradelaidemap, y0_inneradelaidemap, electorate_name, fontsize=8, zorder=600)
                    inner_adelaide_ax.text(x0_inneradelaidemap, y0_inneradelaidemap, indig_text, fontsize=8, zorder=600)
            
            if electorate_state == 'TAS':
                x_hobartmap_lon, y_hobartmap_lat = hobart_m(x_lon, y_lat)
                hobart_ax.plot(x_hobartmap_lon, y_hobartmap_lat, color=line_colour, linewidth=0.25)
                hobart_ax.fill(x_hobartmap_lon, y_hobartmap_lat, color=electorate_colour, alpha=alpha, zorder=zorder)              
                if row == 0 and x0 > hobart_boundary[0][0] and x0 < hobart_boundary[1][0] and y0 > hobart_boundary[1][1] and y0 < hobart_boundary[0][1] and electorate_area > min_capital_electorate_area:
                    x0_hobartmap, y0_hobartmap = hobart_m(x0, y0)
                    #hobart_ax.text(x0_hobartmap, y0_hobartmap, electorate_name, fontsize=8, zorder=600)
                    hobart_ax.text(x0_hobartmap, y0_hobartmap, indig_text, fontsize=8, zorder=600)
            
            if electorate_state == 'VIC':
                x_melbournemap_lon, y_melbournemap_lat = melbourne_m(x_lon, y_lat)
                melbourne_ax.plot(x_melbournemap_lon, y_melbournemap_lat, color=line_colour, linewidth=0.25)
                melbourne_ax.fill(x_melbournemap_lon, y_melbournemap_lat, color=electorate_colour, alpha=alpha, zorder=zorder)              
                if row == 0 and x0 > melbourne_boundary[0][0] and x0 < melbourne_boundary[1][0] and y0 > melbourne_boundary[1][1] and y0 < melbourne_boundary[0][1] and electorate_area > min_capital_electorate_area:
                    x0_melbournemap, y0_melbournemap = melbourne_m(x0, y0)
                    #melbourne_ax.text(x0_melbournemap, y0_melbournemap, electorate_name, fontsize=8, zorder=600)
                    melbourne_ax.text(x0_melbournemap, y0_melbournemap, indig_text, fontsize=8, zorder=600)

                x_innermelbournemap_lon, y_innermelbournemap_lat = inner_melbourne_m(x_lon, y_lat)
                inner_melbourne_ax.plot(x_innermelbournemap_lon, y_innermelbournemap_lat, color=line_colour, linewidth=0.25)
                inner_melbourne_ax.fill(x_innermelbournemap_lon, y_innermelbournemap_lat, color=electorate_colour, alpha=alpha, zorder=zorder)
                if row == 0 and x0 > inner_melbourne_boundary[0][0] and x0 < inner_melbourne_boundary[1][0] and y0 > inner_melbourne_boundary[1][1] and y0 < inner_melbourne_boundary[0][1]:
                    x0_innermelbournemap, y0_innermelbournemap = inner_melbourne_m(x0, y0)
                    #inner_melbourne_ax.text(x0_innermelbournemap, y0_innermelbournemap, electorate_name, fontsize=8, zorder=600)
                    inner_melbourne_ax.text(x0_innermelbournemap, y0_innermelbournemap, indig_text, fontsize=8, zorder=600)

            if electorate_state == 'ACT' or electorate_state == 'NSW':
                #TODO fix Eden-Monaro being written over ACT, in particular, over Bean
                x_actmap_lon, y_actmap_lat = act_m(x_lon, y_lat)
                act_ax.plot(x_actmap_lon, y_actmap_lat, color=line_colour, linewidth=0.25)
                act_ax.fill(x_actmap_lon, y_actmap_lat, color=electorate_colour, alpha=alpha, zorder=zorder)              
                if row == 0 and x0 > act_boundary[0][0] and x0 < act_boundary[1][0] and y0 > act_boundary[1][1] and y0 < act_boundary[0][1] and electorate_area > min_capital_electorate_area:
                    x0_actmap, y0_actmap = act_m(x0, y0)
                    #act_ax.text(x0_actmap, y0_actmap, electorate_name, fontsize=8, zorder=600)
                    act_ax.text(x0_actmap, y0_actmap, indig_text, fontsize=8, zorder=600)
            
            if electorate_state == 'ACT' or electorate_state == 'NSW':
                x_sydneymap_lon, y_sydneymap_lat = sydney_m(x_lon, y_lat)
                sydney_ax.plot(x_sydneymap_lon, y_sydneymap_lat, color=line_colour, linewidth=0.25)
                sydney_ax.fill(x_sydneymap_lon, y_sydneymap_lat, color=electorate_colour, alpha=alpha, zorder=zorder)              
                if row == 0 and x0 > sydney_boundary[0][0] and x0 < sydney_boundary[1][0] and y0 > sydney_boundary[1][1] and y0 < sydney_boundary[0][1] and electorate_area > min_capital_electorate_area:
                    x0_sydneymap, y0_sydneymap = sydney_m(x0, y0)
                    #sydney_ax.text(x0_sydneymap, y0_sydneymap, electorate_name, fontsize=8, zorder=600)                
                    sydney_ax.text(x0_sydneymap, y0_sydneymap, indig_text, fontsize=8, zorder=600)                
                
                x_innersydneymap_lon, y_innersydneymap_lat = inner_sydney_m(x_lon, y_lat)
                inner_sydney_ax.plot(x_innersydneymap_lon, y_innersydneymap_lat, color=line_colour, linewidth=0.25)
                inner_sydney_ax.fill(x_innersydneymap_lon, y_innersydneymap_lat, color=electorate_colour, alpha=alpha, zorder=zorder)
                if row == 0 and x0 > inner_sydney_boundary[0][0] and x0 < inner_sydney_boundary[1][0] and y0 > inner_sydney_boundary[1][1] and y0 < inner_sydney_boundary[0][1]:
                    x0_innersydneymap, y0_innersydneymap = inner_sydney_m(x0, y0)
                    #inner_sydney_ax.text(x0_innersydneymap, y0_innersydneymap, electorate_name, fontsize=8, zorder=600)
                    inner_sydney_ax.text(x0_innersydneymap, y0_innersydneymap, indig_text, fontsize=8, zorder=600)
    
            if electorate_state == 'QLD' or electorate_state == 'NSW':
                x_brisbanemap_lon, y_brisbanemap_lat = brisbane_m(x_lon, y_lat)
                brisbane_ax.plot(x_brisbanemap_lon, y_brisbanemap_lat, color=line_colour, linewidth=0.25)
                brisbane_ax.fill(x_brisbanemap_lon, y_brisbanemap_lat, color=electorate_colour, alpha=alpha, zorder=zorder)              
                if row == 0 and x0 > brisbane_boundary[0][0] and x0 < brisbane_boundary[1][0] and y0 > brisbane_boundary[1][1] and y0 < brisbane_boundary[0][1]: 
                    x0_brisbanemap, y0_brisbanemap = brisbane_m(x0, y0)
                    #brisbane_ax.text(x0_brisbanemap, y0_brisbanemap, electorate_name, fontsize=8, zorder=600) 
                    brisbane_ax.text(x0_brisbanemap, y0_brisbanemap, indig_text, fontsize=8, zorder=600) 
            
            if electorate_state == 'NT':
                x_darwinmap_lon, y_darwinmap_lat = darwin_m(x_lon, y_lat)
                darwin_ax.plot(x_darwinmap_lon, y_darwinmap_lat, color=line_colour, linewidth=0.25)
                darwin_ax.fill(x_darwinmap_lon, y_darwinmap_lat, color=electorate_colour, alpha=alpha, zorder=zorder)              
                if row == 0 and x0 > darwin_boundary[0][0] and x0 < darwin_boundary[1][0] and y0 > darwin_boundary[1][1] and y0 < darwin_boundary[0][1] and electorate_area > min_capital_electorate_area:
                    x0_darwinmap, y0_darwinmap = darwin_m(x0, y0)
                    #darwin_ax.text(x0_darwinmap, y0_darwinmap, electorate_name, fontsize=8, zorder=600)
                    darwin_ax.text(x0_darwinmap, y0_darwinmap, indig_text, fontsize=8, zorder=600)

    #Position the inset maps
    perth_ax.set_title('Perth')
    #lower corner of the original image
    x_perth_lc, y_perth_lc = perth_m(perth_boundary[0][0], perth_boundary[1][1])
    #upper corner of the original image
    x_perth_uc, y_perth_uc = perth_m(perth_boundary[1][0], perth_boundary[0][1])
    #sub region of the original image
    perth_ax.set_xlim(x_perth_lc, x_perth_uc)
    perth_ax.set_ylim(y_perth_lc, y_perth_uc)
    #create inset
    mark_geo_inset(ax, perth_ax, m, perth_m, loc1=(1, 2), loc2=(4, 3), fc='none', ec='0.7')

    inner_perth_ax.set_title('Inner Perth')
    #lower corner of the original image
    x_innerperth_lc, y_innerperth_lc = inner_perth_m(inner_perth_boundary[0][0], inner_perth_boundary[1][1])
    #upper corner of the original image
    x_innerperth_uc, y_innerperth_uc = inner_perth_m(inner_perth_boundary[1][0], inner_perth_boundary[0][1])
    #sub region of the original image
    inner_perth_ax.set_xlim(x_innerperth_lc, x_innerperth_uc)
    inner_perth_ax.set_ylim(y_innerperth_lc, y_innerperth_uc)
    mark_geo_inset(perth_ax, inner_perth_ax, perth_m, inner_perth_m, loc1=(1, 2), loc2=(4, 3), fc='none', ec='0.7')

    adelaide_ax.set_title('Adelaide')
    #lower corner of the original image
    x_adelaide_lc, y_adelaide_lc = adelaide_m(adelaide_boundary[0][0], adelaide_boundary[1][1])
    #upper corner of the original image
    x_adelaide_uc, y_adelaide_uc = adelaide_m(adelaide_boundary[1][0], adelaide_boundary[0][1])
    #sub region of the original image
    adelaide_ax.set_xlim(x_adelaide_lc, x_adelaide_uc)
    adelaide_ax.set_ylim(y_adelaide_lc, y_adelaide_uc)
    #create inset
    mark_geo_inset(ax, adelaide_ax, m, adelaide_m, loc1=(1, 2), loc2=(4, 3), fc='none', ec='0.7')

    inner_adelaide_ax.set_title('Inner Adelaide')
    #lower corner of the original image
    x_inneradelaide_lc, y_inneradelaide_lc = inner_adelaide_m(inner_adelaide_boundary[0][0], inner_adelaide_boundary[1][1])
    #upper corner of the original image
    x_inneradelaide_uc, y_inneradelaide_uc = inner_adelaide_m(inner_adelaide_boundary[1][0], inner_adelaide_boundary[0][1])
    #sub region of the original image
    inner_adelaide_ax.set_xlim(x_inneradelaide_lc, x_inneradelaide_uc)
    inner_adelaide_ax.set_ylim(y_inneradelaide_lc, y_inneradelaide_uc)
    mark_geo_inset(adelaide_ax, inner_adelaide_ax, adelaide_m, inner_adelaide_m, loc1=(1, 2), loc2=(4, 3), fc='none', ec='0.7')

    hobart_ax.set_title('Hobart')
    #lower corner of the original image
    x_hobart_lc, y_hobart_lc = hobart_m(hobart_boundary[0][0], hobart_boundary[1][1])
    #upper corner of the original image
    x_hobart_uc, y_hobart_uc = hobart_m(hobart_boundary[1][0], hobart_boundary[0][1])
    #sub region of the original image
    hobart_ax.set_xlim(x_hobart_lc, x_hobart_uc)
    hobart_ax.set_ylim(y_hobart_lc, y_hobart_uc)
    #create inset
    mark_geo_inset(ax, hobart_ax, m, hobart_m, loc1=(1, 2), loc2=(4, 3), fc='none', ec='0.7')

    melbourne_ax.set_title('Melbourne')
    #lower corner of the original image
    x_melbourne_lc, y_melbourne_lc = melbourne_m(melbourne_boundary[0][0], melbourne_boundary[1][1])
    #upper corner of the original image
    x_melbourne_uc, y_melbourne_uc = melbourne_m(melbourne_boundary[1][0], melbourne_boundary[0][1])
    #sub region of the original image
    melbourne_ax.set_xlim(x_melbourne_lc, x_melbourne_uc)
    melbourne_ax.set_ylim(y_melbourne_lc, y_melbourne_uc)
    #create inset
    mark_geo_inset(ax, melbourne_ax, m, melbourne_m, loc1=(2, 1), loc2=(3, 4), fc='none', ec='0.7')

    inner_melbourne_ax.set_title('Inner Melbourne')
    #lower corner of the original image
    x_innermelbourne_lc, y_innermelbourne_lc = inner_melbourne_m(inner_melbourne_boundary[0][0], inner_melbourne_boundary[1][1])
    #upper corner of the original image
    x_innermelbourne_uc, y_innermelbourne_uc = inner_melbourne_m(inner_melbourne_boundary[1][0], inner_melbourne_boundary[0][1])
    #sub region of the original image
    inner_melbourne_ax.set_xlim(x_innermelbourne_lc, x_innermelbourne_uc)
    inner_melbourne_ax.set_ylim(y_innermelbourne_lc, y_innermelbourne_uc)
    mark_geo_inset(melbourne_ax, inner_melbourne_ax, melbourne_m, inner_melbourne_m, loc1=(2, 1), loc2=(3, 4), fc='none', ec='0.7')

    act_ax.set_title('ACT')
    #lower corner of the original image
    x_act_lc, y_act_lc = act_m(act_boundary[0][0], act_boundary[1][1])
    #upper corner of the original image
    x_act_uc, y_act_uc = act_m(act_boundary[1][0], act_boundary[0][1])
    #sub region of the original image
    act_ax.set_xlim(x_act_lc, x_act_uc)
    act_ax.set_ylim(y_act_lc, y_act_uc)
    #create inset
    mark_geo_inset(ax, act_ax, m, act_m, loc1=(2, 1), loc2=(3, 4), fc='none', ec='0.7')

    sydney_ax.set_title('Sydney')
    #lower corner of the original image
    x_sydney_lc, y_sydney_lc = sydney_m(sydney_boundary[0][0], sydney_boundary[1][1])
    #upper corner of the original image
    x_sydney_uc, y_sydney_uc = sydney_m(sydney_boundary[1][0], sydney_boundary[0][1])
    #sub region of the original image
    sydney_ax.set_xlim(x_sydney_lc, x_sydney_uc)
    sydney_ax.set_ylim(y_sydney_lc, y_sydney_uc)
    #create inset
    mark_geo_inset(ax, sydney_ax, m, sydney_m, loc1=(2, 1), loc2=(3, 4), fc='none', ec='0.7')

    inner_sydney_ax.set_title('Inner Sydney')
    #lower corner of the original image
    x_innersydney_lc, y_innersydney_lc = inner_sydney_m(inner_sydney_boundary[0][0], inner_sydney_boundary[1][1])
    #upper corner of the original image
    x_innersydney_uc, y_innersydney_uc = inner_sydney_m(inner_sydney_boundary[1][0], inner_sydney_boundary[0][1])
    #sub region of the original image
    inner_sydney_ax.set_xlim(x_innersydney_lc, x_innersydney_uc)
    inner_sydney_ax.set_ylim(y_innersydney_lc, y_innersydney_uc)
    mark_geo_inset(sydney_ax, inner_sydney_ax, sydney_m, inner_sydney_m, loc1=(3, 2), loc2=(4, 1), fc='none', ec='0.7')

    brisbane_ax.set_title('Brisbane')
    #lower corner of the original image
    x_brisbane_lc, y_brisbane_lc = brisbane_m(brisbane_boundary[0][0], brisbane_boundary[1][1])
    #upper corner of the original image
    x_brisbane_uc, y_brisbane_uc = brisbane_m(brisbane_boundary[1][0], brisbane_boundary[0][1])
    #sub region of the original image
    brisbane_ax.set_xlim(x_brisbane_lc, x_brisbane_uc)
    brisbane_ax.set_ylim(y_brisbane_lc, y_brisbane_uc)
    #create inset
    mark_geo_inset(ax, brisbane_ax, m, brisbane_m, loc1=(3, 2), loc2=(4, 1), fc='none', ec='0.7')

    darwin_ax.set_title('Darwin')
    #lower corner of the original image
    x_darwin_lc, y_darwin_lc = darwin_m(darwin_boundary[0][0], darwin_boundary[1][1])
    #upper corner of the original image
    x_darwin_uc, y_darwin_uc = darwin_m(darwin_boundary[1][0], darwin_boundary[0][1])
    #sub region of the original image
    darwin_ax.set_xlim(x_darwin_lc, x_darwin_uc)
    darwin_ax.set_ylim(y_darwin_lc, y_darwin_uc)
    #create inset
    mark_geo_inset(ax, darwin_ax, m, darwin_m, loc1=(1, 2), loc2=(4, 3), fc='none', ec='0.7')

    norm = colors.Normalize(vmin=0, vmax=max_boundary)
    cbar_ticks = np.linspace(0, max_boundary, num=5)
    if pop_heatmap == heatmap[0]:
        cbar_ticklabels = [str(round(number=(x * 100), ndigits=1)) + '%' for x in cbar_ticks]
    elif pop_heatmap == heatmap[1]:
        cbar_ticklabels = [str(round(number=(x), ndigits=0)) for x in cbar_ticks]
    elif pop_heatmap == heatmap[2]:
        cbar_ticklabels = [str(round(number=(x), ndigits=1)) for x in cbar_ticks]

    cbar = colorbar.ColorbarBase(ax=ax_colorbar, cmap=cmap, norm=norm, alpha=alpha)
    cbar.set_ticks(ticks=cbar_ticks, update_ticks=True)
    cbar.set_ticklabels(ticklabels=cbar_ticklabels, update_ticks=True)
    ax.set_title(pop_heatmap)

    #display the map
    plt.show()
    #plt.savefig(pop_heatmap + '.png')

#read the shape file
sf = shp.Reader('./data/national-esri-fe2019/COM_ELB_region.shp')

#load shape file into a panda dataframe
#'Elect_div' [0], 'State' [1], 'Numccds' [2], 'Actual' [3], 'Projected' [4], 'Total_Popu' [5], 'Australian' [6], 'Area_SqKm' [7], 'Sortname' [8], coords [9]
df = read_shapefile(sf)

#view shape of specific shapefile
#elect_row = 8
#plot_shape(elect_row, sf, sf.records()[elect_row][0])

#load details of Indigenous populations by electorate
indigenous_population = pd.read_csv('./data/Indigenous Population 2019.csv', index_col='Federal Electorate')

#map indigenous populations to electorate, subject to the type of heatmap chosen
heatmap = ['Indigenous Population Percentage', 'Indigenous Population', 'Indigenous Population per SqKm']
plot_map(sf, heatmap[0])


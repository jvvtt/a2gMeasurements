import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Arc
from matplotlib.transforms import IdentityTransform, TransformedBbox, Bbox
from matplotlib.animation import FuncAnimation
from pyproj import CRS, Transformer, Geod
import pandas as pd
from PIL import Image, ImageDraw
from pyproj import Transformer, Geod
from selenium import webdriver
import folium
import os
import math
from pyrosm import OSM, get_data

def geocentric2geodetic(X, Y, Z, EPSG_GEODETIC=4979, EPSG_GEOCENTRIC=4978):
    """
    Given Geocentric coordinates referred to a datum (given by EPSG_GEOCENTRIC), convert them
    to Geodetic (lat, lon, height) in the datum given by EPSG_GEODETIC.    

    Args:
        X (float): geocentric X coordinate. 
        Y (float): geocentric Y coordinate.
        Z (float): geocentric Z coordinate.
        EPSG_GEODETIC (int, optional): _description_. Defaults to 4979, that corresponds to WSG84 (geodetic)
        EPSG_GEOCENTRIC (int, optional): _description_. Defaults to 4978, that corresponds to WSG84 (geocentric).
    """

    geodet_crs = CRS.from_epsg(4979) # Geodetic (lat,lon,h) system
    geocent_crs = CRS.from_epsg(4978) # Geocentric (X,Y,Z) system

    geocent_to_geodet = Transformer.from_crs(geocent_crs, geodet_crs)

    lat, lon, height = geocent_to_geodet.transform(X, Y, Z)

    return lat, lon, height

def geodetic2geocentric(lat, lon, height, EPSG_GEODETIC=4979, EPSG_GEOCENTRIC=4978):
    """
    Given Geodetic coordinates (lat, lon, h), convert them 
    to Geocentric  in the datum given by EPSG_GEOCENTRIC.    

    Args:
        lat (float): latitude (N)
        lon (float): longitude (E).
        height (float): height in meters.
        EPSG_GEODETIC (int, optional): _description_. Defaults to 4979, that corresponds to WSG84 (geodetic)
        EPSG_GEOCENTRIC (int, optional): _description_. Defaults to 4978, that corresponds to WSG84 (geocentric).
    """

    geodet_crs = CRS.from_epsg(4979) # Geodetic (lat,lon,h) system
    geocent_crs = CRS.from_epsg(4978) # Geocentric (X,Y,Z) system

    geodet_to_geocent = Transformer.from_crs(geodet_crs, geocent_crs)

    X, Y, Z = geodet_to_geocent.transform(lat, lon, height)

    return X, Y, Z

def make_flight_graph_coordinates(flight_graph, number_stops_per_edge):
        """
        Calculates the intermediate coordinates for the flight graph provided with the given number of stops per edge.

        
        Args:
            flight_graph (numpy 2d-array): the provided array rows MUST be ordered according to the 
                                           order of the planned stops of the drone. For example:
                                           1st row corresponds to the first stop of the drone,
                                           2nd row corresponds to the second stop of the drone, and so on.
            number_stops_per_edge (int): number of stops per edge. It includes both vertexes of the edge.

        Raises:
            Exception: _description_

        Returns:
            intermediate_coords (dict): a dictionary whose structure is as follows:
                                        {'EDGE_1': {'LAT': [], 'LON':[]}, 'EDGE_2': {'LAT': [], 'LON':[]}, ...}
        """
        
        flight_graph_2nd_end = flight_graph[1:, :]
        flight_graph_1st_before_end = flight_graph[:-1, :]

        wgs84_geod = Geod(ellps='WGS84')
                
        az12, _, dist = wgs84_geod.inv(flight_graph_1st_before_end[:, 1], 
                                          flight_graph_1st_before_end[:, 0], 
                                          flight_graph_2nd_end[:, 1], 
                                          flight_graph_2nd_end[:, 0])

        intermediate_coords = {}
        for i in range(flight_graph_2nd_end.shape[0]):
            intermediate_coords['EDGE_'+str(i+1)] = {'LAT': [], 'LON': []}
            lon_2, lat_2, _ = wgs84_geod.fwd(flight_graph_1st_before_end[i, 1], flight_graph_1st_before_end[i, 0], az12[i], dist[i]/(number_stops_per_edge-1))
            intermediate_coords['EDGE_'+str(i+1)]['LAT'].append(lat_2)
            intermediate_coords['EDGE_'+str(i+1)]['LON'].append(lon_2)
            
            for j in range(number_stops_per_edge-3):
                lon_2, lat_2, _ = wgs84_geod.fwd(lon_2, lat_2, az12[i], dist[i]/(number_stops_per_edge-1))
                intermediate_coords['EDGE_'+str(i+1)]['LAT'].append(lat_2)
                intermediate_coords['EDGE_'+str(i+1)]['LON'].append(lon_2)
        
        return intermediate_coords

class GPSVis(object):
    """
        Class for GPS data visualization using pre-downloaded OSM map in image format.
    """
    def __init__(self, data_path=None, map_path=None, points=None):
        """
        :param data_path: Path to file containing GPS records.
        :param map_path: Path to pre-downloaded OSM map in image format.
        :param points: 4-tuple consisting in the following (upper_left_lat, upper_left_lon, bottom_right_lat, bottom_right_lon)
        """
        self.data_path = data_path
        self.points = points
        self.map_path = map_path
        
        if map_path is None:
            self.capture_map_image(*points)
            self.map_path = 'map.png'
        
        self.result_image = Image.open(self.map_path, 'r')
        self.x_ticks = []
        self.y_ticks = []

    def plot_map(self, output='save', save_as='resultMap.png'):
        """
        Method for plotting the map. You can choose to save it in file or to plot it.
        :param output: Type 'plot' to show the map or 'save' to save it.
        :param save_as: Name and type of the resulting image.
        :return:
        """
        self.get_ticks()
        _, axis1 = plt.subplots(figsize=(10, 10))
        axis1.imshow(self.result_image)
        axis1.set_xlabel('Longitude')
        axis1.set_ylabel('Latitude')
        axis1.set_xticklabels(self.x_ticks)
        axis1.set_yticklabels(self.y_ticks)
        axis1.grid()
        
        #axis1.scatter([i[0] for i in self.img_points], [i[1] for i in self.img_points], marker='x')
        
        if output == 'save':
            plt.savefig(save_as)
        else:
            plt.show()
    
    def update_map_marker(self, gps_coordinates, r=10):
        
        x1, y1 = self.scale_to_img(gps_coordinates, (self.result_image.size[0], self.result_image.size[1]))
        draw = ImageDraw.Draw(self.result_image)
        draw.ellipse((x1-r, y1-r, x1+r, y1+r), fill=(0,0,0))

    def create_image(self, color, width=2, heading=None):
        """
        Create the image that contains the original map and the GPS records.
        :param color: Color of the GPS records.
        :param width: Width of the drawn GPS records.
        :return:
        """
        data = pd.read_csv(self.data_path, names=['LATITUDE', 'LONGITUDE'], sep=',')

        self.result_image = Image.open(self.map_path, 'r')
        img_points = []
        gps_data = tuple(zip(data['LATITUDE'].values, data['LONGITUDE'].values))
        
        for d in gps_data:
            x1, y1 = self.scale_to_img(d, (self.result_image.size[0], self.result_image.size[1]))
            img_points.append((x1, y1))
            
        img_points_2 = []
        
        for i in range(0, len(img_points)-1):
            img_points_2.append(img_points[-1])
            img_points_2.append(img_points[i])
        
        if heading:
            wgs84_geod = Geod(ellps='WGS84')
            endlon, endlat, _ = wgs84_geod.fwd(gps_data[-1][1], gps_data[-1][0], heading, 50)
            
            x1, y1 = self.scale_to_img((endlat, endlon), (self.result_image.size[0], self.result_image.size[1]))
            img_points_2.append(img_points[-1])
            img_points_2.append((x1,y1))    
        
        draw = ImageDraw.Draw(self.result_image)
        draw.line(img_points_2, fill=color, width=width)
                               

    def scale_to_img(self, lat_lon, h_w):
        """
        Conversion from latitude and longitude to the image pixels.
        It is used for drawing the GPS records on the map image.
        :param lat_lon: GPS record to draw (lat1, lon1).
        :param h_w: Size of the map image (w, h).
        :return: Tuple containing x and y coordinates to draw on map image.
        """
        # https://gamedev.stackexchange.com/questions/33441/how-to-convert-a-number-from-one-min-max-set-to-another-min-max-set/33445
        old = (self.points[2], self.points[0])
        new = (0, h_w[1])
        y = ((lat_lon[0] - old[0]) * (new[1] - new[0]) / (old[1] - old[0])) + new[0]
        old = (self.points[1], self.points[3])
        new = (0, h_w[0])
        x = ((lat_lon[1] - old[0]) * (new[1] - new[0]) / (old[1] - old[0])) + new[0]
        # y must be reversed because the orientation of the image in the matplotlib.
        # image - (0, 0) in upper left corner; coordinate system - (0, 0) in lower left corner
        return int(x), h_w[1] - int(y)

    def get_ticks(self):
        """
        Generates custom ticks based on the GPS coordinates of the map for the matplotlib output.
        :return:
        """
        self.x_ticks = map(
            lambda x: round(x, 4),
            np.linspace(self.points[1], self.points[3], num=7))
        y_ticks = map(
            lambda x: round(x, 4),
            np.linspace(self.points[2], self.points[0], num=8))
        # Ticks must be reversed because the orientation of the image in the matplotlib.
        # image - (0, 0) in upper left corner; coordinate system - (0, 0) in lower left corner
        self.y_ticks = sorted(y_ticks, reverse=True)
    
    def capture_map_image(self, upper_lat, upper_lon, bottom_lat, bottom_lon, width=800, height=600, output_file='map.png'):
        """
        Capture map image as closest as possible to the rectanlge defined by its upper_left corner and lower right corner
        coordinates.

        Args:
            upper_lat (float): latitude of upper left corner
            upper_lon (float): longitude of upper left corner
            bottom_lat (float): latitude of bottom right corner
            bottom_lon (float): longitude of bottom right corner
            width (int, optional): _description_. Defaults to 800.
            height (int, optional): _description_. Defaults to 600.
            output_file (str, optional): Filename of the map to be used to 
                                        display GPS coordinates. Defaults to 'map.png'.
        """
        
        center_lat = (upper_lat + bottom_lat) / 2
        center_lng = (upper_lon + bottom_lon) / 2
        
        #zoom = self.get_zoom_level(upper_lat, upper_lon, bottom_lat, bottom_lon, width, height)
        #m = folium.Map(location=[center_lat, center_lng], zoom_start=zoom, control_scale=True)

        m = folium.Map(location=[center_lat, center_lng])
        
        # Create a rectangle overlay using the provided coordinates
        bounds = [[upper_lat, upper_lon], [bottom_lat, bottom_lon]]
        rect = folium.Rectangle(bounds, color='#3186cc', fill=False, fill_opacity=0.3)
        rect.add_to(m)
        m.fit_bounds([[bottom_lat, upper_lon], [upper_lat, bottom_lon]]) 
        
        # Save the map as an HTML file
        tmp_html = 'create_map_test.html'
        m.save(tmp_html)

        # Use Selenium to capture a screenshot of the map
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Run Chrome in headless mode
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(options=options)
        driver.set_window_size(1920, 1080)  # Adjust the window size as needed
        driver.get(os.getcwd() + '\\' + tmp_html)
        driver.get_screenshot_as_file(output_file)
        driver.quit()

        # Crop the screenshot to the bounds of the rectangle overlay
        im = Image.open(output_file)
        left = int(im.width * (upper_lon - bounds[0][1]) / (bounds[1][1] - bounds[0][1]))
        upper = int(im.height * (bounds[0][0] - upper_lat) / (bounds[0][0] - bounds[1][0]))
        right = int(im.width * (bottom_lon - bounds[0][1]) / (bounds[1][1] - bounds[0][1]))
        lower = int(im.height * (bounds[0][0] - bottom_lat) / (bounds[0][0] - bounds[1][0]))
        im = im.crop((left, upper, right, lower))
        im.save(output_file)

        # Remove the temporary HTML file
        os.remove(tmp_html)
    
    def get_zoom_level(self, upper_lat, upper_lon, bottom_lat, bottom_lon, width, height):
        """
        Calculate the zoom level based on the map dimensions and rectangle coordinates.
        This produce a zoom level that is still zooming out the rectangle bound by the upper left and lower_right corner.

        Maintained for compatibility with a previous version of this code (commented lines in "capture_map_image" function)
        
        Args:
            upper_lat (_type_): _description_
            upper_lon (_type_): _description_
            bottom_lat (_type_): _description_
            bottom_lon (_type_): _description_
            width (_type_): _description_
            height (_type_): _description_

        Returns:
            _type_: _description_
        """
        lat_diff = abs(upper_lat - bottom_lat)
        lng_diff = abs(upper_lon - bottom_lon)

        # Calculate the zoom level based on the width and height of the map
        lat_zoom = math.log(360 * height / 256 / lat_diff) / math.log(2)
        lng_zoom = math.log(360 * width / 256 / lng_diff) / math.log(2)

        zoom = min(lat_zoom, lng_zoom)
        return int(zoom)



class GpsOnMap(object):
    
    def __init__(self, path_to_osmpbf, canvas=None,fig=None, ax=None, air_coord=None, gnd_coord=None):
        """
        This is a handler for the canvas element where gps coords are plot

        It requires an .osm.pbf picture of the map get from https://extract.bbbike.org/
        
        Args:
            path_to_osmpbf (str): path to .osm.pbf file
            canvas (widget, optional): canvas widget from app. Defaults to None.
            fig (fig, optional): _description_. Defaults to None.
            ax (ax, optional): _description_. Defaults to None.
            air_coord (dictionary, optional): the keys of the dictionary should be "LAT" and "LON". Defaults to None.
            gnd_coord (dictionary, optional): the keys of the dictionary should be "LAT" and "LON". Defaults to None.
        """
        
        #plt.rcParams['animation.html'] = 'jshtml'
        if ax is None and fig is None:
            fig, ax = plt.subplots()
        elif ax is not None and fig is None:
            print('\n[DEBUG]: figure handle not provided')
        elif fig is not None and ax is None:
            print('\n[DEBUG]: axes handle not provided')
        
        self.ax = ax
        self.fig = fig
        self.canvas = canvas
        
        # Initialize the OSM parser object
        osm = OSM(path_to_osmpbf)
        
        # Plot cycling, driving and walking layers, and also buildings
        cycling_net = osm.get_network(network_type="cycling")
        drive_net = osm.get_network(network_type="driving")
        walking_net = osm.get_network(network_type="walking")
        buildings = osm.get_buildings()

        cycling_net.plot(ax=self.ax)
        buildings.plot(ax=self.ax)
        walking_net.plot(ax=self.ax)
        
        self.air_coord = air_coord
        
        if air_coord is not None:
            self.rx_pos, =self.ax.plot(air_coord['LON'], air_coord['LAT'], 'b+', markersize=15)

        self.test_cnt = 1
        self.fut_hub = {'LAT': 60.18650, 'LON': 24.81350}
        self.rx_pos.set_data(self.air_coord['LON'], self.air_coord['LAT'])
        
        if canvas is None:
            plt.show()
        else:
            self.canvas.draw()
        
    def show_air_moving(self):     
        """
        Updates the plot with the new positions
        """
        
        if self.test_cnt % 2:
            self.rx_pos.set_data(self.fut_hub['LON'], self.fut_hub['LAT'])
        else:
            self.rx_pos.set_data(self.air_coord['LON'], self.air_coord['LAT'])
        
        if self.canvas is None:
            plt.show()
        else:
            self.canvas.draw()
        
        self.test_cnt = self.test_cnt + 1
        
    def animate(self, i):
        """
        Function to be passed to FuncAnimation

        Args:
            i (int): frame number
        """
        if i % 2:
            self.rx_pos.set_data(self.air_coord['LON'], self.air_coord['LAT'])
        else:
            fut_hub = {'LAT': 60.18650, 'LON': 24.81350}
            self.rx_pos.set_data(fut_hub['LON'], fut_hub['LAT'])

    def show(self, frames=None, interval=100):
        """
        Executes the animation for the number of frames. It executes a function 
        for the given number of frames.

        Args:
            frames (_type_, optional): _description_. Defaults to None.
            interval (int, optional): _description_. Defaults to 100.
        """
        anim = FuncAnimation(self.fig, self.animate, frames=frames, interval=interval)
        if self.canvas is None:
            plt.show()
        else:
            self.canvas.draw()


class AngleAnnotation(Arc):
    """
    Draws an arc between two vectors which appears circular in display space. Implementation
    of class Arc
    """
    def __init__(self, xy, p1, p2, size=75, unit="points", ax=None,
                 text="", textposition="inside", text_kw=None, **kwargs):
        """
        Parameters
        ----------
        xy, p1, p2 : tuple or array of two floats
            Center position and two points. Angle annotation is drawn between
            the two vectors connecting *p1* and *p2* with *xy*, respectively.
            Units are data coordinates.

        size : float
            Diameter of the angle annotation in units specified by *unit*.

        unit : str
            One of the following strings to specify the unit of *size*:

            * "pixels": pixels
            * "points": points, use points instead of pixels to not have a
              dependence on the DPI
            * "axes width", "axes height": relative units of Axes width, height
            * "axes min", "axes max": minimum or maximum of relative Axes
              width, height

        ax : `matplotlib.axes.Axes`
            The Axes to add the angle annotation to.

        text : str
            The text to mark the angle with.

        textposition : {"inside", "outside", "edge"}
            Whether to show the text in- or outside the arc. "edge" can be used
            for custom positions anchored at the arc's edge.

        text_kw : dict
            Dictionary of arguments passed to the Annotation.

        **kwargs
            Further parameters are passed to `matplotlib.patches.Arc`. Use this
            to specify, color, linewidth etc. of the arc.

        """
        self.ax = ax or plt.gca()
        self._xydata = xy  # in data coordinates
        self.vec1 = p1
        self.vec2 = p2
        self.size = size
        self.unit = unit
        self.textposition = textposition

        super().__init__(self._xydata, size, size, angle=0.0,
                         theta1=self.theta1, theta2=self.theta2, **kwargs)

        self.set_transform(IdentityTransform())
        
        if self.ax.patches:
            #for i in self.ax.patches:
            #    i.remove()
            if len(self.ax.patches) > 1:
                self.ax.patches[0].remove()
            
        if self.ax.texts:
            #for i in range(len(self.ax.texts)-1):
            #    if isinstance(i, matplotlib.text.Annotation):
            #        i.remove()            
            if len(self.ax.texts) > 4:
                for i in self.ax.texts[3:-1]:
                    i.remove()
        
        self.ax.add_patch(self)

        self.kw = dict(ha="center", va="center",
                       xycoords=IdentityTransform(),
                       xytext=(0, 0), textcoords="offset points",
                       annotation_clip=True)
        self.kw.update(text_kw or {})
        self.text = ax.annotate(text, xy=self._center, **self.kw)

    def get_size(self):
        factor = 1.
        if self.unit == "points":
            factor = self.ax.figure.dpi / 72.
        elif self.unit[:4] == "axes":
            b = TransformedBbox(Bbox.unit(), self.ax.transAxes)
            dic = {"max": max(b.width, b.height),
                   "min": min(b.width, b.height),
                   "width": b.width, "height": b.height}
            factor = dic[self.unit[5:]]
        return self.size * factor

    def set_size(self, size):
        self.size = size

    def get_center_in_pixels(self):
        """return center in pixels"""
        return self.ax.transData.transform(self._xydata)

    def set_center(self, xy):
        """set center in data coordinates"""
        self._xydata = xy

    def get_theta(self, vec):
        vec_in_pixels = self.ax.transData.transform(vec) - self._center
        return np.rad2deg(np.arctan2(vec_in_pixels[1], vec_in_pixels[0]))

    def get_theta1(self):
        return self.get_theta(self.vec1)

    def get_theta2(self):
        return self.get_theta(self.vec2)

    def set_theta(self, angle):
        pass

    # Redefine attributes of the Arc to always give values in pixel space
    _center = property(get_center_in_pixels, set_center)
    theta1 = property(get_theta1, set_theta)
    theta2 = property(get_theta2, set_theta)
    width = property(get_size, set_size)
    height = property(get_size, set_size)

    # The following two methods are needed to update the text position.
    def draw(self, renderer):
        self.update_text()
        super().draw(renderer)

    def update_text(self):
        c = self._center
        s = self.get_size()
        angle_span = (self.theta2 - self.theta1) % 360
        angle = np.deg2rad(self.theta1 + angle_span / 2)
        r = s / 2
        if self.textposition == "inside":
            r = s / np.interp(angle_span, [60, 90, 135, 180],
                                          [3.3, 3.5, 3.8, 4])
        self.text.xy = c + r * np.array([np.cos(angle), np.sin(angle)])
        if self.textposition == "outside":
            def R90(a, r, w, h):
                if a < np.arctan(h/2/(r+w/2)):
                    return np.sqrt((r+w/2)**2 + (np.tan(a)*(r+w/2))**2)
                else:
                    c = np.sqrt((w/2)**2+(h/2)**2)
                    T = np.arcsin(c * np.cos(np.pi/2 - a + np.arcsin(h/2/c))/r)
                    xy = r * np.array([np.cos(a + T), np.sin(a + T)])
                    xy += np.array([w/2, h/2])
                    return np.sqrt(np.sum(xy**2))

            def R(a, r, w, h):
                aa = (a % (np.pi/4))*((a % (np.pi/2)) <= np.pi/4) + \
                     (np.pi/4 - (a % (np.pi/4)))*((a % (np.pi/2)) >= np.pi/4)
                return R90(aa, r, *[w, h][::int(np.sign(np.cos(2*a)))])

            bbox = self.text.get_window_extent()
            X = R(angle, r, bbox.width, bbox.height)
            trans = self.ax.figure.dpi_scale_trans.inverted()
            offs = trans.transform(((X-s/2), 0))[0] * 72
            self.text.set_position([offs*np.cos(angle), offs*np.sin(angle)])
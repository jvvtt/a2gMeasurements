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

class Checksum(object):
    def __init__(self):
        self.MASK_BIT_TYPE = 0XFF
        self.MAX_INT_8 = 256

        self.CRC16_Table = (
            0x0000, 0xc0c1, 0xc181, 0x0140, 0xc301, 0x03c0, 0x0280, 0xc241,
            0xc601, 0x06c0, 0x0780, 0xc741, 0x0500, 0xc5c1, 0xc481, 0x0440,
            0xcc01, 0x0cc0, 0x0d80, 0xcd41, 0x0f00, 0xcfc1, 0xce81, 0x0e40,
            0x0a00, 0xcac1, 0xcb81, 0x0b40, 0xc901, 0x09c0, 0x0880, 0xc841,
            0xd801, 0x18c0, 0x1980, 0xd941, 0x1b00, 0xdbc1, 0xda81, 0x1a40,
            0x1e00, 0xdec1, 0xdf81, 0x1f40, 0xdd01, 0x1dc0, 0x1c80, 0xdc41,
            0x1400, 0xd4c1, 0xd581, 0x1540, 0xd701, 0x17c0, 0x1680, 0xd641,
            0xd201, 0x12c0, 0x1380, 0xd341, 0x1100, 0xd1c1, 0xd081, 0x1040,
            0xf001, 0x30c0, 0x3180, 0xf141, 0x3300, 0xf3c1, 0xf281, 0x3240,
            0x3600, 0xf6c1, 0xf781, 0x3740, 0xf501, 0x35c0, 0x3480, 0xf441,
            0x3c00, 0xfcc1, 0xfd81, 0x3d40, 0xff01, 0x3fc0, 0x3e80, 0xfe41,
            0xfa01, 0x3ac0, 0x3b80, 0xfb41, 0x3900, 0xf9c1, 0xf881, 0x3840,
            0x2800, 0xe8c1, 0xe981, 0x2940, 0xeb01, 0x2bc0, 0x2a80, 0xea41,
            0xee01, 0x2ec0, 0x2f80, 0xef41, 0x2d00, 0xedc1, 0xec81, 0x2c40,
            0xe401, 0x24c0, 0x2580, 0xe541, 0x2700, 0xe7c1, 0xe681, 0x2640,
            0x2200, 0xe2c1, 0xe381, 0x2340, 0xe101, 0x21c0, 0x2080, 0xe041,
            0xa001, 0x60c0, 0x6180, 0xa141, 0x6300, 0xa3c1, 0xa281, 0x6240,
            0x6600, 0xa6c1, 0xa781, 0x6740, 0xa501, 0x65c0, 0x6480, 0xa441,
            0x6c00, 0xacc1, 0xad81, 0x6d40, 0xaf01, 0x6fc0, 0x6e80, 0xae41,
            0xaa01, 0x6ac0, 0x6b80, 0xab41, 0x6900, 0xa9c1, 0xa881, 0x6840,
            0x7800, 0xb8c1, 0xb981, 0x7940, 0xbb01, 0x7bc0, 0x7a80, 0xba41,
            0xbe01, 0x7ec0, 0x7f80, 0xbf41, 0x7d00, 0xbdc1, 0xbc81, 0x7c40,
            0xb401, 0x74c0, 0x7580, 0xb541, 0x7700, 0xb7c1, 0xb681, 0x7640,
            0x7200, 0xb2c1, 0xb381, 0x7340, 0xb101, 0x71c0, 0x7080, 0xb041,
            0x5000, 0x90c1, 0x9181, 0x5140, 0x9301, 0x53c0, 0x5280, 0x9241,
            0x9601, 0x56c0, 0x5780, 0x9741, 0x5500, 0x95c1, 0x9481, 0x5440,
            0x9c01, 0x5cc0, 0x5d80, 0x9d41, 0x5f00, 0x9fc1, 0x9e81, 0x5e40,
            0x5a00, 0x9ac1, 0x9b81, 0x5b40, 0x9901, 0x59c0, 0x5880, 0x9841,
            0x8801, 0x48c0, 0x4980, 0x8941, 0x4b00, 0x8bc1, 0x8a81, 0x4a40,
            0x4e00, 0x8ec1, 0x8f81, 0x4f40, 0x8d01, 0x4dc0, 0x4c80, 0x8c41,
            0x4400, 0x84c1, 0x8581, 0x4540, 0x8701, 0x47c0, 0x4680, 0x8641,
            0x8201, 0x42c0, 0x4380, 0x8341, 0x4100, 0x81c1, 0x8081, 0x4040,
        )

        self.CRC32_Table = (
            0x00000000, 0x77073096, 0xee0e612c, 0x990951ba, 0x076dc419, 0x706af48f, 0xe963a535, 0x9e6495a3,
            0x0edb8832, 0x79dcb8a4, 0xe0d5e91e, 0x97d2d988, 0x09b64c2b, 0x7eb17cbd, 0xe7b82d07, 0x90bf1d91,
            0x1db71064, 0x6ab020f2, 0xf3b97148, 0x84be41de, 0x1adad47d, 0x6ddde4eb, 0xf4d4b551, 0x83d385c7,
            0x136c9856, 0x646ba8c0, 0xfd62f97a, 0x8a65c9ec, 0x14015c4f, 0x63066cd9, 0xfa0f3d63, 0x8d080df5,
            0x3b6e20c8, 0x4c69105e, 0xd56041e4, 0xa2677172, 0x3c03e4d1, 0x4b04d447, 0xd20d85fd, 0xa50ab56b,
            0x35b5a8fa, 0x42b2986c, 0xdbbbc9d6, 0xacbcf940, 0x32d86ce3, 0x45df5c75, 0xdcd60dcf, 0xabd13d59,
            0x26d930ac, 0x51de003a, 0xc8d75180, 0xbfd06116, 0x21b4f4b5, 0x56b3c423, 0xcfba9599, 0xb8bda50f,
            0x2802b89e, 0x5f058808, 0xc60cd9b2, 0xb10be924, 0x2f6f7c87, 0x58684c11, 0xc1611dab, 0xb6662d3d,
            0x76dc4190, 0x01db7106, 0x98d220bc, 0xefd5102a, 0x71b18589, 0x06b6b51f, 0x9fbfe4a5, 0xe8b8d433,
            0x7807c9a2, 0x0f00f934, 0x9609a88e, 0xe10e9818, 0x7f6a0dbb, 0x086d3d2d, 0x91646c97, 0xe6635c01,
            0x6b6b51f4, 0x1c6c6162, 0x856530d8, 0xf262004e, 0x6c0695ed, 0x1b01a57b, 0x8208f4c1, 0xf50fc457,
            0x65b0d9c6, 0x12b7e950, 0x8bbeb8ea, 0xfcb9887c, 0x62dd1ddf, 0x15da2d49, 0x8cd37cf3, 0xfbd44c65,
            0x4db26158, 0x3ab551ce, 0xa3bc0074, 0xd4bb30e2, 0x4adfa541, 0x3dd895d7, 0xa4d1c46d, 0xd3d6f4fb,
            0x4369e96a, 0x346ed9fc, 0xad678846, 0xda60b8d0, 0x44042d73, 0x33031de5, 0xaa0a4c5f, 0xdd0d7cc9,
            0x5005713c, 0x270241aa, 0xbe0b1010, 0xc90c2086, 0x5768b525, 0x206f85b3, 0xb966d409, 0xce61e49f,
            0x5edef90e, 0x29d9c998, 0xb0d09822, 0xc7d7a8b4, 0x59b33d17, 0x2eb40d81, 0xb7bd5c3b, 0xc0ba6cad,
            0xedb88320, 0x9abfb3b6, 0x03b6e20c, 0x74b1d29a, 0xead54739, 0x9dd277af, 0x04db2615, 0x73dc1683,
            0xe3630b12, 0x94643b84, 0x0d6d6a3e, 0x7a6a5aa8, 0xe40ecf0b, 0x9309ff9d, 0x0a00ae27, 0x7d079eb1,
            0xf00f9344, 0x8708a3d2, 0x1e01f268, 0x6906c2fe, 0xf762575d, 0x806567cb, 0x196c3671, 0x6e6b06e7,
            0xfed41b76, 0x89d32be0, 0x10da7a5a, 0x67dd4acc, 0xf9b9df6f, 0x8ebeeff9, 0x17b7be43, 0x60b08ed5,
            0xd6d6a3e8, 0xa1d1937e, 0x38d8c2c4, 0x4fdff252, 0xd1bb67f1, 0xa6bc5767, 0x3fb506dd, 0x48b2364b,
            0xd80d2bda, 0xaf0a1b4c, 0x36034af6, 0x41047a60, 0xdf60efc3, 0xa867df55, 0x316e8eef, 0x4669be79,
            0xcb61b38c, 0xbc66831a, 0x256fd2a0, 0x5268e236, 0xcc0c7795, 0xbb0b4703, 0x220216b9, 0x5505262f,
            0xc5ba3bbe, 0xb2bd0b28, 0x2bb45a92, 0x5cb36a04, 0xc2d7ffa7, 0xb5d0cf31, 0x2cd99e8b, 0x5bdeae1d,
            0x9b64c2b0, 0xec63f226, 0x756aa39c, 0x026d930a, 0x9c0906a9, 0xeb0e363f, 0x72076785, 0x05005713,
            0x95bf4a82, 0xe2b87a14, 0x7bb12bae, 0x0cb61b38, 0x92d28e9b, 0xe5d5be0d, 0x7cdcefb7, 0x0bdbdf21,
            0x86d3d2d4, 0xf1d4e242, 0x68ddb3f8, 0x1fda836e, 0x81be16cd, 0xf6b9265b, 0x6fb077e1, 0x18b74777,
            0x88085ae6, 0xff0f6a70, 0x66063bca, 0x11010b5c, 0x8f659eff, 0xf862ae69, 0x616bffd3, 0x166ccf45,
            0xa00ae278, 0xd70dd2ee, 0x4e048354, 0x3903b3c2, 0xa7672661, 0xd06016f7, 0x4969474d, 0x3e6e77db,
            0xaed16a4a, 0xd9d65adc, 0x40df0b66, 0x37d83bf0, 0xa9bcae53, 0xdebb9ec5, 0x47b2cf7f, 0x30b5ffe9,
            0xbdbdf21c, 0xcabac28a, 0x53b39330, 0x24b4a3a6, 0xbad03605, 0xcdd70693, 0x54de5729, 0x23d967bf,
            0xb3667a2e, 0xc4614ab8, 0x5d681b02, 0x2a6f2b94, 0xb40bbe37, 0xc30c8ea1, 0x5a05df1b, 0x2d02ef8d,
        )

    def calc_crc16(self, hex_seq):
        Init_CRC = 0x3AA3
        hex_seq = [eval("0x" + hex_num) for hex_num in hex_seq.split(":")]
        for hex_num in hex_seq:
            Init_CRC = ((Init_CRC >> 8) & self.MASK_BIT_TYPE) ^ self.CRC16_Table[(
                Init_CRC ^ hex_num) % self.MAX_INT_8]
        crc_str = "%04X" % Init_CRC
        return crc_str[2:] + ":" + crc_str[0:2]

    def calc_crc32(self, hex_seq):
        Init_CRC = 0x3AA3

        hex_seq2 = [int(hex_num, base=16) for hex_num in hex_seq.split(":")]

        # hex_seq = [int('0x' + hex_num, base=16) for hex_num in hex_seq.split(":")]
        for hex_num in hex_seq2:
            msg = 0x000000ff & hex_num
            tmp = Init_CRC ^ msg
            Init_CRC = (Init_CRC >> 8) ^ self.CRC32_Table[tmp & 0xff]
        crc_str = "%08X" % Init_CRC

        return crc_str[6:] + ":" + crc_str[4:6] + ":" + crc_str[2:4] + ":" + crc_str[0:2]

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

def compute_block_mean_2d_array(array, block_length):
    """
    Compute the block mean of a matrix by assuming the matrix consists of blocks of size
    block_length-by-array.shape[1].
        
    'array' should be a matrix, and 'block_length' should be less than array.shape[1].

    Args:
        array (ndarray): _description_
        block_length (int): _description_
    """
        
    tmp = array.reshape((-1, block_length, array.shape[1]//array.shape[1], array.shape[1]))
    tmp = tmp.transpose((0,2,1,3))
    tmp = np.mean(tmp, axis=(2,))
    tmp = np.squeeze(tmp)
    return tmp      

def azimuth_difference_between_coordinates(heading, lat_origin, lon_origin, lat_dest, lon_dest):
    """
    This is the angle difference between the **heading** direction (angle w.r.t the North) of the node behaving as the origin and the destination node direction (w.r.t the origin node).

    The following picture provides an illustration of the angle to be computed (named here theta).
    
    <figure markdown="span">
    ![Image title](assets/azimuth_difference_btw_coods.PNG){ width="400" }
    <figcaption>Illustration of the angle difference theta</figcaption>
    </figure>
    
    Args:
        heading (float): angle between [0, 2*pi] (rads) corresponding to the heading direction of the line between the two antennas connected to Septentrio's receiver in the origin node. Defaults to None.
        lat_origin (float): latitude of the origin node. 
        lon_origin (float): longitude of the origin node.
        lat_dest (float): latitude of the destination node.
        lon_dest (float): longitude of the destination node. 
    Returns:
        yaw_to_set (int): azimuth angle difference.
    """
    
    wgs84_geod = Geod(ellps='WGS84')
        
    ITFA, _, _ = wgs84_geod.inv(lon_origin, lat_origin, lon_dest, lat_dest)
                
    # Restrict heading to [-pi, pi] interval. No need for < -2*pi check, cause it won't happen
    if heading > 180:
        heading = heading - 360
                    
    yaw_to_set = ITFA - heading

    if yaw_to_set > 180:
        yaw_to_set = yaw_to_set - 360
    elif yaw_to_set < -180:
        yaw_to_set = yaw_to_set + 360
            
    yaw_to_set = int(yaw_to_set*10)
    
    return yaw_to_set

def elevation_difference_between_coordinates(lat_origin, lon_origin, h_origin, lat_dest, lon_dest, h_dest):
    """
    Elevation angle difference between the origin node and the destination node.

    The following picture provides an illustration of the angle to be computed (named here theta).
    
    <figure markdown="span">
    ![Image title](assets/elevation_difference_btw_coods.PNG){ width="400" }
    <figcaption>Illustration of the angle difference phi</figcaption>
    </figure>
    
    Args:
        lat_origin (float): latitude of the origin node. 
        lon_origin (float): longitude of the origin node.
        h_origin (float): height of the origin node.
        lat_dest (float): latitude of the destination node.
        lon_dest (float): longitude of the destination node. 
        h_dest (float): height of the destination node.
    Returns:
        pitch_to_set (int): elevation angle difference.
    """
    
    wgs84_geod = Geod(ellps='WGS84')
        
    # dist_proj_2D is the distance between the origin node and the projection of the destination node to the plane at the height of the origin node.
    _, _, dist_proj_2D = wgs84_geod.inv(lon_origin, lat_origin, lon_dest, lat_dest)
    
    pitch_to_set = np.arctan2(h_dest - h_origin, dist_proj_2D) 
    pitch_to_set = int(np.rad2deg(pitch_to_set)*10)
    
    return pitch_to_set

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
            self.air_pos, =self.ax.plot(air_coord['LON'], air_coord['LAT'], 'b+', markersize=15)

        self.test_cnt = 1
        self.fut_hub = {'LAT': 60.18650, 'LON': 24.81350}
        self.air_pos.set_data(self.air_coord['LON'], self.air_coord['LAT'])
        
        if canvas is None:
            plt.show()
        else:
            self.canvas.draw()
    
    def show_air_moving(self, lat, lon):
        """
        Updates the plot with the new positions
        """
        
        self.air_pos.set_data(lon, lat)
        
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
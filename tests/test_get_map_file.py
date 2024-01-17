from selenium import webdriver
from PIL import Image
import folium
import os
import math

def get_zoom_level(upper_lat, upper_lon, bottom_lat, bottom_lon, width, height):
    """
    Calculate the zoom level based on the map dimensions and rectangle coordinates.
    """
    lat_diff = abs(upper_lat - bottom_lat)
    lng_diff = abs(upper_lon - bottom_lon)

    # Calculate the zoom level based on the width and height of the map
    lat_zoom = math.log(360 * height / 256 / lat_diff) / math.log(2)
    lng_zoom = math.log(360 * width / 256 / lng_diff) / math.log(2)

    zoom = min(lat_zoom, lng_zoom)
    return int(zoom)


def capture_map_image(upper_lat, upper_lon, bottom_lat, bottom_lon, width=800, height=600, output_file='map.png'):
    # Create a folium map centered around the midpoint of point A and point B
    center_lat = (upper_lat + bottom_lat) / 2
    center_lng = (upper_lon + bottom_lon) / 2
    
    zoom = get_zoom_level(upper_lat, upper_lon, bottom_lat, bottom_lon, width, height)
    
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


    '''
    # Crop the screenshot to the bounds of the rectangle overlay
    im = Image.open(output_file)
    left = int(im.width * (upper_lon - bounds[0][1]) / (bounds[1][1] - bounds[0][1]))
    upper = int(im.height * (bounds[0][0] - upper_lat) / (bounds[0][0] - bounds[1][0]))
    right = int(im.width * (bottom_lon - bounds[0][1]) / (bounds[1][1] - bounds[0][1]))
    lower = int(im.height * (bounds[0][0] - bottom_lat) / (bounds[0][0] - bounds[1][0]))
    im = im.crop((left, upper, right, lower))
    im.save(output_file)
    '''
    
    
    # Remove the temporary HTML file
    os.remove(tmp_html)

# Usage
upper_left = {'LAT': 60.1871, 'LON': 24.8113}
lower_right = {'LAT': 60.1837, 'LON': 24.8245}

upper_lat = 60.1871  # Latitude of point A (upper left corner)
upper_lon = 24.8113  # Longitude of point A (upper left corner)
bottom_lat = 60.1837  # Latitude of point B (bottom right corner)
bottom_lon = 24.8245  # Longitude of point B (bottom right corner)

width = 800 # Width of the desired map image in pixels
height = 800 # Height of the desired map image in pixels

capture_map_image(upper_lat, upper_lon, bottom_lat, bottom_lon, width, height, output_file='create_map_test.png')

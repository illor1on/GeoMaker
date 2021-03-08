import webbrowser
import numpy as np
import matplotlib.pyplot as plt
import geojson
from geopandas import gpd
import requests
import flexpolyline
from shapely.geometry import Point, LineString
import folium
from geopy.geocoders import Nominatim



print("Введите адрес старта: ")
start = str(input())

print("Введите адрес окончания: ")
end = str(input())



def get_geo(loc):
    geolocator = Nominatim(user_agent="http")
    location = geolocator.geocode(loc)
    return location.latitude, location.longitude

start = [get_geo(start)]
end = [get_geo(end)]


geo = get_geo()

print("Введите кол-во точек: ")
count_of_points = int(input())

current_points = []
total_points = []

for i in range(count_of_points):
    current_points = []
    for j in range(1):
        px = float(input())
        py = float(input())
        current_points.append(px)
        current_points.append(py)
    total_points.append(current_points)

def distance(P1, P2):
    return ((P1[0]-P2[0])**2+(P1[1]-P2[1])**2)**0.5

def optimized_path(coords, start=None):
    if start is None:
        start = coords[0]
    pass_by = coords
    path = [start]
    pass_by.remove(start)
    while pass_by:
        nearest = min(pass_by, key=lambda x: distance(path[-1],x))
        path.append(nearest)
        pass_by.remove(nearest)
    return path

path = optimized_path(total_points)
x = np.array([i[0] for i in path])
y = np.array([[i] for i in path])

matrix = np.array([x, -y])

plt.plot(matrix[0], matrix[1], maker='o')
for index, coord in enumerate(matrix[0]):
    plt.text(coord, matrix[1][index], str(index))

meters = 100

x_original_point = 41.4352
y_x_original_point = 34.5555


mx = x * meters + x_original_point
my = y * -meters + y_x_original_point

mxy = list(zip(mx, my))

picture_df = gpd.GeoDataFrame(
    {"id": range(0, len(mxy))},
    crs="EPSG:3857",
    geometry=[Point(resu) for resu in mxy]
)

#picture_df['geometry'] = picture_df['geometry'].to_crs(epsg=4326)

picture_df.to_file("route.geojson", driver='GeoJSON', encoding='utf-8')

SERVICE = 'https://router.hereapi.com/v8/routes?apiKey=RUT4mbP2bY7ndeADMB8NZJyKfCPZMobqePrHQc6KgpQ&transportMode=pedestrian&return=polyline'
file = open('route.geojson')
data = geojson.load(file).copy()
file.close()

coords_list = [feature['geometry']['coordinates'] for feature in data['features']]

start_point = coords_list[0]
destination_point = coords_list[len(coords_list)-1]

coords_list.remove(start_point)
coords_list.remove(destination_point)

origin = f"&origin={start_point[1]},{start_point[0]}"
destination = f"&destination={destination_point[1]},{destination_point[0]}&"
waypoints = '&'.join([f'via={coords[1]},{coords[0]}' for coords in coords_list])

routes = requests.get(SERVICE + origin + destination + waypoints)
def decode(section):
    line = flexpolyline.decode(section['polyline'])
    line = [(coord[1], coord[2]) for coord in line]
    return LineString(line)

geometry = [decode(section) for section in routes['routes'][0]['sections']]

route_df = gpd.GeoDataFrame(geometry=geometry)

route_df.to_file("route.geojson", driver='GeoJSON', encoding='utf-8')

m = folium.Map(
    location=[start_point, destination_point],
    zoom_start=15,
    tiles='https://1.base.maps.ls.hereapi.com/maptile/2.1/maptile/newest/reduced.day/{z}/{x}/{y}/256/png?lg=RU&apiKey={RUT4mbP2bY7ndeADMB8NZJyKfCPZMobqePrHQc6KgpQ}',
    attr='HERE'
)

#webbrowser.open('https://vk.com', new=1)


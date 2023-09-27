#!/usr/bin/python
# GoogleMapDownloader.py
# Created by Tigran Makyan
#
# A script which when given a longitude, latitude and zoom level downloads a
# high resolution google map
# Find the associated blog post at: http://blog.eskriett.com/2013/07/19/downloading-google-maps/

import urllib.request
from PIL import Image
import os
import math
from joblib import Parallel, delayed
from tqdm import tqdm
import itertools
from pathlib import Path
import requests
import numpy as np
import argparse 
import json

class GoogleMapsLayers:
  ROADMAP = "v"
  TERRAIN = "p"
  ALTERED_ROADMAP = "r"
  SATELLITE = "s"
  TERRAIN_ONLY = "t"
  HYBRID = "y"


def getXY(zoom, lat, lng, tile_size=256):
    """
            Generates an X,Y tile coordinate based on the latitude, longitude
            and zoom level
            Returns:    An X,Y tile coordinate
    """

    # Use a left shift to get the power of 2
    # i.e. a zoom level of 2 will have 2^2 = 4 tiles
    numTiles = 1 << zoom
    
    # Find the x_point given the longitude
    point_x = (tile_size / 2 + lng * tile_size / 360.0) * numTiles // tile_size

    # Convert the latitude to radians and take the sine
    sin_y = math.sin(lat * (math.pi / 180.0))

    # Calulate the y coorindate
    point_y = ((tile_size / 2) + 0.5 * math.log((1 + sin_y) / (1 - sin_y)) * -(
    tile_size / (2 * math.pi))) * numTiles // tile_size
    print(point_x, point_y)
    return int(point_x), int(point_y)

def get_corner_latlng(zoom, lat, lng, xy = None):
    if xy is not None:
        x, y = xy
    else:
        x,y = getXY(zoom, lat, lng)
    n = 1 << zoom 
    lon_deg = (x/ n) * 360.0 - 180.0
    lat_rad = np.arctan(np.sinh(np.pi * (1 - 2 * y / n)))
    lat_deg = lat_rad * 180.0 / np.pi
    print(lat_deg)
    print(lon_deg)
    return lat_deg, lon_deg

class GoogleMapDownloader:
    """
        A class which generates high resolution google maps images given
        a longitude, latitude and zoom level
    """

    def __init__(self, lat, lng, zoom=12, layer=GoogleMapsLayers.SATELLITE):
        """
            GoogleMapDownloader Constructor
            Args:
                lat:    The latitude of the location required
                lng:    The longitude of the location required
                zoom:   The zoom level of the location required, ranges from 0 - 23
                        defaults to 12
        """
        self._lat = lat
        self._lng = lng
        self._zoom = zoom
        self._layer = layer


    def generateImage(self, **kwargs):
        """
            Generates an image by stitching a number of google map tiles together.
            Args:
                start_x:        The top-left x-tile coordinate
                start_y:        The top-left y-tile coordinate
                tile_width:     The number of tiles wide the image should be -
                                defaults to 5
                tile_height:    The number of tiles high the image should be -
                                defaults to 5
            Returns:
                A high-resolution Goole Map image.
        """

        start_x = kwargs.get('start_x', None)
        start_y = kwargs.get('start_y', None)
        tile_width = kwargs.get('tile_width', 5)
        tile_height = kwargs.get('tile_height', 5)

        # Check that we have x and y tile coordinates
        if start_x == None or start_y == None:
            start_x, start_y = getXY(self._zoom, self._lat, self._lng)
            #print(f'start_x = {start_x}; start_y = {start_y}')

        # Determine the size of the image
        width, height = 256 * tile_width, 256 * tile_height
        imf = Path(kwargs.get('folder', 'gmap'))
        imf.mkdir(exist_ok=True)
        print(imf)
        def download_img(x,y):
            url = f"https://mt0.google.com/vt?lyrs={self._layer}&x={start_x + x}&y={start_y + y}&z={self._zoom}"
            im_path = imf.joinpath(f"{x}-{y}.jpg")
            r = requests.get(url)
            im_path.write_bytes(r.content)

        Parallel(n_jobs=20)(delayed(download_img)(x,y) for x,y in tqdm(itertools.product(range(0, tile_width),range(0, tile_height))))
        # if True:
        #     map_img = Image.new('RGB', (width, height))
        #     for x,y in tqdm(itertools.product(range(0, tile_width),range(0, tile_height))):
        #         current_tile = imf.joinpath(f"{x}-{y}.jpg")
        #         im = Image.open(current_tile)
        #         map_img.paste(im, (x * 256, y * 256))
        #
        #         # os.remove(current_tile)
        #     return map_img
        # return map_img

def join_tiles(in_folder,out_folder,total_x, total_y,extent=None,out_prefix="", debug=False, coords=None, ts=256):
    # total = 10
    # extent = 2
    in_folder = Path(in_folder)
    out_folder = Path(out_folder)
    out_folder.mkdir(exist_ok=True)
    if extent is None:
        extent_x = total_x
        extent_y = total_y

    print(extent_x)
    nums_x = np.arange(total_x).reshape((-1,extent_x))
    nums_y = np.arange(total_y).reshape((-1,extent_y))
    for gx,gy in  itertools.product(nums_x,nums_y):
        map_img = Image.new('RGB', (extent_x*ts, extent_y*ts))
        for (i,x),(j,y) in itertools.product(enumerate(gx),enumerate(gy)):
            current_tile = in_folder.joinpath(f"{x}-{y}.jpg")
            im = Image.open(current_tile)
            map_img.paste(im, (i * ts, j * ts))
            # print((i,x),(j,y))
        if debug:
            map_img.save(out_folder.joinpath(f"{out_prefix}.jpg")) if coords==None else \
            map_img.save(out_folder.joinpath(f"{out_prefix}{coords[0]}-{coords[1]}.jpg"))
    return map_img


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download a map.')
    parser.add_argument('--config', type=str, default=None, help="path to the config file")
    parser.add_argument('--lat', type=float, default=39.618688, help="initial latitude")
    parser.add_argument('--long', type=float, default=45.235564, help="initial long")
    parser.add_argument('--size', type=float, default=5,  help="Size of the map given in km.")
    parser.add_argument('--tile_size_km', type=float, default=1.6,  help="Size of the tile given in km.")
    parser.add_argument('--zoom', type=int, default=12,  help="zoom of the map given in km.")
    parser.add_argument('--path', type=str, default='new_map', help='path where to save the map')
    parser.add_argument('--attach_grid', type=bool, default=False, help='sets coordinate grid to map if specified')
    parser.add_argument('--image_name', type=str, default='image')
    parser.add_argument('--tile_width', type=int, default=10)
    
    args = parser.parse_args()

    os.system(f'mkdir {args.path}')
        
    if args.config is not None:
        pass
    elif args.lat ==None or args.long == None or  args.size == None:
        raise ValueError("Either there is no config file or one of the latitude, longitude or size is not specified")
    ## TODO add config file for map aqnd specify necessary arguments like zoom etc. 
    
    path = args.path 
    map_size_km = args.size#10
    init_lat = args.lat #40.3047861
    init_long = args.long# 44.5608759
    zoom = args.zoom
    tile_size_km = args.tile_size_km
    image_name = args.image_name
    lat_measure = 110.574
    long_measure = 111.320
    tile_width = args.tile_width
    

    lats = [init_lat - tile_size_km * i /lat_measure for i in range(int(np.ceil(map_size_km/tile_size_km))) ]
    
    get_point = lambda lats: [[(lat_i, init_long + tile_size_km *i/(long_measure*np.cos(np.pi * lat_i/180))) \
                    for i in range(int(np.ceil(map_size_km/tile_size_km))) ] for lat_i in lats]
    # print(get_point(lats))
    points = get_point(lats)
    #print(points)
    x1, y1 = getXY(zoom, init_lat, init_long)
    x2, y2 = getXY(zoom, init_lat - tile_size_km  /lat_measure, init_long)
    # tile_width  = (y2 - y1 ) // 2
    # tile_width = 10
    print("tile_width", tile_width)
    #
    if args.attach_grid:
        map_dict = dict()
        map_dict.update({'base_size': 256})
        map_dict.update({'tile_width': tile_width})
        map_dict.update({'tile_size_km': tile_size_km})
        map_dict.update({'map_size_km': map_size_km})
        map_dict.update({'zoom': zoom})
        map_dict.update({'path': path})
        map_dict.update({'tiles': {}})

    for i,j in itertools.product(range(len(lats)), range(len(lats))):
        gmd = GoogleMapDownloader(*points[i][j], zoom=zoom, layer=GoogleMapsLayers.SATELLITE)
        gmd.generateImage(tile_width=tile_width,tile_height=tile_width ,folder="raw_files")
        
        if args.attach_grid:
            map_dict['tiles'].update({f'{i}-{j}': get_corner_latlng(zoom, *points[i][j])})
        join_tiles("raw_files", path, total_x=tile_width, total_y=tile_width, out_prefix=image_name, debug=True )
        os.system('rm -rf raw_files')
    
    # with open(f"{path}.json", "a") as outfile:
    #     json.dump(map_dict, outfile)
    #     json.dump('\n',outfile)

    with open(f'{path}.txt', 'a') as file:
        file.write(str(map_dict))
        file.write('\n')
   

##TODO
# def get_realpoint(image, pixel):
#     lat, lng = some_calculations
#     pass

# def get_pixel(image, (lat, lng)):
#     pixel  = some_calculations(lat, lng)
#     pass

import os
import sys
from pathlib import Path
from google_map_cropping import get_corner_latlng, getXY
import random
import numpy as np

cmd_example = 'python google_map_cropping.py --lat 40.3047861 --long 44.5608759 --size 10 --zoom 19 --attach_grid True'

lat_left_top_first = 40.3047861
lng_left_top_first = 44.5608759
size = 10
zoom_example = 19   # 18, 19, 20, 21

# pairs_path: Path = '/home/user/computer_vision/scripts/map_pairs.txt'
# data_path: Path = '/home/user/computer_vision/scripts/data/'

pairs_path: Path = '/home/user/computer_vision/scripts/map_pairs.txt'
data_path: Path = '/home/user/computer_vision/scripts/data/'

if not os.path.exists(data_path):
    os.mkdir(data_path)

def center_point(lat, lng, zoom, index):

    image_name = f'garnik_{zoom}_' + str(index)
    os.system(f'python google_map_cropping.py --lat {lat} --long {lng}\
        --size 1.6 --zoom {zoom} --attach_grid True --image_name {image_name} --path data --tile_width 8')
    
    image_abs_path = f'/home/user/computer_vision/scripts/data/{image_name}'

    '''
    stex hima voroshum enq stacac nkari nerqevi aj koordinatnery
    '''
    x1, y1 = lat, lng
    pix1, pix2 = getXY(zoom=zoom, lat=lat, lng=lng)
    pix1 += 10
    pix2 += 10
    x2, y2 = get_corner_latlng(zoom=zoom,
                                lat=x1,
                                lng=y1,
                                xy=(pix1, pix2))
    
    
    '''
    hima voroshenq nkri kentroni koordinatnery
    '''
    x_center = (x1 + x2) / 2
    y_center = (y1 + y2) / 2
    

    '''
    sahmanenq hajord nkari skzbnakety random generatori mijocov
    '''
    lat_new = round(random.uniform(x_center, x1), 7)
    lng_new = round(random.uniform(y1, y_center), 7)
    return lat_new, lng_new, image_abs_path



def quadro_images(lat_first, lng_fist, index):
    '''
    patrastvum enq u pahum 4 hat nkar u pairs.txt fileum grum enq iranc relative scalery
    '''
    image2_lat, image2_lng, image1_path = center_point(lat_first, lng_fist, index=index, zoom=18)
    #image 1 is saved in data dir

    image3_lat, image3_lng, image2_path = center_point(image2_lat, image2_lng, index=index, zoom=19)
    #image 2 is saved in data dir

    image4_lat, image4_lng, image3_path = center_point(image3_lat, image3_lng, index=index, zoom=20)
    #image 3 is saved in data dir

    _, _, image4_path = center_point(image4_lat, image4_lng, index=index, zoom=21)
    #image 4 is saved in data dir

    return image1_path, image2_path, image3_path, image4_path



for i, lat in enumerate(np.arange(41.2098335, 38.6271460, -0.0095470)):   # 41.309833
    for j, lng in enumerate(np.arange(42.4859030, 48.4029150, 0.0134038)):   # 42.9550359
        # step = 0.0134038
        # lat, lng = lat_left_top_first, lng_left_top_first + index * step
        img1_path, img2_path, img3_path, img4_path = quadro_images(lat, lng, index=str(i)+str(j))
        
        with open(pairs_path, 'a') as file:
            file.write(f'{img4_path} {img3_path} 0.5 {lat} {lng}')
            file.write('\n')
            file.write(f'{img3_path} {img2_path} 0.5 {lat} {lng}')
            file.write('\n')
            file.write(f'{img2_path} {img1_path} 0.5 {lat} {lng}')
            file.write('\n')
            file.write(f'{img4_path} {img2_path} 0.25 {lat} {lng}')
            file.write('\n')
            file.write(f'{img3_path} {img1_path} 0.25 {lat} {lng}')
            file.write('\n')
            file.write(f'{img4_path} {img1_path} 0.125 {lat} {lng}')
            file.write('\n')


















# for i in range(250000):
#     for zoom_value in range(18, 22):
#         '''
#         skzni hamar amena vat rezolutionov nkarn enq qashum
#         '''
#         image_name = f'garnik_{zoom_value}_{i}'
#         os.system(f'python google_map_cropping.py --lat {lat_left_top_first} --long {lng_left_top_first}\
#             --size 1.6 --zoom {zoom_value} --attach_grid True --image_name {image_name} --path data')
        
#         image_abs_path = f'/home/user/computer_vision/scripts/data/{image_name}'

#         '''
#         stex hima voroshum enq stacac nkari nerqevi aj koordinatnery
#         '''
#         x1, y1 = lat_left_top_first, lng_left_top_first
#         pix1, pix2 = getXY(zoom=zoom_value, lat=lat_left_top_first, lng=lng_left_top_first)
#         pix1 += 10
#         pix2 += 10
#         x2, y2 = get_corner_latlng(zoom=zoom_value,
#                                     lat=x1,
#                                     lng=y1,
#                                     xy=(pix1, pix2))
        
#         '''
#         hima voroshenq nkri kentroni koordinatnery
#         '''
#         x_center = (x1 + x2) / 2
#         y_center = (y1 + y2) / 2

    
#         '''
#         sahmanenq hajord nkari skzbnakety random generatori mijocov
#         '''
#         lat_new = round(random.uniform(x_center, x1), 7)
#         lng_new = round(random.uniform(y1, y_center), 7)

#         '''
#         stex arden grecinq 4 hat nkar, inchy petqq cvhi irakanum
#         '''



































"""east.py

Utility script to create the bounding boxes of the EAST view in the example.

"""

from utils import print_annotation


slate_box_coordinates = [

    [[180, 110], [460, 110], [180, 170], [460, 170]],    # DATE
    [[660, 110], [1250, 110], [660, 170], [1250, 170]],

    [[180, 320], [460, 320], [180, 380], [460, 380]],    # TITLE
    [[660, 320], [1210, 320], [660, 380], [1210, 380]],

    [[180, 520], [460, 520], [180, 580], [460, 580]],    # HOST
    [[660, 520], [1200, 520], [660, 580], [1200, 580]],

    [[180, 750], [470, 750], [180, 810], [470, 810]],    # PROP
    [[660, 750], [1180, 750], [660, 810], [1180, 810]]

]

fido_box_coordinates = [[150, 810], [1120, 810], [150, 870], [1120, 870]]


    
    

if __name__ == '__main__':

    count = 0
    for time_offset in 3000, 4000, 5000:
        for coordinates in slate_box_coordinates:
            count += 1
            box_id = 'bb%s' % count
            print_annotation(
                "http://mmif.clams.ai/0.2.0/vocabulary/BoundingBox",
                [('id', box_id),
                 ('timePoint', time_offset),
                 ('coordinates', coordinates),
                 ('boxType', 'text')])

    count += 1
    box_id = 'bb%s' % count
    print_annotation(
        "http://mmif.clams.ai/0.2.0/vocabulary/BoundingBox",
        [('id', box_id),
         ('timePoint', 21000),
         ('coordinates', fido_box_coordinates),
         ('boxType', 'text')])

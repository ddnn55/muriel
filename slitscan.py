#!/usr/bin/env python

import argparse, sys, os, math
from PIL import Image

class Slitscan():

    def __init__(self, image_paths, output_dir, step):
        self.image_paths = image_paths
        self.output_dir = output_dir
        self.step = step

        self.height = None
        self.tile_width = None
        self.slit_index = 0
        self.tile_image = None
        self.extract_column = None
        self.slit_width = step
        self.last_index_saved = -1
    
    def save_next_tile_image(self):
        self.tile_index = self.last_index_saved + 1
        output_path = os.path.join(
            self.output_dir,
            'tile-%05d.png' % self.tile_index
        )

        self.tile_image.save(output_path)
        print('Saved ' + output_path)
        self.last_index_saved = self.last_index_saved + 1

    def copy_next_slit_to_mural(self, image):
        mural_column = self.slit_index * self.slit_width
        tile_column = mural_column % self.tile_width
        print(str(tile_column) + ' / ' + str(self.tile_width))

        if tile_column == 0:
            # save current tile if exists
            if self.slit_index != 0:
                self.save_next_tile_image()

            # create new tile
            self.tile_image = Image.new('RGB', (self.tile_width, self.height), (0, 0, 0))
        
        band = image.crop((
            self.extract_column,
            0,
            self.extract_column + self.slit_width,
            self.height
        ))
        self.tile_image.paste(band, (tile_column, 0))
        # print('pasting to ', {tile_column})

        self.slit_index = self.slit_index + 1


    def run(self):
        for image_path in image_paths:
            image = Image.open(image_path)
            if self.height == None:
                    self.height = image.height
                    self.tile_width = int(math.ceil(self.height / self.slit_width) * self.slit_width)
                    # tile_width = 50
                    # self.extract_column = Math.round(metadata.width / 2)
                    self.extract_column = math.floor(image.width / 2)
                    print('height = ' + str(self.height))

            self.copy_next_slit_to_mural(image)

        self.save_next_tile_image()

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    
    parser.add_argument('--input-images-path', help='Path to directory of video frame images to slitscan')
    parser.add_argument('--output', help='Directory to which slitscan tiles will be written')
    parser.add_argument('--step', help='Pixel width of the scan. Try 1 or slightly more.')

    args=parser.parse_args()

    step = int(args.step)

    # print args

    image_paths = []
    for root, directories, filenames in os.walk(args.input_images_path):
        for filename in filenames: 
            if filename[0] != '.':
                image_paths.append(os.path.join(root, filename))

    image_paths.sort()
    # print "\n".join(image_paths)

    scanner = Slitscan(image_paths, args.output, step)
    scanner.run()

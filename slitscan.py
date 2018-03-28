#!/usr/bin/env python

import argparse, sys, os, math, av
from PIL import Image

import base64
import cStringIO

# from http://code.activestate.com/recipes/82465-a-friendly-mkdir/
def mkdirp(newdir):
    """works the way a good mkdir should :)
        - already exists, silently complete
        - regular file in the way, raise an exception
        - parent directory(ies) does not exist, make them as well
    """
    if os.path.isdir(newdir):
        pass
    elif os.path.isfile(newdir):
        raise OSError("a file with the same name as the desired " \
                      "dir, '%s', already exists." % newdir)
    else:
        head, tail = os.path.split(newdir)
        if head and not os.path.isdir(head):
            _mkdir(head)
        #print "_mkdir %s" % repr(newdir)
        if tail:
            os.mkdir(newdir)

class Slitscan():

    def __init__(self, images, output_dir, step, rotation, direction, stdout):
        self.images = images
        self.output_dir = output_dir
        self.step = step
        self.rotation = rotation
        self.direction = direction
        self.stdout = stdout

        self.height = None
        self.tile_width = None
        self.slit_index = 0
        self.tile_image = None
        self.extract_column = None
        self.slit_width = step
        self.last_index_saved = -1

        self.current_tile_paste_count = 0

        mkdirp(self.output_dir)
    
    def save_next_tile_image(self):
        self.tile_index = self.last_index_saved + 1
        output_path = os.path.join(
            self.output_dir,
            'tile-%05d.png' % self.tile_index
        )

        if self.current_tile_paste_count * self.slit_width != self.tile_width:
            self.tile_image = self.tile_image.crop(box=(0, 0, self.current_tile_paste_count * self.slit_width, self.height))

        if self.direction == "rtl":
            self.tile_image = self.tile_image.transpose(Image.FLIP_LEFT_RIGHT)

        self.tile_image.save(output_path)
        print('Saved ' + output_path)
        self.last_index_saved = self.last_index_saved + 1

    def copy_next_slit_to_mural(self, image):
        mural_column = self.slit_index * self.slit_width
        tile_column = mural_column % self.tile_width
        print(str(tile_column) + ' / ' + str(self.tile_width))

        if tile_column == 0 and not self.stdout:
            # save current tile if exists
            if self.slit_index != 0:
                self.save_next_tile_image()

            # create new tile
            self.tile_image = Image.new('RGB', (self.tile_width, self.height), (0, 0, 0))
            self.current_tile_paste_count = 0
        
        band = image.crop((
            self.extract_column,
            0,
            self.extract_column + self.slit_width,
            self.height
        ))
        if self.direction == "rtl":
            band = band.transpose(Image.FLIP_LEFT_RIGHT)
        if self.stdout:
            buffer = cStringIO.StringIO()
            band.save(buffer, format="PNG")
            band_str = base64.b64encode(buffer.getvalue())
            print band_str
        else:
            self.tile_image.paste(band, (tile_column, 0))
            self.current_tile_paste_count = self.current_tile_paste_count + 1
            # print('pasting to ', {tile_column})

        self.slit_index = self.slit_index + 1


    def run(self):
        for image in self.images:
            # print str(image.width) + ' x ' + str(image.height)
            if self.rotation != 0:
                image = image.rotate(self.rotation, expand=True)
                # print "rotated to"
                # print str(image.width) + ' x ' + str(image.height)
            # image = Image.open(image_path)
            if self.height == None:
                    self.height = image.height
                    self.tile_width = int(math.ceil(self.height / self.slit_width) * self.slit_width)
                    # tile_width = 50
                    # self.extract_column = Math.round(metadata.width / 2)
                    self.extract_column = math.floor(image.width / 2)
                    print('height = ' + str(self.height))

            self.copy_next_slit_to_mural(image)

        self.save_next_tile_image()

def frames(video_path):
    container = av.open(video_path)

    for frame in container.decode(video=0):
        yield frame.to_image()

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    
    parser.add_argument('--input', help='Video to slitscan')
    parser.add_argument('--output', help='Directory to which slitscan tiles will be written')
    parser.add_argument('--step', help='Pixel width of the scan. Try 1 or slightly more.')
    parser.add_argument('--rotate', help='Rotate image by a multiple of 90. Handy because we may not recognize orientation metadata.', default=0)
    parser.add_argument('--direction', help='Either "ltr" or "rtl", i.e. left to right, or right to left. Default is "ltr".', default="ltr")
    parser.add_argument('--stdout', nargs='?', const=True, default=False, help='Instead of saving square tiles to --output, print one base64 PNG band per line to stdout.')

    args=parser.parse_args()

    print args

    step = int(args.step)

    # print args

    # image_paths = []
    # for root, directories, filenames in os.walk(args.input_images_path):
    #     for filename in filenames: 
    #         if filename[0] != '.':
    #             image_paths.append(os.path.join(root, filename))

    # image_paths.sort()
    # print "\n".join(image_paths)

    video_frames = frames(args.input)

    # scanner = Slitscan(image_paths, args.output, step)
    scanner = Slitscan(video_frames, args.output, step, int(args.rotate), args.direction, args.stdout)
    scanner.run()

#!/usr/bin/env python3

from wand.image import Image
from wand.color import Color
from wand.drawing import Drawing
from wand.display import display
from math import sqrt, ceil
from sys import stdout

import argparse

parser = argparse.ArgumentParser(description='Enlarge an image to allow for circular cropping without losing any colored pixels')
parser.add_argument('inputfile', type=argparse.FileType('r'), help="Path of the input image to be read and processed.")
parser.add_argument('outputfile', type=argparse.FileType('w'), help="Path of the output file where the processed image will be saved. Will be overwritten if it exists.")
parser.add_argument('-b', '--bgcolor', type=str, default='white', help="Background color that will be applied to all transparent areas in the image. Defaults to 'white', can be set to 'transparent' if desired. This string will be passed directly to ImageMagick, so any color specifier understood by ImageMagick can be used.")
parser.add_argument('-s', '--size', type=float, default='0', help="Change the computed optimal image size by <x> percent, i.e. add more or less than the optimal border size. Accepts positive and negative numbers, including ones with decimal places: +10, -5.432, etc.")
parser.add_argument('-t', '--transparent-color', type=str, default=None, help="Replace the given color (in any notation understood by ImageMagick) with transparency. By default, no such replacement is applied.")
parser.add_argument('-d', '--output-size', type=str, default=None, help="Resizes the output image to the given size (in ImageMagick notation, e.g. 512x512).")

args = parser.parse_args()

with Image(filename=args.inputfile.name) as img:
    print('Loaded %s' % args.inputfile.name)

    if args.transparent_color:
        print('Replacing \'%s\' with transparency' % args.transparent_color)
        img.alpha_channel = 'activate'
        with Color(args.transparent_color) as c:
            img.transparent_color(color=c, alpha=0.0, fuzz=10)

    img.trim()

    max_dim = max(img.size)
    center = max_dim/2

    r = 0
    while r < center:
        stdout.write('\rProgress >= %.0f%%' % (100*r/center))
        tmp_img = img.clone()
        with Drawing() as draw:
            draw.stroke_antialias = False
            draw.circle((center, center), (0, r))
            draw(tmp_img)
        color_count = len(tmp_img.histogram)
        #print(r, color_count)
        if color_count > 2:
            max_r = r - 1
            break
        r += 1
    stdout.write('\r')

    encompassing_radius = sqrt(center**2 + (center - max_r)**2)
    print('Radius of smallest circle encompassing all non-transparent pixels: %d' % ceil(encompassing_radius))

    size_offset = 1 + (args.size/100)
    if size_offset != 1:
        print('%s optimal size by %d%%' % ('Increasing' if size_offset > 1 else 'Reducing', abs(args.size)))
        encompassing_radius *= size_offset # relax the border a little

    width = 2*ceil(encompassing_radius)
    print('Putting the image in the center of a %dx%d px canvas to allow for circular cropping without losing pixels' % (width, width))
    print('New background color: %s' % args.bgcolor)

    frame_vert = ceil((width - img.height)/2)
    frame_horz = ceil((width - img.width)/2)
    img.frame(width=frame_horz, height=frame_vert, matte=Color('none'))

    # reset image offset
    img.page_x = 0
    img.page_y = 0

    img.background_color = Color(args.bgcolor)
    img.alpha_channel = 'remove'

    if args.output_size:
        print('Resizing image to %s' % args.output_size)
        img.transform(resize=args.output_size)

    img.save(filename=args.outputfile.name)

    print('Processed image written to %s' % args.outputfile.name)

# vim: set ft=python ts=8 sw=4 tw=0 et :

#!/usr/bin/env python3

from wand.image import Image
from wand.color import Color
from wand.drawing import Drawing
from wand.display import display
from math import sqrt, ceil

def process_image(img, transparent_color=None, background_color='white', size_offset_percent=0, output_size=None, verbose=False):
    if verbose:
        from sys import stdout

    if transparent_color:
        if verbose:
            print('Replacing \'%s\' with transparency' % transparent_color)
        img.alpha_channel = 'activate'
        with Color(transparent_color) as c:
            img.transparent_color(color=c, alpha=0.0, fuzz=10)

    img.trim()

    max_dim = max(img.size)
    center = max_dim/2

    r = 0
    while r < center:
        if verbose:
            stdout.write('\rProgress >= %.0f%%' % (100*r/center))
        tmp_img = img.clone()
        with Drawing() as draw:
            draw.stroke_antialias = False
            draw.circle((center, center), (0, r))
            draw(tmp_img)
        color_count = len(tmp_img.histogram)
        if color_count > 2:
            max_r = r - 1
            break
        r += 1
    if verbose:
        stdout.write('\r')

    encompassing_radius = sqrt(center**2 + (center - max_r)**2)
    if verbose:
        print('Radius of smallest circle encompassing all non-transparent pixels: %d' % ceil(encompassing_radius))

    size_offset = 1 + (size_offset_percent/100)
    if size_offset != 1:
        if verbose:
            print('%s optimal size by %d%%' % ('Increasing' if size_offset > 1 else 'Reducing', abs(size_offset_percent)))
        encompassing_radius *= size_offset # relax the border a little

    width = 2*ceil(encompassing_radius)
    if verbose:
        print('Putting the image in the center of a %dx%d px canvas to allow for circular cropping without losing pixels' % (width, width))
        print('New background color: %s' % background_color)

    frame_vert = ceil((width - img.height)/2)
    frame_horz = ceil((width - img.width)/2)
    img.frame(width=frame_horz, height=frame_vert, matte=Color('none'))

    # reset image offset
    img.page_x = 0
    img.page_y = 0

    img.background_color = Color(background_color)
    img.alpha_channel = 'remove'

    if output_size:
        if verbose:
            print('Resizing image to %s' % output_size)
        img.transform(resize=output_size)

    return img

def main():
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
        new_img = process_image(img, transparent_color=args.transparent_color, background_color=args.bgcolor, size_offset_percent=args.size, output_size=args.output_size, verbose=True)
        new_img.save(filename=args.outputfile.name)
        print('Processed image written to %s' % args.outputfile.name)

if __name__ == "__main__":
        main()

# vim: set ft=python ts=8 sw=4 tw=0 et :

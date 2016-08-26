#!/usr/bin/env python3

from wand.image import Image
from wand.color import Color
from wand.drawing import Drawing
from wand.display import display
from math import sqrt, ceil
from sys import stderr

with Image(filename='/tmp/beermugs.png') as img:
    img.trim(color=Color('none'))
    max_dim = max(img.size)
    center = max_dim/2
    r = 0
    while r < center:
        stderr.write('\rProgress >= %.0f%%' % (100*r/center))
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
    stderr.write('\r')
    encompassing_radius = sqrt(center**2 + (center - max_r)**2)
    encompassing_radius *= 1.05 # relax the border a little
    print('Radius of smallest circle encompassing all non-transparent pixels: %d' % ceil(encompassing_radius))
    width = 2*ceil(encompassing_radius)
    print('Put the image in the center of a %dx%d px canvas to allow for circular cropping without losing pixels.' % (width, width))
    frame_vert = ceil((width - img.height)/2)
    frame_horz = ceil((width - img.width)/2)
    img.frame(width=frame_vert, height=frame_horz, matte=Color('none'))

    # reset image offset
    img.page_x = 0
    img.page_y = 0

    img.background_color = Color('forestgreen')
    img.alpha_channel = 'remove'

    img.save(filename='/tmp/pythoned.png')

# vim: set ft=python ts=8 sw=4 tw=0 et :

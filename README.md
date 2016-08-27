moja -- eMOJi Avatar generator
==============================

Enlarges the canvas of an image with a transparent background, such that the
resulting image can be cropped to a circle without losing any coloured pixels.

Main use case: Transforming rendered emojis into avatars that can be used on
any of the modern messenger services that apply a circular mask when displaying
user avatars.

Requirements
------------

* Python 3
* `pip3 install Wand`

Usage
-----

    $ ./moja-cmd.py3 -h
    usage: moja-cmd.py3 [-h] [-b BGCOLOR] [-s SIZE] inputfile outputfile

    Enlarge an image to allow for circular cropping without losing any colored
    pixels

    positional arguments:
      inputfile             Path of the input image to be read and processed.
      outputfile            Path of the output file where the processed image will
                            be saved. Will be overwritten if it exists.

    optional arguments:
      -h, --help            show this help message and exit
      -b BGCOLOR, --bgcolor BGCOLOR
                            Background color that will be applied to all
                            transparent areas in the image. Defaults to 'white',
                            can be set to 'transparent' if desired. This string
                            will be passed directly to ImageMagick, so any color
                            specifier understood by ImageMagick can be used.
      -s SIZE, --size SIZE  Change the computed optimal image size by <x> percent,
                            i.e. add more or less than the optimal border size.
                            Accepts positive and negative numbers, including ones
                            with decimal places: +10, -5.432, etc.

Todo
----

* Use binary search instead of linear search to determine optimal image size
  (will *vastly* improve runtime performance)


Manual process (bash + ImageMagick)
-----------------------------------

* Download image
* Add transparent border
  convert -bordercolor none -border 50x50 beermugs.png beermugs-bordered.png
* Trim image to smallest size containing all non-transparent pixels
  convert -trim +repage beermugs-bordered.png beermugs-trimmed.png
* Get size of trimmed image
  identify beermugs-trimmed.png
  beermugs-trimmed.png PNG 481x481 481x481+0+0 8-bit DirectClass 16.2KB 0.000u 0:00.000
* Get maximum dimension (width or height), store in $dim
* Draw progressively smaller black circles onto the image, until the circle no longer covers all non-transparent pixels
  center=$((dim/2)); r=0; while test $(convert -fill black -stroke black +antialias -draw "circle $center,$center $r,0" beermugs-trimmed.png - | identify -format %k -) -lt 3; do r=$((r+1)); echo $r; done; min_r=$((r-1))
* The radius of the smallest circle enclosing all non-transparent pixels is now sqrt(center^2 + (center - min_r)^2)
* Optionally: Increase the computed minimum radius by 5% to make the image look less squished.
* Center the image on a square canvas of that size
  convert -gravity center -background white -extent 592x592 beermugs-trimmed.png beermugs-circle-large.png

__author__ = 'Caleb Madrigal'
__date__ = '2025-05-15'

import os
import sys
import time
import math
import colorsys
from PIL import Image

# ###### View stuff ###### #

scale_factor = 1
img_size = (int(3000*scale_factor), int(2000*scale_factor))
CENTER = (0, 0)
ZOOM = 200
print(f'Center: {CENTER}')


def pixel_to_point_x(x_pixel, zoom=1):
    return (x_pixel - img_size[0]//2) / zoom

def pixel_to_point_y(y_pixel, zoom=1):
    return (img_size[1]//2 - y_pixel) / zoom

def pixel_to_point(x_pixel=None, y_pixel=None, zoom=1):
    if (x_pixel is not None) and (y_pixel is not None):
        return (pixel_to_point_x(x_pixel, zoom=zoom), pixel_to_point_y(y_pixel, zoom=zoom))
    if x_pixel is not None:
        return pixel_to_point_x(x_pixel, zoom=zoom)
    if y_pixel is not None:
        return pixel_to_point_y(y_pixel, zoom=zoom)

def get_values_for_pixels(func, zoom=1):
    upper_left = pixel_to_point(0, 0, zoom=zoom)
    bottom_right = pixel_to_point(img_size[0], img_size[1], zoom=zoom)
    print('Zoom={}, Xmin={}, Xmax={}, Ymin={}, Ymax={}'
          .format(zoom, upper_left[0] + CENTER[0], bottom_right[0] + CENTER[0], upper_left[1] + CENTER[1], bottom_right[1] + CENTER[1]))
    pixel_to_value = {}
    for x_pixel in range(img_size[0]):
        for y_pixel in range(img_size[1]):
            (x, y) = pixel_to_point(x_pixel, y_pixel, zoom=zoom)

            # Adjust for CENTER
            x = x + CENTER[0]
            y = y + CENTER[1]

            val = func(x, y)
            pixel_to_value[(x_pixel, y_pixel)] = val
    return pixel_to_value

def make_linear_mapper(in_range, out_range, int_out=False):
    in_delta = in_range[1] - in_range[0]
    out_delta = out_range[1] - out_range[0]
    # y = mx + b (m = slope, b = y-intersect)
    # Note: This can throw a division by zero error. I could catch it, but I dont wanna.
    m = (out_delta / in_delta)
    # To find b: b = y - mx
    # Just plug in first item of each range
    b = out_range[0] - m * in_range[0]
  
    if int_out:
        def _linear_mapper(val):
            return int(m * val + b)
    else:
        def _linear_mapper(val):
            return m * val + b
  
    return _linear_mapper


# ###### Math ###### #

def equation(x, y, fuzzy_level=1/2):
    amplitude = 1
    frequency = 1
    phase = 0

    equation_left = y
    equation_right = amplitude * math.sin(2 * math.pi * frequency * x + phase)

    return abs(equation_left - equation_right)**(fuzzy_level)


# ###### Paint the image ###### #

def build_frame(frame_num, rotate=None, show_image=False):
    start_time = time.time()
    im = Image.new('RGB', img_size)
    pixel_values = get_values_for_pixels(lambda x, y: equation(x, y), zoom=ZOOM*scale_factor)
    min_val = min(pixel_values.values())
    max_val = max(pixel_values.values())
    print('min: {}, max: {}'.format(min_val, max_val))

    error_to_color_map = make_linear_mapper([min_val, max_val], [255, 0], int_out=True)

    def magenta_color_map(value):
        color_val = error_to_color_map(value)
        # Magenta = Red + Blue
        return (color_val, 0, color_val)

    for x_pixel in range(img_size[0]):
        for y_pixel in range(img_size[1]):
            value = pixel_values[(x_pixel, y_pixel)]
            color = magenta_color_map(value)
            im.putpixel((x_pixel, y_pixel), color)

    print('Render seconds elapsed: {}'.format(time.time() - start_time))

    # Save image
    img_name = sys.argv[0].split('.')[0]  # sinc_thing.py -> sinc_thing
    if not os.path.exists(img_name):
        os.mkdir(img_name)
    file_name = '{}_{}_{}x{}.png'.format(img_name, frame_num, img_size[0], img_size[1])
    img_path = '{}/{}'.format(img_name, file_name)  # img_name is both directory name and beginning of filename

    if rotate is not None:
        im=im.rotate(rotate, expand=True)

    im.save(img_path)
    if show_image:
        im.show()
    print('Saved to {}'.format(img_path))

if __name__ == '__main__':
    build_frame(0, rotate=0, show_image=True)


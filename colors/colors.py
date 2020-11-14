#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014-2020 Richard Hull and contributors
# See LICENSE.rst for details.
# PYTHON_ARGCOMPLETE_OK

"""
Color rendering demo.
"""

import math
import time
import random
from pathlib import Path
from demo_opts import get_device
from luma.core.render import canvas
from PIL import Image


def main():
    img_path = str(Path(__file__).resolve().parent.joinpath('images', 'sun.jpg'))
    balloon = Image.open(img_path) \
        .transform(device.size, Image.AFFINE, (1, 0, 0, 0, 1, 0), Image.BILINEAR) \
        .convert(device.mode)

    img_path = str(Path(__file__).resolve().parent.joinpath('images', 'greyline.jpg'))
    greyline = Image.open(img_path) \
        .transform(device.size, Image.AFFINE, (1, 0, 0, 0, 1, 0), Image.BILINEAR) \
        .convert(device.mode)

    while True:
        # Image display
        device.display(balloon)
        time.sleep(10)
        device.display(greyline)
        time.sleep(60)

        # Cycle through some primary colours
        data = [line.strip() for line in open('rgb.dat')]
        for color in data:
            with canvas(device, dither=True) as draw:
                draw.rectangle(device.bounding_box, fill=color)
                size = draw.textsize(color)
                left = (device.width - size[0]) // 2
                top = (device.height - size[1]) // 2
                right = left + size[0]
                bottom = top + size[1]
                draw.rectangle((left - 1, top, right, bottom), fill="black")
                draw.text((left, top), text=color, fill="white")

            time.sleep(0.1)

        # Rainbow Gray
        w = 4
        with canvas(device, dither=True) as draw:
            for i in range(device.width // w):
                r = i
                g = i
                b = i
                rgb = (r << 16) | (g << 8) | b
                draw.rectangle((i * w, 0, (i + 1) * w, device.height), fill=rgb)

            size = draw.textsize("rainbow")
            left = (device.width - size[0]) // 2
            top = (device.height - size[1]) // 2
            right = left + size[0]
            bottom = top + size[1]
            draw.rectangle((left - 1, top, right, bottom), fill="black")
            draw.text((left, top), text="rainbow", fill="white")

        time.sleep(5)

        # Rainbow
        w = 4
        with canvas(device, dither=True) as draw:
            for i in range(device.width // w):
                r = int(math.sin(0.3 * i + 0) * 127) + 128
                g = int(math.sin(0.3 * i + 2) * 127) + 128
                b = int(math.sin(0.3 * i + 4) * 127) + 128
                rgb = (r << 16) | (g << 8) | b
                draw.rectangle((i * w, 0, (i + 1) * w, device.height), fill=rgb)

            size = draw.textsize("rainbow")
            left = (device.width - size[0]) // 2
            top = (device.height - size[1]) // 2
            right = left + size[0]
            bottom = top + size[1]
            draw.rectangle((left - 1, top, right, bottom), fill="black")
            draw.text((left, top), text="rainbow", fill="white")

        time.sleep(5)

        # Gradient
        with canvas(device, dither=True) as draw:
            for y in range(device.height):
                for x in range(device.width):
                    r = int(min(x / (device.width / 256), 255))
                    g = int(min(y / (device.height / 256), 255))
                    b = 0
                    draw.point((x, y), fill=(r, g, b))

            size = draw.textsize("gradient")
            left = (device.width - size[0]) // 2
            top = (device.height - size[1]) // 2
            right = left + size[0]
            bottom = top + size[1]
            draw.rectangle((left - 1, top, right, bottom), fill="black")
            draw.text((left, top), text="gradient", fill="white")

        time.sleep(5)

        # Random blocks
        w = device.width // 12
        h = device.height // 8
        for _ in range(40):
            with canvas(device, dither=True) as draw:
                for x in range(12):
                    for y in range(8):
                        color = random.randint(0, 2 ** 24)
                        left = x * w
                        right = (x + 1) * w
                        top = y * h
                        bottom = (y + 1) * h
                        draw.rectangle((left, top, right - 2, bottom - 2), fill=color)

                time.sleep(0.25)


if __name__ == "__main__":
    try:
        device = get_device()
        main()
    except KeyboardInterrupt:
        pass                   
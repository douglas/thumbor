#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license: 
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from tornado.options import options

class BaseEngine(object):

    def __init__(self):
        self.image = None
        self.extension = None

    def load(self, buffer, extension):
        self.extension = extension
        self.image = self.create_image(buffer)

    @property
    def size(self):
        return self.image.size

    def normalize(self):
        width, height = self.size
        if width > options.MAX_WIDTH or height > options.MAX_HEIGHT:
            width_diff = width - options.MAX_WIDTH
            height_diff = height - options.MAX_HEIGHT
            if options.MAX_WIDTH and width_diff > height_diff:
                height = self.get_proportional_height(options.MAX_WIDTH)
                self.resize(options.MAX_WIDTH, height)
            elif options.MAX_HEIGHT and height_diff > width_diff:
                width = self.get_proportional_width(options.MAX_HEIGHT)
                self.resize(width, options.MAX_HEIGHT)

    def get_proportional_width(self, new_height):
        width, height = self.size
        return round(float(new_height) * width / height, 0)

    def get_proportional_height(self, new_width):
        width, height = self.size
        return round(float(new_width) * height / width, 0)

    def create_image(self):
        raise NotImplementedError()

    def crop(self):
        raise NotImplementedError()

    def resize(self):
        raise NotImplementedError()

    def flip_horizontally(self):
        raise NotImplementedError()
    
    def flip_vertically(self):
        raise NotImplementedError()

    def read(self):
        raise NotImplementedError()

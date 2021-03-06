#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import json

from tornado.options import options

from thumbor.engines import BaseEngine

class JSONEngine(BaseEngine):

    def __init__(self, engine, path):
        super(JSONEngine, self).__init__()
        self.engine = engine
        self.width, self.height = self.engine.size
        self.path = path
        self.operations = []
        self.refresh_image()

    def refresh_image(self):
        self.image = self.engine.image

    @property
    def size(self):
        return self.engine.size

    def resize(self, width, height):
        self.operations.append({
            "type": "resize",
            "width": width,
            "height": height
        })
        self.engine.resize(width, height)
        self.refresh_image()

    def crop(self, left, top, right, bottom):
        self.operations.append({
            "type": "crop",
            "left": left,
            "top": top,
            "right": right,
            "bottom": bottom
        })
        self.engine.crop(left, top, right, bottom)
        self.refresh_image()

    def flip_vertically(self):
        self.operations.append({ "type": "flip_vertically" })

    def flip_horizontally(self):
        self.operations.append({ "type": "flip_horizontally" })

    def get_target_dimensions(self):
        width = self.width
        height = self.height

        for operation in self.operations:
            if operation['type'] == 'crop':
                width = operation['right'] - operation['left']
                height= operation['bottom'] - operation['top']

            if operation['type'] == 'resize':
                width = operation['width']
                height = operation['height']

        return (width, height)

    def read(self, extension):
        target_width, target_height= self.get_target_dimensions()

        thumbor_json = json.dumps({
            "thumbor": {
                "source": {
                    "url": self.path,
                    "width": self.width,
                    "height": self.height,
                },
                "operations": self.operations,
                "target": {
                    "width": target_width,
                    "height": target_height
                }
            }
        })

        if options.META_CALLBACK_NAME:
            return "%s(%s);" % (options.META_CALLBACK_NAME, thumbor_json)

        return thumbor_json


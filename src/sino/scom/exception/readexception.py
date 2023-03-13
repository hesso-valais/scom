#!/usr/bin/env python
# -*- coding: utf-8 -*-

class ReadException(Exception):

    def __init__(self, message):
        super(ReadException, self).__init__(message)

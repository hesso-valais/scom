#!/usr/bin/env python
# -*- coding: utf-8 -*-

class WriteException(Exception):

    def __init__(self, message):
        super(WriteException, self).__init__(message)

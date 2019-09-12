# -*- coding: utf-8 -*-


class ResponseFrameException(Exception):
    def __init__(self, message):
        super(ResponseFrameException, self).__init__(message)

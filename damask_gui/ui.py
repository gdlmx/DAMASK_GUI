# -*- coding: utf-8
progname = "DAMASK GUI"
progversion = "1.0"
__copyright__ = "Copyright (C) 2015 Mingxuan Lin"

__license__   = """
DAMASK_GUI License Agreement (MIT License)
------------------------------------------

Copyright (c) 2015 Mingxuan Lin
Copyright (c) 2009-2013 Pierre Raybaut

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
"""

def is_in_jupyter():
    import sys
    return any( m  in sys.modules for m in ['IPython.core', 'jupyter_client.jupyter_core'] )

try:
    if is_in_jupyter():
        from ._ipy_ui import * # UIFilter, ApplicationWindow
    else:
        from ._qt4_ui import * # UIFilter, ApplicationWindow
except ImportError:
    from .Filter import FilterBase
    class ApplicationWindow(object):
        def __init__(self, filters=[]):
            print( 'Main window fails to start because Qt4 cannot be found.' )

    class UIFilter(FilterBase):
        name = 'Dummy UI Filter'
        DEBUG=None
        options_def =  ((None,'str', 'NULL'),)  #[(Key, Type, defaultVal)]
        options = None

        @property   # obsoleted
        def ui_options(self):
            return [ ( key,  d_val) for key, typestr, d_val in self.options_def]

        @ui_options.setter # obsoleted
        def ui_options(self, value):
            pass

        def update_form(self, valueDict): # obsoleted
            pass

        def printmsg(self, msg, pauseTime=1000):
            print(msg)

        def set_options_def(self): # obsoleted
            pass

        def set_optparser(self, p):
            pass

        def __getitem__(self, k):
            return None

        def __setitem__(self, k, v):
            pass


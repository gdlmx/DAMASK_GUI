#!/usr/bin/env python
from __future__ import unicode_literals

from .formlayout import *
from .Filter import *
import sys, os, random,pdb
from PyQt4 import QtGui, QtCore

from numpy import arange, sin, pi
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import  matplotlib.tight_layout 

__copyright__ = "Copyright (C) 2015 Mingxuan Lin \n"

__license__   = """
DAMASK_GUI License Agreement (MIT License)
------------------------------------------

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

__about__ =  __copyright__ + '\n' + __license__

progname = os.path.basename(sys.argv[0])
progversion = "1.0"


class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (matplotlib.backends.backend_qt4agg)
       Author: Florent Rougon, Darren Dale
    """

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        # We want the axes cleared every time plot() is called
        self.axes.hold(False)
        self.fig = fig

        self.compute_initial_figure()

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        pass

class Plot2D(FilterBase):
    def update(self, src):
        # plot data from input
        data = self.input[0].result
        canvas = self.canvas
        canvas.axes.plot(  data['x'], data['y'] )
        canvas.axes.set_xlabel(data['xlabel'])
        canvas.axes.set_ylabel(data['ylabel'])
        canvas.fig.tight_layout()
        canvas.draw()
    
        
class Fig2D(MyMplCanvas):
    """A canvas that contains a Plot2D object appended to input"""
    def __init__(self, input=[],  *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)
        self.plotter = Plot2D(input)
        self.plotter.canvas = self
        
    def update(self):
        self.fig.tight_layout()
        MyMplCanvas.update(self)



class ApplicationWindow(QtGui.QMainWindow):
    def __init__(self, filters=[]):
        QtGui.QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("application main window")

        #----------------------------------
        self.file_menu = QtGui.QMenu('&File', self)
        self.file_menu.addAction('&Quit', self.fileQuit,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)

        self.help_menu = QtGui.QMenu('&Help', self)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.help_menu)

        self.help_menu.addAction('&About', self.about)

        self.main_widget = QtGui.QWidget(self)

        l = QtGui.QVBoxLayout(self.main_widget)
        
        
        #----------------------------------
        self.filters = filters
        for f in filters:
            assert (isinstance(f, FilterBase)), 'unexpected type of filter'

        #----------------------------------
        L=len(filters)
        dc = Fig2D( filters[L-1:L],  self.main_widget, width=6, height=4, dpi=100)
        l.addWidget(dc)
        
        #----------------------------------
        dialog = Dialog4Pipe(  filters, self.main_widget, self.updateWindow   )
        #pdb.set_trace()
        dialog.setWindowFlags(QtCore.Qt.Widget)
        l.addWidget(dialog)
        #mdiarea = QtGui.QMdiArea() 
        #l.addWidget(mdiarea)
        #w = mdiarea.addSubWindow(dialog.formwidget)
        #w.show()

        #----------------------------------
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

        self.statusBar().showMessage("", 2000)

    def updateWindow(self, formdata,  filter_list ):
        if filter_list: filter_list[0].proc(None)

    def fileQuit(self):
        self.close()

    def closeEvent(self, ce):
        self.fileQuit()

    def about(self):
        QtGui.QMessageBox.about(self, "About", __about__ )

class Dialog4Pipe(FormDialog):
    """Connect pipeline to TabFormDialog"""
    def __init__(self, filters, parent=None, update_callback=None):
        """ travel through the pipeline and create a form connected to each filter """
        
        f = filters[0] if filters else None
        Tabs = []
        Flts = []
        while f:
            try:
                Tabs.append( (f.ui_options,  type(f).__name__,  f.name ) ) 
                # datalist, tab_name, tab_help_msg
                Flts.append( f )
            except AttributeError:
                pass
            if f is filters[-1] :
                break
            else:
                f = f.output[0] if f.output else None

        FormDialog.__init__(self,  Tabs , 
                              "Options", "input parameters for each filter in the pipeline",
                              parent = parent,
                              apply = self.__apply__  )
                              
        self.filter_list = Flts
        self.update_callback = update_callback

    def __apply__(self, formdata):
        for i, f in enumerate( self.filter_list ):
            f.ui_options = formdata[i]
        if self.update_callback:
            self.update_callback( formdata, self.filter_list )


def show_example(name = "Example UI"):
    qApp = QtGui.QApplication(sys.argv)

    # 'creating ApplicationWindow ...'
    aw = ApplicationWindow( [fooFltr()] )
    aw.setWindowTitle(name)
    
    # 'show window'
    aw.show()
    sys.exit(qApp.exec_())
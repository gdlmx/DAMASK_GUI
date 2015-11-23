from __future__ import unicode_literals

from .formlayout import *
from .Filter import *
import sys, os, random,pdb
from PyQt4 import QtGui, QtCore, Qt

from numpy import arange, sin, pi
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT
from matplotlib.figure import Figure
from matplotlib import pyplot as ppl
import matplotlib

pkgs_version = {'Qt':QtCore.QT_VERSION_STR, 'PyQt': Qt.PYQT_VERSION_STR, 'Matplotlib':matplotlib.__version__}
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



class ApplicationWindow(QtGui.QMainWindow):
    def __init__(self, filters=[]):
        QtGui.QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("application main window")

        #----------------------------------
        self.file_menu = QtGui.QMenu('&File', self)
        self.menuBar().addMenu(self.file_menu)
        self.file_menu.addAction('&Quit',         self.fileQuit, QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        #self.file_menu.addAction('&NewFigWindow', self.create_sep_pplWindow, QtCore.Qt.CTRL + QtCore.Qt.Key_N)

        self.menuBar().addSeparator()

        self.help_menu = QtGui.QMenu('&Help', self)
        self.menuBar().addMenu(self.help_menu)
        self.help_menu.addAction('&About', self.about)

        self.main_widget = QtGui.QWidget(self)

        layout = QtGui.QVBoxLayout(self.main_widget)


        #----------------------------------
        self.filters = filters
        for f in filters:
            assert (isinstance(f, FilterBase)), 'unexpected type of filter'

        #----------------------------------
        dc = Fig2D( self.main_widget, width=6, height=6, dpi=100)
        layout.addWidget(dc)
        L=len(filters)
        pl = MPL_Plotter(filters[L-1:L]);
        pl.canvas, pl.fig, pl.axes = dc, dc.fig, dc.axes

        #----------------------------------
        self.mpl_toolbar = NavigationToolbar2QT(dc, self.main_widget)
        layout.addWidget(self.mpl_toolbar)

        #----------------------------------
        dialog = Dialog4Pipe(  filters, self.main_widget, self.exec_pipeline   )
        dialog.setWindowFlags(QtCore.Qt.Widget)
        layout.addWidget(dialog)


        #----------------------------------
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

        self.statusBar().showMessage("", 2000)

    @QtCore.pyqtSlot()
    def exec_pipeline(self, formdata,  filter_list ):
        if filter_list: filter_list[0].proc(None)

    @QtCore.pyqtSlot()
    def create_sep_pplWindow(self):
        fl = self.filters
        #fl[-1].output = []
        pl = MPL_Plotter(fl[-1])
        pl.fig    = ppl.figure()
        pl.axes   = pl.fig.add_subplot(111)
        pl.canvas = pl.fig.canvas
        #ppl.show()
        self.statusBar().showMessage("Figure will be plotted in new window", 2000)
        #pl.fig.show()
        #thread = SubWinThread( ppl )
        #thread.start()


    @QtCore.pyqtSlot()
    def fileQuit(self):
        self.close()

    @QtCore.pyqtSlot()
    def closeEvent(self, ce):
        self.fileQuit()

    @QtCore.pyqtSlot()
    def about(self):
        QtGui.QMessageBox.about(self, "About",
                                ''.join([k+' version = '+v+'\n' for k,v in pkgs_version.items()]) + __license__  )


class Fig2D(FigureCanvas):
    """Ultimately, this is a QWidget (matplotlib.backends.backend_qt4agg)
       Author: Florent Rougon, Darren Dale
    """
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        # We want the axes cleared every time plot() is called
        self.axes.hold(False)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    @QtCore.pyqtSlot()
    def update(self):
        self.fig.tight_layout()
        FigureCanvas.update(self)

class MPL_Plotter(FilterBase):
    def update(self, src):
        # plot data from input
        data = self.input[0].result
        self.axes.plot(  data['x'], data['y'] )
        self.axes.set_xlabel(data['xlabel'])
        self.axes.set_ylabel(data['ylabel'])
        self.fig.tight_layout()
        if isinstance(self.canvas, Fig2D):
            self.canvas.draw()
        else:
            ppl.show()
            src.output.remove(self)
            #thread = SubWinThread( )
            #thread.start()

class SubWinThread(QtCore.QThread):
    def __init__(self, v):
        QtCore.QThread.__init__(self)
        self.obj = v

    def run(self):
        self.obj.show()
        print 'thread1 ends'

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

    @QtCore.pyqtSlot()
    def __apply__(self, formdata):
        # get tab_widgets [formlayout.FormWidget,]
        widgetList =  self.formwidget.widgetlist
        # set ui_options of each filter object
        for i, f in enumerate( self.filter_list ):
            f.ui_options = (formdata[i],  widgetList[i].widgets)
        if self.update_callback:
            self.update_callback( formdata, self.filter_list )

class QWidgetModifier(object):
    def __call__(self, w):
        pass

class UIFilter(FilterBase):
    name = 'UIFilter'
    DEBUG=None
    options_def =  ((None,'str', 'NULL'),)  #[(Key, Type, defaultVal)]

    @property
    def ui_options(self):
        return [ ( key,  d_val) for key, typestr, d_val in self.options_def]

    @ui_options.setter
    def ui_options(self, value):
        valueList, self.widgetList = value
        i = 0
        time_inc = 0
        for key, typestr, d_val in self.options_def:
            v = valueList[i]
            if typestr=='list' and isinstance(v,int):
                v = d_val[v+1]
            elif typestr=='str_ml':
                v =[ k for k in v.split('\n') if k]
            self.options[key] =  v
            if self.options.has_key(key) and self.options[key] != v :
                time_inc = 1
            i+=1
        self.opt_time += time_inc

    def update_form(self, valueDict):
        for i, w in enumerate(self.widgetList):
            key, typestr, d_val = self.options_def[i]
            try:
                value = valueDict[key]
                if isinstance(value, QWidgetModifier):
                    value(w)
                    value = value.value
            except (KeyError,AttributeError):
                continue
            if typestr == 'list' and isinstance(w, QComboBox):
                self.options_def[i] = (key, typestr, value)
                w.clear()
                w.addItems(value[1:])
                w.setCurrentIndex(value[0])
            elif isinstance(w, (QLineEdit,QTextEdit)):
                w.setText(value if isinstance(value, (str, unicode)) else repr(value))
                

    def set_options_def(self):
        self.options_def =[ (k, type(v).__name__, v) for k,v in self.options.items() ]

    def set_optparser(self, p):
        """ read optparse.OptionParser object """
        self.options_def = []
        for opt in p.option_list:
            if not opt.dest: continue
            key = opt.dest
            # https://docs.python.org/2/library/optparse.html#optparse-standard-option-types
            # Decision tree
            oType = DT( { "store_true":"bool", "store_false":"bool",
                          "append":{'string':"str_ml"},
                          "DT_default":{'int':'int','long':'int','float':'float','choice':'list','DT_default':'str'}
                        } )[opt.action][opt.type].value
            if self.DEBUG : print('{0}\t{1}\t{2}'.format(opt, key, oType))

            # set default value
            default = opt.default
            if isinstance(default , (tuple,list) ) and default[0] == 'NO':
                default = ''
            if oType == 'bool':
                self.options[key] = default = bool(default)
            elif oType == 'str_ml':
                oType = 'str'
                default = "{0}\n".format(default)
            elif oType == 'list':
                Id = opt.choices.index(default)  if  default else 0
                default = [ Id ] + opt.choices
            elif not self.options.has_key(key):
                self.options[key] = default

            # set option definition
            self.options_def.append( (key, oType, default) )

class DT(object):
    def __init__(self, tree=None):
        self.value = tree
    def __getitem__(self, index):
        if isinstance(self.value, dict):
            try:
                return DT(self.value[index])
            except KeyError:
                return DT(self.value['DT_default'])
        else:
            return DT(self.value)


class fooFltr(UIFilter):
    """Example UI_Filter"""
    name = 'plot sin(n*x)'
    opt_time = 1

    def __init__(self, *value):
        super(fooFltr, self).__init__( *value )
        import numpy as np
        self.options = {'xlabel':'x', 'ylabel':'sin(x)', 'n':1.0}
        x = np.arange(0, 2 * 3.141, 0.1)
        self.result = {'x':x, 'y':np.sin(x), 'xlabel':'x', 'ylabel':'sin(x)'}
        self.set_options_def()

    def update(self, src):
        import numpy as np
        x = self.result['x']
        n = self.options['n']
        self.result['y'] =  np.sin(n*x)
        for k in ['xlabel','ylabel'] :  self.result[k] = self.options[k]
        self.mod_time = self.opt_time


def show_example(name = "Example UI"):
    qApp = QtGui.QApplication(sys.argv)

    # 'creating ApplicationWindow ...'
    aw = ApplicationWindow( [fooFltr()] )
    aw.setWindowTitle(name)

    # 'show window'
    aw.show()
    sys.exit(qApp.exec_())
# -*- coding: utf-8 -*-
__copyright__ = "Copyright (C) 2015 Mingxuan Lin"

import sys
from  .ui import QtGui, ApplicationWindow, progname
from  .plugin import stdout_parser as sp
from  .plugin import plotdat as pd

if __name__ == "__main__":
    qApp = QtGui.QApplication(sys.argv)

    # creating ApplicationWindow
    m = sp.SO_Reader()
    aw = ApplicationWindow( [ m , pd.PlotXY(m)] )

    aw.setWindowTitle(progname)

    # show window
    aw.show()
    sys.exit(qApp.exec_()) # execute the window/app.

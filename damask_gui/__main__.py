# -*- coding: utf-8 -*-
__copyright__ = "Copyright (C) 2015 Mingxuan Lin"

import sys
from . import QtGui, ApplicationWindow
from  .plugin import stdout_parser as sp
from  .plugin import plotdat as pd

if __name__ == "__main__":
    qApp = QtGui.QApplication(sys.argv)

    # 'creating ApplicationWindow ...'
    m = sp.SO_Reader()
    aw = ApplicationWindow( [ m , pd.PlotXY(m)] )

    aw.setWindowTitle("DAMASK_GUI")

    # 'show window'
    aw.show()
    sys.exit(qApp.exec_()) # execute the window/app.

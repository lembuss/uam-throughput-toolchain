import sys
import globals
import dataImport as imp
import guiWindow as gui
from matplotlib.backends.qt_compat import QtWidgets
import os


if __name__ == "__main__":
    globals.init()

    # Get the current script's directory and construct parent
    current_dir = os.path.dirname(__file__)
    parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
    
    # get file path for input data for import
    source_file_path = 'Input_Data/EDDM_STARs_SIDs_Waypoints_RF_no_crossing_UAV_Approach.xlsx'
    file_path = os.path.join(parent_dir, source_file_path)

    # import routes and waypoints, automatically calculates everythisng necessary to plot from source file
    imp.importExcelData(file_path)

    # prepare plot
    qapp = QtWidgets.QApplication.instance()
    if not qapp:
        qapp = QtWidgets.QApplication(sys.argv)

    app = gui.Window3DPlot()
    app.show()
    app.activateWindow()
    app.raise_()
    qapp.exec()  
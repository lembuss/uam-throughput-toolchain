import globals
import guiFigureoptions
from PyQt5 import QtGui
from classes import AircraftRoute
from matplotlib.figure import Figure
from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.backends.backend_qt5agg import (FigureCanvas, NavigationToolbar2QT as NavigationToolbar)

class Window3DPlot(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)
        layout = QtWidgets.QVBoxLayout(self._main)

        self.canvas = FigureCanvas(Figure())
        layout.addWidget(NavigationToolbar(self.canvas, self))
        layout.addWidget(self.canvas)

        AircraftRoute.getRoutesSorted()
        #self._axis = self.canvas.figure.gca(projection='3d')
        self._axis = self.canvas.figure.add_subplot(projection='3d')
        self._axis.set_box_aspect((1, 1, 1 / globals.factorm2ft))
        AircraftRoute.plotRoutes(axis=self._axis)
        AircraftRoute.plotContour(axis=self._axis)

        # self._axis.contour(globals.map_population_grid_x, globals.map_population_grid_y, globals.map_population)
        # self._axis.scatter(globals.map_population_grid_x[::100], globals.map_population_grid_y[::100], zdir='z')
        # self._axis.bar3d(globals.map_population_grid_x[::1000], globals.map_population_grid_y[::1000],
        #                  npy.zeros_like(globals.map_population_grid_x[::1000]), 500, 500, npy.ones_like(globals.map_population_grid_x[::1000]) * 500, shade=True)

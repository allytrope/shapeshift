"""Create window and widgets, the starting point for executing Shapeshift."""

# Standard library imports
import sys

# Third-party imports
import numpy as np
from PySide6 import QtCore, QtGui, QtWidgets

# Local imports
from graphics import ModernGLWidget
from operations import Operations
import polyhedra


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        print("first")
        super(MainWindow, self).__init__()
        self.setWindowTitle("Shapeshift")
        self.setGeometry(100, 100, 800, 500)

        self.prior_polyhedra = []
        self.set_current_polyhedron(polyhedra.Tetrahedron())
        #self.current_polyhedron = polyhedra.Cube()
        
    def setupUI(self):
        """Set up layout of widgets."""
        # Toolbar
        menubar = QtWidgets.QMenuBar()

        file_menu = menubar.addMenu("File")
        file_menu.addAction(open_action := QtGui.QAction("Open", self))
        file_menu.addAction(export_action := QtGui.QAction("Export", self))

        edit_menu = menubar.addMenu("Edit")
        edit_menu.addAction(undo_action := QtGui.QAction("Undo", self))
        edit_menu.addAction(redo_action := QtGui.QAction("Redo", self))

        view_menu = menubar.addMenu("View")
        view_menu.addAction(tetrahedron_action := QtGui.QAction("Tetrahedron", self))
        view_menu.addAction(cube_action := QtGui.QAction("Cube", self))
        view_menu.addAction(octahedron_action := QtGui.QAction("Octahedron", self))
        view_menu.addAction(dodecahedron_action := QtGui.QAction("Dodecahedron", self))
        view_menu.addAction(icosahedron_action := QtGui.QAction("Icosahedron", self))

        modify_menu = menubar.addMenu("Modify")
        modify_menu.addAction(clear_prior_polyhedra_action := QtGui.QAction("Clear prior polyhedra", self))

        details_menu = menubar.addMenu("Details")
        details_menu.addAction(element_values_action := QtGui.QAction("Element values", self))
        details_menu.addAction(element_counts_action := QtGui.QAction("Element counts", self))
        details_menu.addAction(face_types_action := QtGui.QAction("Face types", self))

        self.setMenuBar(menubar)

        # Operations tab
        self.tab_1_layout = QtWidgets.QGridLayout()
        self.tab_1 = QtWidgets.QWidget()
        self.truncate = QtWidgets.QPushButton("Truncate")
        self.tab_1_layout.addWidget(self.truncate, 1, 1)
        self.rectify = QtWidgets.QPushButton("Rectify")
        self.tab_1_layout.addWidget(self.rectify, 2, 1)
        self.facet = QtWidgets.QPushButton("Facet")
        self.tab_1_layout.addWidget(self.facet, 3, 1)
        self.dual = QtWidgets.QPushButton("Dual")
        self.tab_1_layout.addWidget(self.dual, 2, 2)
        self.cap = QtWidgets.QPushButton("Cap")
        self.tab_1_layout.addWidget(self.cap, 1, 3)
        self.bridge = QtWidgets.QPushButton("Bridge")
        self.tab_1_layout.addWidget(self.bridge, 2, 3)
        self.stellate = QtWidgets.QPushButton("Stellate")
        self.tab_1_layout.addWidget(self.stellate, 3, 3)
        self.tab_1.setLayout(self.tab_1_layout)

        self.tab_2_layout = QtWidgets.QGridLayout()
        self.tab_2 = QtWidgets.QWidget()
        self.decompose = QtWidgets.QPushButton("Decompose")
        self.tab_2_layout.addWidget(self.decompose, 1, 1)
        self.uncouple = QtWidgets.QPushButton("Uncouple")
        self.tab_2_layout.addWidget(self.uncouple, 1, 2)
        self.tab_2.setLayout(self.tab_2_layout)

        # Create tab widget
        self.tab_widget = QtWidgets.QTabWidget()
        self.tab_widget.setMaximumWidth(300)
        
        self.tab_widget.addTab(self.tab_1, "Truncation")
        self.tab_widget.addTab(self.tab_2, "Separation")

        # Create horizontal box layout
        self.hbox = QtWidgets.QHBoxLayout()
        self.hbox.addWidget(self.tab_widget)

        # Create moderngl widget
        #self.moderngl_widget = ModernGLWidget(self)
        #self.hbox.addWidget(self.moderngl_widget)

        # Create vertical box for QOpenGLWidget and QSliders
        self.vbox = QtWidgets.QVBoxLayout()
        self.vbox.addWidget(moderngl_widget := ModernGLWidget(self))
        self.vbox.addWidget(x_slider := QtWidgets.QSlider(QtCore.Qt.Horizontal))
        self.vbox.addWidget(y_slider := QtWidgets.QSlider(QtCore.Qt.Horizontal))
        self.vbox.addWidget(z_slider := QtWidgets.QSlider(QtCore.Qt.Horizontal))

        self.moderngl_and_sliders = QtWidgets.QWidget()
        self.moderngl_and_sliders.setLayout(self.vbox)
        self.hbox.addWidget(self.moderngl_and_sliders)

        # Create central widget
        self.central_widget = QtWidgets.QWidget()
        self.central_widget.setLayout(self.hbox)
        self.setCentralWidget(self.central_widget)

        # Connect operations to buttons/actions
        self.truncate.clicked.connect(lambda: self.operations(Operations.truncate))
        self.rectify.clicked.connect(lambda: self.operations(Operations.rectify))
        self.facet.clicked.connect(lambda: self.operations(Operations.facet))
        self.dual.clicked.connect(lambda: self.operations(Operations.reciprocate))
        self.cap.clicked.connect(lambda: self.operations(Operations.cap))
        self.bridge.clicked.connect(lambda: self.operations(Operations.bridge))
        self.stellate.clicked.connect(lambda: self.operations(Operations.stellate))
        self.decompose.clicked.connect(lambda: self.operations(Operations.decompose))
        self.uncouple.clicked.connect(lambda: self.operations(Operations.uncouple))
        tetrahedron_action.triggered.connect(lambda: self.set_current_polyhedron(polyhedra.Tetrahedron()))
        cube_action.triggered.connect(lambda: self.set_current_polyhedron(polyhedra.Cube()))
        octahedron_action.triggered.connect(lambda: self.set_current_polyhedron(polyhedra.Octahedron()))
        dodecahedron_action.triggered.connect(lambda: self.set_current_polyhedron(polyhedra.Dodecahedron()))
        icosahedron_action.triggered.connect(lambda: self.set_current_polyhedron(polyhedra.Icosahedron()))
        undo_action.triggered.connect(self.undo)
        redo_action.triggered.connect(self.redo)
        clear_prior_polyhedra_action.triggered.connect(self.clear_prior_polyhedra)
        element_values_action.triggered.connect(self.element_values)
        element_counts_action.triggered.connect(self.element_count)
        face_types_action.triggered.connect(self.face_types)

        timer = QtCore.QTimer(self)
        timer.timeout.connect(moderngl_widget.update)
        timer.start(30)        

    def add_list_item(self, text):
        if self.current_polyhedron:
            item = QtWidgets.QListWidgetItem(text)
            #self.listWidget.addItem(item)

    def set_current_polyhedron(self, polyhedron):
        """Set current_polyhedron to a seed polyhedron."""
        self.prior_polyhedra.append(polyhedron)
        self.current_polyhedron = polyhedron
        self.add_list_item(polyhedron.__class__.__name__.capitalize())

    def operations(self, operation):
        """Perform a polyhedral operation on current_polyhedron."""
        self.prior_polyhedra.append(self.current_polyhedron)
        self.current_polyhedron = operation(self.current_polyhedron)
        self.add_list_item(operation.__name__.capitalize())

    def clear_prior_polyhedra(self):
        self.prior_polyhedra.clear()

    def element_values(self):
        self.current_polyhedron.full_stats()

    def element_count(self):
        self.current_polyhedron.stats()

    def face_types(self):
        self.current_polyhedron.face_types()

    def undo(self):
        if len(self.prior_polyhedra) == 0:
            print("No previous polyhedron")
        else:
            self.current_polyhedron = self.prior_polyhedra.pop()

    def redo(self):
        print("No function yet")


app = QtWidgets.QApplication(sys.argv)
app_window = MainWindow()
app_window.setupUI()
app_window.show()
sys.exit(app.exec())

#mglw.run_window_config(WindowMGLW)
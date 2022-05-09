"""Create window and widgets, the starting point for executing Shapeshift."""

# Standard library imports
import random
import sys

# Third-party imports
from PySide6 import QtCore, QtGui, QtWidgets

# Local imports
import figures
from graphics import ModernGLWidget
from polytope import Polyhedron


class AxisSlider(QtWidgets.QSlider):
    def __init__(self):
        super().__init__(QtCore.Qt.Horizontal)
        self.setValue(random.randint(0, 100))


class OperationButton(QtWidgets.QPushButton):
    def __init__(self, name):
        super().__init__(name)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Shapeshift")
        self.setGeometry(100, 100, 830, 550)
        self.polytope_models = [Model(figures.octahedron)]
        self.setStyleSheet("""
        background-color: #262626;
        color: #FFFFFF;
        """)

    @property
    def polytope(self):
        return self.polytope_models[-1].polytope
        
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
        modify_menu.addAction(clear_polyhedra_action := QtGui.QAction("Clear polyhedra", self))

        details_menu = menubar.addMenu("Details")
        details_menu.addAction(element_values_action := QtGui.QAction("Element values", self))
        details_menu.addAction(element_counts_action := QtGui.QAction("Element counts", self))
        details_menu.addAction(face_types_action := QtGui.QAction("Face types", self))

        self.setMenuBar(menubar)

        # Operations tab
        self.tab_1 = QtWidgets.QWidget()
        self.tab_1_layout = QtWidgets.QGridLayout()
        self.tab_1_layout.addWidget(truncate := OperationButton("Truncate"), 1, 1)
        self.tab_1_layout.addWidget(rectify := OperationButton("Rectify"), 2, 1)
        self.tab_1_layout.addWidget(facet := OperationButton("Facet"), 3, 1)
        self.tab_1_layout.addWidget(dual := OperationButton("Dual"), 2, 2)
        self.tab_1_layout.addWidget(cap := OperationButton("Cap"), 1, 3)
        self.tab_1_layout.addWidget(bridge := OperationButton("Bridge"), 2, 3)
        self.tab_1_layout.addWidget(stellate := OperationButton("Stellate"), 3, 3)
        self.tab_1.setLayout(self.tab_1_layout)

        self.tab_2 = QtWidgets.QWidget()
        self.tab_2_layout = QtWidgets.QGridLayout()
        self.tab_2_layout.addWidget(decompose := OperationButton("Decompose"), 1, 1)
        self.tab_2_layout.addWidget(uncouple := OperationButton("Uncouple"), 1, 2)
        self.tab_2.setLayout(self.tab_2_layout)

        self.tab_3 = QtWidgets.QWidget()
        self.tab_3_layout = QtWidgets.QGridLayout()
        self.tab_3_layout.addWidget(prismate := OperationButton("Prismate"), 1, 1)
        self.tab_3.setLayout(self.tab_3_layout)

        # Create tab widget
        self.tab_widget = QtWidgets.QTabWidget()
        self.tab_widget.addTab(self.tab_1, "Truncate")
        self.tab_widget.addTab(self.tab_2, "Separate")
        self.tab_widget.addTab(self.tab_3, "Hypermutate")

        # Create descriptive text box
        self.descriptive_textbox = QtWidgets.QLabel("")
        self.descriptive_textbox.setWordWrap(True)

        # Polyhedra rendering options
        self.show_edges_only = QtWidgets.QCheckBox("Show edges only", self)
        self.show_prior_polyhedra_checkbox = QtWidgets.QCheckBox("Show prior polyhedra", self)

        # Create left vertical box
        self.left_vbox = QtWidgets.QVBoxLayout()
        self.left_vbox.addWidget(self.tab_widget)
        self.left_vbox.addWidget(self.descriptive_textbox)
        self.left_vbox.addWidget(self.show_edges_only)
        self.left_vbox.addWidget(self.show_prior_polyhedra_checkbox)
        self.left_widget = QtWidgets.QWidget()
        self.left_widget.setLayout(self.left_vbox)
        self.left_widget.setMaximumWidth(330)

        # Create horizontal box layout
        self.hbox = QtWidgets.QHBoxLayout()
        self.hbox.addWidget(self.left_widget)

        # Create vertical box for QOpenGLWidget and QSliders
        self.vbox = QtWidgets.QVBoxLayout()
        self.vbox.addWidget(moderngl_widget := ModernGLWidget(self))
        self.x_slider = AxisSlider()
        self.vbox.addWidget(self.x_slider)
        self.y_slider = AxisSlider()
        self.vbox.addWidget(self.y_slider)
        self.z_slider = AxisSlider()
        self.vbox.addWidget(self.z_slider)

        self.moderngl_and_sliders = QtWidgets.QWidget()
        self.moderngl_and_sliders.setLayout(self.vbox)
        self.hbox.addWidget(self.moderngl_and_sliders)

        # Add zoom slider
        self.zoom_slider = QtWidgets.QSlider()
        self.hbox.addWidget(self.zoom_slider)
        self.zoom_slider.setValue(10)

        # Create list of created polyhedra
        self.right_vbox = QtWidgets.QVBoxLayout()
        self.right_widget = QtWidgets.QWidget()
        self.right_widget.setLayout(self.right_vbox)
        self.hbox.addWidget(self.right_widget)
        
        # Create central widget
        self.central_widget = QtWidgets.QWidget()
        self.central_widget.setLayout(self.hbox)
        self.setCentralWidget(self.central_widget)

        # Connect operations to buttons/actions
        truncate.clicked.connect(lambda: self.operations(Polyhedron.truncate))
        rectify.clicked.connect(lambda: self.operations(Polyhedron.rectify))
        facet.clicked.connect(lambda: self.operations(Polyhedron.facet))
        dual.clicked.connect(lambda: self.operations(Polyhedron.reciprocate))
        cap.clicked.connect(lambda: self.operations(Polyhedron.cap))
        bridge.clicked.connect(lambda: self.operations(Polyhedron.bridge))
        stellate.clicked.connect(lambda: self.operations(Polyhedron.stellate))
        decompose.clicked.connect(lambda: self.operations(Polyhedron.decompose))
        uncouple.clicked.connect(lambda: self.operations(Polyhedron.uncouple))
        tetrahedron_action.triggered.connect(lambda: self.set_current_polyhedron(figures.tetrahedron))
        cube_action.triggered.connect(lambda: self.set_current_polyhedron(figures.cube))
        octahedron_action.triggered.connect(lambda: self.set_current_polyhedron(figures.octahedron))
        dodecahedron_action.triggered.connect(lambda: self.set_current_polyhedron(figures.dodecahedron))
        icosahedron_action.triggered.connect(lambda: self.set_current_polyhedron(figures.icosahedron))
        undo_action.triggered.connect(self.undo)
        redo_action.triggered.connect(self.redo)
        clear_polyhedra_action.triggered.connect(self.clear_polyhedra)
        element_values_action.triggered.connect(self.element_values)
        element_counts_action.triggered.connect(self.element_count)
        face_types_action.triggered.connect(self.face_types)

        timer = QtCore.QTimer(self)
        timer.timeout.connect(moderngl_widget.update)
        timer.start(30)        

    #def add_list_item(self, text):
    #    if self.current_polyhedron:
    #        item = QtWidgets.QListWidgetItem(text)
    #        #self.listWidget.addItem(item)

    def set_current_polyhedron(self, polyhedron):
        """Set current_polyhedron to a seed polyhedron."""
        self.polytope_models.append(Model(polyhedron))
        #self.current_polyhedron = polyhedron
        #self.add_list_item(polyhedron.__class__.__name__.capitalize())

    def operations(self, operation):
        """Perform a polyhedral operation on current_polyhedron."""
        current_polyhedron = operation(self.polytope)
        self.polytope_models.append(Model(current_polyhedron))
        #self.add_list_item(operation.__name__.capitalize())

    def clear_polyhedra(self):
        self.polytope_models.clear()

    def element_values(self):
        self.polytope.full_stats()

    def element_count(self):
        self.polytope.stats()

    def face_types(self):
        self.polytope.face_types()

    def undo(self):
        if len(self.polytope_models) == 0:
            print("No previous polyhedron")
        else:
            self.polytope_models.pop()

    def redo(self):
        print("No function yet")

class Model:
    def __init__(self, polytope):
        # Determine color of the polyhedron
        self.polytope = polytope
        self.color = [self.randomize_color() for face in self.polytope.faces]

    def randomize_color(self):
        """Change RGB color of polyhedron."""
        return (random.randint(2,10)/10,
                random.randint(2,10)/10,
                random.randint(2,10)/10)


app = QtWidgets.QApplication(sys.argv)
app_window = MainWindow()
app_window.setupUI()
app_window.show()
sys.exit(app.exec())

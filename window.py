"""Create window, the starting point for executing Shapeshift."""

# standard library imports
import sys

# third-party imports
from PyQt5 import QtCore, QtGui, QtWidgets, uic
import OpenGL.GL as GL
import OpenGL.GLU as GLU

# local imports
import polyhedra
from operations import Operations


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi("qt_layout.ui", self)
        self.prior_polyhedra = []
        self.set_current_polyhedron(polyhedra.Cube())
        #self.current_polyhedron = polyhedra.Cube()
        
    def setupUI(self):
        self.buttonTruncate.clicked.connect(lambda: self.operations(Operations.truncate))
        self.buttonRectify.clicked.connect(lambda: self.operations(Operations.rectify))
        self.buttonFacet.clicked.connect(lambda: self.operations(Operations.facet))
        self.buttonDual.clicked.connect(lambda: self.operations(Operations.reciprocate))
        self.buttonCap.clicked.connect(lambda: self.operations(Operations.cap))
        self.buttonBridge.clicked.connect(lambda: self.operations(Operations.bridge))
        self.buttonStellate.clicked.connect(lambda: self.operations(Operations.stellate))
        self.openGLWidget.initializeGL = self.initialize
        self.openGLWidget.paintGL = self.paint
        #self.actionDecompose.triggered.connect(lambda: self.operations(Operations.decompose))
        self.actionUndo.triggered.connect(self.undo)
        self.actionRedo.triggered.connect(self.redo)
        self.actionTetrahedron.triggered.connect(lambda: self.set_current_polyhedron(polyhedra.Tetrahedron()))
        self.actionCube.triggered.connect(lambda: self.set_current_polyhedron(polyhedra.Cube()))
        self.actionOctahedron.triggered.connect(lambda: self.set_current_polyhedron(polyhedra.Octahedron()))
        self.actionDodecahedron.triggered.connect(lambda: self.set_current_polyhedron(polyhedra.Dodecahedron()))
        self.actionIcosahedron.triggered.connect(lambda: self.set_current_polyhedron(polyhedra.Icosahedron()))
        self.actionClear_prior_polyhedra.triggered.connect(self.clear_prior_polyhedra)
        self.actionElement_values.triggered.connect(self.element_values)
        self.actionElement_count.triggered.connect(self.element_count)
        self.actionFace_types.triggered.connect(self.face_types)
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.openGLWidget.update)
        timer.start(9)
        

    def add_list_item(self, text):
        #for polyhedron in self.prior_polyhedron:
        if self.current_polyhedron:
            item = QtWidgets.QListWidgetItem(text)
            self.listWidget.addItem(item)

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

    def initialize(self):
        GLU.gluPerspective(45, 1, 0.1, 50.0)
        GL.glTranslatef(0.0, 0.0, -5)

    def paint(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        self.current_polyhedron.draw_faces()
        self.current_polyhedron.draw_edges()
        if self.checkBox.isChecked() == True:
            for polyhedron in self.prior_polyhedra:
                polyhedron.draw_edges()
        GL.glRotatef(.2, .2, 1, .2)

app = QtWidgets.QApplication(sys.argv)
app_window = MainWindow()
app_window.setupUI()
app_window.show()
sys.exit(app.exec_())
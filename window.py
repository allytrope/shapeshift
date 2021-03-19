# standard library imports
import sys

# third-party imports
from PyQt5 import QtCore, QtGui, QtWidgets, uic
import OpenGL.GL as GL
import OpenGL.GLU as GLU

# local imports
import shapeshift


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.prior_polyhedra = []
        self.current_polyhedron = shapeshift.Cube
        uic.loadUi("qt_layout.ui", self)
        
    def setupUI(self):
        self.button1.clicked.connect(self.rectify)
        self.button2.clicked.connect(self.dual)
        self.button3.clicked.connect(self.truncate)
        self.button4.clicked.connect(self.stellate)
        self.openGLWidget.initializeGL = self.initialize
        self.openGLWidget.paintGL = self.paint
        self.actionUndo.triggered.connect(self.undo)
        self.actionRedo.triggered.connect(self.redo)
        self.actionTetrahedron.triggered.connect(self.Tetrahedron)
        self.actionCube.triggered.connect(self.Cube)
        self.actionOctahedron.triggered.connect(self.Octahedron)
        self.actionDodecahedron.triggered.connect(self.Dodecahedron)
        self.actionIcosahedron.triggered.connect(self.Icosahedron)
        self.actionClear_prior_polyhedra.triggered.connect(self.clear_prior_polyhedra)
        self.actionElement_values.triggered.connect(self.element_values)
        self.actionElement_count.triggered.connect(self.element_count)
        self.actionFace_types.triggered.connect(self.face_types)
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.openGLWidget.update)
        timer.start(9)

    def Tetrahedron(self):
        self.prior_polyhedra.append(self.current_polyhedron)
        self.current_polyhedron = shapeshift.Tetrahedron

    def Cube(self):
        self.prior_polyhedra.append(self.current_polyhedron)
        self.current_polyhedron = shapeshift.Cube

    def Octahedron(self):
        self.prior_polyhedra.append(self.current_polyhedron)
        self.current_polyhedron = shapeshift.Octahedron

    def Dodecahedron(self):
        self.prior_polyhedra.append(self.current_polyhedron)
        self.current_polyhedron = shapeshift.Dodecahedron

    def Icosahedron(self):
        self.prior_polyhedra.append(self.current_polyhedron)
        self.current_polyhedron = shapeshift.Icosahedron

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
            print("here")

    def redo(self):
        print("No function yet")

    def rectify(self):
        self.prior_polyhedra.append(self.current_polyhedron)
        self.current_polyhedron = self.current_polyhedron.rectify()

    def dual(self):
        print("No dual function yet")

    def truncate(self):
        self.prior_polyhedra.append(self.current_polyhedron)
        self.current_polyhedron = self.current_polyhedron.truncate()

    def stellate(self):
        print("No stellation function yet")

    def initialize(self):
        GLU.gluPerspective(45, 1, 0.1, 50.0)
        GL.glTranslatef(0.0, 0.0, -5)

    def paint(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        self.current_polyhedron.draw_faces()
        if self.checkBox.isChecked() == True:
            for polyhedron in self.prior_polyhedra:
                polyhedron.draw_faces()
        GL.glRotatef(.2, .2, 1, .2)

app = QtWidgets.QApplication(sys.argv)
app_window = MainWindow()
app_window.setupUI()
app_window.show()
sys.exit(app.exec_())
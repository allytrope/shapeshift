"""Create window, the starting point for executing Shapeshift."""

# standard library imports
import struct
import sys

# third-party imports
import moderngl
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# local imports
from operations import Operations
import polyhedra

class ModernGLWidget(QtWidgets.QOpenGLWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        fmt = QtGui.QSurfaceFormat()
        fmt.setVersion(4, 1)
        fmt.setProfile(QtGui.QSurfaceFormat.CoreProfile)
        self.setFormat(fmt)
        self.resize(512, 512)

    def initializeGL(self):
        #self.screen = self.ctx.detect_framebuffer()

        ctx = moderngl.create_context()

        prog = ctx.program(
            vertex_shader='''
                #version 330

                in vec2 in_vert;
                in vec3 in_color;

                out vec3 v_color;

                void main() {
                    v_color = in_color;
                    gl_Position = vec4(in_vert, 0.0, 1.0);
                }
            ''',
            fragment_shader='''
                #version 330

                in vec3 v_color;

                out vec3 f_color;

                void main() {
                    f_color = v_color;
                }
            ''',
        )

        vertices = np.array([vertex.coordinates for vertex in self.parent.current_polyhedron.vertices], dtype="float32").flatten()
        faces = np.array([face._vertices for face in self.parent.current_polyhedron.faces], dtype=np.uintc).flatten()

        vbo = ctx.buffer(vertices.astype('f4').tobytes())
        self.vao = ctx.simple_vertex_array(prog, vbo, 'in_vert', 'in_color')
        # self.vao = ctx.vertex_array(
        #     prog,
        #     [
        #         (vbo, "3f", "in_vert")
        #     ]
        # )

    def clear(self):
        pass

    def draw(self):
        pass

    def rotate(self):
        pass

    def paintGL(self):
        print("inside paintGL")
        self.clear()
        self.vao.render(moderngl.LINE_LOOP)
        #if self.checkBox.isChecked() == True:
        #    for polyhedron in self.prior_polyhedra:
        #        graphics.draw(polyhedron)
        #graphics.rotate()

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        print("first")
        super(MainWindow, self).__init__()
        #uic.loadUi("qt_layout.ui", self)

        self.setGeometry(100, 100, 640, 480)

        self.prior_polyhedra = []
        self.set_current_polyhedron(polyhedra.Cube())
        #self.current_polyhedron = polyhedra.Cube()
        
    def setupUI(self):
        # Create horizontal box layout
        self.hbox = QtWidgets.QHBoxLayout()
        self.button_1 = QtWidgets.QPushButton("1")
        self.hbox.addWidget(self.button_1)

        # Create moderngl widget
        self.moderngl_widget = ModernGLWidget(self)
        self.hbox.addWidget(self.moderngl_widget)

        # Create central widget
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.hbox)
        self.setCentralWidget(self.central_widget)

        #self.dock = QDockWidget("MyDock")
        #self.addDockWidget(Qt.RightDockWidgetArea, self.dock)

        #self.moderngl_widget = ModernGLWidget(self.dock)
        #self.dock.setWidget(self.moderngl_widget)
        print("Inside MainWindow")

        print("setupUI")

        #self.buttonTruncate.clicked.connect(lambda: self.operations(Operations.truncate))
        #self.buttonRectify.clicked.connect(lambda: self.operations(Operations.rectify))
        #self.buttonFacet.clicked.connect(lambda: self.operations(Operations.facet))
        #self.buttonDual.clicked.connect(lambda: self.operations(Operations.reciprocate))
        #self.buttonCap.clicked.connect(lambda: self.operations(Operations.cap))
        #self.buttonBridge.clicked.connect(lambda: self.operations(Operations.bridge))
        #self.buttonStellate.clicked.connect(lambda: self.operations(Operations.stellate))
        #self.openGLWidget.initializeGL = self.initialize
        #self.openGLWidget.paintGL = self.paint
        ##self.actionDecompose.triggered.connect(lambda: self.operations(Operations.decompose))
        #self.actionUndo.triggered.connect(self.undo)
        #self.actionRedo.triggered.connect(self.redo)
        #self.actionTetrahedron.triggered.connect(lambda: self.set_current_polyhedron(polyhedra.Tetrahedron()))
        #self.actionCube.triggered.connect(lambda: self.set_current_polyhedron(polyhedra.Cube()))
        #self.actionOctahedron.triggered.connect(lambda: self.set_current_polyhedron(polyhedra.Octahedron()))
        #self.actionDodecahedron.triggered.connect(lambda: self.set_current_polyhedron(polyhedra.Dodecahedron()))
        #self.actionIcosahedron.triggered.connect(lambda: self.set_current_polyhedron(polyhedra.Icosahedron()))
        #self.actionClear_prior_polyhedra.triggered.connect(self.clear_prior_polyhedra)
        #self.actionElement_values.triggered.connect(self.element_values)
        #self.actionElement_count.triggered.connect(self.element_count)
        #self.actionFace_types.triggered.connect(self.face_types)

        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.moderngl_widget.update)
        timer.start(9)
        pass
        

    def add_list_item(self, text):
        if self.current_polyhedron:
            item = QtWidgets.QListWidgetItem(text)
            #self.listWidget.addItem(item)

    def set_current_polyhedron(self, polyhedron):
        """Set current_polyhedron to a seed polyhedron."""
        self.prior_polyhedra.append(polyhedron)
        self.current_polyhedron = polyhedron
        self.add_list_item(polyhedron.__class__.__name__.capitalize())
        #graphics.set_buffers(polyhedron)

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
        #graphics.setup(self.current_polyhedron)
        #graphics.set_buffers(self.current_polyhedron)
        pass

    def paint(self):
        #print("Main Loop")
        #graphics.clear()
        #graphics.draw(self.current_polyhedron)
        #if self.checkBox.isChecked() == True:
        #    for polyhedron in self.prior_polyhedra:
        #        graphics.draw(polyhedron)
        #graphics.rotate()
        pass

app = QtWidgets.QApplication(sys.argv)
app_window = MainWindow()
app_window.setupUI()
app_window.show()
sys.exit(app.exec_())
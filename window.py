"""Create window, the starting point for executing Shapeshift."""

# standard library imports
import ctypes
import sys
from OpenGL.raw.GL.VERSION.GL_2_0 import glGetProgramiv, glShaderSource
from OpenGL.raw.GL.VERSION.GL_3_0 import glBindVertexArray

# third-party imports
from PyQt5 import QtCore, QtGui, QtWidgets, uic
import numpy as np
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
        vertex_array = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(vertex_array)

        buffer = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, buffer)
        #vertices = np.array([1.0, 1.0, 1.0, -0.8, 0.8, 0.8, 1.0, -1.0, -1.0], dtype=np.float32)
        #GL.glBufferData(GL.GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL.GL_STATIC_DRAW)

        vertex_src = """
        #version 140

        in vec3 coordinates;

        void main()
        {
            gl_Position = vec4(coordinates, 1.0);
        }
        """
        vertex_shader = GL.glCreateShader(GL.GL_VERTEX_SHADER)
        GL.glShaderSource(vertex_shader, vertex_src)
        GL.glCompileShader(vertex_shader)

        status = GL.glGetShaderiv(vertex_shader, GL.GL_COMPILE_STATUS)
        print("status:", status)
        log =  GL.glGetShaderInfoLog(vertex_shader)
        print("log:", log)

        fragment_src = """
        #version 140

        uniform vec3 color;

        out vec4 outColor;

        void main()
        {
            outColor = vec4(color, 0.8);
        }
        """

        fragment_shader = GL.glCreateShader(GL.GL_FRAGMENT_SHADER)
        GL.glShaderSource(fragment_shader, fragment_src)
        GL.glCompileShader(fragment_shader)

        status = GL.glGetShaderiv(fragment_shader, GL.GL_COMPILE_STATUS)
        print("status:", status)
        log =  GL.glGetShaderInfoLog(vertex_shader)
        print("log:", log)

        shader_program = GL.glCreateProgram()
        GL.glAttachShader(shader_program, vertex_shader)
        GL.glAttachShader(shader_program, fragment_shader)
        GL.glBindFragDataLocation(shader_program, 0, "outColor")
        GL.glLinkProgram(shader_program)
        GL.glUseProgram(shader_program)

        status = GL.glGetProgramiv(shader_program, GL.GL_LINK_STATUS)
        print("Program status:", status)

        # Set color of faces
        color = GL.glGetUniformLocation(shader_program, "color")
        GL.glUniform3f(color, 1.0, 0.0, 0.0)


        coordinates = GL.glGetAttribLocation(shader_program, "coordinates")
        GL.glVertexAttribPointer(coordinates, 3, GL.GL_FLOAT, GL.GL_FALSE, 0, ctypes.c_void_p(0))
        GL.glEnableVertexAttribArray(coordinates)

        #GL.glDrawArrays(GL.GL_TRIANGLES, 0, 3)

        #GL.glOrtho(5.0, 5.0, 1.0, 5.0, 5.0, 5.0)

        #GLU.gluPerspective(45, 1, 0.1, 50.0)
        #GL.glTranslatef(0.0, 0.0, -5)

    def paint(self):
        GL.glClearColor(0, 0, 0, 1)
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
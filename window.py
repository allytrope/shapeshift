"""Create window, the starting point for executing Shapeshift."""

# Standard library imports
import struct
import sys

# Third-party imports
import moderngl
import moderngl_window as mglw
import numpy as np
from PIL import Image
from pyrr import Matrix44
from PySide6 import QtCore, QtGui, QtWidgets, QtOpenGLWidgets, QtOpenGL

# Local imports
from operations import Operations
import polyhedra


class ModernGLWidget(QtOpenGLWidgets.QOpenGLWidget):
#class ModernGLWidget(QtOpenGL.QOpenGLWindow):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        fmt = QtGui.QSurfaceFormat()
        fmt.setVersion(3, 3)
        fmt.setProfile(QtGui.QSurfaceFormat.CoreProfile)
        self.setFormat(fmt)
        self.resize(512, 512)

    def initializeGL(self):
        


        print(self.context)

    def resizeGL(self, width, height):
        print(width)
        print(height)
        #print(self.ctx.viewport)
        #self.ctx.viewport = (0, 0, width, height)
        print("inside resizeGL")

    def paintGL(self):
        #self.screen = self.ctx.detect_framebuffer()

        # self.prog = self.ctx.program(
        #     vertex_shader="""
        #         #version 330

        #         in vec3 in_vert;
        #         in vec3 in_color;

        #         out vec3 v_color;

        #         void main() {
        #             v_color = in_color;
        #             gl_Position = vec4(in_vert, 1.0);
        #         }
        #     """,
        #     fragment_shader="""
        #         #version 330

        #         in vec3 v_color;

        #         out vec4 out_color;

        #         void main() {
        #             out_color = vec4(v_color, 0.8);
        #         }
        #     """,
        # )

        #vertices = np.array([vertex.coordinates for vertex in self.parent.current_polyhedron.vertices], dtype="float32").flatten()
        #faces = np.array([face._vertices for face in self.parent.current_polyhedron.faces], dtype=np.uintc).flatten()
        #vbo = ctx.buffer(vertices.astype('f4').tobytes())

        #vertices = np.array([-0.4, 0.0, -1.0, 0.4, 0.0, -1.0])
        #vbo = ctx.buffer(vertices.astype('f4').tobytes())

        #vertices = np.array([
        #    0.0, 0.9, -0.5,
        #    -0.5, 0.0, -0.5,
        #    0.5, 0.0, -0.5
        #], dtype='f4')

        # vertices = np.array([
        #     0.0, 0.0, -1.0,

        #     -0.6, -0.8, -1.0,
        #     0.6, -0.8, -1.0,

        #     0.6, 0.8, -1.0,
        #     -0.6, 0.8, -1.0
        # ], dtype='f4')

        #indices = np.array([0, 1, 2, 0, 3, 4], dtype='i4')

        # put the array into a VBO
        #self.vbo = self.ctx.buffer(vertices)
        #self.ibo = self.ctx.buffer(indices)

        # use the VBO in a VAO
        #self.vao = self.ctx.vertex_array(
        #    self.prog,
        #    [
        #        (self.vbo, "3f", "in_vert"), # <---- the "2f" is the buffer format
        #    ],
        #    self.ibo
        #)
        #print("After vao")
        #self.makeCurrent()

        #self.vao = self.ctx.simple_vertex_array(self.prog, self.vbo, 'in_vert', 'in_color')



        self.ctx = moderngl.create_context()
        self.prog = self.ctx.program(vertex_shader="""
            #version 330
            uniform mat4 model;
            in vec2 in_vert;
            in vec3 in_color;
            out vec3 color;
            void main() {
                gl_Position = model * vec4(in_vert, 0.0, 1.0);
                color = in_color;
            }
            """,
            fragment_shader="""
            #version 330
            in vec3 color;
            out vec4 fragColor;
            void main() {
                fragColor = vec4(color, 1.0);
            }
        """)

        vertices = np.array([
            -0.6, -0.6,
            1.0, 0.0, 0.0,
            0.6, -0.6,
            0.0, 1.0, 0.0,
            0.0, 0.6,
            0.0, 0.0, 1.0,
        ], dtype='f4')

        vbo = self.ctx.buffer(vertices)
        self.vao = self.ctx.simple_vertex_array(self.prog, vbo, 'in_vert', 'in_color')
        #self.fbo = self.ctx.framebuffer(color_attachments=[self.ctx.texture((512, 512), 4)])
        print("inside paintGL")
        #self.fbo = self.ctx.simple_framebuffer((512, 512))
        #self.fbo.use()
        #print(self.defaultFramebufferObject)
        #self.ctx.clear(0.5, 0, 0.5, 0)
        #self.vao.render(moderngl.TRIANGLE_FAN)

        #if self.checkBox.isChecked() == True:
        #    for polyhedron in self.prior_polyhedra:
        #        graphics.draw(polyhedron)
        #graphics.rotate()

        #self.fbo.use()
        #self.fbo.clear(0.2, 0, 0.2, 0)
        self.prog['model'].write(Matrix44.from_eulers((0.0, 0.1, 0.0), dtype='f4'))
        self.vao.render(moderngl.TRIANGLES)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        print("first")
        super(MainWindow, self).__init__()
        self.setWindowTitle("Shapeshift")
        self.setGeometry(100, 100, 800, 500)

        self.prior_polyhedra = []
        self.set_current_polyhedron(polyhedra.Cube())
        #self.current_polyhedron = polyhedra.Cube()
        
    def setupUI(self):
        # Toolbar
        menubar = QtWidgets.QMenuBar()
        file_menu = QtWidgets.QMenu()
        file_menu.addAction("Open")
        menubar.addMenu(file_menu)

        #self.file.addAction
        menubar.addAction("Edit")
        menubar.addAction("View")
        menubar.addAction("Modify")
        menubar.addAction("Details")

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
        self.tab_2 = QtWidgets.QPushButton("2")

        # Create tab widget
        self.tab_widget = QtWidgets.QTabWidget()
        self.tab_widget.setMaximumWidth(300)
        
        self.tab_widget.addTab(self.tab_1, "Truncation")
        self.tab_widget.addTab(self.tab_2, "Augmentation")

        # Create horizontal box layout
        self.hbox = QtWidgets.QHBoxLayout()
        self.hbox.addWidget(self.tab_widget)

        # Create moderngl widget
        self.moderngl_widget = ModernGLWidget(self)
        self.hbox.addWidget(self.moderngl_widget)

        # Create central widget
        self.central_widget = QtWidgets.QWidget()
        self.central_widget.setLayout(self.hbox)
        self.setCentralWidget(self.central_widget)

        print("setupUI")

        # Connect operations to buttons
        self.truncate.clicked.connect(lambda: self.operations(Operations.truncate))
        self.rectify.clicked.connect(lambda: self.operations(Operations.rectify))
        self.facet.clicked.connect(lambda: self.operations(Operations.facet))
        self.dual.clicked.connect(lambda: self.operations(Operations.reciprocate))
        self.cap.clicked.connect(lambda: self.operations(Operations.cap))
        self.bridge.clicked.connect(lambda: self.operations(Operations.bridge))
        self.stellate.clicked.connect(lambda: self.operations(Operations.stellate))
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
        timer.start(30)
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
sys.exit(app.exec())

#mglw.run_window_config(WindowMGLW)
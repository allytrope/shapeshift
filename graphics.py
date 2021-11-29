"""Generate OpenGL graphics for visualizing polyhedra."""

# Standard library imports
from math import cos, sin, pi

# Third-party imports
import moderngl
import numpy as np
from pyrr import Matrix44, Quaternion
from PySide6 import QtGui, QtOpenGLWidgets


class ModernGLWidget(QtOpenGLWidgets.QOpenGLWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        fmt = QtGui.QSurfaceFormat()
        fmt.setVersion(3, 3)
        fmt.setProfile(QtGui.QSurfaceFormat.CoreProfile)
        self.setFormat(fmt)
        self.resize(512, 512)

    def initializeGL(self):
        pass

    def resizeGL(self, width, height):
        #print(self.ctx.viewport)
        #self.ctx.viewport = (0, 0, width, height)
        pass

    def paintGL(self):
        # Set up context and shaders
        self.ctx = moderngl.create_context()
        self.prog = self.ctx.program(vertex_shader="""
            #version 330
            uniform mat4 model;
            uniform vec3 color;
            in vec3 in_vert;
            out vec3 v_color;
            void main() {
                gl_Position = model * vec4(in_vert, 1.0);
                v_color = color;
            }
            """,
            fragment_shader="""
            #version 330
            in vec3 v_color;
            out vec4 f_color;
            void main() {
                f_color = vec4(v_color, 1.0);
            }
        """)

        # Set up vertices and faces
        vertices = np.array([vertex.coordinates for vertex in self.parent.current_polyhedron.vertices], dtype="f4").flatten()
        faces = np.array([face._vertices for face in self.parent.current_polyhedron.faces], dtype="i4")

        self.vbo = self.ctx.buffer(vertices)
        self.ibo = self.ctx.buffer(faces)

        # Use the VBO in a VAO
        self.vao = self.ctx.vertex_array(
            self.prog,
            [
                (self.vbo, "3f", "in_vert"),
            ],
            self.ibo
        )

        # Set uniforms
        self.prog['color'].value = (0.4, 0.5, 0)
        self.prog['model'].write(Matrix44.from_eulers((0.4, 0.2, 0.0), dtype='f4'))
        #q = Quaternion.from_y_rotation(np.pi / 2.0)
        #self.prog['y_rotation'].value =

        # Clear and render
        self.ctx.clear(0.2, 0, 0.2, 0)
        self.vao.render(moderngl.LINE_LOOP)

        #if self.checkBox.isChecked() == True:
        #    for polyhedron in self.prior_polyhedra:
        #        graphics.draw(polyhedron)
        #graphics.rotate()
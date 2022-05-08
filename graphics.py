"""Generate OpenGL graphics for visualizing polyhedra."""

# Third-party imports
import moderngl
import numpy as np
from pyrr import Matrix44, matrix44
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
        self.ctx.clear(0.2, 0, 0.2, 0)
        self.prog = self.ctx.program(vertex_shader="""
            #version 330
            uniform mat4 rotation;
            uniform mat4 zoom;
            in vec3 color;
            in vec3 in_vert;
            out vec3 v_color;
            void main() {
                gl_Position = zoom * rotation * vec4(in_vert, 1.0);
                v_color = color;
            }
            """,
            fragment_shader="""
            #version 330
            in vec3 v_color;
            out vec4 f_color;
            void main() {
                f_color = vec4(v_color, 1.0);
            }"""
        )

        self.edges_prog = self.ctx.program(vertex_shader="""
            #version 330
            uniform mat4 rotation;
            uniform mat4 zoom;
            uniform vec3 color;
            in vec3 in_vert;
            out vec3 v_color;
            void main() {
                gl_Position = zoom * rotation * vec4(in_vert, 1.0);
                v_color = color;
            }
            """,
            fragment_shader="""
            #version 330
            in vec3 v_color;
            out vec4 f_color;
            void main() {
                f_color = vec4(v_color, 1.0);
            }"""
        )

        if self.parent.show_edges_only.isChecked():
            draw_func = self.draw_edges
        else:
            draw_func = self.draw_polyhedron

        if self.parent.show_prior_polyhedra_checkbox.isChecked():
            # Draw all created polyhedra
            for model in self.parent.polytope_models:
                draw_func(model)
        else:
            # Draw last created polyhedron
            try:
                draw_func(self.parent.polytope_models[-1])
            # For when no created polyhedron exists
            except IndexError:
                pass

    def draw_polyhedron(self, model):
        """Draw polyhedron."""
        # Create VAOs for each face
        vaos = []
        for idx, face in enumerate(model.polytope.faces):
            positions = self.ctx.buffer(np.array([vertex.coordinates for vertex in face.vertices], dtype="f4").flatten())
            color = self.ctx.buffer(np.array(np.tile(model.color[idx], len(face)).flatten(), dtype="f4"))

            vao = self.ctx.vertex_array(
                self.prog,
                [
                    (positions, "3f", "in_vert"),
                    (color, "3f", "color")
                ]
            )
            vaos.append(vao)
            
        # Set uniforms
        x = self.parent.x_slider.value() / 20
        y = self.parent.y_slider.value() / 20
        z = self.parent.z_slider.value() / 20
        zoom = self.parent.zoom_slider.value() / 20
        self.prog["rotation"].write(Matrix44.from_eulers((x, y, z), dtype="f4"))
        self.prog["zoom"].write(matrix44.create_from_scale([zoom, zoom, zoom], dtype="f4"))

        # Render
        self.ctx.enable(moderngl.DEPTH_TEST)
        for vao in vaos:
            vao.render(moderngl.TRIANGLE_FAN)

    def draw_edges(self, model):
        vaos = []
        for face in model.polytope.faces:
            positions = self.ctx.buffer(np.array([vertex.coordinates for vertex in face.vertices], dtype="f4").flatten())

            vao = self.ctx.vertex_array(
                self.edges_prog,
                [
                    (positions, "3f", "in_vert"),
                ]
            )
            vaos.append(vao)
            
        # Set uniforms
        x = self.parent.x_slider.value() / 20
        y = self.parent.y_slider.value() / 20
        z = self.parent.z_slider.value() / 20
        zoom = self.parent.zoom_slider.value() / 20
        self.edges_prog["color"].value = model.color[0]
        self.edges_prog["rotation"].write(Matrix44.from_eulers((x, y, z), dtype="f4"))
        self.edges_prog["zoom"].write(matrix44.create_from_scale([zoom, zoom, zoom], dtype="f4"))

        # Render
        self.ctx.enable(moderngl.DEPTH_TEST)
        for vao in vaos:
            vao.render(moderngl.LINE_LOOP)

    def draw_faces(self):
        pass



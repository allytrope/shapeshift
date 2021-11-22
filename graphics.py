"""Generate OpenGL graphics for visualizing polyhedra."""

import ctypes
from OpenGL.raw.GL.VERSION.GL_1_5 import glBindBuffer
import glm
from math import cos, sin, pi
import numpy as np
import OpenGL.GL as GL

def setup(polyhedron):
    """Prepare shaders and projection matrices."""
    # Create VAO
    vertex_array = GL.glGenVertexArrays(1)
    GL.glBindVertexArray(vertex_array)

    # Set up vertex shader
    vertex_src = """
    #version 140

    in vec3 coordinates;

    uniform mat4 scale;
    uniform mat4 rotation;
    uniform mat4 y_rotation;

    void main()
    {
        gl_Position = scale * rotation * y_rotation * vec4(coordinates, 1.0);
    }
    """
    vertex_shader = GL.glCreateShader(GL.GL_VERTEX_SHADER)
    GL.glShaderSource(vertex_shader, vertex_src)
    GL.glCompileShader(vertex_shader)

    # Set up fragment shader
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

    # Set up prorgam
    shader_program = GL.glCreateProgram()
    GL.glAttachShader(shader_program, vertex_shader)
    GL.glAttachShader(shader_program, fragment_shader)
    GL.glBindFragDataLocation(shader_program, 0, "outColor")
    GL.glLinkProgram(shader_program)
    GL.glUseProgram(shader_program)

    # Check status of shaders and program
    status = GL.glGetShaderiv(vertex_shader, GL.GL_COMPILE_STATUS)
    print("status:", status)
    log =  GL.glGetShaderInfoLog(vertex_shader)
    print("log:", log)
    status = GL.glGetShaderiv(fragment_shader, GL.GL_COMPILE_STATUS)
    print("status:", status)
    log =  GL.glGetShaderInfoLog(vertex_shader)
    print("log:", log)
    status = GL.glGetProgramiv(shader_program, GL.GL_LINK_STATUS)
    print("Program status:", status)

    # Set color of faces
    color = GL.glGetUniformLocation(shader_program, "color")
    GL.glUniform3f(color, 1.0, 0.0, 0.0)

    # Set up projection matrices
    u_scale = GL.glGetUniformLocation(shader_program, "scale")
    u_rotation = GL.glGetUniformLocation(shader_program, "rotation")
    u_y_rotation = GL.glGetUniformLocation(shader_program,"y_rotation")
    
    scale = [0.5, 0.0, 0.0, 0.0,
              0.0, 0.5, 0.0, 0.0,
              0.0, 0.0, 0.5, 0.0,
              0.0, 0.0, 0.0, 1.0]
    theta = pi/8
    rotation = [1.0, 0.0, 0.0, 0.0,
                0.0, cos(theta) , -sin(theta), 0.0,
                0.0, sin(theta), cos(theta), 0.0,
                0.0, 0.0, 0.0, 1.0]
    iota = pi/4
    y_rotation = [1.0, cos(iota), sin(iota), 0.0,
                0.0, 0.0, 0.0, 0.0,
                0.0, -sin(iota), cos(iota), 0.0,
                0.0, 0.0, 0.0, 1.0]
    GL.glUniformMatrix4fv(u_scale, 1, GL.GL_FALSE, scale)
    GL.glUniformMatrix4fv(u_rotation, 1, GL.GL_FALSE, rotation)
    GL.glUniformMatrix4fv(u_y_rotation, 1, GL.GL_FALSE, y_rotation)

    # Set up vertices
    #vertices = [coordinate for coordinate in vertex for vertex in self.vertices]
    vertices = np.array([vertex.coordinates for vertex in polyhedron.vertices], dtype="float32").flatten()
    print("vertices:", vertices)
    vertex_buffer = GL.glGenBuffers(1)
    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, vertex_buffer)
    GL.glBufferData(GL.GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL.GL_DYNAMIC_DRAW)
    
    # Link vertex data to shader program
    coordinates = GL.glGetAttribLocation(shader_program, "coordinates")
    GL.glEnableVertexAttribArray(coordinates)
    GL.glVertexAttribPointer(coordinates, 3, GL.GL_FLOAT, GL.GL_FALSE, 0, ctypes.c_void_p(0))

    # Set up normals
    normal_buffer = GL.glGenBuffers(1)
    #GL.glBindBuffer(GL.GL_ARRAY_BUFFER, normal_buffer)
    #GL.glBufferData(GL.GL_ARRAY_BUFFER)

    #GL.glDrawArrays(GL.GL_TRIANGLES, 0, 3)
    #GL.glOrtho(5.0, 5.0, 1.0, 5.0, 5.0, 5.0)
    #GLU.gluPerspective(45, 1, 0.1, 50.0)
    #GL.glTranslatef(0.0, 0.0, -5)

def set_buffers(polyhedron):
    pass

def draw(polyhedron):
    """Draw polyhedron."""
    # Set up faces and draw
    #faces = []
    face_sizes = []
    faces_starts = []
    #element_count = 0
    for face in polyhedron.faces:
        #faces.append(face)
        faces_starts.append(2)
        face_sizes.append(len(face))
        #element_count += len(face)
    face_sizes = np.array(face_sizes)


    faces = np.array([face._vertices for face in polyhedron.faces], dtype=np.uintc).flatten()
    face_buffer = GL.glGenBuffers(1)
    GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, face_buffer)
    GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, faces.nbytes, faces, GL.GL_DYNAMIC_DRAW)

    #GL.glDrawArrays(GL.GL_TRIANGLE_FAN, 0, 3)
    #for face in polyhedron.faces:
    GL.glDrawElements(GL.GL_LINE_LOOP, 24, GL.GL_UNSIGNED_INT, None)
    #GL.glMultiDrawElements(GL.GL_LINE_LOOP, face_sizes, GL.GL_UNSIGNED_INT, None, len(polyhedron.faces))
    #GL.glMultiDrawArrays(GL.GL_LINE_LOOP, faces_starts, face_sizes, len(polyhedron.faces))

def draw_elements():
    pass


def rotate():
    GL.glRotatef(.2, .2, 1, .2)

def clear():
    """Clear screen."""
    GL.glClearColor(0, 0, 0, 1)
    GL.glClear(GL.GL_COLOR_BUFFER_BIT)
    #GL.glDrawArrays(GL.GL_TRIANGLE_FAN, 0, 3)
    GL.glRotated(3, 0, 0, 1)
    #print("GLerror: ", GL.glGetError())
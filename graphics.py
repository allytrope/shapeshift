"""Generate OpenGL graphics for visualizing polyhedra."""

import ctypes
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

    uniform mat4 trans;

    void main()
    {
        gl_Position = trans * vec4(coordinates, 1.0);
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
    trans = GL.glGetUniformLocation(shader_program, "trans")
    matrix = [1.0, 0.0, 0.0, 0.0,
                0.0, 1.0, 0.0, 0.0,
                0.0, 0.0, 1.0, 1.0,
                0.0, 0.0, 0.0, 1.0]
    GL.glUniformMatrix4fv(trans, 1, GL.GL_FALSE, matrix)

    # Set up vertices
    #vertices = [coordinate for coordinate in vertex for vertex in self.vertices]
    vertices = np.array([vertex.coordinates for vertex in polyhedron.vertices], dtype="float32").flatten()
    vertex_buffer = GL.glGenBuffers(1)
    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, vertex_buffer)
    GL.glBufferData(GL.GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL.GL_DYNAMIC_DRAW)
    
    # Link vertex data to shader program
    coordinates = GL.glGetAttribLocation(shader_program, "coordinates")
    GL.glEnableVertexAttribArray(coordinates)
    GL.glVertexAttribPointer(coordinates, 3, GL.GL_FLOAT, GL.GL_FALSE, 0, ctypes.c_void_p(0))

    #GL.glDrawArrays(GL.GL_TRIANGLES, 0, 3)
    #GL.glOrtho(5.0, 5.0, 1.0, 5.0, 5.0, 5.0)
    #GLU.gluPerspective(45, 1, 0.1, 50.0)
    #GL.glTranslatef(0.0, 0.0, -5)

def set_buffers(polyhedron):
    pass

    # Set up faces and draw
    #faces = np.array([face._vertices for face in polyhedron.faces], dtype=np.uint16).flatten()
    #face_buffer = GL.glGenBuffers(1)
    #GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, face_buffer)
    #GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, faces.nbytes, faces, GL.GL_STATIC_DRAW)
    #GL.glDrawElements(GL.GL_TRIANGLE_FAN, 4, GL.GL_UNSIGNED_INT, 0)


def draw(polyhedron):
    """Draw polyhedron."""
    GL.glDrawArrays(GL.GL_TRIANGLE_FAN, 0, 3)

   

def draw_elements():
    pass


def rotate():
    GL.glRotatef(.2, .2, 1, .2)

def clear():
    """Clear screen."""
    GL.glClearColor(0, 0, 0, 1)
    GL.glClear(GL.GL_COLOR_BUFFER_BIT)
    #GL.glDrawArrays(GL.GL_TRIANGLE_FAN, 0, 3)
    
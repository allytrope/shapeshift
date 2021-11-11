"""
Polyhedron class, operational methods, and built-in seed polyhedra.
Vertex and Face instances are contained within Polyhedron objects.
"""

# standard library imports
from ctypes import c_float
from functools import cached_property
from itertools import cycle, islice
import numpy as np
from random import randint
import weakref

# third-party imports
import OpenGL.GL as GL


class Vertex:
    """Representation of a vertex used in class Polyhedron."""
    def __init__(self, coordinates, neighbours=[], polyhedron=None, idx=None):
        self.idx = idx
        self.coordinates = coordinates
        self._neighbours = neighbours
        self.polyhedron = weakref.proxy(polyhedron)

    def __str__(self):
        return str(self.coordinates)

    def __len__(self):
        return len(self.coordinates)

    @cached_property
    def neighbours(self):
        return list(map(lambda index: self.polyhedron.vertices[index], self._neighbours))

    @cached_property
    def faces(self):
        # collect faces
        faces = [face for face in self.polyhedron.faces if self.idx in face._vertices]

        # order faces
        ordered_faces = [faces.pop()]
        while faces:
            for face in faces:
                for vertex in face.vertices:
                    if self.coordinates != vertex.coordinates:
                        if vertex in ordered_faces[-1].vertices:
                            ordered_faces.append(face)
                            faces.remove(face)
                            break

        return ordered_faces


class Face:
    """Representation of a face used in class Polyhedron."""
    def __init__(self, vertices, neighbours=[], polyhedron=None):
        self._vertices = vertices
        self._neighbours = neighbours
        self.polyhedron = weakref.proxy(polyhedron)

    def __str__(self):
        return str(self.vertices)

    def __len__(self):
        return len(self.vertices)

    @cached_property
    def vertices(self):
        return list(map(lambda index: self.polyhedron.vertices[index], self._vertices))

    # return number of undirected edges
    @cached_property
    def edges(self):
        forward = [(self.vertices[i - 1], self.vertices[i]) for i in range(len(self.vertices))]
        reverse = [(self.vertices[i], self.vertices[i - 1]) for i in range(len(self.vertices))]
        return forward + reverse

    # return faces that share an edge with self
    @cached_property
    def neighbours(self):
        neighbour_faces = []
        for face in self.polyhedron.faces:
            for edge in face.edges:
                if face != self:
                    if edge in self.edges and face not in neighbour_faces:
                        neighbour_faces.append(face)
        return neighbour_faces


class Polyhedron:
    """Store polyhedron attributes and provide operational methods to transform polyhedra."""
    def __init__(self, vertices, faces):
        # cast vertices to type Vertex
        if type(vertices[0]) != Vertex:
            self.vertices = list(map(lambda vertex: Vertex(vertex, polyhedron=self, idx=vertices.index(vertex)), vertices))
        else:
            self.vertices = vertices

        # cast faces to type Face
        if type(faces[0]) != Face:
            self.faces = list(map(lambda face: Face(face, polyhedron=self), faces))
        else:
            self.faces = faces

        # create adjacency list for vertices using Descartes-Euler Polyhedron Formula
        edges = [[] for i in range(len(vertices) + len(faces) - 2)]
        for face in self.faces:
            for x in range(len(face.vertices)):
                edges[face._vertices[x - 1]].append(face._vertices[x])
                edges[face._vertices[x]].append(face._vertices[x - 1])

        # assign neighbours to each vertex
        for vertex, neighbours in zip(self.vertices, edges):
            vertex._neighbours = neighbours

        # determine color of the polyhedron
        self.randomize_color()

    def randomize_color(self):
        """Change RGB color of polyhedron."""
        self.color1 = randint(2,10)/10
        self.color2 = randint(2,10)/10
        self.color3 = randint(2,10)/10

    def stats(self):
        """Print number of vertices, edges, and faces."""
        print("Vertices:", len(self.vertices))
        print("Edges:", sum([len(face.vertices) for face in self.faces])//2)
        print("Faces:", len(self.faces))

    def full_stats(self):
        """Print array representations of vertices, edges, and faces."""
        print("Vertices:\n", [vertex.coordinates for vertex in self.vertices])
        #print("Edges:\n", self.edges)
        print("Faces:\n", [[vertex.idx for vertex in face.vertices] for face in self.faces])

    def face_types(self):
        """Print counts of each n-gon."""
        polygon_names = {3:"triangles", 4:"quadrilaterals", 5:"pentagons", 6:"hexagons", 7:"heptagons",
                        8:"octagons", 9:"nonagons", 10:"decagons", 11:"undecagons", 12:"dodecagons"}
        polygon_counts = {}
        for face in self.faces:
            if len(face.vertices) in polygon_counts:
                polygon_counts[len(face.vertices)] += 1
            else:
                polygon_counts[len(face.vertices)] = 1
        for key, value in polygon_counts.items():
                if key in polygon_names:
                    print(f"{polygon_names[key]}: {value}")
                else:
                    print(f"{key}-gon: {value}")

    def draw_faces(self):
        """"Draw faces with OpenGL."""

        '''
        GL.glBegin(GL.GL_LINES)
        for face in self.faces:
            offset_cycle = islice(cycle(face.vertices), 1, None)
            for vertex, neighbour in zip(face.vertices, offset_cycle):
                GL.glColor3f(self.color1, self.color2, self.color3)
                GL.glVertex3fv(vertex.coordinates)
                GL.glVertex3fv(neighbour.coordinates)
        GL.glEnd()
        '''
    
    def draw_edges(self):
        #vertices = [coordinate for coordinate in vertex for vertex in self.vertices]
        vertices = np.array([vertex.coordinates for vertex in self.vertices], dtype="float32").flatten()
        #print("vertices=", vertices)
        #vertices_arr = (c_float * len(vertices))(*vertices)
        #print(vertices_arr)


        buffer = GL.glGenBuffers(1)
        #GL.glBindBuffer(GL.GL_ARRAY_BUFFER, buffer)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, vertices, GL.GL_DYNAMIC_DRAW)
        


        faces = np.array([face._vertices for face in self.faces], dtype=np.uint16).flatten()
        face_buffer = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, face_buffer)
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, faces.nbytes, faces, GL.GL_STATIC_DRAW)
        GL.glDrawArrays(GL.GL_TRIANGLE_FAN, 0, 3)



        '''
        GL.glBegin(GL.GL_LINES)
        for face in self.faces:
            offset_cycle = islice(cycle(face.vertices), 1, None)
            for vertex, neighbour in zip(face.vertices, offset_cycle):
                GL.glColor3f(self.color1, self.color2, self.color3)
                GL.glVertex3fv(vertex.coordinates)
                GL.glVertex3fv(neighbour.coordinates)
        GL.glEnd()
        '''

PHI = (1 + 5**0.5)/2

class Tetrahedron(Polyhedron):
    def __init__(self):
        vertices = [(1, 1, 1), (-1, -1, 1), (-1, 1, -1), (1, -1, -1)]
        faces = [[0, 1, 2], [0, 2, 3], [0, 1, 3], [1, 2, 3]]
        super().__init__(vertices, faces)


class Cube(Polyhedron):
    def __init__(self):
        vertices = [(0.8, 1.0, 1.0), (1.0, 1.0, -1.0), (1.0, -1.0, -1.0), (1.0, -1.0, 1.0), (-1.0, -1.0, 1.0), (-1.0, -1.0, -1.0), (-1.0, 1.0, -1.0),(-1.0, 1.0, 1.0)]
        faces = [[0, 1, 2, 3], [0, 1, 6, 7], [0, 3, 4, 7], [4, 5, 6, 7], [4, 5, 2, 3], [1, 2, 5, 6]]
        super().__init__(vertices, faces)


class Octahedron(Polyhedron):
    def __init__(self):
        vertices = [(0, 1, 0), (1, 0, 0), (0, 0, 1), (-1, 0, 0), (0, 0, -1), (0, -1, 0)]
        faces = [[0, 1, 4], [0, 1, 2], [0, 2, 3], [0, 3, 4], [1, 4, 5], [1, 2, 5], [2, 3, 5], [3, 4, 5]]
        super().__init__(vertices, faces)


class Dodecahedron(Polyhedron):
    def __init__(self):
        vertices = [(1, 1, 1), (1, 1, -1), (1, -1, 1), (-1, 1, 1), (-1, 1, -1), (-1, -1, 1), (1, -1, -1), (-1, -1, -1),
                    (0, PHI, 1/PHI), (0, PHI, -1/PHI), (0, -PHI, 1/PHI), (0, -PHI, -1/PHI), (1/PHI, 0, PHI), (1/PHI, 0, -PHI),
                    (-1/PHI, 0, PHI), (-1/PHI, 0, -PHI), (PHI, 1/PHI, 0), (PHI, -1/PHI, 0), (-PHI, 1/PHI, 0), (-PHI, -1/PHI, 0)]
        faces = [[14, 12, 2, 10, 5], [12, 0, 16, 17, 2], [2, 17, 6, 11, 10], [5, 10, 11, 7, 19], [17, 16, 1, 13, 6], [6, 13, 15, 7, 11], 
                 [14, 3, 18, 19, 5], [14, 12, 0, 8, 3], [3, 8, 9, 4, 18], [19, 18, 4, 15, 7], [8, 0, 16, 1, 9], [9, 1, 13, 15, 4]]
        super().__init__(vertices, faces)


class Icosahedron(Polyhedron):
    def __init__(self):
        vertices = [(0, 1, PHI), (0, 1, -PHI), (0, -1, PHI), (0, -1, -PHI),
                    (1, PHI, 0), (1, -PHI, 0), (-1, PHI, 0), (-1, -PHI, 0),
                    (PHI, 0, 1), (PHI, 0, -1), (-PHI, 0, 1), (-PHI, 0, -1)]
        faces = [[4, 0, 6], [4, 6, 1], [1, 11, 6], [6, 11, 10], [6, 10, 0],
                 [3, 1, 11], [3, 11, 7], [3, 7, 5], [3, 5, 9], [3, 9, 1],
                 [10, 11, 7], [1, 4, 9], [2, 8, 5], [5, 8, 9], [2, 5, 7],
                 [0, 4, 8], [0, 2, 8], [0, 2, 10], [2, 7, 10], [4, 8, 9]]
        super().__init__(vertices, faces)
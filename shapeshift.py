"""
Polyhedron class, containing operational methods, and built-in base polyhedra.
Vertex and Face instances are contained within Polyhedron objects.
"""

# standard library imports
from functools import reduce
from itertools import cycle, islice
from math import isclose
from random import randint

# third-party imports
import OpenGL.GL as GL


class Vertex:
    """Representation of a vertex used in class Polyhedron."""
    def __init__(self, coordinates, neighbours=[], polyhedron=None, idx=None):
        self.idx = idx
        self.coordinates = coordinates
        self._neighbours = neighbours
        self.polyhedron = polyhedron

    def __str__(self):
        return str(self.coordinates)

    @property
    def neighbours(self):
        return list(map(lambda index: self.polyhedron.vertices[index], self._neighbours))

    @property
    def faces(self):
        return [face for face in self.polyhedron.faces if self.idx in face._vertices]

class Face:
    """Representation of a face used in class Polyhedron."""
    def __init__(self, vertices, neighbours=[], polyhedron=None):
        self._vertices = vertices
        self._neighbours = neighbours
        self.polyhedron = polyhedron

    def __str__(self):
        return str(self.vertices)

    @property
    def vertices(self):
        return list(map(lambda index: self.polyhedron.vertices[index], self._vertices))

    @property
    def neighbours(self):
        return list(map(lambda index: self.polyhedron.vertices[index], self._neighbours))


class Polyhedron:
    """Store polyhedron attributes and provide operational methods to transform polyhedra."""

    def __init__(self, vertices, faces):
        # cast vertices to type Vertex
        if type(vertices) != Vertex:
            self.vertices = list(map(lambda vertex: Vertex(vertex, polyhedron=self, idx=vertices.index(vertex)), vertices))
        else:
            self.vertices = vertices

        # cast faces to type Face
        if type(faces) != Face:
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
        #edge_count = reduce(lambda x, y: len(x.neighbours) + len(y.neighbours), self.vertices)/2
        #print("Edges:", edge_count)
        print("Faces:", len(self.faces))

    def full_stats(self):
        """Print array representations of vertices, edges, and faces."""
        print("Vertices:\n", self.vertices)
        #print("Edges:\n", self.edges)
        print("Faces:\n", self.faces)

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
    '''
    def draw_vertices(self):
        pass
    
    def draw_edges(self):
        """Draw edges with OpenGL."""
        GL.glBegin(GL.GL_LINES)
        for group in enumerate(self.edges):
            for neighbour in group[1]:
                if group[0] < neighbour:
                    GL.glColor3f(self.color1, self.color2, self.color3)
                    GL.glVertex3fv(self.vertices[group[0]])
                    GL.glVertex3fv(self.vertices[neighbour])
        GL.glEnd()
    '''

    def draw_faces(self):
        """"Draw faces with OpenGL."""
        GL.glBegin(GL.GL_LINES)
        for face in self.faces:
            offset_cycle = islice(cycle(face.vertices), 1, None)
            for vertex, neighbour in zip(face.vertices, offset_cycle):
                #print(f"{vertex.coordinates=} {neighbour.coordinates=}")
                GL.glColor3f(self.color1, self.color2, self.color3)
                GL.glVertex3fv(vertex.coordinates)
                GL.glVertex3fv(neighbour.coordinates)
        GL.glEnd()

    def __find_float_in_list(self, query_vertex, vertices):
        """Find close vertex; otherwise, return orignal vertex"""
        for vertex in vertices:
            if isclose(query_vertex[0], vertex[0]):
                if isclose(query_vertex[1], vertex[1]):
                    if isclose(query_vertex[2], vertex[2]):
                        return True, vertex
        return False, query_vertex

    def diminish(self, func, vertex, new_vertices=[]):
        """Remove pyramid off polyhedron where apex is a vertex on the polyhedron.
        Takes a func to determine how base of pyramid is formed.
        Used in rectify() and truncate().
        """
        # create new faces (new faces derived from previous vertices)
        unordered_face = []
        for neighbour in vertex.neighbours:
            midpoint = func(vertex.coordinates, neighbour.coordinates)
            unordered_face.append((midpoint, neighbour))

        # find edges by comparing endpoint faces
        edges = []
        for midpoint1, endpoint1 in unordered_face:
            for midpoint2, endpoint2 in unordered_face:
                if midpoint1 != midpoint2:
                    for end_face in endpoint1.faces:
                        if end_face in endpoint2.faces:
                            edges.append((midpoint1, midpoint2))

        # order vertices in face
        face_vertices = [edges[0][0]]
        for _ in edges:
            for edge in edges:
                if edge[0] == face_vertices[-1] and edge[1] not in face_vertices:
                    face_vertices.append(edge[1])
                    break
        
        # create new faces and vertices
        new_face = []
        for vertex in face_vertices:
            index = new_vertices.index(vertex)
            new_face.append(index)
        return new_face
    
    def rectify(self):
        """Perform rectification operation. Cleave vertices by marking midpoints as new vertices."""
        print("Rectifying")

        def find_midpoint(vertex1, vertex2):
            return ((vertex1[0] + vertex2[0])/2,  # x coordinate
                    (vertex1[1] + vertex2[1])/2,  # y coordinate
                    (vertex1[2] + vertex2[2])/2)  # z coordinate

        # arrays for new polyhedron's vertices, edges, and faces
        new_vertices = []
        new_faces = []

        # create rectified faces (new faces derived from previous faces)
        for face in self.faces:
            new_face = []

            # find new vertices
            offset_cycle = islice(cycle(face.vertices), 1, None)
            for vertex, neighbour in zip(face.vertices, offset_cycle):
                midpoint = find_midpoint(vertex.coordinates, neighbour.coordinates)

                # test if midpoint is already in new_vertices, and if not, to add it
                try:
                    index = new_vertices.index(midpoint)
                    new_face.append(index)
                except ValueError:
                    new_vertices.append(midpoint)
                    new_face.append(len(new_vertices) - 1)
            new_faces.append(new_face)
        
        # create new faces (new faces derived from previous vertices)
        for vertex in self.vertices:
            new_face = self.diminish(find_midpoint, vertex, new_vertices=new_vertices)
            new_faces.append(new_face)

        return Polyhedron(new_vertices, new_faces)

    def truncate(self):
        """Perform truncation operation. Cleave vertices by marking 1/3rd and 2/3rds of each edge as new vertices."""
        print("Truncating")
        def find_third(vertex1, vertex2):
            return ((vertex1[0]*2/3 + vertex2[0]/3),  # x coordinate
                    (vertex1[1]*2/3 + vertex2[1]/3),  # y coordinate
                    (vertex1[2]*2/3 + vertex2[2]/3))  # z coordinate

        new_vertices = []
        new_faces = []

        # create truncated faces (new faces derived from previous faces)
        for face in self.faces:
            new_face = []

            # create new vertices and faces
            for x in range(len(face.vertices)):
                coordinates1 = face.vertices[x - 1].coordinates
                coordinates2 = face.vertices[x].coordinates
                third_forward = find_third(coordinates1, coordinates2)
                third_backward = find_third(coordinates2, coordinates1)
                is_in_list, third_forward = self.__find_float_in_list(third_forward, new_vertices)
                if is_in_list == False:
                    new_vertices.append(third_forward)
                is_in_list, third_backward = self.__find_float_in_list(third_backward, new_vertices)
                if is_in_list == False:
                    new_vertices.append(third_backward)
                new_face.append(new_vertices.index(third_forward))
                new_face.append(new_vertices.index(third_backward))
            new_faces.append(new_face)

        # create new faces (new faces derived from previous vertices)
        for vertex in self.vertices:
            new_face = self.diminish(find_third, vertex, new_vertices=new_vertices)
            new_faces.append(new_face)

        return Polyhedron(new_vertices, new_faces)

    def dual(self):
        """Perform dual operation. Convert center of each face into a vertex to generate """
        print("Dual function is under development")
        def find_centroid(face):
            pass
  
    def stellate(self):
        print("Stellation function is under development")


Tetrahedron = Polyhedron(
    [(1, 1, 1), (-1, -1, 1), (-1, 1, -1), (1, -1, -1)],  # vertices
    #[[1, 2, 3], [0, 2, 3], [0, 1, 3], [0, 1, 2]],  # edges as adjacency matrix of vertices
    [[0, 1, 2], [0, 2, 3], [0, 1, 3], [1, 2, 3]]  # faces as path defined by vertices
    )

Cube = Polyhedron(
    [(1, 1, 1), (1, 1, -1), (1, -1, -1), (1, -1, 1), (-1, -1, 1), (-1, -1, -1), (-1, 1, -1),(-1, 1, 1)],
    #[[1, 3, 7], [0, 2, 6], [1, 3, 5], [2, 4, 0] ,[3, 5, 7] ,[4, 6, 2] ,[5, 7, 1], [6, 0, 4]],
    [[0, 1, 2, 3], [0, 1, 6, 7], [0, 3, 4, 7], [4, 5, 6, 7], [4, 5, 2, 3], [1, 2, 5, 6]]
    )

Octahedron = Polyhedron(
    [(0, 1, 0), (1, 0, 0), (0, 0, 1), (-1, 0, 0), (0, 0, -1), (0, -1, 0)],
    #[[1, 2, 3, 4], [0, 2, 4, 5], [0, 1, 3, 5], [0, 2, 4, 5], [0, 1, 3, 5], [1, 2, 3, 4]],
    [[0, 1, 4], [0, 1, 2], [0, 2, 3], [0, 3, 4], [1, 4, 5], [1, 2, 5], [2, 3, 5], [3, 4, 5]]
    )

phi = (1 + 5**0.5)/2

Dodecahedron = Polyhedron(
    [(1, 1, 1), (1, 1, -1), (1, -1, 1), (-1, 1, 1), (-1, 1, -1), (-1, -1, 1), (1, -1, -1), (-1, -1, -1),  # 0 through 7
    (0, phi, 1/phi), (0, phi, -1/phi), (0, -phi, 1/phi), (0, -phi, -1/phi), (1/phi, 0, phi), (1/phi, 0, -phi),  # 8 through 13
    (-1/phi, 0, phi), (-1/phi, 0, -phi), (phi, 1/phi, 0), (phi, -1/phi, 0), (-phi, 1/phi, 0), (-phi, -1/phi, 0)],  # 14 through 19
    #[[12, 8, 16], [16, 9, 13], [12, 17, 10], [14, 8, 18], [9, 15, 18],  # 0 through 4
    #[14, 10, 19], [17, 13, 11], [11, 15, 19], [0, 9, 3], [8, 1, 4],  # 5 through 9
    #[2, 11, 5], [10, 6, 7], [0, 2, 14], [1, 6, 15], [12, 3, 5],  # 10 through 14
    #[4, 13, 7], [0, 1, 17], [16, 6, 2], [3, 4, 19], [5, 18, 7]],  # 15 through 19
    [[14, 12, 2, 10, 5], [12, 0, 16, 17, 2], [2, 17, 6, 11, 10], [5, 10, 11, 7, 19], [17, 16, 1, 13, 6], [6, 13, 15, 7, 11], 
    [14, 3, 18, 19, 5], [14, 12, 0, 8, 3], [3, 8, 9, 4, 18], [19, 18, 4, 15, 7], [8, 0, 16, 1, 9], [9, 1, 13, 15, 4]]
    )

Icosahedron = Polyhedron(
    [(0, 1, phi), (0, 1, -phi), (0, -1, phi), (0, -1, -phi),  # 0 through 3
    (1, phi, 0), (1, -phi, 0), (-1, phi, 0), (-1, -phi, 0),  # 4 through 7
    (phi, 0, 1), (phi, 0, -1), (-phi, 0, 1), (-phi, 0, -1)],  # 8 through 11
    #[[10, 6, 4, 8, 2], [4, 9, 3, 11, 6], [8, 5, 7, 0, 10], [1, 9, 5, 11, 7],
    #[0, 6, 1, 9, 8], [7, 3, 9, 2, 8], [0, 4, 1, 11, 10], [3, 5, 11, 2, 10],
    #[2, 5, 9, 0, 4], [3, 5, 1, 4, 8], [6, 2, 0, 11, 7], [1, 6, 10, 3, 7]],
    [[4, 0, 6], [4, 6, 1], [1, 11, 6], [6, 11, 10], [6, 10, 0],
    [3, 1, 11], [3, 11, 7], [3, 7, 5], [3, 5, 9], [3, 9, 1],
    [10, 11, 7], [1, 4, 9], [2, 8, 5], [5, 8, 9], [2, 5, 7],
    [0, 4, 8], [0, 2, 8], [0, 2, 10], [2, 7, 10], [4, 8, 9]]
    )
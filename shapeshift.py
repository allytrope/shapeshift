"""
Polyhedron class, containing operational methods, and built-in base polyhedra.
"""

# standard library imports
from random import randint
from math import isclose

# third-party imports
from numpy import dot, arccos
from numpy.linalg import norm
import OpenGL.GL as GL


class Polyhedron:
    """Store polyhedron attributes and provide operational methods to transform polyhedra."""

    def __init__(self, vertices, edges, faces):
        self.vertices = vertices  # list of tuples: [(x, y, z), (x, y, z)...]
        self.edges = edges  # primary index is one vertex and the list's entry is other
        self.faces = faces  # ordered lists of vertex indices
        
        # determines color of the polyhedron
        self.color1 = randint(2,10)/10
        self.color2 = randint(2,10)/10
        self.color3 = randint(2,10)/10

    def stats(self):
        """Print number of vertices, edges, and faces."""
        print("Vertices:", len(self.vertices))
        directed_edges = 0
        for group in self.edges:
            directed_edges += len(group)
        undirected_edges = directed_edges//2
        print("Edges:", undirected_edges)
        print("Faces:", len(self.faces))

    def full_stats(self):
        """Print array representations of vertices, edges, and faces."""
        print("Vertices:\n")
        print("Edges:\n", self.edges)
        print("Faces:\n", self.faces)

    def face_types(self):
        """Print counts of each n-gon."""
        polygon_names = {3:"triangles", 4:"quadrilaterals", 5:"pentagons", 6:"hexagons", 7:"heptagons",
                        8:"octagons", 9:"nonagons", 10:"decagons", 11:"undecagons", 12:"dodecagons"}
        polygon_counts = {}
        for face in self.faces:
            if len(face) in polygon_counts:
                polygon_counts[len(face)] += 1
            else:
                polygon_counts[len(face)] = 1
        for key, value in polygon_counts.items():
                if key in polygon_names:
                    print(f"{polygon_names[key]}: {value}")
                else:
                    print(f"{key}-gon: {value}")

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

    def draw_faces(self):
        """"Draw faces with OpenGL."""
        GL.glBegin(GL.GL_LINES)
        for face in self.faces:
            for i in range(len(face)):
                #if face[i-1] > face[i]:
                GL.glVertex3fv(self.vertices[face[i - 1]])
                GL.glVertex3fv(self.vertices[face[i]])
        GL.glEnd()

    # used in rectify() and truncate()
    def __convex_hull(self, vertices):
        ordered_vertices = [vertices[0]]  # index corresponds to index in angles
        while len(ordered_vertices) != len(vertices):
            tested_vertices = []  # index corresponds to index in angles
            angles = []  # index corresponds to index in tested_vertices
            for vertex in vertices:
                if vertex not in (ordered_vertices or tested_vertices):
                    vector1 = ordered_vertices[-1]
                    vector2 = vertex
                    #finds angle between vertices[0] and other vertex
                    angle = arccos(dot(vector1, vector2)/(norm(vector1)*norm(vector2)))
                    tested_vertices.append(vertex)
                    angles.append(angle)
            # adds vertex with smallest angle
            index = angles.index(min(angles))
            ordered_vertices.append(tested_vertices[index])  # adds next vertex in order
        return ordered_vertices

    # finds close vertex; otherwise, returns orignal vertex
    def __find_float_in_list(self, query_vertex, vertices):
        for vertex in vertices:
            if isclose(query_vertex[0], vertex[0]):
                if isclose(query_vertex[1], vertex[1]):
                    if isclose(query_vertex[2], vertex[2]):
                        return True, vertex
        return False, query_vertex

    def rectify(self):
        """Perform rectification operation. Cleave vertices by marking midpoints as new vertices."""
        print("Rectifying")
        def find_midpoint(given_edge):
            new_vertex = ((self.vertices[given_edge[0]][0] + self.vertices[given_edge[1]][0])/2,  # x coordinate
                          (self.vertices[given_edge[0]][1] + self.vertices[given_edge[1]][1])/2,  # y coordinate
                          (self.vertices[given_edge[0]][2] + self.vertices[given_edge[1]][2])/2)  # z coordinate
            return new_vertex

        # arrays for new polyhedron's vertices, edges, and faces
        new_vertices = []
        prev_edges_count = 0
        for face in self.faces:
            prev_edges_count += len(face)
        prev_edges_count //= 2
        new_edges = [[] for i in range(prev_edges_count)]
        new_faces = []

        # creates rectified faces (new faces derived from previous faces)
        for face in self.faces:
            new_face = []
            # creates new vertices and faces
            for x in range(len(face)):  # x acts as counter
                edge = [face[x - 1], face[x]]
                midpoint = find_midpoint(edge)
                if midpoint not in new_vertices:
                    new_vertices.append(midpoint)
                new_face.append(new_vertices.index(midpoint))
            new_faces.append(new_face)
            # creates new edges
            for x in range(len(new_face)):
                new_edges[new_face[x - 1]].append(new_face[x])
                new_edges[new_face[x]].append(new_face[x - 1])

        # creates new faces (new faces derived from previous vertices)
        for vertex_index in range(len(self.vertices)):  # vertex_index = 0, 1, 2, ... n
            face = []
            for neighbour in self.edges[vertex_index]:
                edge = [neighbour, vertex_index]
                midpoint = find_midpoint(edge)
                face.append(new_vertices.index(midpoint))
            unordered = []
            # orders vertices of face
            for vertex_index in face:
                unordered.append(new_vertices[vertex_index])
            ordered = self.__convex_hull(unordered)
            ordered_indexed = []
            # converts vertices to corresponding indices
            for vertex in ordered:
                ordered_indexed.append(new_vertices.index(vertex))
            new_faces.append(ordered_indexed)
        return Polyhedron(new_vertices, new_edges, new_faces)

    def truncate(self):
        """Perform truncation operation. Cleaves vertices by marking 1/3rd and 2/3rds of each edge as new vertices."""
        print("Truncating")
        def find_third(given_edge):
            new_vertex = ((self.vertices[given_edge[0]][0]/3 + self.vertices[given_edge[1]][0]*2/3),  # x coordinate
                          (self.vertices[given_edge[0]][1]/3 + self.vertices[given_edge[1]][1]*2/3),  # y coordinate
                          (self.vertices[given_edge[0]][2]/3 + self.vertices[given_edge[1]][2]*2/3))  # z coordinate
            return new_vertex

        new_vertices = []
        prev_edges_count = 0
        for edge_group in self.edges:
            prev_edges_count += len(edge_group)
        
        new_edges = [[] for i in range(prev_edges_count)]
        new_faces = []

        # creates truncated faces (new faces derived from previous faces)
        for face in self.faces:
            new_face = []
            # creates new vertices and faces
            for x in range(len(face)):
                edge_forward = [face[x], face[x - 1]]
                edge_backward = [face[x - 1], face[x]]
                third_forward = find_third(edge_forward)
                third_backward = find_third(edge_backward)
                is_in_list, third_forward = self.__find_float_in_list(third_forward, new_vertices)
                if is_in_list == False:
                    new_vertices.append(third_forward)
                is_in_list, third_backward = self.__find_float_in_list(third_backward, new_vertices)
                if is_in_list == False:
                    new_vertices.append(third_backward)
                new_face.append(new_vertices.index(third_forward))
                new_face.append(new_vertices.index(third_backward))
            new_faces.append(new_face)
            # creates new edges
            for x in range(len(new_face)):
                if new_face[x] not in new_edges[new_face[x - 1]]:
                    new_edges[new_face[x - 1]].append(new_face[x])
                if new_face[x - 1] not in new_edges[new_face[x]]:
                    new_edges[new_face[x]].append(new_face[x - 1])
        
        # creates new faces (new faces derived from previous vertices)
        for vertex_index in range(len(self.vertices)):  # vertex_index = 0, 1, 2, ... n
            face = []
            for neighbour in self.edges[vertex_index]:
                edge = [neighbour, vertex_index]
                third = find_third(edge)
                face.append(new_vertices.index(third))
            unordered = []
            # orders vertices of face
            for vertex_index in face:
                unordered.append(new_vertices[vertex_index])
            ordered = self.__convex_hull(unordered)
            ordered_indexed = []
            # converts vertices to corresponding indices
            for vertex in ordered:
                ordered_indexed.append(new_vertices.index(vertex))
            new_faces.append(ordered_indexed)
        return Polyhedron(new_vertices, new_edges, new_faces)

    def dual(self):
        """Perform dual operation. Convert center of each face into a vertex to generate """
        print("Dual function is under development")
        def find_centroid(face):
            for vertex in face:
                pass
        for face in self.faces:
            for vertex_index in range(len(self.faces)):
                edge_forward = [self.face[vertex_index - 1], self.face[vertex_index]]
                edge_backward = [self.face[vertex_index], self.face[vertex_index - 1]]
            centroid = find_centroid(face)


    def stellate(self):
        print("Stellation function is under development")

    def greatening(self):
        pass


        new_vertices = self.vertices
        new_edges = self.edges
        new_faces = self.faces
        return Polyhedron(new_vertices, new_edges, new_faces)

Tetrahedron = Polyhedron(
    [(1, 1, 1), (-1, -1, 1), (-1, 1, -1), (1, -1, -1)],  # vertices
    [[1, 2, 3], [0, 2, 3], [0, 1, 3], [0, 1, 2]],  # edges as adjacency matrix of vertices
    [[0, 1, 2], [0, 2, 3], [0, 1, 3], [1, 2, 3]]  # faces as path defined by vertices
    )

Cube = Polyhedron(
    [(1, 1, 1), (1, 1, -1), (1, -1, -1), (1, -1, 1), (-1, -1, 1), (-1, -1, -1), (-1, 1, -1),(-1, 1, 1)],
    [[1, 3, 7], [0, 2, 6], [1, 3, 5], [2, 4, 0] ,[3, 5, 7] ,[4, 6, 2] ,[5, 7, 1], [6, 0, 4]],
    [[0, 1, 2, 3], [0, 1, 6, 7], [0, 3, 4, 7], [4, 5, 6, 7], [4, 5, 2, 3], [1, 2, 5, 6]]
    )

Octahedron = Polyhedron(
    [(0, 1, 0), (1, 0, 0), (0, 0, 1), (-1, 0, 0), (0, 0, -1), (0, -1, 0)],
    [[1, 2, 3, 4], [0, 2, 4, 5], [0, 1, 3, 5], [0, 2, 4, 5], [0, 1, 3, 5], [1, 2, 3, 4]],
    [[0, 1, 4], [0, 1, 2], [0, 2, 3], [0, 3, 4], [1, 4, 5], [1, 2, 5], [2, 3, 5], [3, 4, 5]]
    )

phi = (1 + 5**0.5)/2

Dodecahedron = Polyhedron(
    [(1, 1, 1), (1, 1, -1), (1, -1, 1), (-1, 1, 1), (-1, 1, -1), (-1, -1, 1), (1, -1, -1), (-1, -1, -1),  # 0 through 7
    (0, phi, 1/phi), (0, phi, -1/phi), (0, -phi, 1/phi), (0, -phi, -1/phi), (1/phi, 0, phi), (1/phi, 0, -phi),  # 8 through 13
    (-1/phi, 0, phi), (-1/phi, 0, -phi), (phi, 1/phi, 0), (phi, -1/phi, 0), (-phi, 1/phi, 0), (-phi, -1/phi, 0)],  # 14 through 19
    [[12, 8, 16], [16, 9, 13], [12, 17, 10], [14, 8, 18], [9, 15, 18],  # 0 through 4
    [14, 10, 19], [17, 13, 11], [11, 15, 19], [0, 9, 3], [8, 1, 4],  # 5 through 9
    [2, 11, 5], [10, 6, 7], [0, 2, 14], [1, 6, 15], [12, 3, 5],  # 10 through 14
    [4, 13, 7], [0, 1, 17], [16, 6, 2], [3, 4, 19], [5, 18, 7]],  # 15 through 19
    [[14, 12, 2, 10, 5], [12, 0, 16, 17, 2], [2, 17, 6, 11, 10], [5, 10, 11, 7, 19], [17, 16, 1, 13, 6], [6, 13, 15, 7, 11], 
    [14, 3, 18, 19, 5], [14, 12, 0, 8, 3], [3, 8, 9, 4, 18], [19, 18, 4, 15, 7], [8, 0, 16, 1, 9], [9, 1, 13, 15, 4]]
    )

Icosahedron = Polyhedron(
    [(0, 1, phi), (0, 1, -phi), (0, -1, phi), (0, -1, -phi),  # 0 through 3
    (1, phi, 0), (1, -phi, 0), (-1, phi, 0), (-1, -phi, 0),  # 4 through 7
    (phi, 0, 1), (phi, 0, -1), (-phi, 0, 1), (-phi, 0, -1)],  # 8 through 11
    [[10, 6, 4, 8, 2], [4, 9, 3, 11, 6], [8, 5, 7, 0, 10], [1, 9, 5, 11, 7],
    [0, 6, 1, 9, 8], [7, 3, 9, 2, 8], [0, 4, 1, 11, 10], [3, 5, 11, 2, 10],
    [2, 5, 9, 0, 4], [3, 5, 1, 4, 8], [6, 2, 0, 11, 7], [1, 6, 10, 3, 7]],
    [[4, 0, 6], [4, 6, 1], [1, 11, 6], [6, 11, 10], [6, 10, 0],
    [3, 1, 11], [3, 11, 7], [3, 7, 5], [3, 5, 9], [3, 9, 1],
    [10, 11, 7], [1, 4, 9], [2, 8, 5], [5, 8, 9], [2, 5, 7],
    [0, 4, 8], [0, 2, 8], [0, 2, 10], [2, 7, 10], [4, 8, 9]]
    )
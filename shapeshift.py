# standard library imports
from random import randint
from math import isclose

# third-party imports
from numpy import dot, arccos
from numpy.linalg import norm
import OpenGL.GL as GL


class Polyhedron:
    def __init__(self, vertices, edges, faces):
        self.vertices = vertices  # np.array(vertices, dtype=Decimal)  # list of tuples: [(x, y, z), (x, y, z)...]
        self.edges = edges  # primary index is one vertex and the list's entry is other
        self.faces = faces  # ordered lists of vertex indices
        
        # determines color of the polyhedron
        self.color1=randint(0,10)/10
        self.color2=randint(0,10)/10
        self.color3=randint(0,10)/10

    def stats(self):
        print("Vertices:", len(self.vertices))
        directed_edges = 0
        for group in self.edges:
            for neighbour in group:
                directed_edges += 1
        undirected_edges = directed_edges//2
        print("Edges:", undirected_edges)
        print("Faces:", len(self.faces))

    def full_stats(self):
        print("Vertices: ", self.vertices)
        print("Edges: ", self.edges)
        print("Faces: ", self.faces)

    def face_types(self):
        polygon_names = {1:"monogon", 2:"digon", 3:"triangles", 4:"quadrilaterals", 5:"pentagons", 6:"hexagons", 7:"heptagon", 8:"octagon"}
        polygon_counts = [0, 0, 0, 0, 0, 0, 0, 0]
        for face in self.faces:
            polygon_counts[len(face) - 3] += 1
        index = 0
        for count in polygon_counts:
            if count != 0:
                print(polygon_names[index + 3] + ":", polygon_counts[index])
            index += 1

    def draw_vertices(self):
        pass

    def draw_edges(self):
        GL.glBegin(GL.GL_LINES)
        for group in enumerate(self.edges):
            for neighbour in group[1]:
                if group[0] < neighbour:
                    GL.glColor3f(self.color1, self.color2, self.color3)
                    GL.glVertex3fv(self.vertices[group[0]])
                    GL.glVertex3fv(self.vertices[neighbour])
        GL.glEnd()

    def draw_faces(self):
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
        print("Dual function is under development")

    def stellate(self):
        print("Stellation function is under development")

    def greatening(self):
        pass


        new_vertices = self.vertices
        new_edges = self.edges
        new_faces = self.faces
        return Polyhedron(new_vertices, new_edges, new_faces)

Tetrahedron = Polyhedron([(1, 1, 1), (-1, -1, 1), (-1, 1, -1), (1, -1, -1)],  # vertices
                         [[1, 2, 3], [0, 2, 3], [0, 1, 3], [0, 1, 2]],  # edges as adjacency matrix
                         [[0, 1, 2], [0, 2, 3], [0, 1, 3], [1, 2, 3]])  # faces as defined by vertices

Cube = Polyhedron([(1, 1, 1), (1, 1, -1), (1, -1, -1), (1, -1, 1), (-1, -1, 1), (-1, -1, -1), (-1, 1, -1),(-1, 1, 1)],
                 [[1, 3, 7], [0, 2, 6], [1, 3, 5], [2, 4, 0] ,[3, 5, 7] ,[4, 6, 2] ,[5, 7, 1], [6, 0, 4]],
                 [[0, 1, 2, 3], [0, 1, 6, 7], [0, 3, 4, 7], [4, 5, 6, 7], [4, 5, 2, 3], [1, 2, 5, 6]])

TruncatedTruncatedCube = Polyhedron([(1.0, -0.7777777777777777, 0.5555555555555556),(1.0, -0.5555555555555556, 0.7777777777777777),(1.0, -0.1111111111111111, 1.0),
(1.0, 0.1111111111111111, 1.0),(1.0, 0.5555555555555556, 0.7777777777777777),(1.0, 0.7777777777777777, 0.5555555555555556),
(1.0, 1.0, 0.1111111111111111),(1.0, 1.0, -0.1111111111111111),(1.0, 0.7777777777777777, -0.5555555555555556),
(1.0, 0.5555555555555556, -0.7777777777777777),(1.0, 0.1111111111111111, -1.0),(1.0, -0.1111111111111111, -1.0),
(1.0, -0.5555555555555556, -0.7777777777777777),(1.0, -0.7777777777777777, -0.5555555555555556),(1.0, -1.0, -0.1111111111111111),
(1.0, -1.0, 0.1111111111111111)], [],
[[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12,13, 14, 15], [2, 4, 6]])

'''
x2 = [(-0.7777777777777777, 1.0, 0.5555555555555556),
(-0.5555555555555556, 1.0, 0.7777777777777777),
(-0.1111111111111111, 1.0, 1.0),
(0.1111111111111111, 1.0, 1.0),
(0.5555555555555556, 1.0, 0.7777777777777777),
(0.7777777777777777, 1.0, 0.5555555555555556),
(0.7777777777777777, 1.0, -0.5555555555555556),
(0.5555555555555556, 1.0, -0.7777777777777777),
(0.1111111111111111, 1.0, -1.0),
(-0.1111111111111111, 1.0, -1.0),
(-0.5555555555555556, 1.0, -0.7777777777777777),
(-0.7777777777777777, 1.0, -0.5555555555555556),
(-1.0, 1.0, -0.1111111111111111),
(-1.0, 1.0, 0.1111111111111111)]
c = 30

x3 = [(-0.7777777777777777, 0.5555555555555556, 1.0),
(-0.5555555555555556, 0.7777777777777777, 1.0),
(0.5555555555555556, 0.7777777777777777, 1.0),
(0.7777777777777777, 0.5555555555555556, 1.0),
(0.7777777777777777, -0.5555555555555556, 1.0),
(0.5555555555555556, -0.7777777777777777, 1.0),
(0.1111111111111111, -1.0, 1.0),
(-0.1111111111111111, -1.0, 1.0),
(-0.5555555555555556, -0.7777777777777777, 1.0),
(-0.7777777777777777, -0.5555555555555556, 1.0),
(-1.0, -0.1111111111111111, 1.0),
(-1.0, 0.1111111111111111, 1.0)]
c = 42

x4 = [(-1.0, 0.7777777777777777, 0.5555555555555556),
(-1.0, 0.5555555555555556, 0.7777777777777777),
(-1.0, -0.5555555555555556, 0.7777777777777777),
(-1.0, -0.7777777777777777, 0.5555555555555556),
(-1.0, -1.0, 0.1111111111111111),
(-1.0, -1.0, -0.1111111111111111),
(-1.0, -0.7777777777777777, -0.5555555555555556),
(-1.0, -0.5555555555555556, -0.7777777777777777),
(-1.0, -0.1111111111111111, -1.0),
(-1.0, 0.1111111111111111, -1.0),
(-1.0, 0.5555555555555556, -0.7777777777777777),
(-1.0, 0.7777777777777777, -0.5555555555555556)]
c = 54

x5 = [(0.7777777777777777, -1.0, 0.5555555555555556),
(0.5555555555555556, -1.0, 0.7777777777777777),
(-0.5555555555555556, -1.0, 0.7777777777777777),
(-0.7777777777777777, -1.0, 0.5555555555555556),
(-0.7777777777777777, -1.0, -0.5555555555555556),
(-0.5555555555555556, -1.0, -0.7777777777777777),
(-0.1111111111111111, -1.0, -1.0),
(0.1111111111111111, -1.0, -1.0),
(0.5555555555555556, -1.0, -0.7777777777777777),
(0.7777777777777777, -1.0, -0.5555555555555556)]
c = 64

x6 = [(-0.7777777777777777, 0.5555555555555556, -1.0),
(-0.5555555555555556, 0.7777777777777777, -1.0),
(0.5555555555555556, 0.7777777777777777, -1.0),
(0.7777777777777777, 0.5555555555555556, -1.0),
(0.7777777777777777, -0.5555555555555556, -1.0),
(0.5555555555555556, -0.7777777777777777, -1.0),
(-0.5555555555555556, -0.7777777777777777, -1.0),
(-0.7777777777777777, -0.5555555555555556, -1.0)]
c = 72

x7 = [(0.1111111111111111, 1.0, 0.5555555555555556),
(0.5555555555555556, 1.0, 0.1111111111111111),
(1.0, 0.5555555555555556, 0.1111111111111111),
(1.0, 0.1111111111111111, 0.5555555555555556),
(0.5555555555555556, 0.1111111111111111, 1.0),
(0.1111111111111111, 0.5555555555555556, 1.0)]
'''

'''
phi = (1 + 5**0.5)/2

Dodecahedron = Polyhedron([(1, 1, 1), (1, 1, -1), (1, -1, 1), (-1, 1, 1), (-1, 1, -1), (-1, -1, 1), (1, -1, -1), (-1, -1, -1), (0, phi, 1/phi), (0, phi, -1/phi), (0, -phi, 1/phi), (0, -phi, -1/phi), (1/phi, 0, phi), (1/phi, 0, -phi), (-1/phi, 0, phi), (-1/phi, 0, -phi), (phi, 1/phi, 0), (phi, -1/phi, 0), (-phi, 0, 1/phi), (-phi, 0, -1/phi)]
[[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []],
[[], [], [], [], [], [], [], [], [], [], [], []])
'''
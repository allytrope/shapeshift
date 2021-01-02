import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from numpy import dot, arccos
from numpy.linalg import norm

from random import randint


class Polyhedron:
    def __init__(self, vertices, edges, faces):
        self.vertices = vertices  # list of tuples: [(x, y, z), (x, y, z)...]
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
        polygon_names = {3:"triangles", 4:"quadrilaterals", 5:"pentagons", 6:"hexagons"}
        polygon_counts = [0, 0, 0, 0, 0, 0]
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
        glBegin(GL_LINES)
        for group in enumerate(self.edges):
            for neighbour in group[1]:
                if group[0] < neighbour:
                    glColor3f(self.color1, self.color2, self.color3)
                    glVertex3fv(self.vertices[group[0]])
                    glVertex3fv(self.vertices[neighbour])
        glEnd()

    def draw_faces(self):
        glBegin(GL_LINES)
        for face in self.faces:
            for i in range(len(face)):
                #if face[i-1] > face[i]:
                glVertex3fv(self.vertices[face[i-1]])
                glVertex3fv(self.vertices[face[i]])
        glEnd()


    def rectify(self):
        print("Rectifying")
        def find_midpoint(given_edge):
            new_vertex = ((self.vertices[given_edge[0]][0] + self.vertices[given_edge[1]][0]) / 2,  # x coordinate
                          (self.vertices[given_edge[0]][1] + self.vertices[given_edge[1]][1]) / 2,  # y coordinate
                          (self.vertices[given_edge[0]][2] + self.vertices[given_edge[1]][2]) / 2)  # z coordinate
            return new_vertex

        def convex_hull(vertices):
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
            # creates new vertices and faces
            new_face = []
            for x in range(len(face)):  # x acts as counter
                edge = [face[x-1], face[x]]
                midpoint = find_midpoint(edge)
                if midpoint not in new_vertices:
                    new_vertices.append(midpoint)
                new_face.append(new_vertices.index(midpoint))
            new_faces.append(new_face)
            # creates new edges
            for x in range(len(new_face)):
                new_edges[new_face[x-1]].append(new_face[x])
                new_edges[new_face[x]].append(new_face[x-1])

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
            ordered = convex_hull(unordered)
            ordered_indexed = []
            # converts vertices to corresponding indices
            for vertex in ordered:
                ordered_indexed.append(new_vertices.index(vertex))
            new_faces.append(ordered_indexed)
        return Polyhedron(new_vertices, new_edges, new_faces)


Tetrahedron = Polyhedron([(1, 1, 1), (-1, -1, 1), (-1, 1, -1), (1, -1, -1)],  # vertices
                         [[1, 2, 3], [0, 2, 3], [0, 1, 3], [0, 1, 2]],  # edges as adjacency matrix
                         [[0, 1, 2], [0, 2, 3], [0, 1, 3], [1, 2, 3]])  # faces as defined by vertices

Cube = Polyhedron([(1, 1, 1), (1, 1, -1), (1, -1, -1), (1, -1, 1), (-1, -1, 1), (-1, -1, -1), (-1, 1, -1),(-1, 1, 1)],
                 [[1, 3, 7], [0, 2, 6], [1, 3, 5], [2, 4, 0] ,[3, 5, 7] ,[4, 6, 2] ,[5, 7, 1], [6, 0, 4]],
                 [[0, 1, 2, 3], [0, 1, 6, 7], [0, 3, 4, 7], [4, 5, 6, 7], [4, 5, 2, 3], [1, 2, 5, 6]])


def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -5)

    # default polyhedron shown
    shape = Cube
    prior_polyhedra = []
    keep_prior_polyhedra = False
    # event loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    if keep_prior_polyhedra == True:
                        print(shape)
                        prior_polyhedra.append(shape)
                    shape = shape.rectify()
                if event.key == pygame.K_s:
                    shape.stats()
                if event.key == pygame.K_x:
                    shape.full_stats()
                if event.key == pygame.K_f:
                    shape.face_types()
                if event.key == pygame.K_k:
                    keep_prior_polyhedra = not keep_prior_polyhedra
                    if keep_prior_polyhedra == False:
                        prior_polyhedra.clear()
                    

        glRotatef(.2, .2, 1, .2)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # shape can change in events
        shape.draw_edges()
        if keep_prior_polyhedra == True:
            for polyhedron in prior_polyhedra:
                polyhedron.draw_edges()
        pygame.display.flip()
        pygame.time.wait(10)


main()

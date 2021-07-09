"""Operations class and corresponding operations for transforming polyhedra."""

# standard library imports
from itertools import cycle, islice

# third-party imports
import numpy as np
from sympy import Rational

# local imports
from polyhedra import Polyhedron


class Operations:
    """This class contains operations to be performed on instances of class Polyhedron
     as well as helper functions for those operations.
     """
    @staticmethod
    def __add_to_list(point, new_vertices, new_face):
        """Test if point already in new_vertices, and if not, add it."""
        try:
            index = new_vertices.index(point)
            new_face.append(index)
        except ValueError:
            new_vertices.append(point)
            new_face.append(len(new_vertices) - 1)

    @staticmethod
    def diminish(func, vertex, new_vertices):
        """Remove pyramid off polyhedron where apex is a vertex on the polyhedron.
        Takes a func to determine how base of pyramid is formed.
        Used in truncate(), rectify(), and facet().
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
    
    @classmethod
    def truncate(cls, polyhedron):
        """Perform truncation operation. Cleave vertices by marking 1/3rd and 2/3rds of each edge as new vertices."""
        print("Truncating")
        def find_third(vertex1, vertex2):
            return ((vertex1[0]*Rational(2, 3) + vertex2[0]*Rational(1, 3)),  # x coordinate
                    (vertex1[1]*Rational(2, 3) + vertex2[1]*Rational(1, 3)),  # y coordinate
                    (vertex1[2]*Rational(2, 3) + vertex2[2]*Rational(1, 3)))  # z coordinate

        new_vertices = []
        new_faces = []

        # create truncated faces (new faces derived from previous faces)
        for face in polyhedron.faces:
            new_face = []

            # create new vertices and faces
            for x in range(len(face.vertices)):
                coordinates1 = face.vertices[x - 1].coordinates
                coordinates2 = face.vertices[x].coordinates

                third_forward = find_third(coordinates1, coordinates2)
                third_backward = find_third(coordinates2, coordinates1)

                cls.__add_to_list(third_forward, new_vertices, new_face)
                cls.__add_to_list(third_backward, new_vertices, new_face)

            new_faces.append(new_face)

        # create new faces (new faces derived from previous vertices)
        for vertex in polyhedron.vertices:
            new_face = cls.diminish(find_third, vertex, new_vertices)
            new_faces.append(new_face)

        return Polyhedron(new_vertices, new_faces)

    @classmethod
    def rectify(cls, polyhedron):
        """Perform rectification operation. Cleave vertices by marking midpoints as new vertices."""
        print("Rectifying")

        def find_midpoint(vertex1, vertex2):
            return ((vertex1[0] + vertex2[0])*Rational(1, 2),  # x coordinate
                    (vertex1[1] + vertex2[1])*Rational(1, 2),  # y coordinate
                    (vertex1[2] + vertex2[2])*Rational(1, 2))  # z coordinate

        # arrays for new polyhedron's vertices, edges, and faces
        new_vertices = []
        new_faces = []

        # create rectified faces (new faces derived from previous faces)
        for face in polyhedron.faces:
            new_face = []

            # find new vertices
            offset_cycle = islice(cycle(face.vertices), 1, None)
            for vertex, neighbour in zip(face.vertices, offset_cycle):
                midpoint = find_midpoint(vertex.coordinates, neighbour.coordinates)

                # test if midpoint is already in new_vertices, and if not, add it
                cls.__add_to_list(midpoint, new_vertices, new_face)

            new_faces.append(new_face)
            
        
        # create new faces (new faces derived from previous vertices)
        for vertex in polyhedron.vertices:
            new_face = cls.diminish(find_midpoint, vertex, new_vertices)
            new_faces.append(new_face)

        return Polyhedron(new_vertices, new_faces)

    @classmethod
    def facet(cls, polyhedron):
        """Perform facet operation. Maintain all previous vertices, but connect them differently to form new faces on a nonconvex figure."""
        print("Faceting")

        def keep_only_neighbour(vertex1, vertex2):
            return vertex2

        new_faces = []
        new_vertices = [vertex.coordinates for vertex in polyhedron.vertices]
        
        # create new faces (new faces derived from previous vertices)
        for vertex in polyhedron.vertices:
            new_face = cls.diminish(keep_only_neighbour, vertex, new_vertices)
            new_faces.append(new_face)

        return Polyhedron(new_vertices, new_faces)

    @classmethod
    def reciprocate(cls, polyhedron):
        """Perform reciprocation operation. Convert centroid of each face into a vertex and connect each adjacent centroid.
        This implementation creates skew faces on some polyhedra."""
        print("Reciprocating")
        def find_centroid(vertices_coordinates):
            return tuple(sum(np.array(vertices_coordinates))/len(vertices_coordinates))

        new_vertices = []
        new_faces = []

        # create new vertices and faces
        for vertex in polyhedron.vertices:
            new_face = []
            for face in vertex.faces:
                centroid = find_centroid([vertex.coordinates for vertex in face.vertices])

                # test if centroid is already in new_vertices, and if not, add it
                cls.__add_to_list(centroid, new_vertices, new_face)

            new_faces.append(new_face)
        return Polyhedron(new_vertices, new_faces)

    @staticmethod
    def augment(func, face, new_vertices):
        print("Under development")
        pass

    @classmethod
    def cap(cls, polyhedron):
        print("Under development")
        return polyhedron

    @classmethod
    def bridge(cls, polyhedron):
        print("Under development")
        return polyhedron

    @classmethod
    def stellate(cls, polyhedron):
        print("Under development")
        return polyhedron

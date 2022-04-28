"""Operations class and corresponding operations for transforming polyhedra."""

# Standard library imports
from itertools import cycle, islice

# Third-party imports
import numpy as np
from sympy import Line, Line3D, Point, Point3D, Rational

# Local imports
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
        # Create new faces (new faces derived from previous vertices)
        unordered_face = []
        for neighbour in vertex.neighbours:
            midpoint = func(vertex.coordinates, neighbour.coordinates)
            unordered_face.append((midpoint, neighbour))

        # Find edges by comparing endpoint faces
        edges = []
        for midpoint1, endpoint1 in unordered_face:
            for midpoint2, endpoint2 in unordered_face:
                if midpoint1 != midpoint2:
                    for end_face in endpoint1.faces:
                        if end_face in endpoint2.faces:
                            edges.append((midpoint1, midpoint2))

        # Order vertices in face
        face_vertices = [edges[0][0]]
        for _ in edges:
            for edge in edges:
                if edge[0] == face_vertices[-1] and edge[1] not in face_vertices:
                    face_vertices.append(edge[1])
                    break
        
        # Create new faces and vertices
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

        # Create truncated faces (new faces derived from previous faces)
        for face in polyhedron.faces:
            new_face = []

            # Create new vertices and faces
            for x in range(len(face.vertices)):
                coordinates1 = face.vertices[x - 1].coordinates
                coordinates2 = face.vertices[x].coordinates

                third_forward = find_third(coordinates1, coordinates2)
                third_backward = find_third(coordinates2, coordinates1)

                cls.__add_to_list(third_forward, new_vertices, new_face)
                cls.__add_to_list(third_backward, new_vertices, new_face)

            new_faces.append(new_face)

        # Create new faces (new faces derived from previous vertices)
        for vertex in polyhedron.vertices:
            new_face = cls.diminish(find_third, vertex, new_vertices)
            new_faces.append(new_face)

        return Polyhedron(new_vertices, new_faces)

    @classmethod
    def rectify(cls, polyhedron, method="by_midsphere"):
        """Perform rectification operation. This diminishes the polyhedron at vertices such edges are converted into new vertices.
        The default implementation uses the intersections of the edges to the polyhedron's midsphere to place new vertices.
        And thus, this only works on polyhedra that have a midsphere.

        An alternate method can be used by setting the parameter method to "by_midpoint".
        This method doesn't require a midsphere and instead cleaves vertices by marking midpoints of edges as new vertices.
        For uniform polyhedra, this produces the same results as the midsphere method; however, for nonuniform polyhedra,
        this can result in nonplanar faces."""
        print("Rectifying")

        def find_midsphere_intersection(vertex1, vertex2):
            """"Use sympy to find point on line closest to origin."""
            line = Line3D(Point3D(vertex1), Point3D(vertex2))
            point = line.projection(Point3D(0, 0, 0))
            return point.coordinates

        def find_midpoint(vertex1, vertex2):
            return ((vertex1[0] + vertex2[0])*Rational(1, 2),  # x coordinate
                    (vertex1[1] + vertex2[1])*Rational(1, 2),  # y coordinate
                    (vertex1[2] + vertex2[2])*Rational(1, 2))  # z coordinate

        # Decide on method of rectification
        if method == "by_midsphere":
            if not polyhedron.is_canonical():
                print("Polyhedron is not canonical; must have a midsphere to rectify.")
                return polyhedron
            create_new_vertices = find_midsphere_intersection
        elif method == "by_midpoint":
            create_new_vertices = find_midpoint
        else:
            print("Not a valid option for parameter alt_method.")
        

        # Arrays for new polyhedron's vertices, edges, and faces
        new_vertices = []
        new_faces = []

        # Create rectified faces (new faces derived from previous faces)
        for face in polyhedron.faces:
            new_face = []

            # Find new vertices
            offset_cycle = islice(cycle(face.vertices), 1, None)
            for vertex, neighbour in zip(face.vertices, offset_cycle):
                midpoint = create_new_vertices(vertex.coordinates, neighbour.coordinates)

                # Test if midpoint is already in new_vertices, and if not, add it
                cls.__add_to_list(midpoint, new_vertices, new_face)

            new_faces.append(new_face)
            
        
        # Create new faces (new faces derived from previous vertices)
        for vertex in polyhedron.vertices:
            new_face = cls.diminish(create_new_vertices, vertex, new_vertices)
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
        
        # Create new faces (new faces derived from previous vertices)
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

        # Create new vertices and faces
        for vertex in polyhedron.vertices:
            new_face = []
            for face in vertex.faces:
                centroid = find_centroid([vertex.coordinates for vertex in face.vertices])

                # Test if centroid is already in new_vertices, and if not, add it
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
    def stellate(cls, polyhedron, nth_stellation: int = 2):
        """Extends edges until meeting other edges, creating new vertices and changing shape of faces.
        The base polyhedron is designated as the first stellation, or nth_stellation=1."""
        
        print("Under development")

        def find_midpoint(edge):
            midpoint = ((edge[0][0] + edge[1][0])*Rational(1, 2),  # x coordinate
                        (edge[0][1] + edge[1][1])*Rational(1, 2),  # y coordinate
                        (edge[0][2] + edge[1][2])*Rational(1, 2))  # z coordinate
            return midpoint
        
        # Edge needs to be of form [(1.0, 1.0, 1.0), (1.5, 2.0, 1.5)]
        # Create lines from edges
        lines = [Line(*edge) for edge in polyhedron.edges]
        midpoints = [Point(find_midpoint(edge)) for edge in polyhedron.edges]

        new_edges = []
        for idx, line1 in enumerate(lines):
            intersections = []
            for line2 in lines:
                if line1 != line2:
                    intersection = line1.intersection(line2)
                    if intersection:
                        intersections.append(intersection[0])
            distances = [intersection.distance(midpoints[idx]) for intersection in intersections]
            print("Distances", distances)
            try:
                mins = sorted(list(set(distances)))
                endpoints = []
                for idx, distance in enumerate(distances):
                    if distance == mins[nth_stellation]:
                        endpoints.append(idx)
                new_edges.append(tuple(endpoints))
            except:
                print("Stellation of order", nth_stellation, "does not exist.")
                return polyhedron

    @classmethod
    def decompose(cls, polyhedron):
        """Slice polyhedron into two or more parts. If not decomposable, return self."""
        print("Under development")
        return polyhedron

    @classmethod
    def uncouple(cls, polyhedron):
        """Separate compound polyhedra."""
        print("Under development")
        return polyhedron
        composititions = []

        connected_faces = []
        def neighbour_recursion(connected_faces, face):
            for neighbour in face.neighbours:
                if neighbour not in connected_faces:
                    connected_faces.append(neighbour)
                    neighbour_recursion(neighbour)


        neighbour_recursion(polyhedron.faces[0].neighbours)

        if len(connected_faces) == len(polyhedron.faces):
            return polyhedron
        else:
            return Polyhedron(polyhedron.vertices, connected_faces)  # change new vertices 

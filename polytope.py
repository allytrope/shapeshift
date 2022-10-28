"""
Polytope class and subclasses for n-polytopes. Likewise, generalized NFace class and subclasses for n-faces, which are stored inside Polytopes.
"""

# Standard library imports
from __future__ import annotations
from functools import cached_property, reduce
from itertools import combinations, cycle, islice
from math import isclose
from typing import List, Set, Tuple
import weakref

# Third-party imports
import numpy as np
import sympy
from sympy import Rational

# Local imports
#from exceptions import SubfaceError


class Polytope:
    """
    Superclass for n-polytopes. Such as polyhedra, polygons, line segments, and points.
    Each positional argument is a list. Vertices are a list of 3-tuples.
    And the rest are lists of integers to represent the indicies of the subfaces that form that n-face.
    Example for constructing a polyhedron:
    Polytope([vertices, edges, faces])
    """
    def __init__(self, subfaces: List[Polytope] = None, superfaces: List[Polytope] = None):
        if subfaces is None:
            self.subfaces = []
        else:
            self.subfaces = subfaces
        if superfaces is None:
            self.superfaces = []
        else:
            self.superfaces = weakref.proxy(superfaces)

    # def __eq__(self, other) -> bool:
    #     if isinstance(other, Polytope):
    #         return self.subfaces == self.subfaces
        
    # def __hash__(self):
    #     return hash(self.subfaces)
    
    def __getitem__(self, idx) -> Polytope:
        """Index by subfaces."""
        return self.subfaces[idx]

    def __len__(self):
        """Return count of subfaces."""
        return len(self.subfaces)

    @property
    def rank(self) -> int:
        """The dimension of self."""
        if self.subfaces == []:
            return 0
        else:
            return next(iter(self.subfaces)).rank + 1

    @property
    def parents(self) -> List[Polytope]:
        """Alias for superfaces; that is, (n+1)-faces that contain self."""
        return self.superfaces

    @cached_property
    def siblings(self) -> List[Polytope]:
        """Return n-faces that share an (n+1)-face with self."""
        neighbours = set()
        for superface in self.superfaces:
            neighbours = neighbours.union(superface.subfaces)
        neighbours.remove(self)
        return list(neighbours)

    @cached_property
    def neighbours(self) -> List[Polytope]:
        """Return n-faces that share an (n-1)-face with self."""
        neighbours = set()
        for subface in self.subfaces:
            neighbours = neighbours.union(subface.superfaces)
        neighbours.remove(self)
        return list(neighbours)

    @property
    def children(self) -> List[Polytope]:
        """Alias for subfaces; that is, (n-1)-faces that self contains."""
        return self.subfaces

    @property
    def facets(self) -> List[Polytope]:
        """(n-1)-faces."""
        return self.subfaces

    @property
    def ridges(self) -> List[Polytope]:
        """(n-2)-faces."""
        return self.nfaces(self.rank - 2)

    @property
    def peaks(self) -> List[Polytope]:
        """(n-3)-faces."""
        return self.nfaces(self.rank - 3)

    def nfaces(self, rank) -> List[Polytope]:
        """Return n-faces, where n is the "rank" argument, that are within self or that self is within."""
        if rank > self.rank:
            faces = self.superfaces
            superfaces = set()
            while True:
                if next(iter(faces)).rank == rank:
                    return list(faces)
                for superface in faces:
                    superfaces = superfaces.union(superface.superfaces)
                faces = superfaces
                superfaces = set()
        elif rank == self.rank:
            return self
        else:
            faces = self.subfaces
            subfaces = set()
            while True:
                if next(iter(faces)).rank == rank:
                    return list(faces)
                for subface in faces:
                    subfaces = subfaces.union(subface.subfaces)
                faces = subfaces
                subfaces = set()

    @property
    def cells(self) -> List[Polytope]:
        """3-faces."""
        return self.nfaces(3)

    @property
    def faces(self) -> List[Polygon]:
        """2-faces."""
        return self.nfaces(2)

    @property
    def edges(self) -> List[LineSegment]:
        """1-faces."""
        return self.nfaces(1)

    @property
    def vertices(self) -> List[Point]:
        """0-faces."""
        if next(iter(self.subfaces)) == []:
            return self.subfaces
        return self.nfaces(0)

    @property
    def ambient_dimension(self) -> int:
        """The number of dimensions in which the polytope resides in.
        Note that this is not always the dimensionality of the shape itself,
        such as a square in a 3D space."""
        return self.vertices[0].ambient_dimension

    @property
    def centroid(self) -> Point:
        """Average of positions in element."""
        positions = [vertex.position for vertex in self.vertices]
        centroid = []
        for axis in range(len(positions[0])):
            centroid.append(reduce(lambda a, b: a + b[axis], positions, 0)*Rational(1, len(positions)))
        return Point(centroid)

    def stats(self) -> None:
        """Print number of vertices, edges, faces, etc."""
        nfaces = ["Vertices", "Edges", "Faces", "Cells"]
        for rank in range(0, self.rank):
            if rank <= 3:
                nface = nfaces[rank]
            else:
                nface = f"{rank}-face"
            count = len(self.nfaces(rank))
            print(f"{nface}: {count}")
    

class Polyhedron(Polytope):
    """The 3-polytope."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def face_types(self) -> None:
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

    def is_canonical(self) -> bool:
        """Return whether Polyhedron has midsphere. That is to say whether all edges form lines tangent to the same sphere."""
        midradius = None
        for edge in self.edges:
            vertex1 = list(edge.vertices)[0]
            vertex2 = list(edge.vertices)[1]
            line = sympy.Line3D(sympy.Point3D(vertex1.coordinates), sympy.Point3D(vertex2.coordinates))
            distance = line.distance(sympy.Point3D(0, 0, 0))
            if midradius is None:
                midradius = distance
            elif not isclose(float(midradius), float(distance)):
                return False
        return True

    ### Operations and closely associated functions ###

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
    def diminish(method, fraction, vertex, new_vertices):
        """Remove pyramid off polyhedron where apex is a vertex on the polyhedron.
        Takes a func to determine how base of pyramid is formed.
        Used in truncate(), rectify(), and facet().
        """
        # Create new faces (new faces derived from previous vertices)
        unordered_face = []
        for neighbour in vertex.neighbours:
            midpoint = method(LineSegment([Point(vertex.coordinates), Point(neighbour.coordinates)]))
            new_vertex = ((vertex.coords[0]*(1-fraction) + midpoint[0]*fraction),  # x coordinate
                          (vertex.coords[1]*(1-fraction) + midpoint[1]*fraction),  # y coordinate
                          (vertex.coords[2]*(1-fraction) + midpoint[2]*fraction)) 
            unordered_face.append((new_vertex, neighbour))

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

    def rectify(self, method="by_midsphere") -> Polyhedron:
        """Perform rectification operation. This is a special case of the truncation operation.
        This diminishes the polyhedron at vertices such that edges are converted into new vertices.
        The new vertices are created using the method parameter, which is described in more detail under the truncation function."""
        print("Rectifying")
        return self.truncate(fraction=1, method=method)

    def truncate(self, fraction=Rational(2, 3), method="by_midsphere") -> Polyhedron:
        """Perform truncation operation. This diminishes the polyhedron at vertices such that new faces are made.
        The default implementation uses the intersections of the edges to the polyhedron's midsphere to base the maximum diminishment.
        And thus, this only works on polyhedra that have a midsphere.

        An alternate method can be used by setting the parameter method to "by_midpoint".
        This method doesn't require a midsphere and instead cleaves vertices by marking the midpoint (halfway down the edge).
        For uniform polyhedra, this produces the same results as the midsphere method; however, for nonuniform polyhedra,
        this can result in nonplanar faces."""
        print("Truncating")

        # Decide on method of truncation
        if method == "by_midsphere":
            if not self.is_canonical():
                print("Polyhedron is not canonical; must have a midsphere to rectify.")
                return self
            create_new_vertices = LineSegment.find_midsphere_intersection
        elif method == "by_midpoint":
            create_new_vertices = LineSegment.find_midpoint
        else:
            print("Not a valid option for parameter alt_method.")
        
        # Arrays for new polyhedron's vertices, edges, and faces
        new_vertices = []
        new_faces = []

        # Create truncated faces (new faces derived from previous faces)
        for face in self.faces:
            new_face = []

            # Find new vertices
            offset_cycle = islice(cycle(face.vertices), 1, None)
            for vertex, neighbour in zip(face.vertices, offset_cycle):
                midpoint = create_new_vertices(LineSegment([Point(vertex.coordinates), Point(neighbour.coordinates)]))

                new_vertex = ((vertex.coords[0]*(1-fraction) + midpoint[0]*fraction),  # x coordinate
                               (vertex.coords[1]*(1-fraction) + midpoint[1]*fraction),  # y coordinate
                               (vertex.coords[2]*(1-fraction) + midpoint[2]*fraction)) 

                # Test if midpoint is already in new_vertices, and if not, add it
                self.__add_to_list(new_vertex, new_vertices, new_face)

                # Checks if not rectification
                if fraction != 1:
                    new_vertex = ((neighbour.coords[0]*(1-fraction) + midpoint[0]*fraction),  # x coordinate
                                (neighbour.coords[1]*(1-fraction) + midpoint[1]*fraction),  # y coordinate
                                (neighbour.coords[2]*(1-fraction) + midpoint[2]*fraction))
                    self.__add_to_list(new_vertex, new_vertices, new_face)

            new_faces.append(new_face)
            
        # Create new faces (new faces derived from previous vertices)
        for vertex in self.vertices:
            new_face = self.diminish(create_new_vertices, fraction, vertex, new_vertices)
            new_faces.append(new_face)

        return create_polytope(new_vertices, new_faces)

    def facet(self) -> Polyhedron:
        """Perform facet operation. Maintain all previous vertices, but connect them differently to form new faces on a nonconvex figure."""
        print("Faceting")

        def keep_only_neighbour(vertex1, vertex2):
            return vertex2

        new_faces = []
        new_vertices = [vertex.coordinates for vertex in self.vertices]
        
        # Create new faces (new faces derived from previous vertices)
        for vertex in self.vertices:
            new_face = self.diminish(keep_only_neighbour, vertex, new_vertices)
            new_faces.append(new_face)

        return create_polytope(new_vertices, new_faces)

    def reciprocate(self) -> Polyhedron:
        """Perform reciprocation operation. Convert centroid of each face into a vertex and connect each adjacent centroid.
        This implementation creates skew faces on some polyhedra."""
        print("Reciprocating")
        def find_centroid(vertices_coordinates):
            return tuple(sum(np.array(vertices_coordinates))/len(vertices_coordinates))

        new_vertices = []
        new_faces = []

        # Create new vertices and faces
        for vertex in self.vertices:
            new_face = []
            for face in vertex.faces:
                centroid = find_centroid([vertex.coordinates for vertex in face.vertices])

                # Test if centroid is already in new_vertices, and if not, add it
                self.__add_to_list(centroid, new_vertices, new_face)

            new_faces.append(new_face)
        return create_polytope(new_vertices, new_faces)

    @staticmethod
    def augment(func, face, new_vertices):
        print("Under development")
        pass

    def cap(self):
        print("Under development")
        return self

    def bridge(self):
        print("Under development")
        return self

    def stellate(self, nth_stellation: int = 2) -> Polyhedron:
        """Extends edges until meeting other edges, creating new vertices and changing shape of faces.
        The base polyhedron is designated as the first stellation, or nth_stellation=1."""
        print("Under development")
        
        # Edge needs to be of form [(1.0, 1.0, 1.0), (1.5, 2.0, 1.5)]
        # Create lines from edges
        lines = [sympy.Line(*edge) for edge in self.edges]
        midpoints = [Point(edge.midpoint) for edge in self.edges]

        new_edges = []
        for idx, line1 in enumerate(lines):
            intersections = []
            for line2 in lines:
                if line1 != line2:
                    intersection = line1.intersection(line2)
                    if intersection:
                        intersections.append(intersection[0])
            distances = [intersection.distance(midpoints[idx]) for intersection in intersections]
            #print("Distances", distances)
            try:
                mins = sorted(list(set(distances)))
                endpoints = []
                for idx, distance in enumerate(distances):
                    if distance == mins[nth_stellation]:
                        endpoints.append(idx)
                new_edges.append(tuple(endpoints))
            except:
                print("Stellation of order", nth_stellation, "does not exist.")
                return self
        return create_polytope()

    def greaten(self):
        """Extend faces to form new larger faces."""
        print("Under development")

        def intersection(face1):
            """The line that two face meet along."""
            pass

        # Find intersections of neighbours of each face.
        for face in self.faces:
            for face1, face2 in combinations([neighbour for neighbour in face.neighbours], 2):
                edge = intersection(face1, face2)
        return self

    def decompose(self):
        """Slice polyhedron into two or more parts. If not decomposable, return self."""
        print("Under development")
        return self

    def uncouple(self):
        """Separate compound polyhedra."""
        print("Under development")
        return self
        composititions = []

        connected_faces = []
        def neighbour_recursion(connected_faces, face):
            for neighbour in face.neighbours:
                if neighbour not in connected_faces:
                    connected_faces.append(neighbour)
                    neighbour_recursion(neighbour)


        neighbour_recursion(self.faces[0].neighbours)

        if len(connected_faces) == len(self.faces):
            return polyhedron
        else:
            return Polyhedron(self.vertices, connected_faces)  # change new vertices 


class Polygon(Polytope):
    """The 2-polytope."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @cached_property
    def vertices(self):
        """Return ordered vertices."""
        edges = {*self.edges}
        first_edge = edges.pop()
        vertices = [first_edge.vertices[0], first_edge.vertices[1]]
        while len(edges) > 1:
            for edge in edges:
                try:
                    vertex_idx = edge.vertices.index(vertices[-1])
                    if vertex_idx == 0:
                        neighbour_idx = 1
                    else:
                        neighbour_idx = 0
                    vertices.append(edge.vertices[neighbour_idx])
                    edges.remove(edge)
                    break
                except:
                    pass
        return vertices


class LineSegment(Polytope):
    """The 1-polytope."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def midpoint(self) -> Point:
        """Alias for centroid."""
        return self.centroid

    def find_midpoint(self) -> Point:
        """Alias for centroid."""
        return self.centroid

    def find_third(self) -> Point:
        return ((self[0][0]*Rational(2, 3) + self[1][0]*Rational(1, 3)),  # x coordinate
                (self[0][1]*Rational(2, 3) + self[1][1]*Rational(1, 3)),  # y coordinate
                (self[0][2]*Rational(2, 3) + self[1][2]*Rational(1, 3)))  # z coordinate

    def find_midsphere_intersection(self):
        """"Use sympy to find point on line closest to origin."""
        line = sympy.Line3D(sympy.Point3D(self[0].coords), sympy.Point3D(self[1].coords))
        point = line.projection(sympy.Point3D(0, 0, 0))
        return point.coordinates


class Point(Polytope):
    """The 0-polytope."""
    def __init__(self, coords: Tuple[float]):
        super().__init__()
        self.coordinates = coords

    # def __eq__(self, other) -> bool:
    #     """Overide class Polytope implementation."""
    #     return isinstance(other, Point) and self.coords == self.coords

    # def __hash__(self):
    #     return hash(self.coords)

    def __str__(self):
        return "Point: " + str(self.coordinates)

    def __len__(self):
        return len(self.coordinates)

    def __getitem__(self, idx) -> Polytope:
        """Override class Polytope implementation. Index by coordinate."""
        return self.coordinates[idx]

    @property
    def children(self):
        # Overides the corresponding method for superclass NFace since vertices don't have subfaces.
        #raise SubfaceError("Vertices don't have subfaces.")
        pass

    @cached_property
    def neighbours(self) -> List[Point]:
        """Overide class Polytope implementation. Because vertices can't share a subface (for not having any),
        the closest idea of neighbours are those that share an edge.
        This usage of the term "neighbours" is used in graph theory and so applied here."""
        return self.siblings

    @property
    def coords(self):
        """Alias for coordinates."""
        return self.coordinates

    @property
    def position(self):
        """Alias for coordinates."""
        return self.coordinates

    @property
    def ambient_dimension(self):
        return len(self.position)


def create_polytope(*elements, with_edges=False) -> Polytope:
    """Construct instance of class Polytope."""

    def create_with_edges(input_faces):
        """Take faces referencing vertices and convert to faces referencing edges and edges referencing vertices."""
        # Convert input element tuples into type Polytope or one of its subclasses
        new_edges = []
        new_faces = []
        # Find new edges and faces
        for face_by_indices in input_faces:
            offset_cycle = islice(cycle(face_by_indices), 1, None)
            new_face = []
            for vertex_idx, neighbour_idx in zip(face_by_indices, offset_cycle):
                directed_edge = (vertex_idx, neighbour_idx)
                if directed_edge in new_edges:
                    idx = new_edges.index(directed_edge)
                elif tuple(reversed(directed_edge)) in new_edges:
                    idx = new_edges.index(tuple(reversed(directed_edge)))
                else:
                    idx = len(new_edges)
                    new_edges.append(directed_edge)
                new_face.append(idx)
            new_faces.append(new_face)
        return new_edges, new_faces

    elements_by_indices = list(elements)
    if not with_edges:
        new_edges, new_faces = create_with_edges(elements[1])
        # Assign new edges and faces to elements
        elements_by_indices.insert(1, new_edges)
        elements_by_indices[2] = new_faces
    else:
        elements_by_indices = elements

    nfaces = [[] for rank in elements_by_indices]

    for rank, elements in enumerate(elements_by_indices):
        for nface in elements:
            # Set class to instantiate as
            if rank == 0:
                NFace = Point
            elif rank == 1:
                NFace = LineSegment
            elif rank == 2:
                NFace = Polygon
            elif rank == 3:
                NFace = Polyhedron
            else:
                NFace = Polytope

            # Build instance
            if rank == 0:
                nfaces[rank].append(NFace(nface))
            else:
                subfaces = []
                # Add subfaces for n-face
                for subface_idx in nface:
                    subfaces.append(nfaces[rank - 1][subface_idx])
                cur_face = NFace(subfaces=subfaces)
                nfaces[rank].append(cur_face)

                # Add superface to (n-1)-faces (except for facet)
                for subface in subfaces:
                    subface.superfaces.append(cur_face)

    # Create and return outermost container for all n-faces
    if len(elements_by_indices) == 2:
        polytope = Polygon(subfaces=nfaces[-1])
    elif len(elements_by_indices) == 3:
        polytope = Polyhedron(subfaces=nfaces[-1])
    elif len(elements_by_indices) > 3:
        polytope = Polytope(subfaces=nfaces[-1])
    
    # Add polytope as superface to facets
    for facet in nfaces[-1]:
        facet.superfaces.append(polytope)

    # Create and return outermost container for all n-faces
    return polytope

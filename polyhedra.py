"""
Polytope class and subclasses for n-polytopes. Likewise, generalized NFace class and subclasses for n-faces, which are stored inside Polytopes.
"""

# Standard library imports
from __future__ import annotations
from functools import cached_property, reduce
from itertools import cycle, islice
from math import isclose
from typing import List, Set, Tuple
import weakref

# Third-party imports
import numpy as np
from sympy import GoldenRatio as PHI, Line3D, Point3D, Rational

# Local imports
#from exceptions import SubfaceError

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

    @property
    def parents(self) -> Set[Polytope]:
        """Alias for superfaces; that is, (n+1)-faces that contain self."""
        return self.superfaces

    @cached_property
    def siblings(self) -> Set[Polytope]:
        """Return n-faces that share an (n+1)-face with self."""
        neighbours = set()
        for superface in self.superfaces:
            neighbours = neighbours.union(superface.subfaces)
        neighbours.remove(self)
        return neighbours

    @cached_property
    def neighbours(self) -> Set[Polytope]:
        """Return n-faces that share an (n-1)-face with self."""
        neighbours = set()
        for subface in self.subfaces:
            neighbours = neighbours.union(subface.superfaces)
        neighbours.remove(self)
        return neighbours

    @property
    def children(self) -> Set[Polytope]:
        """Alias for subfaces; that is, (n-1)-faces that self contains."""
        return self.subfaces

    # @property
    # def facets(self) -> List[Polytope]:
    #     """(n-1)-faces."""
    #     return self.subfaces

    # @property
    # def ridges(self) -> List[Polytope]:
    #     """(n-2)-faces."""
    #     return self.nfaces(-2)

    # @property
    # def peaks(self) -> List[Polytope]:
    #     """(n-3)-faces."""
    #     return self.nfaces(-3)

    # def nfaces(self, rank) -> List[Polytope]:
    #     """n-faces."""
    #     return self.elements[rank]

    # @property
    # def cells(self) -> List[Polytope]:
    #     """3-faces."""
    #     return self.nfaces(3)

    # @property
    # def faces(self) -> List[Polygon]:
    #     """2-faces."""
    #     return self.nfaces(2)

    # @property
    # def edges(self) -> List[LineSegment]:
    #     """1-faces."""
    #     return self.nfaces(1)

    # @property
    # def vertices(self) -> List[Point]:
    #     """0-faces."""
    #     return self.nfaces(0)

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
    

class Polyhedron(Polytope):
    """The 3-polytope."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def faces(self):
        return set(self.subfaces)

    @property
    def edges(self):
        edges = set()
        for face in self.faces:
            edges = edges.union(face.subfaces)
        return edges

    @property
    def vertices(self):
        vertices = set()
        for edge in self.edges:
            vertices = vertices.union(edge.subfaces)
        return vertices

    def stats(self):
        """Print number of vertices, edges, and faces."""
        print("Vertices:", len(self.vertices))
        print("Edges:", sum([len(face.vertices) for face in self.faces])//2)
        print("Faces:", len(self.faces))

    def full_stats(self):
        """Print array representations of vertices, edges, and faces."""
        print("Vertices:\n", [vertex.coordinates for vertex in self.vertices])
        #print("Edges:\n", self.edges)
        print("Faces by vertex:\n", [[vertex.idx for vertex in face.vertices] for face in self.faces])

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

    def is_canonical(self):
        """Return whether Polyhedron has midsphere. That is to say whether all edges form lines tangent to the same sphere."""
        midradius = None
        for edge in self.edges:
            vertex1 = list(edge.vertices)[0]
            vertex2 = list(edge.vertices)[1]
            line = Line3D(Point3D(vertex1.coordinates), Point3D(vertex2.coordinates))
            distance = line.distance(Point3D(0, 0, 0))
            if midradius is None:
                midradius = distance
            elif not isclose(float(midradius), float(distance)):
                return False
        return True


class Polygon(Polytope):
    """The 2-polytope."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __len__(self):
        return len(self.edges)

    @property
    def edges(self):
        return set(self.children)

    @property
    def vertices2(self):
        vertices = set()
        for edge in self.edges:
            vertices = vertices.union(edge.subfaces)
        return vertices
    
    # TEST THIS
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
    def faces(self):
        return self.superfaces

    @property
    def vertices(self):
        return self.children

    @property
    def midpoint(self):
        """Alias for centroid."""
        return self.centroid


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
        return str(self.coordinates)

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
    def neighbours(self) -> Set[Point]:
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

    @property
    def faces(self):
        faces = set()
        for edge in self.edges:
            faces = faces.union(edge.superfaces)
        return faces

    @property
    def edges(self):
        return self.superfaces


PHI = (1 + 5**0.5)/2

tetrahedron = create_polytope(
    [(1, 1, 1), (-1, -1, 1), (-1, 1, -1), (1, -1, -1)],
    [[0, 1, 2], [0, 2, 3], [0, 1, 3], [1, 2, 3]])

cube = create_polytope(
    [(1.0, 1.0, 1.0), (1.0, 1.0, -1.0), (1.0, -1.0, -1.0), (1.0, -1.0, 1.0), (-1.0, -1.0, 1.0), (-1.0, -1.0, -1.0), (-1.0, 1.0, -1.0),(-1.0, 1.0, 1.0)],
    [[0, 1, 2, 3], [0, 1, 6, 7], [0, 3, 4, 7], [4, 5, 6, 7], [4, 5, 2, 3], [1, 2, 5, 6]])

octahedron = create_polytope(
    [(0, 1, 0), (1, 0, 0), (0, 0, 1), (-1, 0, 0), (0, 0, -1), (0, -1, 0)],
    [[0, 1, 4], [0, 1, 2], [0, 2, 3], [0, 3, 4], [1, 4, 5], [1, 2, 5], [2, 3, 5], [3, 4, 5]])

dodecahedron = create_polytope(
    [(1, 1, 1), (1, 1, -1), (1, -1, 1), (-1, 1, 1), (-1, 1, -1), (-1, -1, 1), (1, -1, -1), (-1, -1, -1),
        (0, PHI, 1/PHI), (0, PHI, -1/PHI), (0, -PHI, 1/PHI), (0, -PHI, -1/PHI), (1/PHI, 0, PHI), (1/PHI, 0, -PHI),
        (-1/PHI, 0, PHI), (-1/PHI, 0, -PHI), (PHI, 1/PHI, 0), (PHI, -1/PHI, 0), (-PHI, 1/PHI, 0), (-PHI, -1/PHI, 0)],
    [[14, 12, 2, 10, 5], [12, 0, 16, 17, 2], [2, 17, 6, 11, 10], [5, 10, 11, 7, 19], [17, 16, 1, 13, 6], [6, 13, 15, 7, 11], 
        [14, 3, 18, 19, 5], [14, 12, 0, 8, 3], [3, 8, 9, 4, 18], [19, 18, 4, 15, 7], [8, 0, 16, 1, 9], [9, 1, 13, 15, 4]])

icosahedron = create_polytope(
    [(0, 1, PHI), (0, 1, -PHI), (0, -1, PHI), (0, -1, -PHI),
        (1, PHI, 0), (1, -PHI, 0), (-1, PHI, 0), (-1, -PHI, 0),
        (PHI, 0, 1), (PHI, 0, -1), (-PHI, 0, 1), (-PHI, 0, -1)],
    [[4, 0, 6], [4, 6, 1], [1, 11, 6], [6, 11, 10], [6, 10, 0],
        [3, 1, 11], [3, 11, 7], [3, 7, 5], [3, 5, 9], [3, 9, 1],
        [10, 11, 7], [1, 4, 9], [2, 8, 5], [5, 8, 9], [2, 5, 7],
        [0, 4, 8], [0, 2, 8], [0, 2, 10], [2, 7, 10], [4, 8, 9]])
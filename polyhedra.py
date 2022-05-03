"""
Polytope class and subclasses for n-polytopes. Likewise, generalized NFace class and subclasses for n-faces, which are stored inside Polytopes.
"""

# Standard library imports
from __future__ import annotations
from functools import cached_property, reduce
from itertools import cycle, islice
from math import isclose
from random import randint
from typing import List, Tuple
import weakref

# Third-party imports
import numpy as np
from sympy import GoldenRatio as PHI, Line3D, Point3D, Rational

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
    def __init__(self, *elements, with_edges=False):

        def create_new_edges_and_faces(input_faces):
            """Take faces referencing vertices and convert to faces referencing edges and edges referencing vertices."""
            # Convert input element tuples into type NFace or one of its subclasses
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
                        #print(directed_edge)
                        new_edges.append(directed_edge)
                    new_face.append(idx)
                new_faces.append(new_face)
            return new_edges, new_faces

        elements_by_indices = list(elements)
        if not with_edges:
            new_edges, new_faces = create_new_edges_and_faces(elements[1])
            # Assign new edges and faces to elements
            elements_by_indices.insert(1, new_edges)
            elements_by_indices[2] = new_faces
        else:
            elements_by_indices = elements

        # Convert input element tuples into type NFace or one of its subclasses
        self.elements = []
        for rank, n_elements in enumerate(elements_by_indices):
            if rank == 0:
                nface = Vertex
            elif rank == 1:
                nface = Edge
            elif rank == 2:
                nface = Face
            else:
                nface = NFace
            self.elements.append([])
            for idx, face in enumerate(n_elements):
                if nface == NFace:
                    self.elements[-1].append(nface(face, rank=rank, idx=idx, polytope=self))
                else:
                    self.elements[-1].append(nface(face, idx=idx, polytope=self))

        # Determine color of the polyhedron
        self.color = [self.randomize_color() for face in self.faces]
        self.rank = len(self.elements)

    @property
    def facets(self) -> List[NFace]:
        """(n-1)-faces."""
        return self.nfaces(-1)

    @property
    def ridges(self) -> List[NFace]:
        """(n-2)-faces."""
        return self.nfaces(-2)

    @property
    def peaks(self) -> List[NFace]:
        """(n-3)-faces."""
        return self.nfaces(-3)

    def nfaces(self, rank) -> List[NFace]:
        """n-faces."""
        return self.elements[rank]

    @property
    def cells(self) -> List[NFace]:
        """3-faces."""
        return self.nfaces(3)

    @property
    def faces(self) -> List[Face]:
        """2-faces."""
        return self.nfaces(2)

    @property
    def edges(self) -> List[Edge]:
        """1-faces."""
        return self.nfaces(1)

    @property
    def vertices(self) -> List[Vertex]:
        """0-faces."""
        return self.nfaces(0)

    @property
    def ambient_dimension(self):
        """The number of dimensions in which the polytope resides in.
        Note that this is not always the dimensionality of the shape itself,
        such as a square in a 3D space."""
        return self.vertices[0].ambient_dimension
    

class Polyhedron(Polytope):
    """The 3-polytope."""
    def __init__(self, *args):
        super().__init__(*args)

    def randomize_color(self):
        """Change RGB color of polyhedron."""
        return (randint(2,10)/10,
                randint(2,10)/10,
                randint(2,10)/10)

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
            vertex1 = edge.vertices[0]
            vertex2 = edge.vertices[1]
            line = Line3D(Point3D(vertex1.coordinates), Point3D(vertex2.coordinates))
            distance = line.distance(Point3D(0, 0, 0))
            if midradius is None:
                midradius = distance
            elif not isclose(float(midradius), float(distance)):
                return False
        return True

class Polygon(Polytope):
    """The 2-polytope."""
    def __init__(self, *args):
        super().__init__(*args)

class LineSegment(Polytope):
    """The 1-polytope."""
    def __init__(self, *args):
        super().__init__(*args)

class Point(Polytope):
    """The 0-polytope."""
    def __init__(self, coords):
        super().__init__()
        self.coordinates = coords


class NFace:
    """Inferface to view how an n-face of a polytope relates to other elements."""
    def __init__(self, subfaces: List[int], rank: int, idx: int, polytope: Polytope):
        self.subfaces = subfaces  # Indices for subfaces
        self.rank = rank
        self.idx = idx
        self.polytope = weakref.proxy(polytope)

    def __getitem__(self, idx):
        return self.polytope.elements[self.rank - 1][self.subfaces[idx]]

    # def __iter__(self):
    #     yield from self.subfaces

    @cached_property
    def children(self) -> NFace:
        """Return (n-1)-faces contained within this n-face."""
        children = []
        for idx in self.subfaces:
            children.append(self.polytope.elements[self.rank - 1][idx])
        return children

    @cached_property
    def neighbours(self) -> NFace:
        """Return other n-faces that share an (n-1)-face."""
        neighbours = []
        for nface in self.polytope.elements[self.rank]:
            if nface != self:
                if set(nface.subfaces).intersection(set(self.subfaces)):
                    neighbours.append(nface)
        return neighbours

    @cached_property
    def parents(self) -> NFace:
        """Return (n+1)-faces that contain this n-face."""
        parents = []
        if self.rank < self.polytope.rank:
            for nface in self.polytope.elements[self.rank + 1]:
                if self.idx in nface.subfaces:
                    parents.append(nface)
        else:
            print("This n-Face does not have a parent n-face.")
        return parents

    def centroid(self) -> Point:
        """Average of positions in element."""
        positions = [vertex.position for vertex in self.vertices]
        centroid = []
        for axis in range(len(positions[0])):
            centroid.append(reduce(lambda a, b: a + b[axis], positions, 0)*Rational(1, len(positions)))
        return Vertex(centroid)


class Face(NFace):
    """The 2-face."""
    def __init__(self, edges: List[int], idx, polytope):
        super().__init__(edges, rank=2, idx=idx, polytope=polytope)

    def __len__(self):
        return len(self.edges)

    @property
    def edges(self):
        return self.children
    
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


class Edge(NFace):
    """The 1-face."""
    def __init__(self, vertices: List[int], idx, polytope):
        super().__init__(vertices, rank=1, idx=idx, polytope=polytope)

    @property
    def vertices(self):
        return self.children

class Vertex(NFace):
    """The 0-face. A special case of an n-face having no subfaces but instead a position in space."""
    def __init__(self, coords: Tuple[float], idx, polytope):
        super().__init__([], rank=0, idx=idx, polytope=polytope)
        self.coordinates = coords

    def __str__(self):
        return str(self.coordinates)

    def __len__(self):
        return len(self.coordinates)

    @property
    def children(self):
        # Overides the corresponding method for superclass NFace since vertices don't have subfaces.
        #raise SubfaceError("Vertices don't have subfaces.")
        pass

    @cached_property
    def neighbours(self) -> NFace:
        """A different usage than the method for NFace.
        This returns other vertices that share an edge."""
        neighbours = []
        for nface in self.polytope.elements[self.rank + 1]:
            if self in nface:
                for subface in nface:
                    if subface is not self and subface not in neighbours:
                        neighbours.append(subface)
        return neighbours

    @property
    def position(self):
        """Alias for coordinates."""
        return self.coordinates

    @property
    def ambient_dimension(self):
        return len(self.position)

    @property
    def faces(self):
        grandparents = set()
        for parent in self.parents:
            for grandparent in parent.parents:
                grandparents.add(grandparent)
        return list(grandparents)


PHI = (1 + 5**0.5)/2

class Tetrahedron(Polyhedron):
    def __init__(self):
        vertices = [(1, 1, 1), (-1, -1, 1), (-1, 1, -1), (1, -1, -1)]
        faces = [[0, 1, 2], [0, 2, 3], [0, 1, 3], [1, 2, 3]]
        super().__init__(vertices, faces)


class Cube(Polyhedron):
    def __init__(self):
        vertices = [(1.0, 1.0, 1.0), (1.0, 1.0, -1.0), (1.0, -1.0, -1.0), (1.0, -1.0, 1.0), (-1.0, -1.0, 1.0), (-1.0, -1.0, -1.0), (-1.0, 1.0, -1.0),(-1.0, 1.0, 1.0)]
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
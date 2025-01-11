## Model class and subclasses for n-polytopes. Likewise, generalized NFace class and subclasses for n-faces, which are stored inside Models.

import arraymancer
import std/[enumerate, hashes, rationals, sequtils, sets, strformat, sugar, tables]

## Model and subtypes + Polyhedron and subtypes
type
  Model* = ref object of RootObj
    ## Containers for polytopes connected as one figure.
    rank*: int
    ambientRank*: int
    elements*: seq[HashSet[Polytope]]

  # Polytopes
  Point* = ref object of Polytope
    ## The 0-polytope.
  LineSegment* = ref object of Polytope
    ## The 1-polytope.
  Polygon* = ref object of Polytope
    ## The 2-polytope.
  Polyhedron* = ref object of Polytope
    ## The 3-polytope.
  Polychoron* = ref object of Polytope
    ## The 4-polytope.
  Polytope* = ref object of RootObj
    ## The n-polytope. Each instance is expected to have only one of
    ## `subfaces` and `coords`, though this is not enforced.
    model*: Model
    #rank: int
    subfaces*: HashSet[Polytope]
    coords*: seq[float]

  # Errors
  RankError = object of CatchableError
    ## Raised when procedure requires Polytope/Model of a different rank

# Hash functions
func hash(model: Model): Hash =
  ## Models are defined by their subfaces
  return hash(model.elements)
func hash(polytope: Polytope): Hash =
  # Not necessary. Also not even actually correct.
  return hash(polytope.subfaces) + hash(polytope.coords)

# Object creation functions
func newModel*(): Model =
  return Model()
func newModel*(rank: int, ambientRank: int): Model =
  ## Create instance of type Model
  return Model(rank: rank, ambientRank: ambientRank)
func newModel*(rank: int, ambientRank: int, elements: seq[HashSet[Polytope]]): Model =
  ## Create instance of type Model
  return Model(rank: rank, ambientRank: ambientRank, elements: elements)

func newPoint*(coords: seq[float]): Polytope =
  return Polytope(coords: coords)
func newPolytope*(coords: seq[float]): Polytope =
  return Polytope(coords: coords)
func newPolytope*(subfaces: HashSet[Polytope]): Polytope =
  return Polytope(subfaces: subfaces)

# Helper methods for polytopes
func `[]`*(polytope: Model, idx: int): HashSet[Polytope] =
  ## Alias for func `elements`
  return polytope.elements[idx]
func len*(polytope: Polytope): int =
  return len(polytope.subfaces)

func rank*(polytope: Polytope): int =
  # Find rank of polytope.
  if len(polytope.coords) > 0:
    return 0
  else:
    return rank(polytope.subfaces.toSeq()[0]) + 1

proc register*(model: Model, polytope: Polytope) =
  ## Add polytope to model.
  model.elements[polytope.rank()].incl(polytope)
proc registerAll*(model: Model, polytope: Polytope) =
  ## Recursively add polytope and all its elements to model.
  register(model = model, polytope = polytope)
  for subface in polytope.subfaces:
    registerAll(model = model, polytope = subface)

# Functions for finding related polytopic elements on same Model
func superfaces*(polytope: Polytope): HashSet[Polytope] =
  ## Alias for superfaces; that is, (n+1)-faces that contain self.
  var
    superfaces: HashSet[Polytope]
    nplus1faces = polytope.model.elements[polytope.rank + 1]
  for face in nplus1faces:
    if polytope in face.subfaces:
      superfaces.incl(polytope)
  return superfaces
func parents*(element: Polytope): HashSet[Polytope] =
  ## Alias for superfaces; that is, (n+1)-faces that contain self.
  return element.superfaces()
func siblings*(polytope: Polytope): HashSet[Polytope] =
  ## Return n-faces that share an (n+1)-face with self.
  var neighbours: HashSet[Polytope]
  for superface in polytope.superfaces():
    neighbours = neighbours + superface.subfaces
  #return neighbours.incl(polytope)
  return neighbours + toHashSet([polytope])
func neighbours*(polytope: Polytope): HashSet[Polytope] =
  ## Return n-faces that share an (n-1)-face with self.
  var neighbours: HashSet[Polytope]
  for subface in polytope.subfaces:
    neighbours = neighbours + subface.superfaces()
  return neighbours - toHashSet([polytope])
func neighbours*(polytope: Polytope, border_rank: seq[int]): HashSet[Polytope] =
  ## Return n-faces that share an m-face with self, where n is the rank of the polytope and m is the rank specified.
  # Is it better to specified the objective rank to count as border rank? Or should it be number of ranks below
func children*(polytope: Polytope): HashSet[Polytope] =
  ## Alias for subfaces property; that is, (n-1)-faces that self contains.
  return polytope.subfaces
func subfaces*(polytope: Polytope): HashSet[Polytope] =
  ## Alias for subfaces property; that is, (n-1)-faces that self contains.
  return polytope.subfaces
func nfaces*(polytope: Polytope, rank: int): HashSet[Polytope] =
  ## Return n-faces, where n is the "rank" argument, that are within self or that self is within.
  # TODO: Simply this function
  if rank > polytope.rank():
    var 
      faces = polytope.superfaces
      superfaces: HashSet[Polytope]
    while true:
      if toSeq(faces)[0].rank() == rank:
        return HashSet(faces)
      for superface in faces:
        superfaces = superfaces + superface.superfaces
      faces = superfaces
      superfaces.clear()
  elif rank == polytope.rank():
    return toHashSet([polytope])
  else:
    var
      faces = polytope.subfaces
      subfaces: HashSet[Polytope]
    while true:
      if toSeq(faces)[0].rank() == rank:
        return HashSet(faces)
      for subface in faces:
        subfaces = subfaces + subface.subfaces
      faces = subfaces
      subfaces.clear()

## Model functions for finding n-faces
func elements*(model: Model, rank: int): HashSet[Polytope] =
  ## Generic implementation.
  return model.elements[rank]
func facets*(model: Model): HashSet[Polytope] =
  ## (n-1)-faces.
  return model.elements[model.rank - 1]
func ridges*(model: Model): HashSet[Polytope] =
  ## (n-2)-faces.
  return model.elements[model.rank - 2]
func peaks*(model: Model): HashSet[Polytope] =
  ## (n-3)-faces.
  return model.elements[model.rank - 3]
func cells*(model: Model): HashSet[Polytope] =
  ## 3-faces.
  return model.elements[3]
func faces*(model: Model): HashSet[Polytope] =
  ## 2-faces.
  return model.elements[2]
func edges*(model: Model): HashSet[Polytope] =
  ## 1-faces.
  return model.elements[1]
func vertices*(model: Model): HashSet[Polytope] =
  ## 0-faces.
  return model.elements[0]

# Converters
converter toModel*(polytope: Polytope): Model =
  var elements: seq[HashSet[Polytope]]
  for rank in 0..polytope.rank():
    elements[rank] = polytope.nfaces(rank)
  return Model(elements: elements)
converter toPolytope*(model: Model): Polytope =
  return Polytope(subfaces: model.elements[^1])

# func centroid(polytope: Model): Point =
#   ## Average of positions in element.
#   let positions = [vertex.position for vertex in polytope.vertices]
#   centroid = []
#   for axis in range(len(positions[0])):
#     centroid.append(reduce(lambda a, b: a + b[axis], positions, 0)*Rational(1, len(positions)))
#   return Point(centroid)
func ambientRank*(model: Model): int =
  ## The number of dimensions in which the polytope resides in.
  ## Note that this is not always the rank of the shape itself,
  ## such as a square in a 3D space.
  return toSeq(model.vertices())[0].coords.len()

# Discardable procedures
proc echo*(polytope: Polytope) {.discardable.} =
  if len(polytope.subfaces) == 0:
    echo polytope.coords
  else:
    for subface in polytope.subfaces:
      echo polytope.coords
proc stats*(model: Model) {.discardable.} =
  ## Print number of vertices, edges, faces, etc.
  const nfaces = ["Vertices", "Edges", "Faces", "Cells"]
  var
    nface: string
    count: int
  for rank in 0 .. model.rank:
    if rank <= 3:
      nface = nfaces[rank]
    else:
      nface = &"{rank}-face"
    count = len(model.elements[rank])
    echo &"{nface}: {count}"
proc faceTypes*(polytope: Polytope) {.discardable.} =
  ## Print counts of each n-gon.
  const polygonNames = {
    3: "triangles", 4: "quadrilaterals", 5 :"pentagons", 6: "hexagons", 7: "heptagons",
    8: "octagons", 9: "nonagons", 10: "decagons", 11: "undecagons", 12: "dodecagons"}.toTable
  var polygonCounts: seq[int]
  for face in polytope.subfaces:
    polygonCounts.add(face.len())
  for key, value in polygonCounts.toCountTable.pairs:
    if key in polygonNames:
      echo &"{polygonNames[key]}: {value}"
    else:
      echo &"{key}-gon: {value}"

# Boolean checks on polytopes
func is_vertex*(polytope: Polytope): bool =
  if polytope.rank == 0:
    return true
  return false
# func is_canonical(polytope: Polytope): bool =
#   ## Return whether Polyhedron has midsphere. That is to say whether all edges form lines tangent to the same sphere.
#   if polytope.rank() != 3:
#     raise newException(RnkError, "Only defined for polytopes of rank 3.")
#   midradius = None
#   for edge in polytope.edges:
#     vertex1 = list(edge.vertices)[0]
#     vertex2 = list(edge.vertices)[1]
#     line = sympy.Line3D(sympy.Point3D(vertex1.coordinates), sympy.Point3D(vertex2.coordinates))
#     distance = line.distance(sympy.Point3D(0, 0, 0))
#     if midradius is None:
#       midradius = distance
#     elif not isclose(float(midradius), float(distance)):
#       return false
#   return true

# Under development
proc centroid*(polytope: Polytope): Tensor[float] =
  ## Average of positions in element.

  let positions = collect(newSeq):
    for vertex in polytope.nfaces(0):
      vertex.coords.toTensor()
  var
    # TODO: Generalize ambient dimension
    centroid = [0.0, 0.0].toTensor()
    #tensors: seq[Tensor[float]]
  #for vertex in polytope.vertices():
  #echo centroid
  #echo len(polytope.nfaces(0))
  #echo len(polytope.subfaces)
  # for vertex in polytope.nfaces(0):
  #   echo vertex.coords
  #   tensors.add(vertex.coords.toTensor())
  #   #echo foldl(vectors, a + b) #/len(polytope.vertices)
  for position in positions:
    #echo position
    centroid += position
  #centroid = centroid / len(polytope.nfaces(0))
  #echo centroid
  return centroid

echo $([[1, 2, 3], [4, 5, 6]].toTensor())


    # positions = [vertex.position for vertex in self.vertices]
    # centroid = []
    # for axis in range(len(positions[0])):
    #     centroid.append(reduce(lambda a, b: a + b[axis], positions, 0)*Rational(1, len(positions)))
    # return Point(centroid)


  # tuple(sum(np.array(vertices_coordinates))/len(vertices_coordinates))

proc createModel*(vertices: seq[seq[float]], elements: seq[seq[seq[int]]], withEdges=false): Model =
  ## Construct instance of class Polytope.
  ##
  ## Parameters
  ## ----------
  ## vertices: seq[seq[float]]
  ##     Sequence of coordinates.
  ## elements: seq[seq[seq[int]]]
  ##     All n-faces of rank 1 or higher, grouped by rank, starting with the lowest rank.
  ## withEdges: bool (Not yet implemented)
  ##     Specifies whether edges are included or if the lowest rank indicies actually correspond directly to vertices.
  var
    #new_elements: seq[seq[Polytope]]
    #new_elements: array[0 .. 2, seq[Polytope]]
    newElements = newSeqWith[len(elements) + 1, newSeq[Polytope]()]
    hashedElements: seq[HashSet[Polytope]]

  # Construct vertices
  for vertex in vertices:
    newElements[0].add(newPoint(coords = vertex))

  # TODO: Implement 
  # # Construct edges with `with_edges` set to `false`
  # if with_edges == false:
  #   var new_edges: HashSet[Polytope]
  #   for edge in elements[0]:
  #     for vertex_idx in edge:
  #       new_edges.incl(new_vertices[vertex_idx])
  #     #newPolytope(elements = )

  # Construct all other elements
  for rank, indicesOfPolytopes in enumerate(1, elements):
    var newNfaces: seq[Polytope]
    for polytopeIndices in indicesOfPolytopes:
      var newNface: HashSet[Polytope]
      for polytopeIdx in polytopeIndices:
        newNface.incl(new_elements[rank - 1][polytopeIdx])
      newNfaces.add(newPolytope(subfaces = newNface))
    newElements[rank].add(new_nfaces)

  # Convert seqs to HashSets
  for elementsOfRank in newElements:
    hashedElements.add(elementsOfRank.toHashSet() )
  #new_elements.map( (x) => x.toHashSet() )
  #new_elements.apply(proc(x) = x.toHashSet())

  # TODO: Fix ambient_rank
  return newModel(rank = len(elements), ambient_rank = len(elements), elements = hashedElements)

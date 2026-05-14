## Polytope class and subclasses for n-polytopes. Likewise, generalized NElement class and subclasses for n-faces, which are stored inside Polytopes.

#import arraymancer
import std/[enumerate, hashes, rationals, sequtils, sets, strformat, sugar, tables]

## Polytope and subtypes + Polyhedron and subtypes
type
  Polytope* = ref object of RootObj
    ## Containers for polytopes connected as one figure.
    rank*: int
    #ambientRank*: int
    elements*: seq[seq[Element]]

  # Polytopes
  # Point* = ref object of Polytope
  #   ## The 0-polytope.
  # LineSegment* = ref object of Polytope
  #   ## The 1-polytope.
  # Polygon* = ref object of Polytope
  #   ## The 2-polytope.
  # Polyhedron* = ref object of Polytope
  #   ## The 3-polytope.
  # Polychoron* = ref object of Polytope
  #   ## The 4-polytope.
  Element* = ref object of RootObj
    ## The n-polytope. Each instance is expected to have only one of
    ## `subfaces` and `coords`, though this is not enforced.
    polytope*: Polytope
    #rank: int
    subfaces*: HashSet[Element]
    coords*: Coords
  Coords* = seq[float]

  # Errors
  RankError* = object of CatchableError
    ## Raise when procedure requires Element/Polytope of a different rank
  CanonicalError* = object of CatchableError
    ## Raise when polytope is not canonical, but the operations requires it

# Hash functions
# func hash(model: Polytope): Hash =
#   ## Polytopes are defined by their subfaces
#   return hash(model.elements)
func hash*(element: Element): Hash =
  # Not necessary. Also not even actually correct.
  return hash(element.subfaces) + hash(element.coords)

# Object creation functions
func newPolytope*(): Polytope =
  return Polytope()
# func newPolytope*(rank: int, ambientRank: int): Polytope =
#   ## Create instance of type Polytope
#   return Polytope(rank: rank, ambientRank: ambientRank)
func newPolytope*(rank: int): Polytope =
  # Set the size of the elements seq based on the rank
  # return Polytope(rank: rank, elements: newSeq[seq[Element]](rank))
  # return Polytope(rank: rank, elements: @[@[]])
  return Polytope(rank: rank, elements: newSeq[seq[Element]](rank))

    
func newPolytope*(rank: int, elements: seq[seq[Element]]): Polytope =
  ## Create instance of type Polytope
  result = Polytope(rank: rank, elements: elements)
  # Set the parent polytope for each element
  for rank in result.elements:
    for element in rank:
      element.polytope = result

func newVertex*(coords: Coords): Element =
  return Element(coords: coords)
func newElement*(coords: Coords): Element =
  return Element(coords: coords)
func newElement*(subfaces: HashSet[Element]): Element =
  return Element(subfaces: subfaces)

# Helper methods for polytopes
func `[]`*(polytope: Polytope, idx: int): seq[Element] =
  ## Alias for func `elements`
  return polytope.elements[idx]
# func `[]`*(element: Element,)
func len*(element: Element): int =
  return len(element.subfaces)

# Helper methods for elements
func rank*(element: Element): int =
  # Find rank of polytope.
  if len(element.coords) > 0:
    return 0
  else:
    return rank(element.subfaces.toSeq()[0]) + 1
func `==`*(a, b: Element): bool =
  a.subfaces == b.subfaces
func `!=`*(a, b: Element): bool =
  a.subfaces != b.subfaces
func index*(element: Element): int =
  let idx = element.polytope.elements[element.rank()].find(element)  
  if idx == -1:
    raise newException(IndexDefect, "Element isn't listed in it's own polytope.")
  return idx
proc register*(polytope: Polytope, element: Element) =
  ## Add element to polytope.
  # if polytope.elements.len 
  # Add element to polytope
  polytope.elements[element.rank()].add(element)

  # Set reference for polytope in element
  element.polytope = polytope
proc register*(polytope: Polytope, elements: seq[Element]) =
  # Add multiple elements to polytope.
  for element in elements:
    polytope.register(element)
proc registerAll*(polytope: Polytope, element: Element) =
  ## Recursively add element and all its elements to polytope.
  register(polytope = polytope, element = element)
  for subface in element.subfaces:
    registerAll(polytope = polytope, element = subface)

## Discardable procedures
# Echo procedures
# proc `$`*(element: Polytope): string = 
#   if element.rank() == 0:
#     $(element.coords)
#   else:
#     &"{element.rank}-face"
proc echo*(element: Polytope) {.discardable.} =
  echo &"{element.rank}-polytope"
proc echo*(element: Element) {.discardable.} =
  if element.rank() == 0:
    echo element.coords
  else:
    echo &"{element.rank}-face"
    # for subface in element.subfaces:
    #   echo subface
# proc echo*(elements: HashSet[Element]) {.discardable.} =
#   stdout.write("{")
#   for element in elements:
#     stdout.write($element & ", ")
#   stdout.write("\b}")
# proc echo*(elements: seq[Element]) {.discardable.} =
#   stdout.write("[")
#   for element in elements:
#     stdout.write($element & ", ")
#   stdout.write("\b]")

# Functions for finding related elements related to another
# NOTE: Maybe want to redefine superfaces and subfaces to go beyond just n+1 and n-1, respectively
func superfaces*(element: Element): HashSet[Element] =
  ## Alias for superfaces; that is, (n+1)-faces that contain self.
  var
    superfaces: HashSet[Element]
    nplus1faces = element.polytope.elements[element.rank + 1]
  for face in nplus1faces:
    if element in face.subfaces:
      # debug
      # debugEcho "Subface" element
      superfaces.incl(face)
  return superfaces
func parents*(element: Element): HashSet[Element] =
  ## Alias for superfaces; that is, (n+1)-faces that contain self.
  return element.superfaces()
func siblings*(element: Element): HashSet[Element] =
  ## Return n-faces that share an (n+1)-face with self, besides self.
  var neighbours: HashSet[Element]
  for superface in element.superfaces():
    neighbours = neighbours + superface.subfaces
  #return neighbours.incl(element)
  return neighbours - toHashSet([element])
func neighbours*(element: Element): HashSet[Element] =
  ## Return n-faces that share an (n-1)-face with self.
  var neighbours: HashSet[Element]
  for subface in element.subfaces:
    # TODO: Use "incl()" if possible to not have to recreate the HashSet each time
    neighbours = neighbours + subface.superfaces()
  return neighbours - toHashSet([element])
func neighbours*(element: Element, borderRank: seq[int]): HashSet[Element] =
  ## Return n-faces that share an m-face with self, where n is the rank of the element and m is the rank specified.
  # Is it better to specify the objective rank to count as border rank? Or should it be number of ranks below
func children*(element: Element): HashSet[Element] =
  ## Alias for subfaces property; that is, (n-1)-faces that self contains.
  return element.subfaces
func subfaces*(element: Element): HashSet[Element] =
  ## Alias for subfaces property; that is, (n-1)-faces that self contains.
  return element.subfaces
func nfaces*(element: Element, rank: int): HashSet[Element] =
  ## Return n-faces, where n is the "rank" argument, that are within self or that self is within.
  # TODO: Simplify this function
  if rank > element.rank():
    var 
      faces = element.superfaces
      superfaces: HashSet[Element]
    while true:
      if toSeq(faces)[0].rank() == rank:
        return HashSet(faces)
      for superface in faces:
        superfaces = superfaces + superface.superfaces
      faces = superfaces
      superfaces.clear()
  elif rank == element.rank():
    return toHashSet([element])
  else:
    var
      faces = element.subfaces
      subfaces: HashSet[Element]
    while true:
      if toSeq(faces)[0].rank() == rank:
        return HashSet(faces)
      for subface in faces:
        subfaces = subfaces + subface.subfaces
      faces = subfaces
      subfaces.clear()
func intersectedParents*(elements: HashSet[Element]): HashSet[Element] =
  ## Find parent elements whose only children are those in the passed in as "elements"
  var parents: HashSet[Element]
  for element in elements:
    for parent in element.parents():
      block parentIt:
        for child in parent.children():
          if child notin elements:
              break parentIt
        parents.incl(parent)
  return parents
func areSiblings*(a, b: Element): bool =
  intersection(a.parents(), b.parents()).card() > 0


# func allSharedElements*(element1: Element, element2: Element): seq[HashSet[Element]] =
#   ## Find all elements that both are either inside of or contain.
#   ## Elements are separated by rank, where the idx is the rank.
  

## Polytope functions for finding n-faces
func elements*(polytope: Polytope, rank: int): seq[Element] =
  ## Generic implementation.
  return polytope.elements[rank]
func facets*(polytope: Polytope): seq[Element] =
  ## (n-1)-faces.
  return polytope.elements[polytope.rank - 1]
func ridges*(polytope: Polytope): seq[Element] =
  ## (n-2)-faces.
  return polytope.elements[polytope.rank - 2]
func peaks*(polytope: Polytope): seq[Element] =
  ## (n-3)-faces.
  return polytope.elements[polytope.rank - 3]
func cells*(polytope: Polytope): seq[Element] =
  ## 3-faces.
  return polytope.elements[3]
func faces*(polytope: Polytope): seq[Element] =
  ## 2-faces.
  return polytope.elements[2]
func edges*(polytope: Polytope): seq[Element] =
  ## 1-faces.
  return polytope.elements[1]
func vertices*(polytope: Polytope): seq[Element] =
  ## 0-faces.
  return polytope.elements[0]

# Converters
# converter toPolytope*(polytope: Element): Polytope =
#   let elements = collect:
#     for rank in 0..polytope.rank():
#       toSeq(polytope.nfaces(rank))
#   return Polytope(elements: elements)
converter toElement*(model: Polytope): Element =
  return Element(subfaces: toHashSet(model.elements[^1]))

# Functions for coordinates
func avg*(a, b: Coords): Coords =
  #var result = zip(a, b).mapIt(it[0] + it[1])
  var result = zip(a, b).mapIt(it[0] + it[1])
  result.applyIt(it / 2.0)
  result  # NOTE: For some reason it won't work without this line
func `+`(a, b: Coords): Coords =
  zip(a, b).mapIt(it[0] + it[1])
#func `/`(a: Coords, b: )
func midpoint*(edge: Element): Element =
  if edge.rank != 1:
    raise newException(RankError, "Only edges can have a midpoint.")
  let coordss = collect:
    for subface in edge.subfaces.toSeq():
      subface.coords
  newVertex(avg(coordss[0], coordss[1]))

# Find relations between elements
proc contains*(larger_element: Element, smaller_element: Element): bool =
  ## Return whether smaller_polytope is contained within the larger.
  ## This iterates through all elements down to vertices.
  ## Also returns true if both arguments are the same polytope.
  if larger_element == smaller_element:
    return true
  for subface in larger_element.subfaces:
    if contains(subface, smaller_element):
      return true
  return false
proc boundary*(element1: Element, element2: Element): HashSet[Element] =
  ## Find (n-1)-face that is the shared boundary between two n-faces.
  for subface in element1.subfaces:
    if subface in element2.subfaces:
      return [subface].toHashSet()
  var empty: HashSet[Element]
  return empty
proc isAdjacent*(element1: Element, element2: Element): bool =
  ## Check if there is an (n-1)-face that is a shared boundary between two n-faces.
  if len(element1.subfaces.intersection(element2.subfaces)) > 0:
    return true
  return false
# proc isMinimallyAdjacent*(element1: Element, element2: Element): bool =
#   ## Check if there is an element contained by both elements.
# proc highestCommon*(larger_element: Element, smaller_element: Element): Element =
#   ## Find element that is one less dimension than the larger_element that also contains the smaller_element.
#   let elements = collect:
#     for subface in larger_element.subfaces:
#       if 

func ambientRank*(model: Polytope): int =
  ## The number of dimensions in which the polytope resides in.
  ## Note that this is not always the rank of the shape itself,
  ## such as a square in a 3D space.
  return toSeq(model.vertices())[0].coords.len()

# Find new elements
# proc centroid*(polytope: Element): seq[float] =
#   ## Average of positions in element.
#   let positions = collect(newSeq):
#     for vertex in polytope.nfaces(0):
#       vertex.coords.toTensor()
#   var summed_positions = repeat(0.0, polytope.ambientRank()).toTensor()
#   for position in positions:
#     #echo position
#     summed_positions += position
#   # This commented line inexplicably is not working, so instead wrote it in a longer way below.
#   # It was saying: Error: To subtract a scalar from a tensor you must use the `-.` operator (instead of a plain `-` operator)
#   # centroid = centroid /. len(polytope.nfaces(0)).float()
#   var centroid = collect:
#     for num in summed_positions.toSeq1D():
#       num / len(polytope.nfaces(0)).float()
#   return centroid


proc stats*(polytope: Polytope) {.discardable.} =
  ## Print number of vertices, edges, faces, etc.
  const nfaces = ["Vertices", "Edges", "Faces", "Cells"]
  var
    nface: string
    count: int
  for rank in 0 .. polytope.rank - 1:
    if rank <= 3:
      nface = nfaces[rank]
    else:
      nface = &"{rank}-face"
    count = len(polytope.elements[rank])
    echo &"{nface}: {count}"
proc faceTypes*(polytope: Element) {.discardable.} =
  ## Print counts of each n-gon.
  const polygonNames = {
    # 0: "zerogon", 1: "monogons", 2: "digons",
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
func isPoint*(polytope: Polytope): bool =
  if polytope.rank == 0:
    return true
  return false
# func is_canonical(polytope: Element): bool =
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
func isIsogonal*(polytope: Polytope): bool =
  ## Return whether polytope is vertex-transitive.
  ## That is, that all vertices and surrounding environment is identical.
func isIsotoxal*(polytope: Polytope): bool =
  ## Return whether polytope is edge-transitive.
func isIsohedral*(polytope: Polytope): bool =
  ## Return whether polytope is face-transitive.
func isRegular*(polytope: Polytope): bool =
  ## .
func isUniform*(polytope: Polytope): bool =
  ## .
func isCanonical*(polytope: Polytope): bool =
  ## TODO: Implement this
  return true
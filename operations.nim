## Polyhedron operations (and closely related functions)
# Note that not all parameters mentioned actually work yet. This is a layout for how the function will work.

import std/[enumerate, rationals, sequtils, sets, sugar]

# Local imports
import polytope #, geometry

# Enums for operation patterns
type
  TruncationPattern* = enum
    ## Describes how to determine which elements to truncate.
    all,
    alternate  # Alternate every other vertex. Only works on shapes where this would be possible.
  Midpoint* = enum 
    ## Desribes where to determine where `fraction` cuts towards.
    canonicalSphere,  # Intersection with insphere, midsphere, etc.
    centroid  # Average of points

#proc find_equation(points: seq[])

# proc pointClosestToOrigin(Element: Element): Element =
#   ## Find point on element closest to origin.


# proc findTruncationFractions(): seq[] =
#   ## Find the positions from n-face to center along which each of
#   ## rectification, birectification, trirectification, etc are met.
#   ## This should be helpful for animating truncation.

proc truncate*(
  polytope: Polytope;
  depth = 1//3,
  #ranks: set[int8] = {0},
  ranks: seq[int8] = @[0],
  allowOverlap: bool = false,
  pattern: TruncationPattern = TruncationPattern.all,
  midpoint: Midpoint = Midpoint.centroid,
  elements: HashSet[Element]): Element =
  ## Cut n-faces to create new facets.
  ## 
  ## Parameters
  ## ----------
  ## polytope: Polytope
  ##     The polytope to be truncated.
  ## depth: Rational|int
  ##     The fraction towards rectification.
  ##     For example, 1/2 would cut halfway to the rectified polytope.
  ##     `Rational(1)` is equivalent to rectifying.
  ##     Likewise, 2 birectifies.
  ##     `Rational(4, 3)` would give a polytope truncation between rectification and birectification.
  ## ranks: set[int8]
  ##     Specifies which n-faces should be truncated.
  ##     For instance, `{0, 1}` would truncate both vertices and edges (also known as cantellation).
  ##     The default `{0}` truncates only vertices.
  ## allowOverlap: bool
  ##     Flag for whether to allow hypertruncation. That is, inversing edges after they become a point.
  ##     Truncations with `fraction` from 0 to 1/2 will be identical when this is set to true.
  ##     Beyond that, a value of false will cause larger values to lead to
  ##     bitruncation, birectification, tritruncation, etc.
  ##     If true, larger than 1/2 values will lead to
  ##     hypertruncation, quasitruncation, and antitruncation before cycling back again.
  ## pattern: str
  ##     Determines which elements to truncate.
  ##     `all` (default): Truncates all of the elements of the specified dimension.
  ##     `alternate`: Truncates every other. That is, no two adjacent n-faces. Not all polytopes are compatible.
  ## elements: HashSet[Element]
  ##     Specifies which elements are to be truncated. If specified, takes priority over `pattern` parameter.
  ##     By default, all n-faces of the specified dimensions from `nfaces` are truncated.
  ##     Otherwise, only those in the passed set will be truncated.

  proc truncateElement(element: Element, depth: Rational): Polytope {.discardable.} =
    ## Cut off element from a polytope. Called by proc truncate.
    ## Should I cut off one element at a time? Correcting any adjacent elements before cutting off the next?
    ## Also, should the fraction really be measured along the edges? Or towards center of shape?
    ## If a vertex has edges of all different lengths, the fraction can't be the same along all adjacent edges
    ## or else the new facet will not be planar. Should nonplanar faces be allowed?
    # Find every pair of edges that are adjacent
    let
      superfaces = element.superfaces()
      new_vertices = collect:
        for superface in superfaces:
          # TODO: Generalize
          superface.centroid()


    # # Option 1: Starting from small elements to larger
    # for superface in superfaces:
    #   for supr

    var previous_element: Element

    # proc subfacesDepthFirstSearch(larger_polytope: Element, smaller_polytope: Element): bool =
    # ## Return whether smaller_polytope is contained within the larger.
    # ## This iterates through all elements down to vertices.
    # ## Also returns true if both arguments are the same polytope.
    #   if larger_polytope == smaller_polytope:
    #     return true
    #   for subface in larger_polytope.subfaces:
    #     if subfacesDepthFirstSearch(subface, smaller_polytope):
    #       previous_element = smaller_polytope
    #       return true
    #   return false

    # Option 2: Start from facets and go down before going back up
    # let overlappingElementts = collect:
    #   for facet in model.facets():
    #     if facet.contains(element):
    #       facet

    let overlappingElementts = element.facets()

    # for facet in overlappingElementts:



    return polytope

  # Check polytope is canonical
  # if not polytope.is_canonical():
  #   raise CanonicalError

  # if pattern == TruncationPattern.all:
  #   for rank in ranks:
  #     # Iterate through each element of polytope to truncate
  #     for element in polytope.nfaces(rank):
  #       element.truncate

  # # Create new facets
  # if elements.type() is Element:
  #   for element in elements:
  #     model.truncateElement(element, fraction=fraction)
  #   # Find neighbouring edges
  # else:
  #   for rank in ranks:
  #     for element in model.nfaces(rank):
  #       model.truncateElement(element, fraction=fraction)
  # return model

  # for rank in 1..polytope.rank: # Or is it 0?
  #   for nface in polytope.elements(rank):

  #     # Create line from center to vertex
  #     # TODO: Create line function
  #     line = Line(polytope.center, vertex)
  #     # Shift down line
  #     new_vertex = translate(vertex, polytope.center, fraction)
  #     # Find n-1 plane that is perpendicular to line at the new vertex
  #     normal = line.perpendicular(new_vertex)

  #     # Find reduced length from intersecting lines and then create new n-1 plane between ends of overlapping parts

  #     # For every neighbouring facet, iterate down to edges,
  #     new_facets = []
  #     for facet in vertex.neighbouring_facets():
  #       new_facets.append(facet.intersect(normal))
  #     # finding intersections with plane, and constructing polygons.
  #     # Then build the higher elements on the way back up.


#     # for edge in self.edges:
#     #     x, y = symbols('x y')
#     #     x1 = edge.vertices[0].coords
#     #     x2 = edge.vertices[0].coords
#     #     m = (y2 - y1)/(x2 - x1)
#     #     line_equation = Eq(y - y1, m*(x - x1) )



###### Unimplemented operations ######
# Specific types of truncation. These all can be callsed just from truncation
# proc midpoint(E)

proc rectify*(polytope: Polytope, depth = 1, allowOverlap = false): Polytope =
  ## Truncate to where new faces meet at shared vertices.
  if polytope.rank != 3:
    raise newException(RankError, "Operation not implemented for ranks other than 3.")
  var new_polytope = newPolytope(rank = polytope.rank)

  # Create new vertices at midpoints
  var new_vertices: seq[Element]
  for edge in polytope.edges:
    new_vertices.add(edge.midpoint())
  new_polytope.register(new_vertices)

  # Create new edges
  var new_edges: seq[Element]
  for edge_idx, edge in enumerate(polytope.edges):
    for neighbour in edge.neighbours():
      let
        neighbour_idx = polytope.edges.find(neighbour)
        new_edge = newElement(
          subfaces = @[new_vertices[edge_idx], new_vertices[neighbour_idx]].toHashSet()
        )
      if new_edge notin new_edges:
        new_edges.add(new_edge)
  new_polytope.register(new_edges)

  # Modify faces from existing faces
  # Logic: old_faces -> old_edges -> new_vertices -> new_edges -> modified_faces
  # New faces in the same order as the original they come from
  var new_faces: seq[Element]
  for face in polytope.faces():
    var new_vertices_of_face: HashSet[Element]
    for edge in face.subfaces:
      new_vertices_of_face.incl(polytope.vertices[edge.index()])
    new_faces.add(newElement(
      subfaces = new_vertices_of_face.intersectedParents()
    ))
  new_polytope.register(new_faces)

  # Create faces by filling in gaps of the newly modified faces
  # Logic option: old vertices -> old_edges -> new_vertices -(intersectedParents)> new_edges -> new_faces
  var new_faces2: seq[Element]
  for vertex in polytope.vertices:
    # Find parental edges of original vertices
    var old_edges = collect:
      for parent in vertex.parents:
        {parent}
    # Find the new vertices that surround where the original vertex was 
    var new_vertices2 = collect():
      for edge in old_edges:
        {new_polytope.vertices[edge.index()]}
    new_faces2.add(newElement(
      subfaces = new_vertices2.intersectedParents()
    ))
  new_polytope.register(new_faces2)
      



  # var new_faces_from_vertices: seq[Element]
  # for vertex in polytope.vertices():
    
  # var new_face_subfaces: seq[Element]
  # for vertex_idx, vertex in enumerate(polytope.vertices()):
  #   if vertex in face.nfaces(0):
  #     new_face_subfaces.add(new_edges[vertex_idx])
  # new_faces.add(newElement(
  #   subfaces = new_face_subfaces.toHashSet()
  # ))


  return new_polytope
proc bitruncate*(polytope: Polytope, depth = 4//3, allowOverlap = false): Polytope =
  ## Truncate beyond rectification.
proc birectify*(polytope: Polytope, allowOverlap = false): Polytope =
  ## .
  # return polytope.truncate(polytope, depth=2, allowOverlap=false)
proc tritruncate*(polytope: Polytope, depth = 7//3, allowOverlap = false): Polytope =
  ## .
proc trirectify*(polytope: Polytope, depth = 3, allowOverlap = false): Polytope =
  ## .
proc reciprocate*(polytope: Polytope): Polytope =
  ## Perform reciprocation operation. Convert each face
  ## into a vertex and connect each new adjacent vertex.
  ## While this operation can be thought of as a type of truncation,
  ## it is implemented differently in order to speed up computation.
  ## Depending on polytope and arguments specified, this implementation creates skew faces on some polyhedra.
proc alternate*(polytope: Polytope, depth = 1//3, allowOverlap = false): Polytope =
  ## Alternatively truncate on vertices.
  #return polytope.truncate(ranks={0}, depth=depth, allowOverlap=false, pattern=truncation_pattern.alternate)
proc chamfer*(polytope: Polytope, depth = 1//3, allowOverlap = false): Polytope =
  ## Truncation on vertices and edges.
  #return polytope.truncate(ranks={1}, depth=depth, allowOverlap=false)
proc edgeTruncate*(polytope: Polytope, depth = 1//3, allowOverlap = false): Polytope =
  ## Alias of chamfer.
  #return polytope.truncate(ranks={1}, depth=depth, allowOverlap=false)
proc cantellate*(polytope: Polytope, depth = 1//3, allowOverlap = false): Polytope =
  ## Truncation on vertices and edges.
  #return polytope.truncate(ranks={0, 1}, depth=depth, allowOverlap=false)
proc bevel*(polytope: Polytope, depth = 1//3, allowOverlap = false): Polytope =
  ## Incompletely cantellate.
proc runcinate*(polytope: Polytope, depth = 1//3, allowOverlap = false): Polytope =
  ## Truncation on vertices, edges, and faces.
  #return polytope.truncate(ranks={0, 1, 2}, depth=depth, allowOverlap=False)
proc stericate*(polytope: Polytope,
  depth = 1//3,
  allowOverlap = false,
  pattern = TruncationPattern.all,
  elements: HashSet[Element]): Polytope =
  ## Truncation on vertices, edges, faces, and cells.
  # return polytope.truncate(
  #   ranks={0, 1, 2, 3},
  #   depth=depth,
  #   allowOverlap=allowOverlap,
  #   pattern = TruncationPattern.all,
  #   elements: HashSet[Element]
  # )
proc pentellate*(polytope: Polytope, depth = 1//3, allowOverlap = false): Polytope =
  ## Truncation on vertices, edges, and faces.
  #return polytope.truncate(ranks={0, 1, 2, 3, 4}, depth=depth, allowOverlap=False)
proc hexicate*(polytope: Polytope, depth = 1//3, allowOverlap = false): Polytope =
  ## Truncation on vertices, edges, and faces.
  #return polytope.truncate(ranks={0, 1, 2, 3, 4, 5}, depth=depth, allowOverlap=False)
proc omnitruncate*(polytope: Polytope, depth = 1//3, allowOverlap = false): Polytope =
  ## Truncate along all elements of polytope.
  ## For example, for a polyhedron this would be cantellation, while for a polychoron, would be runcination.
proc hypertruncate*(polytope: Polytope, depth = 2, allowOverlap = true): Polytope =
  ## .
proc quasitruncate*(polytope: Polytope, depth = 3, allowOverlap = true): Polytope =
  ## .
proc antitruncate*(polytope: Polytope, depth = -1, allowOverlap = true): Polytope =
  ## Instead of cutting off vertices, extend vpolytope outward at vertices to create pyramids hanging off of original polytope.
proc facet*(polytope: Polytope): Polytope =
  ## Perform facet operation. Maintain all previous vertices, but connect them differently
  ## to form new faces on a nonconvex figure.

# Types of augmentation
proc augment*(polytope: Polytope, depth = 1//3, allowOverlap = false): Element =
  ## Add vertex to middle of facets, connecting the vertex to the facets's vertices.
  ## This effectively either adds a hyperpyramid to each facets if `depth` is positive,
  ## cuts out a hyperpyramid if negative, or splits each facet into new coplanar facets if zero.
proc cap*(polytope: Polytope): Polytope =
  ## Augment outward.
  # augument(polytope=polytope, depth=1//3)
proc bridge*(polytope: Polytope): Polytope =
  ## Augment outward enough for neighbouring facet's hyperpyramids to align such that their facets become coplanar.
  ## This is defined as a depth of 1.
  # augument(polytope=polytope, depth=1)
proc triangulate*(polytope: Polytope): Polytope =
  ## Split faces into new coplanar faces. Equivalent to an augmentation of depth 0.
  # augument(polytope=polytope, depth=0)
proc excavate*(polytope: Polytope): Polytope =
  ## Inversion of augmentation. Remove pyramid from polytope's face.
# Types of stellation
proc stellate*(polytope: Polytope, nthStellation: int = 2): Polytope =
  ## Extends edges until meeting other edges, creating new vertices and changing shape of faces.
  ## The base polyhedron is designated as the first stellation, or nth_stellation=1.
proc greaten*(polytope: Polytope): Polytope =
  ## Extend faces to form new larger faces.

# Compound operations
proc uncouple*(polytope: Polytope): HashSet[Polytope] =
  ## Separate compound polyhedra.
proc compound*(polytope: Polytope, n: int): Polytope =
  ## Create a compound of n polytopes. Only works if such a symmetric polytope exists.
  ## There may also be multiple different compounds.

# Operations to extend into next spatial dimension
proc increaseAmbientDimension*(polytope: Polytope) =
  ## Add a final coordinate to vertices
  for vertex in polytope.vertices:
    vertex.coords.add(0)
proc prismate*(polytope: Polytope): Polytope =
  ## Drag polytope into adjacent dimension to create a prism of the original polytope.
  ## For example, rectange -> rectangular prism.
  # TODO: Work on this implementation
  # polytope.increaseAmbientDimension()
  # for vertex in polytope.vertices:
  #   new_vertex = vertex.coords[^1] 

proc pyramidate*(polytope: Polytope, height: float = 1.0): Polytope =
  ## Connect vertices to a new vertex (an apex) in the next higher dimension.
  ## For example, square -> square pyramid.
  # polytope.increaseAmbientDimension()
  # let
  #   new_vertex = newVertex(newSeq[float64](polytope.rank) & @[height])
  #   edges = collect:
  #     # Create edges connecting the new apex to every other one
  #     for vertex in polytope.vertices:
  #       {Element(subfaces: toHashSet([vertex, new_vertex]))}
  # var kfaces = edges
  # while rank < polytope.rank:
  #   for kface in kfaces:
  #     discard
      
  #   rank += 1

proc frustumate*(polytope: Polytope, fraction = 0.5, height = 1.0): Polytope =
  ## Create frustum using polytope as base. When fraction is 1.0, create pyramid instead.
  if fraction == 1.0:
    return pyramidate(polytope)
  ## TODO: Finish
  discard

proc cupolate*(polytope: Polytope): Element =
  ## Turn n-polytope in the base of an (n+1)-cupola.
  ## For example, cube -> cubic cupola.

# Other operations
proc decompose*(polytope: Polytope): Polytope =
  ## Slice polyhedron into two or more parts. If not decomposable, return self.
proc snubify*(polytope: Polytope): Polytope =
  ## Perform snub operation on polytope. Replace edges with a trail of triangles.
  ## This requires rotating the positions of existing faces.
proc canonize*(polytope: Polytope, rank: int = 3): Polytope =
  ## Adjust n-faces of specific rank so that each one's closest point to the origin is equidistant.
  ## For many operations, it is ideal to work on canonized polytopes to guarantee a valid resulting polytope.
  ## However, this operation is computationally expensive.

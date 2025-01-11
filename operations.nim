## Polyhedron operations (and closely related functions)
# Note that not all parameters mentioned actually work yet. This is a layout for how the function will work.

import std/[rationals, sets]

# Local imports
import polytope


# Enums for operation patterns
type
  TruncationPattern* = enum
    ## Describes how to determine which elements to truncate.
    all, alternate
  Midpoint* = enum 
    ## Desribes where to determine where `fraction` cuts towards.
    canonicalSphere,  # Intersection with insphere, midsphere, etc.
    centroid  # Average of points

#proc find_equation(points: seq[])

# proc pointClosestToOrigin(polytope: Polytope): Polytope =
#   ## Find point on element closest to origin.

proc truncateElement(model: Model, element: Polytope, fraction: Rational): Model =
  ## Cut off element from a polytope. Called by proc truncate.
  ## Should I cut off one element at a time? Correcting any adjacent elements before cutting off the next?
  ## Also, should the fraction really be measured along the edges? Or towards center of shape?
  ## If a vertex has edges of all different lengths, the fraction can't be the same along all adjacent edges
  ## or else the new facet will not be planar. Should nonplanar faces be allowed?

  # Find every pair of edges that are adjacent
  var superfaces = element.superfaces()
  for superface in superfaces:
    # Find point where superface is closest to center
    var midpoint = superface.pointClosestToOrigin()

proc truncate*(
  #polytope: Polytope;
  model: Model;
  fraction = 1//3,
  #ranks: set[int8] = {0},
  ranks: seq[int8] = @[0],
  hyper: bool = false,
  pattern: TruncationPattern = TruncationPattern.all,
  midpoint: Midpoint = Midpoint.centroid,
  elements: HashSet[Polytope]): Polytope =
  ## Cut n-faces to create new facets.
  ## 
  ## Parameters
  ## ----------
  ## polytope: Polytope
  ##     The polytope to be truncated.
  ## fraction: Rational|int
  ##     The fraction towards rectification.
  ##     For example, 1/2 would cut halfway to the rectified polytope.
  ##     `Rational(1)` is equivalent to rectifying.
  ##     Likewise, 2 birectifies.
  ##     `Rational(4, 3)` would give a polytope truncation between rectification and birectification.
  ## ranks: set[int8]
  ##     Specifies which n-faces should be truncated.
  ##     For instance, `{0, 1}` would truncate both vertices and edges (also known as cantellation).
  ##     The default `{0}` truncates only vertices.
  ## hyper: bool
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
  ## elements: HashSet[Polytope]
  ##     Specifies which elements are to be truncated. If specified, takes priority over `pattern` parameter.
  ##     By default, all n-faces of the specified dimensions from `nfaces` are truncated.
  ##     Otherwise, only those in the passed set will be truncated.


  # Create new facets
  # if elements.type() is Polytope:
  #   for element in elements:
  #     model.truncateElement(element, fraction=fraction)
  #   # Find neighbouring edges
  # else:
  #   for rank in ranks:
  #     for element in polytope.nfaces(rank):
  #       model.truncateElement(element, fraction=fraction)
  return model

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

# Specific types of truncation
proc alternate*(polytope: Polytope, fraction = 1//3, hyper = false): Polytope =
  ## Alternatively truncate on vertices.
  #return polytope.truncate(nfaces={0}, fraction=fraction, hyper=false, pattern=truncation_pattern.alternate)
  return polytope
proc chamfer*(polytope: Polytope, fraction = 1//3, hyper = false): Polytope =
  ## Truncation on vertices and edges.
  #return polytope.truncate(nfaces={1}, fraction=fraction, hyper=false)
  return polytope
proc edgeTruncate*(polytope: Polytope, fraction = 1//3, hyper = false): Polytope =
  ## Alias of chamfer.
  #return polytope.truncate(nfaces={1}, fraction=fraction, hyper=false)
  return polytope
proc cantellate*(polytope: Polytope, fraction = 1//3, hyper = false): Polytope =
  ## Truncation on vertices and edges.
  #return polytope.truncate(nfaces={0, 1}, fraction=fraction, hyper=false)
  return polytope
proc runcinate*(polytope: Polytope, fraction = 1//3, hyper = false): Polytope =
  ## Truncation on vertices, edges, and faces.
  #return polytope.truncate(nfaces={0, 1, 2}, fraction=fraction, hyper=False)
  return polytope
proc stericate*(polytope: Polytope,
  fraction = 1//3,
  hyper = false,
  pattern = TruncationPattern.all,
  elements: HashSet[Polytope]): Polytope =
  ## Truncation on vertices, edges, faces, and cells.
  # return polytope.truncate(
  #   nfaces={0, 1, 2, 3},
  #   fraction=fraction,
  #   hyper=hyper,
  #   pattern = TruncationPattern.all,
  #   elements: HashSet[Polytope]
  # )
  return polytope
proc facet*(polytope: Polytope): Polytope =
  ## Perform facet operation. Maintain all previous vertices, but connect them differently
  ## to form new faces on a nonconvex figure.
  return polytope

# Types of augmentation
proc augment*(polytope: Polytope): Polytope =
  return polytope
proc cap*(polytope: Polytope): Polytope =
  return polytope
proc bridge*(polytope: Polytope): Polytope =
  return polytope

# Types of stellation
proc stellate*(polytope: Polytope, nthStellation: int = 2): Polytope =
  ## Extends edges until meeting other edges, creating new vertices and changing shape of faces.
  ## The base polyhedron is designated as the first stellation, or nth_stellation=1.
  return 
proc greaten*(polytope: Polytope): Polytope =
  ## Extend faces to form new larger faces.
  return polytope

# Compound operations
proc uncouple*(polytope: Polytope): HashSet[Polytope] =
  ## Separate compound polyhedra.
  return [polytope].toHashSet()
proc compound*(polytope: Polytope, n: int): Polytope =
  ## Create a compound of n polytopes. Only works if such a symmetric polytope exists.
  ## There may also be multiple different compounds.
  return polytope

# Other operations
proc reciprocate*(polytope: Polytope): Polytope =
  ## Perform reciprocation operation. Convert each face
  ## into a vertex and connect each new adjacent vertex.
  ## While this operation can be thought of as a type of truncation,
  ## it is implemented differently in order to speed up computation.
  ## Depending on polytope and arguments specified, this implementation creates skew faces on some polyhedra.
  return polytope
proc decompose*(polytope: Polytope): Polytope =
  ## Slice polyhedron into two or more parts. If not decomposable, return self.
  return polytope
proc snubify*(polytope: Polytope): Polytope =
  ## Perform snub operation on polytope. Replace edges with a trail of triangles.
  ## This requires rotating the positions of existing faces.
  return polytope
proc canonize*(polytope: Polytope, rank: int = 3): Polytope =
  ## Adjust n-faces of specific rank so that each one's closest point to the origin is equidistant.
  ## For many operations, it is ideal to work on canonized polytopes to guarantee a valid resulting polytope.
  ## However, this operation is computationally expensive.
  return polytope

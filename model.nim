import polytope
import std/[enumerate, sequtils, sets, sugar, tables]

type
  # These models are in a format to pass to THREE.js for rendering
  Model = ref object of RootObj
  FaceModel* = ref object of Model
    # Used for modeling solid polytope in three.js
    vertices*: seq[cfloat]
    faces*: seq[cint]
  EdgeModel* = ref object of Model
    # Used for modeling wireframe of polytope in three.js
    vertices*: seq[cfloat]
    edges*: seq[cint]

proc echo*(model: FaceModel) {.discardable.} =
  echo "FaceModel:"
  echo model.vertices
  echo model.faces
proc echo*(model: EdgeModel) {.discardable.} =
  echo "EdgeModel:"
  echo model.vertices
  echo model.edges

proc orderVertices*(element: Element): seq[Element] =
  ## Order vertices of a face. Takes face and returns ordered vertices
  # Create a new set where elements can be popped
  var 
    unordered_vertices = collect: 
      for edge in element.subfaces:
        for vertex in edge.subfaces:
          {vertex}
    ordered_vertices = @[unordered_vertices.pop()]
  # Follow path through edges using vertices
  while card(unordered_vertices) > 0:
    for vertex in unordered_vertices:
      # If vertices share a parent
      if intersection(vertex.parents, ordered_vertices[^1].parents).card == 1:
        ordered_vertices.add(vertex)
        break
    unordered_vertices.excl(ordered_vertices[^1])
  return ordered_vertices

proc toFaceModel*(polytope: Polytope): FaceModel =
  ## Unpack coordinates into a single list, each three corresponding to a vertex
  let coordinates = collect:
    for vertex in polytope.vertices:
      for coord in vertex.coords:
        coord.cfloat()
  # Order vertices of face
  var unpacked_indices: seq[cint]
  for face in polytope.faces:
    var indices = collect:
      for vertex in face.orderVertices():
        vertex.index().cint()
    # Create triangles all coming off of the first vertex
    for n in 1..len(indices)-2:
      unpacked_indices.add(indices[0])
      unpacked_indices.add(indices[n])
      unpacked_indices.add(indices[n+1])     
  return FaceModel(vertices: coordinates, faces: unpacked_indices)
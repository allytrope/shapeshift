## Convert polytopes into different representations.
import polytope
import std/[enumerate, sequtils, sets, sugar]

proc createPolytope*(vertices: seq[seq[float]], elements: seq[seq[seq[int]]], withEdges=false): Polytope =
  ## Construct instance of class Element.
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
    #new_elements: seq[seq[Element]]
    #new_elements: array[0 .. 2, seq[Element]]
    newElements = newSeqWith[len(elements) + 1, newSeq[Element]()]
    hashedElements: seq[HashSet[Element]]

  # Construct vertices
  for vertex in vertices:
    newElements[0].add(newVertex(coords = vertex))

  # TODO: Implement 
  # # Construct edges with `with_edges` set to `false`
  # if with_edges == false:
  #   var new_edges: HashSet[Element]
  #   for edge in elements[0]:
  #     for vertex_idx in edge:
  #       new_edges.incl(new_vertices[vertex_idx])
  #     #newElement(elements = )

  # Construct all other elements
  for rank, indicesOfElements in enumerate(1, elements):
    var newNfaces: seq[Element]
    for polytopeIndices in indicesOfElements:
      var newNface: HashSet[Element]
      for polytopeIdx in polytopeIndices:
        newNface.incl(new_elements[rank - 1][polytopeIdx])
      newNfaces.add(newElement(subfaces = newNface))
    newElements[rank].add(new_nfaces)

  # # Convert seqs to HashSets
  # for elementsOfRank in newElements:
  #   hashedElements.add(elementsOfRank.toHashSet() )
  #new_elements.map( (x) => x.toHashSet() )
  #new_elements.apply(proc(x) = x.toHashSet())

  # TODO: Fix ambient_rank
  var rank: int
  if with_edges == true:
    rank = len(elements) + 1
  else:
    rank = len(elements) + 2
  return newPolytope(rank = rank, elements = newElements)



# Functions for representing polytopes with indices. Often for plotting.

proc index*(polytope: Polytope, withEdges = false): tuple[vertices: seq[seq[float]], nfaces: seq[seq[seq[int]]]] =
  ## Convert a polytope into a container of indicies.
  ## Edges themselves are not recorded. Rather, faces are defined directly by their vertices.
  ## This is useful for rendering with other tools.
  let
    # Determine whether to skip edges
    rankOfElementIndices = if withEdges == true: 1 else: 2
    # Collect positions
    vertices = collect:
      for vertex in polytope.vertices():
        vertex.coords

    # Collect edges
    edges = collect:
      for edge in polytope.edges():
        collect:
          for vertex in edge.subfaces:
            polytope.nfaces(0).find(vertex)

    # Collect faces
    faces = collect:
      for face in polytope.faces():
        if withEdges == true:
          collect:
            for edge in face.nfaces(1):
              polytope.nfaces(1).find(edge)
        else:
          collect:
            #echo len(face.vertices())
            echo len(face.nfaces(0))
            for vertex in face.nfaces(0):
              polytope.nfaces(0).find(vertex)
              

    # # Collect n-faces
    # indexed_nfaces = collect:
    #   # Iterate over ranks
    #   for rank in startingRank .. (polytope.rank() - 1):
    #     # Allow for skipping edges when finding subfaces of face
    #     let subfaceRank = if rank == 2: 0 else: rank - 1
    #     collect:
    #       # Iterate over faces in rank
    #       for nface in polytope.nfaces(subfaceRank):
    #         collect:
    #           echo "test1"
    #           echo nface.rank()
    #           # Iterate of subfaces to find each's index
    #           for subface in nface.subfaces:
    #             echo "test2"
    #             polytope.nfaces(subfaceRank - 1).find(subface)
    nfaces = if withEdges == true: @[edges, faces] else: @[faces]

  return (vertices, nfaces)

# proc triangulate*(polytope: Element): tuple[seq[float], seq[int]] =
#   ## Convert a polytope into a container of indicies.
#   ## This further breaks down faces into triangles for rendering.
#   ## This unpacks vertex coordinates and faces.
#   ## This is useful for plotting using a PolyhedronGeometry from THREE.js
#   let vertices, faces = index(polytope, withEdges=false)

# proc unpack*()
#   ## Unpack nested lists into a single one.
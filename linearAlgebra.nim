import polytope
import std/[enumerate, math, sequtils, sets, sugar]

type PlaneEquation* = tuple
  ## Represents a plane equation: normal · x = d
  normal: Coords
  d: float
# # ============================================================================
# # Plane intersection functions
# # ============================================================================
func dot*(a, b: Coords): float =
  ## Compute dot product of two coordinate vectors.
  return zip(a, b).mapIt(it[0] * it[1]).foldl(a + b)

func subtract*(a, b: Coords): Coords =
  ## Subtract coordinate vector b from a.
  return zip(a, b).mapIt(it[0] - it[1])

func cross3d*(a, b: Coords): Coords =
  ## Compute 3D cross product. Returns (a[0]*b[1] - a[1]*b[0], ...).
  ## Requires exactly 3 coordinates.
  if a.len != 3 or b.len != 3:
    raise newException(ValueError, "3D cross product requires 3-coordinate vectors")
  return @[
    a[1] * b[2] - a[2] * b[1],
    a[2] * b[0] - a[0] * b[2],
    a[0] * b[1] - a[1] * b[0]
  ]

func magnitude*(v: Coords): float =
  ## Compute the magnitude (length) of a vector.
  return sqrt(dot(v, v))

func normalize*(v: Coords): Coords =
  ## Normalize a vector to unit length.
  let mag = magnitude(v)
  if mag == 0.0:
    raise newException(ValueError, "Cannot normalize zero vector")
  return v.mapIt(it / mag)

func computePlaneEquation*(vertices: seq[Coords]): PlaneEquation =
  ## Compute the plane equation from 3 or more coplanar points.
  ## Returns a tuple of (normal vector, d) where the plane equation is: normal · x = d
  ##
  ## For 3D: Uses cross product of two edge vectors.
  ## For general n-D: Uses the first n points to compute normal via Gram-Schmidt.
  
  if vertices.len < 2:
    raise newException(ValueError, "Need at least 2 points to define a plane")
  
  let dimension = vertices[0].len
  if dimension == 3 and vertices.len >= 3:
    # 3D case: use cross product
    let
      v1 = subtract(vertices[1], vertices[0])
      v2 = subtract(vertices[2], vertices[0])
      normal = cross3d(v1, v2)
      normalNorm = normalize(normal)
      d = dot(normalNorm, vertices[0])
    return (normal: normalNorm, d: d)
  
  else:
    # General n-D case: compute normal using first n points
    # The normal is orthogonal to all edge vectors
    var edges: seq[Coords]
    for i in 1..<min(dimension, vertices.len):
      edges.add(subtract(vertices[i], vertices[0]))
    
    if edges.len < dimension - 1:
      raise newException(ValueError, 
        "Not enough linearly independent points to define a plane in " & $dimension & "D space")
    
    # Use weighted sum of edges as approximation (could use SVD)
    var normal = repeat(0.0, dimension - 1)
    for edge in edges:
      for i in 0..<dimension:
        normal[i] += edge[i]
    
    let
      normalNorm = normalize(normal)
      d = dot(normalNorm, vertices[0])
    return (normal: normalNorm, d: d)

func findPlaneIntersection*(faces: seq[Element]): Coords =
  ## Find the intersection of three 3D planes defined by multiple faces.
  
  # TODO: Generalize to be able to return lines
  if faces.len < 3:
    raise newException(ValueError, "Need at least three faces to find intersecting point.")
  
  # Get all plane equations
  let
    planeEqs = collect:
      for face in faces:
        let vertexCoords = collect:
          for v in face.vertices:
            v.coords
        computePlaneEquation(vertexCoords.toSeq)
    dimension = planeEqs[0].normal.len
    numPlanes = planeEqs.len
  
  # Build system of linear equations: A * x = b
  # where A[i] = normal[i], b[i] = d[i]
  var
    aMatrix = newSeq[seq[float]](numPlanes)
    bVector = newSeq[float](numPlanes)
  
  for i, planeEq in planeEqs:
    aMatrix[i] = planeEq.normal
    bVector[i] = planeEq.d
  
  # Solve Ax = b using Gaussian elimination
  var solution = newSeq[float](dimension)
  
  try:    
    # Gaussian elimination with partial pivoting
    for col in 0..<min(dimension, numPlanes):
      # Find pivot
      var maxRow = col
      for row in col + 1..<numPlanes:
        if abs(aMatrix[row][col]) > abs(aMatrix[maxRow][col]):
          maxRow = row
      
      # Swap rows
      (aMatrix[col], aMatrix[maxRow]) = (aMatrix[maxRow], aMatrix[col])
      (bVector[col], bVector[maxRow]) = (bVector[maxRow], bVector[col])
      
      # Check for singular matrix
      if abs(aMatrix[col][col]) < 1e-10:
        continue
      
      # Eliminate column
      for row in col + 1..<numPlanes:
        if col < aMatrix[row].len:
          let factor = aMatrix[row][col] / aMatrix[col][col]
          for j in col..<aMatrix[row].len:
            aMatrix[row][j] -= factor * aMatrix[col][j]
          bVector[row] -= factor * bVector[col]
    
    # Back substitution
    for i in countdown(min(dimension, numPlanes) - 1, 0):
      if i < aMatrix.len and i < aMatrix[i].len:
        solution[i] = bVector[i]
        for j in i + 1..<dimension:
          if j < aMatrix[i].len:
            solution[i] -= aMatrix[i][j] * solution[j]
        if abs(aMatrix[i][i]) > 1e-10:
          solution[i] /= aMatrix[i][i]
    
    return solution
  
  except:
    raise newException(ValueError, "Could not solve plane intersection system")
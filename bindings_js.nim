## Binding functions for exporting to JavaScript

import figures, model, operations, polytope
import std/[sequtils]


var
  # Available operations are "rectify" and "stellate"
  current_polytope = tetrahedron
  current_model {.exportc.} = current_polytope.toFaceModel

proc refreshModel() =
  current_model = current_polytope.toFaceModel


## Operations for bindings

proc rectifyPolytope*() {.exportc.} =
  current_polytope = current_polytope.rectify
  refreshModel()

proc stellatePolytope*() {.exportc.} =
  current_polytope = current_polytope.stellate
  refreshModel()

proc separatePolytope*() {.exportc.} =
  let pieces = current_polytope.separate()
  if pieces.len > 0:
    current_polytope = pieces[0]
  refreshModel()

proc getCurrentModel*(): FaceModel {.exportc.} =
  current_model

# proc rank(): cint {.exportc.} =
#   return tetrahedron.rank.cint()

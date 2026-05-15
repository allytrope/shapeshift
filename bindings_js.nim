## Binding functions for exporting to JavaScript

import figures, model, operations, polytope
import std/[sequtils]


var current_model {.exportc.} = tetrahedron.rectify.rectify.rectify.toFaceModel

# proc rank(): cint {.exportc.} =
#   return tetrahedron.rank.cint()

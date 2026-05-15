# shapeshift
A GUI application for generating and visualizing polyhedra using geometric operations. This branch is a rewrite of the project in Nim.

## Description
This tool seeks to include a catalogue of operations that can be applied to polytopes in sequence to generate new polytopes, inlcuding operations that work on polytopes of arbitrary dimension.

The simplest of the polyhedra, the regular tetrahedron (the 3-simplex) is set as the seed.
From this most basic shape, operations can be applied to generate new, more complex polyhedra.
Currently, this tool offers the rectification operation.

## How to Run
With Nim and `npx` installed, run the starting script with:
```bash
sh run.sh
```

Currently, the polyhedron and its operations can be set in bindings_js.nim, and then running the above script will render that polyhedron.

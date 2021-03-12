# shapeshift
A GUI application for generating and visualizing polyhedra using rectification and truncation. 

## Premise
Polyhedra can be manipulated using operations to generate new polyhedra. 

Curently implemented operations are [rectification](https://en.wikipedia.org/wiki/Rectification_(geometry)), which constructs new vertices from midpoints, and [truncation](https://en.wikipedia.org/wiki/Truncation_(geometry)), which creates new faces at each vertex.
Shapeshift displays these resulting polyhedra in 3D rotation and provides details on vertices, edges, and faces.

Additional features are expected to expand the toolbox of operations including stellation and creating duals.
Such buttons in the GUI are currently nonfunctional.

## Dependencies
Shapeshift uses Python3 along with a few packages that can be installed through the Python package manager `pip`:
* `pyqt5` for window and widgets
* `PyOpenGL` for polyhedron visualization
* `numpy` for computation

The program can then be run by executing window.py in a Python3 interpreter.

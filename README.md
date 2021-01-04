# shapeshift
A GUI application for generating and visualizing polyhedra using rectification. 

## Premise
Polyhedra can be manipulated using operations to generate new polyhedra. 
Shapeshift utilizes an operation called rectification, which constructs new vertices from midpoints. 
These resulting polyhedra are observed in 3D rotation and provide details on vertices, edges, and faces. 
More info on rectification can be found on the [Wikipedia page](https://en.wikipedia.org/wiki/Rectification_(geometry)).

Additional features are expected to expand the toolbox of operations including stellation and creating duals.
Such buttons in the GUI are currently nonfunctional.

## Dependencies
Shapeshift uses Python3 along with a few packages that can be installed through the Python package manager `pip`:
* `pyqt5` for window and widgets
* `PyOpenGL` for polyhedron visualization
* `numpy` for computation

The program can then be run my executing window.py in a Python3 interpreter.

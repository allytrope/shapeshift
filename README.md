# shapeshift
A tool for generating and visualizing polyhedra using rectification. 

## Premise
Polyhedra can be manipulated using operations to generate new polyhedra. 
Shapeshift utilizes an operation called rectification, which constructs new vertices from midpoints. 
These resulting polyhedra are observed in 3D rotation and provide details on vertices, edges, and faces. 
More info on rectification can be found on the [Wikipedia page](https://en.wikipedia.org/wiki/Rectification_(geometry)).

Additional features are expected to expand the toolbox of operations including creating duals as well as providing a more sophisticated UI.

## Controls
Currently, controls are keybound as follows:

Key | Function
----|--------
r | Rectifies polyhedron
s | Prints # of vertices, edges, and faces
x | Prints vertex coordinants, edge pairs, and faces boundaries
f | Prints # of faces for each *n*-gon


## Dependencies
Shapeshift uses Python3 along with a few packages that can be installed through the Python package manager `pip`:
* `pygame` and `PyOpenGL` for visualization
* `numpy` for computation

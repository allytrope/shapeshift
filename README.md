# shapeshift
A GUI application for generating and visualizing polyhedra using geometric operations. This branch is a rewrite of the project in Nim.

## Premise
Seed polyhedra are provided.
Operations can then be applied to polyhedra to create new and more complex ones.

## Setup
`owlkettle` works on Ubuntu 22, but not Ubuntu 20. This is because GTK4 is not available for the later. The GUI also isn't working for Ubuntu 24.

First had to update:
`sudo apt-get update`

Then install `gcc` (wouldn't work if the above command wasn't run first):
`sudo apt install gcc`

Then download `choosenim`:
`curl https://nim-lang.org/choosenim/init.sh -sSf | sh`

Then add `export PATH=/home/allytrope/.nimble/bin:$PATH` to `.profile` or `.bashrc`

For `owlkettle`:
`sudo apt install libgtk-4-dev libadwaita-1-dev`
`sudo apt-get install freeglut3`
`sudo apt-get install libglu1-mesa`

Then install `owlkettle`:
`nimble install owlkettle`
`nimble install opengl`

If on Ubuntu 24, it gives these errors:
`could not load: libGLU.so.1`
`could not load: libglut.so.3`

For now, I'm testing if it the GUI code runs with this code: https://github.com/nim-lang/opengl/blob/master/examples/glut_example.nim

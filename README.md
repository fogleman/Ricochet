----------------------------------------
    RICOCHET ROBOTS / RASENDE ROBOTER
----------------------------------------

Requirements
============
- Python 3.8+
- wxPython (a recent appropriate version for Python3.8)
  - It is helpful to install this using `conda` pre-built wheels, as the build process using pip takes unreasonably long.

Compile and Run
===============
- To compile the C-based solver, run ./build_ricochet (requires gcc).
  - If you skip this step, the Python solver will be used, which is slower. 

Launch the program with: `python3 main.py [-h] [-s|--state SEED] [-r|--nrobots NROBOTS]`. 
The additional arguments determine the random seed and no. of robots to use.

Controls
========
To move a robot, select one by color and then use the arrow keys on the keyboard.

- R - Red
- G - Green
- B - Blue
- Y - Yellow
- V - Silver

Other program controls are listed below.

- N - New Game
- S - Solve
- U - Undo
- Esc - Quit

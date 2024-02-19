# Python Implementation of Go/Baduk.

## Overview
This is a Python based implemention of Go, utilizing PySimpleGUI v4 and pygame for the GUI and player input. There is file saving and loading via pythons pickle module. Play is currently only possible via hotseat. Scoring can be done manually or via a automatic system that uses floodfill alongside Monte Carlo Search Trees to calculate what areas on the board are dead or not. It is currently only possible to play against a random bot, however once more training is done on the Artificial Intelligence it will be possible to play against them.
The Artificial Intelligence used is a version of AlphaGo Zero implemented in keras alongside my own version of a MCST.

### Dependencies to install, and how to install them:

This program relies on PySimpleGUI v4, pygame, tensorflow, and a newer version of Python.
It is possible to use python 3.6 and newer, however 3.10 is the most stable version for this project. Tensorflow v2 will require python 3.8 or newer, however. 
Pygame 2.5.2 or newer is preferable, but might work with older version.
PySimpleGUI is v4, which is FOSS, while v5 is closed source.

[PySimpleGUI v4 FOSS](https://github.com/andor-pierdelacabeza/PySimpleGUI-4-foss). Clone the repository to your computer, and install to the environment in which you will be using this program via `pip install -e /path/to/folder/PySimpleGUI`

Pygame:
`pip install pygame`

Tensorflow:
`pip install tensorflow`

If you wish to access this program as an exe, you can use PyInstaller or auto-py-to-exe.




### Future plans for this project include:
    
    1. Extending the current system to allow for a hexagonal version of Go that means three players can play.
    2. Implementing server based multiplayer.
    3. Heavily optimizing or rewriting of the program in C++ to greatly improve the ability of the Artificial Intelligence to self-play for training purposes.
    4. Devote more computational resources towards training of the Artifical Intelligence.
    5. Implementing more unittests/test cases.

### Contributing:

    1. Report bugs: If you encounter any bugs or errors, open up issue on github and explain what the bug is, and how you encountered it.
    2. Suggestions: If you have any suggestions, please open up an issue on github explaining your ideas regarding what could be improved or added into the program.
    3. Documentation: If you see any documentation that you believe to be confusing, or that you believe could be better explained, open up a issue on github and I will discuss it with you.
    4. Contributing code: Read the following section on how to contribute code. All contributions are welcome, but anything related to online multiplayer is specifically encouraged. 

### How to Contribute Code:

    1. Fork this repository, then clone it.
    2. Add your contributions (code, or documentation after discussion in an issue).
    3. Commit and push your commit.
    4. Wait for pull requests to be merged.



# RPGenerator
Simple lib, proof of concept, aiming at generating scenarios for RPGs, written in Python3.

## Dependencies
The core part of this project only requires Python3.
It might work with former versions of Python, but the code is tested under Python 3.6.3.

Other parts of the project, including demos, need additional packages. See `Demo` section for more information.

## Demo
The demo generates a graph given the parameters set in `main.py`.
It outputs dot-formatted graph description onto stdout, and can be used by any piece of software that supports dot files.
The demo is launched from `build.sh` and requires package `graphviz`.

To run the demo, simply run `./build.sh`.
Two files must appear, `out.dot` which contains the dot-formatted graph description and `out.pdf` which shows a visual interpretation of this graph.

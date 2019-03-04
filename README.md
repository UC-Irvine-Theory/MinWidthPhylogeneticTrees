# MinWidthPhylogeneticTrees

A small width upward planar phylogenetic tree drawer.
This project has several modules:

## Generate Drawings

runner.py
The main module, recieves and input file containing 1 or more trees and generates small width tree drawings.
Runs the following heuristics:
  - Human Ordered: The order defined by the original tree source data.

  - Random Ordering: The order defined by randomly shuffling the children at each node.

  - Left Heavy: The order defined by sorting the children of each node in descending order.

  - Alternating Heavy: The order obtained by alternately sorting in descending and ascending order the children of each node according to their sub-tree.

  - Greedy: The order obtained by greedily bottom-to-top minimizing the width of each sub-tree. 

  - White-space-phobic: The order obtained by greedily bottom-to-top minimizing the whitespace (gaps) in the interior of each sub-tree. 

For each tree and for each heuristic it generates a minimum width drawing and calculates its width. 
It also generates a CSV file with the information for each tree and a nice scatter plot. 

usage: runner.py [-h] [-n] [-s SEED] [-c CSVPATH] [-i IMAGEPATH]
                 inputPath schema

positional arguments:
  inputPath             Path to file with trees
  schema                Schema of input file ("newick", "nexus", "nexml")

optional arguments:
  -h, --help            show this help message and exit
  -n, --noImage         Suppress images. Generate only csv and plot
  -s SEED, --seed SEED  Set the seed of the random heuristic
  -c CSVPATH, --csvPath CSVPATH
                        Path to csvFile. Default: results.csv
  -i IMAGEPATH, --imagePath IMAGEPATH
                        Path to Image storage folder. Defailt: Images/

## Clean Trees

readTree.py
A cleaning utility for simplifying large tree set files. Recommended if running large files.
Removed metadata information and trees without edge lengths. 

usage: readTree.py [-h] inputPath schema outputPath

positional arguments:
  inputPath   Path to file with trees
  schema      Schema of input file ("newick", "nexus", "nexml")
  outputPath  Path to output path with cleaned trees

optional arguments:
  -h, --help  show this help message and exit
  
This project originally focused on downloading large sets from TreeBase (a fantastic website!). When doing so a common problem with these files is that the large nexus files have a few small error. Mainly some tree definitions are missing or some trees are missing the closing semicolon. Both are easy to fix (delete the line, or add the semicolon), so check the error message if cleaning runs into problems. 
  
## Requirements
  
Requires python 3 and the following external libraries:
  
  - dendropy: https://dendropy.org --> Reading and writing phylogenetic data
  - cv2: http://opencv.org/ --> Image generation
  - matplotlib: https://matplotlib.org -> Scatter plot
  - numpy: http://www.numpy.org -> Math

Thanks to all the creators and maintainers of these libraries!

## Contact

This module was made by the University of California, Irvine Computer Science Theory group.
Please send comments to jjbesavi at uci.edu

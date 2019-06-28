# MinWidthPhylogeneticTrees

A small width upward planar phylogenetic tree drawer.
This project has several modules:

## Generate Drawings

**runner.py**
The main module, recieves and input file containing 1 or more trees and generates small width tree drawings.
Runs the following default heuristics:
  - Human Ordered```(Orig)```: The order defined by the original tree source data.

  - Greedy```(Greedy)```: The order obtained by greedily bottom-to-top minimizing the width of each sub-tree. 

  - Minimum Area```(White)```: The order obtained by greedily bottom-to-top minimizing the area of the orthogonal y-monotone polygon bounding each sub-tree.

  - Hill Climbing```(HillClimbing)```: The order obtained by running a black-box optimization approach obtained by making gradual changes to the human order that lead to a better solution.

  - Simulated Annealing```(Annealing)```: The order obtained by running a black-box optimization approach similar to hill climbing that also keeps changes that worsen the solution with probability inversely proportional to the difference.

Furthermore the following heuristics are also available:
  - Tetris```(Tetris)```: The order obtained by greedily bottom-to-top maintaining a set shapes the subtree can obtain (and the order required to achieve them) and finds the best shape that both subtrees can combine into. 

  - Random Ordering```(Random)```: The order defined by randomly shuffling the children at each node.

  - Left Heavy: The order defined by sorting the children of each node in descending order, where the child's value is determined by either the lowest leaf ```(DToLeaf)``` or the leaf with the largest number of ancestors ```(NToLeaf)```

  - Alternating Heavy: The order obtained by alternately sorting in descending and ascending order, where the child's value is determined by either the lowest leaf ```(AltDToLeaf)``` or the leaf with the largest number of ancestors ```(AltNToLeaf)```

For each tree and for each heuristic it generates a minimum width drawing and calculates its width. 
It also generates a CSV file with the information for each tree and a nice scatter plot. 

**usage:** runner.py [-h] [-n] [-s SEED] [-c CSVPATH] [-i IMAGEPATH] [-l HEURISTIC1 [HEURISTIC2 ... HEURISTICN]]
                 inputPath schema

positional arguments:
  inputPath             Path to file with trees
  schema                Schema of input file ("newick", "nexus", "nexml")

optional arguments:
  -h, --help                      show this help message and exit
  -n, --noImage                   Suppress images. Generate only csv and plot
  -s SEED, --seed SEED            Set the seed of the random heuristic
  -c CSVPATH, --csvPath CSVPATH   Path to csvFile.              Default: results.csv
  -i IMAGEPATH, --imagePath imagePath
                                  Path to Image storage folder. Default: Images/
  -l HEURISTICS, --heuristics HEURISTICS   
                                  List of one or more heuristics to run. Default: "Orig" "Greedy" "White" "HillClimbing" "Annealing"

## Clean Trees

**readTree.py**
A cleaning utility for simplifying large tree set files. Recommended if running large files.
Removed metadata information and trees without edge lengths. 

**usage**: readTree.py [-h] inputPath schema outputPath

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
A special thanks to the people at https://treebase.org/ and the contributers that provided the trees for our paper.

## Other Files

In Trees/ are the files used to generate the drawings of the paper "Minimum-Width Drawings of Phylogenetic Trees". The top-level has the cleaned files (reccommended for running experiments) and Trees/Original/ has the original files with the complete metadata. To see the origin of the tree please search for its name (eg: "Tr78560") at https://treebase.org/.

## Contact

This module was made by the University of California, Irvine Computer Science Theory group.
Please send comments to jjbesavi at uci.edu

import argparse
import random
import sys
import time

import matplotlib.pyplot as plt
import numpy as np

from draw import save_img,show
from fixedOrderEmbedder import embedTree, lowerBound
import heuristics
from readTree import readTrees
from node import Node
from matplotlib.lines import Line2D

from shapes import approximateWithTwoRects
from shapes import Shape
from shapes import Rect

def embedTest():
    n0  = Node( 0,  8, [])
    n1  = Node( 1,  6, [n0])

    n2  = Node( 2,  4, [])
    n3  = Node( 3,  2, [n2,n1])

    n4  = Node( 4,  4, [])
    n5  = Node( 5,  6, [])
    n6  = Node( 6,  8, [])

    n7  = Node( 7,  4, [n5,n6])
    n8  = Node( 8,  2, [n4,n7])

    n9  = Node( 9,  0, [n3,n8])

    n9.fillStats()

    tree = heuristics.identity(n9)

    width = embedTree(tree)
    print("Width: " + str(width))
    print("White: " + str(tree.stats.whitespace))

    tree.printMe(0)

    save_img(tree, "test")

def smallTest():
    n0  = Node( 0, 10, [])
    n1  = Node( 1, 10, [])
    n2  = Node( 2,  8, [n0,n1])

    n3  = Node( 3,  8, [])
    n4  = Node( 4,  6, [n3])
    n5  = Node( 5,  4, [])
    n6  = Node( 6,  2, [n4,n5])

    n7  = Node( 7,  0, [n2,n6])
    n7.fillStats()

    tree = heuristics.tetris(n7)

    width = embedTree(tree)
    print("Width: " + str(width))
    print("White: " + str(tree.stats.whitespace))

    s = Shape(tree)
    print("BottomRect: " + str(s.bottomRect))
    print("TopRect: " + str(s.topRect))
    print(str(s.type))

    tree.printMe(0)

    print("Shape tests--------------------------------")

    r0 = Rect(10,0,  0,10)
    r1 = Rect(20,0, 10,30)

    print(s.getType(r1,r0))
    r0.left = 10; r0.right = 20
    print(s.getType(r1,r0))
    r0.left = 20; r0.right = 30
    print(s.getType(r1,r0))
    r0.left = 1;  r0.right = 29
    print(s.getType(r1,r0))
    r0.left = 0;  r0.right = 30
    print(s.getType(r1,r0))
    r1.left = 0;  r1.right = 10
    print(s.getType(r1,r0))
    r1.left = 10; r1.right = 20
    print(s.getType(r1,r0))
    r1.left = 10; r1.right = 30
    print(s.getType(r1,r0))
    r1.left = 1;  r1.right = 29
    print(s.getType(r1,r0))
    r1.left = 0;  r1.right = 30
    print(s.getType(r1,r0))
    r1.left = 10;  r1.right = 50
    print(s.getType(r1,r0))
    r0.left = 20;  r0.right = 60
    print(s.getType(r1,r0))

def test():
    n0  = Node( 0,  6, [])
    n1  = Node( 1,  8, [])
    n2  = Node( 2,  4, [n0,n1])

    n3  = Node( 3,  8, [])
    n4  = Node( 4, 10, [])
    n5  = Node( 5,  6, [n3,n4])

    n6  = Node( 6, 12, [])


    n7  = Node( 7,  2, [n2,n5,n6])

    n8  = Node( 8,  4, [])
    n9  = Node( 9,  6, [])
    n10 = Node(10,  2, [n8,n9])


    n11 = Node(11,  0, [n7,n10])
    n11.fillStats()

    tree = heuristics.nodesToLeaf(n11)

    width = embedTree(tree)
    print("Width: " + str(width))
    print("White: " + str(tree.stats.whitespace))
    bottomRect, topRect = approximateWithTwoRects(tree.stats.leftBorder, tree.stats.rightBorder)

    print("BottomRect: " + str(bottomRect))
    print("TopRect: " + str(topRect))

    s = Shape(bottomRect, topRect, tree)
    print(str(s.type))

    tree.printMe(0)
    #tree.printMe(0, lambda n : str((n.dNode, str(n))) )
    #tree.printMe(0, lambda n : str((n.dNode, str(n.stats))) )
    save_img(tree, "test")

def flip(node):
    node.children.reverse()
    for c in node.children:
        flip(c)

def writeCSV(path,schema,seed,allResults,tests,csvFile):
    csvFile.write(path + ", " + schema + "\n")
    csvFile.write("Seed, " + str(seed) + "\n")
    csvFile.write("ID, Size, ")
    for name in tests:
        csvFile.write(name + ", ")
    csvFile.write("\n\n")

    for id, size, results in allResults:
        csvFile.write(str(id) + ", " + str(size) + ",\t")
        for  name,width in results:
            csvFile.write( str(width) + ", ")
        csvFile.write("\n")

    csvFile.close()

def makeScatter(allResults,title='Width Achieved for Trees using Different Heuristics'):
    symbols = {
        "Orig"      : (".", "green"),
        "Random"    : ("+", "blue"),
        "Greedy"    : ("^", "red"),
        "Heavy"     : (".", "sienna"),
        "Tetris"  : (".", "sandybrown"),
        "White"     : ("^", "mediumslateblue"),
        "HillClimbing": ("o", "green"),
        "Annealing" : ("o", "black"),
        "BruteForce": ("o", "green")
    }
    for_legend = [Line2D([],[],color=s[1],marker=s[0],label=name,lw=0) for name,s in symbols.items()]
    maxy=0
    maxw=0
    for id, size, results in allResults:
        if maxw<int(size):
            maxw=int(size)
        for name,width in results:
            if maxy<int(width):
                maxy=int(width)
            plt.scatter(int(size), int(width), marker=symbols[name][0], color=symbols[name][1])
    plt.xlabel('Number of Nodes in Tree')
    plt.ylabel('Width achieved')
    plt.xlim(left=0,right=min(np.ceil(maxw*1.1),1200))
    plt.ylim(bottom=0,top=min(np.ceil(maxy*1.1),500))

    plt.title(title)
    plt.legend(handles=for_legend)
    plt.show()
    plt.close()

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("inputPath", help ="Path to file with trees")
    parser.add_argument("schema"   , help = 'Schema of input file ("newick", "nexus", "nexml")')

    parser.add_argument("-n", "--noImage"  , help="Suppress images. Generate only csv and plot", action="store_true")
    parser.add_argument("-s", "--seed"     , help="Set the seed of the random heuristic", type=int)
    parser.add_argument("-c", "--csvPath"  , help="Path to csvFile. Default: results.csv")
    parser.add_argument("-i", "--imagePath", help="Path to Image storage folder. Defailt: Images/")

    args = parser.parse_args()

    suppressImage = args.noImage
    if suppressImage:
        print("Supressing images!")

    csvPath = "results.csv"
    if args.csvPath:
        csvPath = args.csvPath

    csvFile = None
    try:
        csvFile = open(csvPath, "w")
    except:
        print("Couldn't open csv output file: " + csvPath )
        return
    print("CSV file: " + csvPath);

    imagePath = "Images/"
    if args.imagePath:
        imagePath = args.imagePath
    print("Image folder: " + imagePath);

    seed = random.randint(0, 1000000)
    if args.seed:
        seed = args.seed
    random.seed(seed)
    print("Seed : " + str(seed))

    path = args.inputPath
    schema = args.schema
    trees = readTrees(path,schema)
    print("Finished reading the trees!")
    print("Read in " + str(len(trees)))

    tests = [
        (heuristics.identity, "Orig"),
        #(heuristics.randomShuffle, "Random"),
        (heuristics.greedy, "Greedy"),
        #(heuristics.leftHeavy, "Heavy"),
        #(heuristics.tetris, "Tetris"),
        (heuristics.whitespacePhobic, "White"),
        (heuristics.hillClimbing, "HillClimbing"),
        (heuristics.annealing, "Annealing"),
        #(heuristics.bruteForce, "BruteForce"),
        #(heuristics.distanceToLeaf, "DToLeaf"),
        #(heuristics.altDistanceToLeaf, "AltDToLeaf"),
        #(heuristics.nodesToLeaf, "NToLeaf"),
        #(heuristics.altNodesToLeaf, "AltNToLeaf"),
    ]

    def runTests(id, tree, tests):

        results = []

        print("Running " + str(id), end = "\t")
        print("Lower bound: ", lowerBound(tree))
        for heuristic,name in tests:

            start = time.process_time()
            resultTree = heuristic(tree)
            resultWidth = embedTree(resultTree)
            end = time.process_time()
            results.append((name,resultWidth))

            if not suppressImage:
                save_img(resultTree, imagePath + name + "_" + str(id))
            print(name + " took " + "{:.2f}".format(end-start) + "s",  end = " ")
        print("")
        sys.stdout.flush()

        return results

    allResults = []
    for i,t in enumerate(trees):

        t.fillStats()
        treeSize = t.size()

        results = runTests(i, t, tests)

        allResults.append( (i, t.size(), results))

        #randomWidth = results[1][0]
        #greedyWidth = results[2][0]
        #heavyWidth = results[3][0]
        #suprises = ""
        #if randomWidth < greedyWidth:
        #    suprises = suprises + "Random Won!"
        #if heavyWidth < greedyWidth:
        #    suprises = suprises + " Heavy Won!"

        print(str(i) + " n: " + str(treeSize), end="\t\t")

        for r in results:
            print(str(r[0]) +  ": " + str(r[1]), end=" \t")

        #print("Root Stats: " + str(t.stats) + " \t" + suprises)
        print("Root Stats: " + str(t.stats))

    writeCSV(path,schema,seed,allResults,[name for f,name in tests], csvFile)
    makeScatter(allResults)

if __name__ == "__main__":
    #embedTest()
    #smallTest()
    #test()
    main()

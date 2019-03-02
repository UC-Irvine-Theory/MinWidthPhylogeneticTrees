import argparse
import random
import sys

import matplotlib.pyplot as plt
import numpy as np

from draw import save_img,show
from fixedOrderEmbedder import embedTree
import heuristics
from readTree import readTrees
from node import Node
from matplotlib.lines import Line2D

def write_file(path,schema,seed,allResults,tests,outpath='results.csv'):
    outFile = None
    try:
        outFile = open(outpath, "w")
    except:
        print("Couldn't open result output file: "+outpath )
        return
    outFile.write(path + ", " + schema + "\n")
    outFile.write("Seed, " + str(seed) + "\n")
    outFile.write("ID, Size, ")
    for name in tests:
        outFile.write(name + ", ")
    outFile.write("\n\n")

    for id, size, results in allResults:
        outFile.write(str(id) + ", " + str(size) + ",\t")
        for  name,width in results:
            outFile.write( str(width) + ", ")
        outFile.write("\n")

    outFile.close()


def makeScatter(allResults,title='Width Achieved for Trees using Different Heuristics'):
    symbols = {
        "Orig"     : (".", "green"),
        "Random"   : ("+", "blue"),
        "Greedy"   : ("^", "red"),
        "Heavy"    : (".", "sienna"),
        "AltHeavy" : (".", "sandybrown"),
        "White"    : ("^", "mediumslateblue")
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


####################################
def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("inputPath", help="Path to file with trees")
    parser.add_argument("schema", help = 'Schema of input file ("newick", "nexus", "nexml")')

    parser.add_argument("-n", "--noImage", help="Suppress images. Generate only csv and plot", action="store_true")
    parser.add_argument("-s", "--seed"   , help="Set the seed of the random heuristic", type=int)
    parser.add_argument("-c", "--csvPath", help="Path to csvFile")

    args = parser.parse_args()

    path = args.inputPath
    schema = args.schema

    suppressImage = args.noImage
    if suppressImage:
        print("Supressing images!")

    csvPath = "results.csv"
    if args.csvPath:
        csvPath = args.csvPath

    trees = readTrees(path,schema)

    print("Finished reading the trees!")

    def runTests(id, tree, tests):

        results = []

        print("Running " + str(i), end = "\t")
        for heuristic,name in tests:
            resultTree = heuristic(tree)
            resultWidth = embedTree(resultTree)

            results.append((name,resultWidth))

            if not suppressImage:
                save_img(resultTree, "Images/" + name + "_" + str(id))
            print("Finished " + name, end = " ")
        print("")
        sys.stdout.flush()

        return results

    tests = [
        (heuristics.identity, "Orig"),
        (heuristics.randomShuffle, "Random"),
        (heuristics.greedy, "Greedy"),
        (heuristics.leftHeavy, "Heavy"),
        (heuristics.altHeavy, "AltHeavy"),
        (heuristics.whitespacePhobic, "White"),
        #(heuristics.distanceToLeaf, "DToLeaf"),
        #(heuristics.altDistanceToLeaf, "AltDToLeaf"),
        #(heuristics.nodesToLeaf, "NToLeaf"),
        #(heuristics.altNodesToLeaf, "AltNToLeaf"),
        ]


    seed = random.randint(0, 1000000)
    if args.seed:
        seed = args.seed
    random.seed(seed)
    print("Seed : " + str(seed))
    print("Read in " + str(len(trees)))
    allResults = []
    for i,t in enumerate(trees):

        t.fillStats()
        treeSize = t.size()


        results = runTests(i, t, tests)

        allResults.append( (i, t.size(), results))

        randomWidth = results[1][0]
        greedyWidth = results[2][0]
        heavyWidth = results[3][0]
        suprises = ""
        if randomWidth < greedyWidth:
            suprises = suprises + "Random Won!"
        if heavyWidth < greedyWidth:
            suprises = suprises + " Heavy Won!"

        print(str(i) + " size:\t" + str(treeSize), end="\t")

        for r in results:
            print(str(r[1]) +  " width: " + str(r[0]), end=" \t")

        print("Root Stats: " + str(t.stats) + " \t" + suprises)

    write_file(path,schema,seed,allResults,[name for f,name in tests], csvPath)
    makeScatter(allResults)

if __name__ == "__main__":
    main()

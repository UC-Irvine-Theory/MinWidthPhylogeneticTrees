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

def smallTest():
    n0  = Node( 0, 10, [])
    n1  = Node( 1, 10, [])
    n2  = Node( 2,  8, [n0,n1])

    n3  = Node( 3,  8, [])
    n4  = Node( 4,  6, [n3])
    n5  = Node( 5,  4, [])
    n6  = Node( 6,  2, [n4,n5])

    n7  = Node( 7,  0, [n2,n6])

    tree = heuristics.identity(n7)

    width = embedTree(tree)
    print("Width: " + str(width))

    tree.printMe(0)

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

    tree = heuristics.veeShape(n11)

    embedTree(tree)

    tree.printMe(0, lambda n : str((n.dNode, str(n))) )
    #tree.printMe(0, lambda n : str((n.dNode, str(n.stats))) )
    save_img(tree, "test")

def flip(node):
    node.children.reverse()
    for c in node.children:
        flip(c)
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
def main():

    seed = random.randint(0, 1000000)
    random.seed(seed)
    #test()
    #return

    if len(sys.argv) != 3 and len(sys.argv) != 4 :
        print("Two few arguments expected 2 or 3 (path, schema and optional -s to supress image) and got " + str(len(sys.argv)-1) + " arguments")
        return

    path = sys.argv[1]
    schema = sys.argv[2]
    suppressImage = len(sys.argv) == 4

    if suppressImage:
        print("Supressing images!")

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
        #(heuristics.randomShuffle, "Random"),
        #(heuristics.greedy, "Greedy"),
        (heuristics.leftHeavy, "Heavy"),
        #(heuristics.altHeavy, "AltHeavy"),
        #(heuristics.whitespacePhobic, "White"),
        #(heuristics.distanceToLeaf, "DToLeaf"),
        #(heuristics.altDistanceToLeaf, "AltDToLeaf"),
        #(heuristics.nodesToLeaf, "NToLeaf"),
        #(heuristics.altNodesToLeaf, "AltNToLeaf"),
        ]

    #want = {7,12,101}

    print("Seed : " + str(seed))
    print("Read in " + str(len(trees)))
    allResults = []
    for i,t in enumerate(trees):

     #   if want and i not in want:
     #       continue

        t.fillStats()
        treeSize = t.size()


        results = runTests(i, t, tests)

        allResults.append( (i, t.size(), results))

        #randomWidth = results[1][0]
        #greedyWidth = results[2][0]
        #heavyWidth = results[3][0]
        suprises = ""
        #if randomWidth < greedyWidth:
            #suprises = suprises + "Random Won!"
        #if heavyWidth < greedyWidth:
            #suprises = suprises + " Heavy Won!"

        print(str(i) + " size:\t" + str(treeSize), end="\t")

        for r in results:
            print(str(r[1]) +  " width: " + str(r[0]), end=" \t")

        print("Root Stats: " + str(t.stats) + " \t" + suprises)
    write_file(path,schema,seed,allResults,[name for f,name in tests])
    #makeScatter(allResults)
    #summary = [(key, sum(value[1])) for key,value in allResults.items()]

    #for name,total in summary:
    #    print(name + " \t" + str(total))

if __name__ == "__main__":
    main()

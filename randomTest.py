#Runs random trees testing the correctness of the fixed order embedder


import random
import sys

from node import Node
from fixedOrderEmbedder import makeDAG, rowMakeDAG

def randomTree(size, maxEdgeLength = 20):

    nodes = []

    root = Node(0, 0, [])
    nodes.append(root)

    for i in range(size-1):

        parent = random.choice(nodes)
        edgeLength = 2*(random.randint(2, maxEdgeLength))

        newNode = Node(i+1, parent.height + edgeLength, [])

        nodes.append(newNode)
        parent.right(newNode)

    return root

def printEdges(vertices):

    def simple(v):
        return "<" + str(v.node.dNode) + " " + str(v.node.height) + " - " + str(v.type.name) + ">"

    for v in sorted(vertices, key= lambda v: (v.node.dNode, v.node.height, v.type) ):
        print(simple(v), end=" --> \t")
        for o in sorted(v.outgoing, key = lambda o: (o.node.height, o.type) ):
            print(simple(o), end=" ")
        print()

def checkCorrectness(root):

    fast = list(sorted(makeDAG(root), key = lambda v : (v.node.dNode, v.node.height, v.type)))

    slow = list(sorted(rowMakeDAG(root), key = lambda v : (v.node.dNode, v.node.height, v.type)))

    if len(fast) != len(slow):
        print("Different top lengths")
        return False

    for i in range(len(fast)):
        eFast = list(sorted(fast[i].outgoing, key = lambda n: (n.node.dNode, n.node.height, n.type)))
        eSlow = list(sorted(slow[i].outgoing, key = lambda n: (n.node.dNode, n.node.height, n.type)))

        if len(eFast) != len(eSlow):
            print("Different edge lengths " + str(i) + " --> " + str(fast[i].node.dNode))
            print("\nFast")
            printEdges(fast)
            print("\nSlow")
            printEdges(slow)
            print("\n")
            return False

        for j in range(len(eFast)):
            nFast = eFast[j]
            nSlow = eSlow[j]

            if nFast.node.height != nSlow.node.height or nFast.type != nSlow.type:
                print("Different edges " + str(i) + ", " +  str(j)  )
                print("\nFast")
                printEdges(fast)
                print("\nSlow")
                printEdges(slow)
                print("\n")
                return False

    return True

#random.seed(0)
size = 5
n = 1000000
tick = n/10

while True:

    for s in range(5,10000):
        print(s)
        for i in range(n):
            random.seed(i)
            root = randomTree(s)
            correct = checkCorrectness(root)

            if not correct:
                print("Bad s: " + str(s) + " i " + str(i))
                root.printMe(0)
                exit()

            if i % tick == 0:
                print(".", end=" ")
                sys.stdout.flush()
        print("\n\n\nFinished " + str(s))


import copy
import itertools
import math
import pdb
import random
from collections import defaultdict

from node import Node
from fixedOrderEmbedder import embedTree
from shapes import Shape

def flip(node):
    if node.children:
        node.children.reverse()

def identity(root):
    newTree = copy.deepcopy(root)

    return newTree

def randomShuffle(root):

    newTree = copy.deepcopy(root)

    def shuffle(node):
        random.shuffle(node.children)
        for c in node.children:
            shuffle(c)

    shuffle(newTree)

    return newTree

def greedy(root):

    newTree = copy.deepcopy(root)

    def greedyOrder(node):

        for c in node.children:
            greedyOrder(c)

        if len(node.children) > 4:
            print("Warning going to try more than " + str(len(node.children)) + "! permutations")

#Well do permutations if stable
        stable = copy.copy(node.children)

        best = copy.copy(stable)
        bestWidth = embedTree(node)
        bestWhitespace = node.stats.whitespace
        bestFlip = None


        for i in range(0, len(stable)+1):

            for flipPerm in itertools.combinations(stable, i):
                for n in flipPerm:
                    flip(n)

                for perm in itertools.permutations(stable):
                    perm = list(perm)
                    node.children =  perm

                    permWidth = embedTree(node)
                    permWhitespace = node.stats.whitespace

                    if permWidth < bestWidth or (permWidth == bestWidth and permWhitespace < bestWhitespace):
                        best = copy.copy(perm)
                        bestWidth = permWidth
                        bestWhitespace = permWhitespace
                        bestFlip = flipPerm

                node.children = stable
                for n in flipPerm:
                    flip(n)

        node.children = best
        if bestFlip:
            for n in bestFlip:
                flip(n)

    greedyOrder(newTree)

    return newTree

def whitespacePhobic(root):

    newTree = copy.deepcopy(root)

    def whitespaceOrder(node):

        for c in node.children:
            whitespaceOrder(c)

        if len(node.children) > 4:
            print("Warning going to try more than " + str(len(node.children)) + "! permutations")

#Well do permutations if stable
        stable = copy.copy(node.children)

        best = copy.copy(stable)
        bestWidth = embedTree(node)
        bestWhitespace = node.stats.whitespace
        bestFlip = None

        for i in range(0, len(stable)+1):

            for flipPerm in itertools.combinations(stable, i):
                for n in flipPerm:
                    flip(n)

                for perm in itertools.permutations(stable):
                    perm = list(perm)
                    node.children =  perm

                    permWidth = embedTree(node)
                    permWhitespace = node.stats.whitespace

                    if permWhitespace < bestWhitespace or (permWhitespace == bestWhitespace and permWidth < bestWidth):
                        best = copy.copy(perm)
                        bestWidth = permWidth
                        bestWhitespace = permWhitespace
                        bestFlip = flipPerm

                node.children = stable
                for n in flipPerm:
                    flip(n)

        node.children = best
        if bestFlip:
            for n in bestFlip:
                flip(n)

    whitespaceOrder(newTree)

    return newTree

def childSort(root, key, reverse, alternating = False):
    newTree = copy.deepcopy(root)

    def sortChildren(node, innerReverse):
        node.children.sort(key=key, reverse=innerReverse)

        if alternating:
            innerReverse = not innerReverse

        for c in node.children:
            sortChildren(c, innerReverse)

    sortChildren(newTree, reverse)

    return newTree

# Left subtree always has more (or equal) nodes
def leftHeavy(root):
    return childSort(root, lambda c: c.stats.subtreeSize, reverse = True)

def distanceToLeaf(root):
    return childSort(root, lambda c: c.stats.distanceToLeaf, reverse = True)

def nodesToLeaf(root):
    return childSort(root, lambda c: c.stats.nodesToLeaf, reverse = True)

def altHeavy(root):
    return childSort(root, lambda c: c.stats.subtreeSize, reverse = True, alternating = True)

def altDistanceToLeaf(root):
    return childSort(root, lambda c: c.stats.distanceToLeaf, reverse = True, alternating = True)

def altNodesToLeaf(root):
    return childSort(root, lambda c: c.stats.nodesToLeaf, reverse = True, alternating = True)


def prob1(cost1, cost2, temp):
    if cost2 <= cost1:
        return 1
    else:
        return 0
        
def prob2(cost1, cost2, temp):
    if cost2 <= cost1:
        return 1
    else:
        return math.exp((cost1 - cost2) / temp)

def nodesToFlip(tree):
    nodesToFlip = []
    nonLeafNodes = tree.getAllNonLeafNodes()
    nonLeafNodeHeights = tree.nonLeafNodeHeights()
    for node in nonLeafNodes:
        if not node.ignoreFlip(nonLeafNodeHeights):
            nodesToFlip.append(node)
    return nodesToFlip

def search(root, prob):
    currentTree = copy.deepcopy(root)
    currentCost = embedTree(currentTree)
    startTemp = currentCost / 100
    totalSteps = 5000.0
    tempDecrease = startTemp / totalSteps
    currentTemp = startTemp
    
    flippedNodes = nodesToFlip(currentTree)
    while currentTemp > 0:
        flipNode = random.choice(flippedNodes)

        # Save the old ordering
        oldChildren = flipNode.children

        # Generate a new random ordering, and compute the new cost
        newChildren = [c for c in flipNode.children]
        if (len(newChildren) == 2):
            newChildren = [newChildren[1], newChildren[0]]
        else:
            random.shuffle(newChildren)
        flipNode.children = newChildren
        newCost = embedTree(currentTree)

        # print(currentCost, newCost, currentTemp, prob(currentCost, newCost, currentTemp))
        if (random.random() < prob(currentCost, newCost, currentTemp)):
            # If keep, update the cost
            currentCost = newCost
        else:
            # Else, return to the old ordering
            flipNode.children = oldChildren
        currentTemp -= tempDecrease

    return currentTree

def hillClimbing(root):
    return search(root, prob1)

def annealing(root):
    return search(root, prob2)

def bruteForce(root):
    currentTree = copy.deepcopy(root)
    minWidth = embedTree(currentTree)
    bestTree = currentTree
    maxSize = 16
    nonLeafNodes = bestTree.getAllNonLeafNodes()

    flippedNodes = nodesToFlip(currentTree)
    if len(flippedNodes) <= maxSize:
        print ("Computing optimal solution with", len(flippedNodes), "flipped nodes...")
        perms = [list(itertools.permutations(node.children)) for node in flippedNodes]
        widths = defaultdict(int)
        allOrders = itertools.product(*perms)
        for ordering in allOrders:
            # Note that currentTree is not copied when we check new orderings,
            # so the nodes in flippedNodes are always part of currentTree.
            for i in range(len(perms)):
                flippedNodes[i].children = ordering[i]
            newWidth = embedTree(currentTree)
            widths[newWidth] += 1
            if newWidth < minWidth:
                minWidth = newWidth
                bestTree = copy.deepcopy(currentTree)
        print("Number of ways to achieve each width:", widths)
    else:
        print("Error! Tree is too large for brute force (", len(perms), "flipped nodes ).")
    return bestTree

def approximateShape(tree):
    assert(tree.stats.leftBorder)

DO_PRINT = False

def tetris(root):

    def tetrisOrder(node):

        def shapeAndStoreIfBetter(temp, shapes):
            embedTree(temp)
            shape = Shape(temp)

            if not shape.type in shapes or shapes[shape.type].better(shape):
                newTree = copy.copy(temp)
                newTree.children = copy.copy(temp.children)
                shape.tree = newTree
                shapes[shape.type] = shape

        if node.isLeaf():
            shape = Shape(node)
            node.shapes = {shape.type : shape}
            if DO_PRINT:
                print("Shapes of node: " + str(node))
                for t,s in node.shapes.items():
                    print(t);
                    s.tree.printMe(1)
                print("--------------------");
            return

        if len(node.children) > 2:
            print("SKIPPING TETRIS: More than 2 children..  " + str(len(node.children)) + " is too many")
            return

        for c in node.children:
            tetrisOrder(c)

        shapes = {}
        if len(node.children) == 1:
            childShapes = node.children[0].shapes
            node.children[0].shapes = None #Don't want to copy
            tempNode = copy.copy(node)
            for type,subShape in childShapes.items():
                tempNode.children = [subShape.tree] #switch to shapes subtree
                shapeAndStoreIfBetter(tempNode, shapes)
        else:
            tempNode = copy.copy(node)
            leftShapes = node.children[0].shapes
            node.children[0].shapes = None #Don't want to copy
            rightShapes = node.children[1].shapes
            node.children[1].shapes = None #Don't want to copy

            for leftType, leftShape in leftShapes.items():
                #flippedLeft = copy.deepcopy(leftShape.tree)
                #flip(flippedLeft)
                for rightType, rightShape in rightShapes.items():
                    #Left-Right
                    tempNode.children = [leftShape.tree,rightShape.tree]
                    shapeAndStoreIfBetter(tempNode, shapes)
                    #Right-Left
                    tempNode.children = [rightShape.tree,leftShape.tree]
                    shapeAndStoreIfBetter(tempNode, shapes)

                    #flip(Left) - Right
                    #tempNode.children = [flippedLeft,rightShape.tree]
                    #shapeAndStoreIfBetter(tempNode, shapes)
                    #Right-flip(Left)
                    #tempNode.children = [rightShape.tree,flippedLeft]
                    #shapeAndStoreIfBetter(tempNode, shapes)
        node.shapes = shapes

        if DO_PRINT:
            print("Shapes of node: " + str(node))
            for t,s in node.shapes.items():
                print(t);
                s.tree.printMe(1)
            print("--------------------");


    newTree = copy.deepcopy(root)
    tetrisOrder(newTree)

    best = min(newTree.shapes.values(), key = lambda s : s.width())

    return best.tree
    
    
def branch_and_bound(tree):
    currentTree = copy.deepcopy(root)
    minWidth = embedTree(currentTree)
    nonLeafNodes = currentTree.getAllNonLeafNodes()
    # Upper bound: Choose an arbitrary ordering, and compute 
    # Lower bound: Should be linear time?



from collections import deque
from enum import IntEnum
from node import Node
import pdb

FIXED_DEBUG = False

class Type(IntEnum):
    LEFT = 1
    EDGE = 2    #incoming edge
    RIGHT = 3

class Vertex:

    def __init__(self, node, type):
        self.node = node
        self.type = type
        self.outgoing = set()
        self.incoming = set()

        self.column = 0 # column in drawing will then be transformed to x coord for node

    def addEdge(self, outNeighbor):
        if outNeighbor not in self.outgoing:
            self.outgoing.add(outNeighbor)
            outNeighbor.incoming.add(self)

    def __str__(self):
        return "<" + str(self.node) + ", " + self.type.name + ", " + str(self.column) + ">";

def getMaxHeight(node):

    max = node.height

    for c in node.children:
        childMax = getMaxHeight(c)
        if childMax > max:
            max = childMax

    return max

def createVertices(node, isRoot, nodeToVertices):
    leftSide  = Vertex(node, Type.LEFT)
    rightSide = Vertex(node, Type.RIGHT)


    incoming = None
    if isRoot:
        nodeToVertices[node] = { Type.LEFT: leftSide, Type.RIGHT : rightSide}
        leftSide.addEdge(rightSide)
    else:
        incoming = Vertex(node, Type.EDGE)
        leftSide.addEdge(incoming)
        incoming.addEdge(rightSide)
        nodeToVertices[node] = { Type.LEFT: leftSide, Type.EDGE : incoming, Type.RIGHT : rightSide}

    return leftSide, incoming, rightSide

def preorderEdges(node, l, parentIndex, vertices, nodeToVertices, isRoot):

    class Range:
        def __init__(self, height, vertex):
            self.height = height
            self.vertex = vertex

        def __str__(self):
            return str((self.height, self.vertex.type.name))

    leftSide, incoming, rightSide = createVertices(node, isRoot, nodeToVertices)
    vertices.add(leftSide)
    vertices.add(rightSide)

    nodeIndex = 0
    if isRoot:
        assert len(l) == 0
        l.append(Range(node.height, leftSide))
    else:
        vertices.add(incoming)

#Incoming Edge
        edgeBottomHeight = node.height - 1 #Edges are open at bottom
        top = parentIndex
        bottom = top
        while bottom < len(l) and l[bottom].height <= edgeBottomHeight:
            l[bottom].vertex.addEdge(incoming)
            bottom += 1

#Left side of node

        if bottom < len(l) and l[bottom].height >= node.height:
            l[bottom].vertex.addEdge(leftSide)
            if l[bottom].height == node.height: #Covered by the node
                if l[bottom].vertex.type == Type.EDGE:
                    l[bottom].vertex.addEdge(incoming)
                bottom += 1
            else:
                l[bottom].vertex.addEdge(incoming)

#Fix the list
        del l[top:bottom] #Everything covered
        l.insert(parentIndex, Range(edgeBottomHeight, incoming))
        nodeIndex = parentIndex+1
        l.insert(nodeIndex, Range(node.height, leftSide))

    if node.children:
        for c in node.children:
            preorderEdges(c, l, nodeIndex, vertices, nodeToVertices, False)
#Right side of the node
        l[nodeIndex].vertex.addEdge(rightSide) #Rightmost edge
        l.insert(nodeIndex, Range(node.height, rightSide))
    else:
        leftSide.addEdge(rightSide)
        l[nodeIndex] = Range(node.height, rightSide) #Replace Left Side

def makeDAG(root):

    vertices = set()
    nodeToVertices = dict()
    l = []
    preorderEdges(root, l, -1, vertices, nodeToVertices, True)

    return (vertices, nodeToVertices)

def topologicalSort(vertices):

    result = []

    inCounts = { v:len(v.incoming)  for v in vertices }

    nextLevel = [v for v in vertices if (len(v.incoming) == 0)]

    nextLevel.sort(key = lambda v : -v.node.height)

    while nextLevel:
        currentLevel = nextLevel
        nextLevel = []
        result = result + currentLevel
        for v in currentLevel:
            for n in v.outgoing:
                inCounts[n] = inCounts[n] - 1
                if inCounts[n] == 0:
                    nextLevel.append(n)

        nextLevel.sort(key = lambda v : -v.node.height)

    #print("Topo Order")
    #for v in result:
    #    print( (v.node.height, v.type.name))

    return result

def assignLeftLeaning(order):
# Implements rule for column displacement
    def colCalc(v):
        def leftColCalc(n):
            assert n.type != Type.LEFT
            return n.column + 1
        def edgeColCalc(n):
            if n.type == Type.LEFT:
                return n.column
            else:
                return n.column + 1
        def rightColCalc(n):
            assert n.type != Type.RIGHT
            return n.column

        if v.type == Type.LEFT:
            return leftColCalc
        elif v.type == Type.EDGE:
            return edgeColCalc
        else:
            return rightColCalc

#Assign the columns, the leftmost columns is 0 and so on (due to the topo sort)
    for v in order:
        if len(v.incoming) == 0:
           v.column = 0
        else:
            v.column = colCalc(v)( max(v.incoming, key = colCalc(v)))

def tightenRight(root, nodeToVertices):
    def colCalc(v):
        def leftColCalc(n):
            assert n.type != Type.LEFT
            return n.column
        def edgeColCalc(n):
            if n.type == Type.RIGHT:
                return n.column
            else:
                return n.column - 1
        def rightColCalc(n):
            assert n.type != Type.RIGHT
            return n.column - 1

        if v.type == Type.LEFT:
            return leftColCalc
        elif v.type == Type.EDGE:
            return edgeColCalc
        else:
            return rightColCalc

    def traversal(node):
        #Edge and Right first
        if node != root:

            edge  = nodeToVertices[node][Type.EDGE]
            right = nodeToVertices[node][Type.RIGHT]

            edgeCol = colCalc(edge) ( min( (w for w in edge.outgoing if w != right), key = colCalc(edge)))
            #print("\tEdge  Col: " + str(edgeCol))
            bestCol = edgeCol

            if right.outgoing:
                rightCol = colCalc(right)( min(right.outgoing, key = colCalc(right))) #How far right side can move
                #print("\tRight Col: " + str(rightCol))

                bestCol = min(edgeCol, rightCol) #As far right I can move considering both edge and rightSide
                #print("\tBest  Col: " + str(bestCol))

                right.column = max(bestCol, right.column)
                edge.column = bestCol

            right.column = max(bestCol, right.column)
            edge.column = bestCol

        #Then children
        for c in reversed(node.children):
            traversal(c)

        #Then Left
        left  = nodeToVertices[node][Type.LEFT]
        left.column = colCalc(left)( min(left.outgoing, key = colCalc(left)))

    traversal(root)

#Move edges and leftSides as far right as possible
#    for v in reversed(order):
#            if v.type == Type.LEFT:
#                assert len(v.outgoing) > 0
#                v.column = colCalc(v)( min(v.outgoing, key = colCalc(v)))
#            if v.type == Type.EDGE:
#                print("Processing edge: " + str(v))
#
#                assert len(v.outgoing) > 1
#
#                rightSide = next(r for r in v.outgoing if r.node == v.node)
#                print("\tRight Side: " + str(rightSide))
#
#                assert(rightSide)
#
#                if rightSide.outgoing:
#                    rightCol = colCalc(rightSide)( min(rightSide.outgoing, key = colCalc(rightSide))) #How far right side can move
#                    print("\tRight Col: " + str(rightCol))
#
#                    vCol = colCalc(v) ( min( (w for w in v.outgoing if w != rightSide), key = colCalc(v)))
#                    print("\tV     Col: " + str(vCol))
#
#                    bestCol = min(vCol, rightCol) #As far right I can move considering both edge and rightSide
#                    print("\tBest  Col: " + str(bestCol))
#
#                    rightSide.column = max(bestCol, rightSide.column)
#                    v.column = bestCol
#                else:
#                    vCol = colCalc(v) ( min( (w for w in v.outgoing if w != rightSide), key = colCalc(v)))
#                    print("\tV     Col: " + str(vCol))
#
#                    bestCol = vCol
#
#                    rightSide.column = max(bestCol, rightSide.column)
#                    v.column = bestCol


# order is topological order of the constraint DAG
def assignColumns(order):

    assignLeftLeaning(order)


    width = max(order, key = lambda v : v.column).column

    return width

#Assigns from vertices to nodes
def assignToNodes(vertices):
    for v in vertices:
        if v.type == Type.LEFT:
            v.node.start = v.column
        elif v.type == Type.EDGE:
            v.node.incoming = v.column
        else:
            v.node.end = v.column

def printEdges(vertices):

    def simple(v):
        return "<" + str(v.node.height) + " - " + str(v.type.name) + ">"

    for v in sorted(vertices, key= lambda v: (v.node.height, v.type) ):
        print(simple(v), end=" --> \t")
        for o in sorted(v.outgoing, key = lambda o: (o.node.height, o.type) ):
            print(simple(o), end=" ")
        print()

def embedTree(root, polygonCalculations = True):

    if root == None:
        return 0
    if root.isLeaf():
        root.start = 0
        root.end = 0
        root.stats.whitespace = 0
        return 1

    vertices, nodeToVertices = makeDAG(root)

    order = topologicalSort(vertices)

    width = assignColumns(order)
    height = getMaxHeight(root)
    root.dims=(width,height)

    tightenRight(root, nodeToVertices)


    assignToNodes(vertices)

    if polygonCalculations:
        root.stats.leftBorder, root.stats.rightBorder = calculateBorders(root)
        root.stats.whitespace = calculateArea(root.stats.leftBorder, root.stats.rightBorder)

    return width

def calculateBorders(root):

    def getBorder(node, isLeftSide, prevWasLeaf, border):

        if node == None: return

        if not border or border[-1][1] < node.height:
            height = node.height
            if prevWasLeaf and border[-1][1] + 1 < node.height:
                border.append( (node.incoming, border[-1][1] + 1))
            border.append( (node.start if isLeftSide else node.end, node.height))
            if not node.children:
                return True
            else:
                prevWasLeaf = False

        for c in node.children if isLeftSide else reversed(node.children):
            prevWasLeaf = getBorder(c, isLeftSide, prevWasLeaf, border)

        return prevWasLeaf

    if root == None: return ([],[])

    leftBorder  = []
    rightBorder = []

    getBorder(root, True , False, leftBorder)
    if leftBorder:
        leftBorder.append( (leftBorder[-1][0], leftBorder[-1][1]+1))
    getBorder(root, False, False, rightBorder)
    if rightBorder:
        rightBorder.append( (rightBorder[-1][0], rightBorder[-1][1]+1))

    return leftBorder,rightBorder


def calculateArea(leftBorder, rightBorder):

    #print("Left  Border: " + str(leftBorder));
    #print("Right Border: " + str(rightBorder));

    i = 1
    j = 1

    leftSide  = leftBorder[0][0]
    rightSide = rightBorder[0][0]
    currentHeight = leftBorder[0][1]

    total = 0;
    while i < len(leftBorder) and j < len(rightBorder):

        width = (rightSide-leftSide) + 1
        #print(str(leftBorder[i]) + " + " + str(rightBorder[j]) + " --> " + str(width) + " h: " + str(currentHeight))

        if leftBorder[i][1] < rightBorder[j][1]:
            leftSide, nextHeight = leftBorder[i]
            i += 1
        elif leftBorder[i][1] > rightBorder[j][1]:
            rightSide, nextHeight = rightBorder[j]
            j += 1
        else:
            leftSide, nextHeight = leftBorder[i]
            rightSide = rightBorder[j][0]
            i += 1
            j += 1

        total += (nextHeight-currentHeight) * width

        #print("Total = " + str(total))

        currentHeight = nextHeight;

    return total

# Lower bound computation based on number of elements per row
def lowerBound(root):
    maxHeight = getMaxHeight(root)
    elementsPerRow = [0 for i in range(maxHeight + 1)]
    addElementsRec(root, elementsPerRow)
    return max(elementsPerRow) - 1

# Recursively count the elements on each level in the current subtree
def addElementsRec(node, elementsPerRow):
    if node.parent:
        assert node.parent.height < node.height, "Found child " + str(node) + " lower than parent " + str(node.parent)
        for i in range(node.parent.height, node.height):
            elementsPerRow[i] += 1

    if node.children:
        for c in node.children:
            addElementsRec(c, elementsPerRow)
    else:
        elementsPerRow[node.height] += 1

# --------------------------------------------------------------------------------
# OLD Table Based DAG Creation (saved for testing correctness)
# --------------------------------------------------------------------------------    

def rowMakeDAG(root):
    constraintTable, vertices = makeConstraintTable(root)

    if FIXED_DEBUG:
        for v in vertices:
            print( (v.node.height, v.type.name), end=" --> \t")
            for n in v.outgoing:
                print( (n.node.height, n.type.name), end=" ")
            print()

    addEdges(constraintTable)


    if FIXED_DEBUG:
        print("After adding edges")
        for v in vertices:
            print( (v.node.height, v.type.name, len(v.incoming)), end=" --> \t")
            for n in v.outgoing:
                print( (n.node.height, n.type.name), end=" ")
            print()

    return vertices

def addConstraints(node, constraintTable, vertices):

#First add the edge to each row. Notice we don't add leftSide->IncomingEdge-RightSide constraint as it is already added

    leftSide, edgeVertex, rightSide = createVertices(node)
    vertices.add(leftSide)
    vertices.add(rightSide)

    if edgeVertex: #root doesn't have one!
        vertices.add(edgeVertex)
        assert node.parent.height < node.height, "Found child " + str(node) + " lower than parent " + str(node.parent)
        for i in range(node.parent.height, node.height):
            constraintTable[i].append(edgeVertex)

    #Inorder traversal: Left side, outgoing edges and right side
    constraintTable[node.height].append(leftSide)
    for c in node.children:
        addConstraints(c, constraintTable, vertices)
    constraintTable[node.height].append(rightSide)

def makeConstraintTable(root):

    maxHeight = getMaxHeight(root)

    if FIXED_DEBUG:
        print("Max Height: " + str(maxHeight))

    constraintTable = [ [] for x in range(maxHeight+1)] #one row per y-coord, not optimal but simple

    vertices = set()
    addConstraints(root, constraintTable, vertices)

    if FIXED_DEBUG:
        for i,r in enumerate(constraintTable):
            print(i, end="\t")
            for c in r:
                print( (c.node.height, c.type.name), end="\t")
            print()

    return constraintTable, vertices

def addEdges(constraintTable):

    for row in constraintTable:
        for i in range(len(row)-1):
            row[i].addEdge(row[i+1])




#leftLeft = Node(None, 8, [])
#leftRight = Node(None, 10, [])
#left = Node(None, 5, [leftLeft, leftRight])
#
#rightRight = Node(None, 9, [])
#right = Node(None, 7, [rightRight])
#
#root = Node(None, 0, [left,right])
##
#embedTree(root)

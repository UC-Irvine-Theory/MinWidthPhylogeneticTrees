from collections import deque
from enum import IntEnum
from node import Node

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

def createVertices(node, isRoot):
    leftSide  = Vertex(node, Type.LEFT)
    rightSide = Vertex(node, Type.RIGHT)

    incoming = None
    if isRoot:
        leftSide.addEdge(rightSide)
    else:
        incoming = Vertex(node, Type.EDGE)
        leftSide.addEdge(incoming)
        incoming.addEdge(rightSide)

    return leftSide, incoming, rightSide

def preorderEdges(node, l, parentIndex, vertices, isRoot):

    class Range:
        def __init__(self, height, vertex):
            self.height = height
            self.vertex = vertex

        def __str__(self):
            return str((self.height, self.vertex.type.name))

    leftSide, incoming, rightSide = createVertices(node, isRoot)
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
            preorderEdges(c, l, nodeIndex, vertices, False)
#Right side of the node
        l[nodeIndex].vertex.addEdge(rightSide) #Rightmost edge
        l.insert(nodeIndex, Range(node.height, rightSide))
    else:
        leftSide.addEdge(rightSide)
        l[nodeIndex] = Range(node.height, rightSide) #Replace Left Side

def makeDAG(root):

    vertices = set()
    l = []
    preorderEdges(root, l, -1, vertices, True)

    return vertices

def topologicalSort(vertices):

    result = []

    inCounts = { v:len(v.incoming)  for v in vertices }

    queue = deque( v for v in vertices if (len(v.incoming) == 0) )
    while queue:
        v = queue.popleft()
        result.append(v)

        for n in v.outgoing:
            inCounts[n] = inCounts[n] - 1
            if inCounts[n] == 0:
                queue.append(n)

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

def tightenRight(order):
    def colCalc(v):
        def leftColCalc(n):
            assert n.type != Type.LEFT
            return n.column
        def edgeColCalc(n):
            if n.type == Type.RIGHT:
                return n.column
            else:
                return n.column - 1

        assert v.type != Type.RIGHT

        if v.type == Type.LEFT:
            return leftColCalc
        else:
            return edgeColCalc

#Move edges and leftSides as far right as possible
    for v in reversed(order):
        if v.type == Type.RIGHT:
            continue
        else:
            assert len(v.outgoing) > 0
            v.column = colCalc(v)( min(v.outgoing, key = colCalc(v)))

# order is topological order of the constraint DAG
def assignColumns(order):

    assignLeftLeaning(order)

    tightenRight(order)

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

def embedTree(root):

    if root == None:
        return 0
    if root.isLeaf():
        root.start = 0
        root.end = 0
        root.stats.whitespace = 0
        return 1

    vertices = makeDAG(root)

    order = topologicalSort(vertices)

    width = assignColumns(order)
    height = getMaxHeight(root)
    root.dims=(width,height)

    calculateWhiteSpace(vertices, root)

    assignToNodes(vertices)

    return width


def calculateWhiteSpace(vertices, root):

    for v in vertices:
        if v.type == Type.LEFT:
            v.whitespace = 0
        elif v.type == Type.RIGHT:
            assert len(v.outgoing) <= 1
            if v.outgoing:
                v.whitespace = next(iter(v.outgoing)).column - v.column - 1
                assert v.whitespace >= 0
            else:
                v.whitespace = 0
        else:
            assert v.node != root
            top = v.node.parent.height
            bottom = v.node.height

            whitespace = dict()
            for i in range(top, bottom):
                whitespace[i] = -1

            for n in v.outgoing:
                if n.type == Type.RIGHT:
                    continue
                elif n.type == Type.LEFT:
                    currentWhiteSpace = whitespace[n.node.height]
                    newWhiteSpace = n.column - v.column
                    assert newWhiteSpace > 0
                    if currentWhiteSpace == -1 or newWhiteSpace < currentWhiteSpace:
                        whitespace[n.node.height] = newWhiteSpace - 1
                elif n.type == Type.EDGE:
                    nTop = n.node.parent.height
                    nBottom = n.node.height
                    newWhiteSpace = n.column - v.column
                    assert newWhiteSpace > 0
                    newWhiteSpace = newWhiteSpace - 1
                    for i in range(nTop,nBottom):
                        if i in whitespace:
                            currentWhiteSpace = whitespace[i]
                            if currentWhiteSpace == -1 or newWhiteSpace < currentWhiteSpace:
                                whitespace[i] = newWhiteSpace

            total = sum( filter(lambda w : w >= 0, whitespace.values()) )

            v.whitespace = total

    total = 0
    for v in vertices:
        #print( (v.node.dNode, v.type.name, v.whitespace))
        total += v.whitespace

    root.stats.whitespace = total



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

    leftSide, edgeVertex, rightSide = createVertices(node, node.parent == None)
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

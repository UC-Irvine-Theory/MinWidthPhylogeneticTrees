from node import Node
from enum import IntEnum

class Rect:

    def __init__(self, top,left, bottom,right):
        self.top = top
        self.left = left
        self.bottom = bottom
        self.right = right

    def width(self):
        return (self.right-self.left)

    def height(self):
        return (self.top-self.bottom)

    def area(self):
        return self.width() * self.height()

    def __str__(self):
        return "[" + str(self.top) + ',' + str(self.left) + " " + str(self.bottom) + ',' + str(self.right) + ']'

class ShapeType(IntEnum):
    L = 1
    P = 2
    T = 3
    A = 4
    Z = 5
    I = 6

class Shape:

    def __init__(self, tree):
        if tree.isLeaf():
            self.bottomRect = Rect(tree.height,tree.start, tree.height+1,tree.end+1,)
            self.topRect = Rect(0,0, 1,1)
            self.type = ShapeType.I
            self.tree = tree
        else:
            self.bottomRect, self.topRect = approximateWithTwoRects(tree.stats.leftBorder, tree.stats.rightBorder)
            self.type = self.getType(self.bottomRect, self.topRect)
            self.tree = tree

    def getType(self,bottomRect, topRect):

        ratio = 0.1
        threshold = ratio * max(bottomRect.width(), topRect.width())

        leftAligned  = abs(bottomRect.left - topRect.left) < threshold
        rightAligned = abs(bottomRect.right - topRect.right) < threshold

        if leftAligned and rightAligned:
            return ShapeType.I
        elif leftAligned != rightAligned:
            if bottomRect.width() > topRect.width():
                return ShapeType.L
            else:
                return ShapeType.P
        else:
            if bottomRect.left < topRect.left and bottomRect.right > topRect.right:
                return ShapeType.A
            elif bottomRect.left > topRect.left and bottomRect.right < topRect.right:
                return ShapeType.T
            else:
                return ShapeType.Z

    def width(self):
        return max(self.bottomRect.width(), self.topRect.width())

    def thinWidth(self):
        return min(self.bottomRect.width(), self.topRect.width())

    def better(self, other):
        assert(self.type == other.type)

        if self.type == ShapeType.L:
            if self.thinWidth() != other.thinWidth():
                return self.thinWidth() != other.thinWidth()
            else:
                return self.width() < other.width()
        elif self.type == ShapeType.P:
            if self.thinWidth() != other.thinWidth():
                return self.thinWidth() != other.thinWidth()
            else:
                return self.width() < other.width()
        elif self.type == ShapeType.T:
            if self.thinWidth() != other.thinWidth():
                return self.thinWidth() != other.thinWidth()
            else:
                return self.width() < other.width()
            return self.thinWidth() < other.thinWidth()
        elif self.type == ShapeType.A:
            if self.width() != other.width():
                return self.width() != other.width()
            else:
                return self.thinWidth() < other.thinWidth()
        elif self.type == ShapeType.Z:
            def displacement(shape):
                return abs(shape.bottomRect.left - shape.topRect.left) 
                + abs(shape.bottomRect.right - shape.topRect.right)

            if displacement(self) != displacement(other):
                return displacement(self) > displacement(other)
            else:
                return self.width() < other.width()
        else:
            if self.width() != other.width():
                return self.width() != other.width()
            else:
                return self.thinWidth() < other.thinWidth()

def approximateWithTwoRects(leftBorder, rightBorder):

    #print("Left Border:");
    #for l in leftBorder:
    #    print("\t" + str(l))
    #print("Right Border:");
    #for l in rightBorder:
    #    print("\t" + str(l))
    #print("------------");


    assert(leftBorder)
    assert(rightBorder)

    assert(len(leftBorder)  >= 2)
    assert(len(rightBorder) >= 2)

    rootToLeavesRects = []

    currLeft = leftBorder[0][0]
    currRight = rightBorder[0][0]
    bottom = leftBorder[0][1]

    l = 1
    r = 1
    while l < len(leftBorder) and r < len(rightBorder):

        leftHeight  = leftBorder[l][1]
        rightHeight = rightBorder[r][1]

        nextHeight = min(leftHeight, rightHeight)

        if leftHeight  == nextHeight:
            if currLeft > leftBorder[l][0]:
                currLeft = leftBorder[l][0]
            l += 1
        if rightHeight == nextHeight:
            if currRight < rightBorder[r][0]:
                currRight = rightBorder[r][0]
            r+=1

        rootToLeavesRects.append(Rect(nextHeight, currLeft, bottom, currRight+1))

    while l < len(leftBorder):
        nextHeight = leftBorder[l][1]

        if currLeft > leftBorder[l][0]:
            currLeft = leftBorder[l][0]
        l += 1

        rootToLeavesRects.append(Rect(nextHeight, currLeft, bottom, currRight+1))


    while r < len(rightBorder):
        nextHeight = rightBorder[l][1]

        if currRight < rightBorder[l][0]:
            currRight = rightBorder[l][0]
        r += 1

        rootToLeavesRects.append(Rect(nextHeight, currLeft, bottom, currRight+1))

    leavesToRootRects = []

    currLeft  = leftBorder[-1][0]
    currRight = rightBorder[-1][0]
    top = leftBorder[-1][1]

    l = len(leftBorder)-2
    r = len(rightBorder)-2

    while l >= 0 and r >= 0:
        leftBottom  = leftBorder[l][1]
        rightBottom = rightBorder[r][1]

        nextBottom = max(leftBottom, rightBottom)

        if leftBottom  == nextBottom:
            if currLeft > leftBorder[l][0]:
                currLeft = leftBorder[l][0]
            l -= 1
        if rightBottom == nextBottom:
            if currRight < rightBorder[r][0]:
                currRight = rightBorder[r][0]
            r-=1

        leavesToRootRects.append(Rect(top, currLeft, nextBottom, currRight+1))

    while l  >= 0:
        nextBottom = leftBorder[l][1]

        if currLeft > leftBorder[l][0]:
            currLeft = leftBorder[l][0]
        l -= 1

        leavesToRootRects.append(Rect(top, currLeft, nextBottom, currRight+1))


    while r >= 0:
        nextHeight = rightBorder[l][1]

        if currRight < rightBorder[l][0]:
            currRight = rightBorder[l][0]
        r -= 1

        leavesToRootRects.append(Rect(top, currLeft, nextBottom, currRight+1))

    assert(len(rootToLeavesRects) == len(leavesToRootRects))

    rootToLeavesRects = rootToLeavesRects[:-1]
    leavesToRootRects = leavesToRootRects[:-1]

    #for r in rootToLeavesRects:
    #    print(r)
    #print("----")
    #for r in reversed(leavesToRootRects):
    #    print(r)

    bestRootToLeaf = rootToLeavesRects[0]
    bestLeafToRoot = leavesToRootRects[-1]
    bestArea = bestRootToLeaf.area() + bestLeafToRoot.area()

    for l,r in zip(rootToLeavesRects, reversed(leavesToRootRects)):
        area = l.area() + r.area()
        if area < bestArea:
            bestArea = area
            bestRootToLeaf = r
            bestLeafToRoot = l

    #print("Best area " + str(bestArea) + " with: " + str(bestRootToLeaf) + " and " + str(bestLeafToRoot)) 

    return (bestRootToLeaf,bestLeafToRoot)




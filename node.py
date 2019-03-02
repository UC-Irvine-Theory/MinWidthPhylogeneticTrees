import dendropy

#Represents a tree node and its drawing information
class Node:

    class Stats:
        def __init__(self, subtreeSize, distanceToLeaf, nodesToLeaf):
            self.subtreeSize = subtreeSize
            self.distanceToLeaf = distanceToLeaf
            self.nodesToLeaf = nodesToLeaf

        def __str__(self):
            return "<SS:" + str(self.subtreeSize) + ", D2L:" + str(self.distanceToLeaf) + ", N2L:" + str(self.nodesToLeaf) + ">";

    def __init__(self,dNode, height, children, parent = None, start = -1, end = -1, incoming = -1):
        self.dNode = dNode
        self.height = height
        self.children = children
        for c in children:
            c.parent = self
        self.parent = parent
        self.start = start
        self.end = end
        self.incoming = incoming

        assert start <= end,      "start " + str(start) + " must be <= end " + str(end)
        assert start >= incoming, "start " + str(start) + " must be <= incoming " + str(incoming)
        assert incoming <= end,   "incoming " + str(incoming) + " must be <= end " + str(end)

    def isLeaf(self):
        return not self.children

    def left(self):
        return self.children.keys()[0]
    def left(self, newLeft):
        self.children.insert(0, newLeft)
        newLeft.parent = self

    def right(self):
        return self.children.keys()[-1]
    def right(self, newRight):
        self.children.append(newRight)
        newRight.parent = self

    def printMe(self,depth, printer = str):
        print( "\t"*depth + printer(self))
        for c in self.children:
            c.printMe(depth+1, printer)

    def incomingLength(self):
        if self.parent:
            return self.height - self.parent.height
        else:
            return 0

    def __str__(self):
        return str((self.height,    self.start, self.incoming, self.end))

    def fillStats(self):
        if self.isLeaf():
            self.stats = Node.Stats(1, 0, 0)
        else:
            for c in self.children:
                c.fillStats()

            distToLeafCalc = lambda c : c.stats.distanceToLeaf + c.incomingLength()

            subtreeSize    = 1 + sum(c.stats.subtreeSize for c  in self.children)
            distanceToLeaf = distToLeafCalc( max(self.children, key = lambda c : distToLeafCalc(c)) )
            nodesToLeaf    = max(self.children, key = lambda c : c.stats.nodesToLeaf).stats.nodesToLeaf + 1

            self.stats = Node.Stats(subtreeSize, distanceToLeaf, nodesToLeaf)


    def size(self):
        count = 1
        for c in self.children:
            count += c.size()
        return count


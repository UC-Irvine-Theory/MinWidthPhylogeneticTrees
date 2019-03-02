import pdb

import copy
import itertools
import random
from node import Node
from fixedOrderEmbedder import embedTree

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

        def flip(node):
            if node.children:
                node.children.reverse()

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

        def flip(node):
            if node.children:
                node.children.reverse()

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


def veeShape(root):

    newTree = copy.deepcopy(root)

    def side(node, amLeft):
        node.children.sort(key = lambda c : c.stats.distanceToLeaf, reverse = amLeft)
        for c in node.children:
            side(c, amLeft)

    def middle(node, amLeft):
        node.children.sort(key = lambda n : n.stats.distanceToLeaf, reverse = amLeft)

        if node.children:
            if amLeft:
                for c in node.children[:-1]:
                    side(c, amLeft)
                middle(node.children[-1], not amLeft)
            else:
                for c in node.children[1:]:
                    side(c, not amLeft)
                middle(node.children[0], not amLeft)

    middle(newTree, True)

    return newTree


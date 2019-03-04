import argparse
import sys

import dendropy

from fixedOrderEmbedder import embedTree
from node import Node

def normalize(tree):
    distances = tree.calc_node_root_distances(return_leaf_distances_only=False)

    #Remove uniques
    distances =  list(set(distances))

    distances.sort()
    distanceMap = dict()
    for i,d in enumerate(distances):
       distanceMap[d] = 4*i

    for n in tree:
        n.norm_root_distance = distanceMap[n.root_distance]

    return tree

def create(dNode):

    children = []
    for dc in dNode.child_node_iter():
        child = create(dc)
        children.append(child)

    node = Node(dNode, dNode.norm_root_distance, children)

    return node

def hasEdgeLengths(rawTree):

    if rawTree.length() == 0:
        return False

    zeroLengthEdges = rawTree.edges(lambda e : e.length == None)

    return True

def fixZeroLengthEdges(node):

    if node.parent:
        if node.parent.height >= node.height:
            node.height = node.parent.height + 2

    for c in node.children:
        fixZeroLengthEdges(c)

def read(path, schema):

    rawTree = dendropy.Tree.get(path=path, schema=schema)

    rawTree = normalize(rawTree)

    root = create(rawTree.seed_node)

    fixZeroLengthEdges(root)

    return root

def readTrees(path, schema):

    rawTrees = dendropy.TreeList.get(path=path, schema=schema, suppress_internal_node_taxa=True, suppress_leaf_node_taxa=True)

    trees = []
    for i,rawTree in enumerate(rawTrees):
        #Filter out trees without edge lengths
        if not hasEdgeLengths(rawTree):
            print("Warning tree " + str(i) + " has no edge lengths, skipping")
            continue

        try:
            rawTree = normalize(rawTree)

            tree = create(rawTree.seed_node)

            fixZeroLengthEdges(tree)
        except:
            print("Warning tree " + str(i) + " ran into an error, skipping")
            continue

        trees.append(tree)

    return trees


def cleanFile(path, schema, outputPath):

    def unclean(tree):
        if not hasEdgeLengths(tree):
            return False

        #large degree nodes?
        maxDegreeNode = max(tree, key = lambda node : len(node.child_nodes()))

        if len(maxDegreeNode.child_nodes()) > 4:
            return False

        if len(tree.nodes()) < 20:
            return False

        return True


    inputTrees = dendropy.TreeList.get(path=path, schema=schema, suppress_internal_node_taxa=True, suppress_leaf_node_taxa=True)

    print("Read in " + str(len(inputTrees)) + " trees\nCleaning...")

    trees = dendropy.TreeList(filter(unclean, [dendropy.Tree(t) for t in inputTrees]))

    trees.purge_taxon_namespace()

    print("Writing " + str(len(trees)) + " trees")

    trees.write(path=outputPath, schema=schema)

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("inputPath", help ="Path to file with trees")
    parser.add_argument("schema"   , help = 'Schema of input file ("newick", "nexus", "nexml")')
    parser.add_argument("outputPath", help ="Path to output path with cleaned trees")

    args = parser.parse_args()

    print("Welcome to the reader utility")
    cleanFile(args.inputPath, args.schema, args.outputPath)

if __name__ == "__main__":
    main()


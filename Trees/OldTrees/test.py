import dendropy


tree = dendropy.Tree.get(path="./TreeBase_S19934", schema = "nexml")

#i = 0
#for node in tree.preorder_node_iter():
#    print(node)
#    i += 1

tree.print_plot()

#print("Number of nodes: " + str(i))

heights = tree.calc_node_root_distances(False)
#heights = tree.calc_node_root_distances(return_lef_distance_only=False)


#for h in sorted(heights):
#    print(h)

i = 0
for node in tree.preorder_node_iter():
    print(str(i) + "\t" + str(node.root_distance))
    i += 1

print("All clear")

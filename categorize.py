import numpy as np
import math
from runner import makeScatter,write_file
from readTree import readTrees
import sys
# Categories
# drawing
# 1. bottom leafed
# 2. unit-edged
# tree
# 1. balanced
# 2. heavy
def is_bottom_leafed(root):
	leaves=find_leaves(root)
	parents = [leaf.parent for leaf in leaves if leaf!=leaf.parent]

	max_p = max(parents,key=lambda p: p.height)
	min_l = min(leaves,key=lambda l:l.height) 
	if max_p.height>min_l.height:
		return False
	return True
def is_unit_edged(root):
	max_dif=calc_max_edge_dif(root)
	if max_dif==0:
		return True
	else:
		return False
def is_high_variation(root,portion_nodes=0.5,varition_th=0.3):
	d,ct = get_depth_and_ct(root)
	var = count_over(root,threshold=varition_th)
	ct= ct - len(find_leaves(root))
	if var*1./ct > portion_nodes:
		return True
	return False
def count_over(root,threshold=0.5):
	if root.isLeaf():
		return 0
	lowc = max(root.children,key=lambda c:c.height).height
	dif=lowc-min(root.children,key=lambda c: c.height).height
	fr = dif/lowc
	if fr > threshold:
		ct = 1
	else:
		ct = 0
	for c in root.children:
		ct=ct+count_over(c,threshold)
	return ct	
def is_low_variation(root,portion_nodes=0.5,varition_th=0.3):
	d,ct = get_depth_and_ct(root)
	var = count_over(root,threshold=varition_th)
	ct= ct - len(find_leaves(root))
	if var*1./ct < portion_nodes:
		return True
	return False
def is_balanced(root,threshold=.5):
	deepest = depth(root,f=lambda x: max(x))
	shallowest = depth(root,f=lambda x:min(x))
	if deepest-shallowest>threshold*deepest:
		return False
	return True
def count_nodes(root):
	if root.isLeaf():
		return 1
	ct=sum([count_nodes(c) for c in root.children])
	return ct+1
def depth(root,f=max):
	if root.isLeaf():
		return 1
	depths=f([depth(c) for c in root.children])
	return depths+1
def calc_max_edge_dif(root):
	if root.isLeaf():
		return None
	dif=max(root.children,key=lambda c:c.height).height-min(root.children,key=lambda c: c.height).height
	for c in root.children:
		cdif=calc_max_edge_dif(c)
		if cdif and cdif>dif:
			dif=cdif
	return dif
def get_depth_and_ct(root):
	if root.isLeaf():
		return 1,1
	dnc=np.array([get_depth_and_ct(c) for c in root.children])
	ct=sum(dnc[:,1])
	difmx= math.ceil(max(dnc[:,0]))
	difmn= math.floor(min(dnc[:,0]))
	if difmn==-1 or difmx==-1:
		return -1, ct+1
	if difmx-difmn<=1:
		depth=(difmx+difmn)/2
	else:
		depth=-1
	return depth+1, ct+1
def find_leaves(root):
	if root.isLeaf():
		return [root]
	leaves=[]
	for c in root.children:
		leaves=leaves+find_leaves(c)
	return leaves
topo={#is_balanced:"Balanced",lambda root:not is_balanced(root):"Unbalanced"
}
edges={	#is_unit_edged:"Unit Edges",
		is_high_variation:"HighVar",
		is_low_variation:"LowVar"
		}
solo={is_bottom_leafed:"BotLeafed"}
def condense(allResults, bin_size=2):
    results={}
    for id,size,res in allResults:
        bn = int(size)//bin_size
        if not(bn in results):
            results[bn]={'ct':1}
        else:
            results[bn]['ct']=results[bn]['ct']+1
        for name, width in res:
        	if not(name in results[bn]):
        		results[bn][name]=0
        	results[bn][name]=results[bn][name]+int(width)
    out=[]
    for bn,res in results.items():
        outarr=[]
        for k,sm in res.items():
        	if k=='ct':
        		continue
        	outarr.append((k,sm/res['ct']))
        out.append((0,bn*bin_size+bin_size/2,outarr))
    return out
def filterFile(path, schema, outputPath=None,remove_solo=False,csv=None):
    trees = readTrees(path,schema)
    rem = set()
    results={}
    for cat in solo.keys():
    	temp=list(map(cat,trees))
    	res = np.where(temp)[0]
    	results[solo[cat]]=res
    	results['not'+solo[cat]]=np.where([not(t) for t in temp])[0]
    	if remove_solo:
    		rem.update(res)
    
    for top in topo.keys():
    	filt = np.array(list(map(top,trees)))
    	#print(filt)
    	for w in edges.keys():
    		temp=list(map(w,trees))
    		res = np.where(temp*filt)[0]
    		if len(res)==0:
    			print(edges[w],topo[top],"No Matches")
    			continue
    		res = [r for r in res if not (r in rem)]
    		results[str(edges[w])+str(topo[top])]=res
    		#print(edges[w],topo[top],res)
    print(results)
    read,seed,names,from_file = read_results(csv)
    if read!=path:
    	print('CSV for ('+read+') does not match current path ('+path+')')
    	return
    else:
    	print('CSV file for '+read+' matches file'+path)
    if not outputPath:
    	outputPath=path[-4]
    binned = condense(from_file)
    makeScatter(binned)
    makeScatter(from_file)
    get_stats(from_file)
    for k,sat in results.items():
    	to_draw=[t for i,t in enumerate(from_file) if i in sat]
    	print('\nAnalysing '+str(len(to_draw))+' trees ('+k+')')
    	makeScatter(to_draw)
    	get_stats(to_draw)
    	if len(k)==0:
    		k='1'
    	write_file(read,schema,seed,to_draw,names,outpath=(csv[:-4]+str(k)+'.csv'))
def get_stats(allResults):
	best_cts=count_best(allResults)
	better=better_than_greedy(allResults)
	names,absolute,fraction=calc_avg_over_human(allResults)
	#print(best_cts,names,len(allResults))
	print('Heuristic','&','Absolute Change','&','Percent Change (\%)','&','Best Count','&','Percent Best(\%)','\\\\')
	for i,name in enumerate(names):
		print(name,'&',int(absolute[i]),'&',round(fraction[i]*100,2),'&',int(best_cts.get(name,0)),'&',round(best_cts.get(name,0)*100.0/len(allResults),2),'\\\\')
	print('Non-Greedy Best:')
	for i,r in better:
		if r!='Greedy' and r!='White':
			print(i,r)

def read_results(fn):
	with open(fn,'r') as file:
		line = list(map(str.strip, file.readline().split(',')))
		path=line[0]
		schema=line[1]
		seed = list(map(str.strip, file.readline().split(',')))[1]
		names = list(map(str.strip, file.readline().split(',')))[2:-1]
		print(names)
		file.readline()
		from_file = []
		for line in file:
			words = list(map(str.strip, line.split(',')))
			i=words[0]
			size = words[1]
			tests = words[2:]
			from_file.append((i,size,[(n,w) for n,w in zip(names,tests)]))
		return path,seed,names,from_file
	return None
def find_best(allResults):
	best = {}
	for i,size,results in allResults:
		best[i]=max(results,key=lambda r:r[1])
	return best
def count_best(allResults):
	best = {}
	for i,size,results in allResults:
		w = 1e20
		bests=[]
		for name,width in results:
			if w>int(width):
				bests=[name]
				w=int(width)
			elif w==int(width):
				bests.append(name)
		for be in bests:
			best[be]=best.get(be,0)+1
	return best
def better_than_greedy(allResults):
	better=[]
	for i,size,results in allResults:
		res = {name:width for name,width in results}
		b = [name for name in res.keys() if res[name]<res["Greedy"]]
		if len(b)!=0:
			better.append((i,b))
	return better

def calc_avg_over_human(allResults):
	sums=np.zeros(len(allResults[0][2]))
	names=['']*len(allResults[0][2])
	for i,size,results in allResults:
		for j,data in enumerate(results):
			name,width = data
			sums[j]=sums[j]+int(width)
			names[j]=name
	h = names.index('Orig')
	human = sums[h]
	abs_width_d = [sums[i]-human for i in range(len(sums))]
	frac_width_d = [abs_width_d[i]*1./human for i in range(len(sums))]
	return names,abs_width_d,frac_width_d
def main():
	print("Welcome to the reader utility")
	if len(sys.argv) != 4:
			print(sys.argv[0]+' [infile] [schema] [csv_file]')
			return
	if len(sys.argv)!=4:
		filterFile(sys.argv[1], sys.argv[2])
	else:
		filterFile(sys.argv[1],sys.argv[2],csv=sys.argv[3])

if __name__ == "__main__":
    main()

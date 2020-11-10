import sys

debug_print = True

class Node:
	# name, annotation, children[], is_parent_node, 
	def __init__(self, name, anno):
		self.name = name
		self.anno = anno
		self.children = []
		
	def isLeafNode(self):
		return len(self.children) == 0
	
	def addChild(self, child):
		self.children.append(child)

	def __repr__(self):
		result = "[N]" + self.name + str(self.children)
		if self.anno:
			result += "// " + self.anno
		return result

class Edge:
	def __init__(self, src, dst, anno):
		self.src = src
		self.dst = dst
		self.anno = anno

	def __repr__(self):
		result = "[E]" + self.src + " --> " + self.dst
		if self.anno:
			result += " // " + self.anno
		return result

def makeAnnotation(wordArray, separator):
	CHARS_THRESHOLD = 30
	result = ""
	curLineLen = 0
	for word in wordArray:
		curLineLen += len(word)
		result += word + " "
		if curLineLen > CHARS_THRESHOLD:
			result += separator
			curLineLen = 0
	return result

def makeNodeAnnotation(wordArray):
	return makeAnnotation(wordArray, "<BR />")

def makeEdgeAnnotation(wordArray):
	return makeAnnotation(wordArray, "\\n")

def checkNodeName(name):
	troublemakers = ["."]
	for trouble in troublemakers:
		if trouble in name:
			print "Node name" + name + "has character" + trouble + "which is not an allowed character."
			return False
	return True

def extractNodesAndEdges(simbl_source_file):
	ancestorStack = [] # at any given point, should list nodes ending with the current node 'in scope' / being processed, and beginning with the root ancestor of that node.
	topLevelNodeNames = [] # Node[]
	nodeMap = {} # name : Node 
	edges = [] # Edge[]
	with open(simbl_source_file, 'rb') as simbl_source:
		debug_linecount = 0
		for line in simbl_source:
			debug_linecount += 1
			if debug_print: print debug_linecount
			if line.isspace(): continue
			num_ancestors = 0
			while line[num_ancestors] == '\t': num_ancestors += 1
			ancestorStack = ancestorStack[:num_ancestors]

			lineArr = line.split()
			isEdge = True if lineArr[0] in ["CALLS", "CBY", "CALLEDBY"] else False
			if isEdge:
				node1name = ancestorStack[-1]
				node2name = lineArr[1]
				annotation = makeEdgeAnnotation(lineArr[3:]) if len(lineArr) > 2 and lineArr[2] == "ANNO" else None
				srcNode, dstNode = [node1name, node2name] if lineArr[0] == "CALLS" else [node2name, node1name]
				edges.append(Edge(srcNode, dstNode, annotation))
			else:
				nodeName = lineArr[0]
				checkNodeName(nodeName)
				ancestorStack.append(nodeName)
				annotation = makeNodeAnnotation(lineArr[2:]) if len(lineArr) > 1 and lineArr[1] == "ANNO" else None
				nodeMap[nodeName] = Node(nodeName, annotation)
				if len(ancestorStack) > 1:
					parentNodeName = ancestorStack[-2]
					nodeMap[parentNodeName].addChild(nodeName)
				else:
					topLevelNodeNames.append(nodeName)
		return topLevelNodeNames, nodeMap, edges

def printPrelude():
	print '''
digraph G {
	compound=true;
	# rankdir=LR; # uncomment to make graph go left to right
	fontname=\"Arial\" fontsize=8;
	node [
		shape=box color=steelblue
		fontname=\"Helvetica\" fontsize=8 
		margin=0.03 width=0 height=0];
	edge [
		fontname=\"Helvetica\" fontsize=6 fontcolor=steelblue
		color=steelblue
		arrowsize = 0.5]
	'''

def leafNodeToString(node):
	if node.anno is not None:
		return node.name + "[label=<" + node.name +"<BR /><FONT POINT-SIZE='6'>" + node.anno +"</FONT>>];"
	else:
		return node.name + ";"

def getClusterAlias(parentNodeName):
	return "cluster_" + parentNodeName

def printNodesDescendedFromTopLevelNode(nodeName, nodeMap, tabDepth=1):
	tabstr = "\t" * tabDepth
	node = nodeMap[nodeName]

	if node.isLeafNode():
		print tabstr + leafNodeToString(node)
	else: # has children - turn into 'cluster' and recurse on children
		print tabstr + "subgraph " + getClusterAlias(nodeName) + " {"
		if node.anno is not None:
			print tabstr + "label=<" + nodeName + "<BR /><FONT POINT-SIZE='6'>" + node.anno + "</FONT>>"
		else:
			print tabstr + "label =\"" + nodeName +  "\""
		for childName in node.children:
			printNodesDescendedFromTopLevelNode(childName, nodeMap, tabDepth + 1)
		print tabstr + "}"

def isParentNode(nodeName, nodeMap):
	return nodeName in nodeMap and not nodeMap[nodeName].isLeafNode()

def findLeafDescendantName(nodeName):
	node = nodeMap[nodeName]
	while node and not node.isLeafNode():
		nodeName = node.children[0]
		node = nodeMap[nodeName]
	return nodeName

hue = 0.4
def getNextEdgeAnnotationColor():
	global hue
	hue += 0.17
	if hue >= 1.00: hue -= 1.0
	return str(hue) + " 0.25 0.8"

def printEdges(edges, nodeMap):
	for edge in edges:
		edgeModifierStrArr = []
		# Simbl treats parent nodes and leaf nodes as the same type of entity,
		# but in Dot, they are 'subgraph cluster_nodename { ... }' and 'nodename',
		# and subgraphs cannot point to each other. Leaf nodes a and b can be
		# declared a->b, but subgraphs A and B must use their leaf descendants,
		# like so: a->b [lhead=cluster_B, ltail=cluster_A]. So our first step
		# if one of the nodes is a parent node is to find a leaf descendant and
		# use it instead.
		srcLeafName = edge.src
		if isParentNode(edge.src, nodeMap):
			srcLeafName = findLeafDescendantName(srcLeafName)
			srcClusterName = getClusterAlias(edge.src)
			edgeModifierStrArr.append("ltail=" + srcClusterName)

		dstLeafName = edge.dst
		if isParentNode(edge.dst, nodeMap):
			dstLeafName = findLeafDescendantName(dstLeafName)
			dstClusterName = getClusterAlias(edge.dst)
			edgeModifierStrArr.append("lhead=" + dstClusterName)
		
		if edge.anno is not None:
			edgeModifierStrArr.append("label=\"" + edge.anno + "\"")
			hsv = getNextEdgeAnnotationColor()
			edgeModifierStrArr.append("fontcolor=\"" + hsv + "\"")
			edgeModifierStrArr.append("color=\"" + hsv + "\"")
		
		modifierStr = "[" + " ".join(edgeModifierStrArr) + "]"

		print "\t" + srcLeafName + "->" + dstLeafName + modifierStr + ";"

source_file_name = sys.argv[1] if len(sys.argv) > 1 else 'graph.simbl'
topLevelNodeNames, nodeMap, edges = extractNodesAndEdges(source_file_name)

printPrelude()
for tlNode in topLevelNodeNames:
	printNodesDescendedFromTopLevelNode(tlNode, nodeMap)
print ""
printEdges(edges, nodeMap)
print "}"

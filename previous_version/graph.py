## A class for graph analyses

class Graph(object):
	"""docstring for Graph"""
	def __init__(self, V):
		super(Graph, self).__init__()
		self.V = V  # list of valid nodes
		self.adj = {}  # empty dictionary

		for i in V:
			self.adj[i] = []

	def addEdge(self, u, v):
		if(v not in self.adj[u]):
			self.adj[u].append(v)
			self.adj[v].append(u)

  # Breadth First Search
	def BFS(self, s):
		visited = {}
		for i in self.V:
			visited[i] = False

		queue = []

		queue.append(s)
		visited[s] = True

		subgraph = []

		while(queue != []):
			s = queue.pop(0)
			subgraph.append(s)

			for i in self.adj[s]:
				if(not visited[i]):
					visited[i] = True
					queue.append(i)

		return subgraph

	def subgraphs(self):

		subgraphs = []

		for i in self.V:
			subgraph = self.BFS(i)
			contains = False
			for sb in subgraphs:
				if(set(subgraph) == set(sb)):
					contains = True
					break
			if(not contains):
				subgraphs.append(subgraph)

		print subgraphs

		return subgraphs

#%%

# reads the cnf file, cleans it and returns a list containing nested sub lists
# the sublists contains the literals
def loadCnfFile(fileName):
    cnf=[]
    cnfFile = open(fileName, 'r')
    for line in cnfFile:
        if line[0]!="c" and line[0]!="p":
            l=line.split("0")[0].strip().split(" ")
            m=[]
            for k in l:
                m.append(int(k))
            cnf.append(m)
    cnfFile.close()
    return cnf

# converts the list of clauses with their literals into an implication graph
def listToCnf(cnf):
    dictOut = dict()
    
    # iterate through the list cnf
    for clause in cnf:
        
        # check if literal in 0th index exists as a key in the dictionary
        # if the key exists, add edge
        if int(clause[0])*-1 in dictOut.keys():
            dictOut[int(clause[0])*-1].append(clause[1])
        
        # if the key does not exist, create a new list to store the literals
        else:
            dictOut[int(clause[0])*-1] = []
            dictOut[int(clause[0])*-1].append(clause[1])
        
        # repeat above for the 2nd literal
        if int(clause[1])*-1 in dictOut.keys():
            dictOut[int(clause[1])*-1].append(clause[0])
        else:
            dictOut[int(clause[1])*-1] = []
            dictOut[int(clause[1])*-1].append(clause[0])
    
    # return the Python dictionary representing the vertexes and edges of a dfs graph         
    return dictOut

#%%
class Vertex:
    def __init__(self, id=""):
        self.id = id 
        self.neighbours = {}
    
    def add_neighbour(self, nbr_vertex, weight=0):
        self.neighbours[nbr_vertex] = weight
        pass
    
    def __repr__(self):
        return repr(self.id)

    def get_neighbours(self):
        return list(self.neighbours.keys())

    def get_neighbours(self):
        return list(self.neighbours.keys())
    
    def get_weight(self, neighbour):
        return self.neighbours.get(neighbour, None)
    
    def __eq__(self, other):
        return self.id == other.id 
    
    def __lt__(self, other):
        return self.id < other.id 
    
    def __hash__(self):
        return hash(self.id) 

#%%
class Graph:
    def __init__(self):
        self.vertices = {} # Dictionary, key = String of Vertex id, value is the Vertex instance
        # to get the neighbours of a vertex in this graph: self.vertices[vid].neighbours 
         
    def _create_vertex(self, id):
        return Vertex(id)
    
    def add_vertex(self, id):
        v = self._create_vertex(id)
        self.vertices[v.id] = v 
        pass
    
    # return the instance of the requested id 
    def get_vertex(self, id):
        return self.vertices.get(id, None)
    
    def add_edge(self, start_v, end_v, weight=0):
        # check if start_v is in the graph's vertices dictionary
        if start_v not in self.vertices.keys():
            self.add_vertex(start_v)
        
        # obtain the instance of Vertex with id start_v
        start_vertex = self.vertices[start_v]

        # check if end_v is in the graph's vertices dictionary
        if end_v not in self.vertices.keys():
            self.add_vertex(end_v)
        
        # obtain the instance of Vertex with id end_v
        end_vertex = self.vertices[end_v]
        start_vertex.add_neighbour(end_vertex, weight)
    
    # @args: id is the String of vertex in question 
    # returns: ids of all neighbouring vertices 
    def get_neighbours(self, id):
        v = self.get_vertex(id)
        if v is not None: # if v exists in the graph, get all its neighbours 
            neighbours = v.get_neighbours() # utilising the get_neighbours method in Vertex class instance
            neighbours_id = []
            for neighbouring_vertex in neighbours:
                # neighbouring_vertex is a vertex instance, so extract its id
                neighbours_id.append(neighbouring_vertex.id)
            return neighbours_id
        return None                 
    
    # returns True or False if given val (String representing Vertex id) is in the Graph
    def __contains__(self, v_id):
        return v_id in self.vertices.keys()
    
    def __iter__(self):
        for k,v in self.vertices.items():
            yield v 
        
    # write a code to create a computed property called num_vertices
    @property
    def num_vertices(self):
        return len(self.vertices)

# %%
#function used to find SCCs
def DFS(implication_graph, visited, stack, scc): #add to the stack and scc lists passed in
    for node in implication_graph.vertices.values():
        if node not in visited:
            visit_node(implication_graph, visited, node, stack, scc)


# DFS helper function that visits all the reachable nodes, traverses a DFS tree
def visit_node(implication_graph, visited, node, stack, scc):
    if node not in visited:
        visited.append(node)
        for neighbour in node.get_neighbours(): #retrieve the neighbours of the node
            visit_node(implication_graph, visited, neighbour, stack, scc) #recursively go down the trail.
        stack.append(node)
        scc.append(node)
    return visited

#reverse the directions of all the edges  
def reverse_graph(implication_graph): 
    t_graph = Graph()
    # for each node in graph
    for node in implication_graph.vertices.values():
        # for each neighbour node of a single node
        for neighbour in node.get_neighbours():
            t_graph.add_edge(neighbour, node)
    return t_graph

#find the SCCs by running DFS, to get the topological order, denoted by the reverse of stack.
def find_SCCs(implication_graph):
    stack = []
    sccs = [] #nested list of SCCs
    #get the topological order of the implication graph
    DFS(implication_graph, [], stack, [])
    #reverse the graph to get the SCCs denoted by the DFS trees
    t_g = reverse_graph(implication_graph)
    
    visited = []
    while len(stack) != 0:
        node = stack.pop() #get the lowest topological order node to search for a SCC
        if node not in visited:
            scc = []
            visit_node(t_g, visited, node, [], scc) #add all strongly connect nodes to the DFS-tree named SCC
            if len(scc) != 0:
                sccs.append(scc) #add the DFS tree to the list of DFS trees called SCCs
    return sccs, stack

def find_contradiction(sccs):
    print("SCCs")
    print(sccs)
    print()
    for scc in sccs:
        print("SCC")
        print(scc)
        print()
        for literal in scc: #scc --> group of nodes
            for other_literal in scc[scc.index(literal):]:
                if other_literal.id == -literal.id:
                    return True
    return False

def find_solution(sccs):
    #go down the SCCs in reverse topological order
    solution = []
    for scc in sccs:
        for literal in scc:
            if (abs(literal.id) not in solution) and (literal.id not in solution) and (-literal.id not in solution):
                solution.append(literal.id)
    return solution



def solver():
    print("Checking if the following 2-CNF is Satisfiable in linear time ")
    # input the file name or file path
    file = input("Input the file name or file path: " )
    cnf = loadCnfFile(file)
    dictfinal = listToCnf(cnf)
    graph = Graph()
    for key in dictfinal:
        for val in dictfinal[key]:
            graph.add_edge(key, val, weight=0)

    sccs = find_SCCs(graph)[0]

    if not find_contradiction(sccs):
        print("2-CNF Satisfiable")
        solution = find_solution(sccs)
        print(solution)
    else:
        print("2-CNF not Satisfiable")
        

solver()
#%%
import sys

class Vertex:
    def __init__(self, id=""):
        self.id = id 
        self.neighbours = {}
    
    def add_neighbour(self, nbr_vertex, weight=0):
        self.neighbours[nbr_vertex] = weight
    
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

    def __repr__(self):
        return repr("Vertex: " + str(self.id))

class Graph:
    def __init__(self):
        self.vertices = {}
         
    def _create_vertex(self, id):
        return Vertex(id)
    
    def add_vertex(self, id):
        vert = self._create_vertex(id)
        self.vertices[vert.id] = vert 

    def get_vertex(self, id):
        return self.vertices.get(id, None)
    
    def add_edge(self, start_v, end_v, weight=0):
        if start_v not in self.vertices.keys():
            self.add_vertex(start_v)
        start_vertex = self.vertices[start_v]

        if end_v not in self.vertices.keys():
            self.add_vertex(end_v)
        end_vertex = self.vertices[end_v]

        start_vertex.add_neighbour(end_vertex, weight)
    
    def get_neighbours(self, id):
        v = self.get_vertex(id)

        if v is not None:
            neighbours = v.get_neighbours()
            neighbours_id = []

            for neighbouring_vertex in neighbours:
                neighbours_id.append(neighbouring_vertex.id)
                
            return neighbours_id

        else:
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

# reads the cnf file, cleans it and returns a list containing nested sub lists
def loadCnfFile(fileName):
    cnf=[]
    cnfFile = open(fileName, 'r')
    for line in cnfFile:
        if line[0]!="c" and line[0]!="p":
            l = line.split(" 0 ")[0].strip().split(" ")

            m=[]
            for k in l:
                if k != "" and k != "0":
                    m.append(k)
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
            dictOut[int(clause[0])*-1].append(int(clause[1]))
        
        # if the key does not exist, create a new list to store the literals
        else:
            dictOut[int(clause[0])*-1] = []
            dictOut[int(clause[0])*-1].append(int(clause[1]))
        
        # repeat above for the 2nd literal
        if int(clause[1])*-1 in dictOut.keys():
            dictOut[int(clause[1])*-1].append(int(clause[0]))
        else:
            dictOut[int(clause[1])*-1] = []
            dictOut[int(clause[1])*-1].append(int(clause[0]))
    
    # return the Python dictionary representing the vertexes and edges of a dfs graph
    # print(dictOut)         
    return dictOut

# function used to find SCCs
def DFS(graph, visited, stack): #add to the stack lists passed in
    for vert in graph.vertices.values():
        if vert not in visited:
            visit_vert(graph, visited, vert, stack)

# DFS helper function that visits all the reachable vertices, traverses a DFS tree
def visit_vert(graph, visited, vert, stack):
    if vert not in visited:
        visited.append(vert)
        for neighbour in vert.get_neighbours(): #retrieve the neighbours of the vert
            if neighbour not in visited:
                visit_vert(graph, visited, neighbour, stack) #recursively go down the trail.
        stack.append(vert)

#reverse the directions of all the edges  
def reverse_graph(graph): 
    transpose_graph = Graph()
    # for each vert in graph
    for key, vert in graph.vertices.items():
        # for each neighbour vert of a single vert
        for neighbour in vert.get_neighbours():
            transpose_graph.add_edge(neighbour.id, vert.id)

    return transpose_graph

#find the SCCs by running DFS, to get the topological order, denoted by the reverse of stack.
def find_SCCs(implication_graph):
    stack = []
    sccs = [] #nested list of SCCs
    scc = []
    visited = []
    #get the topological order of the implication graph
    DFS(implication_graph, visited, stack)

    #reverse the graph to get the SCCs denoted by the DFS trees
    transpose_graph = reverse_graph(implication_graph)

    for vert in transpose_graph.vertices.values():
        print("Transpose graph - Neighbours of {}:".format(vert.id), vert.get_neighbours())

    visited = []
    while len(stack) != 0:
        vert = stack.pop() #get the lowest topological order vert to search for a SCC
        transpose_vert = transpose_graph.vertices.get(vert.id, None)

        if vert not in visited:
            scc = []
            visit_vert(transpose_graph, visited, transpose_vert, scc) #add all strongly connect vertices to the DFS-tree named SCC

            if len(scc) != 0:
                sccs.append(scc) #add the DFS tree to the list of DFS trees called SCCs

    return sccs, stack


def find_contradiction(sccs):
    for scc in sccs:
        for literal in scc: #scc --> group of vertices
            for other_literal in scc[scc.index(literal):]:
                if other_literal.id == -1*literal.id:
                    return True
    return False

def find_solution(sccs):
    #go down the SCCs in reverse topological order
    solution = []
    for i in range(0, len(sccs)-1):
        scc = sccs[i]
        for literal in scc:
            key = int(literal.id)
            if (key not in solution) and (-1*key not in solution):
                solution.append(key)
    
    absolute = lambda x: abs(x)
    solution.sort(key=absolute)
    print(solution)

    result = [-1]*len(solution)
    for val in solution:
        ind = abs(val) - 1
        if val > 0:
            result[ind] = "1"
        else:
            result[ind] = "0"
    
    return " ".join(result)

def solver():
    print("Checking if the following 2-CNF is Satisfiable in linear time.")

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
        print("SATISFIABLE")
        solution = find_solution(sccs)
        print(solution)
    else:
        print("UNSATISFIABLE")
        

solver()
# %%

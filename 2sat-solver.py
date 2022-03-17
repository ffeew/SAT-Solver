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
        self.vertices = {} # Dictionary, key = String of Vertex id, value is the Vertex instance
         
    def _create_vertex(self, id):
        return Vertex(id)
    
    def add_vertex(self, id):
        vert = self._create_vertex(id)
        self.vertices[vert.id] = vert # Make the id of the object instance as the key instead of the string!

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
        # add the end vertex to start vertex's list of neighbours
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
        else:
            return None                 
    
    # returns True or False if given val (String representing Vertex id) is in the Graph
    def __contains__(self, v_id):
        return v_id in self.vertices.keys()
    
    def __iter__(self):
        for k,v in self.vertices.items():
            yield v 

# reads the cnf file, cleans it and returns a list containing nested sub lists
# the sublists contains the literals
def loadCnfFile(fileName):
    cnf=[]
    cnfFile = open(fileName, 'r')
    for line in cnfFile:
        if line[0]!="c" and line[0]!="p":
            l = line.split(" 0")[0].strip().split(" ")
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
    return dictOut

# function used to find the topological order of the implication graph
# modify the stack and scc lists passed in
def DFS(implication_graph, visited, stack, scc):
    #visit every vertex in the graph
    for vert in implication_graph.vertices.values():
        if vert not in visited:
            visit_vert(implication_graph, visited, vert, stack, scc)

# DFS helper function that visits all the reachable vertices --> traverses a DFS tree
def visit_vert(implication_graph, visited, vert, stack, scc):
    if vert not in visited:
        visited.append(vert)
        for neighbour in vert.get_neighbours():
            if neighbour not in visited:
                visit_vert(implication_graph, visited, neighbour, stack, scc) #recursively go down the DFS tree.
        stack.append(vert)
        scc.append(vert)
    return visited

# reverse the directions of all the edges  
def reverse_graph(implication_graph): 
    transposed_graph = Graph()
    # for each vert in graph
    for key, vert in implication_graph.vertices.items():
        # for each neighbour vert of a single vert
        for neighbour in vert.get_neighbours():
            transposed_graph.add_edge(neighbour.id, vert.id)
    return transposed_graph

# find the list of all SCCs by running DFS, to get the topological order, denoted by the reverse of stack,
# then another DFS to obtain all SCCs
def find_SCCs(implication_graph):
    stack = [] # reverse topological order of the implication graph
    sccs = [] #nested list of SCCs

    #get the topological order of the implication graph, stored in stack. top of stack --> last vertex to finish
    DFS(implication_graph, [], stack, [])

    #reverse the graph to get the SCCs denoted by the DFS trees
    transposed_graph = reverse_graph(implication_graph)

    #DFS iteration 2
    # retrieve the vertex from top of the stack, index = n-1, to visit in the reverse graph, 
    # each visit will generate a DFS-tree that corresponds to a Strongly connected component
    visited = []
    while len(stack) != 0:
        #get the lowest topological order vert to search for a SCC
        vert_id = stack.pop().id # int object
        
        # check if the vertice has not been visited before to avoid adding the same nodes into different SCCs
        if transposed_graph.get_vertex(vert_id) not in visited:
            scc = []
            # add all strongly connect vertices to the DFS-tree named scc
            visit_vert(transposed_graph, visited, transposed_graph.get_vertex(vert_id), [], scc)
            # prevent an empty list from being appended into sccs
            if len(scc) != 0:
                sccs.append(scc) #add the DFS tree to the list of DFS trees called SCCs
    print("SCCs: ", sccs)
    return sccs, stack


def find_contradiction(sccs):
    for scc in sccs:
        for literal in scc: #scc --> group of vertices
            for other_literal in scc[scc.index(literal):]:
                if other_literal.id == -1*literal.id:
                    return True
    return False

def find_solution(sccs):
    
    # solution contains all the vertices in the implication graph that is assigned to True.
    solution = []
    
    # go down the list of all SCCs in reverse topological order
    for i in range(len(sccs)-1,0,-1):
        scc = sccs[i]
        for literal in scc:
            key = int(literal.id)
            if (key not in solution) and (-1*key not in solution):
                solution.append(key)
    
    # sorting the literals in solution in ascending order based on their absolute value
    absolute = lambda x: abs(x)
    solution.sort(key=absolute)
    print(solution)

    # convert the values in solution into "0" and "1", leftmost--> boolean value of literal 1, rightmost --> boolean value of literal n
    result = [-1]*len(solution)
    for val in solution:
        ind = abs(val) - 1
        if val > 0:
            result[ind] = "1"
        else:
            result[ind] = "0"
    
    return " ".join(result)

def solver():
    print("Checking if the following 2-SAT Problem is Satisfiable")

    # input the file name or file path
    file = input("Input the file name or file path: " )
    cnf = loadCnfFile(file)
    dictfinal = listToCnf(cnf)

    # generate the implication graph
    graph = Graph()
    for key in dictfinal:
        for val in dictfinal[key]:
            graph.add_edge(key, val, weight=0)
    
    # generate the list of all Strongly connected components
    sccs = find_SCCs(graph)[0]

    # check for the presecence of any SCCs that contains both a literal i and its complement -i.
    # if such a SCC exists, 2SAT is unsatisfiable due to the contradiction
    if not find_contradiction(sccs):
        print()
        print("****************************************************************************************************")
        print("SATISFIABLE")
        solution = find_solution(sccs)
        print(solution)
        print("****************************************************************************************************")
        print()
        return solution
    else:
        print()
        print("****************************************************************************************************")
        print("UNSATISFIABLE")
        print("****************************************************************************************************")
        print()
        return None

solver()
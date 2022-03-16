#%%
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
        # print("equal method is called")
        return self.id == other.id
    
    def __lt__(self, other):
        return self.id < other.id
    
    def __hash__(self):
        # print("hash method is called ", self.id)
        return hash(self.id)

    def __repr__(self):
        # print(self.id)
        # print("Vertex {vert.id} is connected to: ".format(vert=self) + ", ".join(str(x.id) for x in self.get_neighbours()))
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
        
    # write a code to create a computed property called num_vertices
    @property
    def num_vertices(self):
        return len(self.vertices)

# reads the cnf file, cleans it and returns a list containing nested sub lists
# the sublists contains the literals
def loadCnfFile(fileName):
    cnf=[]
    cnfFile = open(fileName, 'r')
    for line in cnfFile:
        if line[0]!="c" and line[0]!="p":
            l = line.split(" 0")[0].strip().split(" ")
            # print(l)
            m=[]
            for k in l:
                if k != "" and k != "0":
                    # print(k)
                    m.append(k)
                    # print(m)
            cnf.append(m)
    cnfFile.close()
    # print(cnf)
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
# C:\Users\issac\Desktop\SUTD\School Year\Year 2\Term 4\2D\50.004\2SAT\Test2.cnf
# function used to find SCCs
def DFS(implication_graph, visited, stack, scc): #add to the stack and scc lists passed in
    # print("Depth First Search is called \n")
    for vert in implication_graph.vertices.values():
        if vert not in visited:
            visit_vert(implication_graph, visited, vert, stack, scc)
    stack.reverse()

# DFS helper function that visits all the reachable vertices, traverses a DFS tree
def visit_vert(implication_graph, visited, vert, stack, scc):
    # print("{} is being visited.".format(vert.id))

    if vert not in visited:
        visited.append(vert)
        # print("Neighbours of {}:".format(vert.id),vert.get_neighbours())
        for neighbour in vert.get_neighbours(): #retrieve the neighbours of the vert
            if neighbour not in visited:
                visit_vert(implication_graph, visited, neighbour, stack, scc) #recursively go down the trail.
        stack.append(vert)
        # print("Stack of DFS:", stack)
        scc.append(vert)
    return visited

#reverse the directions of all the edges  
def reverse_graph(implication_graph): 
    transpose_graph = Graph()
    # for each vert in graph
    for key, vert in implication_graph.vertices.items():
        # for each neighbour vert of a single vert
        for neighbour in vert.get_neighbours():
            transpose_graph.add_edge(neighbour.id, vert.id)

    # print("Transpose graph vertices:", transpose_graph.vertices)

    # for vert in transpose_graph.vertices.values():
    #     print("Transpose graph - {}:".format(vert), vert.get_neighbours())
    return transpose_graph

#find the SCCs by running DFS, to get the topological order, denoted by the reverse of stack.
def find_SCCs(implication_graph):
    # print("Find SCCs is called \n")
    stack = []
    sccs = [] #nested list of SCCs
    scc = []
    visited = []
    #get the topological order of the implication graph
    DFS(implication_graph, visited, stack, scc)

    #reverse the graph to get the SCCs denoted by the DFS trees
    transpose_graph = reverse_graph(implication_graph)

    # print("Stack for reverse graph traversal:", stack)
    visited = []
    while len(stack) != 0:
        vert = stack.pop() #get the lowest topological order vert to search for a SCC
        # print("Nodes remaining:", stack)
        # print("Visited nodes:", visited)
        # print("Vertex popped from stack:", vert)
        if vert not in visited:
            scc = []
            visit_vert(transpose_graph, visited, vert, [], scc) #add all strongly connect vertices to the DFS-tree named SCC
            # print("Checking SCC from visiting:", scc)
            if len(scc) != 0:
                sccs.append(scc) #add the DFS tree to the list of DFS trees called SCCs

    # print("Check SCCs from find SCCs:", sccs)
    return sccs, stack


def find_contradiction(sccs):
    # print("Find Contradiction is called")
    # print("SCCs:", sccs, "\n")

    for scc in sccs:
        # print("SCC:",scc, "\n")

        for literal in scc: #scc --> group of vertices
            for other_literal in scc[scc.index(literal):]:
                if other_literal.id == -1*literal.id:
                    return True
    return False

def find_solution(sccs):
    # print("Find Solution is called")
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
    # print("Stage 1 \n")
    file = input("Input the file name or file path: " )
    # file = r"C:\Users\issac\Desktop\SUTD\School Year\Year 2\Term 4\2D\50.004\2SAT\Test2.cnf"
    cnf = loadCnfFile(file)

    # print("Stage 2 \n")
    dictfinal = listToCnf(cnf)

    # print("Stage 3 \n")
    graph = Graph()
    for key in dictfinal:
        for val in dictfinal[key]:
            graph.add_edge(key, val, weight=0)
    
    # print("Vertices in a graph:", graph.vertices)

    # print("Stage 4 \n")
    sccs = find_SCCs(graph)[0]

    # print("Stage 5 \n")
    if not find_contradiction(sccs):
        print("SATISFIABLE")
        solution = find_solution(sccs)
        print(solution)
    else:
        print("UNSATISFIABLE")
        

solver()
# %%

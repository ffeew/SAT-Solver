# SAT-Solver
Our Python code implementation of the 2SAT solver is inspired by Arunptl100’s 2SAT solver implementation. It uses Kosaraju’s algorithm to find the SCCs in the graph and check for any contradictions within each SCC. We took reference from his design, studied the theory behind it (credits to Algorithm Live!) and built our 2SAT solver with a CNF file parser + solution generator. We also optimized the performance of the algorithm by using dictionaries instead of lists to store the visited nodes for the DFS, improving the performance of the solver by a factor of 10.

## 2-SAT Solver Approach
Implicative Normal Form
We first transform the 2-SAT problem in the CNF file into its implicit normal form. This is done so by converting each clause into a pair of implications. This is done so by converting each clause into a pair of implications. Since each clause in a 2-SAT expression has 2 literals, there should be at least one literal in each clause that is assigned to a true value to ensure that each clause is true, so that the problem can be satisfied. This also implies that if one of the literals in a clause is false, the other literal must be true so that the expression is satisfiable.

One example would be the clause (A V B). If A is assigned a false value, B must be assigned to a true value for the clause to be true; If B is assigned a false value, A must be assigned to a true value. This can be extended to the set of implications presented in the table below.

<table>
  <tr>
    <th>Clause</th>
    <th>Implication</th>
  </tr>
  <tr>
    <td>(A V B)</td>
    <td>(A' -> B) and (B' -> A)</td>
  </tr>
  <tr>
    <td>(A' V B)</td>
    <td>(A -> B) and (B' -> A')</td>
  </tr>
    <tr>
    <td>(A V B')</td>
    <td>(A' -> B') and (B -> A)</td>
  </tr>
  </tr>
    <tr>
    <td>(A' V B')</td>
    <td>(A -> B') and (B -> A')</td>
  </tr>
</table>

## Implication Graph
We can then use these implications to construct an implication graph. This is a directed graph displaying all the relationships between the literals and their negation. The vertices represent the literals and their negation, while the directed edges represent the implications between the 2 literals.

Using the example of clause (A V B) again, this clause can be presented as (A  B)  (B  A), meaning that there would be a directed edge from A to B and another from B to A in its implication graph. This can be extended to the rest of the clauses in the 2-SAT formula.

## Strongly Connected Component (SCC)
A SSC in a directed graph is a set of nodes in which there exists a path connecting every node in the set to every other node in the set . SSCs can be used as a quick way of identifying whether a boolean expression is solvable: if both a literal and its negated value are found to be in a SCC, this means that there will always be a contradiction regardless of the value the literal is assigned. A contradiction occurs when: (B  B AND  B  B) =  B ⋀ B is present in the graph. If a contradiction is present, no matter what the value of B is assigned, B ⋀ B is always False. Thus the 2-SAT problem is unsatisfiable.

## 2SAT Solver Implementation

We implemented Kosaraju's algorithm to find all the SCCs of a given graph using a stack and 2 Depth First Searches (DFS). The first DFS traverses the original implication graph and pushes the nodes into a stack when all its children have been visited. This produces a topological order for the nodes in the implication graph that is stored in the stack (the node at the top of the stack has the highest finishing time). 

Next, we transpose our original implication graph into its reverse graph and traverse it during the second DFS. In the second DFS, the nodes at the top of the stack are popped, serving as the starting nodes for the DFS. DFS trees will be produced by the second DFS and each DFS tree is a SCC.

The SCCs will then be appended into a list of SCCs such that the last SCC in the list has the lowest topological order (highest finishing time).

Subsequently, for each SCC, we will check if a contradiction is present i.e. the SCC contains a node i and i, ∀ i ∈{all literals in the problem}. If no contradiction is present, the problem is satisfiable, else, it is unsatisfiable.

Lastly, to generate a possible solution to a satisfiable 2 SAT problem, the nodes of each SCC are added into a list of solutions, starting from the SCC with the lowest topological order (last in the list of SCCs). If the list of solutions already contains the node or its negated value, then do not add it. This produces a list of solutions where each literal is represented by either node i or i, ∀ i ∈{all literals in the problem}. To obtain the boolean value for each literal, we sort the list of solutions in ascending order and convert it into a string of 1s and 0s, where i = 1 and i = 0.

## Time Complexity of the 2SAT Solver
visit_vert: For visit_vert, the time complexity of the function is O(V+E), where V is the total number of vertices in the graph and E is the total number of edges in the graph. The worst case would be that the algorithm can visit all nodes in the graph from the starting node.

DFS: For DFS, the time complexity of the function is O(V+E), where V is the total number of vertices in the graph and E is the total number of edges in the graph.

reverse_graph: For reverse_graph, the time complexity of the function is O(V+E), where V is the total number of vertices in the graph and E is the total number of edges in the graph.

find_SCCs: For find_SCCs, the running time consists of creating a dictionary for visited (O(V)), performing a DFS traversal on the implication graph (O(V+E)), creating a reverse graph (O(V+E)), resetting the values in the visited dictionary to False (O(V)) and performing a DFS traversal on the reverse_graph (O(V+E)). Hence, the time complexity can be determined via the following equation: max(O(V), O(V+E), O(V+E), O(V), O(V+E)) = O(V+E).

find_contradiction: For find_contradiction, the time complexity of the function is O(V2), where V is the total number of vertices in the graph. This is because the graph would have traversed all nodes and compared its key value to all other nodes in the scc.

find_solution: For find_solution, the time complexity is O(V2), where V is the total number of vertices in the graph. This is because the 2 for loops visits all of the vertices. Hence, the time complexity is O(V). Within the nested for loops, the function checks whether the literal is in the solution (O(V)).

solver: max(O(V+E), O(V+E), O(V2), O(V2)) = O(V2)
The solver is the driver code for the 2SAT solver and it takes into account the maximum time complexity of all functions used within it. The solver first creates an implication graph from the dictionary obtained after parsing the CNF file and converting it into the implicative normal form. The time complexity for that operation is O(V+E). Next, it calls find_SCCs and the time complexity of that is O(V+E). Subsequently, find_contradiction is called to check if the 2SAT is satisfiable and the time complexity of that is O(V2). If the 2SAT is satisfiable, then find_solution will be called and that has a time complexity of O(V2). Since the time complexity of the solver is the max time complexity of the functions within it, the time complexity of the solver is O(V2).

Therefore, our 2-SAT solver is able to solve a 2-SAT problem in polynomial time, excluding the parsing step’s time complexity.

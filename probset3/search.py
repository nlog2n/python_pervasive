class SearchProblem:
    """a classic search problem, as described in AIAMA (Russell, Norvig).  This
    is an abstract class and should not be instantiated.
    """
    def __init__(self):
        self.initial_state = None
        raise NotImplementedError()

    def successors(self, state):
        """returns a list of action, result_state pairs reachable from the
        specified state"""
        raise NotImplementedError()
    
    def is_goal(self, state):
        """returns True if state is the goal state.  False otherwise"""
        raise NotImplementedError()

    def step_cost(self, from_state, action, to_state):
        """returns the cost of taking the specified action that leads to 
        to_state from from_state.  duh.
        """
        raise NotImplementedError()

    def estimated_cost_from( self, state ):
        """returns an admissible, consistent guess of the cost to reach the
        goal state from the specified state.  Admissible means the guess never
        underestimates the actual cost.  Consistent means something else.
        """
        raise NotImplementedError()


class __SearchNode:
    def __init__(self, state, \
            parent = None, \
            action = None, \
            path_cost = 0):
        self.state = state        # the current state
        self.parent = parent      # the previous state
        self.action = action      # the action that resulted in this state
        self.path_cost = path_cost
        if parent is None:
            self.depth = 0
        else:
            self.depth = parent.depth + 1
    def solution(self):
        path = []
        n = self
        while True:
            path.insert(0, ( n.state, n.action ) )
            n = n.parent
            if n is None: return path

def __search_expand(problem, node):
    successors = []
    for action, result in problem.successors( node.state ):
        step_cost = problem.step_cost( node.state, action, result )
        successors.append(__SearchNode( result, node, action, \
                                     node.path_cost + step_cost ))
    return successors
#    return [ __SearchNode( result, node, action, node.path_cost + \
#                problem.step_cost( node.state, action, result ) ) \
#                for action, result in problem.successors( node.state ) ]

def tree_breadth_first_search(problem):
    fringe = [ __SearchNode(problem.initial_state) ]
    while len(fringe) > 0:
        node = fringe.pop(0)
        if problem.is_goal( node.state ):
            return node.solution()
        fringe.extend( __search_expand( problem, node ) )
    return None

def tree_depth_first_search(problem):
    fringe = [ __SearchNode(problem.initial_state) ]
    while len(fringe) > 0:
        node = fringe[-1]
        del fringe[-1]
        if problem.is_goal( node.state ):
            return node.solution()
        fringe.extend( __search_expand( problem, node ) )
    return None

def graph_breadth_first_search(problem):
    fringe = [ __SearchNode(problem.initial_state) ]
    closed = []
    while len(fringe) > 0:
        node = fringe.pop(0)
        if problem.is_goal( node.state ):
            return node.solution()
        if node.state not in closed:
            closed.append(node.state)
            fringe.extend( __search_expand( problem, node ) )
    return None

def graph_depth_first_search(problem):
    fringe = [ __SearchNode(problem.initial_state) ]
    closed = []
    while len(fringe) > 0:
        node = fringe[-1]
        del fringe[-1]
        if problem.is_goal( node.state ):
            return node.solution()
        if node.state not in closed:
            closed.append(node.state)
            fringe.extend( __search_expand( problem, node ) )
    return None

def astar_search(problem):
    fringe = [ __SearchNode(problem.initial_state) ]
    closed = []
    while len(fringe) > 0:
        # pick a node to expand
        best_node = None
        best_estimate = 0

        for n in fringe:
            if problem.is_goal( n.state ):
                return n.solution()
            estimate = n.path_cost + problem.estimated_cost_from( n.state )
            if best_node is None or estimate < best_estimate:
                best_node = n
                best_estimate = estimate
                
#        print "%s %s" % (best_node.state.x, best_node.state.y)
        fringe.remove( best_node )
        closed.append( best_node.state )

        new_nodes = __search_expand( problem, best_node )
        existing_fringe_states = [ n.state for n in fringe ]

        for n in new_nodes:
            if n.state not in closed and n.state not in existing_fringe_states:
                fringe.append( n )
    return None

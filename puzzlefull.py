#!/usr/bin/env python

## @title  CSCE-625 Programming Assignment 2 : Eight Puzzle
## @author Karthik Venugopal (k4rthikv@gmail.com)
## @date   09-19-2013

# Implementation of a solution to the eight-puzzle problem,
# using each of DFS, BFS, DLS, IDS, Greedy Best-First, A-*,
# ID-A*

import sys;
import re;
import math;
import time;
import collections;


def GOAL_STATE(): return [1,2,3,4,5,6,7,8,0]                                        # The constant goal state 

usedStates={};                                                                      # List of states already visited by algorithm. [State => (parent, direction from parent, depth encountered)]
knownHeuristics={};                                                                 # List of heuristics computed for various states. [State => heuristic]

spaceComplexity = 0;                                                                # Parameter used to judge space and time complexity.
timeComplexity = 0;                                                                 # Actual semantic will depend on the algorithm


# Representing enums
def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named);
    reverse = dict((value, key) for key, value in enums.iteritems());
    enums['reverse_mapping'] = reverse;
    return type('Enum', (), enums);


# Representing setting for various program runtime parameters
DIRECTIONS   = enum(UP=-3, DOWN=3, RIGHT=1, LEFT=-1);                               # Direction flipped from one state to next
QUEUEING     = enum(STACK=1, QUEUE=2);                                              # Different queueing between BFS and DFS
UI_ALGORITHM = enum(DFS=1, BFS=2, DLS=3, IDS=4);                                    # List of uninformed search algorithms
IN_ALGORITHM = enum(GBF=5, AST=6, IDA=7);                                           # List of informed search algorithms
HEURISTICS   = enum(BOOLEAN=1, MANHATTAN=2);                                        # Two heuristic used in informed search


# Check inversion number for input state
def getInversionNumber(nodeState):
    return len([(x,y) for x in range(len(nodeState)-1) for y in range(x+1,9)
        if nodeState[x]>nodeState[y] and (not (nodeState[x]==0 or nodeState[y]==0))]);



# Parse input arguments to get algo and initial state
def parseInputArgs():
    statePattern = re.compile('^([^ ]+) \((([0-8] ){8}[0-8])\)( [h0-9]+){0,1}$'); 

    patternMatch = statePattern.match(' '.join(sys.argv[1:]));
    if patternMatch is None:
        print "Invalid state pattern";
        exit(1);

    algoName = patternMatch.group(1).upper();                                       # Set algorithm to a defined enum
    if algoName=='DFS':
        algoName=UI_ALGORITHM.DFS;
    elif algoName=='BFS':
        algoName = UI_ALGORITHM.BFS;
    elif algoName=='DLS':
        algoName = UI_ALGORITHM.DLS;
    elif algoName=='IDS':
        algoName = UI_ALGORITHM.IDS;
    elif algoName=='GREEDY':
        algoName = IN_ALGORITHM.GBF;
    elif algoName=='A-STAR':
        algoName = IN_ALGORITHM.AST;
    elif algoName=='IDA-STAR':
        algoName = IN_ALGORITHM.IDA;
    else:
        print "Unrecognized algorithm: "+algoName;
        exit(1);

    initialState = patternMatch.group(2);                                           # Read initial state string from input args
    initialState = [int(x) for x in initialState if x.isdigit()];                   # Initialize initial state to list

    if not (getInversionNumber(initialState)%2 == getInversionNumber(GOAL_STATE())%2): # Compare inversion numbers for goal and initial state
        print "No path exists from initial state "+str(initialState)+" to goal state "+str(GOAL_STATE());
        exit(1);

    if algoName<5:                                                                  # If uninformed search, 3rd parameter is max search depth
        if patternMatch.group(4) is None:                                           # Read max search depth parameter from input (optional)
            maxSearchDepth = 0;
        else:
            maxSearchDepth = int(patternMatch.group(4));
        return [algoName, initialState, maxSearchDepth];

    else:                                                                           # If informed search, 3rd parameter is heuristic (required) 
        if patternMatch.group(4) is None:
            print "Heuristic required for informed search. \'h1\' (for tiles out of place) or \'h2\' for Manhattan distance";
            exit(1);
        else:
            heuristicName = patternMatch.group(4).strip().upper();
            print "Heuristic: "+heuristicName;
            if heuristicName == 'H1':
                heuristicName = HEURISTICS.BOOLEAN;
            elif heuristicName == 'H2':
                heuristicName = HEURISTICS.MANHATTAN;
            else:
                print "Unrecognized value for heuristic. Should be \'h1\' (for tiles out of place) or \'h2\' for Manhattan distance"
                exit(1);

            return [algoName, initialState, heuristicName];



# Calculate heuristic value for a given state as number of tiles out of place
def getBooleanDistance(nodeState):
    heuristicValue = 0;
    for i in range(len(nodeState)):
        if nodeState[i]==0:                                                           # Discount the blank tile
            continue;
        if GOAL_STATE()[i] != nodeState[i]:                                           # Compare value at index between nodeState and goalState
            heuristicValue+=1;

    return heuristicValue;



# Calculate heuristic value for a given state as Manhattan distance of the tiles
def getManhattanDistance(nodeState):
    heuristicValue = 0;
    for i in range(1,len(nodeState)):
        intendedIndex = GOAL_STATE().index(i);
        actualIndex   = nodeState.index(i);
        
	xMovement = math.fabs(actualIndex-intendedIndex)%3;
        yMovement = int(math.fabs(actualIndex-intendedIndex)/3);
        
	heuristicValue += (xMovement+yMovement);
    
    return int(heuristicValue);



# Calculate actual node cost as (heuristic + node depth)
# Heuristic function could be boolean or Manhattan distance
def getTotalCost(nodeState, heuristicFunction):
     return heuristicFunction(nodeState)+usedStates[str(nodeState)][2];



# Get valid child states from  a given state. Does not include states in `usedStates`
def getChildStates(currentState):
    global usedStates;

    zeroIndex = currentState.index(0);
    
    xIndex = zeroIndex%3;                                                           # x-Index of '0' in the 3x3 box
    yIndex = zeroIndex/3;                                                           # y-Index of '0' in the 3x3 box

    validDirections = [x for x in [1, -1] if ((xIndex%3)+x) in [0,1,2]];            # Get directions movable in X-direction
    validDirections.extend([y*3 for y in [-1, 1] if ((yIndex%3)+y) in [0,1,2]]);    # Get directions movable in Y-direction

    childStates = collections.deque();                                              # Deques used to optimize front-side inserts

    for validDirection in validDirections:                                          # Move '0' in the corresponding direction and check for loop
        tempState = currentState[:];
        (tempState[zeroIndex],tempState[zeroIndex+validDirection]) = (tempState[zeroIndex+validDirection],tempState[zeroIndex]);


        if str(tempState) not in usedStates:                                        # Child state is valid only if first encounter
            childStates.append(tempState);
            currentDepth = usedStates[str(currentState)][2];                        # Depth of the parent node
            usedStates[str(tempState)]=(currentState,validDirection, currentDepth+1);
        

    return childStates;



def addChildrenToList(nodeList, childStates, queueingMethod):
    if queueingMethod==QUEUEING.STACK:                                              # Queueing for DFS
        nodeList.extendleft(childStates);
    elif queueingMethod==QUEUEING.QUEUE:                                            # Queueing for BFS
        nodeList.extend(childStates);                                               # Prepend child states to queue. If childStates is empty, the sibling of current node will be taken next

    return nodeList;



# Actual implementation of an uninformed search. Based on parameters passed for queueing mechanism and search depth,
# runs BFS, DFS or a variant
def runUninformedSearch(initialState, queueingMethod, maxSearchDepth=0):
    global usedStates;                                                              # Reset usedStates to default before starting search.
    usedStates={};
    usedStates[str(initialState)] = (None, None, 1);

    global timeComplexity;
    global spaceComplexity;

    nodeList = collections.deque();                                                 # Stores list of colored nodes not yet expanded
    nodeList.append(initialState);

    allNodesVisited=True;

    while(len(nodeList)>0):
        currentState = nodeList.popleft();                                          # Remove element to extend all its children
        currentDepth = usedStates[str(currentState)][2];

        timeComplexity=timeComplexity+1;

        if currentState==GOAL_STATE():                                              # If current node is goal, end search
            return currentState;
       
        if maxSearchDepth<=0 or currentDepth<maxSearchDepth:                        # Expand to children only if depth limit hasn't been reached
            childStates = getChildStates(currentState);                             # Retrieve child states for node
            nodeList = addChildrenToList(nodeList, childStates, queueingMethod);    # Add children to list according to algorithm 
        else:
            allNodesVisited=False;
            
        if len(nodeList)>spaceComplexity:
            spaceComplexity = len(nodeList);

    return allNodesVisited;



# Based on algorithm and max depth, define parameters to run uninformed search
def setupUninformedSearch(algoName, initialState, maxSearchDepth=0):
    global timeComplexity;
    timeComplexity=0;

    global spaceComplexity;
    spaceComplexity = 1;

    if algoName==UI_ALGORITHM.DFS or algoName==UI_ALGORITHM.DLS:                    # Run DFS algorithm for DFS and DLS (maxSearchDepth will determine which one)
        return runUninformedSearch(initialState, QUEUEING.STACK, maxSearchDepth);

    elif algoName==UI_ALGORITHM.BFS:                                                # Run BFS algorithm
        return runUninformedSearch(initialState, QUEUEING.QUEUE, maxSearchDepth);

    elif algoName==UI_ALGORITHM.IDS:                                                # Run IDS algorithm
        currentDepthLimit=0;                                                        # Current depth IDS is limited to
        searchResult = None;                                                        # Decides if the DLS can run any deeper

        while searchResult is not True and type(searchResult) is not list:
            
            currentDepthLimit=currentDepthLimit+1;                                  # Run DLS while incrementing max depth each time
            searchResult = runUninformedSearch(initialState, QUEUEING.STACK, currentDepthLimit);

        return searchResult;



# Actual implementation of an informed search. Based on cost function, 
# runs Greedy Best-First or A-*
def runInformedSearch(initialState, costFunction):
    global timeComplexity;
    timeComplexity=0;

    global spaceComplexity;
    spaceComplexity = 1;

    nodeList = list();
    nodeList.append(initialState);

    global knownHeuristics;
    knownHeuristics[str(initialState)] = costFunction(initialState);

    while(len(nodeList)>0):
        currentState = nodeList.pop(0);
        timeComplexity +=1;

        if currentState == GOAL_STATE():
            return currentState;

        childStates = getChildStates(currentState);
        for childState in childStates:

            childHeuristic = knownHeuristics[str(childState)] = costFunction(childState);
            
            insertPosition=0;
            for nodeState in nodeList:
                if knownHeuristics[str(nodeState)] > childHeuristic:
                    break;
                else:
                    insertPosition+=1;

            nodeList.insert(insertPosition, childState);

        if spaceComplexity < len(nodeList):
            spaceComplexity = len(nodeList);



# DFS Contour for IDA-*
def DFSContour(currentNode, fLimit, costFunction, recursionDepth=0):

    global spaceComplexity;
    if spaceComplexity < recursionDepth:
        spaceComplexity = recursionDepth;

    global timeComplexity;

    if str(currentNode) in knownHeuristics:
        pathCost = knownHeuristics[str(currentNode)];
    else:
        pathCost = costFunction(currentNode);
        knownHeuristics[str(currentNode)] = pathCost;
        
    if pathCost>fLimit:
        return (None, pathCost);

    if currentNode == GOAL_STATE():
        return (currentNode, fLimit);

    minF = sys.maxint;

    childStates = getChildStates(currentNode);
    for childState in childStates:
        timeComplexity = timeComplexity+1;
        (searchResult, childF) = DFSContour(childState, fLimit, costFunction, recursionDepth+1);

        if searchResult is not None:
            return (searchResult, fLimit);
        else:
            minF = min(minF, childF);

    return (None, minF);
        


# Implementation of ID-A*
def runIDAStar(initialState, costFunction):
    fLimit = costFunction(initialState);

    global knownHeuristics;
    global usedStates;

    global timeComplexity;
    timeComplexity  = 1;

    while(True):
        knownHeuristics = {};
        knownHeuristics[str(initialState)] = fLimit;
        
        usedStates = {};
        usedStates[str(initialState)] = (None, None, 1); 

        (searchResult, fLimit) = DFSContour(initialState, fLimit, costFunction);
        if searchResult is not None:
            return searchResult;
        if fLimit==sys.maxint:
            return None;



# Based on algorithm and heuristic, define parameters to run informed search
def setupInformedSearch(algoName, initialState, heuristicName):
    if heuristicName == HEURISTICS.BOOLEAN:
        heuristicFunction = getBooleanDistance;
    elif heuristicName == HEURISTICS.MANHATTAN:
        heuristicFunction = getManhattanDistance;

    if algoName==IN_ALGORITHM.GBF:
        return runInformedSearch(initialState, lambda nodeState:heuristicFunction(nodeState));
    elif algoName==IN_ALGORITHM.AST:
        return runInformedSearch(initialState, lambda nodeState:getTotalCost(nodeState, heuristicFunction));
    elif algoName==IN_ALGORITHM.IDA:
        return runIDAStar(initialState, lambda nodeState:getTotalCost(nodeState, heuristicFunction));



# Follow direction that algorithm took from root node to goal
def followRootToGoal(currentNode):
    movementList = collections.deque();
    while(currentNode is not None):
        nextDirection = usedStates[str(currentNode)][1];
        
        if nextDirection is not None:
            movementList.appendleft(DIRECTIONS.reverse_mapping[nextDirection]);

        currentNode = usedStates[str(currentNode)][0];
    return movementList;



# Program main routine. Expects initial state as argument
if __name__=="__main__":
    searchParams = parseInputArgs();                                                # Check if input is a valid initial state and return run parameters

    print str(searchParams);
    # Recursion in DFS Contour can exceed default recursion limit
    sys.setrecursionlimit(10000);

    initialState = searchParams[1];
    usedStates[str(initialState)] = (None, None, 1);                                # Root node 
    
    startTime = time.time();
    
    if searchParams[0] < 5:                                                         # Algorithm is uninformed
        goalNode = setupUninformedSearch(searchParams[0], initialState, searchParams[2]); # Run uninformed search algorithm 
    else:                                                                           # Algorithm is informed
        goalNode = setupInformedSearch(searchParams[0], initialState, searchParams[2]);   # Run informed search algorithm

    elapsedTime = time.time() - startTime;

    if type(goalNode) is not list:
        print "Goal not found. Nodes visited: "+str(timeComplexity);
        exit(0);
    
    startToGoal = followRootToGoal(goalNode);                                       # Follow nodes from root to goal (in opposite order)

    print "\nSolution:\n----------";
    if len(startToGoal)<=50:
        print list(startToGoal),'\n';
    
    print "Solution takes "+str(len(startToGoal))+" movements to get to the goal";

    if searchParams[0] != IN_ALGORITHM.IDA:
        # Logging program time and search depth
        print "\nNodes visited: ",str(timeComplexity);
        print "Maximum length of node list: ",str(spaceComplexity);
        print "Search run-time: ",str(elapsedTime),"seconds\n";
    else:
        print "\nNodes visited: ",str(timeComplexity);
        print "Maximum recursion depth: ",str(spaceComplexity);
        print "Search run-time: ",str(elapsedTime),"seconds\n";
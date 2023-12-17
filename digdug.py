from tree_search import *

class DigDug(SearchDomain):
    def __init__(self, offlimits, map, size):
        self.offlimits = offlimits # List of [x, y] pairs --> defines where DigDug can't go
        self.map = map
        self.size = size # [x, y] pair --> x is width, y is height
    
    def can_go(self, x, y):            
        for offlimit in self.offlimits: # can't go to offlimit squares
            if offlimit[0] == x and offlimit[1] == y:
                return False
            
        # also has to be inside the map
        if self.size[0] < x or x < 0:
            return False
        if self.size[1] < y or y < 0:
            return False
        
        return True

    def actions(self, state):
        actlist = []
        x, y = state
        if self.can_go(x, y-1):
            actlist.append("w")
        if self.can_go(x-1, y):
            actlist.append("a")
        if self.can_go(x, y+1):
            actlist.append("s")
        if self.can_go(x+1, y):
            actlist.append("d")
        return actlist
    
    def result(self, state, action):
        newstate = state.copy()
        x, y = state
        if action == "w":
            newstate = [x, y-1]
        elif action == "a":
            newstate = [x-1, y]
        elif action == "s":
            newstate = [x, y+1]
        elif action == "d":
            newstate = [x+1, y]
        return newstate
    
    def cost(self, state, action): # the cost of moving to a square is always 1
        return 1
    
    def heuristic(self, state, goal):
        return abs(state[0] - goal[0]) + abs(state[1] - goal[1])
    
    def satisfies(self, state, goal):
        return state == goal
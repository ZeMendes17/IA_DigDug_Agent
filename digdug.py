from tree_search import *

class DigDug(SearchDomain):
    def __init__(self, offlimits, map, size):
        self.offlimits = offlimits
        self.map = map
        self.size = size
    
    def can_go(self, x, y):            
        for offlimit in self.offlimits:
            if offlimit[0] == x and offlimit[1] == y:
                return False
            
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
    
    def cost(self, state, action):
        return 1
    
    def heuristic(self, state, goal):
        return abs(state[0] - goal[0]) + abs(state[1] - goal[1])
    
    def satisfies(self, state, goal):
        return state == goal
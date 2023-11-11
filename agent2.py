from digdug import *

class Agent():
    def __init__(self):
        self.state = None
        self.action = " "
        self.map = None
        self.size = None
        self.my_position = None
        self.closest_enemy = None
        self.my_tunnel = []
        self.offlimits = set()
        self.trace_back = []
        self.path = []
        self.wait = False

    def update_state(self, state):
        if 'map' in state:
            self.map = state['map']
            self.size  = state['size']

        if 'digdug' in state and state['enemies'] != []:
            self.state = state
            self.my_position = state['digdug']
            # update the map with the new position
            self.map[self.my_position[0]][self.my_position[1]] = 0
            self.my_tunnel = self.get_tunnel(self.my_position[0], self.my_position[1], self.map, [])

            # get enemies in my tunnel
            in_my_tunnel = [enemy for enemy in state['enemies'] if enemy['pos'] in self.my_tunnel]
            if in_my_tunnel != []:
                # get the closest enemy
                self.closest_enemy = in_my_tunnel[0]
                for enemy in in_my_tunnel:
                    if self.distance(self.my_position, enemy['pos']) < self.distance(self.my_position, self.closest_enemy['pos']):
                        self.closest_enemy = enemy

                if self.distance(self.my_position, self.closest_enemy['pos']) < 3:
                        self.key = "A"
                        return self.key

                st = self.get_tree_search(self.closest_enemy['pos'], self.my_tunnel)
                next_position = st.search()[1]
                
                return self.go_to(next_position)
            
            if self.is_pooka_traversing(state):
                if self.trace_back == []:
                    st = self.get_tree_search(self.closest_enemy['pos'], self.my_tunnel).search()[1:]
                    next_position = st[0]
                    self.trace_back = st[1:]

                    return self.go_to(next_position)

                else:
                    next_position = self.trace_back[0]
                    self.trace_back = self.trace_back[1:]

                return self.go_to(next_position)
            
            self.trace_back = []
            # agora ver o inimigo mais próximo, pegar no tunel dele e meter todos os outros
            # em offlimits
            # nao esquecer que se um pooka der traverse temos de limpar os offlimits
            # melhor maneira de entrar no tunel
            if self.path == []:
                if self.wait:
                    enemy = None
                    
                    for e in state['enemies']:
                        if e['id'] == self.closest_enemy['id']:
                            enemy = e
                            break
                    
                    orientation = self.go_to(enemy['pos'])   

                    if orientation == self.dir_to_key(enemy['dir']):
                        self.key = orientation
                        self.wait = False
                        return self.key       
                    else:
                        self.key = " "
                        return self.key
                else:
                    self.offlimits = []

                    if self.closest_enemy not in state['enemies']:
                        self.closest_enemy = None

                    for enemy in state['enemies']:
                        if enemy['name'] == 'Pooka':
                            if self.closest_enemy == None or self.distance(self.my_position, enemy['pos']) < self.distance(self.my_position, self.closest_enemy['pos']):
                                self.closest_enemy = enemy

                        elif enemy['name'] == 'Fygar':
                            enemy_names = [e['name'] for e in state['enemies']]
                            if 'Pooka' not in enemy_names:
                                if self.closest_enemy == None or self.distance(self.my_position, enemy['pos']) < self.distance(self.my_position, self.closest_enemy['pos']):
                                    self.closest_enemy = enemy

                    self.offlimits  = self.get_offlimits(state['rocks'], self.state['enemies'])

                    start, end = self.get_entries(self.closest_enemy)

                    # check if they both exist
                    if start != None and end != None:
                        # check which one is the closest
                        closest = start if self.distance(self.my_position, start) < self.distance(self.my_position, end) else end

                    elif start == None and end != None:
                        closest = end
                    elif start != None and end == None:
                        closest = start
                    else:
                        print("Error: no start or end")

                    st = self.get_tree_search(closest, self.map)
                    self.path = st.search()[1:]

            else:
                if len(self.path) == 1:
                    self.wait = True

                next_position = self.path[0]
                self.path = self.path[1:]

                return self.go_to(next_position)
            
        else:
            # reset variables
            self.my_tunnel = []
            self.offlimits = set()
            self.trace_back = []
            self.path = []
            self.wait = False
            self.key = " "

        return self.key


    # function to get the tunel for a give position
    def get_tunnel(self, i, j, map, visited):
        width = len(map)
        height = len(map[0])
        # if the current cell is not 0 or already visited, return
        if i < 0 or j < 0 or i >= width or j >= height or map[i][j] != 0 or [i, j] in visited:
            return

        # mark the current cell as visited
        visited.append([i, j])

        # get the adjacent cells
        adjacent_cells = [(i-1, j), (i+1, j), (i, j-1), (i, j+1)]

        # iterate over the adjacent cells
        for cell in adjacent_cells:
            # if the cell is within the map boundaries
            if cell[0] >= 0 and cell[0] < len(map) and cell[1] >= 0 and cell[1] < len(map[0]):
                # if the cell is 0 and not visited, recursively call the function
                if map[cell[0]][cell[1]] == 0 and [cell[0], cell[1]] not in visited:
                    self.get_tunnel(cell[0], cell[1], map, visited)

        return visited


    # fuction to the the tree search for a given goal
    def get_tree_search(self, goal, map):
        domain = DigDug(self.offlimits, map, self.size)
        problem = SearchProblem(domain, self.my_position, goal)
        return SearchTree(problem, 'greedy')
    
    # funtion to calculate the distance between two points
    def distance(self, a, b):
        return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** (1 / 2)
    
    # function to know if a pooka is traverssing
    def is_pooka_traversing(self, state):
        enemies = state["enemies"]
        for enemy in enemies:
            if enemy["name"] == "Pooka":
                if 'traverse' in enemy:
                    return True
        return False
    
    # funtion to go to a given position
    def go_to(self, position):
        if self.my_position[0] < position[0]:
            self.key = "d"
        elif self.my_position[0] > position[0]:
            self.key = "a"
        elif self.my_position[1] < position[1]:
            self.key = "s"
        elif self.my_position[1] > position[1]:
            self.key = "w"
        else:
            self.key = " "
        return self.key
    
    def dir_to_key(self, direction):
        if direction == 0:
            return "w"
        elif direction == 2:
            return "s"
        elif direction == 3:
            return "a"
        elif direction == 1:
            return "d"
        else:
            return None
        
    # function that gets map when it is received and gets important information from it
    def get_offlimits(self, rocks, enemies):
        offlimits = []
        # rocks and the square directly below
        for rock in rocks: # for now
            offlimits.append(rock["pos"])
            offlimits.append([rock["pos"][0], rock["pos"][1] + 1])

        # it is better not to perfurate other enemies tunnels
        offlimits = offlimits + self.tunnel_offlimits(enemies)

        # remove duplicates
        new_offlimits = []
        for offlimit in offlimits:
            if offlimit not in new_offlimits:
                new_offlimits.append(offlimit)

        return new_offlimits
    
    # function to get the entries of the closest enemy tunnel
    def get_entries(self, enemy):
        x = enemy["pos"][0]
        y = enemy["pos"][1]
        start = enemy["pos"]
        end = enemy["pos"]

        try:
            if self.map[x][y+1] == 0 or self.map[x][y-1] == 0: # vertical
                column = self.map[x]
                for i in range(y, len(column)):
                    if column[i] == 0:
                        end = [x, i]
                    else:
                        break
                for i in range(y, -1, -1):
                    if column[i] == 0:
                        start = [x, i]
                    else:
                        break

                start = [start[0], start[1] - 2] 
                end = [end[0], end[1] + 2]

            elif self.map[x+1][y] == 0 or self.map[x-1][y] == 0: # horizontal
                for i in range(x, self.size[0]):
                    if self.map[i][y] == 0:
                        end = [i, y]
                    else:
                        break
                for i in range(x, -1, -1):
                    if self.map[i][y] == 0:
                        start = [i, y]
                    else:
                        break

                start = [start[0] - 2, start[1]]
                end = [end[0] + 2, end[1]]
            
        except IndexError:
            # se if the block that is out of limits is the end or the start
            if start == enemy["pos"]:
                start = None
            elif end == enemy["pos"]:
                end = None
            pass
        
        return (start, end)
    
    # function that gets the offlimits around the fygar tunnels
    def tunnel_offlimits(self, enemies):
        offlimits = []

        for enemy in enemies:
            x = enemy["pos"][0]
            y = enemy["pos"][1]
            try:
                if self.map[x][y+1] == 0 or self.map[x][y-1] == 0: # vertical
                    column = self.map[x]
                    for i in range(y, len(column)):
                        if column[i] == 0:
                            if enemy == self.closest_enemy:
                                offlimits.append([x + 1, i])
                                offlimits.append([x - 1, i])
                            else:
                                offlimits.append([x, i])
                                offlimits.append([x, i + 1])
                                offlimits.append([x, i - 1])
                                offlimits.append([x + 1, i])
                                offlimits.append([x - 1, i])
                        else:
                            break
                    for i in range(y, -1, -1):
                        if column[i] == 0:
                            if enemy == self.closest_enemy:
                                offlimits.append([x + 1, i])
                                offlimits.append([x - 1, i])
                            else:
                                offlimits.append([x, i])
                                offlimits.append([x, i + 1])
                                offlimits.append([x, i - 1])
                                offlimits.append([x + 1, i])
                                offlimits.append([x - 1, i])
                        else:
                            break

                elif self.map[x+1][y] == 0 or self.map[x-1][y] == 0: # horizontal
                    for i in range(x, self.size[0]):
                        if self.map[i][y] == 0:
                            if enemy == self.closest_enemy:
                                offlimits.append([i, y + 1])
                                offlimits.append([i, y - 1])
                            else:
                                offlimits.append([i, y])
                                offlimits.append([i + 1, y])
                                offlimits.append([i - 1, y])
                                offlimits.append([i, y + 1])
                                offlimits.append([i, y - 1])
                        else:
                            break
                    for i in range(x, -1, -1):
                        if self.map[i][y] == 0:
                            if enemy == self.closest_enemy:
                                offlimits.append([i, y + 1])
                                offlimits.append([i, y - 1])
                            else:
                                offlimits.append([i, y])
                                offlimits.append([i + 1, y])
                                offlimits.append([i - 1, y])
                                offlimits.append([i, y + 1])
                                offlimits.append([i, y - 1])
                        else:
                            break
            except IndexError:
                # if the block is out of the map it will be ignored but it will continue the loop
                continue
        return offlimits
    
    def print_map(self, map):
        for i in range(len(map[0])):
            for j in range(len(map)):
                print(map[j][i], end=" ")
            print()
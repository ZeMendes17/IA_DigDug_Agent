from digdug import *

class Agent():
    def __init__(self):
        self.state = None
        self.key = " "
        self.map = None
        self.size = None
        self.my_position = None
        self.my_tunnel = []

        self.closest_enemy = None
        self.offlimits = set()
        self.trace_back = []
        self.path = []
        self.wait = False
        self.entry = None

        self.level = 0
        self.count = 1

    def update_state(self, state):
        if 'map' in state:
            self.map = state['map']
            self.level = state['level']
            self.size  = state['size']

        elif 'digdug' in state and state['enemies'] != []:
            if self.level != self.count:
                self.key = " "
                return self.key

            self.state = state
            self.my_position = state['digdug']
            # update the map with the new position
            self.map[self.my_position[0]][self.my_position[1]] = 0
            # get my updated tunnel
            self.my_tunnel = self.get_tunnel(self.my_position[0], self.my_position[1], self.map, [])

            ## if you want to see the map
            # print(self.print_enemy_tunnels(self.get_enemy_tunnels(state['enemies'])))

            # if pooka is traversing, go back
            if self.is_pooka_traversing(state):
                if self.my_position == [0, 0]:
                    self.key = " "
                    return self.key

                if self.trace_back == []:
                    st = self.get_tree_search([0, 0], self.my_tunnel).search()[1:]
                    next_position = st[0]
                    self.trace_back = st[1:]

                    return self.go_to(next_position)

                else:
                    next_position = self.trace_back[0]
                    self.trace_back = self.trace_back[1:]
                    # reset variables
                    self.closest_enemy = None
                    self.offlimits = set()
                    self.path = []
                    self.wait = False

                return self.go_to(next_position)


            # get enemies in my tunnel
            in_my_tunnel = [enemy for enemy in state['enemies'] if enemy['pos'] in self.my_tunnel]
            print(in_my_tunnel)
            if in_my_tunnel != []:
                print("ENTROU")
                # get the closest enemy
                self.closest_enemy = in_my_tunnel[0]
                for enemy in in_my_tunnel:
                    if self.distance(self.my_position, enemy['pos']) < self.distance(self.my_position, self.closest_enemy['pos']):
                        self.closest_enemy = enemy


                # if the enemy is close enough, face it and attack
                if (self.distance(self.my_position, self.closest_enemy['pos']) < 3):
                    if self.is_facing_enemy():
                        if self.only_tunnel_between():
                            self.key = "A"
                            return self.key

                st = self.get_tree_search(self.closest_enemy['pos'], self.my_tunnel)
                next_position = st.search()[1]
                
                # reset variables
                self.offlimits = set()
                self.path = []
                self.wait = False

                print("SAIU")
                return self.go_to(next_position)
            
            self.trace_back = []

            if self.path == []:
                if self.wait:
                    self.key = " "
                    
                    if self.enter_tunnel():
                        self.wait = False
                        self.key = self.go_to(self.entry[1])
                    
                    return self.key


                else:
                    enemy_tunnels = self.get_enemy_tunnels(state['enemies'])
                    # print(state['enemies'])
                    # print(self.print_map(self.map))
                    # print()
                    # for tunnel in enemy_tunnels:
                    #     print(tunnel)
                    entries = [entry for tunnel in enemy_tunnels for entry in self.get_tunnel_entries(tunnel)]
                    self.offlimits = [border for tunnel in enemy_tunnels for border in self.get_tunnel_borders(tunnel)]
                    rocks = [rock['pos'] for rock in state['rocks']]
                    below_rocks = [[rock[0], rock[1] + 1] for rock in rocks]
                    self.offlimits += rocks
                    self.offlimits += below_rocks
                    self.entry = self.closest_entry(entries)

                    st = self.get_tree_search(self.entry[0], self.map)
                    # if st.search() == [self.my_position]:
                    #     self.wait = True
                    #     self.key = " "
                    #     return self.key
                    self.path = st.search()[1:]
                    self.key = self.go_to(self.path[0])
                    self.path = self.path[1:]

                    return self.key

            else:
                if len(self.path) <= 1:
                    self.wait = True

                next_position = self.path[0]
                self.path = self.path[1:]

                return self.go_to(next_position)
            
        else:
            # reset variables
            self.count += 1
            self.my_tunnel = []
            self.offlimits = set()
            self.trace_back = []
            self.path = []
            self.wait = False
            self.key = " "
            print(self.state)
        return self.key
    
    # function to know if there is only tunnel between digdug and the enemy
    def only_tunnel_between(self):
        # first lets get our direction
        agent_dir = self.get_direction(self.my_position, self.closest_enemy['pos'])

        blocks_between = []

        if agent_dir == 0: # up
            blocks_between = [[self.my_position[0], i] for i in range(self.my_position[1]+1, self.closest_enemy['pos'][1])]
        elif agent_dir == 1: # right
            blocks_between = [[i, self.my_position[1]] for i in range(self.my_position[0]+1, self.closest_enemy['pos'][0])]

        elif agent_dir == 2: # down
            blocks_between = [(self.my_position[0], i) for i in range(self.closest_enemy['pos'][1] + 1, self.my_position[1])]

        elif agent_dir == 3: # left
            blocks_between = [(i, self.my_position[1]) for i in range(self.closest_enemy['pos'][0] + 1, self.my_position[0])]


        return all(self.map[i][j] == 0 for i,j in blocks_between)

    # function to know the direction the digdug is facing
    def get_direction(self, origin, destination):
        if origin[0] < destination[0]:
            return 1 # right
        
        elif origin[0] > destination[0]:
            return 3 # left
        
        elif origin[1] < destination[1]:
            return 2 # down
        
        elif origin[1] > destination[1]:
            return 0 # up
        
        else:
            return -1 # No direction aka same position



    # function to know if digdug is facing an enemy
    def is_facing_enemy(self):
        agent_dir = self.get_direction(self.my_position, self.closest_enemy['pos'])
        
        return (
            (agent_dir == 0 and self.closest_enemy['dir'] in {0, 1, 2, 3})
            or (agent_dir == 1 and self.closest_enemy['dir'] in {0, 1, 2, 3})
            or (agent_dir == 2 and self.closest_enemy['dir'] in {0, 1, 2, 3})
            or (agent_dir == 3 and self.closest_enemy['dir'] in {0, 1, 2, 3})
        )
    


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
            key = "d"
        elif self.my_position[0] > position[0]:
            key = "a"
        elif self.my_position[1] < position[1]:
            key = "s"
        elif self.my_position[1] > position[1]:
            key = "w"
        else:
            key = " "
        return key
    
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

    # function to get all enemy tunnels
    def get_enemy_tunnels(self, enemies):
        tunnels = []
        for enemy in enemies:
            tunnel = self.get_tunnel(enemy["pos"][0], enemy["pos"][1], self.map, [])
            if tunnel not in tunnels:
                tunnels.append(tunnel)

        return tunnels

    # function to get the entries of a tunnel
    def get_tunnel_entries(self, tunnel):
        entries = []
        # get the furtherst left and right, up and down positions
        left = tunnel[0]
        right = tunnel[0]
        up = tunnel[0]
        down = tunnel[0]
        for position in tunnel:
            if position[0] < left[0]:
                left = position
            elif position[0] > right[0]:
                right = position
            elif position[1] < up[1]:
                up = position
            elif position[1] > down[1]:
                down = position

        # if it is not the furthest point, it is not an entry
        for position in tunnel:
            if left != None and position[0] == left[0] and position[1] != left[1]:
                left = None
            elif right != None and position[0] == right[0] and position[1] != right[1]:
                right = None
            elif up != None and position[1] == up[1] and position[0] != up[0]:
                up = None
            elif down != None and position[1] == down[1] and position[0] != down[0]:
                down = None

        # get each point 2 squares away from the entry in order to not perfurate the tunnel
        # this will store a tuple like: (position to go to, position to enter the tunnel)
        if left != None:
            left = ([left[0] - 2, left[1]], [left[0] - 1, left[1]])
        if right != None:
            right = ([right[0] + 2, right[1]], [right[0] + 1, right[1]])
        if up != None:
            up = ([up[0], up[1] - 2], [up[0], up[1] - 1])
        if down != None:
            down = ([down[0], down[1] + 2], [down[0], down[1] + 1])

        return [x for x in [left, right, up, down] if x != None and x[0][0] >= 0 and x[0][0] < len(self.map) and x[0][1] >= 0 and x[0][1] < len(self.map[0])]
    
    # function to get the borders of a tunnel
    def get_tunnel_borders(self, tunnel):
        borders = []
        
        for position in tunnel:
            adjacent_cells = [[position[0]-1, position[1]], [position[0]+1, position[1]], [position[0], position[1]-1], [position[0], position[1]+1]]
            for cell in adjacent_cells:
                if cell[0] >= 0 and cell[0] < len(self.map) and cell[1] >= 0 and cell[1] < len(self.map[0]):
                    if self.map[cell[0]][cell[1]] != 0 and cell not in borders:
                        borders.append(cell)

        return borders
    
    # function to get the closest position from a list of positions
    def closest_entry(self, entries):
        closest = entries[0]
        for entry in entries:
            if self.distance(self.my_position, entry[0]) < self.distance(self.my_position, closest[0]):
                closest = entry
        return closest
    
    # function to see if digdug can enter a tunnel
    def enter_tunnel(self):
        position = self.entry[1]
        dir = self.go_to(position)
        if dir == "a":
            line = []
            for i in range(position[0] - 1, 0, -1):
                if self.map[i][position[1]] == 0:
                    line.append([i, position[1]])
                else:
                    break

            for enemy in self.state["enemies"]:
                if enemy["pos"] in line and enemy["dir"] == 1:
                    return False
                
        elif dir == "w":
            column = []
            for i in range(position[1] - 1, 0, -1):
                if self.map[position[0]][i] == 0:
                    column.append([position[0], i])
                else:
                    break

            for enemy in self.state["enemies"]:
                if enemy["pos"] in column and enemy["dir"] == 2:
                    return False
                
        elif dir == "d":
            line = []
            for i in range(position[0] + 1, len(self.map)):
                if self.map[i][position[1]] == 0:
                    line.append([i, position[1]])
                else:
                    break

            for enemy in self.state["enemies"]:
                if enemy["pos"] in line and enemy["dir"] == 3:
                    return False
                
        elif dir == "s":
            column = []
            for i in range(position[1] + 1, len(self.map[0])):
                if self.map[position[0]][i] == 0:
                    column.append([position[0], i])
                else:
                    break

            for enemy in self.state["enemies"]:
                if enemy["pos"] in column and enemy["dir"] == 0:
                    return False

        return True

    
    
    def print_map(self, map):
        for i in range(len(map[0])):
            for j in range(len(map)):
                print(map[j][i], end=" ")
            print()

    def print_enemy_tunnels(self, tunnels):
        for i in range(len(self.map[0])):
            for j in range(len(self.map)):
                for tunnel in tunnels:
                    if [j, i] in self.get_tunnel_borders(tunnel):
                        print("B", end=" ")
                        break 
                    if [j, i] in [entry[0] for entry in self.get_tunnel_entries(tunnel)]:
                        print("E", end=" ")
                        break
                    if [j, i] in tunnel:
                        print("X", end=" ")
                        break
                else:
                    print(self.map[j][i], end=" ")
            print()
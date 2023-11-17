from digdug import *

# states
STATE_IDLE = 0
STATE_GOAROUND = 1
STATE_SHOOT = 2

# initial state
current_state = STATE_IDLE

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
        self.path_behind_enemy = []
        self.wait = False
        self.entry = None

        self.last_dir = None
        self.go_to_position = None

        self.go_up = False
        self.go_rigth = False
        self.go_left = False
        self.flag = False

        self.level = 0
        self.count = 1
        self.around_enemy = False
        self.drop_rock = False

    def update_state(self, state, current_state=STATE_IDLE):
        if 'map' in state:
            self.map = state['map']
            self.level = state['level']
            self.size  = state['size']

        elif 'digdug' in state and state['enemies'] != []:
            print(self.path)
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

            # get enemies in my tunnel
            in_my_tunnel = [enemy for enemy in state['enemies'] if enemy['pos'] in self.my_tunnel]
            # print(in_my_tunnel)
            if in_my_tunnel != []:
                # get the closest enemy
                self.closest_enemy = in_my_tunnel[0]
                for enemy in in_my_tunnel:
                    if self.distance(self.my_position, enemy['pos']) < self.distance(self.my_position, self.closest_enemy['pos']):
                        self.closest_enemy = enemy

                # if self.path_behind_enemy != []:
                #     next_position = self.path_behind_enemy[0]
                #     self.path_behind_enemy = self.path_behind_enemy[1:]
                #     return self.go_to(next_position)

                # if self.fygar_our_way(state['enemies']):
                #     self.go_behind(self.closest_enemy)
                #     next_position = self.path_behind_enemy[0]
                #     self.path_behind_enemy = self.path_behind_enemy[1:]
                #     return self.go_to(next_position)

                if self.closest_enemy['name'] != "Fygar":
                    self.around_enemy = False
                    

                if self.around_enemy:
                    if self.closest_enemy['dir'] == 1 and self.closest_enemy['pos'][0] - self.my_position[0] <= 2:
                        self.key = "a"
                        return self.key
                    
                    elif self.closest_enemy['dir'] == 3 and self.my_position[0] - self.closest_enemy['pos'][0] <= 2:
                        self.key = "d"
                        return self.key

                    else:
                        self.around_enemy = False
                        return self.go_to([self.my_position[0], self.closest_enemy['pos'][1]])
                    
                if self.rock_between(self.closest_enemy):
                    print("rock between")
                    self.around_enemy = True
                    if self.my_position[1] + 1 < len(self.map[0]):
                        self.key = "s"
                        return self.key
                    else:
                        self.key = "w"
                        return self.key

                if not self.same(self.closest_enemy):
                    next_position = self.go_behind(self.closest_enemy)
                    if next_position != None:
                        self.key = next_position
                        return next_position
                    
                if self.fygar_our_way(self.closest_enemy):
                    self.around_enemy = True
                    if self.my_position[1] + 1 < len(self.map[0]):
                        self.key = "s"
                        return self.key
                    else:
                        self.key = "w"
                        return self.key

                    
                self.go_to_position = self.my_position
                # if the enemy is close enough, face it and attack
                if (self.distance(self.my_position, self.closest_enemy['pos']) <= 3):
                    # If we are facing the enemy
                    if self.is_facing_enemy():
                        # and there is no walls between us shoot
                        #if self.only_tunnel_between() and not self.wait:
                        self.key = "A"
                        
                        # if there is walls lets keep going towards the enemy
                        #else:
                        #print("Walls between")
                        #self.key = self.go_to(self.closest_enemy['pos'])
                        
                    
                    # IF we are nor facing the enemy we probably too close, so we need to do a step back and redirect our direction
                    elif (self.closest_enemy['pos'][1] < self.my_position[1]): # up

                        # If we are in the same x as the enemy, we need to do a step back
                        if self.closest_enemy['pos'][0] == self.my_position[0]:
                            self.key = 's'

                        # If we are not in the same x as the enemy, we need to go to the same x as the enemy
                        else:
                            self.go_to_position[0] = self.closest_enemy['pos'][0]
                            self.key = self.go_to(self.go_to_position)


                    elif  (self.closest_enemy['pos'][0] > self.my_position[0]): # right
                        if self.closest_enemy['pos'][1] == self.my_position[1]:
                            self.key = 'a'

                        else:
                            self.go_to_position[1] = self.closest_enemy['pos'][1]
                            self.key = self.go_to(self.go_to_position)

                       
                    elif (self.closest_enemy['pos'][1] > self.my_position[1]): # down
                        if self.closest_enemy['pos'][0] == self.my_position[0]:
                            self.key = 'w'                      
                        else:
                            self.go_to_position[0] = self.closest_enemy['pos'][0]
                            self.key = self.go_to(self.go_to_position)

                    elif (self.closest_enemy['pos'][0] < self.my_position[0]): # left
                        if self.closest_enemy['pos'][1] == self.my_position[1]:
                            self.key = 'd'
                        else:
                            self.go_to_position[1] = self.closest_enemy['pos'][1]
                            self.key = self.go_to(self.go_to_position)

                    return self.key                  

                    
                    

                else:
                    self.key = self.go_to(self.closest_enemy['pos'])
                    return self.key
                    

            # if pooka is traversing, go back
            # TEMPORARY
            closest_enemy = state['enemies'][0]
            for enemy in state['enemies']:
                if self.distance(self.my_position, enemy['pos']) < self.distance(self.my_position, closest_enemy['pos']):
                    closest_enemy = enemy
            if 'traverse' in closest_enemy:
                self.key = self.go_to([0, 0])
                return self.key

            # if self.is_pooka_traversing(state):
            #     if self.my_position == [0, 0]:
            #         self.key = " "
            #         return self.key

            #     possible_positions = []
            #     if self.my_position[0] - 1 > 0 and self.map[self.my_position[0] - 1][self.my_position[1]] == 0:
            #         possible_positions.append([self.my_position[0] - 1, self.my_position[1]])

            #     if self.my_position[0] + 1 < self.size[0] and self.map[self.my_position[0] + 1][self.my_position[1]] == 0:
            #         possible_positions.append([self.my_position[0] + 1, self.my_position[1]])

            #     if self.my_position[1] - 1 > 0 and self.map[self.my_position[0]][self.my_position[1] - 1] == 0:
            #         possible_positions.append([self.my_position[0], self.my_position[1] - 1])

            #     if self.my_position[1] + 1 < self.size[1] and self.map[self.my_position[0]][self.my_position[1] + 1] == 0:
            #         possible_positions.append([self.my_position[0], self.my_position[1] + 1])

            #     # get what is the closest position to [0, 0]
            #     closest_position = possible_positions[0]
            #     for position in possible_positions:
            #         if self.distance(position, [0, 0]) < self.distance(closest_position, [0, 0]):
            #             closest_position = position

            #     self.key = self.go_to(closest_position)
            #     return self.key
            
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
                    # if an offlimit is one of the entries, remove it
                    entries = [entry for entry in entries if entry[0] not in self.offlimits]
                    self.entry = self.closest_entry(entries)
                    print(self.entry)
                    # print(self.offlimits)

                    st = self.get_tree_search(self.entry[0], self.map)
                    # if st.search() == [self.my_position]:
                    #     self.wait = True
                    #     self.key = " "
                    #     return self.key
                    # print(st.search())
                    print("BEFORE")
                    print("AFTER")
                    self.path = st.search()[1:]
                    print("AFTER2")
                    if self.path == []:
                        self.wait = True
                        self.key = " "
                        return self.key
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
        return self.key
    
    # function to know if there is only tunnel between digdug and the enemy
    def only_tunnel_between(self):

        blocks_between = []

        if  (self.closest_enemy['pos'][0] == self.my_position[0] and self.closest_enemy['pos'][1] < self.my_position[1]): # up
            blocks_between = [[self.my_position[0], i] for i in range(self.my_position[1]+1, self.closest_enemy['pos'][1])]

        elif  (self.closest_enemy['pos'][1] == self.my_position[1] and self.closest_enemy['pos'][0] > self.my_position[0]): # right
            blocks_between = [[i, self.my_position[1]] for i in range(self.my_position[0]+1, self.closest_enemy['pos'][0])]

        elif (self.closest_enemy['pos'][0] == self.my_position[0] and self.closest_enemy['pos'][1] > self.my_position[1]): # down
            blocks_between = [(self.my_position[0], i) for i in range(self.closest_enemy['pos'][1] + 1, self.my_position[1])]

        elif (self.closest_enemy['pos'][1] == self.my_position[1] and self.closest_enemy['pos'][0] < self.my_position[0]): # left
            blocks_between = [(i, self.my_position[1]) for i in range(self.closest_enemy['pos'][0] + 1, self.my_position[0])]


        return all(self.map[i][j] == 0 for i,j in blocks_between)

    # function to know the direction the digdug is facing
    def get_direction(self):
        return self.last_dir


    # function to know if digdug is facing an enemy
    def is_facing_enemy(self):
        agent_dir = self.get_direction()
        
        if (agent_dir == 0 and self.closest_enemy['pos'][0] == self.my_position[0] and self.closest_enemy['pos'][1] < self.my_position[1]): # up
            print("facing up")
            return True
            
        elif (agent_dir == 1 and self.closest_enemy['pos'][1] == self.my_position[1] and self.closest_enemy['pos'][0] > self.my_position[0]):
            return True
        
        elif (agent_dir == 2 and self.closest_enemy['pos'][0] == self.my_position[0] and self.closest_enemy['pos'][1] > self.my_position[1]):
            print("facing down")
            return True
        
        elif (agent_dir == 3 and self.closest_enemy['pos'][1] == self.my_position[1] and self.closest_enemy['pos'][0] < self.my_position[0]):
            return True
        
        return False
        

    


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
        print("returns tree search")
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
            self.last_dir = 1
        elif self.my_position[0] > position[0]:
            key = "a"
            self.last_dir = 3
        elif self.my_position[1] < position[1]:
            key = "s"
            self.last_dir = 2
        elif self.my_position[1] > position[1]:
            key = "w"
            self.last_dir = 0
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
            if enemy["name"] == "Pooka" and 'traverse' in enemy:
                continue
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

        if [left, right, up, down] == [None, None, None, None]:
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

            left = ([left[0] - 2, left[1]], [left[0] - 1, left[1]])
            right = ([right[0] + 2, right[1]], [right[0] + 1, right[1]])
            up = ([up[0], up[1] - 2], [up[0], up[1] - 1])
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
    
    # function to go behind an enemy
    def go_behind(self, enemy):
        if enemy["dir"] == 0 or enemy["dir"] == 2:
            if abs(self.my_position[1] - enemy["pos"][1]) <= 3: # has to go further
                if self.my_position[1] < enemy["pos"][1]:
                    return self.go_to([self.my_position[0], self.my_position[1] - 1])
                else:
                    return self.go_to([self.my_position[0], self.my_position[1] + 1])
            else:
                return self.go_to([enemy["pos"][0], self.my_position[1]])
            
        elif enemy["dir"] == 1 or enemy["dir"] == 3:
            if abs(self.my_position[0] - enemy["pos"][0]) <= 3:
                if self.my_position[0] < enemy["pos"][0]:
                    return self.go_to([self.my_position[0] - 1, self.my_position[1]])
                else:
                    return self.go_to([self.my_position[0] + 1, self.my_position[1]])
            else:
                return self.go_to([self.my_position[0], enemy["pos"][1]])
            

    # function to see if fygar horizontal and facing digdug
    def fygar_our_way(self, enemy):
        if enemy["name"] == "Fygar" and enemy["pos"][1] == self.my_position[1] and self.distance(self.my_position, enemy["pos"]) <= 4:
            if enemy["dir"] == 1 and enemy["pos"][0] < self.my_position[0]:
                return True
            elif enemy["dir"] == 3 and enemy["pos"][0] > self.my_position[0]:
                return True
        return False
                
    # funtion to see if digdug is in the same x or y as an enemy
    def same(self, enemy):
        if enemy["pos"][0] == self.my_position[0] or enemy["pos"][1] == self.my_position[1]:
            return True
        return False
    
    # function to see if there is a rock between digdug and the enemy
    def rock_between(self, enemy):
        print("Entrou")
        if enemy["pos"][0] == self.my_position[0]: # vertical
            if enemy["pos"][1] < self.my_position[1]: # enemy is above
                for rock in self.state["rocks"]:
                    if rock["pos"][0] == enemy["pos"][0] and rock["pos"][1] > enemy["pos"][1] and rock["pos"][1] < self.my_position[1]:
                        return True
            else:
                for rock in self.state["rocks"]:
                    if rock["pos"][0] == enemy["pos"][0] and rock["pos"][1] < enemy["pos"][1] and rock["pos"][1] > self.my_position[1]:
                        return True
        elif enemy["pos"][1] == self.my_position[1]: # horizontal
            if enemy["pos"][0] < self.my_position[0]: # enemy is to the left
                for rock in self.state["rocks"]:
                    if rock["pos"][1] == enemy["pos"][1] and rock["pos"][0] > enemy["pos"][0] and rock["pos"][0] < self.my_position[0]:
                        return True
            else:
                for rock in self.state["rocks"]:
                    if rock["pos"][1] == enemy["pos"][1] and rock["pos"][0] < enemy["pos"][0] and rock["pos"][0] > self.my_position[0]:
                        return True
        return False
    
    
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
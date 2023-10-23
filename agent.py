from digdug import *

class Agent():
    def __init__(self):
        self.state = None
        self.my_position = None
        self.enemy_positions = None
        self.closest_enemy = None
        self.map = None
        self.size = None
        self.key = " "
        

        self.count = 0
        self.rocks = []
        self.offlimits = set()
        self.trace_back = []

        self.path = []
        self.wait_to_shoot = False
        self.shoot = False
        self.closest_enemy_id = None


    def update_state(self, state):
        ## go after and shoot solution
        if 'map' in state:
            print("Map received")
            self.map = state['map']
            self.size = state["size"]

        if 'digdug' in state and state['enemies'] != []:
            # first we need to define the squares that are offlimits
            # for that we need to know which enemy we will be following
            # we will follow the closest one
            self.state = state
            self.my_position = state['digdug']

            # if self.is_pooka_traversing(state):
            #     if self.trace_back == []:
            #         domain = DigDug(self.offlimits, self.map, self.size)
            #         problem = SearchProblem(domain, self.my_position, [0, 0])
            #         tree = SearchTree(problem, "greedy")

            #         self.trace_back = tree.search()
            #         position = self.trace_back[0]
            #         self.trace_back = self.trace_back[1:]
            #         return position
                
            #     else:
            #         position = self.trace_back[0]
            #         self.trace_back = self.trace_back[1:]     

            #         if position[0] < self.my_position[0]:
            #             self.key = "a"
            #         elif position[0] > self.my_position[0]:
            #             self.key = "d"
            #         elif position[1] < self.my_position[1]:
            #             self.key = "w"
            #         elif position[1] > self.my_position[1]:
            #             self.key = "s"
            #         else:
            #             self.key = " "
            #         print(self.key)
            #         return self.key

            self.trace_back = []
            id_in_enemies = True
            for e in state["enemies"]:
                if e["id"] == self.closest_enemy_id:
                    id_in_enemies = True
                    break
                else:
                    id_in_enemies = False

            if not id_in_enemies:
                self.shoot = False
                self.closest_enemy_id = None
                self.closest_enemy = None
            
            if self.path == []:
                if self.wait_to_shoot:

                    enemy = None
                    for e in state["enemies"]:
                        if e["id"] == self.closest_enemy_id:
                            enemy = e
                            break
                    orientation = None

                    if self.my_position[0] < enemy["pos"][0]:
                        orientation = "d"
                    elif self.my_position[0] > enemy["pos"][0]:
                        orientation = "a"
                    elif self.my_position[1] < enemy["pos"][1]:
                        orientation = "s"
                    elif self.my_position[1] > enemy["pos"][1]:
                        orientation = "w"

                    if orientation == self.oposite_direction(enemy["dir"]):
                        self.key = orientation
                        self.wait_to_shoot = False
                        self.shoot = True
                        return self.key
                    else:
                        self.key = " "
                        return self.key
                    
                elif self.shoot:
                    enemy = None
                    for e in state["enemies"]:
                        if e["id"] == self.closest_enemy_id:
                            enemy = e
                            break

                    if self.distance(self.my_position, enemy["pos"]) > 3:
                        self.key = self.direction_to_enemy(self.my_position, enemy["pos"])
                        return self.key
                    
                    else:
                        self.key = "A"
                        return self.key

                else:
                    self.offlimits = [] # will have coordinates
                    enemies_to_offlimits = []
                    # print(state["enemies"])
                    for enemy in state["enemies"]:
                        if enemy["name"] == "Pooka":
                            if self.closest_enemy == None or self.distance(self.my_position, enemy["pos"]) < self.distance(self.my_position, self.closest_enemy["pos"]):
                                if self.closest_enemy != None:
                                    enemies_to_offlimits.append(self.closest_enemy)
                                self.closest_enemy = enemy

                            else:
                                enemies_to_offlimits.append(enemy)

                        elif enemy["name"] == "Fygar":
                            enemy_names = [e["name"] for e in state["enemies"]]
                            if "Pooka" not in enemy_names:
                                if self.closest_enemy == None or self.distance(self.my_position, enemy["pos"]) < self.distance(self.my_position, self.closest_enemy["pos"]):
                                    if self.closest_enemy != None:
                                        enemies_to_offlimits.append(self.closest_enemy)
                                    self.closest_enemy = enemy

                                else:   
                                    enemies_to_offlimits.append(enemy)

                            else:
                                enemies_to_offlimits.append(enemy)

                    self.closest_enemy_id = self.closest_enemy["id"]
                    print(self.closest_enemy)
                    
                    # offlimits
                    self.offlimits = self.get_offlimits(state["rocks"], enemies_to_offlimits)

                    print(self.offlimits)

                    # get the start and end of the tunnel
                    start, end = self.get_entries(self.closest_enemy)
                    closest = start if self.distance(self.my_position, start) < self.distance(self.my_position, end) else end

                    # using the domain, get the path to the closest enemy
                    domain = DigDug(self.offlimits, self.map, self.size)
                    problem = SearchProblem(domain, self.my_position, closest)
                    tree = SearchTree(problem, "greedy")
                    self.path = tree.search()
                

            else:
                if len(self.path) == 1:
                    self.wait_to_shoot = True

                next_step = self.path[0]
                self.path = self.path[1:]

                if self.my_position[0] > next_step[0]:
                    self.key = "a"
                elif self.my_position[0] < next_step[0]:
                    self.key = "d"
                elif self.my_position[1] > next_step[1]:
                    self.key = "w"
                elif self.my_position[1] < next_step[1]:
                    self.key = "s"
                else:
                    self.key = " "
                    


            
        else:
            self.key = " "   

        return self.key
            

    # funtion to calculate the distance between two points
    def distance(self, a, b):
        return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** (1 / 2)

    # function to calculate the closest enemy
    def get_closest(self):
        self.closest_enemy = self.enemy_positions[0]
        for enemy in self.enemy_positions:
            if self.distance(self.my_position, enemy) < self.distance(self.my_position, self.closest_enemy):
                self.closest_enemy = enemy
        return self.closest_enemy
    
    # function to calculate the direction to the closest enemy
    def direction_to_enemy(self, my_position, closest_enemy):
        if my_position[0] > closest_enemy[0]:
            self.key = "a"
            return "a"
        elif my_position[0] < closest_enemy[0]:
            self.key = "d"
            return "d"
        elif my_position[1] > closest_enemy[1]:
            self.key = "w"
            return "w"
        elif my_position[1] < closest_enemy[1]:
            self.key = "s"
            return "s"
        else:
            self.key = " "
            return " "
        
    # function that sees if digdug needs to shoot
    def shoot(self):
        # if the closest enemy is in the same row
        if self.my_position[1] == self.closest_enemy[1]:
            # if the closest enemy is on the left
            if self.my_position[0] > self.closest_enemy[0]:
                # if digdug is 3 blocks away from the enemy -> shoot!
                if self.my_position[0] - self.closest_enemy[0] <= 3 and not self.is_something_in_the_way("a"):
                    return True
            # if the closest enemy is on the right
            elif self.my_position[0] < self.closest_enemy[0]:
                # if digdug is 3 blocks away from the enemy -> shoot!
                if self.closest_enemy[0] - self.my_position[0] <= 3 and not self.is_something_in_the_way("d"):
                    return True
                
        # if the closest enemy is in the same column
        elif self.my_position[0] == self.closest_enemy[0]:
            # if the closest enemy is above
            if self.my_position[1] > self.closest_enemy[1]:
                # if digdug is 3 blocks away from the enemy -> shoot!
                if self.my_position[1] - self.closest_enemy[1] <= 3 and not self.is_something_in_the_way("w"):
                    return True
            # if the closest enemy is below
            elif self.my_position[1] < self.closest_enemy[1]:
                # if digdug is 3 blocks away from the enemy -> shoot!
                if self.closest_enemy[1] - self.my_position[1] <= 3 and not self.is_something_in_the_way("s"):
                    return True
        return False

    # function to see if there is something in the way of digdug and the enemy
    def is_something_in_the_way(self, direction):
        if direction == "a":
            if self.map[self.my_position[0] - 1][self.my_position[1]] != 0:
                return True
        elif direction == "d":
            if self.map[self.my_position[0] + 1][self.my_position[1]] != 0:
                return True
        elif direction == "w":
            if self.map[self.my_position[0]][self.my_position[1] - 1] != 0:
                return True
        elif direction == "s":
            if self.map[self.my_position[0]][self.my_position[1] + 1] != 0:
                return True
        return False
    
    # function to update the map
    def update_map(self):
        if self.map != None:
            self.map[self.my_position[0]][self.my_position[1]] = 0
            self.trace_back.append(self.my_position)


    # function that gets the offlimits around the fygar tunnels
    def tunnel_offlimits(self, enemies):
        offlimits = []

        for enemy in enemies:
            x = enemy["pos"][0]
            y = enemy["pos"][1]
            if self.map[x][y+1] == 0 or self.map[x][y-1] == 0: # vertical
                column = self.map[x]
                for i in range(y, len(column)):
                    if column[i] == 0:
                        offlimits.append([x, i])
                        offlimits.append([x, i + 1])
                        offlimits.append([x, i - 1])
                        offlimits.append([x + 1, i])
                        offlimits.append([x - 1, i])
                    else:
                        break
                for i in range(y, -1, -1):
                    if column[i] == 0:
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
                        offlimits.append([i, y])
                        offlimits.append([i + 1, y])
                        offlimits.append([i - 1, y])
                        offlimits.append([i, y + 1])
                        offlimits.append([i, y - 1])
                    else:
                        break
                for i in range(x, -1, -1):
                    if self.map[i][y] == 0:
                        offlimits.append([i, y])
                        offlimits.append([i + 1, y])
                        offlimits.append([i - 1, y])
                        offlimits.append([i, y + 1])
                        offlimits.append([i, y - 1])
                    else:
                        break

        return offlimits
    
    def get_entries(self, enemy):
        x = enemy["pos"][0]
        y = enemy["pos"][1]
        start = enemy["pos"]
        end = enemy["pos"]

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

        return (start, end)
                    
    
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

        
                    
            
    # function to know if a pooka is traverssing
    def is_pooka_traversing(self, state):
        enemies = state["enemies"]
        for enemy in enemies:
            if enemy["name"] == "Pooka":
                if 'traverse' in enemy:
                    return True
        return False
    
    # function to go back
    def go_back(self):
        if self.trace_back != []:
            return self.trace_back.pop()
        else:
            return None
        
    def closest_pooka(self, state):
        pookas = [p for p in state["enemies"] if p["name"] == "Pooka"]
        if pookas == []:
            return None
        
        closest = pookas[0]
        for pooka in pookas:
            if self.distance(self.my_position, pooka["pos"]) < self.distance(self.my_position, closest["pos"]):
                closest = pooka
        return closest
    
    def closest_pooka_tunnel(self, state): # will return the start and end of the tunnel
        pooka = self.closest_pooka(state)
        start = pooka["pos"]
        end = pooka["pos"]

        if pooka["dir"] == 0 or pooka["dir"] == 2: # vertical
            column = self.map[pooka["pos"][0]]
            for i in range(pooka["pos"][1], len(column)):
                if column[i] == 0:
                    end = (pooka["pos"][1], i)
                else:
                    break

            for i in range(pooka["pos"][1], -1, -1):
                if column[i] == 0:
                    start = (pooka["pos"][1], i)
                else:
                    break

            start = (pooka["pos"][0], start[1] - 2) # to go to the start of the tunnel without making a hole yet
            end = (pooka["pos"][0], end[1] + 2) # same here

        elif pooka["dir"] == 1 or pooka["dir"] == 3: # horizontal
            for i in range(pooka["pos"][0], len(self.map)):
                if self.map[i][pooka["pos"][1]] == 0:
                    end = (i, pooka["pos"][1])
                else:
                    break

            for i in range(pooka["pos"][0], -1, -1):
                if self.map[i][pooka["pos"][1]] == 0:
                    start = (i, pooka["pos"][1])
                else:
                    break

            start = (start[0] - 2, pooka["pos"][1]) # to go to the start of the tunnel without making a hole yet
            end = (end[0] + 2, pooka["pos"][1]) # same here
                

        return (start, end)
        

    def wait_to_attack(self, pooka):
        # vertical
        if pooka["dir"] == 0 and self.my_position[1] < pooka["pos"][1]:
            return True
        elif pooka["dir"] == 2 and self.my_position[1] > pooka["pos"][1]:
            return True

        # horizontal
        elif pooka["dir"] == 1 and self.my_position[0] > pooka["pos"][0]:
            return True
        elif pooka["dir"] == 3 and self.my_position[0] < pooka["pos"][0]:
            return True
            
        return False
    
    def go_after_and_shoot(self, pooka):
        # vertical
        if pooka["dir"] == 0 and (pooka["pos"][1] - self.my_position[1]) > 3:
            return "w"
        elif pooka["dir"] == 2 and (self.my_position[1] - pooka["pos"][1]) > 3:
            return "s"
        
        # horizontal
        elif pooka["dir"] == 1 and (pooka["pos"][0] - self.my_position[0]) > 3:
            return "d"
        elif pooka["dir"] == 3 and (self.my_position[0] - pooka["pos"][0]) > 3:
            return "a"
        
        return "A"
    
    def oposite_direction(self, direction):
        if direction == 0:
            return "w"
        elif direction == 2:
            return "s"
        elif direction == 3:
            return "a"
        elif direction == 1:
            return "d"
        return None
        
    #def pooka_in_my_tunel(self, p)

## go after and shoot solution
# if 'map' in state:
#     print("Map received")
#     self.map = state['map']

# if 'digdug' in state and state['enemies'] != []:
#     print(state)
#     self.state = state
#     self.my_position = state['digdug']
#     self.enemy_positions = []
#     for enemy in state["enemies"]:
#         self.enemy_positions.append(enemy["pos"])

#     for rock in state["rocks"]:
#         self.rocks.append(rock["pos"])

#     # see which one is the closest
#     self.closest_enemy = self.get_closest()

#     # if the closest enemy is 3 blocks away, shoot
#     if self.shoot():
#         self.key = "A"
#     else:
#         self.key = self.direction_to_enemy(self.my_position, self.closest_enemy)
#         # update the map
#         self.update_map()
# else:
#     self.key = " "   
# return self.key


# ## semi inteligent solution
# if 'map' in state:
#     self.map = state['map']

# if 'digdug' in state:
#     if self.offlimits == set():
#         self.offlimits = self.get_offlimits(state)

#     self.state = state
#     self.my_position = state['digdug']

#     if self.is_pooka_traversing(state):
#         position = self.go_back()
#         if self.my_position[0] - position[0] == 1:
#             return "a"
#         elif self.my_position[0] - position[0] == -1:
#             return "d"
#         elif self.my_position[1] - position[1] == 1:
#             return "w"
#         elif self.my_position[1] - position[1] == -1:
#             return "s"
#         return " "
    
#     start, end = self.closest_pooka_tunnel(state)
#     if self.distance(self.my_position, start) < self.distance(self.my_position, end):
#         if self.my_position == start:
#             if self.wait_to_attack(self.closest_pooka(state)):
#                 return " "
#             else:
#                 return self.go_after_and_shoot(self.closest_pooka(state))
            
#         self.key = self.direction_to_enemy(self.my_position, start)
#         self.update_map()
#     else:
#         if self.my_position == end:
#             if self.wait_to_attack(self.closest_pooka(state)):
#                 return " "
#             else:
#                 return self.go_after_and_shoot(self.closest_pooka(state))
            
#         self.key = self.direction_to_enemy(self.my_position, end)
#         self.update_map()

# else:
#     self.key = " "

# return self.key
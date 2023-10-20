from queue import PriorityQueue

class Agent():
    def __init__(self):
        self.state = None
        self.my_position = None
        self.enemy_positions = None
        self.closest_enemy = None
        self.map = None
        self.key = " "
        

        self.count = 0
        self.rocks = []
        self.offlimits = set()
        self.trace_back = []

    def update_state(self, state):
        ## go after and shoot solution
        if 'map' in state:
            print("Map received")
            self.map = state['map']

        if 'digdug' in state and state['enemies'] != []:
            print(state)
            self.state = state
            self.my_position = state['digdug']
            self.enemy_positions = []
            for enemy in state["enemies"]:
                self.enemy_positions.append(enemy["pos"])

            for rock in state["rocks"]:
                self.rocks.append(rock["pos"])

            # see which one is the closest
            self.closest_enemy = self.get_closest()

            # if the closest enemy is 3 blocks away, shoot
            if self.shoot():
                self.key = "A"
            else:
                self.key = self.direction_to_enemy(self.my_position, self.closest_enemy)
                # update the map
                self.update_map()
        else:
            self.key = " "   

        return self.key

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
    def fygar_offlimits(self, orientation, position):
        offlimits = set()
        x = position[0]
        y = position[1]

        if orientation == 0: # vertical
            column = self.map[x]
            for i in range(y, len(column)):
                if column[i] == 0:
                    offlimits.add((x, i), (x, i + 1), (x, i - 1), (x + 1, i), (x - 1, i))
                else:
                    break
            for i in range(y, -1, -1):
                if column[i] == 0:
                    offlimits.add((x, i), (x, i + 1), (x, i - 1), (x + 1, i), (x - 1, i))
                else:
                    break

        elif orientation == 1: # horizontal
            for i in range(x, len(self.map)):
                if self.map[i][y] == 0:
                    offlimits.add((i, y), (i + 1, y), (i - 1, y), (i, y + 1), (i, y - 1))
                else:
                    break
            for i in range(x, -1, -1):
                if self.map[i][y] == 0:
                    offlimits.add((i, y), (i + 1, y), (i - 1, y), (i, y + 1), (i, y - 1))
                else:
                    break

        return offlimits
    
    # function that gets map when it is received and gets important information from it
    def get_offlimits(self, state):
        # get all fygar tunnels
        enemies = state["enemies"]
        offlimits = set()
        for enemy in enemies:
            if enemy["name"] == "fygar":
                # see if the tunnel is horizontal or vertical
                if enemy["dir"] == 0 or enemy["dir"] == 2: # vertical
                    fygar = self.fygar_offlimits(0, enemy["pos"])
                    offlimits = offlimits.union(fygar)
                elif enemy["dir"] == 1 or enemy["dir"] == 3: # horizontal
                    fygar = self.fygar_offlimits(1, enemy["pos"])
                    offlimits = offlimits.union(fygar)
                    
        # get all rocks
        for rock in state["rocks"]:
            offlimits.union(rock["pos"])

        return offlimits
            
    # function to know if a pooka is traverssing
    def is_pooka_traversing(self, state):
        enemies = state["enemies"]
        for enemy in enemies:
            if enemy["name"] == "pooka":
                if enemy["state"] == True:
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
        
    #def pooka_in_my_tunel(self, p)
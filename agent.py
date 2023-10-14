class Agent():
    def __init__(self):
        self.state = None
        self.my_position = None
        self.enemy_positions = None
        self.closest_enemy = None
        self.map = None
        self.key = " "

    def update_state(self, state):
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
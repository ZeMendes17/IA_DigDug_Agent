class Agent():
    def __init__(self):
        self.state = None
        self.my_position = None
        self.enemy_positions = None
        self.closest_enemy = None
        self.key = " "

    def update_state(self, state):
        if 'digdug' in state:
            self.state = state
            self.my_position = state['digdug']
            self.enemy_positions = []
            for enemy in state["enemies"]:
                self.enemy_positions.append(enemy["pos"])

            # see which one is the closest
            self.closest_enemy = self.get_closest(self.my_position, self.enemy_positions)

            key = self.direction_to_enemy(self.my_position, self.closest_enemy)
        else:
            key = " "

        return key
    
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


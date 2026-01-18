import pygame


class Castle(pygame.Rect):
    def __init__(
        self,
        name,
        level,
        position=(0, 20),
        food=0,
        food_gain_amount=5,
        food_gain_interval=0.5,
        max_health=500,
    ):
        width, height = 200, 300
        super().__init__(position[0], position[1], width, height)
        self.name = name
        self.level = level
        self.food = food
        self._base_food_gain_amount = food_gain_amount
        self.food_gain_amount = food_gain_amount * level
        self.food_gain_interval = food_gain_interval
        self.max_health = max_health
        self.health = float(max_health)
        self._food_timer = 0.0

    def gain_food(self, delta_time):
        self._food_timer += delta_time
        if self._food_timer < self.food_gain_interval:
            return

        gain_cycles = int(self._food_timer // self.food_gain_interval)
        self._food_timer -= gain_cycles * self.food_gain_interval
        total_gain = gain_cycles * self.food_gain_amount
        self.food += total_gain
        print(f"{self.name} gained {total_gain} food. Total food: {self.food}")

    def upgrade(self):
        self.level += 1
        self.food_gain_amount = self._base_food_gain_amount * self.level
        print(f"{self.name} upgraded to level {self.level}!")

    def take_damage(self, amount):
        self.health = max(0.0, self.health - amount)
        print(f"{self.name} took {amount} damage. Remaining health: {self.health}")

    @property
    def is_destroyed(self):
        return self.health <= 0

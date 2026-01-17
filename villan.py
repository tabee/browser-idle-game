import pygame


class Villan:
    WIDTH = 40
    HEIGHT = 60

    def __init__(
        self,
        owner: str,
        spawn_pos: tuple[float, float],
        direction: int,
        speed: float = 140.0,
        max_health: int = 60,
        damage: int = 12,
        attack_cooldown: float = 0.8,
    ) -> None:
        self.owner = owner
        self.direction = direction
        self.speed = speed
        self.max_health = max_health
        self.health = float(max_health)
        self.damage = damage
        self.attack_cooldown = attack_cooldown
        self._attack_timer = 0.0
        self.rect = pygame.Rect(
            int(spawn_pos[0]),
            int(spawn_pos[1]) - self.HEIGHT,
            self.WIDTH,
            self.HEIGHT,
        )
        self._pos_x = float(self.rect.x)

    @property
    def is_alive(self) -> bool:
        return self.health > 0

    def move_forward(self, delta_time: float) -> None:
        self._pos_x += self.direction * self.speed * delta_time
        self.rect.x = int(self._pos_x)

    def take_damage(self, amount: float) -> None:
        self.health = max(0.0, self.health - amount)

    def ready_to_attack(self) -> bool:
        return self._attack_timer <= 0.0

    def tick_attack_timer(self, delta_time: float) -> None:
        if self._attack_timer > 0.0:
            self._attack_timer = max(0.0, self._attack_timer - delta_time)

    def register_attack(self) -> None:
        self._attack_timer = self.attack_cooldown

    def draw(self, surface: pygame.Surface, color: tuple[int, int, int]) -> None:
        pygame.draw.rect(surface, color, self.rect)
        if self.max_health <= 0:
            return
        health_ratio = self.health / self.max_health
        bar_width = int(self.rect.width * health_ratio)
        bar_rect = pygame.Rect(self.rect.x, self.rect.top - 6, bar_width, 4)
        back_rect = pygame.Rect(self.rect.x, self.rect.top - 6, self.rect.width, 4)
        pygame.draw.rect(surface, (60, 20, 20), back_rect)
        pygame.draw.rect(surface, (180, 40, 40), bar_rect)

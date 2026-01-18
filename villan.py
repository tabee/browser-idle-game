from __future__ import annotations

import pygame


class Villan:

    def __init__(
        self,
        owner: str,
        spawn_pos: tuple[float, float],
        direction: int,
        sprite: pygame.Surface,
        weapon_sprite: pygame.Surface | None = None,
        weapon_rotation_speed: float = 360.0,
        weapon_rotation_direction: float = 1.0,
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
        self.sprite = sprite
        width = sprite.get_width()
        height = sprite.get_height()
        self.rect = pygame.Rect(
            int(spawn_pos[0]),
            int(spawn_pos[1]) - height,
            width,
            height,
        )
        self._pos_x = float(self.rect.x)
        self.weapon_base_sprite = weapon_sprite
        self.weapon_rotation_speed = weapon_rotation_speed
        self.weapon_rotation_direction = weapon_rotation_direction
        self.weapon_angle = 0.0
        self.weapon_surface: pygame.Surface | None = None
        self.weapon_rect: pygame.Rect | None = None
        if self.weapon_base_sprite is not None:
            self._refresh_weapon_surface()

    @property
    def is_alive(self) -> bool:
        return self.health > 0

    def move_forward(self, delta_time: float) -> None:
        self._pos_x += self.direction * self.speed * delta_time
        self.rect.x = int(self._pos_x)
        self._set_weapon_center()

    def take_damage(self, amount: float) -> None:
        self.health = max(0.0, self.health - amount)

    def ready_to_attack(self) -> bool:
        return self._attack_timer <= 0.0

    def tick_attack_timer(self, delta_time: float) -> None:
        if self._attack_timer > 0.0:
            self._attack_timer = max(0.0, self._attack_timer - delta_time)

    def register_attack(self) -> None:
        self._attack_timer = self.attack_cooldown

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self.sprite, self.rect)
        if self.weapon_surface is not None and self.weapon_rect is not None:
            surface.blit(self.weapon_surface, self.weapon_rect)
        if self.max_health <= 0:
            return
        health_ratio = self.health / self.max_health
        bar_width = int(self.rect.width * health_ratio)
        bar_rect = pygame.Rect(self.rect.x, self.rect.top - 6, bar_width, 4)
        back_rect = pygame.Rect(self.rect.x, self.rect.top - 6, self.rect.width, 4)
        pygame.draw.rect(surface, (60, 20, 20), back_rect)
        pygame.draw.rect(surface, (180, 40, 40), bar_rect)

    def update_weapon(self, delta_time: float, engaged: bool) -> None:
        if self.weapon_base_sprite is None:
            return
        if engaged:
            self.weapon_angle = (
                self.weapon_angle
                + self.weapon_rotation_speed * self.weapon_rotation_direction * delta_time
            ) % 360.0
            self._refresh_weapon_surface()
        else:
            self._set_weapon_center()

    def _set_weapon_center(self) -> None:
        if self.weapon_rect is not None:
            self.weapon_rect.center = self._weapon_anchor()

    def _refresh_weapon_surface(self) -> None:
        if self.weapon_base_sprite is None:
            self.weapon_surface = None
            self.weapon_rect = None
            return
        if abs(self.weapon_angle) < 1e-5:
            self.weapon_surface = self.weapon_base_sprite
        else:
            self.weapon_surface = pygame.transform.rotate(
                self.weapon_base_sprite, -self.weapon_angle
            )
        self.weapon_rect = self.weapon_surface.get_rect(center=self._weapon_anchor())

    def _weapon_anchor(self) -> tuple[int, int]:
        anchor_y = self.rect.centery
        if self.direction > 0:
            return self.rect.right, anchor_y
        if self.direction < 0:
            return self.rect.left, anchor_y
        return self.rect.center

from __future__ import annotations

import pygame
from castle import Castle
from villan import Villan

pygame.init()

font = pygame.font.SysFont("arial", 24)
small_font = pygame.font.SysFont("arial", 20)
overlay_font = pygame.font.SysFont("arial", 48)

VILLAN_COST = 40
ENEMY_SPAWN_INTERVAL = 4.0
VILLAN_PLAYER_COLOR = (70, 170, 100)
VILLAN_ENEMY_COLOR = (190, 90, 90)
BUTTON_WIDTH, BUTTON_HEIGHT = 200, 60

castle_left = Castle("LeftCastle", 1, position=(50, 50))
castle_right = Castle("RightCastle", 1, position=(1350, 50))
castles = [castle_left, castle_right]


def create_villan_for_castle(castle: Castle, direction: int, owner: str) -> Villan:
    spawn_x = castle.right if direction > 0 else castle.left - Villan.WIDTH
    spawn_y = castle.bottom
    return Villan(owner, (spawn_x, spawn_y), direction)

W, H = 1600, 900
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Rect läuft links/rechts (pygame-ce)")

buy_button_rect = pygame.Rect(30, H - BUTTON_HEIGHT - 30, BUTTON_WIDTH, BUTTON_HEIGHT)

clock = pygame.time.Clock()

player_villans: list[Villan] = []
enemy_villans: list[Villan] = []
enemy_spawn_timer = ENEMY_SPAWN_INTERVAL
game_over_text: str | None = None

# Spieler-Rect
player = pygame.Rect(100, H // 2 - 25, 60, 50)
speed = 420  # Pixel pro Sekunde



running = True
while running:
    dt = clock.tick(60) / 1000.0  # Sekunden seit letztem Frame

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if buy_button_rect.collidepoint(event.pos) and castle_left.food >= VILLAN_COST:
                castle_left.food -= VILLAN_COST
                player_villans.append(create_villan_for_castle(castle_left, 1, "player"))

    keys = pygame.key.get_pressed()

    # Bewegung (A/D oder Pfeile)
    direction = 0
    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        direction -= 1
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        direction += 1

    player.x += int(direction * speed * dt)

    # Im Fenster halten
    if player.left < 0:
        player.left = 0
    if player.right > W:
        player.right = W

    for castle in castles:
        castle.gain_food(dt)

    enemy_spawn_timer -= dt
    if enemy_spawn_timer <= 0.0:
        if castle_right.food >= VILLAN_COST:
            castle_right.food -= VILLAN_COST
            enemy_villans.append(create_villan_for_castle(castle_right, -1, "enemy"))
            enemy_spawn_timer = ENEMY_SPAWN_INTERVAL
        else:
            enemy_spawn_timer = 1.0

    for villan in (*player_villans, *enemy_villans):
        villan.tick_attack_timer(dt)

    engaged: set[Villan] = set()

    for pv in player_villans:
        if not pv.is_alive:
            continue
        for ev in enemy_villans:
            if not ev.is_alive:
                continue
            if pv.rect.colliderect(ev.rect):
                engaged.add(pv)
                engaged.add(ev)
                if pv.ready_to_attack():
                    ev.take_damage(pv.damage)
                    pv.register_attack()
                if ev.ready_to_attack():
                    pv.take_damage(ev.damage)
                    ev.register_attack()

    for pv in player_villans:
        if not pv.is_alive:
            continue
        if pv.rect.colliderect(castle_right):
            engaged.add(pv)
            if pv.ready_to_attack():
                castle_right.take_damage(pv.damage)
                pv.register_attack()

    for ev in enemy_villans:
        if not ev.is_alive:
            continue
        if ev.rect.colliderect(castle_left):
            engaged.add(ev)
            if ev.ready_to_attack():
                castle_left.take_damage(ev.damage)
                ev.register_attack()

    for pv in player_villans:
        if pv.is_alive and pv not in engaged:
            pv.move_forward(dt)

    for ev in enemy_villans:
        if ev.is_alive and ev not in engaged:
            ev.move_forward(dt)

    player_villans = [pv for pv in player_villans if pv.is_alive]
    enemy_villans = [ev for ev in enemy_villans if ev.is_alive]

    if game_over_text is None:
        if castle_left.is_destroyed:
            game_over_text = "Enemy wins!"
            running = False
        elif castle_right.is_destroyed:
            game_over_text = "Player wins!"
            running = False

    # Zeichnen
    screen.fill((20, 20, 25))

    for castle in castles:
        pygame.draw.rect(screen, (150, 75, 0), castle)
        name_surface = font.render(castle.name, True, (230, 230, 230))
        food_surface = small_font.render(f"Food: {castle.food}", True, (200, 200, 80))
        health_surface = small_font.render(f"HP: {int(castle.health)}", True, (200, 120, 120))
        name_rect = name_surface.get_rect(midbottom=(castle.centerx, castle.top - 10))
        food_rect = food_surface.get_rect(midtop=(castle.centerx, castle.bottom + 10))
        health_rect = health_surface.get_rect(midtop=(castle.centerx, food_rect.bottom + 4))
        screen.blit(name_surface, name_rect)
        screen.blit(food_surface, food_rect)
        screen.blit(health_surface, health_rect)

    for villan in player_villans:
        villan.draw(screen, VILLAN_PLAYER_COLOR)

    for villan in enemy_villans:
        villan.draw(screen, VILLAN_ENEMY_COLOR)

    pygame.draw.rect(screen, (80, 120, 120), player)

    affordable = castle_left.food >= VILLAN_COST
    button_color = (80, 180, 100) if affordable else (70, 70, 70)
    text_color = (20, 20, 20) if affordable else (200, 200, 200)
    pygame.draw.rect(screen, button_color, buy_button_rect, border_radius=10)
    pygame.draw.rect(screen, (25, 25, 25), buy_button_rect, width=2, border_radius=10)
    button_text = small_font.render(f"Buy Villan ({VILLAN_COST})", True, text_color)
    button_text_rect = button_text.get_rect(center=buy_button_rect.center)
    screen.blit(button_text, button_text_rect)

    if game_over_text is not None:
        overlay_surface = overlay_font.render(game_over_text, True, (240, 230, 140))
        overlay_rect = overlay_surface.get_rect(center=(W // 2, H // 2))
        screen.blit(overlay_surface, overlay_rect)

    pygame.display.flip()

pygame.quit()

if game_over_text is not None:
    print(game_over_text)

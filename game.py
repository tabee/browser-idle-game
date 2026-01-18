from __future__ import annotations

from dataclasses import dataclass
import random
from pathlib import Path
import pygame
from castle import Castle
from villan import Villan
from sprite_loader import SpriteAtlas

pygame.init()

font = pygame.font.SysFont("arial", 24)
small_font = pygame.font.SysFont("arial", 20)
overlay_font = pygame.font.SysFont("arial", 48)

@dataclass
class VillanStats:
    speed: float
    max_health: int
    damage: int


PLAYER_VILLAN_STATS = VillanStats(speed=140.0, max_health=60, damage=12)
ENEMY_VILLAN_STATS = VillanStats(speed=140.0, max_health=60, damage=12)

sprites_dir = Path(__file__).with_name("sprites")
spritesheet_image_path = sprites_dir / "spritesheet_retina.png"
spritesheet_meta_path = sprites_dir / "spritesheet_retina.xml"

VILLAN_COST = 40
BUTTON_WIDTH, BUTTON_HEIGHT = 200, 60
UPGRADE_BUTTON_MARGIN = 20
ENEMY_DECISION_INTERVAL = 3.0

UPGRADE_OPTIONS = [
    {"label": "Tower Lv +1", "cost": 100, "key": "tower"},
    {"label": "Speed +5", "cost": 60, "key": "speed"},
    {"label": "Damage +2", "cost": 50, "key": "damage"},
]

castle_left = Castle("LeftCastle", 1, position=(50, 50))
castle_right = Castle("RightCastle", 1, position=(1350, 50))
castle_left.villan_stats = PLAYER_VILLAN_STATS
castle_right.villan_stats = ENEMY_VILLAN_STATS
castles = [castle_left, castle_right]


def create_villan_for_castle(
    castle: Castle,
    direction: int,
    owner: str,
    sprite: pygame.Surface,
    weapon_sprite: pygame.Surface,
) -> Villan:
    spawn_x = castle.right if direction > 0 else castle.left - sprite.get_width()
    spawn_y = castle.bottom
    rotation_direction = -1.0 if owner == "enemy" else 1.0
    stats: VillanStats = getattr(castle, "villan_stats", PLAYER_VILLAN_STATS)
    return Villan(
        owner,
        (spawn_x, spawn_y),
        direction,
        sprite,
        weapon_sprite,
        weapon_rotation_direction=rotation_direction,
        speed=stats.speed,
        max_health=stats.max_health,
        damage=stats.damage,
    )


def apply_upgrade(castle: Castle, key: str, active_units: list[Villan]) -> None:
    if not hasattr(castle, "villan_stats"):
        castle.villan_stats = VillanStats(speed=140.0, max_health=60, damage=12)
    if key == "tower":
        castle.upgrade()
    elif key == "speed":
        castle.villan_stats.speed += 5
        for unit in active_units:
            unit.speed += 5
    elif key == "damage":
        castle.villan_stats.damage += 2
        for unit in active_units:
            unit.damage += 2


def enemy_take_action(castle: Castle, enemy_units: list[Villan]) -> bool:
    choices: list[dict[str, object]] = [{"type": "save", "cost": 0}]
    if castle.food >= VILLAN_COST:
        choices.append({"type": "spawn", "cost": VILLAN_COST})
    for option in UPGRADE_OPTIONS:
        if castle.food >= option["cost"]:
            choices.append({"type": "upgrade", "key": option["key"], "cost": option["cost"]})

    if not choices:
        return False

    action = random.choice(choices)
    action_type = action["type"]
    cost = action["cost"]

    if action_type == "save":
        return True

    if action_type == "spawn":
        castle.food -= cost
        enemy_units.append(
            create_villan_for_castle(
                castle,
                -1,
                "enemy",
                ENEMY_VILLAN_SPRITE,
                DEFAULT_WEAPON_SPRITE,
            )
        )
        return True

    if action_type == "upgrade":
        castle.food -= cost
        apply_upgrade(castle, action["key"], enemy_units)
        return True
    return False

W, H = 1600, 900
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Rect läuft links/rechts (pygame-ce)")

sprite_atlas = SpriteAtlas(spritesheet_image_path, spritesheet_meta_path)
PLAYER_VILLAN_SPRITE = sprite_atlas.sprite("character_squarePurple.png")
ENEMY_VILLAN_SPRITE = sprite_atlas.sprite("character_squareRed.png")
DEFAULT_WEAPON_SPRITE = sprite_atlas.sprite("item_sword.png")

buy_button_rect = pygame.Rect(30, H - BUTTON_HEIGHT - 30, BUTTON_WIDTH, BUTTON_HEIGHT)
upgrade_button_rects = []
for idx, _ in enumerate(UPGRADE_OPTIONS):
    x_pos = buy_button_rect.right + UPGRADE_BUTTON_MARGIN + idx * (BUTTON_WIDTH + UPGRADE_BUTTON_MARGIN)
    upgrade_button_rects.append(
        pygame.Rect(x_pos, H - BUTTON_HEIGHT - 30, BUTTON_WIDTH, BUTTON_HEIGHT)
    )

clock = pygame.time.Clock()

player_villans: list[Villan] = []
enemy_villans: list[Villan] = []
enemy_decision_timer = ENEMY_DECISION_INTERVAL
game_over_text: str | None = None



running = True
while running:
    dt = clock.tick(60) / 1000.0  # Sekunden seit letztem Frame

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if buy_button_rect.collidepoint(event.pos) and castle_left.food >= VILLAN_COST:
                castle_left.food -= VILLAN_COST
                player_villans.append(
                    create_villan_for_castle(
                        castle_left,
                        1,
                        "player",
                        PLAYER_VILLAN_SPRITE,
                        DEFAULT_WEAPON_SPRITE,
                    )
                )
            else:
                for idx, rect in enumerate(upgrade_button_rects):
                    if not rect.collidepoint(event.pos):
                        continue
                    option = UPGRADE_OPTIONS[idx]
                    if castle_left.food < option["cost"]:
                        break
                    castle_left.food -= option["cost"]
                    apply_upgrade(castle_left, option["key"], player_villans)
                    break

    for castle in castles:
        castle.gain_food(dt)

    if castle_right.food > VILLAN_COST:
        enemy_decision_timer -= dt
        if enemy_decision_timer <= 0.0:
            acted = enemy_take_action(castle_right, enemy_villans)
            enemy_decision_timer = ENEMY_DECISION_INTERVAL if acted else 1.0
    else:
        enemy_decision_timer = 0.0

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

    for villan in (*player_villans, *enemy_villans):
        villan.update_weapon(dt, villan in engaged)

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
        level_surface = small_font.render(f"Level: {castle.level}", True, (210, 180, 120))
        gain_surface = small_font.render(
            f"Food Gain: {getattr(castle, 'food_gain_amount', 0):.0f}", True, (210, 180, 120)
        )
        level_rect = level_surface.get_rect(midtop=(castle.centerx, health_rect.bottom + 4))
        gain_rect = gain_surface.get_rect(midtop=(castle.centerx, level_rect.bottom + 4))
        screen.blit(level_surface, level_rect)
        screen.blit(gain_surface, gain_rect)
        stats: VillanStats = getattr(castle, "villan_stats", PLAYER_VILLAN_STATS)
        stat_color = (180, 190, 210)
        stat_texts = (
            small_font.render(f"Speed: {stats.speed:.0f}", True, stat_color),
            small_font.render(f"HP: {stats.max_health}", True, stat_color),
            small_font.render(f"Damage: {stats.damage}", True, stat_color),
        )
        stat_y = gain_rect.bottom + 6
        for stat_surface in stat_texts:
            stat_rect = stat_surface.get_rect(midtop=(castle.centerx, stat_y))
            screen.blit(stat_surface, stat_rect)
            stat_y = stat_rect.bottom + 2

    for villan in player_villans:
        villan.draw(screen)

    for villan in enemy_villans:
        villan.draw(screen)

    affordable = castle_left.food >= VILLAN_COST
    button_color = (80, 180, 100) if affordable else (70, 70, 70)
    text_color = (20, 20, 20) if affordable else (200, 200, 200)
    pygame.draw.rect(screen, button_color, buy_button_rect, border_radius=10)
    pygame.draw.rect(screen, (25, 25, 25), buy_button_rect, width=2, border_radius=10)
    button_text = small_font.render(f"Buy Villan ({VILLAN_COST})", True, text_color)
    button_text_rect = button_text.get_rect(center=buy_button_rect.center)
    screen.blit(button_text, button_text_rect)

    for rect, option in zip(upgrade_button_rects, UPGRADE_OPTIONS):
        affordable_upgrade = castle_left.food >= option["cost"]
        upgrade_color = (120, 160, 220) if affordable_upgrade else (70, 70, 70)
        upgrade_text_color = (15, 20, 30) if affordable_upgrade else (200, 200, 200)
        pygame.draw.rect(screen, upgrade_color, rect, border_radius=10)
        pygame.draw.rect(screen, (25, 25, 25), rect, width=2, border_radius=10)
        label_surface = small_font.render(option["label"], True, upgrade_text_color)
        cost_surface = small_font.render(f"{option['cost']} food", True, upgrade_text_color)
        label_rect = label_surface.get_rect(midtop=(rect.centerx, rect.top + 8))
        cost_rect = cost_surface.get_rect(midtop=(rect.centerx, label_rect.bottom + 4))
        screen.blit(label_surface, label_rect)
        screen.blit(cost_surface, cost_rect)

    if game_over_text is not None:
        overlay_surface = overlay_font.render(game_over_text, True, (240, 230, 140))
        overlay_rect = overlay_surface.get_rect(center=(W // 2, H // 2))
        screen.blit(overlay_surface, overlay_rect)

    pygame.display.flip()

pygame.quit()

if game_over_text is not None:
    print(game_over_text)

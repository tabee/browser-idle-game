import pygame
import json
import os
from dataclasses import dataclass
from typing import List
import random


class SpriteManager:
    """Verwaltet Grass-Tile Sprites"""

    def __init__(self, graphics_folder: str):
        self.graphics_folder = graphics_folder
        self.tiles: List[pygame.Surface] = []
        self._load_tiles()

    def _load_tiles(self):
        """Lädt alle Grass-Tiles aus dem graphics Ordner"""
        tile_files = ["grass-tile.png", "grass-tile-2.png", "grass-tile-3.png"]
        
        for tile_file in tile_files:
            path = os.path.join(self.graphics_folder, tile_file)
            if os.path.exists(path):
                tile = pygame.image.load(path)
                # Skaliere auf 48x48
                tile = pygame.transform.scale(tile, (48, 48))
                self.tiles.append(tile)
            else:
                print(f"Warning: {path} not found")

    def get_random_tile(self) -> pygame.Surface:
        """Gibt ein zufälliges Tile zurück"""
        return random.choice(self.tiles) if self.tiles else None


@dataclass
class Tile:
    """Ein einzelner Tile in der Welt"""
    x: int
    y: int
    tile_index: int

    def to_dict(self) -> dict:
        return {"x": self.x, "y": self.y, "tile_index": self.tile_index}

    @classmethod
    def from_dict(cls, data: dict) -> "Tile":
        return cls(data["x"], data["y"], data["tile_index"])


class World:
    """Repräsentiert die gesamte Welt"""

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.tiles: List[Tile] = []

    def to_dict(self) -> dict:
        return {
            "width": self.width,
            "height": self.height,
            "tiles": [tile.to_dict() for tile in self.tiles]
        }

    @classmethod
    def from_dict(cls, data: dict) -> "World":
        world = cls(data["width"], data["height"])
        world.tiles = [Tile.from_dict(tile_data) for tile_data in data["tiles"]]
        return world

    def save(self, filepath: str):
        """Speichert die Welt als JSON"""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, filepath: str) -> "World":
        """Lädt eine Welt aus JSON"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)


class WorldGenerator:
    """Generiert zufällige Welten"""

    def __init__(self, tile_count: int = 3):
        self.tile_count = tile_count

    def generate(self, width: int, height: int) -> World:
        """Generiert eine neue zufällige Welt mit 75% Wahrscheinlichkeit für gleiche Nachbar-Tiles"""
        world = World(width, height)
        
        # Erstelle ein Grid für schnellen Zugriff
        grid = {}
        
        for y in range(height):
            for x in range(width):
                # Sammle alle bereits gesetzten Nachbarn (8 Richtungen)
                neighbors = []
                for dx, dy in [(-1, -1), (0, -1), (1, -1), (-1, 0)]:
                    nx, ny = x + dx, y + dy
                    if (nx, ny) in grid:
                        neighbors.append(grid[(nx, ny)])
                
                # 75% Wahrscheinlichkeit für gleichen Typ wie ein zufälliger Nachbar
                if neighbors and random.random() < 0.75:
                    tile_index = random.choice(neighbors)
                else:
                    tile_index = random.randint(0, self.tile_count - 1)
                
                # Speichere im Grid und World
                grid[(x, y)] = tile_index
                world.tiles.append(Tile(x, y, tile_index))

        return world


class Button:
    """Ein einfacher UI Button"""

    def __init__(self, x: int, y: int, width: int, height: int, text: str):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.hovered = False

    def draw(self, surface: pygame.Surface, font: pygame.font.Font):
        """Zeichnet den Button"""
        color = (100, 150, 100) if self.hovered else (80, 120, 80)
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 2)

        text_surface = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def is_clicked(self, pos: tuple) -> bool:
        """Prüft ob Button geklickt wurde"""
        return self.rect.collidepoint(pos)

    def update_hover(self, pos: tuple):
        """Updated Hover-Status"""
        self.hovered = self.rect.collidepoint(pos)


class Game:
    TILE_SIZE = 48
    WINDOW_WIDTH = 1600
    WINDOW_HEIGHT = 1200

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("World Generator")
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.Font(None, 24)

        # Berechne Welt-Größe basierend auf Tile-Größe
        self.world_width = self.WINDOW_WIDTH // self.TILE_SIZE
        self.world_height = self.WINDOW_HEIGHT // self.TILE_SIZE

        # Initialize managers
        self.sprite_manager = SpriteManager("graphics")
        self.world_generator = WorldGenerator(tile_count=3)
        self.world = self.world_generator.generate(self.world_width, self.world_height)

        # UI
        self.generate_button = Button(
            self.WINDOW_WIDTH - 220, 20, 200, 50, "Generate World"
        )

    def handle_events(self):
        """Verarbeitet Events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.generate_button.is_clicked(event.pos):
                    self.world = self.world_generator.generate(
                        self.world_width, self.world_height
                    )
                    self.world.save("world.json")
            elif event.type == pygame.MOUSEMOTION:
                self.generate_button.update_hover(event.pos)

    def draw(self):
        """Zeichnet das Spiel"""
        self.screen.fill((0, 0, 0))

        # Zeichne Welt-Tiles
        for tile in self.world.tiles:
            if 0 <= tile.tile_index < len(self.sprite_manager.tiles):
                sprite = self.sprite_manager.tiles[tile.tile_index]
                self.screen.blit(
                    sprite, (tile.x * self.TILE_SIZE, tile.y * self.TILE_SIZE)
                )

        # Zeichne UI
        self.generate_button.draw(self.screen, self.font)

        pygame.display.flip()

    def run(self):
        """Main Game Loop"""
        while self.running:
            self.handle_events()
            self.draw()
            self.clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()

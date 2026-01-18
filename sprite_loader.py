from __future__ import annotations

from pathlib import Path
import xml.etree.ElementTree as ET
import pygame


class SpriteAtlas:
    def __init__(self, image_path: Path, meta_path: Path) -> None:
        self._surface = pygame.image.load(str(image_path)).convert_alpha()
        self._rects = self._load_rects(meta_path)

    @staticmethod
    def _load_rects(meta_path: Path) -> dict[str, pygame.Rect]:
        tree = ET.parse(meta_path)
        root = tree.getroot()
        rects: dict[str, pygame.Rect] = {}
        for node in root.findall("SubTexture"):
            rects[node.attrib["name"]] = pygame.Rect(
                int(node.attrib["x"]),
                int(node.attrib["y"]),
                int(node.attrib["width"]),
                int(node.attrib["height"]),
            )
        return rects

    def sprite(self, name: str) -> pygame.Surface:
        rect = self._rects[name]
        return self._surface.subsurface(rect).copy()

    def rect(self, name: str) -> pygame.Rect:
        return self._rects[name].copy()

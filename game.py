from pathlib import Path

import pygame


class CharacterAnimator:
    ACTION_FILES = {
        "Walk": ("Walk.png", 12),
        "Attack": ("Attack2.png", 6),
        "Dialogue": ("Dialogue.png", 11),
    }

    def __init__(self, variant: str, *, scale: int = 3, frame_duration: float = 0.08) -> None:
        base_path = Path(__file__).parent / "sprites" / "schoolgirl" / variant
        self._scale = scale
        self._frame_duration = frame_duration
        self._sheets: dict[str, pygame.Surface] = {}
        self._default_frame_counts: dict[str, int] = {}
        for action, (filename, frame_count) in self.ACTION_FILES.items():
            image_path = base_path / filename
            self._sheets[action] = pygame.image.load(str(image_path)).convert_alpha()
            self._default_frame_counts[action] = frame_count

        self._frame_time = 0.0
        self._frame_index = 0
        self._current_action = "Walk"
        self._frames: list[pygame.Surface] = []
        self.set_animation("Walk")

    def _slice_frames(self, action: str, frame_count: int) -> list[pygame.Surface]:
        sheet = self._sheets[action]
        frame_width = sheet.get_width() // frame_count
        frame_height = sheet.get_height()
        frames: list[pygame.Surface] = []
        for i in range(frame_count):
            frame = sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height)).copy()
            if self._scale != 1:
                scaled_size = (frame_width * self._scale, frame_height * self._scale)
                frame = pygame.transform.smoothscale(frame, scaled_size)
            frames.append(frame)
        return frames

    def set_animation(self, action: str, frame_count: int | None = None) -> None:
        if action not in self._sheets:
            raise ValueError(f"Unknown action '{action}'")
        if frame_count is None:
            frame_count = self._default_frame_counts[action]
        if frame_count < 1:
            raise ValueError("frame_count must be positive")
        self._current_action = action
        self._frames = self._slice_frames(action, frame_count)
        self._frame_index = 0
        self._frame_time = 0.0

    def play_walk(self, frame_count: int | None = None) -> None:
        self.set_animation("Walk", frame_count)

    def play_attack(self, frame_count: int | None = None) -> None:
        self.set_animation("Attack", frame_count)

    def play_dialogue(self, frame_count: int | None = None) -> None:
        self.set_animation("Dialogue", frame_count)

    def update(self, dt: float) -> None:
        self._frame_time += dt
        if self._frame_time >= self._frame_duration:
            self._frame_time -= self._frame_duration
            self._frame_index = (self._frame_index + 1) % len(self._frames)

    def draw(self, surface: pygame.Surface, center: tuple[int, int]) -> None:
        current_frame = self._frames[self._frame_index]
        frame_rect = current_frame.get_rect(center=center)
        surface.blit(current_frame, frame_rect)

    @property
    def current_action(self) -> str:
        return self._current_action

    @property
    def frame_index(self) -> int:
        return self._frame_index

    @property
    def total_frames(self) -> int:
        return len(self._frames)


class Button:
    def __init__(self, label: str, rect: pygame.Rect, callback) -> None:
        self.label = label
        self.rect = rect
        self.callback = callback

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        color = (110, 110, 110) if self.rect.collidepoint(pygame.mouse.get_pos()) else (80, 80, 80)
        pygame.draw.rect(surface, color, self.rect, border_radius=6)
        pygame.draw.rect(surface, (40, 40, 40), self.rect, 2, border_radius=6)
        text_surface = font.render(self.label, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.callback()


pygame.init()
W, H = 1600, 900
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("My Game")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

CHARACTER_VARIANT = "Girl_1"
ATTACK_FRAMES = 8
DIALOGUE_FRAMES = 11

animator = CharacterAnimator(CHARACTER_VARIANT, scale=3)

buttons = [
    Button("Walk", pygame.Rect(20, 120, 140, 48), animator.play_walk),
    Button("Attack", pygame.Rect(180, 120, 140, 48), lambda: animator.play_attack(ATTACK_FRAMES)),
    Button("Dialogue", pygame.Rect(340, 120, 140, 48), lambda: animator.play_dialogue(DIALOGUE_FRAMES)),
]

running = True
while running:
    dt = clock.tick(60) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        for button in buttons:
            button.handle_event(event)

    animator.update(dt)

    screen.fill((30, 30, 30))
    animator.draw(screen, (W // 2, H // 2 + 80))

    dt_text = font.render(f"dt: {dt:.4f}s", True, (255, 255, 255))
    info_text = font.render(
        f"{animator.current_action} {animator.frame_index + 1}/{animator.total_frames}",
        True,
        (255, 255, 255),
    )
    screen.blit(dt_text, (20, 20))
    screen.blit(info_text, (20, 60))

    for button in buttons:
        button.draw(screen, font)

    pygame.display.flip()


pygame.quit()
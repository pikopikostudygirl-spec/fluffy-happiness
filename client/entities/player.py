import pygame
class Player:
    def __init__(self, x, y, color, name):
        self.x = float(x)
        self.y = float(y)
        self.width = 40
        self.height = 40
        self.speed = 4
        self.color = color
        self.name = name
        self.rect = pygame.Rect(
            int(self.x),
            int(self.y),
            self.width,
            self.height
        )
    def move(self, keys):
        dx = 0
        dy = 0
        if keys[pygame.K_w]:
            dy -= 1
        if keys[pygame.K_s]:
            dy += 1
        if keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_d]:
            dx += 1
        self._apply_movement(dx, dy)
    def move_with_arrows(self, keys):
        dx = 0
        dy = 0
        if keys[pygame.K_UP]:
            dy -= 1
        if keys[pygame.K_DOWN]:
            dy += 1
        if keys[pygame.K_LEFT]:
            dx -= 1
        if keys[pygame.K_RIGHT]:
            dx += 1
        self._apply_movement(dx, dy)
    def _apply_movement(self, dx, dy):
        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071
        self.x += dx * self.speed
        self.y += dy * self.speed
        self.rect.topleft = (round(self.x), round(self.y))
    def draw(self, screen):
        pygame.draw.rect(
            screen,
            self.color,
            self.rect,
            border_radius=8
        )
        font = pygame.font.Font(None, 24)
        label = font.render(
            self.name,
            True,
            (240, 245, 255)
        )
        screen.blit(
            label,
            label.get_rect(
                center=(self.rect.centerx, self.rect.top - 15)
            )
        )
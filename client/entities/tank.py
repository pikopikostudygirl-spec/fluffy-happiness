import math
import pygame
class Tank:
    def __init__(self, x, y, owner_id=None):
        self.x = float(x)
        self.y = float(y)
        self.width = 100
        self.height = 76
        self.speed = 180  # pixels per second
        self.owner_id = owner_id
        self.angle = 0.0
        self.track_color = (35, 40, 38)
        self.hull_color = (65, 100, 65)
        self.highlight_color = (105, 140, 90)
        self.turret_color = (75, 115, 70)
        self.rect = pygame.Rect(
            round(self.x),
            round(self.y),
            self.width,
            self.height,
        )
    @property
    def center(self):
        return pygame.Vector2(self.rect.center)
    def move(self, keys, dt):
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
        direction = pygame.Vector2(dx, dy)
        if direction.length_squared() > 0:
            direction = direction.normalize()
        self.x += direction.x * self.speed * dt
        self.y += direction.y * self.speed * dt
        self.rect.topleft = (
            round(self.x),
            round(self.y),
        )
    def aim_at(self, target_pos):
        direction = pygame.Vector2(target_pos) - self.center

        if direction.length_squared() > 0:
            self.angle = math.atan2(
                direction.y,
                direction.x,
            )
    def draw(self, screen, driver=None):
        x = self.rect.x
        y = self.rect.y
        pygame.draw.rect(
            screen,
            self.track_color,
            (x, y + 8, self.width, self.height - 16),
            border_radius=12,
        )
        for track_x in range(x + 8, x + self.width - 4, 12):
            pygame.draw.line(
                screen,
                (100, 105, 95),
                (track_x, y + 12),
                (track_x, y + self.height - 12),
                2,
            )
        hull = pygame.Rect(
            x + 10,
            y + 13,
            self.width - 20,
            self.height - 26,
        )
        pygame.draw.rect(
            screen,
            self.hull_color,
            hull,
            border_radius=10,
        )
        pygame.draw.rect(
            screen,
            self.highlight_color,
            hull,
            width=2,
            border_radius=10,
        )
        if driver is not None:
            driver.rect.centerx = self.rect.centerx
            driver.rect.bottom = self.rect.top + 39
            driver.x = float(driver.rect.x)
            driver.y = float(driver.rect.y)
            driver.draw(screen)
        turret_center = pygame.Vector2(
            self.rect.centerx,
            self.rect.centery,
        )
        barrel_length = 43
        barrel_end = turret_center + pygame.Vector2(
            math.cos(self.angle),
            math.sin(self.angle),
        ) * barrel_length
        pygame.draw.line(
            screen,
            (40, 50, 40),
            turret_center,
            barrel_end,
            12,
        )
        pygame.draw.line(
            screen,
            self.highlight_color,
            turret_center,
            barrel_end,
            6,
        )
        pygame.draw.circle(
            screen,
            self.turret_color,
            (round(turret_center.x), round(turret_center.y)),
            20,
        )
        pygame.draw.circle(
            screen,
            self.highlight_color,
            (round(turret_center.x), round(turret_center.y)),
            20,
            2,
        )
        pygame.draw.rect(
            screen,
            self.hull_color,
            (x + 20, y + 31, self.width - 40, 10),
            border_radius=4,
        )
        pygame.draw.line(
            screen,
            self.highlight_color,
            (x + 22, y + 31),
            (x + self.width - 22, y + 31),
            2,
        )
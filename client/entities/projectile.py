import math
import pygame
class Projectile:
    def __init__(self, start_pos, target_pos, owner_id, color):
        self.position = pygame.Vector2(start_pos)
        self.target = pygame.Vector2(target_pos)
        direction = self.target - self.position
        if direction.length_squared() > 0:
            direction = direction.normalize()
        else:
            direction = pygame.Vector2(1, 0)
        self.direction = direction
        self.owner_id = owner_id
        self.color = color
        self.speed = 500
        self.radius = 5
        self.max_range = 600
        self.distance_travelled = 0
        self.alive = True
    def update(self, dt):
        distance = self.speed * dt
        remaining_range = self.max_range - self.distance_travelled
        distance = min(distance, remaining_range)
        self.position += self.direction * distance
        self.distance_travelled += distance
        if self.distance_travelled >= self.max_range:
            self.alive = False
    def draw(self, screen):
        pygame.draw.circle(
            screen,
            self.color,
            (round(self.position.x), round(self.position.y)),
            self.radius + 2,
        )
        pygame.draw.circle(
            screen,
            (240, 245, 255),
            (round(self.position.x), round(self.position.y)),
            self.radius,
        )
    @property
    def rect(self):
        return pygame.Rect(
            round(self.position.x - self.radius),
            round(self.position.y - self.radius),
            self.radius * 2,
            self.radius * 2,
        )
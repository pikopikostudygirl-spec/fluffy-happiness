import pygame
import time
class Player:
    def __init__(self, x, y, color, name):
        self.x = float(x)
        self.y = float(y)
        self.width = 40
        self.height = 40
        self.base_speed = 4
        self.speed = self.base_speed
        self.color = color
        self.name = name
        self.rect = pygame.Rect(
            int(self.x),
            int(self.y),
            self.width,
            self.height
        )
        self.abilities = {}
        self.active_effects = {}
        self.cooldowns = {}
        self.base_damage = 10
        self.damage_multiplier = 1.0
        self.can_attack = True
        self.visible = True
    def register_ability(self, key, duration, cooldown):
        self.abilities[key] = {
            "duration": duration,
            "cooldown": cooldown
        }
        self.cooldowns[key] = 0
    def activate_ability(self, key):
        if key not in self.abilities:
            return False
        now = time.monotonic()
        if now < self.cooldowns[key]:
            return False
        config = self.abilities[key]
        self.active_effects[key] = now + config["duration"]
        self.cooldowns[key] = now + config["cooldown"]
        return True
    def update_abilities(self):
        now = time.monotonic()
        expired = [
            key
            for key, end_time in self.active_effects.items()
            if now >= end_time
        ]
        for key in expired:
            del self.active_effects[key]
        self.speed = self.base_speed
        self.damage_multiplier = 1.0
        self.can_attack = True
        self.visible = True
    def is_ability_active(self, key):
        return key in self.active_effects
    def cooldown_remaining(self, key):
        if key not in self.cooldowns:
            return 0
        return max(
            0,
            self.cooldowns[key] - time.monotonic()
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
        self.rect.topleft = (
            round(self.x),
            round(self.y)
        )
    def draw(self, screen):
        if not self.visible:
            return
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
                center=(
                    self.rect.centerx,
                    self.rect.top - 15
                )
            )
        )
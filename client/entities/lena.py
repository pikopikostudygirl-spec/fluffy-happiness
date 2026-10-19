import pygame
from client.entities.player import Player
class Lena(Player):
    def __init__(self, x, y):
        super().__init__(
            x=x,
            y=y,
            color=(210, 55, 65),
            name="Lena"
        )
        self.width = 44
        self.height = 76
        self.rect = pygame.Rect(
            int(x),
            int(y),
            self.width,
            self.height
        )
    def draw(self, screen):
        blonde = (245, 205, 95)
        blonde_shadow = (195, 145, 55)
        skin = (255, 224, 200)
        red = (205, 45, 60)
        blue = (55, 105, 210)
        dark_blue = (30, 55, 125)
        black = (35, 30, 35)
        x = self.rect.x
        y = self.rect.y
        pygame.draw.ellipse(
            screen,
            blonde_shadow,
            (x + 3, y + 5, 38, 34)
        )
        pygame.draw.rect(
            screen,
            blonde,
            (x + 5, y + 20, 7, 30),
            border_radius=4
        )
        pygame.draw.rect(
            screen,
            blonde,
            (x + 32, y + 20, 7, 30),
            border_radius=4
        )
        pygame.draw.rect(
            screen,
            skin,
            (x + 10, y + 53, 9, 17),
            border_radius=3
        )
        pygame.draw.rect(
            screen,
            skin,
            (x + 25, y + 53, 9, 17),
            border_radius=3
        )
        pygame.draw.ellipse(
            screen,
            black,
            (x + 7, y + 67, 14, 7)
        )
        pygame.draw.ellipse(
            screen,
            black,
            (x + 23, y + 67, 14, 7)
        )
        pygame.draw.rect(
            screen,
            blue,
            (x + 7, y + 43, 30, 14),
            border_radius=3
        )
        pygame.draw.line(
            screen,
            dark_blue,
            (x + 22, y + 46),
            (x + 22, y + 55),
            2
        )
        pygame.draw.rect(
            screen,
            skin,
            (x + 11, y + 22, 22, 24),
            border_radius=4
        )
        pygame.draw.rect(
            screen,
            red,
            (x + 8, y + 22, 28, 23),
            border_radius=5
        )
        pygame.draw.rect(
            screen,
            red,
            (x + 11, y + 17, 6, 10)
        )
        pygame.draw.rect(
            screen,
            red,
            (x + 27, y + 17, 6, 10)
        )
        pygame.draw.line(
            screen,
            skin,
            (x + 9, y + 27),
            (x + 5, y + 44),
            6
        )
        pygame.draw.line(
            screen,
            skin,
            (x + 35, y + 27),
            (x + 39, y + 44),
            6
        )
        pygame.draw.ellipse(
            screen,
            skin,
            (x + 11, y + 5, 22, 24)
        )
        curls = [
            (12, 9, 7),
            (19, 5, 8),
            (27, 9, 7),
            (10, 15, 7),
            (31, 15, 7),
            (12, 21, 6),
            (30, 22, 6),
        ]
        for cx, cy, radius in curls:
            pygame.draw.circle(
                screen,
                blonde,
                (x + cx, y + cy),
                radius
            )
        pygame.draw.circle(
            screen,
            (255, 230, 145),
            (x + 18, y + 7),
            3
        )
        pygame.draw.circle(
            screen,
            (55, 75, 105),
            (x + 17, y + 17),
            2
        )
        pygame.draw.circle(
            screen,
            (55, 75, 105),
            (x + 27, y + 17),
            2
        )
        pygame.draw.arc(
            screen,
            (150, 65, 65),
            (x + 18, y + 18, 9, 7),
            3.4,
            6.0,
            1
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
                center=(self.rect.centerx, y - 10)
            )
        )
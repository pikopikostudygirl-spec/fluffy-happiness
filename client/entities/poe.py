import pygame
from client.entities.player import Player
class Poe(Player):
    def __init__(self, x, y):
        super().__init__(
            x=x,
            y=y,
            color=(55, 105, 65),
            name="Poe"
        )
        self.width = 40
        self.height = 56
        self.rect = pygame.Rect(
            int(x),
            int(y),
            self.width,
            self.height
        )
    def draw(self, screen):
        # Color palette
        hair = (105, 67, 42)
        skin = (232, 190, 155)
        uniform = (55, 105, 65)
        dark_green = (35, 70, 43)
        black = (25, 28, 27)
        gold = (220, 185, 80)
        x = self.rect.x
        y = self.rect.y
        pygame.draw.rect(
            screen, black,
            (x + 8, y + 39, 9, 13)
        )
        pygame.draw.rect(
            screen, black,
            (x + 23, y + 39, 9, 13)
        )
        pygame.draw.rect(
            screen, uniform,
            (x + 5, y + 21, 30, 23),
            border_radius=4
        )
        pygame.draw.polygon(
            screen,
            (210, 215, 195),
            [
                (x + 15, y + 21),
                (x + 20, y + 28),
                (x + 25, y + 21)
            ]
        )
        pygame.draw.rect(
            screen, dark_green,
            (x + 3, y + 23, 7, 9)
        )
        pygame.draw.rect(
            screen, dark_green,
            (x + 30, y + 23, 7, 9)
        )
        for button_y in (30, 36):
            pygame.draw.circle(
                screen,
                gold,
                (x + 20, y + button_y),
                1
            )
        pygame.draw.ellipse(
            screen,
            skin,
            (x + 9, y + 4, 22, 23)
        )
        pygame.draw.ellipse(
            screen,
            hair,
            (x + 8, y + 1, 24, 15)
        )
        pygame.draw.polygon(
            screen,
            hair,
            [
                (x + 9, y + 8),
                (x + 14, y + 12),
                (x + 18, y + 7),
                (x + 23, y + 12),
                (x + 29, y + 7),
                (x + 31, y + 14),
                (x + 29, y + 18),
                (x + 10, y + 17)
            ]
        )
        pygame.draw.circle(
            screen, black,
            (x + 15, y + 17), 2
        )
        pygame.draw.circle(
            screen, black,
            (x + 25, y + 17), 2
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
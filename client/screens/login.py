import pygame
class LoginScreen:
    def __init__(self, screen):
        self.screen = screen
        self.username = ""
        self.password = ""
        self.active_field = "username"
        self.message = ""
        self.font = pygame.font.Font(None, 32)
        self.title_font = pygame.font.Font(None, 56)
        self.username_rect = pygame.Rect(400, 260, 400, 50)
        self.password_rect = pygame.Rect(400, 340, 400, 50)
        self.login_rect = pygame.Rect(400, 430, 190, 55)
        self.register_rect = pygame.Rect(610, 430, 190, 55)
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.username_rect.collidepoint(event.pos):
                self.active_field = "username"
            elif self.password_rect.collidepoint(event.pos):
                self.active_field = "password"
            elif self.login_rect.collidepoint(event.pos):
                return "login"
            elif self.register_rect.collidepoint(event.pos):
                return "register"
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:
                self.active_field = (
                    "password"
                    if self.active_field == "username"
                    else "username"
                )
            elif event.key == pygame.K_BACKSPACE:
                if self.active_field == "username":
                    self.username = self.username[:-1]
                else:
                    self.password = self.password[:-1]
            elif event.key == pygame.K_RETURN:
                return "login"
            elif event.unicode.isprintable():
                if self.active_field == "username":
                    if len(self.username) < 18:
                        self.username += event.unicode
                else:
                    if len(self.password) < 64:
                        self.password += event.unicode
        return None
    def draw(self):
        self.screen.fill((8, 10, 20))
        title = self.title_font.render(
            "BLUE NIGHT ARENA", True, (240, 245, 255)
        )
        self.screen.blit(
            title,
            title.get_rect(center=(600, 150))
        )
        self.draw_field(
            self.username_rect,
            "Username",
            self.username,
            "username"
        )
        self.draw_field(
            self.password_rect,
            "Password",
            "*" * len(self.password),
            "password"
        )
        self.draw_button(self.login_rect, "LOG IN")
        self.draw_button(self.register_rect, "REGISTER")
        if self.message:
            text = self.font.render(
                self.message, True, (255, 100, 100)
            )
            self.screen.blit(
                text,
                text.get_rect(center=(600, 520))
            )
    def draw_field(self, rect, label, value, field_name):
        color = (
            (35, 90, 180)
            if self.active_field == field_name
            else (70, 80, 110)
        )
        pygame.draw.rect(
            self.screen, color, rect, 2, border_radius=6
        )
        label_surface = self.font.render(
            label, True, (150, 160, 190)
        )
        self.screen.blit(
            label_surface, (rect.x, rect.y - 30)
        )
        value_surface = self.font.render(
            value, True, (240, 245, 255)
        )
        self.screen.blit(
            value_surface, (rect.x + 12, rect.y + 12)
        )
    def draw_button(self, rect, label):
        pygame.draw.rect(
            self.screen,
            (35, 90, 180),
            rect,
            border_radius=8
        )
        text = self.font.render(
            label, True, (240, 245, 255)
        )
        self.screen.blit(
            text,
            text.get_rect(center=rect.center)
        )
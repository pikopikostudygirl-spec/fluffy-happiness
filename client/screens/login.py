import pygame
import os
import sys
if getattr(sys, "frozen", False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..")
    )
class LoginScreen:
    def __init__(self, screen):
        self.screen = screen
        self.username = ""
        self.password = ""
        self.active_field = "username"
        self.message = ""
        self.language = "en"
        self.language_rect = pygame.Rect(950, 25, 200, 45)
        self.font = pygame.font.Font(
            os.path.join(BASE_DIR, "assets", "fonts", "NotoSansCJK-Regular.ttc"), 18
        )
        self.title_font = pygame.font.Font(
            os.path.join(BASE_DIR, "assets", "fonts", "NotoSansCJK-Regular.ttc"), 44
        )
        self.username_rect = pygame.Rect(400, 260, 400, 50)
        self.password_rect = pygame.Rect(400, 340, 400, 50)
        self.login_rect = pygame.Rect(400, 430, 190, 55)
        self.register_rect = pygame.Rect(610, 430, 190, 55)
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.language_rect.collidepoint(event.pos):
                self.language = "zh" if self.language == "en" else "en"
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
        game_title = (
            "蓝夜竞技场"
            if self.language == "zh"
            else "BLUE NIGHT ARENA"
        )
        title = self.title_font.render(
            game_title, True, (240, 245, 255)
        )
        language_label = (
            "Language: English"
            if self.language == "en"
            else "语言：中文"
        )
        self.draw_button(self.language_rect, language_label)
        self.screen.blit(
            title,
            title.get_rect(center=(600, 150))
        )
        if self.language == "zh":
            username_label = "用户名"
            password_label = "密码"
            login_label = "登录"
            register_label = "注册"
        else:
            username_label = "Username"
            password_label = "Password"
            login_label = "LOG IN"
            register_label = "REGISTER"
        self.draw_field(
            self.username_rect,
            username_label,
            self.username,
            "username"
        )
        self.draw_field(
            self.password_rect,
            password_label,
            "*" * len(self.password),
            "password"
        )
        self.draw_button(self.login_rect, login_label)
        self.draw_button(self.register_rect, register_label)
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
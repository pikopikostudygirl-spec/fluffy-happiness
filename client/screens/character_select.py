import os
import sys
import pygame
from client.entities.poe import Poe
from client.entities.lena import Lena
if getattr(sys, "frozen", False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..")
    )
FONT_PATH = os.path.join(
    BASE_DIR, "assets", "fonts", "NotoSansCJK-Regular.ttc"
)
CHARACTER_BIOS = {
    "Poe": {
        "age": "19",
        "profession": "Army Cadet",
        "likes": "Instant Noodles, Onesies",
        "dislikes": "Situations That Are Not Under Control",
        "backstory": (
            "Poe's mother died following the birth of his now-deceased "
            "little brother, Rick. As a result of that, he was forced to "
            "live with his gaming-addicted father. Due to his father's "
            "neglect, he was forced to devour the only person he has left "
            "and as a result of this crime, he was placed in the system. "
            "His childish heart was filled with hatred and violence, and "
            "he became fascinated with military paraphernalia. Now, he's "
            "seeking comfort on the frontlines of Blue Night Arena when "
            "he's off-duty."
        ),
    },
    "Lena": {
        "age": "25",
        "profession": "Idol",
        "likes": "Gacha Machines",
        "dislikes": "Tennis",
        "backstory": (
            "Lena's father was a gachikoi, meaning he believed he was in "
            "love with an idol. Her mother, unable to handle that, left "
            "little Lena in his care. One day, Mr. Rogers got turned "
            "down by his favorite idol and made the decision to turn "
            "his daughter into the idol who would love him ALWAYS and "
            "FOREVER </3."
        ),
    },
}
CHARACTER_BIOS_ZH = {
    "Poe": {
        "age": "19岁",
        "profession": "陆军学员",
        "likes": "方便面、连体睡衣",
        "dislikes": "无法掌控的局面",
        "backstory": (
            "波伊的母亲在生下他后来去世的弟弟里克后不久便去世了。"
            "此后，他被迫与沉迷游戏的父亲一起生活。"
            "由于父亲长期疏于照顾，他最终被迫吞噬了自己仅剩的亲人。"
            "由于这起罪行，他被送进了福利机构。"
            "他那颗稚嫩的心逐渐充满了仇恨与暴力，"
            "并对各种军事装备产生了浓厚的兴趣。"
            "如今，休假时的他会来到蓝夜竞技场的前线寻找慰藉。"
        ),
    },
    "Lena": {
        "age": "25岁",
        "profession": "偶像",
        "likes": "扭蛋机",
        "dislikes": "网球",
        "backstory": (
            "莉娜的父亲是一个痴迷偶像的人，也就是所谓的嘎其恋。"
            "他坚信自己真的爱上了某位偶像。"
            "她的母亲无法忍受这一切，最终离开了，把年幼的莉娜留给了他。"
            "有一天，罗衰斯被自己最喜欢的偶像拒绝了。"
            "于是，他决定把自己的女儿培养成偶像，"
            "让她永远永远地爱着自己。</3"
        ),
    },
}
CHARACTER_NAMES_ZH = {
    "Poe": "波伊",
    "Lena": "莉娜",
}
class CharacterSelect:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.language = "en"
        self.selected_character = "Poe"
        self.viewing_bio = None
        self.poe_rect = pygame.Rect(
            self.width // 2 - 280, 230, 220, 250
        )
        self.lena_rect = pygame.Rect(
            self.width // 2 + 60, 230, 220, 250
        )
        self.poe_bio_rect = pygame.Rect(
            self.poe_rect.centerx - 55,
            self.poe_rect.bottom - 42,
            110,
            30,
        )
        self.lena_bio_rect = pygame.Rect(
            self.lena_rect.centerx - 55,
            self.lena_rect.bottom - 42,
            110,
            30,
        )
        self.start_rect = pygame.Rect(
            self.width // 2 - 100, 550, 200, 55
        )
        self.back_rect = pygame.Rect(40, 40, 120, 45)
        self.title_font = pygame.font.Font(FONT_PATH, 44)
        self.name_font = pygame.font.Font(FONT_PATH, 32)
        self.info_font = pygame.font.Font(FONT_PATH, 23)
        self.bio_font = pygame.font.Font(FONT_PATH, 23)
        self.small_font = pygame.font.Font(FONT_PATH, 19)
    def handle_event(self, event):
        if self.viewing_bio is not None:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.back_rect.collidepoint(event.pos):
                    self.viewing_bio = None
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                    self.viewing_bio = None
            return None
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.poe_bio_rect.collidepoint(event.pos):
                self.viewing_bio = "Poe"
            elif self.lena_bio_rect.collidepoint(event.pos):
                self.viewing_bio = "Lena"
            elif self.poe_rect.collidepoint(event.pos):
                self.selected_character = "Poe"
            elif self.lena_rect.collidepoint(event.pos):
                self.selected_character = "Lena"
            elif self.start_rect.collidepoint(event.pos):
                return self.selected_character
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.selected_character = "Poe"
            elif event.key == pygame.K_RIGHT:
                self.selected_character = "Lena"
            elif event.key == pygame.K_RETURN:
                return self.selected_character
        return None
    def draw(self):
        if self.viewing_bio is not None:
            self._draw_bio_screen()
        else:
            self._draw_selection_screen()
    def _draw_selection_screen(self):
        self.screen.fill((8, 10, 20))
        title_text = (
            "选择你的角色"
            if self.language == "zh"
            else "CHOOSE YOUR CHARACTER"
        )
        title = self.title_font.render(
            title_text, True, (240, 245, 255)
        )
        self.screen.blit(
            title,
            title.get_rect(center=(self.width // 2, 110)),
        )
        self._draw_character_card(
            self.poe_rect,
            "Poe",
            self.selected_character == "Poe",
        )
        self._draw_character_card(
            self.lena_rect,
            "Lena",
            self.selected_character == "Lena",
        )
        instructions_text = (
            "点击角色或使用左右方向键"
            if self.language == "zh"
            else "Click a character or use LEFT / RIGHT"
        )
        instructions = self.info_font.render(
            instructions_text, True, (180, 190, 210)
        )
        self.screen.blit(
            instructions,
            instructions.get_rect(
                center=(self.width // 2, 510)
            ),
        )
        pygame.draw.rect(
            self.screen,
            (35, 90, 180),
            self.start_rect,
            border_radius=10,
        )
        start_label = "开始" if self.language == "zh" else "START"
        start_text = self.name_font.render(
            start_label, True, (255, 255, 255)
        )
        self.screen.blit(
            start_text,
            start_text.get_rect(center=self.start_rect.center),
        )
    def _draw_character_card(self, rect, name, selected):
        background = (18, 28, 50)
        border_color = (
            (70, 160, 255)
            if selected
            else (55, 65, 90)
        )
        pygame.draw.rect(
            self.screen,
            background,
            rect,
            border_radius=12,
        )
        pygame.draw.rect(
            self.screen,
            border_color,
            rect,
            width=4 if selected else 2,
            border_radius=12,
        )
        center_x = rect.centerx
        center_y = rect.y + 105
        if name == "Poe":
            preview = Poe(center_x - 20, center_y - 28)
            bio_rect = self.poe_bio_rect
        else:
            preview = Lena(center_x - 22, center_y - 38)
            bio_rect = self.lena_bio_rect
        preview.draw(self.screen)
        display_name = (
            CHARACTER_NAMES_ZH[name]
            if self.language == "zh"
            else name
        )
        name_text = self.name_font.render(
            display_name, True, (240, 245, 255)
        )
        self.screen.blit(
            name_text,
            name_text.get_rect(
                center=(rect.centerx, rect.bottom - 72)
            ),
        )
        pygame.draw.rect(
            self.screen,
            (25, 65, 105),
            bio_rect,
            border_radius=7,
        )
        pygame.draw.rect(
            self.screen,
            (70, 145, 210),
            bio_rect,
            width=1,
            border_radius=7,
        )
        bio_label = "简介" if self.language == "zh" else "BIO"
        bio_text = self.small_font.render(
            bio_label, True, (240, 245, 255)
        )
        self.screen.blit(
            bio_text,
            bio_text.get_rect(center=bio_rect.center),
        )
    def _draw_bio_screen(self):
        self.screen.fill((8, 10, 20))
        character_name = self.viewing_bio
        data = (
            CHARACTER_BIOS_ZH[character_name]
            if self.language == "zh"
            else CHARACTER_BIOS[character_name]
        )
        accent = (
            (90, 175, 115)
            if character_name == "Poe"
            else (235, 100, 125)
        )
        panel = pygame.Rect(
            100, 110, self.width - 200, 550
        )
        pygame.draw.rect(
            self.screen,
            (18, 28, 50),
            panel,
            border_radius=16,
        )
        pygame.draw.rect(
            self.screen,
            accent,
            panel,
            width=3,
            border_radius=16,
        )
        pygame.draw.rect(
            self.screen,
            (30, 45, 70),
            self.back_rect,
            border_radius=8,
        )
        back_label = "< 返回" if self.language == "zh" else "< BACK"
        back_text = self.info_font.render(
            back_label, True, (240, 245, 255)
        )
        self.screen.blit(
            back_text,
            back_text.get_rect(center=self.back_rect.center),
        )
        display_name = (
            CHARACTER_NAMES_ZH[character_name]
            if self.language == "zh"
            else character_name.upper()
        )
        name_text = self.title_font.render(
            display_name, True, accent
        )
        self.screen.blit(name_text, (140, 135))
        subtitle_text = (
            f'{data["age"]}  |  {data["profession"]}'
            if self.language == "zh"
            else f'{data["age"]} years old  |  {data["profession"]}'
        )
        subtitle = self.info_font.render(
            subtitle_text, True, (210, 220, 240)
        )
        self.screen.blit(subtitle, (143, 195))
        likes_heading = "喜欢" if self.language == "zh" else "LIKES"
        likes_label = self.info_font.render(
            likes_heading, True, accent
        )
        self.screen.blit(likes_label, (143, 245))
        likes_text = self.info_font.render(
            data["likes"], True, (240, 245, 255)
        )
        self.screen.blit(likes_text, (143, 272))
        dislikes_heading = (
            "不喜欢"
            if self.language == "zh"
            else "DISLIKES"
        )
        dislikes_label = self.info_font.render(
            dislikes_heading, True, accent
        )
        self.screen.blit(dislikes_label, (143, 315))
        dislikes_text = self.info_font.render(
            data["dislikes"], True, (240, 245, 255)
        )
        self.screen.blit(dislikes_text, (143, 342))

        story_heading = (
            "背景故事"
            if self.language == "zh"
            else "BACKSTORY"
        )
        story_label = self.info_font.render(
            story_heading, True, accent
        )
        self.screen.blit(story_label, (143, 390))
        story_lines = self._wrap_text(
            data["backstory"],
            self.bio_font,
            self.width - 300,
        )
        y = 425
        line_height = 31
        for line in story_lines:
            if y + line_height > panel.bottom - 20:
                break

            text_surface = self.bio_font.render(
                line, True, (225, 232, 245)
            )

            self.screen.blit(text_surface, (143, y))
            y += line_height

        footer_text = (
            "按 ESC 键或点击返回以回到角色选择界面"
            if self.language == "zh"
            else "Press ESC or BACK to return to character selection"
        )
        footer = self.small_font.render(
            footer_text, True, (155, 170, 195)
        )
        self.screen.blit(
            footer,
            footer.get_rect(
                center=(self.width // 2, 690)
            ),
        )
    def _wrap_text(self, text, font, max_width):
        lines = []
        current_line = ""
        for character in text:
            test_line = current_line + character
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = character
        if current_line:
            lines.append(current_line)
        return lines
import pygame
import os
import sys
from client.entities.poe import Poe
from client.entities.lena import Lena
from client.screens.character_select import CharacterSelect
from client.network import NetworkClient
from client.entities.tank import Tank
from client.screens.login import LoginScreen
pygame.init()
WIDTH = 1280
HEIGHT = 720
FPS = 60
BLACK = (8, 10, 20)
DARK_BLUE = (12, 20, 45)
BLUE = (35, 90, 180)
WHITE = (240, 245, 255)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Blue Night Arena")
clock = pygame.time.Clock()
if getattr(sys, "frozen", False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(
    BASE_DIR,
    "assets",
    "fonts",
    "NotoSansCJK-Regular.ttc"
)
title_font = pygame.font.Font(FONT_PATH, 56)
subtitle_font = pygame.font.Font(FONT_PATH, 28)
chat_font = pygame.font.Font(FONT_PATH, 20)
game_state = "login"
login_screen = LoginScreen(screen)
character_select = CharacterSelect(screen)
player = None
tank = None
pending_character = None
network = NetworkClient()
chat_active = False
chat_input = ""
scoreboard_visible = False
ARENA_LEFT = 80
ARENA_TOP = 100
ARENA_RIGHT = 1200
ARENA_BOTTOM = 640
WALLS = [
    pygame.Rect(250, 180, 220, 25),
    pygame.Rect(650, 180, 220, 25),
    pygame.Rect(450, 300, 300, 25),
    pygame.Rect(250, 450, 25, 120),
    pygame.Rect(1000, 350, 25, 150),
]
HUD_TRANSLATIONS = {
    "BLUE NIGHT ARENA": "蓝夜竞技场",
    "DEFECT, GI!": "缺陷士兵！",
    "MANIPULATE": "操纵",
    "BINAURAL BEATS": "双耳节拍",
    "RAPID FIRE ACTIVE": "快速射击已激活",
    "❄ FREEZE": "❄ 冰冻",
    "WASD: Move | Left Click: Shoot": "WASD：移动 | 左键：射击",
    "ONLINE": "在线",
    "DISCONNECTED": "连接断开",
    "CONNECTING": "连接中",
    "ESC: Character Select": "ESC：返回角色选择",
    "GLOBAL CHAT": "全球聊天",
    "Press T to chat": "按 T 键聊天",
}
def hud_text(text):
    if login_screen.language == "zh":
        return HUD_TRANSLATIONS.get(text, text)
    return text
character_select.language = login_screen.language
def create_player(character_name):
    if character_name == "Poe":
        return Poe(350, 330)
    if character_name == "Lena":
        return Lena(350, 330)
    return None
def draw_health_bar(surface, x, y, health, max_health=500):
    bar_width = 100
    bar_height = 10
    health = max(0, min(health, max_health))
    fill_width = int(bar_width * health / max_health)
    background_rect = pygame.Rect(
        int(x), int(y), bar_width, bar_height
    )
    health_rect = pygame.Rect(
        int(x), int(y), fill_width, bar_height
    )
    pygame.draw.rect(
        surface, (70, 20, 30), background_rect
    )
    pygame.draw.rect(
        surface, (70, 220, 110), health_rect
    )
    pygame.draw.rect(
        surface, WHITE, background_rect, 1
    )
if scoreboard_visible:
    panel_width = 760
    panel_height = 430

    panel = pygame.Surface(
        (panel_width, panel_height),
        pygame.SRCALPHA
    )
    panel.fill((5, 10, 25, 235))
    pygame.draw.rect(
        panel,
        BLUE,
        panel.get_rect(),
        2,
        border_radius=12
    )
    title = subtitle_font.render(
        "SCOREBOARD",
        True,
        WHITE
    )
    panel.blit(
        title,
        title.get_rect(center=(panel_width // 2, 35))
    )
    columns = [
        ("PLAYER", 30),
        ("CHARACTER", 260),
        ("KILLS", 460),
        ("DEATHS", 550),
        ("K/D", 650),
    ]
    for label, x in columns:
        text = chat_font.render(label, True, BLUE)
        panel.blit(text, (x, 85))
    sorted_players = sorted(
        server_players.items(),
        key=lambda item: (
            -item[1].get("kills", 0),
            item[1].get("deaths", 0)
        )
    )
    for index, (pid, data) in enumerate(sorted_players[:10]):
        y = 125 + index * 28

        kills = data.get("kills", 0)
        deaths = data.get("deaths", 0)
        kd = kills / max(deaths, 1)

        values = [
            (data.get("name", "Unknown"), 30),
            (data.get("character", "Unknown"), 260),
            (str(kills), 460),
            (str(deaths), 550),
            (f"{kd:.2f}", 650),
        ]
        for value, x in values:
            text = chat_font.render(
                value,
                True,
                WHITE
            )
            panel.blit(text, (x, y))
    screen.blit(
        panel,
        (
            (WIDTH - panel_width) // 2,
            (HEIGHT - panel_height) // 2
        )
    )
def draw_chat():
    chat_panel = pygame.Surface(
        (440, 200),
        pygame.SRCALPHA
    )
    chat_panel.fill((5, 10, 25, 220))
    screen.blit(chat_panel, (90, 425))
    pygame.draw.rect(
        screen,
        BLUE,
        (90, 425, 440, 200),
        2
    )
    chat_title = chat_font.render(
        hud_text("GLOBAL CHAT"),
        True,
        WHITE
    )
    screen.blit(chat_title, (105, 435))
    messages = network.get_chat_messages()[-6:]
    if messages:
        print("CHAT DISPLAY DATA:", messages[-1])
    for index, message in enumerate(messages):
        username = str(message.get("username", "Unknown"))
        content = str(message.get("message", ""))
        text = f"{username}: {content}"
        rendered = chat_font.render(
            text,
            True,
            WHITE
        )
        if rendered.get_width() > 405:
            while text and chat_font.size(text + "...")[0] > 405:
                text = text[:-1]
            text += "..."
            rendered = chat_font.render(
                text,
                True,
                WHITE
            )
        screen.blit(
            rendered,
            (105, 465 + index * 23)
        )
    if chat_active:
        input_text = chat_font.render(
            "> " + chat_input + "|",
            True,
            WHITE
        )
    else:
        input_text = chat_font.render(
            hud_text("Press T to chat"),
            True,
            (150, 170, 200)
        )
    screen.blit(input_text, (105, 600))
def draw_local_abilities(my_data, invisible):
    if tank is None or player is None or invisible:
        return
    if player.name == "Lena":
        active_abilities = []
        if my_data.get("defect_gi_active", False):
            active_abilities.append(hud_text("DEFECT, GI!"))
        if my_data.get("manipulate_active", False):
            active_abilities.append(hud_text("MANIPULATE"))
        if my_data.get("binaural_beats_active", False):
            active_abilities.append(hud_text("BINAURAL BEATS"))
        if active_abilities:
            ability_text = subtitle_font.render(
                " | ".join(active_abilities),
                True,
                (255, 130, 170)
            )
            screen.blit(
                ability_text,
                (
                    tank.rect.centerx
                    - ability_text.get_width() // 2,
                    tank.rect.top - 45
                )
            )
    if my_data.get("neetdom_active", False):
        pygame.draw.circle(
            screen,
            (80, 200, 255),
            tank.rect.center,
            65,
            3
        )
    if my_data.get("rapid_fire_active", False):
        rapid_text = subtitle_font.render(
            hud_text("RAPID FIRE ACTIVE"),
            True,
            (255, 190, 70)
        )
        screen.blit(
            rapid_text,
            (
                tank.rect.centerx - rapid_text.get_width() // 2,
                tank.rect.top - 45
            )
        )
def draw_remote_player(other_id, data, my_player_id):
    if other_id == my_player_id:
        return
    if data.get("character") == "Poe":
        other_player = Poe(data["x"], data["y"])
    elif data.get("character") == "Lena":
        other_player = Lena(data["x"], data["y"])
    else:
        return
    other_player.name = data.get("name", "Unknown")
    other_player.rect.topleft = (
        round(data["x"]),
        round(data["y"])
    )
    invisible = (
        data.get("character") == "Poe"
        and data.get("social_anxiety_active", False)
    )
    if invisible:
        return
    other_player.draw(screen)
    if data.get("frozen", False):
        freeze_text = subtitle_font.render(
            hud_text("❄ FREEZE"),
            True,
            (100, 200, 255)
        )
        screen.blit(
            freeze_text,
            (
                other_player.rect.centerx
                - freeze_text.get_width() // 2,
                other_player.rect.top - 45
            )
        )
    if data.get("character") == "Lena":
        active_abilities = []
        if data.get("defect_gi_active", False):
            active_abilities.append(hud_text("DEFECT, GI!"))
        if data.get("manipulate_active", False):
            active_abilities.append(hud_text("MANIPULATE"))
        if data.get("binaural_beats_active", False):
            active_abilities.append(hud_text("BINAURAL BEATS"))
        if active_abilities:
            ability_text = subtitle_font.render(
                " | ".join(active_abilities),
                True,
                (255, 130, 170)
            )
            screen.blit(
                ability_text,
                (
                    other_player.rect.centerx
                    - ability_text.get_width() // 2,
                    other_player.rect.top - 45
                )
            )
    if data.get("neetdom_active", False):
        pygame.draw.circle(
            screen,
            (80, 200, 255),
            other_player.rect.center,
            65,
            3
        )
    if data.get("rapid_fire_active", False):
        rapid_text = subtitle_font.render(
            hud_text("RAPID FIRE ACTIVE"),
            True,
            (255, 190, 70)
        )
        screen.blit(
            rapid_text,
            (
                other_player.rect.centerx
                - rapid_text.get_width() // 2,
                other_player.rect.top - 45
            )
        )
    draw_health_bar(
        screen,
        round(data["x"] + 50),
        round(data["y"] - 15),
        data.get("health", 500)
    )
running = True
while running:
    dt = clock.tick(FPS) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            continue
        if game_state == "login":
            action = login_screen.handle_event(event)
            if action in ("login", "register"):
                network.connect(
                    login_screen.username,
                    login_screen.password,
                    action
                )
            continue
        if game_state == "character_select":
            selected = character_select.handle_event(event)
            if selected is not None:
                pending_character = selected
                network.join_character(selected)
            continue
        if game_state == "arena":
            if event.type == pygame.TEXTINPUT and chat_active:
                chat_input = (
                    chat_input + event.text
                )[:200]
                continue
            if event.type == pygame.KEYDOWN:
                if chat_active:
                    if event.key == pygame.K_TAB:
                        scoreboard_visible = not scoreboard_visible
                        continue
                    if event.key == pygame.K_RETURN:
                        network.send_chat(chat_input)
                        chat_input = ""
                        chat_active = False
                        pygame.key.stop_text_input()
                    elif event.key == pygame.K_ESCAPE:
                        chat_input = ""
                        chat_active = False
                        pygame.key.stop_text_input()
                    elif event.key == pygame.K_BACKSPACE:
                        chat_input = chat_input[:-1]
                    continue
                if event.key == pygame.K_t:
                    chat_active = True
                    pygame.key.start_text_input()
                    continue
                if event.key == pygame.K_ESCAPE:
                    game_state = "character_select"
                    continue
                if player is not None and player.name == "Poe":
                    if event.key == pygame.K_q:
                        network.activate_ability("neetdom")
                    elif event.key == pygame.K_e:
                        network.activate_ability("rapid_fire")
                    elif event.key == pygame.K_x:
                        network.activate_ability("social_anxiety")
                    elif event.key == pygame.K_r:
                        network.activate_ability("kamikaze")
                elif player is not None and player.name == "Lena":
                    if event.key == pygame.K_q:
                        network.activate_ability("defect_gi")
                    elif event.key == pygame.K_e:
                        network.activate_ability("manipulate")
                    elif event.key == pygame.K_x:
                        network.activate_ability("binaural_beats")
                    elif event.key == pygame.K_r:
                        network.activate_ability("freeze")
            if (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and not chat_active
            ):
                if player is not None and network.connected:
                    network.fire(
                        event.pos[0],
                        event.pos[1]
                    )
    if not running:
        break
    if game_state == "login" and network.auth_complete:
        translations = {
            "Login successful.": "登录成功。",
            "Invalid username or password.": "用户名或密码错误。",
            "Invalid authentication request.": "无效的身份验证请求。",
            "Username must be 3–18 characters.": "用户名必须为3至18个字符。",
            "Password must be 8–64 characters.": "密码必须为8至64个字符。",
            "Username can only contain letters and numbers.": "用户名只能包含字母和数字。",
            "Account created successfully.": "账户创建成功。",
            "Username already exists.": "用户名已存在。",
            "Invalid server response.": "服务器响应无效。"
        }
        if network.auth_success:
            game_state = "character_select"
            login_screen.message = (
                "登录成功。"
                if login_screen.language == "zh"
                else "Login successful!"
            )
        else:
            message = network.auth_message
            if login_screen.language == "zh":
                message = translations.get(message, message)
            login_screen.message = message
            network.auth_complete = False
    server_players = network.get_players()
    my_player_id = network.player_id
    if server_players:
        print("MY ID:", my_player_id)
        print("SERVER PLAYERS:", {
            pid: (data.get("name"), data.get("character"))
            for pid, data in server_players.items()
        })
    if (
        game_state == "character_select"
        and pending_character is not None
        and network.connected
        and my_player_id is not None
        and player is None
    ):
        new_player = create_player(pending_character)
        if new_player is not None:
            player = new_player
            tank = Tank(
                350,
                330,
                owner_id=my_player_id
            )
            pending_character = None
            game_state = "arena"
    if game_state == "arena" and player is not None and tank is not None:
        keys = pygame.key.get_pressed()
        if not chat_active:
            network.send_input(
                up=keys[pygame.K_w],
                down=keys[pygame.K_s],
                left=keys[pygame.K_a],
                right=keys[pygame.K_d]
            )
        else:
            network.send_input(
                up=False,
                down=False,
                left=False,
                right=False
            )
        if network.connected and my_player_id in server_players:
            my_data = server_players[my_player_id]
            tank.x = my_data["x"]
            tank.y = my_data["y"]
            tank.rect.topleft = (
                round(tank.x),
                round(tank.y)
            )
        player.rect.centerx = tank.rect.centerx
        player.rect.bottom = tank.rect.top + 39
        player.x = float(player.rect.x)
        player.y = float(player.rect.y)
        tank.aim_at(pygame.mouse.get_pos())
    if game_state == "login":
        login_screen.draw()
    elif game_state == "character_select":
        character_select.language = login_screen.language
        character_select.draw()
    elif game_state == "arena":
        screen.fill(BLACK)
        arena = pygame.Rect(
            ARENA_LEFT,
            ARENA_TOP,
            ARENA_RIGHT - ARENA_LEFT,
            ARENA_BOTTOM - ARENA_TOP
        )
        pygame.draw.rect(
            screen,
            DARK_BLUE,
            arena,
            border_radius=16
        )
        pygame.draw.rect(
            screen,
            BLUE,
            arena,
            width=2,
            border_radius=16
        )
        for wall in WALLS:
            pygame.draw.rect(
                screen,
                (55, 75, 110),
                wall,
                border_radius=5
            )
            pygame.draw.rect(
                screen,
                (90, 140, 210),
                wall,
                width=2,
                border_radius=5
            )
        title = title_font.render(
            hud_text("BLUE NIGHT ARENA"),
            True,
            WHITE
        )
        screen.blit(
            title,
            title.get_rect(center=(WIDTH // 2, 45))
        )
        my_data = server_players.get(my_player_id, {})
        local_invisible = (
            player is not None
            and player.name == "Poe"
            and my_data.get("social_anxiety_active", False)
        )
        if tank is not None and player is not None:
            if not local_invisible:
                tank.draw(screen, driver=player)
            draw_local_abilities(
                my_data,
                local_invisible
            )
            if (
                network.connected
                and my_player_id in server_players
                and not local_invisible
            ):
                draw_health_bar(
                    screen,
                    player.rect.centerx - 50,
                    player.rect.top - 15,
                    my_data.get("health", 500)
                )
        for projectile in network.get_projectiles():
            position = (
                round(projectile["x"]),
                round(projectile["y"])
            )
            color = tuple(projectile["color"])
            pygame.draw.circle(
                screen,
                color,
                position,
                7
            )
            pygame.draw.circle(
                screen,
                (240, 245, 255),
                position,
                5
            )
        for explosion in network.get_explosions():
            position = (
                round(explosion["x"]),
                round(explosion["y"])
            )
            radius = round(explosion["radius"])
            pygame.draw.circle(
                screen,
                (255, 100, 30),
                position,
                radius,
                5
            )
            pygame.draw.circle(
                screen,
                (255, 220, 100),
                position,
                max(1, radius // 2),
                3
            )
        for other_id, data in server_players.items():
            draw_remote_player(
                other_id,
                data,
                my_player_id
            )
        controls = hud_text(
            "WASD: Move | Left Click: Shoot"
        )
        if network.connected:
            connection_status = hud_text("ONLINE")
        elif network.error:
            connection_status = hud_text("DISCONNECTED")
        else:
            connection_status = hud_text("CONNECTING")
        if player is not None:
            if login_screen.language == "zh":
                player_name = {
                    "Poe": "波伊",
                    "Lena": "莉娜"
                }.get(player.name, player.name)
                subtitle_text = (
                    f"使用角色：{player_name} | {controls} | "
                    f"{connection_status} | ESC：返回角色选择"
                )
            else:
                subtitle_text = (
                    f"Playing as {player.name} | {controls} | "
                    f"{connection_status} | ESC: Character Select"
                )
            subtitle = subtitle_font.render(
                subtitle_text,
                True,
                WHITE
            )
            screen.blit(
                subtitle,
                (95, 655)
            )
        draw_chat()
    pygame.display.flip()
pygame.key.stop_text_input()
pygame.quit()
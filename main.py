import pygame
import sys
from client.entities.poe import Poe
from client.entities.lena import Lena
from client.screens.character_select import CharacterSelect
from client.network import NetworkClient
from client.entities.projectile import Projectile
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
title_font = pygame.font.Font(None, 56)
subtitle_font = pygame.font.Font(None, 28)
game_state = "login"
character_select = CharacterSelect(screen)
login_screen = LoginScreen(screen)
player = None
tank = None
pending_character = None
network = NetworkClient()
projectiles = []
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
def create_player(character_name):
    if character_name == "Poe":
        return Poe(350, 330)
    return Lena(350, 330)
running = True
while running:
    dt = clock.tick(FPS) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif game_state == "login":
            action = login_screen.handle_event(event)
            if action in ("login", "register"):
                network.connect(
                    login_screen.username,
                    login_screen.password,
                    action,
                )
        elif game_state == "character_select":
            selected = character_select.handle_event(event)
            if selected is not None:
                pending_character = selected
                network.join_character(selected)
        elif game_state == "arena":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if player is not None and network.connected:
                    network.fire(event.pos[0], event.pos[1])
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_state = "character_select"
                elif player is not None and player.name == "Poe":
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
    if not running:
        break
    if game_state == "login" and network.auth_complete:
        if network.auth_success:
            game_state = "character_select"
            login_screen.message = "Login successful!"
        else:
            login_screen.message = network.auth_message
            network.auth_complete = False
    server_players = network.get_players()
    my_player_id = network.player_id
    if (
            game_state == "character_select"
            and pending_character is not None
            and network.connected
            and network.player_id is not None
    ):
        player = create_player(pending_character)
        tank = Tank(350, 330, owner_id=network.player_id)
        pending_character = None
        game_state = "arena"
    if game_state == "arena" and player is not None:
        keys = pygame.key.get_pressed()
        network.send_input(
            up=keys[pygame.K_w],
            down=keys[pygame.K_s],
            left=keys[pygame.K_a],
            right=keys[pygame.K_d],
        )
        if network.connected and my_player_id in server_players:
            my_data = server_players[my_player_id]
            tank.x = my_data["x"]
            tank.y = my_data["y"]
            tank.rect.topleft = (
                round(tank.x),
                round(tank.y),
            )
        player.rect.centerx = tank.rect.centerx
        player.rect.bottom = tank.rect.top + 39
        player.x = float(player.rect.x)
        player.y = float(player.rect.y)
        tank.aim_at(pygame.mouse.get_pos())
    if game_state == "login":
        login_screen.draw()
    elif game_state == "character_select":
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
            screen, DARK_BLUE, arena, border_radius=16
        )
        pygame.draw.rect(
            screen, BLUE, arena, width=2, border_radius=16
        )
        for wall in WALLS:
            pygame.draw.rect(
                screen, (55, 75, 110), wall, border_radius=5
            )
            pygame.draw.rect(
                screen, (90, 140, 210),
                wall, width=2, border_radius=5
            )
        title = title_font.render(
            "BLUE NIGHT ARENA", True, WHITE
        )
        screen.blit(
            title,
            title.get_rect(center=(WIDTH // 2, 45))
        )
        if tank is not None and player is not None:
            my_data = server_players.get(my_player_id, {})

            invisible = (
                    player.name == "Poe"
                    and my_data.get("social_anxiety_active", False)
            )
            if not invisible:
                tank.draw(screen, driver=player)
            if player.name == "Lena":
                active_abilities = []
                if my_data.get("defect_gi_active", False):
                    active_abilities.append("DEFECT, GI!")
                if my_data.get("manipulate_active", False):
                    active_abilities.append("MANIPULATE")
                if my_data.get("binaural_beats_active", False):
                    active_abilities.append("BINAURAL BEATS")
                if active_abilities:
                    ability_text = subtitle_font.render(
                        " | ".join(active_abilities),
                        True,
                        (255, 130, 170),
                    )
                    screen.blit(
                        ability_text,
                        (
                            tank.rect.centerx
                            - ability_text.get_width() // 2,
                            tank.rect.top - 45,
                        ),
                    )
            if network.connected and my_player_id in server_players:
                my_data = server_players[my_player_id]
                if not invisible and my_data.get("neetdom_active", False):
                    pygame.draw.circle(
                        screen,
                        (80, 200, 255),
                        tank.rect.center,
                        65,
                        3,
                    )
        if network.connected and my_player_id in server_players:
            my_health = server_players[my_player_id]["health"]
            if not invisible:
                draw_health_bar(
                    screen,
                    player.rect.centerx - 50,
                    player.rect.top - 15,
                    my_health,
                )
        if network.connected and my_player_id in server_players:
            my_data = server_players[my_player_id]
            if not invisible and my_data.get("rapid_fire_active", False):
                rapid_text = subtitle_font.render(
                    "RAPID FIRE ACTIVE",
                    True,
                    (255, 190, 70),
                )
                screen.blit(
                    rapid_text,
                    (
                        tank.rect.centerx - rapid_text.get_width() // 2,
                        tank.rect.top - 45,
                    ),
                )
        for projectile in network.get_projectiles():
            position = (
                round(projectile["x"]),
                round(projectile["y"]),
            )
            color = tuple(projectile["color"])
            pygame.draw.circle(
                screen,
                color,
                position,
                7,
            )
            pygame.draw.circle(
                screen,
                (240, 245, 255),
                position,
                5,
            )
        for explosion in network.get_explosions():
            position = (
                round(explosion["x"]),
                round(explosion["y"]),
            )
            radius = round(explosion["radius"])
            pygame.draw.circle(
                screen,
                (255, 100, 30),
                position,
                radius,
                5,
            )
            pygame.draw.circle(
                screen,
                (255, 220, 100),
                position,
                max(1, radius // 2),
                3,
            )
        for other_id, data in server_players.items():
            if other_id == my_player_id:
                continue
            if data["character"] == "Poe":
                other_player = Poe(data["x"], data["y"])
            else:
                other_player = Lena(data["x"], data["y"])
            other_player.name = data["name"]
            frozen = data.get("frozen", False)
            other_player.rect.topleft = (
                round(data["x"]),
                round(data["y"])
            )
            invisible = (
                    data["character"] == "Poe"
                    and data.get("social_anxiety_active", False)
            )
            if not invisible:
                other_player.draw(screen)
                if frozen:
                    freeze_text = subtitle_font.render(
                        "❄ FREEZE",
                        True,
                        (100, 200, 255),
                    )
                    screen.blit(
                        freeze_text,
                        (
                            other_player.rect.centerx
                            - freeze_text.get_width() // 2,
                            other_player.rect.top - 45,
                        ),
                    )
                if data["character"] == "Lena":
                    active_abilities = []
                    if data.get("defect_gi_active", False):
                        active_abilities.append("DEFECT, GI!")
                    if data.get("manipulate_active", False):
                        active_abilities.append("MANIPULATE")
                    if data.get("binaural_beats_active", False):
                        active_abilities.append("BINAURAL BEATS")
                    if active_abilities:
                        ability_text = subtitle_font.render(
                            " | ".join(active_abilities),
                            True,
                            (255, 130, 170),
                        )
                        screen.blit(
                            ability_text,
                            (
                                other_player.rect.centerx
                                - ability_text.get_width() // 2,
                                other_player.rect.top - 45,
                            ),
                        )
            if not invisible and data.get("neetdom_active", False):
                pygame.draw.circle(
                    screen,
                    (80, 200, 255),
                    other_player.rect.center,
                    65,
                    3,
                )
            if not invisible and data.get("rapid_fire_active", False):
                rapid_text = subtitle_font.render(
                    "RAPID FIRE ACTIVE",
                    True,
                    (255, 190, 70),
                )
                screen.blit(
                    rapid_text,
                    (
                        other_player.rect.centerx - rapid_text.get_width() // 2,
                        other_player.rect.top - 45,
                    ),
                )
            if not invisible:
                draw_health_bar(
                    screen,
                    round(data["x"] + 50),
                    round(data["y"] - 15),
                    data.get("health", 500),
                )
        controls = "WASD: Move | Left Click: Shoot"
        if network.connected:
            connection_status = "ONLINE"
        elif network.error:
            connection_status = "DISCONNECTED"
        else:
            connection_status = "CONNECTING"
        if player is not None:
            subtitle = subtitle_font.render(
                f"Playing as {player.name} | {controls} | "
                f"{connection_status} | ESC: Character Select",
                True,
                WHITE
            )
            screen.blit(subtitle, (95, 655))
    pygame.display.flip()
pygame.quit()
sys.exit()
import pygame
import sys
from client.entities.poe import Poe
from client.entities.lena import Lena
from client.screens.character_select import CharacterSelect
from client.network import NetworkClient
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
game_state = "character_select"
character_select = CharacterSelect(screen)
player = None
network = NetworkClient()
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
def create_player(character_name):
    if character_name == "Poe":
        return Poe(350, 330)
    return Lena(350, 330)
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif game_state == "character_select":
            selected = character_select.handle_event(event)
            if selected is not None:
                player = create_player(selected)
                network.connect("Player", selected)
                game_state = "arena"
        elif game_state == "arena":
                keys = pygame.key.get_pressed()
                network.send_input(
                    up=keys[pygame.K_w],
                    down=keys[pygame.K_s],
                    left=keys[pygame.K_a],
                    right=keys[pygame.K_d],
                )
        server_players = network.get_players()
        my_player_id = network.player_id
        if my_player_id in server_players:
            my_data = server_players[my_player_id]
            player.x = my_data["x"]
            player.y = my_data["y"]
            player.rect.topleft = (round(player.x), round(player.y))
    if game_state == "character_select":
        character_select.draw()
    elif game_state == "arena":
        keys = pygame.key.get_pressed()
        player.move(keys)
        player.x = max(ARENA_LEFT, min(player.x, ARENA_RIGHT - player.width))
        player.y = max(ARENA_TOP, min(player.y, ARENA_BOTTOM - player.height))
        player.rect.topleft = (round(player.x), round(player.y))
        for wall in WALLS:
            if player.rect.colliderect(wall):
                player.x -= player.speed
                player.y -= player.speed
                player.rect.topleft = (round(player.x), round(player.y))
        player.rect.topleft = (
            round(player.x),
            round(player.y)
        )
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
            pygame.draw.rect(screen, (55, 75, 110), wall, border_radius=5)
            pygame.draw.rect(screen, (90, 140, 210), wall, width=2, border_radius=5)
        title = title_font.render(
            "BLUE NIGHT ARENA",
            True,
            WHITE
        )
        screen.blit(
            title,
            title.get_rect(
                center=(WIDTH // 2, 45)
            )
        )
        player.draw(screen)
        for other_id, data in server_players.items():
            if other_id == my_player_id:
                continue
            if data["character"] == "Poe":
                other_player = Poe(data["x"], data["y"])
            else:
                other_player = Lena(data["x"], data["y"])
            other_player.name = data["name"]
            other_player.rect.topleft = (
                round(data["x"]),
                round(data["y"]),
            )
            other_player.draw(screen)
        controls = "WASD: Move"
        if network.connected:
            connection_status = "ONLINE"
        elif network.error:
            connection_status = "DISCONNECTED"
        else:
            connection_status = "CONNECTING"
        subtitle = subtitle_font.render(
            f"Playing as {player.name} | {controls} | "
            f"{connection_status} | ESC: Character Select",
            True,
            WHITE
        )
        screen.blit(subtitle, (95, 655))
    pygame.display.flip()
    clock.tick(FPS)
pygame.quit()
sys.exit()
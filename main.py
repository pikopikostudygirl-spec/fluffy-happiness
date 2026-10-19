import pygame
import sys
from client.entities.poe import Poe
from client.entities.lena import Lena
from client.screens.character_select import CharacterSelect
from client.network import NetworkClient
from client.entities.projectile import Projectile
from client.entities.tank import Tank
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
tank = None
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
        elif game_state == "character_select":
            selected = character_select.handle_event(event)
            if selected is not None:
                player = create_player(selected)
                tank = Tank(350, 330, owner_id=network.player_id)
                network.connect("Player", selected)
                game_state = "arena"
        elif game_state == "arena":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if player is not None:
                    projectile_color = (
                        (80, 220, 120)
                        if player.name == "Poe"
                        else (255, 90, 110)
                    )
                    projectiles.append(
                        Projectile(
                            start_pos=tank.rect.center,
                            target_pos=event.pos,
                            owner_id=network.player_id,
                            color=projectile_color,
                        )
                    )
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                game_state = "character_select"
    if not running:
        break
    server_players = network.get_players()
    my_player_id = network.player_id
    if game_state == "arena" and player is not None:
        keys = pygame.key.get_pressed()
        tank.move(keys, dt)
        tank.x = max(
            ARENA_LEFT,
            min(tank.x, ARENA_RIGHT - tank.width)
        )
        tank.y = max(
            ARENA_TOP,
            min(tank.y, ARENA_BOTTOM - tank.height)
        )
        tank.rect.topleft = (
            round(tank.x),
            round(tank.y)
        )
        player.rect.centerx = tank.rect.centerx
        tank.aim_at(pygame.mouse.get_pos())
        player.rect.bottom = tank.rect.top + 39
        player.x = float(player.rect.x)
        player.y = float(player.rect.y)
        if network.connected and my_player_id in server_players:
            my_data = server_players[my_player_id]
            player.x = my_data["x"]
            player.y = my_data["y"]
            player.rect.topleft = (
                round(player.x),
                round(player.y)
            )
    if game_state == "character_select":
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
            tank.draw(screen, driver=player)
        for projectile in projectiles[:]:
            projectile.update(dt)
            for wall in WALLS:
                if projectile.rect.colliderect(wall):
                    projectile.alive = False
                    break
            if not projectile.alive:
                projectiles.remove(projectile)
                continue
            projectile.draw(screen)
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
                round(data["y"])
            )
            other_player.draw(screen)
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
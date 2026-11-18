import asyncio
import json
import math
import os
import uuid
import websockets
import time
import sqlite3
import hashlib
import secrets
def initialize_database():
    connection = sqlite3.connect("accounts.db")
    connection.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL
        )
    """)
    connection.commit()
    connection.close()
HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", 8765))
TICK_RATE = 30
PLAYER_SPEED = 180
CHAT_MAX_LENGTH = 200
TANK_WIDTH = 100
TANK_HEIGHT = 76
MAX_HEALTH = 500
PROJECTILE_DAMAGE = 50
PROJECTILE_SPEED = 500
PROJECTILE_RANGE = 600
PROJECTILE_RADIUS = 5
FIRE_COOLDOWN = 1.0
RESPAWN_DELAY = 3.0
NEETDOM_DURATION = 5.0
NEETDOM_COOLDOWN = 15.0
RAPID_FIRE_DURATION = 10.0
RAPID_FIRE_COOLDOWN = 20.0
RAPID_FIRE_MULTIPLIER = 1.5
SOCIAL_ANXIETY_DURATION = 20.0
SOCIAL_ANXIETY_COOLDOWN = 25.0
KAMIKAZE_COOLDOWN = 60.0
KAMIKAZE_RADIUS = 250
KAMIKAZE_DAMAGE = 300
DEFECT_GI_DURATION = 15.0
DEFECT_GI_COOLDOWN = 30.0
DEFECT_GI_PROJECTILE_MULTIPLIER = 1.5
MANIPULATE_DURATION = 15.0
MANIPULATE_COOLDOWN = 15.0
MANIPULATE_SPEED_MULTIPLIER = 1.5
BINAURAL_BEATS_DURATION = 20.0
BINAURAL_BEATS_COOLDOWN = 20.0
BINAURAL_BEATS_DAMAGE_MULTIPLIER = 1.5
FREEZE_RADIUS = 250
FREEZE_DURATION = 3.0
FREEZE_COOLDOWN = 45.0
ARENA_LEFT = 80
ARENA_TOP = 100
ARENA_RIGHT = 1200
ARENA_BOTTOM = 640
WALLS = [
    (250, 180, 220, 25),
    (650, 180, 220, 25),
    (450, 300, 300, 25),
    (250, 450, 25, 120),
    (1000, 350, 25, 150),
]
players = {}
clients = {}
projectiles = []
explosions = []
def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))
def collides_with_wall(x, y, width, height):
    player_left = x
    player_top = y
    player_right = x + width
    player_bottom = y + height
    for wall_x, wall_y, wall_w, wall_h in WALLS:
        if (
            player_left < wall_x + wall_w
            and player_right > wall_x
            and player_top < wall_y + wall_h
            and player_bottom > wall_y
        ):
            return True
    return False
async def send_json(websocket, data):
    await websocket.send(json.dumps(data))
async def broadcast_chat(sender_id, message):
    player = players.get(sender_id)
    if player is None:
        return
    chat_data = json.dumps({
        "type": "chat",
        "username": player["name"],
        "message": message,
    })
    disconnected = []
    for websocket in list(clients):
        try:
            await websocket.send(chat_data)
        except websockets.exceptions.ConnectionClosed:
            disconnected.append(websocket)
    for websocket in disconnected:
        await remove_player(websocket)
async def broadcast_state():
    state = {
        "type": "state",
        "players": {
            player_id: {
                "id": player_id,
                "name": player["name"],
                "character": player["character"],
                "x": player["x"],
                "y": player["y"],
                "health": player["health"],
                "neetdom_active": time.monotonic() < player["neetdom_until"],
                "rapid_fire_active": time.monotonic() < player["rapid_fire_until"],
                "social_anxiety_active": time.monotonic() < player["social_anxiety_until"],
                "defect_gi_active": time.monotonic() < player["defect_gi_until"],
                "manipulate_active": time.monotonic() < player["manipulate_until"],
                "binaural_beats_active": time.monotonic() < player["binaural_beats_until"],
                "freeze_active": time.monotonic() < player["freeze_until"],
                "frozen": any(
                    lena_id != player_id
                    and lena["character"] == "Lena"
                    and lena["health"] > 0
                    and time.monotonic() < lena["freeze_until"]
                    and math.hypot(
                        (player["x"] + TANK_WIDTH / 2)
                        - (lena["x"] + TANK_WIDTH / 2),
                        (player["y"] + TANK_HEIGHT / 2)
                        - (lena["y"] + TANK_HEIGHT / 2),
                    ) <= FREEZE_RADIUS
                    for lena_id, lena in players.items()
                ),
                "neetdom_ready_at": player["neetdom_ready_at"],
                "rapid_fire_ready_at": player["rapid_fire_ready_at"],
                "social_anxiety_ready_at": player["social_anxiety_ready_at"],
                "kamikaze_ready_at": player["kamikaze_ready_at"],
                "defect_gi_ready_at": player["defect_gi_ready_at"],
                "manipulate_ready_at": player["manipulate_ready_at"],
                "binaural_beats_ready_at": player["binaural_beats_ready_at"],
                "freeze_ready_at": player["freeze_ready_at"],
            }
            for player_id, player in players.items()
        },
        "projectiles": [
            {
                "id": projectile["id"],
                "x": projectile["x"],
                "y": projectile["y"],
                "color": projectile["color"],
            }
            for projectile in projectiles
        ],
        "explosions": [
            {
                "x": explosion["x"],
                "y": explosion["y"],
                "radius": explosion["radius"],
            }
            for explosion in explosions
            if time.monotonic() < explosion["expires_at"]
        ],
    }
    message = json.dumps(state)
    disconnected = []
    for websocket in list(clients):
        try:
            await websocket.send(message)
        except websockets.exceptions.ConnectionClosed:
            disconnected.append(websocket)
    for websocket in disconnected:
        await remove_player(websocket)
async def remove_player(websocket):
    player_id = clients.pop(websocket, None)
    if player_id is not None:
        player = players.pop(player_id, None)
        if player:
            print(f"{player['name']} disconnected.")
async def handle_player(websocket):
    player_id = str(uuid.uuid4())[:8]
    try:
        first_message = await websocket.recv()
        data = json.loads(first_message)
        if not isinstance(data, dict):
            return
        auth_type = data.get("type")
        username = str(data.get("username", "")).strip()
        password = data.get("password", "")
        if not isinstance(password, str):
            return
        if auth_type == "register":
            success, message = register_account(
                username, password
            )
        elif auth_type == "login":
            success = verify_login(username, password)
            message = (
                "Login successful."
                if success
                else "Invalid username or password."
            )
        else:
            success = False
            message = "Invalid authentication request."
        await send_json(websocket, {
            "type": "auth_result",
            "success": success,
            "message": message,
        })
        if not success:
            return
        join_message = await websocket.recv()
        join_data = json.loads(join_message)
        if not isinstance(join_data, dict):
            return
        if join_data.get("type") != "join":
            return
        name = username
        character = join_data.get("character", "Poe")
        if character not in ("Poe", "Lena"):
            character = "Poe"
        for old_websocket, old_player_id in list(clients.items()):
            old_player = players.get(old_player_id)
            if old_player and old_player["name"] == username:
                await old_websocket.close(
                    code=4001,
                    reason="Account logged in elsewhere",
                )
                await remove_player(old_websocket)
        clients[websocket] = player_id
        print("CONNECTED CLIENTS:", len(clients), "PLAYER IDs:", list(players))
        players[player_id] = {
            "name": name,
            "character": character,
            "x": 350,
            "y": 330,
            "health": 500,
            "last_shot": 0.0,
            "respawn_at": None,
            "neetdom_until": 0.0,
            "neetdom_ready_at": 0.0,
            "rapid_fire_until": 0.0,
            "rapid_fire_ready_at": 0.0,
            "social_anxiety_until": 0.0,
            "social_anxiety_ready_at": 0.0,
            "kamikaze_ready_at": 0.0,
            "defect_gi_until": 0.0,
            "defect_gi_ready_at": 0.0,
            "manipulate_until": 0.0,
            "manipulate_ready_at": 0.0,
            "binaural_beats_until": 0.0,
            "binaural_beats_ready_at": 0.0,
            "freeze_until": 0.0,
            "freeze_ready_at": 0.0,
            "input": {
                "up": False,
                "down": False,
                "left": False,
                "right": False,
            },
        }
        await send_json(websocket, {
            "type": "welcome",
            "player_id": player_id,
        })
        print(f"{name} joined as {character}.")
        async for message in websocket:
            try:
                data = json.loads(message)
            except json.JSONDecodeError:
                continue
            if not isinstance(data, dict):
                continue
            player = players.get(player_id)
            if player is None:
                break
            if data.get("type") == "chat":
                message = data.get("message", "")
                if not isinstance(message, str):
                    continue
                message = message.strip()
                if not message:
                    continue
                message = message[:CHAT_MAX_LENGTH]
                await broadcast_chat(player_id, message)
                print("CHAT RECEIVED:", username, message)
            elif data.get("type") == "input":
                if data.get("type") == "input":
                    player["input"] = {
                        "up": bool(data.get("up")),
                        "down": bool(data.get("down")),
                        "left": bool(data.get("left")),
                        "right": bool(data.get("right")),
                    }
            elif data.get("type") == "fire":
                now = time.monotonic()
                if now < player["social_anxiety_until"]:
                    continue
                frozen = False
                for lena_id, lena in players.items():
                    if lena_id == player_id:
                        continue
                    if lena["character"] != "Lena":
                        continue
                    if lena["health"] <= 0:
                        continue
                    if now >= lena["freeze_until"]:
                        continue
                    distance = math.hypot(
                        (player["x"] + TANK_WIDTH / 2)
                        - (lena["x"] + TANK_WIDTH / 2),

                        (player["y"] + TANK_HEIGHT / 2)
                        - (lena["y"] + TANK_HEIGHT / 2),
                    )
                    if distance <= FREEZE_RADIUS:
                        frozen = True
                        break
                if frozen:
                    continue
                current_cooldown = FIRE_COOLDOWN
                if now < player["rapid_fire_until"]:
                    current_cooldown /= RAPID_FIRE_MULTIPLIER
                if now - player["last_shot"] < current_cooldown:
                    continue
                try:
                    target_x = float(data["target_x"])
                    target_y = float(data["target_y"])
                except (KeyError, TypeError, ValueError):
                    continue
                if not (
                    math.isfinite(target_x)
                    and math.isfinite(target_y)
                ):
                    continue
                start_x = player["x"] + TANK_WIDTH / 2
                start_y = player["y"] + TANK_HEIGHT / 2
                direction_x = target_x - start_x
                direction_y = target_y - start_y
                length = math.hypot(direction_x, direction_y)
                if length == 0:
                    continue
                direction_x /= length
                direction_y /= length
                projectiles.append({
                    "id": str(uuid.uuid4())[:8],
                    "owner_id": player_id,
                    "x": start_x,
                    "y": start_y,
                    "dx": direction_x,
                    "dy": direction_y,
                    "distance": 0.0,
                    "color": (
                        [80, 220, 120]
                        if player["character"] == "Poe"
                        else [255, 90, 110]
                    ),
                })
                player["last_shot"] = now
            elif data.get("type") == "ability":
                ability = data.get("ability")
                now = time.monotonic()
                if player["health"] <= 0:
                    continue
                if player["character"] == "Poe":
                    if ability == "neetdom":
                        if now < player["neetdom_ready_at"]:
                            continue
                        player["neetdom_until"] = (
                            now + NEETDOM_DURATION
                        )
                        player["neetdom_ready_at"] = (
                            now + NEETDOM_COOLDOWN
                        )
                    elif ability == "rapid_fire":
                        if now < player["rapid_fire_ready_at"]:
                            continue
                        player["rapid_fire_until"] = (
                            now + RAPID_FIRE_DURATION
                        )
                        player["rapid_fire_ready_at"] = (
                            now + RAPID_FIRE_COOLDOWN
                        )
                    elif ability == "social_anxiety":
                        if now < player["social_anxiety_ready_at"]:
                            continue
                        player["social_anxiety_until"] = (
                            now + SOCIAL_ANXIETY_DURATION
                        )
                        player["social_anxiety_ready_at"] = (
                            now + SOCIAL_ANXIETY_COOLDOWN
                        )
                    elif ability == "kamikaze":

                        if now < player["kamikaze_ready_at"]:
                            continue
                        player["kamikaze_ready_at"] = (
                            now + KAMIKAZE_COOLDOWN
                        )
                        explosion_x = (
                            player["x"] + TANK_WIDTH / 2
                        )
                        explosion_y = (
                            player["y"] + TANK_HEIGHT / 2
                        )
                        explosions.append({
                            "x": explosion_x,
                            "y": explosion_y,
                            "radius": KAMIKAZE_RADIUS,
                            "expires_at": now + 0.6,
                        })
                        for enemy_id, enemy in players.items():
                            if enemy_id == player_id:
                                continue
                            if enemy["health"] <= 0:
                                continue
                            enemy_x = (
                                enemy["x"] + TANK_WIDTH / 2
                            )
                            enemy_y = (
                                enemy["y"] + TANK_HEIGHT / 2
                            )
                            distance = math.hypot(
                                enemy_x - explosion_x,
                                enemy_y - explosion_y,
                            )
                            if distance <= KAMIKAZE_RADIUS:
                                enemy["health"] = max(
                                    0,
                                    enemy["health"] - KAMIKAZE_DAMAGE,
                                )
                                if enemy["health"] == 0:
                                    enemy["respawn_at"] = (
                                        now + RESPAWN_DELAY
                                    )
                        player["health"] = 0
                        player["respawn_at"] = (
                            now + RESPAWN_DELAY
                        )
                elif player["character"] == "Lena":
                    if ability == "defect_gi":
                        if now < player["defect_gi_ready_at"]:
                            continue
                        player["defect_gi_until"] = (
                            now + DEFECT_GI_DURATION
                        )
                        player["defect_gi_ready_at"] = (
                            now + DEFECT_GI_COOLDOWN
                        )
                    elif ability == "manipulate":
                        if now < player["manipulate_ready_at"]:
                            continue
                        player["manipulate_until"] = (
                            now + MANIPULATE_DURATION
                        )
                        player["manipulate_ready_at"] = (
                            now + MANIPULATE_COOLDOWN
                        )
                    elif ability == "binaural_beats":
                        if now < player["binaural_beats_ready_at"]:
                            continue
                        player["binaural_beats_until"] = (
                            now + BINAURAL_BEATS_DURATION
                        )
                        player["binaural_beats_ready_at"] = (
                            now + BINAURAL_BEATS_COOLDOWN
                        )
                    elif ability == "freeze":
                        if now < player["freeze_ready_at"]:
                            continue
                        player["freeze_until"] = (
                            now + FREEZE_DURATION
                        )
                        player["freeze_ready_at"] = (
                            now + FREEZE_COOLDOWN
                        )
    except websockets.exceptions.ConnectionClosed:
        pass
    except (json.JSONDecodeError, TypeError) as error:
        print(f"Invalid client message: {error}")
    finally:
        await remove_player(websocket)
def update_projectiles(dt):
    now = time.monotonic()
    remaining_projectiles = []
    for projectile in projectiles:
        speed = PROJECTILE_SPEED
        for lena_id, lena in players.items():
            if lena["character"] != "Lena":
                continue
            if lena["health"] <= 0:
                continue
            if now >= lena["defect_gi_until"]:
                continue
            if projectile["owner_id"] == lena_id:
                continue
            distance_to_lena = math.hypot(
                projectile["x"] - (lena["x"] + TANK_WIDTH / 2),
                projectile["y"] - (lena["y"] + TANK_HEIGHT / 2),
            )
            if distance_to_lena <= 200:
                speed /= DEFECT_GI_PROJECTILE_MULTIPLIER
                break
        distance = min(
            speed * dt,
            PROJECTILE_RANGE - projectile["distance"],
        )
        projectile["x"] += projectile["dx"] * distance
        projectile["y"] += projectile["dy"] * distance
        projectile["distance"] += distance
        if projectile["distance"] >= PROJECTILE_RANGE:
            continue
        projectile_rect = (
            projectile["x"] - PROJECTILE_RADIUS,
            projectile["y"] - PROJECTILE_RADIUS,
            PROJECTILE_RADIUS * 2,
            PROJECTILE_RADIUS * 2,
        )
        px, py, pw, ph = projectile_rect
        hit_wall = any(
            px < wall_x + wall_w
            and px + pw > wall_x
            and py < wall_y + wall_h
            and py + ph > wall_y
            for wall_x, wall_y, wall_w, wall_h in WALLS
        )
        if hit_wall:
            continue
        hit_player = False
        for player_id, target in players.items():
            if player_id == projectile["owner_id"]:
                continue
            if target["health"] <= 0:
                continue
            if (
                projectile["x"] + PROJECTILE_RADIUS > target["x"]
                and projectile["x"] - PROJECTILE_RADIUS
                    < target["x"] + TANK_WIDTH
                and projectile["y"] + PROJECTILE_RADIUS > target["y"]
                and projectile["y"] - PROJECTILE_RADIUS
                    < target["y"] + TANK_HEIGHT
            ):
                if now < target["neetdom_until"]:
                    hit_player = True
                    break
                damage = PROJECTILE_DAMAGE
                owner = players.get(projectile["owner_id"])
                if (
                        owner is not None
                        and owner["character"] == "Lena"
                        and now < owner["binaural_beats_until"]
                ):
                    damage = int(
                        damage * BINAURAL_BEATS_DAMAGE_MULTIPLIER
                    )
                target["health"] = max(
                    0,
                    target["health"] - damage,
                )
                if target["health"] == 0:
                    target["respawn_at"] = now + RESPAWN_DELAY
                hit_player = True
                break
        if not hit_player:
            remaining_projectiles.append(projectile)
    projectiles[:] = remaining_projectiles
async def game_loop():
    delay = 1 / TICK_RATE
    while True:
        now = time.monotonic()
        explosions[:] = [
            explosion
            for explosion in explosions
            if now < explosion["expires_at"]
        ]
        for player in players.values():
            if (
                player["health"] <= 0
                and player["respawn_at"] is not None
                and now >= player["respawn_at"]
            ):
                player["health"] = MAX_HEALTH
                player["x"] = 350
                player["y"] = 330
                player["respawn_at"] = None
        for player_id, player in list(players.items()):
            if player["health"] <= 0:
                continue
                for player_id, player in list(players.items()):
                    if player["health"] <= 0:
                        continue
                    frozen = False
                    for lena_id, lena in players.items():
                        if lena_id == player_id:
                            continue
                        if lena["character"] != "Lena":
                            continue
                        if lena["health"] <= 0:
                            continue
                        if now >= lena["freeze_until"]:
                            continue
                        distance = math.hypot(
                            (player["x"] + TANK_WIDTH / 2)
                            - (lena["x"] + TANK_WIDTH / 2),
                            (player["y"] + TANK_HEIGHT / 2)
                            - (lena["y"] + TANK_HEIGHT / 2),
                        )
                        if distance <= FREEZE_RADIUS:
                            frozen = True
                            break
                    if frozen:
                        continue
            keys = player["input"]
            dx = int(keys["right"]) - int(keys["left"])
            dy = int(keys["down"]) - int(keys["up"])
            length = math.hypot(dx, dy)
            if length:
                dx /= length
                dy /= length
            speed = PLAYER_SPEED
            for enemy_id, enemy in players.items():
                if (
                    enemy_id != player_id
                    and enemy["character"] == "Lena"
                    and enemy["health"] > 0
                    and now < enemy["manipulate_until"]
                ):
                    speed /= MANIPULATE_SPEED_MULTIPLIER
                    break
            old_x = player["x"]
            old_y = player["y"]
            new_x = clamp(
                old_x + dx * speed * delay,
                ARENA_LEFT,
                ARENA_RIGHT - TANK_WIDTH,
            )
            if not collides_with_wall(
                new_x, old_y, TANK_WIDTH, TANK_HEIGHT
            ):
                player["x"] = new_x
            new_y = clamp(
                old_y + dy * speed * delay,
                ARENA_TOP,
                ARENA_BOTTOM - TANK_HEIGHT,
            )
            if not collides_with_wall(
                player["x"], new_y, TANK_WIDTH, TANK_HEIGHT
            ):
                player["y"] = new_y
        update_projectiles(delay)
        await broadcast_state()
        await asyncio.sleep(delay)
def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt),
        600_000,
    ).hex()
    return password_hash, salt
def register_account(username, password):
    username = username.strip()
    if not 3 <= len(username) <= 18:
        return False, "Username must be 3–18 characters."
    if not 8 <= len(password) <= 64:
        return False, "Password must be 8–64 characters."
    if not username.isalnum():
        return False, "Username can only contain letters and numbers."
    password_hash, salt = hash_password(password)
    connection = sqlite3.connect("accounts.db")
    try:
        connection.execute(
            """
            INSERT INTO accounts (username, password_hash, salt)
            VALUES (?, ?, ?)
            """,
            (username, password_hash, salt),
        )
        connection.commit()
        return True, "Account created successfully."
    except sqlite3.IntegrityError:
        return False, "Username already exists."
    finally:
        connection.close()
def verify_login(username, password):
    connection = sqlite3.connect("accounts.db")
    try:
        account = connection.execute(
            """
            SELECT password_hash, salt
            FROM accounts
            WHERE username = ?
            """,
            (username.strip(),),
        ).fetchone()
        if account is None:
            return False
        stored_hash, salt = account
        calculated_hash, _ = hash_password(password, salt)
        return secrets.compare_digest(stored_hash, calculated_hash)
    finally:
        connection.close()
async def main():
    initialize_database()
    print(f"Starting Blue Night Arena server on port {PORT}...")
    async with websockets.serve(handle_player, HOST, PORT):
        print("Server is ready for connections.")
        await game_loop()
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server stopped.")
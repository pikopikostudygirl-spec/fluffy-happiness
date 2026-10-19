import asyncio
import json
import math
import os
import uuid
import websockets
HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", 8765))
TICK_RATE = 30
PLAYER_SPEED = 180
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
            }
            for player_id, player in players.items()
        },
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
        if data.get("type") != "join":
            await send_json(websocket, {
                "type": "error",
                "message": "Send a join message first.",
            })
            return
        name = str(data.get("name", "Player")).strip()[:18] or "Player"
        character = data.get("character", "Poe")
        if character not in ("Poe", "Lena"):
            character = "Poe"
        clients[websocket] = player_id
        players[player_id] = {
            "name": name,
            "character": character,
            "x": 350,
            "y": 330,
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
            player = players.get(player_id)
            if player is None:
                break
            if data.get("type") == "input":
                player["input"] = {
                    "up": bool(data.get("up")),
                    "down": bool(data.get("down")),
                    "left": bool(data.get("left")),
                    "right": bool(data.get("right")),
                }
    except websockets.exceptions.ConnectionClosed:
        pass
    except (json.JSONDecodeError, TypeError) as error:
        print(f"Invalid client message: {error}")
    finally:
        await remove_player(websocket)
async def game_loop():
    delay = 1 / TICK_RATE
    while True:
        for player in list(players.values()):
            keys = player["input"]
            dx = int(keys["right"]) - int(keys["left"])
            dy = int(keys["down"]) - int(keys["up"])
            length = math.hypot(dx, dy)
            if length:
                dx /= length
                dy /= length
            old_x = player["x"]
            old_y = player["y"]
            new_x = clamp(
                old_x + dx * PLAYER_SPEED * delay,
                ARENA_LEFT,
                ARENA_RIGHT - 44,
            )
            if not collides_with_wall(new_x, old_y, 44, 76):
                player["x"] = new_x
            new_y = clamp(
                old_y + dy * PLAYER_SPEED * delay,
                ARENA_TOP,
                ARENA_BOTTOM - 76,
            )
            if not collides_with_wall(
                player["x"], new_y, 44, 76
            ):
                player["y"] = new_y
        await broadcast_state()
        await asyncio.sleep(delay)
async def main():
    print(f"Starting Blue Night Arena server on port {PORT}...")
    async with websockets.serve(handle_player, HOST, PORT):
        print("Server is ready for connections.")
        await game_loop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server stopped.")
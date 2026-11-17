import asyncio
import json
import os
import threading
import websockets
class NetworkClient:
    def __init__(self, server_url=None):
        self.auth_complete = False
        self.auth_success = False
        self.auth_message = ""
        self.join_event = None
        self.selected_character = None
        self.server_url = server_url or os.environ.get(
            "BNA_SERVER_URL",
            "ws://127.0.0.1:8765",
        )
        print("SERVER URL:", self.server_url)
        self.websocket = None
        self.loop = None
        self.thread = None
        self.connected = False
        self.player_id = None
        self.players = {}
        self.projectiles = []
        self.error = None
        self._lock = threading.Lock()
    def connect(self, username, password, auth_type):
        print("CONNECT CALLED:", username, auth_type)
        if self.thread and self.thread.is_alive():
            return
        self.auth_complete = False
        self.auth_success = False
        self.auth_message = ""
        self.error = None
        self.thread = threading.Thread(
            target=self._run,
            args=(username, password, auth_type),
            daemon=True,
        )
        self.thread.start()
    def _run(self, username, password, auth_type):
        print("NETWORK THREAD STARTED")
        asyncio.run(
            self._network_loop(username, password, auth_type)
        )
    async def _network_loop(self, username, password, auth_type):
        self.loop = asyncio.get_running_loop()
        try:
            async with websockets.connect(self.server_url) as websocket:
                print("WEBSOCKET CONNECTED")
                self.websocket = websocket
                await websocket.send(json.dumps({
                    "type": auth_type,
                    "username": username,
                    "password": password,
                }))
                message = await websocket.recv()
                data = json.loads(message)
                if data.get("type") != "auth_result":
                    self.auth_message = "Invalid server response."
                    self.auth_complete = True
                    return
                self.auth_success = data.get("success", False)
                self.auth_message = data.get("message", "")
                self.auth_complete = True
                if not self.auth_success:
                    return
                self.join_event = asyncio.Event()
                await self.join_event.wait()
                await websocket.send(json.dumps({
                    "type": "join",
                    "character": self.selected_character,
                }))
                async for message in websocket:
                    data = json.loads(message)
                    if data.get("type") == "auth_result":
                        self.auth_complete = True
                        self.auth_success = data.get("success", False)
                        self.auth_message = data.get("message", "")
                        if not self.auth_success:
                            return
                    elif data.get("type") == "welcome":
                        self.player_id = data.get("player_id")
                        self.connected = True
                    elif data.get("type") == "state":
                        with self._lock:
                            self.players = data.get("players", {})
                            self.projectiles = data.get("projectiles", [])
                            self.explosions = data.get("explosions", [])
                        self.connected = True
                    elif data.get("type") == "state":
                        with self._lock:
                            self.players = data.get("players", {})
                            self.projectiles = data.get("projectiles", [])
                            self.explosions = data.get("explosions", [])
        except Exception as error:
            self.error = str(error)
            print("Network error:", error)
        finally:
            self.connected = False
            self.auth_complete = False
            self.auth_success = False
            self.auth_message = ""
            self.join_event = None
            self.selected_character = None
            self.websocket = None
    def join_character(self, character):
        if not self.loop or not hasattr(self, "join_event"):
            return
        self.selected_character = character
        self.loop.call_soon_threadsafe(
            self.join_event.set
        )
    def send_input(self, up, down, left, right):
        if not self.connected or not self.loop or not self.websocket:
            return
        message = {
            "type": "input",
            "up": bool(up),
            "down": bool(down),
            "left": bool(left),
            "right": bool(right),
        }
        try:
            future = asyncio.run_coroutine_threadsafe(
                self.websocket.send(json.dumps(message)),
                self.loop,
            )
        except RuntimeError:
            self.connected = False
    def fire(self, target_x, target_y):
        if not self.connected or not self.loop or not self.websocket:
            return
        message = {
            "type": "fire",
            "target_x": float(target_x),
            "target_y": float(target_y),
        }
        try:
            asyncio.run_coroutine_threadsafe(
                self.websocket.send(json.dumps(message)),
                self.loop,
            )
        except RuntimeError:
            self.connected = False
    def activate_ability(self, ability):
        if not self.connected or not self.loop or not self.websocket:
            return
        if ability not in (
                "neetdom",
                "rapid_fire",
                "social_anxiety",
                "defect_gi",
                "manipulate",
                "binaural_beats",
                "kamikaze",
                "freeze",
        ):
            return
        message = {
            "type": "ability",
            "ability": ability,
        }
        try:
            asyncio.run_coroutine_threadsafe(
                self.websocket.send(json.dumps(message)),
                self.loop,
            )
        except RuntimeError:
            self.connected = False
    def get_players(self):
        with self._lock:
            return dict(self.players)
    def get_projectiles(self):
        with self._lock:
            return list(self.projectiles)
    def get_explosions(self):
        with self._lock:
            return list(getattr(self, "explosions", []))
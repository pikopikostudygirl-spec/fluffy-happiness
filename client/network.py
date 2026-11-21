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
            "wss://blue-night-arena.onrender.com",
        )
        print("SERVER URL:", self.server_url)
        self.websocket = None
        self.loop = None
        self.thread = None
        self.connected = False
        self.player_id = None
        self.players = {}
        self.projectiles = []
        self.explosions = []
        self.chat_messages = []
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
        self.connected = False
        self.player_id = None
        with self._lock:
            self.players = {}
            self.projectiles = []
            self.explosions = []
            self.chat_messages = []
        self.thread = threading.Thread(
            target=self._run,
            args=(username, password, auth_type),
            daemon=True,
        )
        self.thread.start()
    def _run(self, username, password, auth_type):
        print("NETWORK THREAD STARTED")
        try:
            asyncio.run(
                self._network_loop(
                    username,
                    password,
                    auth_type,
                )
            )
        except Exception as error:
            self.error = str(error)
            print("NETWORK THREAD ERROR:", error)
    async def _network_loop(self, username, password, auth_type):
        self.loop = asyncio.get_running_loop()
        try:
            async with websockets.connect(
                self.server_url
            ) as websocket:
                print("WEBSOCKET CONNECTED")
                self.websocket = websocket
                await websocket.send(json.dumps({
                    "type": auth_type,
                    "username": username,
                    "password": password,
                }))
                response = await websocket.recv()
                data = json.loads(response)
                if data.get("type") != "auth_result":
                    self.auth_message = "Invalid server response."
                    self.auth_success = False
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
                    message_type = data.get("type")
                    if message_type == "auth_result":
                        self.auth_complete = True
                        self.auth_success = data.get(
                            "success", False
                        )
                        self.auth_message = data.get(
                            "message", ""
                        )
                        if not self.auth_success:
                            return
                    elif message_type == "welcome":
                        self.player_id = data.get("player_id")
                        self.connected = True
                        print(
                            "JOINED SERVER:",
                            self.player_id
                        )
                    elif message_type == "chat":
                        with self._lock:
                            self.chat_messages.append({
                                "type": "chat",
                                "username": data.get(
                                    "username", "Unknown"
                                ),
                                "message": data.get(
                                    "message", ""
                                ),
                            })
                            self.chat_messages = (
                                self.chat_messages[-50:]
                            )
                    elif message_type == "state":
                        incoming_players = data.get(
                            "players", {}
                        )
                        if not isinstance(incoming_players, dict):
                            continue
                        with self._lock:
                            self.players = incoming_players
                            self.projectiles = data.get(
                                "projectiles", []
                            )
                            self.explosions = data.get(
                                "explosions", []
                            )
                        self.connected = True
        except websockets.exceptions.ConnectionClosed as error:
            self.error = f"Connection closed: {error}"
            print(self.error)
        except Exception as error:
            self.error = str(error)
            print("NETWORK ERROR:", error)
        finally:
            self.connected = False
            self.websocket = None
            self.loop = None
            self.join_event = None
            print("NETWORK DISCONNECTED")
    def join_character(self, character):
        if not self.loop or self.join_event is None:
            return
        self.selected_character = character
        self.loop.call_soon_threadsafe(
            self.join_event.set
        )
    async def _send_json(self, data):
        websocket = self.websocket
        if websocket is None:
            raise ConnectionError("WebSocket is unavailable.")
        await websocket.send(json.dumps(data))
    def _send(self, data):
        if (
            not self.connected
            or self.loop is None
            or self.websocket is None
        ):
            return False
        try:
            future = asyncio.run_coroutine_threadsafe(
                self._send_json(data),
                self.loop,
            )
            def handle_result(result):
                try:
                    result.result()
                except Exception as error:
                    self.error = str(error)
                    self.connected = False
                    print("SEND ERROR:", error)
            future.add_done_callback(handle_result)
            return True
        except RuntimeError as error:
            self.error = str(error)
            self.connected = False
            return False
    def send_input(self, up, down, left, right):
        self._send({
            "type": "input",
            "up": bool(up),
            "down": bool(down),
            "left": bool(left),
            "right": bool(right),
        })
    def fire(self, target_x, target_y):
        self._send({
            "type": "fire",
            "target_x": float(target_x),
            "target_y": float(target_y),
        })
    def activate_ability(self, ability):
        allowed_abilities = {
            "neetdom",
            "rapid_fire",
            "social_anxiety",
            "defect_gi",
            "manipulate",
            "binaural_beats",
            "kamikaze",
            "freeze",
        }
        if ability not in allowed_abilities:
            return
        self._send({
            "type": "ability",
            "ability": ability,
        })
    def send_chat(self, message):
        if not isinstance(message, str):
            return False
        message = message.strip()[:200]
        if not message:
            return False
        return self._send({
            "type": "chat",
            "message": message,
        })
    def get_players(self):
        with self._lock:
            return dict(self.players)
    def get_projectiles(self):
        with self._lock:
            return list(self.projectiles)
    def get_explosions(self):
        with self._lock:
            return list(self.explosions)
    def get_chat_messages(self):
        with self._lock:
            return list(self.chat_messages)
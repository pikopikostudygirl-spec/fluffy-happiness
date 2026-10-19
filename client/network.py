import asyncio
import json
import os
import threading
import websockets
class NetworkClient:
    def __init__(self, server_url=None):
        self.server_url = server_url or os.environ.get(
            "BNA_SERVER_URL",
            "ws://127.0.0.1:8765",
        )
        self.websocket = None
        self.loop = None
        self.thread = None
        self.connected = False
        self.player_id = None
        self.players = {}
        self.error = None
        self._lock = threading.Lock()
    def connect(self, name, character):
        if self.thread and self.thread.is_alive():
            return
        self.thread = threading.Thread(
            target=self._run,
            args=(name, character),
            daemon=True,
        )
        self.thread.start()
    def _run(self, name, character):
        asyncio.run(self._network_loop(name, character))
    async def _network_loop(self, name, character):
        self.loop = asyncio.get_running_loop()
        try:
            async with websockets.connect(self.server_url) as websocket:
                self.websocket = websocket
                await websocket.send(json.dumps({
                    "type": "join",
                    "name": name,
                    "character": character,
                }))
                async for message in websocket:
                    data = json.loads(message)
                    if data.get("type") == "welcome":
                        self.player_id = data.get("player_id")
                        self.connected = True
                    elif data.get("type") == "state":
                        with self._lock:
                            self.players = data.get("players", {})
        except Exception as error:
            self.error = str(error)
            print("Network error:", error)
        finally:
            self.connected = False
            self.websocket = None
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
    def get_players(self):
        with self._lock:
            return dict(self.players)
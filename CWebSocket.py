import asyncio
import websockets


class CWebSocket:
    def __init__(self, trigger=None):
        self.fntrigger = trigger
        self.client = None

    # 启动WebSocket服务器
    async def start_server(self):
        async with websockets.serve(self.handle_connection, "localhost", 16002):
            print("WebSocket服务器已启动，监听 ws://localhost:16002")
            await asyncio.Future()  # 永久运行

    # 处理客户端连接
    async def handle_connection(self, websocket, path):
        print("客户端已连接")
        try:
            async for message in websocket:
                if self.fntrigger is not None:
                    self.fntrigger(message)
        except websockets.ConnectionClosed:
            print("客户端断开连接")
            self.client = None

    def send(self, data):
        try:
            if self.client is None:
                print('客户端已断开')
                return
            self.client.send(data)
        except Exception as er:
            print("客户端断开连接")
            self.client = None

    def start(self):
        asyncio.run(self.start_server())

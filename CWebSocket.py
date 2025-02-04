import asyncio

import websocket
import websockets


class CWebSocket:
    def __init__(self, trigger=None):
        self.fntrigger = trigger

    # 处理客户端连接
    async def handle_connection(self,websocket, path):
        print(f"新客户端连接: {websocket.remote_address}")
        try:
            async for message in websocket:
                ret = ''
                if self.fntrigger is not None:
                    ret = self.fntrigger(message)
                # 将消息原样返回给客户端（回显）
                await websocket.send(ret)
        except websockets.exceptions.ConnectionClosed:
            print(f"客户端断开: {websocket.remote_address}")

    # 启动服务器
    async def start_server(self):
        async with websockets.serve(self.handle_connection, "localhost", 16002):
            print("WebSocket 服务器已启动，监听端口 16002...")
            await asyncio.Future()  # 永久运行

    def start(self):
        asyncio.run(self.start_server())




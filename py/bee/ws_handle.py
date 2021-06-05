import asyncio
import json
from websockets import WebSocketClientProtocol
from py.message.ws_protocol import WSMessage, WSCommand
from py.bee.bee_runner import Bee

async def receive_message(ws: WebSocketClientProtocol):
  message =  await ws.recv()
  if message == None:
    return None
  
  json_data = json.loads(message)
  
  return WSMessage(json_data['command'], json_data.get('data'))

async def send_message(ws: WebSocketClientProtocol, message: WSMessage):
  assert message != None
  json_str = json.dumps(message.__dict__, ensure_ascii=False)
  await ws.send(json_str)


async def perform_handshake(ws: WebSocketClientProtocol) -> Bee:

  loop = asyncio.get_event_loop()
  

  await send_message(ws, WSMessage(WSCommand.handshake_hi))
  message = await receive_message(ws)


  def bee_started(address):
    print('bee started at ',address)
    if address == None:
      loop.create_task(ws.close())
    else:
      done_message = WSMessage(WSCommand.handshake_done, address)
      loop.create_task(send_message(done_message))
  # 创建bee进程
  node_id = message.strData()
  bee = Bee(node_id, bee_started)
  bee.start()
  message = await receive_message(ws)
  if message != None and message.command == WSCommand.handshake_done:
    print('握手成功')

  return bee


async def start_ping_task(ws: WebSocketClientProtocol):
  loop = asyncio.get_event_loop()

  async def task():
    while not ws.closed:
      await send_message(WSMessage(WSCommand.ping))
      asyncio.sleep(3)
  loop.create_task(task())


def handle_message_receive(ws: WebSocketClientProtocol, message: WSMessage):
  pass


import sys
import websockets
import asyncio
import os
from py.message.ws_protocol import WSCommand, WSMessage
from py.bee.bee_runner import Bee
from py.bee.ws_handle import perform_handshake, start_ping_task, handle_message_receive, receive_message, send_message



async def connectLeader():
  url = os.getenv("BEE_LEADER_WS_URL")
  if url is None:
    url = "ws://192.168.0.101:3000/ws"
  connection = await websockets.connect(url)
  
  bee = await perform_handshake(connection)
  print(bee)
  if bee != None:
    print(bee)
    await start_ping_task(connection)

    while not connection.closed and bee.isRunning():
      message = await receive_message(connection)
      print(message.command)
      if message != None and message.command == WSCommand.pong:
        pass
      elif message != None:
        handle_message_receive(message)

  print('exit')
  if bee is not None and bee.isRunning():
    bee.shutdown()
  if not connection.closed:
    await connection.close()
  exit()
    

asyncio.get_event_loop().run_until_complete(connectLeader())
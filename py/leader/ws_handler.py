import json
from geventwebsocket.websocket import WebSocket

from py.message.ws_protocol import WSMessage,WSCommand, handshake_done_message, handshake_node_id_message

from py.leader.db_helper import obtain_idle_node_id, select_by_node_id, update_data, update_status

def receive_message(ws: WebSocket):
  message = ws.receive()
  if message == None:
    return None
  
  json_data = json.loads(message)
  
  return WSMessage(json_data['command'], json_data.get('data'))

def send_message(ws: WebSocket, message: WSMessage):
  assert message != None
  json_str = json.dumps(message.__dict__, ensure_ascii=False)
  ws.send(json_str)

def perform_handshake(ws: WebSocket) -> str:
  node_id: str = None
  
  try:
    message = receive_message(ws)
    
    if message.command == WSCommand.handshake_hi:
      node_id = obtain_idle_node_id()

      send_message(ws, handshake_node_id_message(node_id))
      message = receive_message(ws)
      
      if message != None and message.command == WSCommand.handshake_done:
        address = message.strData()
        remote_ip = ws.environ['REMOTE_ADDR']
        # address, ip
        update_data(node_id, {'address': address, 'remote_ip': remote_ip})
        update_status(node_id, 2)
        print('启动成功', message)
        send_message(ws, handshake_done_message(node_id))
        return node_id
      else:
        update_status(node_id, 1)
        ws.close()
        return None
    elif message != None and message.command == WSCommand.handshake_reconnect:
      node_id = message.strData()
      bee_node = select_by_node_id(node_id)
      if bee_node == None:
        ws.close()
      update_status(node_id, 2)
      
    else:
      # 忽略其他消息，握手失败
      ws.close()
      return None
  except BaseException as err:
    if node_id != None:
      update_status(node_id, 1)
    raise err


def handle_message_receive(ws: WebSocket, message: WSMessage):
  pass

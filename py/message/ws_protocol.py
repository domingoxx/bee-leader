

class WSCommand:
  handshake_hi='handshake_hi'
  handshake_return_node_id = 'handshake_return_node_id'
  handshake_done = 'handshake_done'
  ping = 'ping'
  pong = 'pong'


class WSMessage:
  def __init__(self, command: str, data: any = None) -> None:
    
    self.command = command
    self.data = data
      

  def strData(self) -> str:
    return self.data
  
  def dictData(self) -> dict:
    return self.data



def handshake_node_id_message(node_id: str) -> WSMessage:
  return WSMessage(WSCommand.handshake_return_node_id, node_id)

def handshake_done_message(node_id: str) -> WSMessage:
  return WSMessage(WSCommand.handshake_done, node_id)



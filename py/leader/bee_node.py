

STATUS_MAP = {
  '1': '空闲中',
  '2': '使用中'
}

class BeeNodeInfo: 

  def __init__(self, address: str, state: int, remote_ip: str) -> None:
      self.address = address
      self.state = state
      self.remote_ip = remote_ip

class BeeNode:

  def __init__(self, node_id: str, status: int, node_info: BeeNodeInfo) -> None:
      self.node_id = node_id

      # 记录的状态
      self.status = status
      
      self.node_info: BeeNodeInfo = node_info

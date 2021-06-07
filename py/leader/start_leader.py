from flask import Flask, request, Response
import sqlite3
import hashlib
import json
import uuid
import time
import os, sys
from flask_sockets import Sockets

from gevent import monkey,pywsgi
from geventwebsocket.handler import WebSocketHandler
from geventwebsocket.websocket import WebSocket

from py.leader.db_helper import select_all_dict, update, update_status, initDB
from py.leader.ws_handler import handle_message_receive, perform_handshake, receive_message,  send_message
from py.message.ws_protocol import WSMessage, WSCommand
from py.leader.bee_node import BeeNode



sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))
sys.path.append("..")
monkey.patch_all()


app = Flask(__name__)


sockets = Sockets(app)
now = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))


@sockets.route('/ws')  # 指定路由
def echo_socket(ws):
  node_id: str = None
  try:
    
    node_id = perform_handshake(ws)
    if node_id != None:
      while not ws.closed:
        message = receive_message(ws)
        if message != None and message.command == WSCommand.ping:
          send_message(ws, WSMessage(WSCommand.pong))
        elif message != None:
          handle_message_receive(ws, message)
        else:
          print('close')
          ws.close()
    
  finally:
    if node_id != None:
      update_status(node_id, 1)



@app.route('/')
def index():
  return "HelloWorld"

# def 
# 获得一个未使用的地址，SQLITE CAS
# 查询所有地址
# 新增一个地址
# status 1空闲中 2使用中


# @app.route('/backAddress')
# def backAddress():
#   address = request.args.get('address')
#   if address == None:
#     return "Bad argument address"
#   row = db_helper.select_by_address(address)
#   if row == None:
#     return "Cannot found by address "+address
#   db_helper.update(address, 1, row['data'])
#   return "OK"

# @app.route('/markSented')
# def markSented():
#   address = request.args.get('address')
#   if address == None:
#     return "Bad argument address"
#   row = db_helper.select_by_address(address)
#   if row == None:
#     return "Cannot found by address "+address
#   data = row['data']
#   data['sent'] = True
#   db_helper.update(address, row['status'], data)
#   return "OK"

@app.route('/addressList')
def getAddressList():
  rows = select_all_dict()
  return apiResult(data=rows)

def apiResult(code=0, message="OK", data=None):
  result = {
    'code': code,
    'message': message,
    'data': data
  }
  return Response(json.dumps(result), mimetype='application/json')

if __name__ == '__main__':

  initDB()
  app.debug = True
  server = pywsgi.WSGIServer(('0.0.0.0', 3000), app, handler_class=WebSocketHandler)
  print('server start', flush=True)
  server.serve_forever()


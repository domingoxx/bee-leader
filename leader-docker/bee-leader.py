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
import geventwebsocket
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))
sys.path.append("..")
monkey.patch_all()


app = Flask(__name__)


sockets = Sockets(app)
now = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))


@sockets.route('/ws')  # 指定路由
def echo_socket(ws):
  
  remoteAddress = ws.environ['REMOTE_ADDR']
  message = ws.receive()  # 接收到消息
  print(message)
  if message == "Hi":
    password = obtainIdleAddress()
    
    row = select_by_address(password)
    
    wallet = row['data'].get('wallet')
    if wallet == None:
      wallet = ""
    
    ws.send(password)
    message = ws.receive()
    
    if message == 'Done':
      message = ws.receive()
      row['data']['wallet'] = message
      row['data']['beeIp'] = remoteAddress
      update(password, row['status'], row['data'])
      print('启动成功', message)
    else:
      update(password, 1, row['data'])
      ws.close()
      return
    ws.send("Done")
    while not ws.closed:
      ping = ws.receive()
      if ping != None:
        print(ping, password)
        ws.send("pong")
    update(password, 1, row['data'])
    print('退出', password)

  else:
    ws.close()
    return
  



@app.route('/')
def index():
  return "HelloWorld"

# def 
# 获得一个未使用的地址，SQLITE CAS
# 查询所有地址
# 新增一个地址
# status 1空闲 2使用中
STATUS_MAP = {
  '1': '空闲',
  '2': '使用中'
}
@app.route('/getAddress')
def getAddress():
  result = obtainIdleAddress()
  if result != None:
    return result
  return "NotFound"

@app.route('/backAddress')
def backAddress():
  address = request.args.get('address')
  if address == None:
    return "Bad argument address"
  row = select_by_address(address)
  if row == None:
    return "Cannot found by address "+address
  update(address, 1, row['data'])
  return "OK"

@app.route('/markSented')
def markSented():
  address = request.args.get('address')
  if address == None:
    return "Bad argument address"
  row = select_by_address(address)
  if row == None:
    return "Cannot found by address "+address
  data = row['data']
  data['sent'] = True
  update(address, row['status'], data)
  return "OK"

@app.route('/uploadAddress')
def uploadAddress():
  address = request.args.get('address')
  if address == None or address == '':
    return "address must not be empty"
  row = select_by_address(address)
  if row == None:
    insert(address, 2,{})
  return "OK"
@app.route('/addressList')
def getAddressList():
  rows = select_all()
  result = ""
  for row in rows:
    data = row['data']
    result += '<pre>'
    result += row['address']
    result += '    '
    if data.get('wallet') != None:
      result += data.get('wallet')
    else:
      result += '                                        '
    result += '    '
    result += STATUS_MAP[str(row['status'])]
    result += '    '
    if data.get('sent') == None:
      result += '未发送'
    else:
      result += '已发送'
    result += '    '
    result += (f"<a href='/backAddress?address={row['address']}'>归还</a>")
    result += '    '
    result += (f"<a href='/markSented?address={row['address']}'>标记已发送</a>")
    result += '</pre>'
  return result

def obtainIdleAddress():
  running = True
  address = None
  count = 0
  while running and count <= 3:
    conn = getSqlite()
    cursor = conn.cursor()
    cursor.execute("select address from bee_data where status = 1")
    row = cursor.fetchone()
    print('row: ',row)
    if row != None:
      cursor.close()
      cursor = conn.cursor()
      cursor.execute("update bee_data set status = 2 where address = '%s' and status = 1" % (row[0]))
      if cursor.rowcount >= 1:
        conn.commit()
        address = row[0]
        running = False
    else:
      running = False
    cursor.close()
    conn.close()
    count = count + 1
  if address == None:
    address = str(uuid.uuid1())
    insert(address, 2, {})
  return address


def update(address,status, data):
  print(data)
  conn = getSqlite()
  cursor = conn.cursor()
  sql = '''
  update bee_data
  set status = %s,data = '%s' 
  where address = '%s'
  ''' % (status, json.dumps(data),address)
  cursor.execute(sql)
  conn.commit()
  cursor.close()
  conn.close()

def insert(address,status, data):
  conn = getSqlite()
  cursor = conn.cursor()
  sql = '''
  insert into bee_data 
  (address,status,data) values('%s',%s,'%s')
  ''' % (address, status, json.dumps(data))
  cursor.execute(sql)
  conn.commit()
  cursor.close()
  conn.close()

fields = [
    'address',
    'status', 
    'data']

def select_all():
  conn = getSqlite()
  cursor = conn.cursor()
  cursor.execute("select %s from bee_data" % (','.join(fields)))
  rows = cursor.fetchall()
  itemList = []
  for row in rows:
    item = {}
    i = 0
    for v in row:
      item[fields[i]] = v
      i = i+1
    item['data'] = json.loads(item['data'])
    itemList.append(item)
  return itemList

def select_by_address(address):
  conn = getSqlite()
  cursor = conn.cursor()
  cursor.execute("select %s from bee_data where address = '%s' " % (','.join(fields), address))
  row = cursor.fetchone()
  item = None
  
  if row != None:
    i = 0
    item = {}
    for v in row:
      item[fields[i]] = v
      i = i+1
    item['data'] = json.loads(item['data'])
  return item

def initDB():
  from pathlib import Path
  dbfile = Path('db/bee_data.db')
  if dbfile.is_dir():
    print('Cannot create bee_data.db.')
    exit()
  if dbfile.exists() == False:
    print('db/bee_data.db not found. will create it')
    createTable()

def createTable():
  conn = getSqlite()
  cur = conn.cursor()
  cur.execute('''
    CREATE TABLE bee_data(
      address text primary key,
      data text,
      status integer
    )
  ''')
  conn.commit()
  conn.close()

def getSqlite():
  conn = sqlite3.connect('db/bee_data.db')
  return conn

if __name__ == '__main__':

  initDB()
  app.debug = True
  server = pywsgi.WSGIServer(('0.0.0.0', 3000), app, handler_class=WebSocketHandler)
  print('server start')
  server.serve_forever()


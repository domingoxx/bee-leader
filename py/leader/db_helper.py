
from platform import node
import sqlite3
import uuid
import json

from .bee_node import BeeNode, BeeNodeInfo


# 检查是否存在空闲中的记录，
# 如果有则更新为使用中并返回
# 如果没有则创建一个新的
def obtain_idle_node_id():
  running = True
  count = 0
  result = None
  while running and count <= 3:
    node_id = select_node_id_by_idle()
    print('node_id: ',node_id)
    if node_id != None:
      locked = try_lock_node_by_id(node_id)
      if locked:
        result = node_id
        running = False
    else:
      running = False
    count = count + 1
  
  # 没有空闲中的，创建一个
  if result == None:
    result = str(uuid.uuid1())
    insert(result, 2)
  return result

def select_node_id_by_idle():
  
  conn = getSqlite()
  cursor = conn.cursor()
  cursor.execute("select node_id from bee_data where status = 1")
  row = cursor.fetchone()
  node_id = None
  
  if (row != None):
    node_id = row[0]

  cursor.close()
  conn.close()

  return node_id

def try_lock_node_by_id(node_id):
  conn = getSqlite()
  cursor = conn.cursor()
  cursor.execute("update bee_data set status = 2 where node_id = '%s' and status = 1" % (node_id))
  locked = False
  if cursor.rowcount >= 1:
    locked = True
    conn.commit()
  cursor.close()
  conn.close()
  return locked

def update_status(node_id, status):
  conn = getSqlite()
  cursor = conn.cursor()
  sql = '''
  update bee_data 
  set status = %s 
  where node_id = '%s'
  ''' % (status,node_id)
  cursor.execute(sql)
  conn.commit()
  cursor.close()
  conn.close()

def update_data(node_id, new_data: dict):
  conn = getSqlite()
  cursor = conn.cursor()
  item = __select_by_node_id(cursor, node_id)
  update_data = item['data']
  for key in new_data:
    update_data[key] = new_data[key]
  __update_data(cursor, node_id, update_data)
  conn.commit()
  cursor.close()
  conn.close()

def __update_data(cursor,node_id, data):
  
  sql = '''
  update bee_data
  set data = '%s' 
  where node_id = '%s'
  ''' % (json.dumps(data),node_id)
  cursor.execute(sql)
  

def update(node_id,status, data):
  
  conn = getSqlite()
  cursor = conn.cursor()
  sql = '''
  update bee_data
  set status = %s,data = '%s' 
  where node_id = '%s'
  ''' % (status, json.dumps(data),node_id)
  cursor.execute(sql)
  conn.commit()
  cursor.close()
  conn.close()

def insert(node_id,status, data={}):
  conn = getSqlite()
  cursor = conn.cursor()
  sql = '''
  insert into bee_data 
  (node_id,status,data) values('%s',%s,'%s')
  ''' % (node_id, status, json.dumps(data))
  cursor.execute(sql)
  conn.commit()
  cursor.close()
  conn.close()

fields = [
    'node_id',
    'status', 
    'data']

def select_all_dict() -> list:
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

def __select_by_node_id(cursor,node_id) -> dict: 
  cursor.execute("select %s from bee_data where node_id = '%s' " % (','.join(fields), node_id))
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
def select_by_node_id(node_id) -> BeeNode: 
  conn = getSqlite()
  cursor = conn.cursor()
  item = __select_by_node_id(cursor, node_id)
  cursor.close()
  conn.close()
  return dict2Object(item)

def dict2Object(dict):
  data = dict['data']
  node_info = BeeNodeInfo(data.get('address'), data.get('state'), data.get('ip'))
  node = BeeNode(dict['node_id'], dict['status'], node_info)
  return node

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
      node_id text primary key,
      data text,
      status integer
    )
  ''')
  conn.commit()
  conn.close()

def getSqlite():
  conn = sqlite3.connect('db/bee_data.db')
  return conn

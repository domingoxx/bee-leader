
import sys
import websockets
import asyncio
import subprocess
import threading
import time
import os

commandArgs = " ".join(sys.argv[1:])

clef_process = None
bee_process = None


def clefDataPath(dirname):
  return f"/opt/data/{dirname}/clef"

def beeDataPath(dirname):
  return f"/opt/data/{dirname}/bee"


def initClef(dirname):
  
  cmd = f"clef --stdio-ui --configdir {clefDataPath(dirname)} init"
  sp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,stdin=subprocess.PIPE)
  password = dirname
  while sp.returncode == None:
    result = sp.stdout.readline()
    logStr = str(result, encoding="utf-8")
    print(logStr)
    if logStr.find("Please specify a password") != -1:
      sp.stdin.writelines([bytes(f"{password}\n", encoding="utf-8")])
      sp.stdin.flush()
      sp.stdin.writelines([bytes(f"{password}\n", encoding="utf-8")])
      sp.stdin.flush()
    elif logStr.find("A master seed has been generated") != -1:
      print('初始化成功')
    elif logStr.find("already exists") != -1:
      print("已经存在")
    sp.poll()



def createClefAccount(dirname):
  cmd = f"clef --keystore {clefDataPath(dirname)}/keystore --stdio-ui newaccount --lightkdf"
  sp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,stdin=subprocess.PIPE)
  address = None
  password = dirname
  while sp.returncode == None:
    result = sp.stdout.readline()
    logStr = str(result, encoding="utf-8")
    print(logStr)
    if logStr.find("Please enter a password for the new account") != -1:
      sp.stdin.writelines([bytes(f"{password}\n", encoding="utf-8")])
      sp.stdin.flush()
      sp.stdin.writelines([bytes(f"{password}\n", encoding="utf-8")])
      sp.stdin.flush()
    elif logStr.find("Your new key was generated") != -1:
      print('账户创建成功')
    elif logStr.find("Generated account") != -1:
      address = logStr[18:]
      print('地址生成成功',address)
    sp.poll()
  assert address != None
  return address


def setpwClef(dirname, address): 
  cmd = f"clef --keystore {clefDataPath(dirname)}/keystore --configdir {clefDataPath(dirname)} --stdio-ui setpw {address}"
  sp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,stdin=subprocess.PIPE)
  password = dirname
  while sp.returncode == None:
    result = sp.stdout.readline()
    logStr = str(result, encoding="utf-8")
    print(logStr)
    if logStr.find("Please enter a password to store for this address") != -1:
      sp.stdin.writelines([bytes(f"{password}\n", encoding="utf-8")])
      sp.stdin.flush()
      sp.stdin.writelines([bytes(f"{password}\n", encoding="utf-8")])
      sp.stdin.flush()
    elif logStr.find("Decrypt master seed of clef") != -1:
      sp.stdin.writelines([bytes(f"{password}\n", encoding="utf-8")])
      sp.stdin.flush()
    elif logStr.find("Credential store updated") != -1:
      print('setpwClef成功')
    sp.poll()


def attestClef(dirname):
  rulesHash = "sha256sum /etc/bee-clef/rules.js | cut -d' ' -f1 | tr -d \'\n\'"
  cmd = f'clef --keystore {clefDataPath(dirname)}/keystore --configdir {clefDataPath(dirname)} --stdio-ui attest "$({rulesHash})"'
  sp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,stdin=subprocess.PIPE)
  password = dirname
  while sp.returncode == None:
    result = sp.stdout.readline()
    logStr = str(result, encoding="utf-8")
    print(logStr)
    if logStr.find("Decrypt master seed of clef") != -1:
      sp.stdin.writelines([bytes(f"{password}\n", encoding="utf-8")])
      sp.stdin.flush()
    elif logStr.find("Ruleset attestation updated") != -1:
      print('attest成功')
    sp.poll()

def startClef(dirname, callback):
  
  global clef_process
  print('开始启动clef')
  cmd = f"""
    clef --keystore {clefDataPath(dirname)}/keystore --configdir {clefDataPath(dirname)} --chainid 12345 --http --http.addr 0.0.0.0 --http.port 8551 --http.vhosts '*' --rules /etc/bee-clef/rules.js --nousb --lightkdf --ipcdisable --4bytedb-custom /etc/bee-clef/4byte.json --pcscdpath ""  --auditlog ""  --loglevel 3
  """
  print(cmd)
  password = dirname
  clef_process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,stdin=subprocess.PIPE)
  while clef_process.returncode == None:
    result = clef_process.stdout.readline()
    logStr = str(result, encoding="utf-8")
    print(logStr, flush=True)
    if logStr.find("Please enter the password to decrypt the master seed") != -1:
      clef_process.stdin.writelines([bytes(f"{password}\n", encoding="utf-8")])
      clef_process.stdin.flush()
      clef_process.stdin.writelines([bytes(f"{password}\n", encoding="utf-8")])
      clef_process.stdin.flush()
    elif logStr.find("Please enter password for signing data with account") != -1:
      clef_process.stdin.writelines([bytes(f"{password}\n", encoding="utf-8")])
      clef_process.stdin.flush()
    elif logStr.find("Enter 'ok' to proceed") != -1:
      clef_process.stdin.writelines([b"ok\n"])
      clef_process.stdin.flush()
    elif logStr.find("Rule engine configured") != -1:
      print("启动成功")
      callback()
    clef_process.poll()
  print('Clef退出',flush=True)

class Clef(threading.Thread):

  def __init__(self, password, callback):
    threading.Thread.__init__(self)
    self.password = password
    self.callback = callback

  def run(self):
    password = self.password
    from pathlib import Path
    masterseed_file = Path(f"{clefDataPath(password)}/masterseed.json")
    if not masterseed_file.exists():

      print('文件不存在，执行初始化流程。')
      Path(clefDataPath(password)).mkdir(parents=True)

      initClef(password)
      account = createClefAccount(password)
      setpwClef(password,account)
      attestClef(password)
    startClef(password, self.callback)

  

def startBee(dirname, callback):
  password = dirname
  global bee_process
  print('开始启动')
  
  cmd = f"""
    bee start {commandArgs} --password {password} --data-dir {beeDataPath(dirname)} --clef-signer-enable  --clef-signer-endpoint http://127.0.0.1:8551
  """
  print(cmd)
  bee_process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,stdin=subprocess.PIPE)
  
  while bee_process.returncode == None:
    result = bee_process.stdout.readline()
    logStr = str(result, encoding="utf-8")
    print(logStr, flush=True)
    if logStr.find("using ethereum address") != -1:
      splitList = logStr.split("using ethereum address")
      wallet = splitList[1][1:-2]
      print(wallet)
      callback(wallet)
      
    bee_process.poll()
  print('Bee退出',flush=True)

class Bee(threading.Thread):
  def __init__(self, password, callback):
    threading.Thread.__init__(self)
    self.password = password
    self.callback = callback

  def run(self):
    startBee(self.password, self.callback)

async def connectLeader():
  url = os.getenv("BEE_LEADER_WS_URL")
  # "ws://192.168.0.101:3000/ws"
  connection = await websockets.connect(url)
  await connection.send("Hi")
  password = await connection.recv()
  loop = asyncio.get_event_loop()
  print("获得密码:：",password)

  async def sendDone(wallet):
    await connection.send("Done")
    await connection.send(wallet)

  def bee_started(wallet):
    print('bee_started')
    loop.create_task(sendDone(wallet))
  def clef_started():
    print('clef_started')
    bee = Bee(password, bee_started)
    bee.start()


  clef = Clef(password, clef_started)
  clef.start()
  doneMessage = await connection.recv()
  print('收到完成消息，开始进入心跳轮训', doneMessage)
  if doneMessage == 'Done':
    while not connection.closed and bee_process.returncode == None and clef_process.returncode == None:
      await connection.send("ping")
      pong = await connection.recv()
      print(pong, flush=True)
      await asyncio.sleep(3)
    if bee_process.returncode == None:
      bee_process.kill()
    if clef_process.returncode == None:
      clef_process.kill()
    if not connection.closed:
      await connection.close()
    exit()

asyncio.get_event_loop().run_until_complete(connectLeader())
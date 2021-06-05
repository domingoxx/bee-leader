import sys,threading, subprocess, signal, os

commandArgs = " ".join(sys.argv[1:])



def beeDataPath(dirname):
  return f"/opt/data/{dirname}/bee"



def kill_child_processes(parent_pid, sig=signal.SIGTERM):
  ps_command = subprocess.Popen("ps -o pid --ppid %d --noheaders" % parent_pid, shell=True, stdout=subprocess.PIPE)
  ps_output = ps_command.stdout.read()
  ps_output = str(ps_output, encoding="utf-8")
  retcode = ps_command.wait()
  assert retcode == 0, "ps command returned %d" % retcode
  for pid_str in ps_output.split("\n")[:-1]:
    os.kill(int(pid_str), sig)





class Bee(threading.Thread):
  def __init__(self, datadir, callback):
    threading.Thread.__init__(self)
    self.datadir = datadir
    self.callback = callback
    self.bee_process = None

  def run(self):
    self.startBee(self.datadir, self.callback)

  def isRunning(self):
    return self.bee_process != None and self.bee_process.returncode == None

  def shutdown(self):
    if self.bee_process.returncode == None:
      print('send terminate bee', flush=True)
      kill_child_processes(self.bee_process.pid)
      self.bee_process.terminate()
      self.bee_process.wait(5)
      if self.bee_process.returncode == None:
        print(f'send kill bee {self.bee_process.pid}', flush=True)
        subprocess.check_output(f"kill -9 {self.bee_process.pid}", shell=True)

  def startBee(self, dirname, callback):
    
    print('开始启动')
    
    # --clef-signer-enable  --clef-signer-endpoint http://127.0.0.1:8551

    cmd = f"""
      bee start {commandArgs} --password {dirname} --data-dir {beeDataPath(dirname)} 
    """
    print(cmd)
    self.bee_process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,stdin=subprocess.PIPE)
    success = False
    while self.bee_process.returncode == None:
      result = self.bee_process.stdout.readline()
      logStr = str(result, encoding="utf-8")
      print(logStr, flush=True)
      if logStr.find("using ethereum address") != -1:
        splitList = logStr.split("using ethereum address")
        address = splitList[1][1:-2]
        print(address)
        success = True
        callback(address)
        
        
      self.bee_process.poll()
    if success == False:
      callback(None)
    print('Bee退出',flush=True)

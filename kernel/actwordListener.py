#!/usr/bin/python3

import zmq
import subprocess
import json
import datetime
import kernel

class actwordListener:
  """
  Class maintaining action word listener module.
  """

  def __init__(self, config):
    """
    Constuctor of the class.

    Args:
      config (json): config of the module

    Returns:
      None
    """

    self.config = config
    self.minPort = 5000
    self.maxPort = 5999
    self.maxRetries = 99
    self.port = None
    self.path = '../modules/dummy/dummy.py';
    self.configToSend = {}
    self.name = 'activation word module'

    # ZMQ
    self.zmqctx = zmq.Context()
    self.socket = self.zmqctx.socket(zmq.REQ)


  def execute(self):
    """
    Execute the subprocess and connect to server.

    Returns:
      None
    """

    # disconnect from previus socket
    if self.port != None:
      self.socket.disconnect('ipc://127.0.0.1:{}'.format(port))

    # select free port
    tmpSocket = self.zmqctx.socket(zmq.REP)
    self.port = tmpSocket.bind_to_random_port('ipc://127.0.0.1', self.minPort, self.maxPort, self.maxRetries)
    tmpSocket.unbind('ipc://127.0.0.1:{}'.format(self.port))

    # run the process
    self.process = subprocess.Popen([self.path, str(self.port)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # create client
    self.socket.connect('ipc://127.0.0.1:{}'.format(self.port))

  def start(self):
    """
    Start the module.

    Returns:
      None
    """

    self.execute()


  def stop(self):
    """
    Terminate the module.

    Returns:
      None
    """

    self.process.terminate()


  def sendReply(self, data):
    """
    Constructs the message from given data and sends it to the server. Waits for the reply, parse it and return received data.

    Args:
      data (dict): data to send in dictionary

    Returns:
      dict: received data
    """

    # prepare the data to send
    timestamp = datetime.datetime.now().isoformat(' ')
    message = {'data': data, 'config': self.configToSend, 'timestamp': timestamp}

    # send
    reply = self.commJSON(message)

    # parse the reply
    print(reply['config'])
    if reply['config']['state'] == 'accepted':
      if 'data' in reply:
        return reply['data']
      else:
        raise kernel.CommunicationError('Communication with "Activation word module" failed (no field "data" in reply)')
    elif reply['config']['state'] == 'failed':
      raise kernel.ConfigError(self.name)
    else:
      raise kernel.CommunicationError('Communication with "Activation word module" failed (state of configuration badly defined).')


  def comm(self, message):
    """
    Sends string to the server and waits for the reply.

    Args:
      message (str): message to send

    Returns:
      str: received massage
    """

    #check the process is running
    if self.process.poll() != None:
      self.execute()
    
    self.socket.send_string(message)
    return self.socket.recv().decode('utf-8')


  def commJSON(self, dct):
    """
    Converts dictionary to a JSON string and sends it to the server. Then waits for the reply and converts is back to dictionary.

    Args:
      dct (dict): dictionary to send

    Returns:
      dict: received reply as dictionary
    """

    return json.loads(self.comm(json.dumps(dct)))

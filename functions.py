import numpy as np
import paramiko
from io import StringIO
import random
# returns the vector containing stock data from a fixed file
def getDataVec(key,op):
	vec = []
	lines = open(f'./data/{op}/{key}.csv', "r").read().splitlines()

	for line in lines[1:]:
		vec.append(float(line.split(",")[1]))

	return vec

def sshConnection(address,cmd):
    f = open('/home/sh4n1/shell-scripting/vmi3.pem','r')
    s = f.read()
    keyfile = StringIO(s)
    mykey = paramiko.RSAKey.from_private_key(keyfile)
    mastervm = paramiko.SSHClient()
    mastervm.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print ("connecting")
    mastervm.connect( hostname = address, username = "ubuntu", pkey = mykey  )
    print ("connected")
    stdin , stdout, stderr =mastervm.exec_command(cmd)
    print (stdout.read())
    print (stderr.read())
    mastervm.close()

def retCpuMax():
	return 11703.99824
#print(getDataVec('1')) #returns closing value

# returns the sigmoid
def sigmoid(x):
	return 1 / (1 + np.exp(-x))

# returns an an n-day state representation ending at time t
def getState(data, t, n):
	d = t - n + 1
	block = data[d:t + 1] if d >= 0 else -d * [data[0]] + data[0:t + 1] # pad with t0
	res = []
	for i in range(n - 1):
		res.append(sigmoid(block[i + 1] - block[i]))
	return np.array([res])

def calcReward(action,data):
    print('curr_data->',data)
    if action == 0: #NormalLoad
        if(data>=20 and data<80):
            reward=1
        else:
            reward=-1
    elif action == 1: #OverLoad
        print("OverLoad")
        if(data>=80):
            reward=1
        else:
            reward=-1
    elif action == 2: #UnderLoad
        print("UnderLoad")
        if(data<20):
            reward=1
        else:
            reward=-1
    return reward

def getDataCeilometer():
    cmd='ceilometer --os-username admin --os-password admin_pass --os-project-id 2448c5574f994284a0de2604962a55a0 --os-user-domain-name default --os-auth-url http://192.168.31.2/v3/  sample-list --meter cpu_util'
    # mastervm = paramiko.SSHClient()
    # mastervm.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # print ("connecting")

    # address='controllerIP'
    # mykey='key'
    
    # mastervm.connect( hostname = address, username = "ubuntu", pkey = mykey  )
    # print ("connected")
    # stdin , stdout, stderr =mastervm.exec_command(cmd)
    k=random.randint(0,100)
    print('ceilometer->',k)
    return k

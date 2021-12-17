import random
import time
from keras.saving.saved_model.load import load
import numpy
import paramiko
from io import StringIO
from agent import Agent
from functions import *
import sys
import datetime
import pandas as pd
from keras.models import load_model

df=pd.DataFrame(columns=['ip','threads','datetime'])
availableIps=['192.168.31.65','192.168.31.55','192.168.31.61']
NUMBER_OF_LOADS=100
SLEEP_TIME=3 #minutes
startTime=datetime.datetime.now()

window_size = 3  # input shape
agent = Agent(window_size)
agent1 = Agent(window_size)
fullData =[]
fullData1=[]

#private key loading
pKeyPath = open('/home/sh4n1/shell-scripting/vmi3.pem','r')
stringKey = pKeyPath.read()
keyfile = StringIO(stringKey)
mykey = paramiko.RSAKey.from_private_key(keyfile)

#VM connection
vm = paramiko.SSHClient()
vm.set_missing_host_key_policy(paramiko.AutoAddPolicy())
print ("connecting to 1st VM")
vm.connect( hostname = availableIps[0], username = "ubuntu", pkey = mykey  )
print ("connected to 1st VM")

vm1 = paramiko.SSHClient()
vm1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
print ("connecting to 2nd VM")
vm1.connect( hostname = availableIps[1], username = "ubuntu", pkey = mykey  )
print ("connected to 2nd VM")

wrong=0
wrong1=0

#initial cpu_util
dataNow = getDataCeilometer()
fullData.append(dataNow)
data1Now = getDataCeilometer()
fullData1.append(data1Now)

for x in range(NUMBER_OF_LOADS):
    if(x==NUMBER_OF_LOADS*70/100):
        agent.model.save("models/my_modela")
        agent1.model.save("models/my_modela1")

        agent=Agent(window_size,True,'my_modela')
        agent1=Agent(window_size,True,'my_modela1')
        wrong=0
        wrong1=0
    print('-------------------------------')
    print('LOAD NUMEBR: ',x)
    #for random load at random time
    #time.sleep(60*SLEEP_TIME)
    #cpu_util now 
    dataNow = getDataCeilometer()
    fullData.append(dataNow)
    data1Now = getDataCeilometer()
    fullData1.append(data1Now)
    print('State now:',fullData[x],fullData1[x])
    state = getState(fullData, x, window_size + 1)
    state1= getState(fullData1, x, window_size + 1)
    
    action = agent.act(state)
    action1 = agent1.act(state)
    
    toIp=0
    if(action==action1):
        if(fullData[x]<fullData1[x]):
            toIp=1
        else:
            toIp=0
    elif(action==0): #1st vm mediumload
        if(action1==1):
            toIp=1 #2nd vm overload
        elif(action1==2):
            toIp=0 #2nd vm underload
    elif(action==1): #1st vm overload
        toIp=0
    elif(action==2):  #1st vm underload
        toIp=1

    print('action:',action,'action 1:',action1)
    currIp=availableIps[toIp]
    print('To IP->',currIp)
    threads=random.randint(2,10)
    threads=str(threads)
    print('Number of threads->',threads)
    df.append({'ip':currIp,'threads':threads,'datetime':datetime.datetime.now()},ignore_index=True)
    cmd="sysbench --test=cpu --cpu-max-prime="+threads+" run"
    if(toIp==0):
        stdin,stdout,stderr=vm.exec_command(cmd)
        print(stdout.read())
        print(stderr.read())
    elif(toIp==1):
        stdin,stdout,stderr=vm1.exec_command(cmd)
        print(stdout)
        print(stderr)

    reward=calcReward(action,dataNow)    
    reward1=calcReward(action1,data1Now)
    if(reward!=1):
        wrong=wrong+1
        print('here')
    if(reward1!=1):
        wrong1=wrong1+1
        print('here')
    next_state = getState(fullData, x + 1, window_size + 1)
    next_state1 = getState(fullData1, x + 1, window_size + 1)
    print('next->',fullData[x+1],fullData1[x+1])
    #check if done
    if(x==NUMBER_OF_LOADS-1):
        done=True
    else:
        done=False
    agent.memory.append((state, action, reward, next_state, done))
    agent1.memory.append((state1, action1, reward1, next_state1, done))
    state1 = next_state1
    state = next_state
    
    print('-------------------------------')

print("--------------------------------")
print("Done with accuracy",float(1-(wrong/NUMBER_OF_LOADS)))
print("--------------------------------")


#closing
vm.close()
vm1.close()
endTime=datetime.datetime.now()
print("Total execution time = " + str(endTime-startTime))
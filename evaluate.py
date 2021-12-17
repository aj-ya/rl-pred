import keras
from keras.models import load_model
from agent import Agent
from functions import *
import sys

if len(sys.argv) != 3:
    print("Usage: python evaluate.py [vm] [model]")
    exit()

vm_name, model_name = sys.argv[1], sys.argv[2]  # csv file and model name, default null
model = load_model("models/" + model_name)  # loads model
window_size = model.layers[0].input.shape.as_list()[1]  # input shape
agent = Agent(window_size, True, model_name)
data = getDataVec(vm_name,'test')
l = len(data) - 1
#batch_size = 32
state = getState(data, 0, window_size + 1)
wrong=0
for t in range(l):
	action = agent.act(state)

	load_diff = data[t] - data[t - 1]
	reward = 0

	high=80*retCpuMax()/100
	low=20*retCpuMax()/100
	if action == 0: #NormalLoad
		print("NormalLoad")
		if(data[t]>low and data[t]<high):
			reward=1
			wrong-=1
		else:
			reward=-1
	elif action == 1: #OverLoad
		print("OverLoad")
		if(data[t]>high):
			reward=1
			wrong-=1
		else:
			reward=-1
	elif action == 2: #UnderLoad
		print("UnderLoad")
		if(data[t]<low):
			reward=1
			wrong-=1
		else:
			reward=-1
			
	wrong+=1
	done = True if t == l - 1 else False
	next_state = getState(data, t + 1, window_size + 1)
	agent.memory.append((state, action, reward, next_state, done))
	state = next_state
	if done:
		print("--------------------------------")
		print("Done with accuracy",float(1-(wrong/l)))
		print("--------------------------------")

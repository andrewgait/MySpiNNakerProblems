#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#!/usr/bin/env python
# coding: utf-8

# In[1]:


#Training and classificaiton set creation

train_set=['ABCB', 'CBBD', 'CBBB', 'DAAE', 'DDAC', 'AECB', 'ADEC', 'CCCB', 'DCBB', 'EEAD', 'DEBE', 'DAEC', 'CBBE', 'ACEB', 'DECD', 'DDEC', 'CBED', 'BBBD', 'BEAE', 'ACCA', 'EACD', 'EECA', 'CAAE', 'ECBE', 'AAAE', 'ACBE','BADE', 'DCCB', 'ACCE', 'ACDB', 'DDEB', 'DCEC', 'DDCC', 'DDDC', 'DCBD', 'DCBC', 'DCAE', 'DCBE', 'CECD', 'BECD', 'EEED', 'EBCD', 'BBAE', 'BAAB', 'BCAE', 'BAAD', 'CABD','CBBA', 'CBCD', 'CBAD']
test_set=['BADE', 'DCCB', 'ACCE', 'ACDB', 'DDEB', 'DCEC', 'DDCC', 'DDDC', 'DCBD', 'DCBC', 'DCAE', 'DCBE', 'CECD', 'BECD', 'EEED', 'EBCD', 'BBAE', 'BAAB', 'BCAE', 'BAAD', 'CABD','CBBA', 'CBCD', 'CBAD']
class_set=['ACCD', 'EECB', 'CCBD', 'DABE', 'EECD', 'DCDE', 'EEBD', 'BDEC', 'BAEE', 'DDED', 'EDEC', 'DBBE', 'BAAE', 'EBBD', 'ADCB', 'ACCB']


# In[2]:


import pyNN.spiNNaker as sim
import pyNN.utility.plotting as plot
import random as rnd
import numpy as np
import re
from python_models8.neuron.builds.my_model_curr_exp import MyModelCurrExp
from python_models8.neuron.builds.if_curr_exp_my_threshold import (
    IFCurrExpMyThreshold)


# In[3]:


#Input rate definition

input_rate_train=[]
for data in train_set:
    input_rate=[]
    for i in range(4):
        if data[i]=='A':
            input_rate.append(50)
        elif data[i]=='B':
            input_rate.append(100)
        elif data[i]=='C':
            input_rate.append(200)
        elif data[i]=='D':
            input_rate.append(150)
        elif data[i]=='E':
            input_rate.append(0)
        else:
            print("Error")
    input_rate_train.append(input_rate)

input_rate_test=[]
for data in test_set:
    input_rate=[]
    for i in range(4):
        if data[i]=='A':
            input_rate.append(300)
        elif data[i]=='B':
            input_rate.append(200)
        elif data[i]=='C':
            input_rate.append(100)
        elif data[i]=='D':
            input_rate.append(400)
        elif data[i]=='E':
            input_rate.append(0)
        else:
            print("Error")
    input_rate_test.append(input_rate)

input_rate_class=[]
for data in class_set:
    input_rate=[]
    for i in range(4):
        if data[i]=='A':
            input_rate.append(300)
        elif data[i]=='B':
            input_rate.append(200)
        elif data[i]=='C':
            input_rate.append(100)
        elif data[i]=='D':
            input_rate.append(400)
        elif data[i]=='E':
            input_rate.append(0)
        else:
            print("Error")
    input_rate_class.append(input_rate)


# In[4]:


input_0=[]
input_1=[]
input_2=[]
input_3=[]
beg=[0]
durations_sim=[]
for i in range (len(input_rate_train)):
    input_0.append(input_rate_train[i][0])
    input_1.append(input_rate_train[i][1])
    input_2.append(input_rate_train[i][2])
    input_3.append(input_rate_train[i][3])
    durations_sim.append(350)
    beg.append(beg[-1]+500)
beg.pop()


# In[5]:


theta_delay_tau = 100

excit_param = {'tau_m': 100.0,
               'cm': 100.0,
               'v_rest': -65.04,
               'v_reset': -65.0,
               'tau_refrac': 5.0,
               'tau_syn_E': 1.0,
               'tau_syn_I': 2.0,
               'i_offset': 0,
               'tau_th': theta_delay_tau,


               'threshold_value': -44.95}
#x,'DDEB', 'ABCB', 'CBBD', 'DCBD', 'CBBB'
sim.setup(0.1)
simtime=beg[-1]+400
#input = sim.Population(2,sim.SpikeSourcePoisson(rate=[800,700]))
pop = sim.Population(12, IFCurrExpMyThreshold(**excit_param), label="pop")
# pop = sim.Population(12, sim.IF_curr_exp, {},label="pop")
pop_in = sim.Population(4, sim.extra_models.SpikeSourcePoissonVariable(
        rates=[input_0,input_1,input_2,input_3],
        starts=[beg,beg,beg,beg],
        durations=[durations_sim,durations_sim,durations_sim,durations_sim]),
        label="pop_c")

connections=[[],[],[],[],[],[],[],[],[],[],[],[]]
for i in range (12):
    for j in range(12):
        if i!=j:
            connections[i].append((i, j, 0.007, 0))

inh = sim.Population(12,sim.IF_curr_exp(v_thresh = -60,v_reset=-61))

exc_proj = sim.Projection(pop,inh,sim.OneToOneConnector(),synapse_type=sim.StaticSynapse(weight=5,delay=0))
inh_proj_0 = sim.Projection(inh,pop,sim.FromListConnector(connections[0]), sim.StaticSynapse(), receptor_type="inhibitory")
inh_proj_1 = sim.Projection(inh,pop,sim.FromListConnector(connections[1]), sim.StaticSynapse(), receptor_type="inhibitory")
inh_proj_2 = sim.Projection(inh,pop,sim.FromListConnector(connections[2]), sim.StaticSynapse(), receptor_type="inhibitory")
inh_proj_3 = sim.Projection(inh,pop,sim.FromListConnector(connections[3]), sim.StaticSynapse(), receptor_type="inhibitory")
inh_proj_4 = sim.Projection(inh,pop,sim.FromListConnector(connections[4]), sim.StaticSynapse(), receptor_type="inhibitory")
inh_proj_5 = sim.Projection(inh,pop,sim.FromListConnector(connections[5]), sim.StaticSynapse(), receptor_type="inhibitory")
inh_proj_6 = sim.Projection(inh,pop,sim.FromListConnector(connections[6]), sim.StaticSynapse(), receptor_type="inhibitory")
inh_proj_7 = sim.Projection(inh,pop,sim.FromListConnector(connections[7]), sim.StaticSynapse(), receptor_type="inhibitory")
inh_proj_8 = sim.Projection(inh,pop,sim.FromListConnector(connections[8]), sim.StaticSynapse(), receptor_type="inhibitory")
inh_proj_9 = sim.Projection(inh,pop,sim.FromListConnector(connections[9]), sim.StaticSynapse(), receptor_type="inhibitory")
inh_proj_10 = sim.Projection(inh,pop,sim.FromListConnector(connections[10]), sim.StaticSynapse(), receptor_type="inhibitory")
inh_proj_11 = sim.Projection(inh,pop,sim.FromListConnector(connections[11]), sim.StaticSynapse(), receptor_type="inhibitory")



# In[6]:


w_values=[]
for i in range(len(pop)*len(pop_in)):
    prob=rnd.random()
    w_values.append(prob/3)

#STDP connection
timing = sim.SpikePairRule(tau_plus=10.0, tau_minus=10.0, A_plus=0.01, A_minus=0.01)
weight = sim.AdditiveWeightDependence(w_min=0.0, w_max=6.0)
proj = sim.Projection(pop_in, pop, sim.AllToAllConnector(), sim.STDPMechanism(timing_dependence=timing, weight_dependence=weight, weight=w_values))


# In[7]:


pop.record(["spikes","v"])
pop_in.record(["spikes"])
inh.record(["spikes"])

#input.record(["spikes"])


# In[ ]:


## TRAINING PHASE


# In[ ]:


spikes_train_t=[]
for i in range(len(train_set)):
    spikes_train_t.append([])
for j in range(1):
    print("EPOCH: ")
    print(j)
    for k in range(len(train_set)):
        print("TRAIN SET: ")
        print(k)
        sim.run(350)
        neo = pop.get_data(variables=["spikes", "v"])
        spikes = neo.segments[0].spiketrains
        v = neo.segments[0].filter(name='v')[0]

        neo_3 = pop_in.get_data(variables=["spikes"])
        spikes_3 = neo_3.segments[0].spiketrains
        if k==0:
            for i in range(12):
                spikes_train_t[0].append(len(spikes[i]))

        else:
            for i in range(12):
                spikes_train_t[k].append(len(spikes[i])-len(spikes_before[i]))
        spikes_before=spikes
#         pop.set(tau_th=0.01)
        pop.set(i_offset=0.01)
        sim.run(150)
#         pop.set(tau_th=theta_delay_tau)
        pop.set(i_offset=0.0)


# In[ ]:


print(spikes_train_t)


# In[ ]:


plot.Figure(
    # plot voltage for first ([0]) neuron
    plot.Panel(v, ylabel="Membrane potential (mV)",
               yticks=True, xlim=(0, 1000)),
    # plot spikes (or in this case spike)
    plot.Panel(spikes_3, yticks=True, markersize=5, xlim=(0, 1000)),
    title="Simple Example",
    annotations="Simulated with {}".format(sim.name()),

)


# In[ ]:


"""
plot.Figure(
    # plot voltage for first ([0]) neuron
    plot.Panel(v, ylabel="Membrane potential (mV)",
               yticks=True, xlim=(0, 200)),
    # plot spikes (or in this case spike)
    plot.Panel(spikes_3, yticks=True, markersize=5, xlim=(0, 200)),
    title="Simple Example",
    annotations="Simulated with {}".format(sim.name()),

)
"""


# In[ ]:


#print(proj.get('weight', format='list'))


# In[ ]:


"""
lista=proj.get('weight', format='list')
connez=[]
for h in range(len(lista)):
    tmp_list=[]
    tmp_list.append(lista[h][0])
    tmp_list.append(lista[h][1])
    tmp_list.append(lista[h][2])
    tmp_list.append(0)
    connez.append((lista[h][0],lista[h][1],lista[h][2],0))

"""


# In[ ]:


#sim.end()


# In[ ]:


"""
input_0=[]
input_1=[]
input_2=[]
input_3=[]
beg=[0]
durations_sim=[]
for i in range (len(input_rate_test)):
    input_0.append(input_rate_test[i][0])
    input_1.append(input_rate_test[i][1])
    input_2.append(input_rate_test[i][2])
    input_3.append(input_rate_test[i][3])
    durations_sim.append(200)
    beg.append(beg[-1]+400)
beg.pop()
"""


# In[ ]:


"""
theta_delay_tau = 100

excit_param = {'tau_m': 100.0,
               'cm': 100.0,
               'v_rest': -65.04,
               'v_reset': -65.0,
               'tau_refrac': 5.0,
               'tau_syn_E': 1.0,
               'tau_syn_I': 2.0,
               'i_offset': 0,
               'tau_th': theta_delay_tau,


               'threshold_value': -44.95}
'
sim.setup(0.1)
simtime=beg[-1]+250

pop = sim.Population(12, IFCurrExpMyThreshold(**excit_param), {},label="pop")
pop_in = sim.Population(4, sim.extra_models.SpikeSourcePoissonVariable(
        rates=[input_0,input_1,input_2,input_3],
        starts=[beg,beg,beg,beg],
        durations=[durations_sim,durations_sim,durations_sim,durations_sim]),
        label="pop_c")
connections=[[],[],[],[],[],[],[],[],[],[],[],[]]
for i in range (12):
    for j in range(12):
        if i!=j:
            connections[i].append((i, j, 0.2, 0))

inh = sim.Population(12,sim.IF_curr_exp(v_thresh = -60,v_reset=-61))
inh_proj_0 = sim.Projection(inh,pop,sim.FromListConnector(connections[0]), sim.StaticSynapse(), receptor_type="inhibitory")
inh_proj_1 = sim.Projection(inh,pop,sim.FromListConnector(connections[1]), sim.StaticSynapse(), receptor_type="inhibitory")
inh_proj_2 = sim.Projection(inh,pop,sim.FromListConnector(connections[2]), sim.StaticSynapse(), receptor_type="inhibitory")
inh_proj_3 = sim.Projection(inh,pop,sim.FromListConnector(connections[3]), sim.StaticSynapse(), receptor_type="inhibitory")
inh_proj_4 = sim.Projection(inh,pop,sim.FromListConnector(connections[4]), sim.StaticSynapse(), receptor_type="inhibitory")
inh_proj_5 = sim.Projection(inh,pop,sim.FromListConnector(connections[5]), sim.StaticSynapse(), receptor_type="inhibitory")
inh_proj_6 = sim.Projection(inh,pop,sim.FromListConnector(connections[6]), sim.StaticSynapse(), receptor_type="inhibitory")
inh_proj_7 = sim.Projection(inh,pop,sim.FromListConnector(connections[7]), sim.StaticSynapse(), receptor_type="inhibitory")
inh_proj_8 = sim.Projection(inh,pop,sim.FromListConnector(connections[8]), sim.StaticSynapse(), receptor_type="inhibitory")
inh_proj_9 = sim.Projection(inh,pop,sim.FromListConnector(connections[9]), sim.StaticSynapse(), receptor_type="inhibitory")
inh_proj_10 = sim.Projection(inh,pop,sim.FromListConnector(connections[10]), sim.StaticSynapse(), receptor_type="inhibitory")
inh_proj_11 = sim.Projection(inh,pop,sim.FromListConnector(connections[11]), sim.StaticSynapse(), receptor_type="inhibitory")

in_exc=sim.Projection(pop_in,pop,sim.FromListConnector(connez), sim.StaticSynapse())
exc_proj = sim.Projection(pop,inh,sim.OneToOneConnector(),synapse_type=sim.StaticSynapse(weight=5,delay=0))
"""


# In[ ]:


"""
pop.record(["spikes","v"])
pop_in.record(["spikes"])
"""

#input.record(["spikes"])


# In[ ]:


"""
spikes_train_ts=[]
for i in range(len(test_set)):
    spikes_train_ts.append([])

for k in range(len(test_set)):
    sim.run(400)
    neo = pop.get_data(variables=["spikes", "v"])
    spikes = neo.segments[0].spiketrains
    v = neo.segments[0].filter(name='v')[0]

    neo_3 = pop_in.get_data(variables=["spikes"])
    spikes_3 = neo_3.segments[0].spiketrains
    if k==0:
        for i in range(12):
            spikes_train_ts[0].append(len(spikes[i]))

    else:
        for i in range(12):
            spikes_train_ts[k].append(len(spikes[i])-len(spikes_before[i]))
    spikes_before=spikes
"""


# In[ ]:


#print(spikes_train_ts)


# In[ ]:


#sim.end()


# In[ ]:


"""
input_0=[]
input_1=[]
input_2=[]
input_3=[]
beg=[0]
durations_sim=[]
for i in range (len(input_rate_class)):
    input_0.append(input_rate_class[i][0])
    input_1.append(input_rate_class[i][1])
    input_2.append(input_rate_class[i][2])
    input_3.append(input_rate_class[i][3])
    durations_sim.append(200)
    beg.append(beg[-1]+400)
beg.pop()
"""


# In[ ]:


"""
theta_delay_tau = 100

excit_param = {'tau_m': 100.0,
               'cm': 100.0,
               'v_rest': -65.04,
               'v_reset': -65.0,
               'tau_refrac': 5.0,
               'tau_syn_E': 1.0,
               'tau_syn_I': 2.0,
               'i_offset': 0,
               'tau_th': theta_delay_tau,


               'threshold_value': -44.95}

sim.setup(0.1)
simtime=beg[-1]+250

pop = sim.Population(12, IFCurrExpMyThreshold(**excit_param), {},label="pop")
pop_in = sim.Population(4, sim.extra_models.SpikeSourcePoissonVariable(
        rates=[input_0,input_1,input_2,input_3],
        starts=[beg,beg,beg,beg],
        durations=[durations_sim,durations_sim,durations_sim,durations_sim]),
        label="pop_c")
connections=[[],[],[],[],[],[],[],[],[],[],[],[]]
for i in range (12):
    for j in range(12):
        if i!=j:
            connections[i].append((i, j, 0.2, 0))

inh = sim.Population(12,sim.IF_curr_exp(v_thresh = -60,v_reset=-61))
inh_proj_0 = sim.Projection(inh,pop,sim.FromListConnector(connections[0]), sim.StaticSynapse(), receptor_type="inhibitory")
inh_proj_1 = sim.Projection(inh,pop,sim.FromListConnector(connections[1]), sim.StaticSynapse(), receptor_type="inhibitory")
inh_proj_2 = sim.Projection(inh,pop,sim.FromListConnector(connections[2]), sim.StaticSynapse(), receptor_type="inhibitory")
inh_proj_3 = sim.Projection(inh,pop,sim.FromListConnector(connections[3]), sim.StaticSynapse(), receptor_type="inhibitory")
inh_proj_4 = sim.Projection(inh,pop,sim.FromListConnector(connections[4]), sim.StaticSynapse(), receptor_type="inhibitory")
inh_proj_5 = sim.Projection(inh,pop,sim.FromListConnector(connections[5]), sim.StaticSynapse(), receptor_type="inhibitory")
inh_proj_6 = sim.Projection(inh,pop,sim.FromListConnector(connections[6]), sim.StaticSynapse(), receptor_type="inhibitory")
inh_proj_7 = sim.Projection(inh,pop,sim.FromListConnector(connections[7]), sim.StaticSynapse(), receptor_type="inhibitory")
inh_proj_8 = sim.Projection(inh,pop,sim.FromListConnector(connections[8]), sim.StaticSynapse(), receptor_type="inhibitory")
inh_proj_9 = sim.Projection(inh,pop,sim.FromListConnector(connections[9]), sim.StaticSynapse(), receptor_type="inhibitory")
inh_proj_10 = sim.Projection(inh,pop,sim.FromListConnector(connections[10]), sim.StaticSynapse(), receptor_type="inhibitory")
inh_proj_11 = sim.Projection(inh,pop,sim.FromListConnector(connections[11]), sim.StaticSynapse(), receptor_type="inhibitory")

in_exc=sim.Projection(pop_in,pop,sim.FromListConnector(connez), sim.StaticSynapse())
exc_proj = sim.Projection(pop,inh,sim.OneToOneConnector(),synapse_type=sim.StaticSynapse(weight=5,delay=0))
"""


# In[ ]:


"""
pop.record(["spikes","v"])
pop_in.record(["spikes"])
"""


# In[ ]:


"""
spikes_train_cl=[]
for i in range(len(class_set)):
    spikes_train_cl.append([])

for k in range(len(class_set)):
    sim.run(400)
    neo = pop.get_data(variables=["spikes", "v"])
    spikes = neo.segments[0].spiketrains
    v = neo.segments[0].filter(name='v')[0]

    neo_3 = pop_in.get_data(variables=["spikes"])
    spikes_3 = neo_3.segments[0].spiketrains
    if k==0:
        for i in range(12):
            spikes_train_cl[0].append(len(spikes[i]))

    else:
        for i in range(12):
            spikes_train_cl[k].append(len(spikes[i])-len(spikes_before[i]))
    spikes_before=spikes
"""


# In[ ]:


#print(spikes_train_cl)


# In[ ]:





# In[ ]:





#!/usr/bin/env python
# coding: utf-8

# In[1]:



'''LOG PAVAN-30th May
Found that if splitters are used the weights are not increasing else the neuromdulated weights are increasing.So created the
following version of Code with raster plotsand weight updation plots.

'''

'''
LOG BASAB - 16th May:
(A) Pavan is to now introduce a stim_1 as well as the stim_0 -- in the LIF codes -
although our preferred stim will still be stim_0, so the DA delivery times remain
unchanged.
(B) After writing the code - PAvan to send to Basab for approval - before continuing with the testing

********************************************

LOG PAVAN-15th MAY EVENNING-REPLACED LIF NEURON WITH IZK NEURONS WITH APPROPRIATE CHANGES


LOG BASAB - 14TH MAY EVENING - 15TH MAY
Added the weight recording code here and since manually slicing stim pop - kept the ex:inh==4:1.

PAVAN TO REPLACE LIF NEURON WITH IZK NEURONS AND SEND BACK - DO NOT DISTURB ANY OTHER PART OF THE CODE.

*******************************************
LOG PAVAN:on 14th May evening

Introducing Spike source array-

I have removed Original.sample function instead used Original.__getitem__(slice(760, 810)
because when we use spikesource array and project it to stimulus it is not allowing projection to
randomy sampled neurons i.e,[m,n].But it allows slice as [m:n]


Reward population are firing according to the DA delivery times mentioned.
*******************************************************

LOG BASAB 13th May evening: ok - the stdp mechanism is up and running and impacts the raster.
The reward mechanism also impacts - as a simple test - I removed them
and the network went bonkers after a few time steps. Brought them back and network back to stable.


The NPG[0] stimulus population is now responding even when it is not receiving supra-threshold current input.
I increased the total run time - and checked until 180 seconds (3 mins) - set currently -
and network is stable.


DOABLES FOR PAVAN HEREON:

(1) (a) record all neuromodulated weights and plot the progression
    (b) look closely at the reward pop spike times  - are they at a difference or at the same time? if the
    latter - why? debug

(2) MAKE A COPY OF THE CODE AND DO THE FOLLOWING:
    (A) REPLACE CURRENT PULSE WITH SPIKESOURCEARRAY - this will take care of the time to run - current run times
    are not feasible

(3) MAKE ANOTHER COPY OF THE CODE AND DO THE FOLLOWING:
    (A) Replace LIF with Izhikevich conductance based neurons.

(4) MAKE a third COPY OF THE CODE AND DO THE FOLLOWING:
    (a) Bring in another stimulus - i.e. S0 and S1, where S1 is our preferred stimulus.

    '''


# '''CODE: CREATED BY PAVAN; DESIGNED BY BSB
#
# TESTING BSB: LOG 12-13 MAY -
#
# 1. TOTAL DURATION HAS ANY EFFECT ON THE TOTAL RUNTIME?
#     currently the run stops when the S1 stimuli time stops! How can we make this to run the whole duration?
# 2. CAN WE PLOT THE STIMULUS NEURONS USING SPINNAKER.GET.DATA? =
# --- BSB: checked with Andy and confirmed with Christian - and he said that this is not going to go away anytime soon - definitely not for the duration of your PhD.
# 3. WE HAVE A BALANCED RANDOM NETWORK - CAN WE USE THOSE PARAMETERS?
# 4. NEED TO RECORD THE WEIGHTS TO SEE HOW THEY ARE PROGRESSING - AND VISUALISE
# 5. SPIKESOURCEARRAY: WILL ALLOW LARGER TIME SIMULATIONS
# 6. NEO DOCUMENTATION: http://spinnakermanchester.github.io/spynnaker/4.0.0/PyNN0.8vsPyNN0.75.pdf
# '''

# In[2]:



import pyNN.spiNNaker as p
import numpy as np
from numpy import *
import time
from pyNN.random import RandomDistribution, NumpyRNG
start_time = time.time()

from spinn_front_end_common.utilities import globals_variables
from quantities import ms
import neo

#for plotting
import matplotlib.pyplot as plt
import pyNN.utility.plotting as plot
from pyNN.utility.plotting import Figure, Panel, Histogram
# get_ipython().run_line_magic('matplotlib', 'inline')

import random
rng=np.random.default_rng()


# In[3]:


from spynnaker.pyNN.extra_algorithms.splitter_components import (
SplitterAbstractPopulationVertexNeuronsSynapses, SplitterPoissonDelegate)


# In[4]:


# from spynnaker.pyNN.extra_algorithms.splitter_components import (
#     SplitterAbstractPopulationVertexSlice)


# In[5]:


Total_Duration=50000##msec - at a resolution of 1 msec --> 180 seconds i.e. 3 minutes
nFS = 20
nRS = 80
chooseFS = 1
chooseRS = 4

# In[6]:


RS_cell_params = {'cm': 0.3,  # nF
               'i_offset': 0.005,
               'tau_m': 10.0,
               'tau_refrac': 4.0,
               'tau_syn_E': 1.0,
               'tau_syn_I': 1.0,
               'v_reset': -70.0,
               'v_rest': -65.0,
               'v_thresh': -55.4
               }


# In[7]:


FS_cell_params = {'cm': 0.3,  # nF
               'i_offset': 0.0,
               'tau_m': 10.0,
               'tau_refrac': 2.0,
               'tau_syn_E': 1.0,
               'tau_syn_I': 1.0,
               'v_reset': -70.0,
               'v_rest': -65.0,
               'v_thresh': -56.4
               }


# In[8]:


# %%capture --no-display
p.setup(timestep=0.1)
p.set_number_of_neurons_per_core(p.IF_curr_exp,100)


# In[9]:


RS_neurons=p.Population(nRS, p.IF_curr_exp, {}, label="rs",
                        additional_parameters={
                            "splitter": SplitterAbstractPopulationVertexNeuronsSynapses(1)})


# In[10]:


FS_neurons=p.Population(nFS, p.IF_curr_exp, {}, label="fs",
                        additional_parameters={
                            "splitter": SplitterAbstractPopulationVertexNeuronsSynapses(1)})


# In[11]:


RS_neurons.set(cm= 0.3, i_offset= 0.005,
               tau_m= 10.0,
               tau_refrac= 4.0,
               tau_syn_E= 1.0,
               tau_syn_I= 1.0,
               v_reset= -70.0,
               v_rest= -65.0,
               v_thresh= -55.4)


# In[12]:


FS_neurons.set(cm= 0.3, i_offset= 0.0,
               tau_m= 10.0,
               tau_refrac= 2.0,
               tau_syn_E= 1.0,
               tau_syn_I= 1.0,
               v_reset= -70.0,
               v_rest= -65.0,
               v_thresh= -56.4)


# In[13]:


# '''Pavan log I am introducing a variable neurons_per_stimulus '''
# '''Pavan Log:I have removed Original.sample function instead used Original.__getitem__(slice(760, 810)
# because when we use spikesource array and project it to stimulus it is not allowing projection to
# randomy sampled neurons.But it allows slice as follows'''
# neurons_per_stimulus=50
# NPG=[]
# num_stimulus=1
# for i in range(0,num_stimulus):
#     NPG.append(Original.__getitem__(slice(775, 825)))



# In[14]:


'''Pavan log:As we are using slice we can't use above cell for loop.So manually selecting the slice
index as below'''
neurons_per_stimulus=chooseFS+chooseRS
NPG=[]
num_stimulus=1


# In[15]:


spike_source_Poisson_base_rs = p.Population(nRS, p.SpikeSourcePoisson, {'rate': 3, 'duration': Total_Duration,'start': 0.0}, label='spike_source_Poisson_base') #, additional_parameters={"splitter": SplitterPoissonDelegate()})

spike_source_Poisson_base_fs = p.Population(nFS, p.SpikeSourcePoisson, {'rate': 3, 'duration': Total_Duration,'start': 0.0}, label='spike_source_Poisson_base') #, additional_parameters={"splitter": SplitterPoissonDelegate()})


# In[16]:


''' Pavan log:Introducing new variable num_neurons_in_rewardpop'''
# num_neurons_in_rewardpop=10
reward_pop=p.Population(nRS, p.IF_curr_exp(**FS_cell_params), label='r_pop_1')
reward_pop2=p.Population(nFS, p.IF_curr_exp(**FS_cell_params), label='r_pop_2')


# In[17]:


'''BSB log: I have kept the parameters same as pynn8example file by Andy -
EXCEPT - plastic_weights is 1.0 instead of 1.5'''

plastic_weights=1.0
synapse_dynamics_reward = p.STDPMechanism(
    timing_dependence=p.SpikePairRule(
        tau_plus=2, tau_minus=1,
        A_plus=1, A_minus=1),
    weight_dependence=p.AdditiveWeightDependence(w_min=0, w_max=5),
    weight=plastic_weights)


# In[18]:



noise_input_projection_rs=p.Projection(spike_source_Poisson_base_rs,RS_neurons,p.OneToOneConnector(),
                                   p.StaticSynapse(weight=2.0),
                                   receptor_type='excitatory', label='noise')

noise_input_projection_fs=p.Projection(spike_source_Poisson_base_fs,FS_neurons,p.OneToOneConnector(),
                                   p.StaticSynapse(weight=2.0),
                                   receptor_type='excitatory', label='noise')




projections_RStoRS=p.Projection(RS_neurons,RS_neurons,p.FixedProbabilityConnector(p_connect=0.1),
                                       synapse_type=synapse_dynamics_reward,
                                       receptor_type='excitatory', label='rs2rs')

projections_RStoFS=p.Projection(RS_neurons,FS_neurons,p.FixedProbabilityConnector(p_connect=0.1),
                                       synapse_type=synapse_dynamics_reward,
                                       receptor_type='excitatory', label='rs2fs')

projections_FStoFS=p.Projection(FS_neurons,FS_neurons ,
                            p.FixedProbabilityConnector(p_connect=0.1),
                            p.StaticSynapse(weight=1),
#                                 synapse_type=synapse_dynamics_reward,
                            receptor_type='inhibitory', label='fs2fs')


projections_FStoRS=p.Projection(FS_neurons,RS_neurons ,
                            p.FixedProbabilityConnector(p_connect=0.1),
                            p.StaticSynapse(weight=1),
#                                 synapse_type=synapse_dynamics_reward,
                            receptor_type='inhibitory', label='fs2rs')



# # *****************REWARD PROJECTIONS ***************

# In[19]:


'''BSB log: I have kept the parameters same as pynn8example file by Andy.'''
reward_projections_to_RS_neurons=p.Projection(reward_pop,RS_neurons,p.OneToOneConnector(),
                                          synapse_type=p.extra_models.Neuromodulation(
                                          weight=0.05, tau_c=200.0, tau_d=10.0, w_max=5),
                                          receptor_type='reward', label='reward_synapses1')

reward_projections_to_FS_neurons=p.Projection(reward_pop2,FS_neurons,p.OneToOneConnector(),
                                          synapse_type=p.extra_models.Neuromodulation(
                                          weight=0.05, tau_c=200.0, tau_d=10.0, w_max=5),
                                          receptor_type='reward', label='reward_synapses2')


# #interval_duration --->duration between stimulus-->size
# #stimulus_list     --->list of stimulus --->size is size(interval_duration)+1
# #Dopamine_list     --->when stimulus is S0 then this has 1 in corresponding place and otherwise it has zero-->size is same as stimulus_list
# #Dopamine_times    --->Dopamine random wait times before delivaring -->Size = len(Dopamine_list)
# #stim_start_times  --->start times of stimulus-->Sum of ISI before the particular index of stimulus_list
# #tuple_listOfstim_start_times -->this has stimulus and corresponding start time as a tuple EX:(42,10139)
# #DA_delivary_times -->Time at which DA has to be delivered in the entire run time
# #tuple_listOfstim_DA_delivary_times -->This contains tuples when dopamine needs to be delivered like (-1, 4252)
# #List_Of_DA_and_stimulus --> merged list of  tuple_listOfstim_start_times and tuple_listOfstim_DA_delivary_times
# #Final_sorted_list  -->Final sorted merged list

# In[20]:


'''randomly selected times for providing current input to stimulus population'''
t=0
reward_delay=200
stim_0_start_times=[200, 1700, 4500, 9500, 15600, 21700, 25900, 30400, 33800, 37680]#[200,700,1100,1600,2400,2700,3000]
stim_1_start_times=[1000, 3200,6700, 12845, 18201, 23500, 28600,31800, 35400, 40000]
DA_delivery_times=[i+reward_delay for i in stim_0_start_times]##[1000,1500,1900,2400,3200,3500,3800]


# In[21]:


DA_delivery_times


# In[22]:


SpikeSourceArray_pop_for_reward_pop = p.Population(1, p.SpikeSourceArray,
                            {'spike_times':DA_delivery_times }, label='reward_input_times')


# In[23]:


SpikeSourceArray_pop_for_StimulusS0_pop = p.Population(1, p.SpikeSourceArray,
                            {'spike_times': stim_0_start_times}, label='SpikeSourceArray_pop_for_StimulusS0_pop')


# In[24]:


'''PAVAN log:CREATING POSTSYNAPTIC IDS - TO MAKE PROJECTION FROM SPIKESOURCEARRAY TO RS NEURONS USING FROMTOLIST CONNECTOR'''

presynaptic_id=0
postsynaptic_ids_rs = rng.integers(low=0, high=nRS, size=chooseRS)
postsynaptic_ids_rs=postsynaptic_ids_rs.tolist()

list_connection_rs= []
for i in range(len(postsynaptic_ids_rs)):
    tuple_elem_arr_rs = (presynaptic_id, postsynaptic_ids_rs[i])
    list_connection_rs.append(tuple_elem_arr_rs)

Spikesource_projection_to_stimulus_rs_s0=p.Projection(SpikeSourceArray_pop_for_StimulusS0_pop,RS_neurons,p.FromListConnector(list_connection_rs),
                                    p.StaticSynapse(weight=3.0),
                                    receptor_type='excitatory', label='Spikesource_projection_to_stimulus_rs_S0')


print("list_connection_rs:{}\n".format(list_connection_rs))

'''PAVAN log:CREATING POSTSYNAPTIC IDS - TO MAKE PROJECTION FROM SPIKESOURCEARRAY TO FS NEURONS USING FROMTOLIST CONNECTOR'''
presynaptic_id=0
postsynaptic_ids_fs= rng.integers(low=0, high=nFS, size=chooseFS)
postsynaptic_ids_fs=postsynaptic_ids_fs.tolist()

list_connection_fs= []
for i in range(len(postsynaptic_ids_fs)):
    tuple_elem_arr_fs = (presynaptic_id, postsynaptic_ids_fs[i])
    list_connection_fs.append(tuple_elem_arr_fs)

Spikesource_projection_to_stimulus_fs_s0=p.Projection(SpikeSourceArray_pop_for_StimulusS0_pop,FS_neurons,p.FromListConnector(list_connection_fs),
                                    p.StaticSynapse(weight=3.0),
                                    receptor_type='excitatory', label='Spikesource_projection_to_stimulus_fs_s0')

print("list_connection_fs:{}\n".format(list_connection_fs))
Stimulus_From_rs_and_fs=[]
Stimulus_From_rs_and_fs.extend(postsynaptic_ids_rs)
Stimulus_From_rs_and_fs.extend(postsynaptic_ids_fs)

print("Stimulus_From_rs_and_fs{}\n".format(Stimulus_From_rs_and_fs))

NPG.append(Stimulus_From_rs_and_fs) #Appending stimulus to NPG list i.e,NPG[0] will have the first stimulus that we created above





# In[25]:


print(postsynaptic_ids_rs)


# In[26]:


# NPG[0][0:40]


# In[27]:


Spikesource_projection_to_stimulus=p.Projection(SpikeSourceArray_pop_for_reward_pop,reward_pop,p.AllToAllConnector(),
                                    p.StaticSynapse(weight=5.0),
                                    receptor_type='excitatory', label='SpikeSourceArray2Reward_Projection')
Spikesource_projection_to_stimulus2=p.Projection(SpikeSourceArray_pop_for_reward_pop,reward_pop2,p.AllToAllConnector(),
                                    p.StaticSynapse(weight=5.0),
                                    receptor_type='excitatory', label='SpikeSourceArray2Reward2_Projection2')


# # Recording Spikes

# In[28]:


spike_source_Poisson_base_rs.record('spikes')
spike_source_Poisson_base_fs.record('spikes')
reward_pop.record('spikes')
RS_neurons.record('spikes')
FS_neurons.record('spikes')


# In[29]:


# p.run(Total_Duration)


# In[30]:


projections_RStoRS_w=[]
projections_RStoFS_w=[]
noise_input_projection_rs_w=[]
noise_input_projection_fs_w=[]
Spikesource_projection_to_stimulus_rs_s0_w=[]
n_repeats = 10  ## required to be set to 60 for recording every 100 msec
duration = Total_Duration/n_repeats

for time in range(n_repeats):
    p.run(duration)
    projections_RStoRS_w.append(projections_RStoRS.get(["weight"], "list"))
    projections_RStoFS_w.append(projections_RStoFS.get(["weight"], "list"))
#     noise_input_projection_rs_w.append(noise_input_projection_rs.get(["weight"], "list"))
#     noise_input_projection_fs_w.append(noise_input_projection_fs.get(["weight"], "list"))
    Spikesource_projection_to_stimulus_rs_s0_w.append( Spikesource_projection_to_stimulus_rs_s0.get(["weight"], "list"))


# # Weight Progression
#

# In[31]:


projections_RStoRS_max=[]
projections_RStoFS_max=[]
for i in range(0,n_repeats):
    projections_RStoRS_w_last = np.asarray(projections_RStoRS_w[i])
    projections_RStoRS_max.append(max(projections_RStoRS_w_last[:,2]))

    projections_RStoFS_w_last = np.asarray(projections_RStoFS_w[i])
    projections_RStoFS_max.append(max(projections_RStoFS_w_last[:,2]))
    print("rs2rs: ", projections_RStoRS_w_last)
    print("rs2fs: ", projections_RStoFS_w_last)



# In[32]:


plt.plot(projections_RStoRS_max)
plt.plot(projections_RStoFS_max)
plt.show()


# # GET THE RECORDED DATA

# In[33]:


rs_neurons_population_spikes=RS_neurons.spinnaker_get_data('spikes')
fs_neurons_population_spikes=FS_neurons.spinnaker_get_data('spikes')


# In[34]:


original_indices=(np.arange(0, nFS, 1, dtype=int)).tolist()
wanted_indices=(np.arange(nRS, nRS+nFS, 1, dtype=int)).tolist()


# In[35]:


'''Pavan Log:This code is used to change the fs_neuron indices from 0 to 200 to 800 to 1000 in spikes
array'''
for i in range(0,len(fs_neurons_population_spikes)):
    for j in range(0,len(original_indices)):
        if(fs_neurons_population_spikes[i,0]==original_indices[j]):
            fs_neurons_population_spikes[i,0]=wanted_indices[j]
            break


# In[36]:


'''This is total RS+FS(1000) neurons spikes,which are stored in Full_population_spikes '''
Full_population_spikes_list=[]
Full_population_spikes_list.extend(rs_neurons_population_spikes.tolist())
Full_population_spikes_list.extend(fs_neurons_population_spikes.tolist())
Full_population_spikes=np.asarray(Full_population_spikes_list)


# In[37]:


'''Cross check code to see whether NPG_converted_neuron_ID is getting updated with values 800 to 100
and seeing whether NPG[i][40:50] is not changing because we have created a copy of list and appended
it to NPG_converted_neuron_ID and not the original list.so when we change NPG_converted_neuron_ID then
NPG[i][40:50] will not get affected

'''

# NPG_converted_neuron_ID=[]
# for i in range(0,len(NPG)):
#     NPG_converted_neuron_ID.append(NPG[i].copy())
# NPG_converted_neuron_ID[1][40:50]
# NPG[0][40:50]
# for i in range(0,len(NPG)):
#     for j in range(40,50):
#         for k in range(0,len(original_indices)):
#             if(NPG[i][j]==original_indices[k]):
#                 NPG_converted_neuron_ID[i][j]=wanted_indices[k]
#                 break

# NPG_converted_neuron_ID[1][40:50]
# NPG[1][40:50]


# In[38]:


'''Pavan Log:This code is used to change the fs_neuron indices from 0 to 200 to 800 to 1000'''
NPG_converted_neuron_ID=[]
for i in range(0,len(NPG)):
    NPG_converted_neuron_ID.append(NPG[i].copy())

for i in range(0,len(NPG)):
    for j in range(chooseRS,chooseRS+chooseFS):
        for k in range(0,len(original_indices)):
            if(NPG[i][j]==original_indices[k]):
                NPG_converted_neuron_ID[i][j]=wanted_indices[k]
                break
'''The following code is '''
npg_spikes_rs=[]# this list has only rs spikes for a given stimulus.If it 0th stimuls then npg_spikes_rs[0]
npg_spikes_fs=[]# this list has only fs spikes for a given stimulus.
NPG_rs_fs=[] # this list (RS+FS) spikes for a given stimulus.If NPG_rs_fs[0] then it is 0th stimulus
             #where fs indices are from 800 to 999
for j in range(0,len(NPG)):
    rs_neurons_population_spikes_Npg_mask=[i in (NPG[j][0:chooseRS]) for i in rs_neurons_population_spikes[:,0].tolist()]
    npg_spikes_rs.append(rs_neurons_population_spikes[rs_neurons_population_spikes_Npg_mask])

    fs_neurons_population_spikes_Npg_mask=[i in (NPG_converted_neuron_ID[j][chooseRS:chooseRS+chooseFS]) for i in fs_neurons_population_spikes[:,0].tolist()]
    npg_spikes_fs.append(fs_neurons_population_spikes[fs_neurons_population_spikes_Npg_mask])
#     print(npg_spikes_fs[j])

    npg_all_spikes_list=[] # this is a temporary list for combining RS and FS spikes for a stimulus j.
    npg_all_spikes_list.extend(npg_spikes_rs[j].tolist())

    npg_all_spikes_list.extend(npg_spikes_fs[j].tolist())

    npg_all_spikes=np.asarray(npg_all_spikes_list)

    NPG_rs_fs.append(npg_all_spikes)




# In[39]:


plt.figure(2, figsize=(15, 5))
plt.scatter(Full_population_spikes[:,1], Full_population_spikes[:,0],marker='.',s=20,c='red')
plt.xlabel('Time (msec)')
plt.ylabel('number of neurons')
plt.title('Full_population_spikes')
#plt.xlim=([Total_Duration])
plt.show()


# In[40]:


plt.figure(2, figsize=(15, 5))
plt.scatter(NPG_rs_fs[0][:,1], NPG_rs_fs[0][:,0],marker='.',s=20,c='red')
#plt.scatter(NPG_rs_fs[1][:,1], NPG_rs_fs[1][:,0],marker='|',s=50,c='yellow')
plt.xlabel('Time (msec)')
plt.ylabel('number of neurons')
plt.title('Raster of the Stimilus S0')
#plt.xlim=([Total_Duration])
plt.show()


# In[41]:


p.end()


# In[ ]:





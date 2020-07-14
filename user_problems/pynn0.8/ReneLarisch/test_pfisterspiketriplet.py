"""
Stimulate a network with natural scenes (Olshausen, 1996) and learn with the Pfister and Gerstner (2006) learning rule
"""
import scipy.io as sio
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 8})
# import pyNN.spiNNaker as sim
import spynnaker8 as sim
import sys
import copy
import time


def createBars( patchsize = 8, propability = -1, noiselevel = 0 , fixPosition = -1 ):
    ##CREATEBARS Creates an image containing bars occuring with independent propability.
    ## Each pixel has the maximum value of different patterns.
    ## patchsize:   gives the size of the image patch (patchsize x patchsize)
    ## propability:  propability if a bar is active or not
    ## noiselevel:   gives the level of noise that is modifinig the responses
    ##   active bar: 1 - noise, non-active bar: noise
    ## fixPosition: inserts a vertical bar at the given psition

    # Set propability to 1/patchsize if no value is given
    if propability < 0:
        propability = 1/float(patchsize)

    if fixPosition > 0:
        propability = 0

    # Allocate space
    image=np.zeros((patchsize,patchsize))

    ## Create bars independently
    for i in range(0, patchsize):

        #insert a bar at the given position:
        if fixPosition >= 0:
            if i == fixPosition:
                for j in range(0, patchsize):
                    image[j,i] = max(image[i,j], float(1) - noiselevel*np.random.rand())
                continue

        # insert bars random:
        # Horizontal
        # Select if the bar is active
        if np.random.rand() < propability:
            for j in range(0, patchsize):
                image[i,j] = max(image[i,j], float(1) - noiselevel*np.random.rand())
        else:
            for j in range(0, patchsize):
                image[i,j] = max(image[i,j], noiselevel*np.random.rand())

        # Vertical
        # Select if the bar is active
        if np.random.rand() < propability:
            for j in range(0, patchsize):
                image[j,i] = max(image[j,i], float(1) - noiselevel*np.random.rand())
        else:
            for j in range(0, patchsize):
                image[j,i] = max(image[j,i],  noiselevel*np.random.rand())

    return image

dt=1.0
sim.setup(timestep=1.0*dt, min_delay=1.0*dt,max_delay=10.0*dt)

patchsize = 12

lgn_w = patchsize            ### patchsize
lgn_h = patchsize
lgn_d = 1

## populations
nNeurons = lgn_w * lgn_h * lgn_d

# create cells
cell_params = {
    'cm': 0.2,         # nF
    'i_offset': 0.0,
    'tau_m': 9.4,
    'tau_refrac': 2.0,
    'tau_syn_E': 5.0,
    'tau_syn_I': 5.0,
    'v_reset': -70.6,
    'v_rest': -70.6,
    'v_thresh': -50.4}

lgn_pop = sim.Population(int(nNeurons), sim.SpikeSourcePoisson(rate=31.4))
v1_pop = sim.Population(int(nNeurons/2), sim.IF_curr_exp(**cell_params))


input_firing_rates = np.random.randint(5.0, 10.0, lgn_pop.size)
lgn_pop.set(rate=input_firing_rates)

start_w = 0.5            # np.random.uniform(low=0.01, high=0.5)
param_scale = 0.5

# Build excitatory plasticity model
stdp_model_Ex = sim.STDPMechanism(  timing_dependence = sim.extra_models.PfisterSpikeTriplet(
                                               tau_plus = 16.8, tau_minus = 33.7, tau_x = 101, tau_y = 114, A_plus = 5.0e-10, A_minus = 7.0e-3),
                                    weight_dependence=sim.extra_models.WeightDependenceAdditiveTriplet(
                                               w_min = 0.0, w_max = 1.0, A3_plus = 6.3e-3, A3_minus = 2.3e-4),
                                    weight = sim.RandomDistribution('uniform', (start_w, 3)), delay = 1 )

## create list of random initialized weights and delays
rand_w = np.random.rand(lgn_pop.size,v1_pop.size)
rand_d = np.random.randint(1,10,(lgn_pop.size,v1_pop.size))

idx_pre = np.linspace(0,lgn_pop.size-1,lgn_pop.size-1,dtype='int32')
idx_post = np.linspace(0,v1_pop.size-1,v1_pop.size-1,dtype='int32')

connect_list = []
for pre_i in range(lgn_pop.size):
  for post_i in range(v1_pop.size):
    connect_list.append([pre_i,post_i,rand_w[pre_i,post_i],rand_d[pre_i,post_i]])

proj_LGN_E1 = sim.Projection(lgn_pop, v1_pop,
                       sim.FromListConnector(connect_list),        # all to all connection (like in ANN model)
                       receptor_type='excitatory',
                    synapse_type=stdp_model_Ex)

# run simulation
sim_duration =  100.0 # ms
n_stimuli = 500   #10         ### should be 200
maxFR = 10

spikesPerPatchV1 = []
spikesPerPatchLGN = []
vPerPatchV1 = []
iExcPerPatch = []

t_0= time.time() # timepoint before the simulation loop
#nat_scenes = readDivImages()
for stim_i in range(n_stimuli):
    #inputPatch,maxVal = getInput(patchsize,nat_scenes) # get patch
    inputPatch = createBars( patchsize = patchsize, propability = -1, noiselevel = 0 )#, fixPosition = int(np.floor(patchsize/2)) ) # get patch with a bar
    inputPatch = np.reshape(inputPatch,lgn_pop.size)
    lgn_pop.set(rate=inputPatch*maxFR)
    sim.run(sim_duration)
    #if (stim_i%50) == 0 :
    time.sleep(0.1)
    print('Run Stim:%i'%(stim_i))
    #w_LGNtoV1 = connections.get(variables=['weight','array'], clear = True)
t_1 = time.time() # time point after simulation loop
print('Simulation time in seconds=%f'%(t_1-t_0))


width = 9
height = 8

## get and plots weights

w_LGNtoV1 = proj_LGN_E1.get('weight','arry')

plt.figure(figsize=(16,9))
for i in range(1, width*height+1):
    plt.subplot(width,height,i)
    plt.imshow(np.reshape(w_LGNtoV1[:,i-1],(patchsize,patchsize)))
    if i == nNeurons/2:
        break
plt.savefig('RFs_V1.png')

sim.end()

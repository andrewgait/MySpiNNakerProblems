#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pyNN.spiNNaker as p
import matplotlib.pyplot as plt
import numpy as np
from numpy import *
import time
from pyNN.random import RandomDistribution, NumpyRNG
start_time = time.time()

#from spinn_front_end_common.utilities import globals_variables
from quantities import ms
import neo

#for plotting
from pyNN.utility.plotting import Figure, Panel, Histogram
# get_ipython().run_line_magic('matplotlib', 'inline')
from spynnaker.pyNN.extra_algorithms.splitter_components import (
    SplitterAbstractPopulationVertexNeuronsSynapses, SplitterPoissonDelegate)

'''SETTING NUMBER OF NEURONS PER CHANNEL'''

# numCellsPerCol_STR = 128#125#314# <--1/4th of 1255 #### 90% of 50% of 2790000 = 1255500
# numCellsPerCol_FSI = 8#9####139
numCellsPerCol_STN = 16 #14 ###13560
# numCellsPerCol_SNR = 32#27 ####26320
# numCellsPerCol_GPe = 64#46 ###45960
# numPoissonInput_str= 64#60
# numPoissonInput_str_fsi=8#9
numPoissonInput_stn = 15 #7
# numCellsPerCol_SNC=8
# numPeriodicInput =314

'''NOW START RUNNING MULTIPLE TRIALS, AND INITIALISE THE ARRAYS'''
numtrials = 1

''' SET UP SPINNAKER AND BEGIN SIMULATION'''
p.setup(timestep=0.1,time_scale_factor=10)
# p.set_number_of_neurons_per_core(p.extra_models.Izhikevich_cond_dual,8)
# p.set_number_of_neurons_per_core(p.extra_models.Izhikevich_cond,8)

# stn_cell_params = {'a': stn_a,
#                'b': stn_b,
#                'c': stn_c,
#                'd': stn_d,
#                'v': stn_v_init,
#                'u': stn_u_init,
#                'tau_syn_E': tau_ampa,
#                'tau_syn_E2':tau_nmda,
#                'tau_syn_I': tau_gabaa,
#                'i_offset': current_bias_stn,
#                'isyn_exc': E_ampa,
#                'isyn_inh': E_gabaa
#               }

''' THE FIRST CHANNEL'''
# stn_ch1 = p.Population(numCellsPerCol_STN, p.extra_models.Izhikevich_cond_dual, stn_cell_params, label='stn_pop1',
#                       additional_parameters={"splitter": SplitterAbstractPopulationVertexNeuronsSynapses(1)})
stn_ch1 = p.Population(numCellsPerCol_STN, p.extra_models.Izhikevich_cond_dual, label='stn_pop1',
                        additional_parameters={"splitter": SplitterAbstractPopulationVertexNeuronsSynapses(1)})

'''BASE POISSON INPUTS TO ALL CHANNELS FOR THE ENTIRE SIMULATION DURATION OF 5 SECONDS'''
Rate_Poisson_Inp_base = 3
start_Poisson_Inp_base = 10
Duration_Poisson_Inp_base = 980
Poisson_source_nmda_stn = p.Population(numPoissonInput_stn, p.SpikeSourcePoisson, {'rate': Rate_Poisson_Inp_base,
    'duration': Duration_Poisson_Inp_base,'start': start_Poisson_Inp_base}, label='spike_source_Poisson_base2',
                                            additional_parameters={"splitter": SplitterPoissonDelegate()})

Poisson_source_ampa_stn = p.Population(numPoissonInput_stn, p.SpikeSourcePoisson, {'rate': Rate_Poisson_Inp_base,
    'duration': Duration_Poisson_Inp_base,'start': start_Poisson_Inp_base}, label='spike_source_Poisson_base2',
                                            additional_parameters={"splitter": SplitterPoissonDelegate()})

stdp_cort2stn_ampa_ch1 = p.STDPMechanism(
        timing_dependence=p.SpikePairRule(
            tau_plus=0.001, tau_minus=1,
            A_plus=0.001, A_minus=1),
        weight_dependence=p.AdditiveWeightDependence(
            w_min=0.272, w_max=1), weight=0.3)

'''SETTING NETWORK static connectivity ( CONDUCTANCE) PARAMETERS'''

g_nmda = 0.5

g_cort2stn = g_nmda

pconn_cort2str = 0.15

delay_lo_bound=1
delay_hi_bound=3

distr_stn = RandomDistribution('uniform', (delay_lo_bound,delay_hi_bound))#, rng=NumpyRNG(seed=85522))

## AMPA FOR STN - STDP

# from_list_test = []
# for i in range(16):
#     from_list_test.append([i,i])

p.Projection(Poisson_source_nmda_stn, stn_ch1,
             # p.FixedProbabilityConnector(p_connect=pconn_cort2str),
             # p.FromListConnector(from_list_test),
             p.OneToOneConnector(),
             synapse_type=stdp_cort2stn_ampa_ch1,
             receptor_type='excitatory')

## NMDA FOR STN
p.Projection(Poisson_source_ampa_stn, stn_ch1,
             # p.FixedProbabilityConnector(p_connect=pconn_cort2str),
             p.OneToOneConnector(),
             # p.FromListConnector(from_list_test),
             p.StaticSynapse(weight=g_cort2stn, delay=distr_stn),
             receptor_type ='excitatory2')

stn_ch1.record(['spikes','v','gsyn_exc'])

# In[24]:


p.run(100)


# In[ ]:

p.end()



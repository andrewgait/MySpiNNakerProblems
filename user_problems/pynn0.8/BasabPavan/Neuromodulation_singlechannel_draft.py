#!/usr/bin/env python
# coding: utf-8

# ### Create afferents and efferents of the SNc population
#
# ### LOOK AND DISCUSS THE RESULTS/OUTPUTS ETC
#
# ### DISCUSS THE NEXT STEP - WHICH WILL LIKELY BE - ALL GOING WELL WITH THE STEP ABOVE:
#
# ### PROVIDE CORTICO-STRIATAL PLASTICITY

# ### For later( What do we want to see in this model?: We want to see if the weights go up if rewarded - and go down if punished.)
#
# ### What should we look for at the beginning - i.e. to start with:
# ### (1) Does the weights stay around the set weight? i.e. they shouldn't increase or decrease to the limits without any explicit reward/punishment signal.
# ### (2) What are the base firing rates of the populations and do they conform to the original rates in the 2018 paper i.e. according to biologically informed figures?
#
# ### Can you please ammend the whole code (part of it is done before and during today's meeting 31/05/2022) - and run and see first that it compiles? and check (1) and (2) in the previous point?

# ## Basab edited - checked - and this code should run (9th/10th May 2023)

# In[1]:


import pyNN.spiNNaker as p
import matplotlib.pyplot as plt
import numpy as np
from numpy import *
import time
from pyNN.random import RandomDistribution, NumpyRNG
start_time = time.time()

# from quantities import ms
import neo

#for plotting
from pyNN.utility.plotting import Figure, Panel, Histogram
# get_ipython().run_line_magic('matplotlib', 'inline')

# splitter
from spynnaker.pyNN.extra_algorithms.splitter_components import (
    SplitterAbstractPopulationVertexNeuronsSynapses)


# In[2]:


TotalDuration = 1000##10000  ### TOTAL RUN TIME
TimeInt = 0.1    ### SIMULATION TIME STEP
TotalDataPoints = int(TotalDuration*(1/TimeInt))
countt=4


# In[3]:


print(TotalDataPoints)


# In[4]:


my_resol = 100 ##1000 #msec
checkpoint = int(TotalDuration/my_resol)

# Function returning x if x satisfies both conditions

def my_condition(x, lower_bound, upper_bound):
    return x>=lower_bound and x<upper_bound

# Function to set the bounds progressively and then extract all the spike times in the spike data
# that lie within the bounds - the bound check being done by another function call. In the end, this
# function returns the peri-stimulus-time-histogram of the spike train conforming to the set resolution

def my_firingrate(my_data, checkpoint, my_resol):
    lower_bound = 0
    my_hist = np.zeros((checkpoint))
    for loop in range(0,checkpoint):
        upper_bound = lower_bound + my_resol
        my_hist[loop] = sum(1 for x in my_data if my_condition(x, lower_bound, upper_bound))
    #     y[lower_bound:upper_bound]=my_hist[loop] ## assigning same values to the indices in the filler zone
        lower_bound = upper_bound
    return my_hist


# In[5]:


def get_mean_rate_new(numCells, Pop_spikes, xlim_min, xlim_max):
    """
    Parameters:
        1. numCells (int): Number of neurons in that population
        2. Pop_spikes (array): Generated using Population.spinnaker_get_data('spikes')
        3. xlim_min (int): Lower bound of timeframe (ms)
        4. xlim_max (int): Upper bound of timeframe (ms)

    Returns:
        1. Mean Firing Rate - but with chopped off spikes at the front and end to discard any transient
        network effects.
    """
    count = 0
    for spike in range(len(Pop_spikes)):
        if Pop_spikes[spike][1]<=xlim_min or Pop_spikes[spike][1]>xlim_max:
            continue
        count += 1

    return (count/numCells)/((xlim_max-xlim_min)/1000)


# In[6]:


def print_mean_firing_rate():
    print("E mean firing rate & total no. of spikes: ",get_mean_rate_new(N_E, esp,500,Total_duration-500))#500,Total_duration-500))
    print("I mean firing rate & total no. of spikes: ",get_mean_rate_new(N_I, isp,500,Total_duration-500))#500,Total_duration-500))


# In[7]:


'''PARAMETERS USED IN DEFINING THE BASIC MODEL UNITS: IZHIKEVICH NEURONS'''
tau_ampa = 6.0### 6.0ms ampa synapse time constant
E_ampa = 0.0 ## ampa synapse reversal potential

tau_nmda=160 #160.0ms #NMDA synapse time constant
tau_gabaa= 4.0### gaba synapse time constant
E_gabaa = -80.0 ## gaba synapse reversal potential

strd1_a=0.02
strd1_b=0.2
strd1_c=-65.0
strd1_d=8.0
# strd1_v_init = -80.0
# strd1_u_init = strd1_b * strd1_v_init


strd2_a=0.02
strd2_b=0.2
strd2_c=-65.0
strd2_d=8.0
# strd2_v_init = -80.0
# strd2_u_init = strd2_b * strd2_v_init

current_bias_str = -30.0

fsi_a=0.1
fsi_b=0.2
fsi_c=-65.0
fsi_d=8.0
# fsi_v_init = -70.0
# fsi_u_init = fsi_b * fsi_v_init

current_bias_fsi = -10.0

gpe_a=0.005
gpe_b=0.585
gpe_c=-65.0
gpe_d=4.0
# gpe_v_init = -70.0
# gpe_u_init = gpe_b * gpe_v_init

current_bias_gpe = 2.0

snr_a = 0.005
snr_b = 0.32
snr_c = -65.0
snr_d = 2.0
# snr_v_init = -70.0
# snr_u_init = snr_b * snr_v_init

current_bias_snr = 5.0

stn_a=0.005
stn_b=0.265
stn_c=-65.0
stn_d=2.0
# stn_v_init = -60.0
# stn_u_init = stn_b * stn_v_init

current_bias_stn = 5.0

snc_a=0.0025
snc_b=0.2
snc_c=-55 #-65
snc_d=2#12 #8
# snc_v_init=-70.0
# snc_u_init = snc_b * snc_v_init

current_bias_snc = 9.0 #15.0 ###in literature 9.0

'''SETTING NUMBER OF NEURONS PER CHANNEL'''
scale=0.5
numCellsPerCol_str = 125#314# <--1/4th of 1255 #### 90% of 50% of 2790000 = 1255500
numCellsPerCol_fsi = 9####139
numCellsPerCol_stn = 14 ###13560
numCellsPerCol_snr = 27 ####26320
numCellsPerCol_gpe = 46 ###45960
numPoissonInput_str= round(numCellsPerCol_str * scale)
numPoissonInput_fsi=numCellsPerCol_fsi
numPoissonInput_stn=numCellsPerCol_stn
numCellsPerCol_snc=8
numPoissonInput_snc = numCellsPerCol_snc
# numPeriodicInput =314


# In[8]:


'''NOW START RUNNING MULTIPLE TRIALS, AND INITIALISE THE ARRAYS'''
numtrials = 1

gpe_hist1 = np.zeros((numtrials, checkpoint))
snr_hist1 = np.zeros((numtrials, checkpoint))
stn_hist1 = np.zeros((numtrials, checkpoint))
fsi_hist1 = np.zeros((numtrials, checkpoint))


# In[9]:


''' SET UP SPINNAKER AND BEGIN SIMULATION'''
p.setup(timestep=0.1,time_scale_factor=10)
p.set_number_of_neurons_per_core(p.extra_models.Izhikevich_cond_dual,32)
p.set_number_of_neurons_per_core(p.extra_models.Izhikevich_cond,32)


# # XXXDRAFT - NEED TO DEFINE U , V AND ALL ISYN PARAMETERS FROM WITHIN THE NEURON DEFINITION XXXX TO BE DONE ON A PRIORITY

# In[10]:


'''STRIATUM OF THE BASAL GANGLIA: MEDIUM SPINY NEURONS (MSN - D1 / D2)'''

strd1_cell_params = {'a': strd1_a,
                 'b': strd1_b,
                 'c': strd1_c,
                 'd': strd1_d,
#                  'v': strd1_v_init,
#                  'u': strd1_u_init,
                 'tau_syn_E': tau_ampa,
                 'tau_syn_E2':tau_nmda,
                 'tau_syn_I': tau_gabaa,
                 'i_offset': current_bias_str,
                 'isyn_exc': E_ampa,
                 'isyn_inh': E_gabaa
                }

strd2_cell_params = {'a': strd2_a,
                 'b': strd2_b,
                 'c': strd2_c,
                 'd': strd2_d,
#                  'v': strd2_v_init,
#                  'u': strd2_u_init,
                 'tau_syn_E': tau_ampa,
                 'tau_syn_E2':tau_nmda,
                 'tau_syn_I': tau_gabaa,
                 'i_offset': current_bias_str,
                 'isyn_exc': E_ampa,
                 'isyn_inh': E_gabaa
                }

'''FAST SPIKING INTERNEURONS OF THE STRIATUM'''

fsi_cell_params = { 'a': fsi_a,
                'b': fsi_b,
                'c': fsi_c,
                'd': fsi_d,
#                 'v': fsi_v_init,
#                 'u': fsi_u_init,
                'tau_syn_E': tau_ampa,
                'tau_syn_E2':tau_nmda,
                'tau_syn_I': tau_gabaa,
                'i_offset': current_bias_fsi,
                'isyn_exc': E_ampa,
                'isyn_inh': E_gabaa
             }


'''GLOBAL PALLIDUS - EXTERNA OF THE BASAL GANGLIA'''

gpe_cell_params = {'a': gpe_a,
               'b': gpe_b,
               'c': gpe_c,
               'd': gpe_d,
#                'v': gpe_v_init,
#                'u': gpe_u_init,
               'tau_syn_E': tau_ampa,
               'tau_syn_I': tau_gabaa,
               'i_offset': current_bias_gpe,
               'isyn_exc': E_ampa,
               'isyn_inh': E_gabaa
               }


'''SUBSTANTIA NIAGRA OF THE BASAL GANGLIA'''

snr_cell_params = {'a': snr_a,
               'b': snr_b,
               'c': snr_c,
               'd': snr_d,
#                'v': snr_v_init,
#                'u': snr_u_init,
               'tau_syn_E': tau_ampa,
               'tau_syn_I': tau_gabaa,
               'i_offset': current_bias_snr,
               'isyn_exc': E_ampa,
               'isyn_inh': E_gabaa
             }

'''SUB-THALAMIC NUCLEUS OF THE BASAL GANGLIA'''

stn_cell_params = {'a': stn_a,
               'b': stn_b,
               'c': stn_c,
               'd': stn_d,
#                'v': stn_v_init,
#                'u': stn_u_init,
               'tau_syn_E': tau_ampa,
               'tau_syn_E2':tau_nmda,
               'tau_syn_I': tau_gabaa,
               'i_offset': current_bias_stn,
               'isyn_exc': E_ampa,
               'isyn_inh': E_gabaa
              }
snc_cell_params = { 'a': snc_a,
               'b': snc_b,
               'c': snc_c,
               'd': snc_d,
#                'v': snc_v_init,
#                'u': snc_u_init,
               'tau_syn_E': tau_ampa,
               'tau_syn_I': tau_gabaa,
               'i_offset': current_bias_snc,
               'isyn_exc': E_ampa,
               'isyn_inh': E_gabaa
              }
''' THE FIRST CHANNEL'''
strd1_ch1 = p.Population(numCellsPerCol_str, p.extra_models.Izhikevich_cond_dual, strd1_cell_params, label='strd1_ch1')
                        # additional_parameters={'splitter': SplitterAbstractPopulationVertexNeuronsSynapses(1)})

strd2_ch1 = p.Population(numCellsPerCol_str, p.extra_models.Izhikevich_cond_dual, strd2_cell_params, label='strd2_ch1')
                        # additional_parameters={'splitter': SplitterAbstractPopulationVertexNeuronsSynapses(1)})

fsi_ch1 = p.Population(numCellsPerCol_fsi, p.extra_models.Izhikevich_cond_dual, fsi_cell_params, label='fsi_ch1')
                        # additional_parameters={'splitter': SplitterAbstractPopulationVertexNeuronsSynapses(1)})

gpe_ch1 = p.Population(numCellsPerCol_gpe, p.extra_models.Izhikevich_cond, gpe_cell_params, label='gpe_ch1')
                        # additional_parameters={'splitter': SplitterAbstractPopulationVertexNeuronsSynapses(1)})

snr_ch1 = p.Population(numCellsPerCol_snr, p.extra_models.Izhikevich_cond, snr_cell_params, label='snr_ch1')
                        # additional_parameters={'splitter': SplitterAbstractPopulationVertexNeuronsSynapses(1)})

stn_ch1 = p.Population(numCellsPerCol_stn, p.extra_models.Izhikevich_cond_dual, stn_cell_params, label='stn_ch1')
                        # additional_parameters={'splitter': SplitterAbstractPopulationVertexNeuronsSynapses(1)})

snc_ch1=p.Population(numCellsPerCol_snc, p.extra_models.Izhikevich_cond, snc_cell_params, label='reward_ch1')
                        # additional_parameters={'splitter': SplitterAbstractPopulationVertexNeuronsSynapses(1)})


# In[11]:


'''BASE POISSON INPUTS TO ALL CHANNELS FOR THE ENTIRE SIMULATION DURATION OF 5 SECONDS'''
Rate_Poisson_Inp_base = 3
start_Poisson_Inp_base = 10
Duration_Poisson_Inp_base = 980


Poisson_source_nmda_strd1 = p.Population(numPoissonInput_str, p.SpikeSourcePoisson, {'rate': Rate_Poisson_Inp_base,
    'duration': Duration_Poisson_Inp_base,'start': start_Poisson_Inp_base}, label='Poisson_source_nmda_strd1')

Poisson_source_ampa_strd1 = p.Population(numPoissonInput_str, p.SpikeSourcePoisson, {'rate': Rate_Poisson_Inp_base,
    'duration': Duration_Poisson_Inp_base,'start': start_Poisson_Inp_base}, label='Poisson_source_ampa_strd1')

Poisson_source_nmda_strd2 = p.Population(numPoissonInput_str, p.SpikeSourcePoisson, {'rate': Rate_Poisson_Inp_base,
    'duration': Duration_Poisson_Inp_base,'start': start_Poisson_Inp_base}, label='Poisson_source_nmda_strd2')

Poisson_source_ampa_strd2= p.Population(numPoissonInput_str, p.SpikeSourcePoisson, {'rate': Rate_Poisson_Inp_base,
    'duration': Duration_Poisson_Inp_base,'start': start_Poisson_Inp_base}, label='Poisson_source_ampa_strd2')

Poisson_source_nmda_fsi = p.Population(numPoissonInput_fsi, p.SpikeSourcePoisson, {'rate': Rate_Poisson_Inp_base,
    'duration': Duration_Poisson_Inp_base,'start': start_Poisson_Inp_base}, label='Poisson_source_nmda_fsi')

Poisson_source_ampa_fsi = p.Population(numPoissonInput_fsi, p.SpikeSourcePoisson, {'rate': Rate_Poisson_Inp_base,
    'duration': Duration_Poisson_Inp_base,'start': start_Poisson_Inp_base}, label='Poisson_source_ampa_fsi')

Poisson_source_nmda_stn = p.Population(numPoissonInput_stn, p.SpikeSourcePoisson, {'rate': Rate_Poisson_Inp_base,
    'duration': Duration_Poisson_Inp_base,'start': start_Poisson_Inp_base}, label='Poisson_source_nmda_stn')

Poisson_source_ampa_stn = p.Population(numPoissonInput_stn, p.SpikeSourcePoisson, {'rate': Rate_Poisson_Inp_base,
    'duration': Duration_Poisson_Inp_base,'start': start_Poisson_Inp_base}, label='Poisson_source_ampa_stn')

Poisson_source_ampa_snc = p.Population(numPoissonInput_snc, p.SpikeSourcePoisson, {'rate': Rate_Poisson_Inp_base,
    'duration': Duration_Poisson_Inp_base,'start': start_Poisson_Inp_base}, label='Poisson_source_ampa_snc')


# In[12]:


# "STDP parameters for pop1"

stdp_cort_strd1_nmda_ch1 = p.STDPMechanism(
    timing_dependence=p.SpikePairRule(
        tau_plus=0.5, tau_minus=0.5,
        A_plus=0.5, A_minus=0.5),
    weight_dependence=p.AdditiveWeightDependence(
        w_min=0.01, w_max=1), weight=0.3)

stdp_cort_strd2_ampa_ch1 = p.STDPMechanism(
        timing_dependence=p.SpikePairRule(
            tau_plus=0.5, tau_minus=0.5,
            A_plus=1, A_minus=1),
        weight_dependence=p.AdditiveWeightDependence(
            w_min=0.01, w_max=1), weight=0.3)

stdp_cort_fsi_ampa_ch1 = p.STDPMechanism(
        timing_dependence=p.SpikePairRule(
            tau_plus=0.5, tau_minus=0.5,
            A_plus=0.5, A_minus=0.5),
        weight_dependence=p.AdditiveWeightDependence(
            w_min=0.01, w_max=1), weight=0.3)

# stdp_strd1_snr_gaba_ch1 = p.STDPMechanism(
#         timing_dependence=p.SpikePairRule(
#             tau_plus=0.25, tau_minus=0.5,
#             A_plus=0.25, A_minus=0.5),
#         weight_dependence=p.AdditiveWeightDependence(
#             w_min=0.0, w_max=1), weight=0.001)

stdp_cort_stn_ampa_ch1 = p.STDPMechanism(
        timing_dependence=p.SpikePairRule(
            tau_plus=1, tau_minus=1,
            A_plus=1, A_minus=1),
        weight_dependence=p.AdditiveWeightDependence(
            w_min=0.01, w_max=1), weight=0.3)

# stdp_strd2_gpe_gaba_ch1 = p.STDPMechanism(
#         timing_dependence=p.SpikePairRule(
#             tau_plus=0.25, tau_minus=0.5,
#             A_plus=0.25, A_minus=0.5),
#         weight_dependence=p.AdditiveWeightDependence(
#             w_min=0.0272, w_max=1), weight=0.1)



###############################################################

# stdp_cort2strd1_NMDA_pop1 = p.STDPMechanism(
#     timing_dependence=p.SpikePairRule(
#         tau_plus=0.5, tau_minus=0.5,
#         A_plus=0.25, A_minus=0.5),
#     weight_dependence=p.AdditiveWeightDependence(
#         w_min=0, w_max=1), weight=0.0001)

# stdp_cort2strd2_AMPA_pop1 = p.STDPMechanism(
#         timing_dependence=p.SpikePairRule(
#             tau_plus=0.5, tau_minus=0.5,
#             A_plus=1, A_minus=1),
#         weight_dependence=p.AdditiveWeightDependence(
#             w_min=0.0140, w_max=1), weight=0.1)

# stdp_cort2fsi_AMPA_pop1 = p.STDPMechanism(
#         timing_dependence=p.SpikePairRule(
#             tau_plus=0.001, tau_minus=0.5,
#             A_plus=0.001, A_minus=0.5),
#         weight_dependence=p.AdditiveWeightDependence(
#             w_min=0.0277, w_max=1), weight=0.3)

# # stdp_strd1_snr_AMPA_pop1 = p.STDPMechanism(
# #         timing_dependence=p.SpikePairRule(
# #             tau_plus=0.25, tau_minus=0.5,
# #             A_plus=0.25, A_minus=0.5),
# #         weight_dependence=p.AdditiveWeightDependence(
# #             w_min=0.0, w_max=1), weight=0.001)

# stdp_cort2stn_AMPA_pop1 = p.STDPMechanism(
#         timing_dependence=p.SpikePairRule(
#             tau_plus=0.001, tau_minus=1,
#             A_plus=0.001, A_minus=1),
#         weight_dependence=p.AdditiveWeightDependence(
#             w_min=0.272, w_max=1), weight=0.3)

# # stdp_strd2_pop12gpe_pop1 = p.STDPMechanism(
# #         timing_dependence=p.SpikePairRule(
# #             tau_plus=0.25, tau_minus=0.5,
# #             A_plus=0.25, A_minus=0.5),
# #         weight_dependence=p.AdditiveWeightDependence(
# #             w_min=0.0272, w_max=1), weight=0.1)


# In[13]:


'''SETTING NETWORK static connectivity ( CONDUCTANCE) PARAMETERS'''

g_ampa = 0.5
g_nmda = 0.5

g_cort_strd1 = g_ampa
g_cort_strd2 = g_nmda
g_cort_fsi = g_nmda
g_cort_stn = g_nmda


pconn_cort_strd1 = 0.01
pconn_cort_strd2 = 0.01
pconn_cort_fsi = 0.01

pconn_cort_stn = 0.2

delay_lo_bound=1 # 0.2 # 1
delay_hi_bound=3 # 1.2 # 3

distr_strd1=RandomDistribution('uniform', (delay_lo_bound,delay_hi_bound))


distr_strd2 = RandomDistribution('uniform', (delay_lo_bound,delay_hi_bound))

distr_stn = RandomDistribution('uniform', (delay_lo_bound,delay_hi_bound))

distr_fsi  = RandomDistribution('uniform', (delay_lo_bound,delay_hi_bound))


# In[14]:


## arrays to hold object locations for stdp weight progression
projections_cort_strd1_nmda=[]
projections_cort_strd2_ampa=[]
projections_cort_fsi_ampa=[]
projections_cort_stn_ampa=[]

'''The label excitatory indicates AMPA and relates to the time constant tau_syn_E in the population definition. This is
indicated in the definition in spynnaker. Similarly, the label excitatory2 indicates NMDA and relates to the time constant
tau_syn_E2 in the population defintion on spynnaker.'''
##AMPA FOR STRD1
p.Projection(Poisson_source_ampa_strd1, strd1_ch1,
             p.FixedProbabilityConnector(p_connect=pconn_cort_strd1),
             p.StaticSynapse(weight=g_cort_strd1, delay=distr_strd1),# here I have divided by 1000
             receptor_type='excitatory')

# NMDA FOR STRD1 - STDP
projections_cort_strd1_nmda.append(p.Projection(Poisson_source_nmda_strd1, strd1_ch1,
             p.FixedProbabilityConnector(p_connect=pconn_cort_strd1),
             synapse_type=stdp_cort_strd1_nmda_ch1,
             receptor_type ='excitatory2'))

## AMPA FOR STRD2 - STDP
projections_cort_strd2_ampa.append(p.Projection(Poisson_source_ampa_strd2, strd2_ch1,
             p.FixedProbabilityConnector(p_connect=pconn_cort_strd2),
             synapse_type=stdp_cort_strd2_ampa_ch1,
             receptor_type='excitatory'))

# NMDA FOR STRD2
p.Projection(Poisson_source_nmda_strd2, strd2_ch1,
             p.FixedProbabilityConnector(p_connect=pconn_cort_strd2),
             p.StaticSynapse(weight=g_cort_strd2, delay=distr_strd2),
             receptor_type ='excitatory2')


## AMPA FOR FSI - STDP
projections_cort_fsi_ampa.append(p.Projection(Poisson_source_ampa_fsi, fsi_ch1,
             p.FixedProbabilityConnector(p_connect=pconn_cort_fsi),
             synapse_type=stdp_cort_fsi_ampa_ch1,
             receptor_type='excitatory'))

#NMDA FOR FSI
p.Projection(Poisson_source_nmda_fsi, fsi_ch1,
             p.FixedProbabilityConnector(p_connect=pconn_cort_fsi),
             p.StaticSynapse(weight=g_cort_fsi, delay=distr_fsi),
             receptor_type ='excitatory2')


## AMPA FOR STN - STDP

projections_cort_stn_ampa.append(p.Projection(Poisson_source_nmda_stn, stn_ch1,
             p.FixedProbabilityConnector(p_connect=pconn_cort_stn),
             synapse_type=stdp_cort_stn_ampa_ch1,
             receptor_type='excitatory'))

# NMDA FOR STN
p.Projection(Poisson_source_ampa_stn, stn_ch1,
             p.FixedProbabilityConnector(p_connect=pconn_cort_stn),
             p.StaticSynapse(weight=g_cort_stn, delay=distr_stn),
             receptor_type ='excitatory2')




# In[15]:


################     PROJECTION CONDUCTANCES WITHIN THE CHANNEL        ####################

g_gaba = 0.5  ### the gaba conductance


g_strd1_strd1 = g_gaba
g_strd1_strd2 = g_gaba
g_strd1_snr = g_gaba

g_strd2_strd2 = g_gaba
g_strd2_strd1 = g_gaba
g_strd2_gpe =g_gaba

g_fsi_strd1 = g_gaba
g_fsi_strd2 = g_gaba
g_fsi_fsi = g_gaba

g_gpe_stn = g_gaba
g_gpe_gpe = g_gaba
g_gpe_snr = g_gaba
g_gpe_fsi = g_gaba

g_snr_snr = g_gaba

g_stn_gpe = g_ampa
g_stn_snr = g_ampa


################ PROJECTION DELAYS WITHIN THE CHANNEL        ####################

distr_strd1_strd1 = RandomDistribution('uniform', (delay_lo_bound,delay_hi_bound))
distr_strd1_strd2 = RandomDistribution('uniform', (delay_lo_bound,delay_hi_bound))
distr_strd1_snr =  RandomDistribution('uniform', (delay_lo_bound,delay_hi_bound))

distr_strd2_strd2 = RandomDistribution('uniform', (delay_lo_bound,delay_hi_bound))
distr_strd2_strd1 = RandomDistribution('uniform', (delay_lo_bound,delay_hi_bound))
distr_strd2_gpe =  RandomDistribution('uniform', (delay_lo_bound,delay_hi_bound))

distr_fsi_fsi = RandomDistribution('uniform', (delay_lo_bound,delay_hi_bound))
distr_fsi_strd1 = RandomDistribution('uniform', (delay_lo_bound,delay_hi_bound))
distr_fsi_strd2 = RandomDistribution('uniform', (delay_lo_bound,delay_hi_bound))

distr_gpe_stn =  RandomDistribution('uniform', (delay_lo_bound,delay_hi_bound))
distr_gpe_gpe =  RandomDistribution('uniform', (delay_lo_bound,delay_hi_bound))
distr_gpe_snr =  RandomDistribution('uniform', (delay_lo_bound,delay_hi_bound))
distr_gpe_fsi =  RandomDistribution('uniform', (delay_lo_bound,delay_hi_bound))

distr_snr_snr = p.RandomDistribution("uniform", [delay_lo_bound,delay_hi_bound])


distr_stn_gpe = p.RandomDistribution("uniform", [delay_lo_bound,delay_hi_bound])
distr_stn_snr = p.RandomDistribution("uniform", [delay_lo_bound,delay_hi_bound])

################ PROJECTION PROBABILITIES WITHIN THE CHANNEL        ####################
p_conn=0.15
p_strd1_strd1 = p_conn
p_strd1_strd2 = p_conn
p_strd1_snr = p_conn

p_strd2_strd2 = p_conn
p_strd2_strd1 = p_conn
p_strd2_gpe = p_conn

p_fsi_strd1 = p_conn
p_fsi_strd2 = p_conn
p_fsi_fsi = p_conn

p_gpe_stn = p_conn
p_gpe_gpe = p_conn
p_gpe_snr = p_conn
p_gpe_fsi = p_conn

p_snr_snr = p_conn

p_stn_gpe = p_conn
p_stn_snr = p_conn


# In[16]:


p.Projection(strd1_ch1, strd1_ch1,
             p.FixedProbabilityConnector(p_connect=p_strd1_strd1),
             p.StaticSynapse(weight = g_strd1_strd1, delay=distr_strd1_strd1),
             receptor_type='inhibitory')

p.Projection(strd1_ch1, strd2_ch1,
             p.FixedProbabilityConnector(p_connect=p_strd1_strd2),
             p.StaticSynapse(weight = g_strd1_strd2, delay=distr_strd1_strd2),
             receptor_type='inhibitory')

projections_strd1_ch1_snr_ch1=p.Projection(strd1_ch1, snr_ch1,
             p.FixedProbabilityConnector(p_connect=p_strd1_snr),
#              synapse_type=stdp_strd1_snr_AMPA,
             p.StaticSynapse(weight = g_strd1_snr, delay=distr_strd1_snr),
             receptor_type='inhibitory')

p.Projection(strd2_ch1, strd1_ch1,
             p.FixedProbabilityConnector(p_connect=p_strd2_strd1),
             p.StaticSynapse(weight = g_strd2_strd1, delay=distr_strd2_strd1),
             receptor_type='inhibitory')

p.Projection(strd2_ch1, strd2_ch1,
             p.FixedProbabilityConnector(p_connect=p_strd2_strd2),
             p.StaticSynapse(weight = g_strd2_strd2, delay=distr_strd2_strd2),
             receptor_type='inhibitory')

projections_strd2_ch1_gpe_ch1=p.Projection(strd2_ch1, gpe_ch1,
             p.FixedProbabilityConnector(p_connect=p_strd2_gpe),
#              synapse_type=stdp_strd2_pop12gpe_pop1,
             p.StaticSynapse(weight = g_strd2_gpe, delay=distr_strd2_gpe),
             receptor_type='inhibitory')


p.Projection(fsi_ch1, strd1_ch1,
             p.FixedProbabilityConnector(p_connect=p_fsi_strd1),
             p.StaticSynapse(weight = g_fsi_strd1, delay=distr_fsi_strd1),
             receptor_type='inhibitory')

p.Projection(fsi_ch1, strd2_ch1,
             p.FixedProbabilityConnector(p_connect=p_fsi_strd2),
             p.StaticSynapse(weight = g_fsi_strd2, delay=distr_fsi_strd2),
             receptor_type='inhibitory')


p.Projection(fsi_ch1, fsi_ch1,
             p.FixedProbabilityConnector(p_connect=p_fsi_fsi),
             p.StaticSynapse(weight = g_fsi_fsi, delay=distr_fsi_fsi),
             receptor_type='inhibitory')

p.Projection(gpe_ch1, stn_ch1,
             p.FixedProbabilityConnector(p_connect=p_gpe_stn),
             p.StaticSynapse(weight=g_gpe_stn, delay=distr_gpe_stn),
             receptor_type='inhibitory')

p.Projection(gpe_ch1, gpe_ch1,
             p.FixedProbabilityConnector(p_connect=p_gpe_gpe),
             p.StaticSynapse(weight=g_gpe_gpe, delay=distr_gpe_gpe),
             receptor_type='inhibitory')

p.Projection(gpe_ch1, snr_ch1,
             p.FixedProbabilityConnector(p_connect=p_gpe_snr),
             p.StaticSynapse(weight=g_gpe_snr, delay=distr_gpe_snr),
             receptor_type='inhibitory')

p.Projection(gpe_ch1, fsi_ch1,
             p.FixedProbabilityConnector(p_connect=p_gpe_fsi),
             p.StaticSynapse(weight=g_gpe_fsi, delay=distr_gpe_fsi),
             receptor_type='inhibitory')

p.Projection(snr_ch1, snr_ch1,
             p.FixedProbabilityConnector(p_connect=p_snr_snr),
             p.StaticSynapse(weight=g_snr_snr, delay=distr_snr_snr),
             receptor_type='inhibitory')

p.Projection(stn_ch1, snr_ch1,
             p.FixedProbabilityConnector(p_connect=p_stn_snr),
             p.StaticSynapse(weight=g_stn_snr, delay=distr_stn_snr),
             receptor_type='excitatory')

p.Projection(stn_ch1, gpe_ch1,
             p.FixedProbabilityConnector(p_connect=p_stn_gpe),
             p.StaticSynapse(weight=g_stn_gpe, delay=distr_stn_snr),
             receptor_type='excitatory')



# In[17]:


################     PROJECTION CONDUCTANCES to the SNC       ####################

g_cort_snc = g_ampa
g_strd1_snc = g_gaba
g_strd2_snc = g_gaba
g_stn_snc = g_ampa
g_snr_snc = g_gaba
g_gpe_snc = g_gaba



################ PROJECTION DELAYS to the SNC      ####################

distr_cort_snc = RandomDistribution('uniform', (delay_lo_bound,delay_hi_bound))
distr_strd1_snc = RandomDistribution('uniform', (delay_lo_bound,delay_hi_bound))
distr_strd2_snc =  RandomDistribution('uniform', (delay_lo_bound,delay_hi_bound))

distr_stn_snc = RandomDistribution('uniform', (delay_lo_bound,delay_hi_bound))
distr_snr_snc = RandomDistribution('uniform', (delay_lo_bound,delay_hi_bound))
distr_gpe_snc =  RandomDistribution('uniform', (delay_lo_bound,delay_hi_bound))


################ PROJECTION PROBABILITIES for projections afferents to SNc    ####################

p_cort_snc = 0.1
p_strd1_snc = 0.1
p_strd2_snc = 0.1
p_stn_snc = 0.1
p_snr_snc = 0.1
p_gpe_snc = 0.1

################ PROJECTION PROBABILITIES for projections efferents of SNc    ####################
p_snc_strd1=0.1
p_snc_strd2=0.1
p_snc_fsi=0.1
p_snc_stn=0.1


# In[18]:


####XXXXXXXXXXXXX  DRAFT DRAFT xxxx IN PROGRESS xxx TO BE DONE xxxxxxxxxxxxxxxxxxxxxxxx

p.Projection(Poisson_source_ampa_snc, snc_ch1,
             p.FixedProbabilityConnector(p_connect=p_cort_snc),
             p.StaticSynapse(weight = g_cort_snc, delay=distr_cort_snc),
             receptor_type='excitatory')

p.Projection(strd1_ch1, snc_ch1,
             p.FixedProbabilityConnector(p_connect=p_strd1_snc),
             p.StaticSynapse(weight = g_strd1_snc, delay=distr_strd1_snc),
             receptor_type='inhibitory')

p.Projection(strd2_ch1, snc_ch1,
             p.FixedProbabilityConnector(p_connect=p_strd2_snc),
             p.StaticSynapse(weight = g_strd2_snc, delay=distr_strd2_snc),
             receptor_type='inhibitory')

p.Projection(snr_ch1, snc_ch1,
             p.FixedProbabilityConnector(p_connect=p_snr_snc),
             p.StaticSynapse(weight=g_snr_snc, delay=distr_snr_snc),
             receptor_type='inhibitory')

p.Projection(gpe_ch1, snc_ch1,
             p.FixedProbabilityConnector(p_connect=p_gpe_snc),
             p.StaticSynapse(weight=g_gpe_snc, delay=distr_gpe_snc),
             receptor_type='inhibitory')

p.Projection(stn_ch1, snc_ch1,
             p.FixedProbabilityConnector(p_connect=p_stn_snc),
             p.StaticSynapse(weight=g_stn_snc, delay=distr_stn_snc),
             receptor_type='excitatory')


# In[19]:


## OUTGOING PROJECTIONS FROM SNC

da_conc = 0.05
par_c=100
par_d=5
max_w=1

p.Projection(snc_ch1, strd1_ch1,
             p.FixedProbabilityConnector(p_connect=p_snc_strd1),
        synapse_type=p.extra_models.Neuromodulation(
        weight=da_conc, tau_c=par_c, tau_d=par_d, w_max=max_w),
        receptor_type='reward', label='reward snc to strd1')

p.Projection(snc_ch1, strd2_ch1,
             p.FixedProbabilityConnector(p_connect=p_snc_strd2),
        synapse_type=p.extra_models.Neuromodulation(
        weight=da_conc, tau_c=par_c, tau_d=par_d, w_max=max_w),
        receptor_type='reward', label='reward snc to strd2')

p.Projection(snc_ch1, fsi_ch1,
             p.FixedProbabilityConnector(p_connect=p_snc_fsi),
        synapse_type=p.extra_models.Neuromodulation(
        weight=da_conc, tau_c=par_c, tau_d=par_d, w_max=max_w),
        receptor_type='reward', label='reward snc to fsi')

p.Projection(snc_ch1, stn_ch1,
             p.FixedProbabilityConnector(p_connect=p_snc_stn),
        synapse_type=p.extra_models.Neuromodulation(
        weight=da_conc, tau_c=par_c, tau_d=par_d, w_max=max_w),
        receptor_type='reward', label='reward snc to stn')


# In[20]:


strd1_ch1.record(['spikes'])#,'gsyn_exc'])
strd2_ch1.record(['spikes'])#,'gsyn_exc'])
fsi_ch1.record(['spikes'])#,'v','gsyn_exc'])
gpe_ch1.record(['spikes'])#,'v','gsyn_exc'])
snr_ch1.record(['spikes'])#,'v','gsyn_exc'])
stn_ch1.record(['spikes'])#,'v','gsyn_exc'])
snc_ch1.record(['spikes'])#,'v','gsyn_exc'])


# In[21]:


p.run(TotalDuration)


# In[ ]:


strd1_spikes1 = np.asarray(strd1_ch1.spinnaker_get_data("spikes"))
strd2_spikes1 = np.asarray(strd2_ch1.spinnaker_get_data("spikes"))
fsi_spikes1 = np.asarray(fsi_ch1.spinnaker_get_data("spikes"))
stn_spikes1 = np.asarray(stn_ch1.spinnaker_get_data("spikes"))
gpe_spikes1 = np.asarray(gpe_ch1.spinnaker_get_data("spikes"))
snr_spikes1 = np.asarray(snr_ch1.spinnaker_get_data(["spikes"]))
snc_spikes1 = np.asarray(snc_ch1.spinnaker_get_data(["spikes"]))


# In[ ]:


n=0
plt.figure(n)
plt.scatter(strd1_spikes1[:,1], strd1_spikes1[:,0],marker='|',s=20,c='red')
plt.xlabel('Time (msec)')
plt.ylabel('number of neurons')
plt.title('Raster for strd1_spikes1 population')
n=n+1
plt.figure(n)
plt.scatter(strd2_spikes1[:,1], strd2_spikes1[:,0],marker='|',s=30,c='purple')
plt.xlabel('Time (msec)')
plt.ylabel('number of neurons')
plt.title('Raster for strd2_spikes1 population')
n=n+1
plt.figure(n)
plt.scatter(fsi_spikes1[:,1], fsi_spikes1[:,0],marker='|',s=20,c='orange')
plt.xlabel('Time (msec)')
plt.ylabel('number of neurons')
plt.title('Raster for fsi_spikes1 population')
n=n+1
plt.figure(n)
plt.scatter(stn_spikes1[:,1], stn_spikes1[:,0],marker='.',s=10,c='green')
plt.xlabel('Time (msec)')
plt.ylabel('number of neurons')
plt.title('Raster for stn_spikes1 population')
n=n+1
plt.figure(n)
plt.scatter(gpe_spikes1[:,1], gpe_spikes1[:,0],marker='.',s=10,c='blue')
plt.xlabel('Time (msec)')
plt.ylabel('number of neurons')
plt.title('Raster for gpe_spikes1 population')

n=n+1
plt.figure(n)
plt.scatter(snr_spikes1[:,1], snr_spikes1[:,0],marker='.',s=10,c='purple')
plt.xlabel('Time (msec)')
plt.ylabel('number of neurons')
plt.title('Raster for snr_spikes1 population')
n=n+1
plt.figure(n)
plt.scatter(snc_spikes1[:,1], snc_spikes1[:,0],marker='.',s=10,c='purple')
plt.xlabel('Time (msec)')
plt.ylabel('number of neurons')
plt.title('Raster for snc_spikes1 population')


# In[ ]:


temp = projections_cort_strd2_ampa[0].get(["weight"], "list")
print(len(temp))
plt.plot(temp)
print(temp)


# In[ ]:


# projections_cort2_strd1_w=[]
# projections_cort2_strd1_w.append(projections_cort2_pop1[0].get(["weight"], "list"))

# projections_cort2_strd2_w=[]
# projections_cort2_strd2_w.append(projections_cort2_pop1[1].get(["weight"], "list"))

# projections_cort2_strdfsi_w=[]
# projections_cort2_strdfsi_w.append(projections_cort2_pop1[2].get(["weight"], "list"))

# projections_cort2_stn_w=[]
# projections_cort2_stn_w.append(projections_cort2_pop1[3].get(["weight"], "list"))

# projection_strd1_snr_w=[]
# projection_strd1_snr_w.append(projections_strd1_pop1_snr_pop1.get(["weight"], "list"))

# projection_strd2_gpe_w=[]
# projection_strd2_gpe_w.append(projections_strd2_pop1_gpe_pop1.get(["weight"], "list"))


# In[ ]:


# for numtrials in range(5):
#     p.run(200)
#     projections_cort2_strd1_w.append(projections_cort2_pop1[0].get(["weight"], "list"))
#     projections_cort2_strd2_w.append(projections_cort2_pop1[1].get(["weight"], "list"))
#     projections_cort2_strdfsi_w.append(projections_cort2_pop1[2].get(["weight"], "list"))
#     projections_cort2_stn_w.append(projections_cort2_pop1[3].get(["weight"], "list"))
#     projection_strd1_snr_w.append(projections_strd1_pop1_snr_pop1.get(["weight"], "list"))
#     projection_strd2_gpe_w.append(projections_strd2_pop1_gpe_pop1.get(["weight"], "list"))


# In[ ]:


# spikelist_strd1_pop1=[]
# spikelist_strd2_pop1=[]
# spikelist_fsi1_pop1=[]
# spikelist_gpe_pop1=[]
# spikelist_snr_pop1=[]
# spikelist_stn_pop1=[]





# In[ ]:


# mean_rate_strd1_spikes1 = [] # to store mean firing rate for every trial
# mean_rate_strd2_spikes1 = [] # to store mean firing rate for every trial
# mean_rate_fsi_spikes1 = []
# mean_rate_stn_spikes1 = []
# mean_rate_gpe_spikes1 = []
# mean_rate_snr_spikes1 = []
# mean_rate_snc_spikes1 = []




# # Store and print Mean Firing Rates
# spkrt_lo=1000
# spkrt_hi=9000
# mean_rate_strd1_spikes1.append(get_mean_rate_new(numCellsPerCol_STR, strd1_spikes1, spkrt_lo, spkrt_hi))
# mean_rate_strd2_spikes1.append(get_mean_rate_new(numCellsPerCol_STR, strd2_spikes1, spkrt_lo, spkrt_hi))
# mean_rate_fsi_spikes1.append(get_mean_rate_new(numCellsPerCol_FSI, fsi_spikes1, spkrt_lo, spkrt_hi))
# mean_rate_stn_spikes1.append(get_mean_rate_new(numCellsPerCol_STN, stn_spikes1, spkrt_lo, spkrt_hi))
# mean_rate_gpe_spikes1.append(get_mean_rate_new(numCellsPerCol_GPe, gpe_spikes1, spkrt_lo, spkrt_hi))
# mean_rate_snr_spikes1.append(get_mean_rate_new(numCellsPerCol_SNR, snr_spikes1, spkrt_lo, spkrt_hi))
# mean_rate_snc_spikes1.append(get_mean_rate_new(numCellsPerCol_SNC, snc_spikes1, spkrt_lo, spkrt_hi))


# In[ ]:



# print("strd1 mean freq (spikes/sec): "+str(mean_rate_strd1_spikes1[-1]))
# print("strd2 mean freq (spikes/sec): "+str(mean_rate_strd2_spikes1[-1]))
# print("fsi mean freq (spikes/sec): "+str(mean_rate_fsi_spikes1[-1]))
# print("stn mean freq (spikes/sec): "+str(mean_rate_stn_spikes1[-1]))
# print("gpe mean freq (spikes/sec): "+str(mean_rate_gpe_spikes1[-1]))
# print("snr mean freq (spikes/sec): "+str(mean_rate_snr_spikes1[-1]))
# print("snc mean freq (spikes/sec): "+str(mean_rate_snc_spikes1[-1]))


# In[ ]:


# import sys
# np.set_printoptions(threshold=sys.maxsize)


# In[ ]:


# n=0


# # n=n+1
# # plt.figure(n)
# # plt.plot(avg_signal_strd1_voltage1)
# # plt.xlabel('Time (msec)')
# # plt.ylabel('Membrane potential (mV)')
# # plt.title('Average membrane potential STRD1  population')

# # n=n+1
# # plt.figure(n)
# # plt.plot(avg_signal_strd2_voltage1)
# # plt.xlabel('Time (msec)')
# # plt.ylabel('Membrane potential (mV)')
# # plt.title('Average membrane potential STRD2 population')


# In[ ]:


# '''Checking out the STN,GPe and SNr histograms'''
# plt.xlabel('Time(s)',fontsize=22)
# plt.ylabel('Mean firing rate of STRD1',fontsize=22)
# plt.xticks(fontsize=22)
# plt.yticks(fontsize=22)
# # plt.xlim(-0.5, 12)
# # plt.ylim(0, 75)

# strd1_pop_data = strd1_spikes1[:, 1]  ## just extract the times of each spike
# #print(len(post_pop_data))
# strd1_pop_hist = my_firingrate(strd1_pop_data , checkpoint, my_resol)/numCellsPerCol_STR
# # Figure,
# plt.plot(strd1_pop_hist, c='blue',label='stn_pop',marker='o',linestyle='dotted')
# # plt.title('PSTH for STN')

# # gpe_pop_data = gpe_spikes1[:, 1]  ## just extract the times of each spike
# # gpe_pop_hist = my_firingrate(gpe_pop_data , checkpoint, my_resol)/numCellsPerCol_GPe
# # plt.plot(gpe_pop_hist, c='purple',label='gpe_pop',marker='x',linestyle='dashdot')


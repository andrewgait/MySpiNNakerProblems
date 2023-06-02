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


# In[2]:


from spynnaker.pyNN.extra_algorithms.splitter_components import (
SplitterAbstractPopulationVertexNeuronsSynapses, SplitterPoissonDelegate)


# pop_splitter_strd1_pop1 = SplitterAbstractPopulationVertexNeuronsSynapses(n_synapse_vertices=3,
#                                             max_delay=5,allow_delay_extension=False)
# pop_splitter_strd2_pop1 = SplitterAbstractPopulationVertexNeuronsSynapses(n_synapse_vertices=3,
#                                             max_delay=5,allow_delay_extension=False)

pop_splitter_strd1_pop1 = SplitterAbstractPopulationVertexNeuronsSynapses(3)
pop_splitter_strd2_pop1 = SplitterAbstractPopulationVertexNeuronsSynapses(3)


# In[3]:


TotalDuration = 10000  ### TOTAL RUN TIME
TimeInt = 0.1    ### SIMULATION TIME STEP
TotalDataPoints = int(TotalDuration*(1/TimeInt))
countt=4


# In[4]:


print(TotalDataPoints)


# In[5]:


my_resol = 1000 #msec
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


# In[6]:


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


# In[7]:


def print_mean_firing_rate():
    print("E mean firing rate & total no. of spikes: ",get_mean_rate_new(N_E, esp,500,Total_duration-500))#500,Total_duration-500))
    print("I mean firing rate & total no. of spikes: ",get_mean_rate_new(N_I, isp,500,Total_duration-500))#500,Total_duration-500))


# In[8]:


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
strd1_v_init = -80.0
strd1_u_init = strd1_b * strd1_v_init


strd2_a=0.02
strd2_b=0.2
strd2_c=-65.0
strd2_d=8.0
strd2_v_init = -80.0
strd2_u_init = strd2_b * strd2_v_init

current_bias_str = -30.0

fsi_a=0.1
fsi_b=0.2
fsi_c=-65.0
fsi_d=8.0
fsi_v_init = -70.0
fsi_u_init = fsi_b * fsi_v_init

current_bias_fsi = -10.0

gpe_a=0.005
gpe_b=0.585
gpe_c=-65.0
gpe_d=4.0
gpe_v_init = -70.0
gpe_u_init = gpe_b * gpe_v_init

current_bias_gpe = 2.0

snr_a = 0.005
snr_b = 0.32
snr_c = -65.0
snr_d = 2.0
snr_v_init = -70.0
snr_u_init = snr_b * snr_v_init

current_bias_snr = 5.0

stn_a=0.005
stn_b=0.265
stn_c=-65.0
stn_d=2.0
stn_v_init = -60.0
stn_u_init = stn_b * stn_v_init

current_bias_stn = 5.0

snc_a=0.0025
snc_b=0.2
snc_c=-55 #-65
snc_d=2#12 #8
snc_v_init=-70.0
snc_u_init = snc_b * snc_v_init

current_bias_snc =15 #15.0 ###in literature 9.0

'''SETTING NUMBER OF NEURONS PER CHANNEL'''

numCellsPerCol_STR = 63#125#1255#314# <--1/4th of 1255 #### 90% of 50% of 2790000 = 1255500
numCellsPerCol_FSI = 84####139
numCellsPerCol_STN = 14 ###13560
numCellsPerCol_SNR = 27 ####26320
numCellsPerCol_GPe = 46 ###45960
numPoissonInput_str=600
numPoissonInput_str_fsi=42
numPoissonInput_stn=7
numCellsPerCol_SNC=8
# numPeriodicInput =314


# In[9]:


'''NOW START RUNNING MULTIPLE TRIALS, AND INITIALISE THE ARRAYS'''
numtrials = 1

gpe_hist1 = np.zeros((numtrials, checkpoint))
snr_hist1 = np.zeros((numtrials, checkpoint))
stn_hist1 = np.zeros((numtrials, checkpoint))
fsi_hist1 = np.zeros((numtrials, checkpoint))


# In[10]:


# for thisTrial in range(0, numtrials):

''' SET UP SPINNAKER AND BEGIN SIMULATION'''
p.setup(timestep=0.1,time_scale_factor=1)
p.set_number_of_neurons_per_core(p.extra_models.Izhikevich_cond_dual,16)
p.set_number_of_neurons_per_core(p.extra_models.Izhikevich_cond,16)

'''STRIATUM OF THE BASAL GANGLIA: MEDIUM SPINY NEURONS (MSN - D1 / D2)'''

strd1_cell_params = {'a': strd1_a,
                 'b': strd1_b,
                 'c': strd1_c,
                 'd': strd1_d,
                 'v': strd1_v_init,
                 'u': strd1_u_init,
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
                 'v': strd2_v_init,
                 'u': strd2_u_init,
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
                'v': fsi_v_init,
                'u': fsi_u_init,
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
               'v': gpe_v_init,
               'u': gpe_u_init,
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
               'v': snr_v_init,
               'u': snr_u_init,
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
               'v': stn_v_init,
               'u': stn_u_init,
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
               'v': snc_v_init,
               'u': snc_u_init,
               'tau_syn_E': tau_ampa,
               'tau_syn_I': tau_gabaa,
               'i_offset': current_bias_snc,
               'isyn_exc': E_ampa,
               'isyn_inh': E_gabaa
              }


# In[11]:


''' THE FIRST CHANNEL'''
strd1_pop1 = p.Population(numCellsPerCol_STR, p.extra_models.Izhikevich_cond_dual, strd1_cell_params,
                          label='strd1_pop1', additional_parameters={"splitter": SplitterAbstractPopulationVertexNeuronsSynapses(1)})
strd2_pop1 = p.Population(numCellsPerCol_STR, p.extra_models.Izhikevich_cond_dual, strd2_cell_params,
                          label='strd2_pop1',additional_parameters={"splitter": SplitterAbstractPopulationVertexNeuronsSynapses(1)})
fsi_pop1 = p.Population(numCellsPerCol_FSI, p.extra_models.Izhikevich_cond_dual, fsi_cell_params, label='fsi_pop1',
                       additional_parameters={"splitter": SplitterAbstractPopulationVertexNeuronsSynapses(1)})
gpe_pop1 = p.Population(numCellsPerCol_GPe, p.extra_models.Izhikevich_cond, gpe_cell_params, label='gpe_pop1',
                       additional_parameters={"splitter": SplitterAbstractPopulationVertexNeuronsSynapses(1)})
snr_pop1 = p.Population(numCellsPerCol_SNR, p.extra_models.Izhikevich_cond, snr_cell_params, label='snr_pop1',
                       additional_parameters={"splitter": SplitterAbstractPopulationVertexNeuronsSynapses(1)})
stn_pop1 = p.Population(numCellsPerCol_STN, p.extra_models.Izhikevich_cond_dual, stn_cell_params, label='stn_pop1',
                       additional_parameters={"splitter": SplitterAbstractPopulationVertexNeuronsSynapses(1)})

snc_pop1=p.Population(numCellsPerCol_SNC, p.extra_models.Izhikevich_cond, snc_cell_params, label='reward_pop1'
   , additional_parameters={"splitter": SplitterAbstractPopulationVertexNeuronsSynapses(1)})


# In[12]:


'''BASE POISSON INPUTS TO ALL CHANNELS FOR THE ENTIRE SIMULATION DURATION OF 5 SECONDS'''
Rate_Poisson_Inp_base = 3
start_Poisson_Inp_base = 100
Duration_Poisson_Inp_base = 9900
# poisson_splitter = SplitterPoissonDelegate()
spike_source_Poisson_base1_strd1 = p.Population(numPoissonInput_str, p.SpikeSourcePoisson, {'rate': Rate_Poisson_Inp_base,
    'duration': Duration_Poisson_Inp_base,'start': start_Poisson_Inp_base}, label='spike_source_Poisson_base1',
                                         additional_parameters={"splitter": SplitterPoissonDelegate()})
spike_source_Poisson_base2_strd1 = p.Population(numPoissonInput_str, p.SpikeSourcePoisson, {'rate': Rate_Poisson_Inp_base,
    'duration': Duration_Poisson_Inp_base,'start': start_Poisson_Inp_base}, label='spike_source_Poisson_base2',
                                         additional_parameters={"splitter": SplitterPoissonDelegate()})

spike_source_Poisson_base1_strd2 = p.Population(numPoissonInput_str, p.SpikeSourcePoisson, {'rate': Rate_Poisson_Inp_base,
    'duration': Duration_Poisson_Inp_base,'start': start_Poisson_Inp_base}, label='spike_source_Poisson_base1',
                                         additional_parameters={"splitter": SplitterPoissonDelegate()})
spike_source_Poisson_base2_strd2 = p.Population(numPoissonInput_str, p.SpikeSourcePoisson, {'rate': Rate_Poisson_Inp_base,
    'duration': Duration_Poisson_Inp_base,'start': start_Poisson_Inp_base}, label='spike_source_Poisson_base2',
                                         additional_parameters={"splitter": SplitterPoissonDelegate()})


spike_source_Poisson_base1_strfsi = p.Population(numPoissonInput_str_fsi, p.SpikeSourcePoisson, {'rate': Rate_Poisson_Inp_base,
    'duration': Duration_Poisson_Inp_base,'start': start_Poisson_Inp_base}, label='spike_source_Poisson_base1',
                                         additional_parameters={"splitter": SplitterPoissonDelegate()})
spike_source_Poisson_base2_strfsi = p.Population(numPoissonInput_str_fsi, p.SpikeSourcePoisson, {'rate': Rate_Poisson_Inp_base,
    'duration': Duration_Poisson_Inp_base,'start': start_Poisson_Inp_base}, label='spike_source_Poisson_base2',
                                         additional_parameters={"splitter": SplitterPoissonDelegate()})

'''This are used for the cortext to STN as in the original BG work(by Prof.basab) we have 2 poisson sources so I have not
changed them.Thought of putting it to 14
'''
spike_source_Poisson_base1_stn = p.Population(numPoissonInput_stn, p.SpikeSourcePoisson, {'rate': Rate_Poisson_Inp_base,
    'duration': Duration_Poisson_Inp_base,'start': start_Poisson_Inp_base}, label='spike_source_Poisson_base2')

spike_source_Poisson_base2_stn = p.Population(numPoissonInput_stn, p.SpikeSourcePoisson, {'rate': Rate_Poisson_Inp_base,
    'duration': Duration_Poisson_Inp_base,'start': start_Poisson_Inp_base}, label='spike_source_Poisson_base2')


# In[13]:


stdp_cort2strd1_NMDA = p.STDPMechanism(
        timing_dependence=p.SpikePairRule(
            tau_plus=2, tau_minus=1,
            A_plus=2, A_minus=1),
        weight_dependence=p.AdditiveWeightDependence(
            w_min=0, w_max=0.0096), weight=0.00001)


# In[14]:


'''SETTING THE DOPAMINE LEVELS AND CONDUCTANCE PARAMETERS'''
g_ampa = 0.5

mod_ampa_d2 = 0.2  ###00.156 in humphries nnet 2009

phi_max_dop = 5  ##(Scaled within 0 to 5)
phi_msn_dop = 2.75 #0.55 * phi_max_dop
phi_fsi_dop = 3.75 #0.75 * phi_max_dop
phi_stn_dop = 2 # 0.4 * phi_max_dop  ###(Note that this is scaled between 0 and 16.67)

'''SETTING NETWORK CONDUCTANCE PARAMETERS'''

g_cort2strd1 = g_ampa
g_cort2strd2 = 0.225 #g_ampa * (1 - (mod_ampa_d2 * phi_msn_dop))
g_cort2fsi = 0.125 #g_ampa * (1 - (mod_ampa_d2 * phi_fsi_dop))
g_cort2stn = 0.3 #g_ampa * (1 - (mod_ampa_d2 * phi_stn_dop))

#################DEFINING DISTRIBUTION OF DELAY PARAMETERS
#     intra_pop_delay = RandomDistribution('uniform', (1,3), rng=NumpyRNG(seed=85520))



pconn_cort2str = 0.15
pconn_cort2stn = 0.2

distr_strd1=RandomDistribution('uniform', (9,12), rng=NumpyRNG(seed=85520))


distr_strd2 = RandomDistribution('uniform', (9,12), rng=NumpyRNG(seed=85521))

distr_stn = RandomDistribution('uniform', (9,12), rng=NumpyRNG(seed=85522))

distr_fsi  = RandomDistribution('uniform', (9,12), rng=NumpyRNG(seed=85523))


# In[15]:


######projections for CHANEL 1
# poplist_ch1 = [strd1_pop1, strd2_pop1, fsi_pop1, stn_pop1]
poplist_ch1 = [fsi_pop1, stn_pop1]

g_pop = [g_cort2strd1, g_cort2strd2, g_cort2fsi, g_cort2stn]

distr_pop = [distr_strd1, distr_strd2, distr_fsi, distr_stn]



spike_source_Poisson_base1=[spike_source_Poisson_base1_strd1,spike_source_Poisson_base1_strd2,spike_source_Poisson_base1_strfsi,
                          spike_source_Poisson_base1_stn]
spike_source_Poisson_base2=[spike_source_Poisson_base2_strd1,spike_source_Poisson_base2_strd2,spike_source_Poisson_base2_strfsi,
                          spike_source_Poisson_base2_stn]


count=0
projections_cort2_pop1=[]



p.Projection(spike_source_Poisson_base1_strd1, strd1_pop1,
            p.FixedProbabilityConnector(p_connect=pconn_cort2str),
            p.StaticSynapse(weight=g_cort2strd1/4, delay=distr_strd1),# here I have divided by 1000
            receptor_type='excitatory')
projections_cort2_pop1.append(p.Projection(spike_source_Poisson_base2_strd1, strd1_pop1,
            p.FixedProbabilityConnector(p_connect=pconn_cort2str),
            synapse_type=stdp_cort2strd1_NMDA,
#              p.StaticSynapse(weight=g_cort2strd1/52, delay=distr_strd1),
            receptor_type ='excitatory2'))


projections_cort2_pop1.append(p.Projection(spike_source_Poisson_base1_strd2, strd2_pop1,
            p.FixedProbabilityConnector(p_connect=pconn_cort2str),
#                      synapse_type=stdp_cort[count1],
            p.StaticSynapse(weight=g_cort2strd2/16, delay=distr_strd2),# here I have divided by 1000
            receptor_type='excitatory'))
p.Projection(spike_source_Poisson_base2_strd2, strd2_pop1,
            p.FixedProbabilityConnector(p_connect=pconn_cort2str),
            p.StaticSynapse(weight=g_cort2strd2/32, delay=distr_strd2),
            receptor_type ='excitatory2')


projections_cort2_pop1.append(p.Projection(spike_source_Poisson_base1_strfsi, fsi_pop1,
            p.FixedProbabilityConnector(p_connect=pconn_cort2str),
#                      synapse_type=stdp_cort[count1],
            p.StaticSynapse(weight=g_cort2fsi/4.5, delay=distr_fsi),# here I have divided by 1000
            receptor_type='excitatory'))
p.Projection(spike_source_Poisson_base2_strfsi, fsi_pop1,
            p.FixedProbabilityConnector(p_connect=pconn_cort2str),
            p.StaticSynapse(weight=g_cort2fsi/9, delay=distr_fsi),
            receptor_type ='excitatory2')


projections_cort2_pop1.append(p.Projection(spike_source_Poisson_base1_stn, stn_pop1,
            p.FixedProbabilityConnector(p_connect=pconn_cort2str),
#                      synapse_type=stdp_cort[count1],
            p.StaticSynapse(weight=g_cort2stn/11, delay=distr_stn),   # here I have divided by 1000
            receptor_type='excitatory'))
p.Projection(spike_source_Poisson_base2_stn, stn_pop1,
            p.FixedProbabilityConnector(p_connect=pconn_cort2str),
            p.StaticSynapse(weight=g_cort2stn/22, delay=distr_stn),
            receptor_type ='excitatory2')


# In[16]:


'''INTRA-CHANNEL PROJECTIONS'''

################     EFFERENTS OF STRIATUM        ####################


g_gaba = 0.5 * g_ampa  ### the gaba conductance

mod_gaba = 0.073  ##0.625 ### the level of modulation of dopamine of gaba via the D2 and D1 receptors

g_strd12snr = 0.3 #0.30018 #g_gaba * (1 + mod_gaba * phi_msn_dop)
g_strd22gpe =0.2 # 0.1998 #g_gaba * (1 - mod_gaba * phi_msn_dop)
g_str2str = 0.0982 #0.3921* g_gaba #(1.0/2.55) * g_gaba




distr_strd12snr =  RandomDistribution('uniform', (5,7), rng=NumpyRNG(seed=85520))#p.RandomDistribution("uniform", [5, 7])
distr_strd22gpe =  RandomDistribution('uniform', (5,7), rng=NumpyRNG(seed=85520))#p.RandomDistribution("uniform", [5, 7])
distr_str2str = RandomDistribution('uniform', (5,7), rng=NumpyRNG(seed=85520))#p.RandomDistribution("uniform", [2, 3])
#try change (2,3)


# In[17]:



'''projections of chanel1'''
#STR-D1 to snr is D1-modulated and STR-D2 to GPe is D2 modulated(presynaptically so I think we have to reward) so we have
#STDP in their paths as below.

projections_strd1_pop1_snr_pop1=p.Projection(strd1_pop1, snr_pop1,
             p.FixedProbabilityConnector(p_connect=0.15),
#              synapse_type=stdp_strd1_pop12snr_pop1,
             p.StaticSynapse(weight = g_strd12snr, delay=distr_strd12snr),
             receptor_type='inhibitory')
projections_strd2_pop1_gpe_pop1=p.Projection(strd2_pop1, gpe_pop1,
             p.FixedProbabilityConnector(p_connect=0.15),
#              synapse_type=stdp_strd2_pop12gpe_pop1,
             p.StaticSynapse(weight = g_strd22gpe, delay=distr_strd22gpe),
             receptor_type='inhibitory')

#All the loops in the design are static so below is code for Striatum population loops
p.Projection(strd1_pop1, strd1_pop1,
             p.FixedProbabilityConnector(p_connect=0.1),
             p.StaticSynapse(weight = g_str2str, delay=distr_str2str),
             receptor_type='inhibitory')
p.Projection(strd1_pop1, strd2_pop1,
             p.FixedProbabilityConnector(p_connect=0.1),
             p.StaticSynapse(weight = g_str2str, delay=distr_str2str),
             receptor_type='inhibitory')
p.Projection(strd2_pop1, strd1_pop1,
             p.FixedProbabilityConnector(p_connect=0.1),
             p.StaticSynapse(weight = g_str2str, delay=distr_str2str),
             receptor_type='inhibitory')
p.Projection(strd2_pop1, strd2_pop1,
             p.FixedProbabilityConnector(p_connect=0.1),
             p.StaticSynapse(weight = g_str2str, delay=distr_str2str),
             receptor_type='inhibitory')


################     EFFERENTS OF FAST SPIKING INTERNEURONS       ####################
# In the BG paper(by prof basab) did  not make any neuromodulated projections from FSI neurons
#so all the efferents of FSI are static
'''projections in chanel 1'''
p.Projection(fsi_pop1, strd1_pop1,
             p.FixedProbabilityConnector(p_connect=0.1),
             p.StaticSynapse(weight = g_str2str, delay=distr_str2str),
             receptor_type='inhibitory')

p.Projection(fsi_pop1, strd2_pop1,
             p.FixedProbabilityConnector(p_connect=0.1),
             p.StaticSynapse(weight = g_str2str, delay=distr_str2str),
             receptor_type='inhibitory')


p.Projection(fsi_pop1, fsi_pop1,
             p.FixedProbabilityConnector(p_connect=0.1),
             p.StaticSynapse(weight = g_str2str, delay=distr_str2str),
             receptor_type='inhibitory')


# In[18]:


################     EFFERENTS OF GLOBAL PALLIDUS - EXTERNA       ####################

g_gaba_gpe = 0.1429 #0.14285 #0.57142*g_gaba # (1.0 / 1.75) * g_gaba
g_gpe2stn = 0.1429  #g_gaba_gpe
g_gpe2gpe = 0.1429 #g_gaba_gpe
g_gpe2snr = 0.1429 #g_gaba_gpe
g_gpe2fsi = 0.1429 #g_gaba_gpe


distr_gpe2stn =  RandomDistribution('uniform', (5,7), rng=NumpyRNG(seed=85520))#p.RandomDistribution("uniform", [5, 7])
distr_gpe2gpe =  RandomDistribution('uniform', (2,3), rng=NumpyRNG(seed=85520))#p.RandomDistribution("uniform", [2, 3])
distr_gpe2snr =  RandomDistribution('uniform', (5,7), rng=NumpyRNG(seed=85520))#p.RandomDistribution("uniform", [5, 7])
distr_gpe2fsi =  RandomDistribution('uniform', (5,7), rng=NumpyRNG(seed=85520))#p.RandomDistribution("uniform", [5, 7])


# In[19]:


'''All the effernts of GPe are static  but we have to see whether GPe to STN has D2 receptors and can we implement this?
I think I found a paper where it says there are D2 receptors from GPe to STN projection'''

'''projections in chanel 1'''
p.Projection(gpe_pop1, stn_pop1,
             p.FixedProbabilityConnector(p_connect=0.25),
             p.StaticSynapse(weight=g_gpe2stn, delay=distr_gpe2stn),
             receptor_type='inhibitory')
p.Projection(gpe_pop1, gpe_pop1,
             p.FixedProbabilityConnector(p_connect=0.25),
             p.StaticSynapse(weight=g_gpe2gpe, delay=distr_gpe2gpe),
             receptor_type='inhibitory')
p.Projection(gpe_pop1, snr_pop1,
             p.FixedProbabilityConnector(p_connect=0.25),
             p.StaticSynapse(weight=g_gpe2snr, delay=distr_gpe2snr),
             receptor_type='inhibitory')
p.Projection(gpe_pop1, fsi_pop1,
             p.FixedProbabilityConnector(p_connect=0.05),
             p.StaticSynapse(weight=g_gpe2fsi, delay=distr_gpe2fsi),
             receptor_type='inhibitory')


# In[20]:


'''We did not neuromodulate the self projections of SNr, it is static projection'''
################     EFFERENTS OF SUBSTANTIA NIGRA PARS RETICULATA       ####################

g_gaba_snr = 0.1429 #0.14285 #0.57142* g_gaba #(1 / 1.75) * g_gaba
g_snr2snr = g_gaba_snr

distr_snr2snr = p.RandomDistribution("uniform", [2, 3])
'''projections in chanel 1'''
p.Projection(snr_pop1, snr_pop1,
             p.FixedProbabilityConnector(p_connect=0.25),
             p.StaticSynapse(weight=g_snr2snr, delay=distr_snr2snr),
             receptor_type='inhibitory')


# In[21]:


'''INTER-CHANNEL CONNECTIVITY: DIFFUSE EFFERENTS FROM THE STN'''


distr_stn2gpe_diffuse =  RandomDistribution('uniform', (9,12), rng=NumpyRNG(seed=85520))
distr_stn2snr_diffuse =  RandomDistribution('uniform', (9,12), rng=NumpyRNG(seed=85520))
distr_stn2gpe =  RandomDistribution('uniform', (5,7), rng=NumpyRNG(seed=85520))
distr_stn2snr =  RandomDistribution('uniform', (5,7), rng=NumpyRNG(seed=85520))

p_conn_diffuse=0.5

g_stn2snr_diffuse = 0.05 #(g_ampa* (1 - (mod_ampa_d2 * phi_stn_dop))) / 6.0
g_stn2gpe_diffuse = 0.05 # (g_ampa* (1 - (mod_ampa_d2 * phi_stn_dop))) / 6.0

'''We cannot make D2-modulated projection from STN to SNr because already we have from STR-D1 to SNr D1 modulated'''
'''projections from chanel 1 to chanel 1'''
p.Projection(stn_pop1, snr_pop1,
             p.FixedProbabilityConnector(p_connect=p_conn_diffuse),
             p.StaticSynapse(weight=g_stn2snr_diffuse, delay=distr_stn2snr),
             receptor_type='excitatory')
'''we can make D2 modulation from STN as in the paper by Prof.basabdatta et al used STN to GPe a D2 modulated AMPA projection
as in the equation 7'''
projections_stn_pop1_gpe_pop1=p.Projection(stn_pop1, gpe_pop1,
             p.FixedProbabilityConnector(p_connect=p_conn_diffuse),
             p.StaticSynapse(weight=g_stn2gpe_diffuse, delay=distr_stn2snr),
             receptor_type='excitatory')


# In[22]:


'''Projections to SNc '''

Rate_Poisson_Inp_base = 3
rng = np.random.default_rng(85524)
start_Poisson_Inp_base = 500#rng.integers(low=500, high=700)
#start_Poisson_Inp_base = 500#RandomDistribution('uniform', (500, 700), rng=NumpyRNG(seed=85524)) ###50
Duration_Poisson_Inp_base = 9500
cortextosnc = p.Population(8, p.SpikeSourcePoisson, {'rate': Rate_Poisson_Inp_base, 'duration': Duration_Poisson_Inp_base,'start': start_Poisson_Inp_base}, label='spike_source_Poisson_base1')


projections_ctx_pop1_snc_pop1=p.Projection(cortextosnc, snc_pop1,
             #p.FixedProbabilityConnector(p_connect=0.15),
             p.OneToOneConnector(),
             p.StaticSynapse(weight = g_strd12snr, delay=distr_strd12snr),
             receptor_type='excitatory')
projections_strd1_pop1_snr_pop1=p.Projection(strd1_pop1, snc_pop1,
             p.FixedProbabilityConnector(p_connect=0.15),
             p.StaticSynapse(weight = g_strd12snr, delay=distr_strd12snr),
             receptor_type='inhibitory')

projections_strd2_pop1_snr_pop1=p.Projection(strd2_pop1, snc_pop1,
             p.FixedProbabilityConnector(p_connect=0.15),
             p.StaticSynapse(weight = g_strd12snr, delay=distr_strd12snr),
             receptor_type='inhibitory')

p.Projection(snr_pop1, snc_pop1,
             p.FixedProbabilityConnector(p_connect=0.25),
             p.StaticSynapse(weight=g_snr2snr, delay=distr_snr2snr),
             receptor_type='inhibitory')

p.Projection(gpe_pop1, snc_pop1,
             p.FixedProbabilityConnector(p_connect=0.25),
             p.StaticSynapse(weight=g_gpe2snr, delay=distr_gpe2snr),
             receptor_type='inhibitory')

p.Projection(stn_pop1, snc_pop1,
             p.FixedProbabilityConnector(p_connect=p_conn_diffuse),
             p.StaticSynapse(weight=g_stn2snr_diffuse, delay=distr_stn2snr),
             receptor_type='excitatory')


# In[23]:


DA_concentration_reward = 0.05
max_w=0.0096
snc_2_strd1_pop_projection=p.Projection(
        snc_pop1, strd1_pop1, p.AllToAllConnector(),
        synapse_type=p.extra_models.Neuromodulation(
            weight=DA_concentration_reward, tau_c=100.0, tau_d=5.0, w_max=max_w),
        receptor_type='reward', label='reward synapses')


# In[24]:


# p.Projection(snc_pop1, snc_pop1,
#              p.FixedProbabilityConnector(p_connect=0.25),
#              p.StaticSynapse(weight=g_snr2snr, delay=distr_snr2snr),
#              receptor_type='inhibitory')


# In[25]:


strd1_pop1.record(['spikes','gsyn_exc'])
strd2_pop1.record(['spikes','gsyn_exc'])
fsi_pop1.record(['spikes','v','gsyn_exc'])
gpe_pop1.record(['spikes','v','gsyn_exc'])
snr_pop1.record(['spikes','v','gsyn_exc'])
stn_pop1.record(['spikes','v','gsyn_exc'])
snc_pop1.record(['spikes','v','gsyn_exc'])


# In[26]:


projections_cort2_strd1_w=[]
projections_cort2_strd1_w.append(projections_cort2_pop1[0].get(["weight"], "list"))


# In[27]:


for numtrials in range(5):
    p.run(2000)
    projections_cort2_strd1_w.append(projections_cort2_pop1[0].get(["weight"], "list"))


# In[ ]:


spikelist_strd1_pop1=[]
spikelist_strd2_pop1=[]
spikelist_fsi1_pop1=[]
spikelist_gpe_pop1=[]
spikelist_snr_pop1=[]
spikelist_stn_pop1=[]


# In[ ]:


strd1_spikes1 = np.asarray(strd1_pop1.spinnaker_get_data("spikes"))
strd2_spikes1 = np.asarray(strd2_pop1.spinnaker_get_data("spikes"))
fsi_spikes1 = np.asarray(fsi_pop1.spinnaker_get_data("spikes"))
stn_spikes1 = np.asarray(stn_pop1.spinnaker_get_data("spikes"))
gpe_spikes1 = np.asarray(gpe_pop1.spinnaker_get_data("spikes"))
snr_spikes1 = np.asarray(snr_pop1.spinnaker_get_data(["spikes"]))
snc_spikes1 = np.asarray(snc_pop1.spinnaker_get_data(["spikes"]))


# In[ ]:


mean_rate_strd1_spikes1 = [] # to store mean firing rate for every trial
mean_rate_strd2_spikes1 = [] # to store mean firing rate for every trial
mean_rate_fsi_spikes1 = []
mean_rate_stn_spikes1 = []
mean_rate_gpe_spikes1 = []
mean_rate_snr_spikes1 = []
mean_rate_snc_spikes1 = []


# In[ ]:


# Store and print Mean Firing Rates
spkrt_lo=1000
spkrt_hi=9000
mean_rate_strd1_spikes1.append(get_mean_rate_new(numCellsPerCol_STR, strd1_spikes1, spkrt_lo, spkrt_hi))
mean_rate_strd2_spikes1.append(get_mean_rate_new(numCellsPerCol_STR, strd2_spikes1, spkrt_lo, spkrt_hi))
mean_rate_fsi_spikes1.append(get_mean_rate_new(numCellsPerCol_FSI, fsi_spikes1, spkrt_lo, spkrt_hi))
mean_rate_stn_spikes1.append(get_mean_rate_new(numCellsPerCol_STN, stn_spikes1, spkrt_lo, spkrt_hi))
mean_rate_gpe_spikes1.append(get_mean_rate_new(numCellsPerCol_GPe, gpe_spikes1, spkrt_lo, spkrt_hi))
mean_rate_snr_spikes1.append(get_mean_rate_new(numCellsPerCol_SNR, snr_spikes1, spkrt_lo, spkrt_hi))
mean_rate_snc_spikes1.append(get_mean_rate_new(numCellsPerCol_SNC, snc_spikes1, spkrt_lo, spkrt_hi))
print("strd1 mean freq (spikes/sec): "+str(mean_rate_strd1_spikes1[-1]))
print("strd2 mean freq (spikes/sec): "+str(mean_rate_strd2_spikes1[-1]))
print("fsi mean freq (spikes/sec): "+str(mean_rate_fsi_spikes1[-1]))
print("stn mean freq (spikes/sec): "+str(mean_rate_stn_spikes1[-1]))
print("gpe mean freq (spikes/sec): "+str(mean_rate_gpe_spikes1[-1]))
print("snr mean freq (spikes/sec): "+str(mean_rate_snr_spikes1[-1]))
print("snc mean freq (spikes/sec): "+str(mean_rate_snc_spikes1[-1]))


# In[ ]:


strd1_pop1_g =strd1_pop1.spinnaker_get_data('gsyn_exc')
strd2_pop2_g =strd2_pop1.spinnaker_get_data('gsyn_exc')
fsi_pop1_g =fsi_pop1.spinnaker_get_data('gsyn_exc')
stn_pop1_g=stn_pop1.spinnaker_get_data('gsyn_exc')

p.end()

# In[ ]:


import sys
np.set_printoptions(threshold=sys.maxsize)


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

# n=n+1
# plt.figure(n)
# plt.plot(avg_signal_strd1_voltage1)
# plt.xlabel('Time (msec)')
# plt.ylabel('Membrane potential (mV)')
# plt.title('Average membrane potential STRD1  population')

# n=n+1
# plt.figure(n)
# plt.plot(avg_signal_strd2_voltage1)
# plt.xlabel('Time (msec)')
# plt.ylabel('Membrane potential (mV)')
# plt.title('Average membrane potential STRD2 population')


# In[ ]:


'''Checking out the STN,GPe and SNr histograms'''
plt.xlabel('Time(s)',fontsize=22)
plt.ylabel('Mean firing rate of STRD1',fontsize=22)
plt.xticks(fontsize=22)
plt.yticks(fontsize=22)
# plt.xlim(-0.5, 12)
# plt.ylim(0, 75)

strd1_pop_data = strd1_spikes1[:, 1]  ## just extract the times of each spike
#print(len(post_pop_data))
strd1_pop_hist = my_firingrate(strd1_pop_data , checkpoint, my_resol)/numCellsPerCol_STR
# Figure,
plt.plot(strd1_pop_hist, c='blue',label='stn_pop',marker='o',linestyle='dotted')
# plt.title('PSTH for STN')

# gpe_pop_data = gpe_spikes1[:, 1]  ## just extract the times of each spike
# gpe_pop_hist = my_firingrate(gpe_pop_data , checkpoint, my_resol)/numCellsPerCol_GPe
# plt.plot(gpe_pop_hist, c='purple',label='gpe_pop',marker='x',linestyle='dashdot')


# In[ ]:


'''Checking out the STN,GPe and SNr histograms'''
plt.xlabel('Time(s)',fontsize=22)
plt.ylabel('Mean firing rate of STRD2',fontsize=22)
plt.xticks(fontsize=22)
plt.yticks(fontsize=22)

strd2_pop_data = strd2_spikes1[:, 1]  ## just extract the times of each spike
strd2_pop_hist = my_firingrate(strd2_pop_data , checkpoint, my_resol)/numCellsPerCol_STR
plt.plot(strd2_pop_hist, c='blue',label='stn_pop',marker='o',linestyle='dotted')


# In[ ]:


'''Checking out the STN,GPe and SNr histograms'''
plt.xlabel('Time(s)',fontsize=22)
plt.ylabel('Mean firing rate of STRFSI',fontsize=22)
plt.xticks(fontsize=22)
plt.yticks(fontsize=22)

fsi_pop_data = fsi_spikes1[:, 1]  ## just extract the times of each spike
fsi_pop_hist = my_firingrate(fsi_pop_data , checkpoint, my_resol)/numCellsPerCol_STR
plt.plot(fsi_pop_hist, c='blue',label='stn_pop',marker='o',linestyle='dotted')


# In[ ]:


'''Checking out the STN,GPe and SNr histograms'''
plt.xlabel('Time(s)',fontsize=22)
plt.ylabel('Mean firing rate of STN',fontsize=22)
plt.xticks(fontsize=22)
plt.yticks(fontsize=22)

stn_pop_data = stn_spikes1[:,1]  ## just extract the times of each spike
stn_pop_hist = my_firingrate(stn_pop_data , checkpoint, my_resol)/numCellsPerCol_STR
plt.plot(stn_pop_hist, c='blue',label='stn_pop',marker='o',linestyle='dotted')


# In[ ]:


'''Checking out the STN,GPe and SNr histograms'''
plt.xlabel('Time(s)',fontsize=22)
plt.ylabel('Mean firing rate of SNr',fontsize=22)
plt.xticks(fontsize=22)
plt.yticks(fontsize=22)

snr_pop_data = snr_spikes1[:,1]  ## just extract the times of each spike
snr_pop_hist = my_firingrate(snr_pop_data , checkpoint, my_resol)/numCellsPerCol_STR
plt.plot(snr_pop_hist, c='blue',label='stn_pop',marker='o',linestyle='dotted')


# In[ ]:


'''Checking out the STN,GPe and SNr histograms'''
plt.xlabel('Time(s)',fontsize=22)
plt.ylabel('Mean firing rate of GPe',fontsize=22)
plt.xticks(fontsize=22)
plt.yticks(fontsize=22)

gpe_pop_data = gpe_spikes1[:,1]  ## just extract the times of each spike
gpe_pop_hist = my_firingrate(gpe_pop_data , checkpoint, my_resol)/numCellsPerCol_STR
plt.plot(gpe_pop_hist, c='blue',label='stn_pop',marker='o',linestyle='dotted')


# In[ ]:


'''Checking out the STN,GPe and SNr histograms'''
plt.xlabel('Time(s)',fontsize=22)
plt.ylabel('Mean firing rate',fontsize=22)
plt.xticks(fontsize=22)
plt.yticks(fontsize=22)
plt.xlim(-0.5, 12)
plt.ylim(0, 75)

stn_pop_data = stn_spikes1[:, 1]  ## just extract the times of each spike
#print(len(post_pop_data))
stn_pop_hist = my_firingrate(stn_pop_data , checkpoint, my_resol)/numCellsPerCol_STN
# Figure,
plt.plot(stn_pop_hist, c='blue',label='stn_pop',marker='o',linestyle='dotted')
# plt.title('PSTH for STN')

gpe_pop_data = gpe_spikes1[:, 1]  ## just extract the times of each spike
gpe_pop_hist = my_firingrate(gpe_pop_data , checkpoint, my_resol)/numCellsPerCol_GPe
plt.plot(gpe_pop_hist, c='purple',label='gpe_pop',marker='x',linestyle='dashdot')
# plt.title('PSTH for GPe')

snr_pop_data = snr_spikes1[:, 1]  ## just extract the times of each spike
snr_pop_hist = my_firingrate(snr_pop_data , checkpoint, my_resol)/numCellsPerCol_SNR
plt.plot(snr_pop_hist, c='orange',label='snr_pop',marker='>',ls="--")

plt.legend(fontsize=18)
filename = './Neuromodulation_with_one_projection_between_CTX_and_STRD1'+'.png'
plt.tight_layout()
plt.savefig(filename)
plt.show()
plt.close()


# In[ ]:


projections_cort2_strd1_w_array=np.array(projections_cort2_strd1_w)
projections_cort2_strd1_w_transpose=np.transpose(projections_cort2_strd1_w)


# In[ ]:


'''This code is for seeing weights which are close to 0.0'''
count=0
for i in range(0,len(projections_cort2_strd1_w_transpose[2])):
    for j in range(0,len(projections_cort2_strd1_w_transpose[2][i])):
        if(projections_cort2_strd1_w_transpose[2][i][j]<0.0095 and projections_cort2_strd1_w_transpose[2][i][j]>0 ):
            #print(projections_cort2_strd1_w_transpose[2][i][j])
            count=count+1
print(count)


# In[ ]:


'''This code is for seeing weights which are close to 1.0'''
count=0
for i in range(0,len(projections_cort2_strd1_w_transpose[2])):
    for j in range(0,len(projections_cort2_strd1_w_transpose[2][i])):
        if(projections_cort2_strd1_w_transpose[2][i][j]>0.0095):
            #print(projections_cort2_strd1_w_transpose[2][i][j])
            count=count+1
print(count)


# In[ ]:


projections_cort2_strd1_w


# In[ ]:


#PLOTTING WEIGHTS PROGRESSION FROM CORTICAL TO STRD1
projections_cort2_strd1_w_transpose=np.transpose(projections_cort2_strd1_w)
plt.figure()
plt.xlabel('Time(s)',fontsize=22)
plt.ylabel('Weights',fontsize=22)
# plt.xticks(fontsize=22)
plt.yticks(fontsize=22)
plt.plot(np.transpose(projections_cort2_strd1_w_transpose[2]))
plt.show()


# In[ ]:





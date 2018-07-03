import spynnaker8 as p
import time
import matplotlib.pyplot as plt
import numpy as np
from numpy import *

start_time = time.time()

# total duration of simulation
TotalDuration = 10000.0

# time-step of model equation solver
time_resol = 0.1
TimeInt = 1.0 / time_resol
TotalDataPoints = int(TotalDuration * TimeInt)
# this is in ms.

''' Run the simulation for the total duration set above for each trial, and each dc current value'''
'''Pulse time lengths'''
duration1 = 4000
duration2 = 2000
duration3 = 4000

''' Initialising Model connectivity parameters'''
intra_pop_delay = 1.0
intra_nucleus_delay = 2.0
inter_nucleus_delay = 3.0
inter_pop_delay = 3.0

p_in2tcr = 0.15
p_trn2tcr = 0.15
p_tcr2trn = 0.35

w_tcr2trn = 2.0

w_trn2tcr = 2.0
w_trn2trn = 2.0

w_in2tcr = 2.0
w_in2in = 2.0

''' Initialising Izhikevich spiking neuron model parameters.
We have used the current-based model here.'''

# Tonic mode parameters
tcr_a_tonic = 0.02
tcr_b_tonic = 0.2
tcr_c_tonic = -65.0
tcr_d_tonic = 6.0
tcr_v_init_tonic = -65.0

in_a_tonic = 0.1
in_b_tonic = 0.2
in_c_tonic = -65.0
in_d_tonic = 6.0
in_v_init_tonic = -70.0

trn_a_tonic = 0.02
trn_b_tonic = 0.2
trn_c_tonic = -65.0
trn_d_tonic = 6.0
trn_v_init_tonic = -75.0

tcr_a = tcr_a_tonic
tcr_b = tcr_b_tonic
tcr_c = tcr_c_tonic
tcr_d = tcr_d_tonic
tcr_v_init = tcr_v_init_tonic

in_a = in_a_tonic
in_b = in_b_tonic
in_c = in_c_tonic
in_d = in_d_tonic
in_v_init = in_v_init_tonic

trn_a = trn_a_tonic
trn_b = trn_b_tonic
trn_c = trn_c_tonic
trn_d = trn_d_tonic
trn_v_init = trn_v_init_tonic

tcr_u_init = tcr_b * tcr_v_init
in_u_init = in_b * in_v_init
trn_u_init = trn_b * trn_v_init

# excitatory input time constant
tau_ex = 4

# inhibitory input time constant
tau_inh = 6

scale_fact = 10
NumCellsTCR = 8 * scale_fact
NumCellsIN = 2 * scale_fact
NumCellsTRN = 4 * scale_fact

currentPulse = 10  # 0
'''Starting the SpiNNaker Simulator'''
p.setup(timestep=time_resol, min_delay=1.0, max_delay=14.0)

'''Defining each cell type as dictionary'''

# THALAMOCORTICAL RELAY CELLS (TCR)
TCR_cell_params = {'a': tcr_a, 'b': tcr_b, 'c': tcr_c, 'd': tcr_d,
                   'v_init': tcr_v_init, 'u_init': tcr_u_init,
                   'tau_syn_E': tau_ex, 'tau_syn_I': tau_inh,
                   'i_offset': currentPulse
                   }

# THALAMIC INTERNEURONS (IN)
IN_cell_params = {'a': in_a, 'b': in_b, 'c': in_c, 'd': in_d,
                  'v_init': in_v_init, 'u_init': in_u_init,
                  'tau_syn_E': tau_ex, 'tau_syn_I': tau_inh,
                  'i_offset': currentPulse
                  }

# THALAMIC RETICULAR NUCLEUS (TRN)
TRN_cell_params = {'a': trn_a, 'b': trn_b, 'c': trn_c, 'd': trn_d,
                   'v_init': trn_v_init, 'u_init': trn_u_init,
                   'tau_syn_E': tau_ex, 'tau_syn_I': tau_inh,
                   'i_offset': currentPulse
                   }

'''Creating populations of each cell type'''

TCR_pop = p.Population(
    NumCellsTCR, p.Izhikevich(**TCR_cell_params), label='TCR_pop')
IN_pop = p.Population(
    NumCellsIN, p.Izhikevich(**IN_cell_params), label='IN_pop')
TRN_pop = p.Population(
    NumCellsTRN, p.Izhikevich(**TRN_cell_params), label='TRN_pop')

'''TCR2TRN'''
Proj2 = p.Projection(
    TCR_pop, TRN_pop, p.FixedProbabilityConnector(p_connect=p_tcr2trn),
    p.StaticSynapse(weight=w_tcr2trn, delay=inter_nucleus_delay),
    receptor_type='excitatory')

'''TRN2TCR'''
Proj3 = p.Projection(
    TRN_pop, TCR_pop, p.FixedProbabilityConnector(p_connect=p_trn2tcr),
    p.StaticSynapse(weight=w_trn2tcr, delay=inter_nucleus_delay),
    receptor_type='inhibitory')

'''TRN2TRN'''
Proj4 = p.Projection(
    TRN_pop, TRN_pop, p.FixedProbabilityConnector(p_connect=0.2),
    p.StaticSynapse(weight=w_trn2trn, delay=intra_pop_delay),
    receptor_type='inhibitory')

'''IN2TCR'''
Proj5 = p.Projection(
    IN_pop, TCR_pop, p.FixedProbabilityConnector(p_connect=p_in2tcr),
    p.StaticSynapse(weight=w_in2tcr, delay=intra_nucleus_delay),
    receptor_type='inhibitory')

'''IN2IN'''
Proj6 = p.Projection(
    IN_pop, IN_pop, p.FixedProbabilityConnector(p_connect=0.236),
    p.StaticSynapse(weight=w_in2in, delay=intra_pop_delay),
    receptor_type='inhibitory')

''' Recording simulation data'''

'''recording the spikes only'''
TCR_pop.record(("spikes"))
IN_pop.record(("spikes"))
TRN_pop.record(("spikes"))
p.run(TotalDuration)

# p.run(duration1)
#
# IN_pop.set(i_offset=60)
# p.run(duration2)
# IN_pop.set(i_offset=10)
# p.run(duration3)


'''
On simulation completion, extract the data off the spinnaker machine
memory
'''
tcrSpikeRaster = np.asarray(TCR_pop.spinnaker_get_data("spikes"))
inSpikeRaster = np.asarray(IN_pop.spinnaker_get_data("spikes"))
trnSpikeRaster = np.asarray(TRN_pop.spinnaker_get_data("spikes"))

f1 = plt.plot(tcrSpikeRaster[:, 1], tcrSpikeRaster[:, 0], '.')
plt.show(f1)

f2 = plt.plot(inSpikeRaster[:, 1], inSpikeRaster[:, 0], '.')
plt.show(f2)

f3 = plt.plot(trnSpikeRaster[:, 1], trnSpikeRaster[:,  0], '.')
plt.show(f3)

'''RELEASE THE MACHINE'''
p.end()

# # print "--- {} SECONDS ELAPSED ---".format(time.time() - start_time)
# # print "validating input isi used in the model: {}".format(Inp_isi)

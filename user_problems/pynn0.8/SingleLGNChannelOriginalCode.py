"""
17TH/18TH mARCH 2018:
Ok - failed to run the OOp based LGN code on this small spinnaker board. It runs fine on spalloc.
The original LGN single instance code runs fine on the small board.
So, starting on that, and modifying this to incorporate the ON and OFF cells as well as the Fixed Post Connector...
 ...and let's see if this works?...
 The FixedNumberPostConnector somehow recruits a lot more cores than required, which overflows the capacity of the
 small spinnaker board.....

 ok...so now we know that the culprit is the FixedNumberPostConnector.
 Once this is sorted, the OOP code should also work here.

*********************************************************************
*********************************************************************
Version uploaded on ModelDB October 2017.
Author:
Basabdatta Sen Bhattacharya, APT group, School of Computer Science,
University of Manchester, 2017.

If you are using the code,
please cite the original work on the model - details are:

B. Sen-Bhattacharya, T. Serrano-Gotarredona, L. Balassa, A. Bhattacharya,
A.B. Stokes, A. Rowley, I. Sugiarto, S.B. Furber,
"A spiking neural network model of the Lateral Geniculate Nucleus on the
SpiNNaker machine", Frontiers in Neuroscience, vol. 11 (454), 2017.

Free online access:
http://journal.frontiersin.org/article/10.3389/fnins.2017.00454/abstract

"""
import spynnaker8 as p
import time
import matplotlib.pyplot as plt
import numpy as np
from numpy import *

start_time = time.time()


''' Initialising Time and Frequency parameters'''

# total duration of simulation
TotalDuration = 1000.0

# time-step of model equation solver
time_resol = 0.1
TimeInt = 1.0 / time_resol
TotalDataPoints = int(TotalDuration * TimeInt)
# this is in ms.

''' Initialising Model connectivity parameters'''
intra_pop_delay = 1.0
intra_nucleus_delay = 2.0
inter_nucleus_delay = 3.0
inter_pop_delay = 3.0

p_in2tcr = 0.232

# WHICH IS 1/4th of 0.309 THIS IS KEPT AT A REDUCED VALUE UNDER NORMAL
# SIMULATIONS - HOWEVER, FOR REDUCED EFFECT OF IN, THIS IS INCREASED TO 0.232
# WHICH IS 3/4TH OF 30.9
p_trn2tcr = 0.077
p_tcr2trn = 0.35

w_tcr2trn = 3.0

w_trn2tcr = 2.0
w_trn2trn = 2.0

# SET TO 1 WHEN TESTING FOR REDUCED EFFECT OF THE IN ALONG WITH REDUCING
# P_IN2TCR
w_in2tcr = 8.0
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

# a constant DC bias current; this is used here for testing the RS and FS
# characteristics of IZK neurons


# excitatory input time constant
tau_ex = 4

# inhibitory input time constant
tau_inh = 6

current_Pulse = 4.0
'''Starting the SpiNNaker Simulator'''
p.setup(timestep=0.1, min_delay=1.0, max_delay=14.0)

'''Defining each cell type as dictionary'''

# THALAMOCORTICAL RELAY CELLS (TCR)
TCR_cell_params = {'a': tcr_a, 'b': tcr_b, 'c': tcr_c, 'd': tcr_d,
                   'v_init': tcr_v_init, 'u_init': tcr_u_init,
                   'tau_syn_E': tau_ex, 'tau_syn_I': tau_inh,
                   'i_offset': current_Pulse
                   }

# THALAMIC INTERNEURONS (IN)
IN_cell_params = {'a': in_a, 'b': in_b, 'c': in_c, 'd': in_d,
                  'v_init': in_v_init, 'u_init': in_u_init,
                  'tau_syn_E': tau_ex, 'tau_syn_I': tau_inh,
                  'i_offset': current_Pulse
                  }

# THALAMIC RETICULAR NUCLEUS (TRN)
TRN_cell_params = {'a': trn_a, 'b': trn_b, 'c': trn_c, 'd': trn_d,
                   'v_init': trn_v_init, 'u_init': trn_u_init,
                   'tau_syn_E': tau_ex, 'tau_syn_I': tau_inh,
                   'i_offset': current_Pulse
                   }


'''Creating populations of each cell type'''
scale_fact = 10
NumCellsTCR = 8*scale_fact
NumCellsIN = 2*scale_fact
NumCellsTRN = 4*scale_fact
TCR_pop = p.Population(
    NumCellsTCR, p.Izhikevich(**TCR_cell_params), label='TCR_pop')
IN_pop = p.Population(
    NumCellsIN, p.Izhikevich(**IN_cell_params), label='IN_pop')
TRN_pop = p.Population(
    NumCellsTRN, p.Izhikevich(**TRN_cell_params), label='TRN_pop')


'''TCR2TRN'''
Proj2 = p.Projection(
     TCR_pop, TRN_pop, p.FixedNumberPreConnector(n=2, verbose=True),
     p.StaticSynapse(weight=w_tcr2trn, delay=inter_nucleus_delay),
     receptor_type='excitatory')

#Proj2 = p.Projection(
#    TCR_pop, TRN_pop, p.FixedProbabilityConnector(p_connect=p_tcr2trn),
#    p.StaticSynapse(weight=w_tcr2trn, delay=inter_nucleus_delay),
#    receptor_type='excitatory')

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

# recording the spikes and voltage
TCR_pop.record(("spikes", "v"))
IN_pop.record(("spikes", "v"))
TRN_pop.record(("spikes", "v"))


''' Run the simulation for the total duration set'''
p.run(TotalDuration)


''' On simulation completion, extract the data off the spinnaker machine
memory'''

# extracting the spike time data
TCR_spikes = TCR_pop.spinnaker_get_data("spikes")
IN_spikes = IN_pop.spinnaker_get_data("spikes")
TRN_spikes = TRN_pop.spinnaker_get_data("spikes")

# extracting the membrane potential data (in millivolts)
TCR_membrane_volt2 = TCR_pop.spinnaker_get_data("v")
IN_membrane_volt2 = IN_pop.spinnaker_get_data("v")
TRN_membrane_volt2 = TRN_pop.spinnaker_get_data("v")

''' Now release the SpiNNaker machine'''
p.end()

TCR_membrane_volt = np.reshape(TCR_membrane_volt2[:, 2], [NumCellsTCR, TotalDataPoints])
print('reshaped the TCR signal as 2D matrix')
avgsignaltcr = np.mean(TCR_membrane_volt, axis=0)

IN_membrane_volt = np.reshape(IN_membrane_volt2[:, 2], [NumCellsIN, TotalDataPoints])
print('reshaped the IN signal as 2D matrix')
avgsignalin = mean(IN_membrane_volt, axis=0)

TRN_membrane_volt = np.reshape(TRN_membrane_volt2[:, 2], [NumCellsTRN, TotalDataPoints])
print('reshaped the TRN signal as 2D matrix')
avgsignaltrn = mean(TRN_membrane_volt, axis=0)


plt.figure(1)
plt.plot(TCR_spikes[:, 1], TCR_spikes[:, 0], '.')

plt.figure(2)
plt.plot(IN_spikes[:, 1], IN_spikes[:, 0], '.')

plt.figure(3)
plt.plot(TRN_spikes[:, 1], TRN_spikes[:, 0], '.')

plt.figure(5)
plt.plot([x for x in range(TotalDataPoints)], avgsignaltcr)

plt.figure(6)
plt.plot([x for x in range(TotalDataPoints)], avgsignalin)

plt.figure(7)
plt.plot([x for x in range(TotalDataPoints)], avgsignaltrn)

plt.show()
''' The user can now either save the data for further use, or plot this
using standard python tools'''

# print "--- {} SECONDS ELAPSED ---".format(time.time() - start_time)
# print "validating input isi used in the model: {}".format(Inp_isi)

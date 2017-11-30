"""
1st December
After a lot of literature review throughout November, and setting up interfacing with the retina, and another bout of
literature review on convergence-divergence relationships between retina and TCR(!) - today - I am starting testing
population by population, at a time, and set their spiking pattern when they receive the retinal input.


10th nov: I am testing the code today with retinal inputs recorded by Teresa - so commenting out the corresponding lines
with the poisson source inputs.
23rd October:
I took the modelDB uploaded version and am using this as a standard single channel lgn model now.
I have added polotting tools - figure panel was too slow a rendering and therefore arranged to get the data in the numpy
format. So that I can now use standard plotting tools in python to plot.

Also, added a base Poisson noise to see the effect on periodicity of the output.

today i just arranged to see the spike train outputs of the populations. Tomorrow, I will find
the code that I had written earlier to see the membrane potentials.
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
import math

start_time = time.time()


''' Initialising Time and Frequency parameters'''

# total duration of simulation
TotalDuration = 1000.0

# time-step of model equation solver
time_resol = 0.1
TimeInt = 1.0 / time_resol
TotalDataPoints = int(TotalDuration * TimeInt)


''' Initialising Model connectivity parameters'''
intra_pop_delay = 1.0
intra_nucleus_delay = 2.0
inter_nucleus_delay = 3.0
inter_pop_delay = 3.0
input_delay = inter_pop_delay

w_ret2tcr = 2.0
w_ret2in = 2.0
w_in2tcr = 2.0
w_in2in = 2.0

p_in2tcr = 0.1545

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

tcr_u_init = tcr_b * tcr_v_init
in_u_init = in_b * in_v_init

current_Pulse = 10.0

tau_ex = 6
tau_inh = 4

'''Starting the SpiNNaker Simulator'''
p.setup(timestep=0.1, min_delay=1.0, max_delay=14.0)
## set number of neurons per core to 50, for the spike source to avoid clogging
p.set_number_of_neurons_per_core(p.SpikeSourceArray, 50)

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

'''Creating populations of each cell type'''
scale_fact = 10
NumCellsTCR = 4*scale_fact
NumCellsIN = 1*scale_fact
NumCellsRET = 2 * scale_fact
# NumCellsTRN = 4*scale_fact

TCR_pop_ON = p.Population(
    NumCellsTCR, p.Izhikevich(**TCR_cell_params), label='TCR_pop_ON')
TCR_pop_OFF = p.Population(
    NumCellsTCR, p.Izhikevich(**TCR_cell_params), label='TCR_pop_OFF')
IN_pop_ON = p.Population(
    NumCellsIN, p.Izhikevich(**IN_cell_params), label='IN_pop_ON')
IN_pop_OFF = p.Population(
    NumCellsIN, p.Izhikevich(**IN_cell_params), label='IN_pop_OFF')

'''Retinal outputs at a single frequency imported'''
#
# import diode_sine_pos_30Hz
# eventos1 = diode_sine_pos_30Hz.eventos
# eventos1 = [z * 10 for z in eventos1]
#
# import diode_sine_neg_30Hz
# eventos2 = diode_sine_neg_30Hz.eventos
# eventos2 = [z * 10 for z in eventos2]
#
# eventos1part = eventos1[200:220]
# eventos2part = eventos2[200:220]
#
# print len(eventos1part)
# print '\n'
# print len(eventos2part)
#
# retina_output_spikes_pos = p.Population(NumCellsRET, p.SpikeSourceArray, {'spike_times': eventos1part}, label='retinaspikeoutput_pos')
# retina_output_spikes_neg = p.Population(NumCellsRET, p.SpikeSourceArray, {'spike_times': eventos2part}, label='retinaspikeoutput_neg')
# '''Source to TCR population projections'''
#
# Proj00 = p.Projection(retina_output_spikes_pos, TCR_pop_ON,
#                  p.FixedProbabilityConnector(p_connect=0.07),
#                  synapse_type=p.StaticSynapse(weight=w_ret2tcr, delay=input_delay),
#                  receptor_type='excitatory')
#
# Proj01 = p.Projection(retina_output_spikes_neg, TCR_pop_OFF,
#                  p.FixedProbabilityConnector(p_connect=0.07),
#                  synapse_type=p.StaticSynapse(weight=w_ret2tcr, delay=input_delay),
#                  receptor_type='excitatory')
#
#
# Proj10 = p.Projection(retina_output_spikes_pos, IN_pop_ON,
#                  p.FixedProbabilityConnector(p_connect=0.47),
#                  synapse_type=p.StaticSynapse(weight=w_ret2in, delay=input_delay),
#                  receptor_type='excitatory')
#
# Proj11 = p.Projection(retina_output_spikes_neg, IN_pop_OFF,
#                  p.FixedProbabilityConnector(p_connect=0.47),
#                  synapse_type=p.StaticSynapse(weight=w_ret2in, delay=input_delay),
#                  receptor_type='excitatory')


''' Recording simulation data'''

# recording the spikes and voltage

TCR_pop_ON.record(("spikes", "v"))
TCR_pop_OFF.record(("spikes", "v"))
IN_pop_ON.record(("spikes", "v"))
IN_pop_OFF.record(("spikes", "v"))



''' Run the simulation for the total duration set'''
p.run(TotalDuration)


''' On simulation completion, extract the data off the spinnaker machine
memory'''

# extracting the spike time data
TCR_spikes_ON = TCR_pop_ON.spinnaker_get_data("spikes")
TCR_spikes_OFF = TCR_pop_OFF.spinnaker_get_data("spikes")
IN_spikes_ON = IN_pop_ON.spinnaker_get_data("spikes")
IN_spikes_OFF = IN_pop_OFF.spinnaker_get_data("spikes")


# extracting the membrane potential data (in millivolts)
TCR_membrane_volt2_ON = TCR_pop_ON.spinnaker_get_data("v")
TCR_membrane_volt2_OFF = TCR_pop_OFF.spinnaker_get_data("v")
IN_membrane_volt2_ON = IN_pop_ON.spinnaker_get_data("v")
IN_membrane_volt2_OFF = IN_pop_OFF.spinnaker_get_data("v")


print len(TCR_membrane_volt2_ON)
# np.savetxt('./testingVolt.csv', TCR_membrane_volt2)


TCR_membrane_volt_ON = np.reshape(TCR_membrane_volt2_ON[:, 2], [NumCellsTCR, TotalDataPoints])
print('reshaped the TCR signal as 2D matrix')
avgsignaltcr_ON = np.mean(TCR_membrane_volt_ON, axis=0)
print(np.size(avgsignaltcr_ON))

TCR_membrane_volt_OFF = np.reshape(TCR_membrane_volt2_OFF[:, 2], [NumCellsTCR, TotalDataPoints])
print('reshaped the TCR_OFF signal as 2D matrix')
avgsignaltcr_OFF = np.mean(TCR_membrane_volt_OFF, axis=0)
print(np.size(avgsignaltcr_OFF))

TotalAvgMembraneTCR = avgsignaltcr_OFF + avgsignaltcr_ON

IN_membrane_volt_ON = np.reshape(IN_membrane_volt2_ON[:, 2], [NumCellsIN, TotalDataPoints])
print('reshaped the IN signal as 2D matrix')
avgsignalin_ON = mean(IN_membrane_volt_ON, axis=0)
print(size(avgsignalin_ON))

IN_membrane_volt_OFF = np.reshape(IN_membrane_volt2_OFF[:, 2], [NumCellsIN, TotalDataPoints])
print('reshaped the IN signal as 2D matrix')
avgsignalin_OFF = mean(IN_membrane_volt_OFF, axis=0)
print(size(avgsignalin_OFF))

TotalAvgMembraneIN = avgsignalin_OFF + avgsignalin_ON

''' Now release the SpiNNaker machine'''
p.end()

#

# # np.savetxt('./testingspikes.csv',TCR_spikes_ON)

# for k1 in range(len(eventos1part)):
#     plt.figure(0)
#     plt.plot(eventos1part[k1], k1 * np.ones_like(eventos1part[k1]), '.')
# for k2 in range(len(eventos2part)):
#     plt.figure(1)
#     plt.plot(eventos2part[k2], k2 * np.ones_like(eventos2part[k2]), '.')

plt.figure(2)
plt.plot(TCR_spikes_ON[:, 1], TCR_spikes_ON[:, 0], '.')
plt.plot(TCR_spikes_OFF[:, 1], TCR_spikes_OFF[:, 0], '.')

plt.figure(3)
plt.plot(IN_spikes_ON[:, 1], IN_spikes_ON[:, 0], '.')
plt.plot(IN_spikes_OFF[:, 1], IN_spikes_OFF[:, 0], '.')


plt.figure(4)
plt.plot([x for x in range(TotalDataPoints)], avgsignaltcr_ON)
plt.plot([x for x in range(TotalDataPoints)], avgsignaltcr_OFF)
plt.plot([x for x in range(TotalDataPoints)], TotalAvgMembraneTCR)

plt.figure(5)
plt.plot([x for x in range(TotalDataPoints)], avgsignalin_ON)
plt.plot([x for x in range(TotalDataPoints)], avgsignalin_OFF)
plt.plot([x for x in range(TotalDataPoints)], TotalAvgMembraneIN)

plt.show()

# print "--- {} SECONDS ELAPSED ---".format(time.time() - start_time)
# # print "validating input isi used in the model: {}".format(Inp_isi)

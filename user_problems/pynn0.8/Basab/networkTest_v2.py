import spynnaker8 as sim
from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt
# import pyNN.utility.plotting as plot
# import random
# import numpy as np
# from pyNN.random import RandomDistribution, NumpyRNG

#spynnaker setup
sim.setup(timestep=1.0)

# model = sim.extra_models.Izhikevich_cond
#
#
# snr_a=0.02 #0.005 #0.1
# snr_b=0.2 #0.32
# snr_c=-65 #-65
# snr_d=8 #2
# snr_v_init = -65 #-70
# snr_u_init = snr_b * snr_v_init
#
# tau_ampa = 6###excitatory synapse time constant
# tau_gabaa= 4### inhibitory synapse time constant
# E_ampa = 0.0
# E_gabaa = -80.0
# current_bias = 4##50##100##4.0
# cell_params_input = {'a': snr_a, 'b': snr_b, 'c': snr_c, 'd': snr_d,
#                    'v': snr_v_init, 'u': snr_u_init,
#                    'tau_syn_E': tau_ampa, 'tau_syn_I': tau_gabaa,
#                    'i_offset': current_bias,
#                    'e_rev_E': E_ampa, 'e_rev_I': E_gabaa,
#                    }
#
# cell_params_output = {'a': snr_a, 'b': snr_b, 'c': snr_c, 'd': snr_d,
#                    'v': snr_v_init, 'u': snr_u_init,
#                    'tau_syn_E': tau_ampa, 'tau_syn_I': tau_gabaa,
#                    'i_offset': 0.0,
#                    'e_rev_E': E_ampa, 'e_rev_I': E_gabaa,
#                    }

model = sim.IF_curr_exp

cell_params_input = {'cm': 0.25,
                     'i_offset': 1.0,
                     'tau_m': 20.0,
                     'tau_refrac': 2.0,
                     'tau_syn_E': 5.0,
                     'tau_syn_I': 5.0,
                     'v_reset': -70.0,
                     'v_rest': -65.0,
                     'v_thresh': -50.0
                     }

cell_params_output = {'cm': 0.25,
                      'i_offset': 0.0,
                      'tau_m': 20.0,
                      'tau_refrac': 2.0,
                      'tau_syn_E': 5.0,
                      'tau_syn_I': 5.0,
                      'v_reset': -70.0,
                      'v_rest': -65.0,
                      'v_thresh': -50.0
                      }

pre_size = 2
post_size = 3

simtime = 200

pre_pop = sim.Population(pre_size, model(**cell_params_input))
# spikeArray = {'spike_times': [[10], [50]]}
# pre_pop = sim.Population(pre_size, sim.SpikeSourceArray(**spikeArray))
post_pop = sim.Population(post_size, model(**cell_params_output))


wiring = sim.FixedProbabilityConnector(p_connect=1) ##  sim.AllToAllConnector() ##
# injectionConnection = [(0, 0)]  #, (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)]
# wiring = sim.FromListConnector(injectionConnection)
static_synapse = sim.StaticSynapse(weight=2.5, delay=100.0)
connections = sim.Projection(pre_pop, post_pop, wiring,
                             receptor_type='excitatory',
                             synapse_type=static_synapse)

#record data
pre_pop.record(['v', 'spikes', 'gsyn_exc', 'gsyn_inh'])
# pre_pop.record(['spikes'])
post_pop.record(['v', 'spikes', 'gsyn_exc', 'gsyn_inh'])

#start simulation
sim.run(simtime)

print('connections: ', connections.get(['weight', 'delay'], 'list'))

#get data in neo format
neo_pre_spikes = pre_pop.get_data(variables = ['spikes','v',
                                               'gsyn_exc', 'gsyn_inh'])
# neo_pre_spikes = pre_pop.get_data(variables = ['spikes'])
neo_post_spikes = post_pop.get_data(variables = ['spikes','v',
                                                 'gsyn_exc', 'gsyn_inh'])

#spiketrains
pre_pop_spikes = neo_pre_spikes.segments[0].spiketrains
post_pop_spikes = neo_post_spikes.segments[0].spiketrains

#membrane potential
pre_pop_v = neo_pre_spikes.segments[0].filter(name='v')
post_pop_v = neo_post_spikes.segments[0].filter(name='v')

print('pre_pop_v: ', pre_pop_v)
print('post_pop_v: ', post_pop_v)
print('post_pop_spikes: ', post_pop_spikes, len(post_pop_spikes[0]))

#conductance excitatory
# pre_pop_gsyne = neo_pre_spikes.segments[0].filter(name='gsyn_exc')[0]
post_pop_gsyne = neo_post_spikes.segments[0].filter(name='gsyn_exc')

#conductance inhibitory
# pre_pop_gsyni = neo_pre_spikes.segments[0].filter(name='gsyn_inh')[0]
post_pop_gsyni = neo_post_spikes.segments[0].filter(name='gsyn_inh')

#end simulation
sim.end()

# Plot
Figure(
    # plot voltage(pre_pop) for first ([0]) neuron
    Panel(pre_pop_v[0], ylabel="Mem Potential for pre_pop(mV)",
               yticks=True, markersize=0.2, xlim=(0, simtime)),

    # plot voltage(post_pop) for first ([0]) neuron
    Panel(post_pop_v[0], ylabel="Mem Potential for post_pop(mV)",
               yticks=True, markersize=0.2, xlim=(0, simtime)),
    # plot gsyn(post_pop) for first ([0]) neuron
    Panel(post_pop_gsyne[0],
               ylabel="excitatory synaptic conductance for for post_pop(mS)",
               yticks=True, markersize=0.2, xlim=(0, simtime)),
    Panel(post_pop_gsyni[0],
               ylabel="inhibitory synaptic conductance for for post_pop(mS)",
               yticks=True, markersize=0.2, xlim=(0, simtime)),

    # plot spikes(pre_pop) (or in this case spike)
    Panel(pre_pop_spikes, ylabel="pre-neurons",
               yticks=True, markersize=0.2, xlim=(0, simtime)),
    # plot spikes(post_pop) (or in this case spike)
    Panel(post_pop_spikes, ylabel="post-neurons",
               yticks=True, markersize=0.2, xlim=(0, simtime)),
    title="For RS Neuron params",
    annotations="Simulated with {}".format(
        sim.name())).save('Finalnetwork_staticsynapse0.5_input100.png')

plt.show()

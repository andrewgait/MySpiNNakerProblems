"""
Synfirechain-like example
"""
import spynnaker8 as p
from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt
import numpy
import csa

runtime = 5000
p.setup(timestep=1.0, min_delay=1.0, max_delay=144.0)
nNeurons = 200  # number of neurons in each population
p.set_number_of_neurons_per_core(p.IF_curr_exp, nNeurons / 10)

cell_params_lif = {'cm': 0.25,
                   'i_offset': 0.0,
                   'tau_m': 20.0,
                   'tau_refrac': 2.0,
                   'tau_syn_E': 5.0,
                   'tau_syn_I': 5.0,
                   'v_reset': -70.0,
                   'v_rest': -65.0,
                   'v_thresh': -50.0
                   }

populations = list()
projections = list()

weight_to_spike = 2.0
delay = 5

# connection list in a loop for first population
loopConnections = []
for i in range(0, nNeurons):
    singleConnection = ((i, (i + 1) % nNeurons))
    loopConnections.append(singleConnection)

#print 'loopConnections: ', loopConnections

# injection list to set the chain going
injectionConnection = [(0, 0)]
spikeArray = {'spike_times': [[0]]}

# list of populations
populations.append(
    p.Population(nNeurons, p.IF_curr_exp(**cell_params_lif), label='pop_1'))
populations.append(
    p.Population(nNeurons, p.IF_curr_exp(**cell_params_lif), label='pop_2'))
populations.append(
    p.Population(nNeurons, p.IF_curr_exp(**cell_params_lif), label='pop_3'))
populations.append(
    p.Population(nNeurons, p.IF_curr_exp(**cell_params_lif), label='pop_4'))
populations.append(
    p.Population(1, p.SpikeSourceArray(**spikeArray), label='inputSpikes_1'))

# Loop connector: we can just pass in the list we made earlier
CSA_loop_connector = p.CSAConnector(loopConnections)

# random connector: each connection has a probability of 0.05
CSA_random_connector = p.CSAConnector(csa.random(0.05))

# one-to-one connector: do I really need to explain?
CSA_onetoone_connector = p.CSAConnector(csa.oneToOne)

# This creates a block of size (5,10) with a probability of 0.05; then
# within the block an individual connection has a probability of 0.5
CSA_randomblock_connector = p.CSAConnector(
    csa.block(15,10)*csa.random(0.05)*csa.random(0.5))

# list of projections using the connectors above
projections.append(p.Projection(
    populations[0], populations[0], CSA_loop_connector,
    p.StaticSynapse(weight=weight_to_spike, delay=delay)))
projections.append(p.Projection(
    populations[0], populations[1], CSA_random_connector,
    p.StaticSynapse(weight=weight_to_spike, delay=delay)))
projections.append(p.Projection(
    populations[1], populations[2], CSA_onetoone_connector,
    p.StaticSynapse(weight=weight_to_spike, delay=delay)))
projections.append(p.Projection(
    populations[2], populations[3], CSA_randomblock_connector,
    p.StaticSynapse(weight=weight_to_spike, delay=delay)))
projections.append(p.Projection(
    populations[4], populations[0], p.FromListConnector(injectionConnection),
    p.StaticSynapse(weight=weight_to_spike, delay=1)))

populations[0].record(['v', 'spikes'])
populations[1].record(['v', 'spikes'])
populations[2].record(['v', 'spikes'])
populations[3].record(['v', 'spikes'])

p.run(runtime)

# Use the show functionality of CSA implementation to display connection sets
CSA_loop_connector.show_connection_set(nNeurons, nNeurons)
CSA_random_connector.show_connection_set(nNeurons, nNeurons)
CSA_onetoone_connector.show_connection_set(nNeurons, nNeurons)
CSA_randomblock_connector.show_connection_set(nNeurons, nNeurons)

# get data (could be done as one, but can be done bit by bit as well)
v = populations[0].get_data('v')
v2 = populations[1].get_data('v')
v3 = populations[2].get_data('v')
v4 = populations[3].get_data('v')
spikes = populations[0].get_data('spikes')
spikes2 = populations[1].get_data('spikes')
spikes3 = populations[2].get_data('spikes')
spikes4 = populations[3].get_data('spikes')

Figure(
    # raster plot of the presynaptic neuron spike times
    Panel(spikes.segments[0].spiketrains,
          yticks=True, markersize=1.2, xlim=(0, runtime)),
    # membrane potential of the postsynaptic neuron
    Panel(v.segments[0].filter(name='v')[0],
          ylabel="Membrane potential (mV)",
          data_labels=[populations[0].label], yticks=True, xlim=(0, runtime)),
    # raster plot of the presynaptic neuron spike times
    Panel(spikes2.segments[0].spiketrains,
          yticks=True, markersize=1.2, xlim=(0, runtime)),
    # membrane potential of the postsynaptic neuron
    Panel(v2.segments[0].filter(name='v')[0],
          ylabel="Membrane potential pop_2 (mV)",
          data_labels=[populations[1].label], yticks=True, xlim=(0, runtime)),
    # raster plot of the presynaptic neuron spike times
    Panel(spikes3.segments[0].spiketrains,
          yticks=True, markersize=1.2, xlim=(0, runtime)),
    # membrane potential of the postsynaptic neuron
    Panel(v3.segments[0].filter(name='v')[0],
          ylabel="Membrane potential pop_3 (mV)",
          data_labels=[populations[2].label], yticks=True, xlim=(0, runtime)),
    # raster plot of the presynaptic neuron spike times
    Panel(spikes4.segments[0].spiketrains,
          yticks=True, markersize=1.2, xlim=(0, runtime)),
    # membrane potential of the postsynaptic neuron
    Panel(v3.segments[0].filter(name='v')[0],
          ylabel="Membrane potential pop_4 (mV)",
          data_labels=[populations[3].label],
          yticks=True, xlim=(0, runtime), xticks=True, xlabel="Time"),
    title="Synfire chain example using CSA connectors",
    annotations="Simulated with {}".format(p.name())
)
plt.show()

p.end()

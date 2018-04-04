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
delay = 17

# create loopConnections array using numpy linspaces
#loopConnections = numpy.array([numpy.linspace(0,nNeurons-2,nNeurons/2),
#                               numpy.linspace(2,nNeurons+1,nNeurons/2)],
#                               numpy.uint32)
# connect the final neuron to the first neuron
#loopConnections[1,(nNeurons/2)-1] = 0
#print loopConnections[0,nNeurons-1]
#print loopConnections[1,nNeurons-1]
#print loopConnections
#for i in range(0, nNeurons):
#    singleConnection = ((i, (i + 1) % nNeurons, weight_to_spike, delay))
#    loopConnections.append(singleConnection)

injectionConnection = [(0, 0)]
spikeArray = {'spike_times': [[0]]}
populations.append(
    p.Population(nNeurons, p.IF_curr_exp(**cell_params_lif), label='pop_1'))
populations.append(
    p.Population(nNeurons, p.IF_curr_exp(**cell_params_lif), label='pop_2'))
populations.append(
    p.Population(1, p.SpikeSourceArray(**spikeArray), label='inputSpikes_1'))

CSA_random_connector = p.CSAConnector(csa.random(0.05))
CSA_onetoone_connector = p.CSAConnector(csa.oneToOne)

projections.append(p.Projection(
    populations[0], populations[0], CSA_random_connector,
    p.StaticSynapse(weight=weight_to_spike, delay=delay)))
projections.append(p.Projection(
    populations[0], populations[1], CSA_onetoone_connector,
    p.StaticSynapse(weight=weight_to_spike, delay=delay)))
projections.append(p.Projection(
    populations[2], populations[0], p.FromListConnector(injectionConnection),
    p.StaticSynapse(weight=weight_to_spike, delay=1)))

populations[0].record(['v', 'gsyn_exc', 'gsyn_inh', 'spikes'])
populations[1].record(['v', 'gsyn_exc', 'gsyn_inh', 'spikes'])

p.run(runtime)

CSA_random_connector.show_connection_set()
CSA_onetoone_connector.show_connection_set()

# get data (could be done as one, but can be done bit by bit as well)
v = populations[0].get_data('v')
v2 = populations[1].get_data('v')
gsyn_exc = populations[0].get_data('gsyn_exc')
gsyn_inh = populations[0].get_data('gsyn_inh')
spikes = populations[0].get_data('spikes')

Figure(
    # raster plot of the presynaptic neuron spike times
    Panel(spikes.segments[0].spiketrains,
          yticks=True, markersize=1.2, xlim=(0, runtime)),
    # membrane potential of the postsynaptic neuron
    Panel(v.segments[0].filter(name='v')[0],
          ylabel="Membrane potential (mV)",
          data_labels=[populations[0].label], yticks=True, xlim=(0, runtime)),
    # membrane potential of the postsynaptic neuron
    Panel(v2.segments[0].filter(name='v')[0],
          ylabel="Membrane potential pop_2 (mV)",
          data_labels=[populations[1].label], yticks=True, xlim=(0, runtime)),
    Panel(gsyn_exc.segments[0].filter(name='gsyn_exc')[0],
          ylabel="gsyn excitatory (mV)",
          data_labels=[populations[0].label], yticks=True, xlim=(0, runtime)),
    Panel(gsyn_inh.segments[0].filter(name='gsyn_inh')[0],
          ylabel="gsyn inhibitory (mV)",
          data_labels=[populations[0].label], yticks=True, xlim=(0, runtime)),
    title="Simple synfire chain example",
    annotations="Simulated with {}".format(p.name())
)
plt.show()

p.end()

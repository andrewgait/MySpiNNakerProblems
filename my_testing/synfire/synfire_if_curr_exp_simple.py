"""
Synfirechain-like example
"""
import pyNN.spiNNaker as p
from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt

runtime = 10
p.setup(timestep=0.1, min_delay=1.0, max_delay=14.0)
nNeurons = 10  # number of neurons in each population
p.set_number_of_neurons_per_core(p.IF_curr_exp, nNeurons / 2)

cell_params_lif = {'cm': 0.25,
                   'i_offset': 0.0,
                   'tau_m': 10.0,
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
delay = 1

loopConnections = list()
for i in range(0, nNeurons):
    singleConnection = ((i, (i + 1) % nNeurons, weight_to_spike, delay))
    loopConnections.append(singleConnection)

injectionConnection = [(0, 0),(1,1),(2,2)]
spikeArray = {'spike_times': [[3,5,7],[4],[2]]}
populations.append(
    p.Population(nNeurons, p.IF_curr_exp(**cell_params_lif), label='pop_1'))
populations.append(
    p.Population(3, p.SpikeSourceArray(**spikeArray), label='inputSpikes_1'))

projections.append(p.Projection(
    populations[0], populations[0], p.FromListConnector(loopConnections),
    p.StaticSynapse(weight=weight_to_spike, delay=delay)))
projections.append(p.Projection(
    populations[1], populations[0], p.FromListConnector(injectionConnection),
    p.StaticSynapse(weight=weight_to_spike, delay=1)))

populations[0].record(['v', 'gsyn_exc', 'gsyn_inh', 'spikes'])

p.run(runtime)

# get data (could be done as one, but can be done bit by bit as well)
v = populations[0].get_data('v')
gsyn_exc = populations[0].get_data('gsyn_exc')
gsyn_inh = populations[0].get_data('gsyn_inh')
spikes = populations[0].get_data('spikes')

spikes_spin = populations[0].spinnaker_get_data('spikes')
print(spikes_spin)

Figure(
    # raster plot of the presynaptic neuron spike times
    Panel(spikes.segments[0].spiketrains,
          yticks=True, markersize=1.0, xlim=(0, runtime), xticks=True),
    # membrane potential of the postsynaptic neuron
    Panel(v.segments[0].filter(name='v')[0],
          ylabel="Membrane potential (mV)",
          data_labels=[populations[0].label], yticks=True, xlim=(0, runtime)),
    Panel(gsyn_exc.segments[0].filter(name='gsyn_exc')[0],
          ylabel="gsyn excitatory (mV)",
          data_labels=[populations[0].label], yticks=True, xlim=(0, runtime)),
    Panel(gsyn_inh.segments[0].filter(name='gsyn_inh')[0],
          xlabel="Time (ms)", xticks=True,
          ylabel="gsyn inhibitory (mV)",
          data_labels=[populations[0].label], yticks=True, xlim=(0, runtime)),
    title="Simple synfire chain example",
    annotations="Simulated with {}".format(p.name())
)
plt.show()

p.end()

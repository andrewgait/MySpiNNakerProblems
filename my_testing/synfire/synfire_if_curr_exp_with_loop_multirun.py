"""
Synfirechain-like example
"""
import pyNN.spiNNaker as p
from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt

runtime = 500000
p.setup(timestep=1.0, min_delay=1.0, max_delay=144.0)
nNeurons = 200  # number of neurons in each population
p.set_number_of_neurons_per_core(p.IF_curr_exp, nNeurons / 2)

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
delay = 68

loopConnections = list()
for i in range(0, nNeurons):
    singleConnection = ((i, (i + 1) % nNeurons, weight_to_spike, delay))
    loopConnections.append(singleConnection)

injectionConnection = [(0, 0)]
spikeArray = {'spike_times': [[0]]}
populations.append(
    p.Population(nNeurons, p.IF_curr_exp(**cell_params_lif), label='pop_1'))
populations.append(
    p.Population(1, p.SpikeSourceArray(**spikeArray), label='inputSpikes_1'))

projections.append(p.Projection(
    populations[0], populations[0], p.FromListConnector(loopConnections),
    p.StaticSynapse(weight=weight_to_spike, delay=delay)))
projections.append(p.Projection(
    populations[1], populations[0], p.FromListConnector(injectionConnection),
    p.StaticSynapse(weight=weight_to_spike, delay=1)))

populations[0].record(['v', 'gsyn_exc', 'gsyn_inh', 'spikes'], 10000)

spikes_list = list()
v_list = list()

time_slice = 100000
for nn in range(1, 6):
    populations[0].set(v_reset=-80.0+(nn*2.0))
    p.run(time_slice)

    # get data (could be done as one, but can be done bit by bit as well)
    v = populations[0].get_data('v')
    gsyn_exc = populations[0].get_data('gsyn_exc')
    gsyn_inh = populations[0].get_data('gsyn_inh')
    spikes = populations[0].get_data('spikes')
    v_list.append(v)
    spikes_list.append(spikes)

    Figure(
        # raster plot of the presynaptic neuron spike times
        Panel(spikes_list[nn-1].segments[0].spiketrains,
              yticks=True, markersize=0.2, xlim=(0, runtime)),
        # membrane potential of the postsynaptic neuron
        Panel(v_list[nn-1].segments[0].filter(name='v')[0],
              ylabel="Membrane potential (mV)",
              data_labels=[populations[0].label], yticks=True, xlim=(0, runtime)),
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
# end of loop


p.end()

"""
Synfirechain-like example
"""
import pyNN.spiNNaker as p
from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt

# Del (spinnaker mailing list) reports this behaves differently on NEST
# than on spinnaker, so testing it out...

runtime = 10  # 100
p.setup(timestep=0.1, min_delay=1.0, max_delay=14.0)
nNeurons = 10  # number of neurons in each population
# p.set_number_of_neurons_per_core(p.IF_curr_exp, nNeurons // 2)

cell_params_lif = {'cm': 0.25,
                   'i_offset': 0.0,
                   'tau_m': 20.0,
                   'tau_refrac': 2.0,
                   'tau_syn_E': 5.0,
                   'tau_syn_I': 5.0,
                   'v_reset': -70.0,
                   'v_rest': -65.0,
                   'v_thresh': -50.0,
                   'e_rev_E': 0.,
                   'e_rev_I': -80.
                   }

weight_to_spike = 0.035
delay = 1

loopConnections = list()
for i in range(0, nNeurons):
    singleConnection = ((i, (i + 1) % nNeurons, weight_to_spike, delay))
    loopConnections.append(singleConnection)

injectionConnection = [(0, 0), (1, 5), (2, 8)]
spikeArray = {'spike_times': [[3],[2],[4]]}
main_pop = p.Population(
    nNeurons, p.IF_cond_exp(**cell_params_lif), label='pop_1')
input_pop = p.Population(
    3, p.SpikeSourceArray(**spikeArray), label='inputSpikes_1')

p.Projection(
    main_pop, main_pop, p.FromListConnector(loopConnections),
    p.StaticSynapse(weight=weight_to_spike, delay=delay))
p.Projection(
    input_pop, main_pop, p.FromListConnector(injectionConnection),
    p.StaticSynapse(weight=weight_to_spike, delay=1))

main_pop.record(['v', 'gsyn_exc', 'gsyn_inh', 'spikes'])
input_pop.record(['spikes'])

p.run(runtime)

# get data (could be done as one, but can be done bit by bit as well)
v = main_pop.get_data('v')
gsyn_exc = main_pop.get_data('gsyn_exc')
gsyn_inh = main_pop.get_data('gsyn_inh')
spikes = main_pop.get_data('spikes')
spikes_in = input_pop.get_data('spikes')

figure_filename = "results.png"
Figure(
    # raster plot of the input_pop spike times
    Panel(spikes_in.segments[0].spiketrains,
          yticks=True, markersize=1.5, xlim=(0, runtime), xticks=True),
    # raster plot of the presynaptic neuron spike times
    Panel(spikes.segments[0].spiketrains,
          yticks=True, markersize=1.0, xlim=(0, runtime), xticks=True),
    # membrane potential of the postsynaptic neuron
    Panel(v.segments[0].filter(name='v')[0],
          ylabel="Membrane potential (mV)",
          data_labels=[main_pop.label], yticks=True, xlim=(0, runtime)),
    Panel(gsyn_exc.segments[0].filter(name='gsyn_exc')[0],
          ylabel="gsyn excitatory (mV)",
          data_labels=[main_pop.label], yticks=True, xlim=(0, runtime)),
    Panel(gsyn_inh.segments[0].filter(name='gsyn_inh')[0],
          ylabel="gsyn inhibitory (mV)",
          data_labels=[main_pop.label], yticks=True, xlim=(0, runtime)),
    title="Simple synfire chain example",
    annotations="Simulated with {}".format(p.name())
)
plt.show()
print(figure_filename)

p.end()

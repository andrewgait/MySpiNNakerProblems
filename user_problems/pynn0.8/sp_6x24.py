"""
Synfirechain-like example
"""
import spynnaker8 as p
from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt
import os
import numpy
import json

runtime = 200
p.setup(timestep=1.0)
nNeurons = 8 #3456  # number of neurons in each population
p.set_number_of_neurons_per_core(p.IF_cond_exp, 80 )

cell_params_lif = {'cm': 0.09,
                   'i_offset': 0.0,
                   'tau_m': 1000.0,
                   'tau_refrac': 0.0,
                   'tau_syn_E': 0.01,
                   'tau_syn_I': 0.01,
                   'v_reset': 0.0,
                   'v_rest': 0.0,
                   'v_thresh': 1.0,
                   'e_rev_E' : 10.0,
                   'e_rev_I' : -10.0
                   }


# connections = [
# (0, 0, 1.0, 9),
# (1, 3, 3.0, 10),
# (2, 5, 1.0, 5),
# (3, 6, 1.0, 7),
# (4, 7, 4.0, 4),
# (5, 4, 1.0, 6),
# (6, 1, 1.0, 50),
# (7, 2, 1.0, 5)
# ]
connections = [
(0, 0, 9, 1.0),
(1, 3, 10, 3.0),
(2, 5, 5, 1.0),
(3, 6, 7, 1.0),
(4, 7, 4, 4.0),
(5, 4, 6, 1.0),
(6, 1, 50, 1.0),
(7, 2, 5, 1.0)
]

# path1 = "con.txt"
# if os.path.exists(path1):
#     os.remove(path1)
#
# current_file_path = os.path.dirname(os.path.abspath(__file__))
# file1 = os.path.join(current_file_path, path1)
# numpy.savetxt(file1, connections,
#               header='columns = ["i", "j", "delay", "weight"]')


def input_spike():
    with open('inputspike.txt', 'r') as f:
        data = f.read()
        data = json.loads(data)
        # print('json',data)
        spiketrains=data
        print(spiketrains)

    return spiketrains


p.set_number_of_neurons_per_core(p.SpikeSourceArray, 100)

spiketrains = input_spike()

# spiketrains = {'spike_times': [[0],[1],[1],[0],[1],[0],[0],[1]]}

main_pop = p.Population(
    nNeurons, p.IF_cond_exp(**cell_params_lif), label='pop_1')

main_pop.initialize(v=0.0)
input_pop = p.Population(
    8, p.SpikeSourceArray(spike_times=spiketrains), label='inputSpikes_1')

proj=p.Projection(
    #input_pop, main_pop, p.FromListConnector(connections))
    input_pop, main_pop, p.FromFileConnector('con.txt'))


input_pop.record(['spikes'])

main_pop.record(['v', 'gsyn_exc', 'gsyn_inh', 'spikes'])

p.run(runtime)

print(proj.get(["weight", "delay"], format="list"))

# get data (could be done as one, but can be done bit by bit as well)
v = main_pop.get_data('v')
gsyn_exc = main_pop.get_data('gsyn_exc')
gsyn_inh = main_pop.get_data('gsyn_inh')
spikes = main_pop.get_data('spikes')

in_spikes = input_pop.get_data('spikes')

figure_filename = "results.png"
Figure(
    # raster plot of the presynaptic neuron spike times
    Panel(in_spikes.segments[0].spiketrains,
        yticks=True, markersize=5.0, color='R', xlim=(0, runtime)),

    Panel(spikes.segments[0].spiketrains,
          yticks=True, markersize=0.5, color='B', xlim=(0, runtime)),
    # membrane potential of the postsynaptic neuron
    Panel(v.segments[0].filter(name='v')[0],
          ylabel="Membrane potential (mV)",
          data_labels=[main_pop.label], yticks=True, xlim=(0, runtime)),
    #Panel(gsyn_exc.segments[0].filter(name='gsyn_exc')[0],
    #      ylabel="gsyn excitatory (mV)",
    #      data_labels=[main_pop.label], yticks=True, xlim=(0, runtime)),
    #Panel(gsyn_inh.segments[0].filter(name='gsyn_inh')[0],
    #      ylabel="gsyn inhibitory (mV)",
    #      data_labels=[main_pop.label], yticks=True, xlim=(0, runtime)),
    title="Simple synfire chain example on Spinnaker(poisson rate=50)",
    annotations="Simulated with {}".format(p.name())
)
plt.show()
print(figure_filename)

p.end()
